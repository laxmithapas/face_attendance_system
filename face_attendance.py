import cv2
import numpy as np
import sqlite3
import json
import hashlib
from datetime import datetime, date
import os
from cryptography.fernet import Fernet
import pickle
import pytz

# Register sqlite3 adapters and converters to avoid DeprecationWarning in Python 3.12
def adapt_date_iso(val):
    return val.isoformat()

def adapt_datetime_iso(val):
    return val.isoformat()

def convert_date(val):
    return date.fromisoformat(val.decode())

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

sqlite3.register_adapter(date, adapt_date_iso)
sqlite3.register_adapter(datetime, adapt_datetime_iso)
sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("timestamp", convert_datetime)

class SimpleFaceAttendanceSystem:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.encryption_key = self.load_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.init_database()
        
        # Security tracking
        self.failed_attempts = {}
        self.suspicious_activity = []
        self.face_data = []
        self.face_labels = []
        self.name_dict = {}
        
        # Load existing data
        self.load_training_data()
        
    def load_or_create_key(self):
        """Load encryption key or create new one"""
        key_file = "encryption_key.key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('attendance_system.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            face_data BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Attendance table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'present',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Security events table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            severity TEXT DEFAULT 'medium'
        )
        ''')
        
        self.conn.commit()
    
    def encrypt_data(self, data):
        """Encrypt data for secure storage"""
        data_bytes = pickle.dumps(data)
        return self.cipher_suite.encrypt(data_bytes)
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data from storage"""
        decrypted_bytes = self.cipher_suite.decrypt(encrypted_data)
        return pickle.loads(decrypted_bytes)
    
    def capture_faces_for_training(self, name, num_samples=30):
        """Capture face samples for training"""
        print(f"Capturing face samples for {name}")
        print("Look at the camera and press SPACE to capture samples")
        print("Press 'q' to quit")
        
        cap = cv2.VideoCapture(0)
        samples_collected = 0
        face_samples = []
        
        while samples_collected < num_samples:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Better face detection parameters to reduce false positives
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1,
                minNeighbors=6,       # Higher threshold
                minSize=(80, 80),     # Minimum size
                maxSize=(300, 300)    # Maximum size to avoid background objects
            )
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, f"Samples: {samples_collected}/{num_samples}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' '):  # Space bar to capture
                    face_sample = gray[y:y+h, x:x+w]
                    face_samples.append(face_sample)
                    samples_collected += 1
                    print(f"Sample {samples_collected} captured")
                    
                elif key == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return face_samples if len(face_samples) > 0 else None
            
            cv2.imshow('Face Capture', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return face_samples
    
    def enroll_user(self, name):
        """Enroll a new user"""
        try:
            # Check if user already exists
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
            if cursor.fetchone():
                return False, f"User {name} already exists"
            
            # Capture face samples
            face_samples = self.capture_faces_for_training(name)
            if not face_samples:
                return False, "No face samples captured"
            
            # Encrypt and store face data
            encrypted_data = self.encrypt_data(face_samples)
            cursor.execute("INSERT INTO users (name, face_data) VALUES (?, ?)", 
                          (name, encrypted_data))
            user_id = cursor.lastrowid
            self.conn.commit()
            
            # Update training data
            for sample in face_samples:
                self.face_data.append(sample)
                self.face_labels.append(user_id)
            
            self.name_dict[user_id] = name
            self.train_recognizer()
            
            return True, f"User {name} enrolled successfully"
            
        except Exception as e:
            return False, f"Enrollment failed: {str(e)}"
    
    def load_training_data(self):
        """Load training data from database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, face_data FROM users")
        users = cursor.fetchall()
        
        self.face_data = []
        self.face_labels = []
        self.name_dict = {}
        
        for user_id, name, encrypted_data in users:
            try:
                face_samples = self.decrypt_data(encrypted_data)
                for sample in face_samples:
                    self.face_data.append(sample)
                    self.face_labels.append(user_id)
                
                self.name_dict[user_id] = name
            except Exception as e:
                print(f"Error loading data for {name}: {e}")
        
        if len(self.face_data) > 0:
            self.train_recognizer()
    
    def train_recognizer(self):
        """Train the face recognizer"""
        if len(self.face_data) > 0:
            self.recognizer.train(self.face_data, np.array(self.face_labels))
            print("Face recognizer trained successfully")
    
    def detect_motion(self, frame1, frame2):
        """Simple motion detection for liveness"""
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        return np.sum(thresh) > 1000  # Motion detected if enough pixels changed
    
    def get_current_time(self):
        """Get current time in IST"""
        ist = pytz.timezone('Asia/Kolkata')
        return datetime.now(ist)

    def log_security_event(self, event_type, description, severity="medium"):
        """Log security events with IST timestamp"""
        cursor = self.conn.cursor()
        current_time = self.get_current_time()
        cursor.execute(
            "INSERT INTO security_events (event_type, description, severity, timestamp) VALUES (?, ?, ?, ?)",
            (event_type, description, severity, current_time)
        )
        self.conn.commit()
        print(f"Security Event: {event_type} - {description} at {current_time}")
    
    def mark_attendance(self, name):
        """Mark attendance for recognized user"""
        cursor = self.conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        user_result = cursor.fetchone()
        
        if user_result:
            user_id = user_result[0]
            
            # Check if already marked today
            today = datetime.now().date()
            cursor.execute("""
                SELECT id FROM attendance 
                WHERE user_id = ? AND date(timestamp) = ?
            """, (user_id, today))
            
            if cursor.fetchone():
                return False, f"{name} already marked present today"
            
            # Mark attendance
            cursor.execute("INSERT INTO attendance (user_id) VALUES (?)", (user_id,))
            self.conn.commit()
            return True, f"Attendance marked for {name}"
        
        return False, "User not found"
    
    def run_attendance_system(self):
        """Main attendance system loop"""
        cap = cv2.VideoCapture(0)
        
        print("Face Recognition Attendance System Started")
        print("Controls:")
        print("- 'a': Mark attendance for recognized faces")
        print("- 'e': Enroll new user")
        print("- 'q': Quit")
        
        prev_frame = None
        recognition_enabled = len(self.face_data) > 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Motion detection for liveness
            motion_detected = False
            if prev_frame is not None:
                motion_detected = self.detect_motion(prev_frame, frame)
            prev_frame = frame.copy()
            
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                
                name = "Unknown"
                confidence = 0
                
                if recognition_enabled:
                    # Recognize face
                    user_id, confidence = self.recognizer.predict(face_roi)
                    if confidence < 100:  # Lower is better for LBPH
                        name = self.name_dict.get(user_id, "Unknown")
                    else:
                        self.log_security_event("unknown_face", 
                                               "Unrecognized person detected", "high")
                
                # Choose color based on recognition and motion
                if name != "Unknown" and motion_detected:
                    color = (0, 255, 0)  # Green for recognized + motion
                elif name != "Unknown":
                    color = (0, 255, 255)  # Yellow for recognized but no motion
                else:
                    color = (0, 0, 255)  # Red for unknown
                
                # Draw rectangle and info
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Display info
                info = f"{name} ({confidence:.0f})"
                if motion_detected:
                    info += " - Live"
                else:
                    info += " - Static"
                
                cv2.putText(frame, info, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            # Display system status
            status = f"Users: {len(self.name_dict)} | Recognition: {'ON' if recognition_enabled else 'OFF'}"
            cv2.putText(frame, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Face Attendance System', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a') and len(faces) > 0:
                # Mark attendance for all recognized faces with motion
                for (x, y, w, h) in faces:
                    if recognition_enabled:
                        face_roi = gray[y:y+h, x:x+w]
                        user_id, confidence = self.recognizer.predict(face_roi)
                        if confidence < 100:
                            name = self.name_dict.get(user_id, "Unknown")
                            if name != "Unknown" and motion_detected:
                                success, message = self.mark_attendance(name)
                                print(message)
                            elif name != "Unknown" and not motion_detected:
                                self.log_security_event("spoofing_attempt", 
                                                       f"Static image detected for {name}", "high")
                                print(f"Spoofing attempt detected for {name}")
            
            elif key == ord('e'):
                # Enroll new user
                cap.release()
                cv2.destroyAllWindows()
                
                name = input("Enter name for new user: ").strip()
                if name:
                    success, message = self.enroll_user(name)
                    print(message)
                    if success:
                        recognition_enabled = True
                
                cap = cv2.VideoCapture(0)
        
        cap.release()
        cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    system = SimpleFaceAttendanceSystem()
    system.run_attendance_system()