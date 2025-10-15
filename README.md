# Face Recognition Attendance System

A comprehensive face recognition-based attendance tracking system built with Python, OpenCV, and Flask. This system provides secure, real-time attendance monitoring with anti-spoofing capabilities and a modern web dashboard.

## 🚀 Features

### Core Functionality
- **Real-time Face Recognition**: Uses OpenCV's LBPH (Local Binary Patterns Histograms) face recognizer
- **Live Attendance Marking**: Automatically marks attendance for recognized users
- **Anti-Spoofing Protection**: Motion detection to prevent static image attacks
- **Secure Data Storage**: Encrypted face data using Fernet cryptography
- **Web Dashboard**: Modern, responsive web interface for monitoring and management

### Security Features
- **Motion Detection**: Liveness verification to detect real faces vs. photos
- **Security Event Logging**: Tracks suspicious activities and unrecognized faces
- **Encrypted Face Data**: All face samples are encrypted before database storage
- **SQLite Database**: Secure local database with proper data types

### Dashboard Features
- **Real-time Statistics**: Live updates of attendance counts and user statistics
- **Today's Attendance**: View all attendance records for the current day
- **Security Monitoring**: Track security events and alerts
- **User Management**: View registered users and their attendance history
- **IST Timezone Support**: All timestamps displayed in Indian Standard Time (IST)

## 🛠️ Technology Stack

- **Backend**: Python 3.x
- **Computer Vision**: OpenCV 4.x with Haar Cascade Classifiers
- **Web Framework**: Flask
- **Database**: SQLite3 with custom adapters for date/time handling
- **Cryptography**: Fernet (symmetric encryption)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Timezone Handling**: pytz library

## 📁 Project Structure

```
face_attendance_system/
├── app.py                          # Flask web application
├── face_attendance.py              # Main face recognition system
├── test_setup.py                   # Installation verification script
├── clear_database.py               # Database reset utility
├── README.md                       # Project documentation
├── TODO.md                         # Development tasks
├── attendance_system.db            # SQLite database (auto-generated)
├── encryption_key.key              # Encryption key (auto-generated)
├── face_env/                       # Python virtual environment
│   ├── Scripts/                    # Windows executables
│   ├── Lib/                        # Python packages
│   └── pyvenv.cfg                  # Virtual environment config
├── templates/                      # Flask templates
│   └── dashboard.html              # Web dashboard
└── images/                         # Directory for storing images (currently empty)
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Webcam/camera device
- Windows/Linux/macOS

### Step-by-Step Installation

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd face_attendance_system
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv face_env
   ```

3. **Activate Virtual Environment**
   - **Windows**:
     ```bash
     face_env\Scripts\activate
     ```
   - **Linux/macOS**:
     ```bash
     source face_env/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install opencv-python numpy flask cryptography pytz
   ```

5. **Verify Installation**
   ```bash
   python test_setup.py
   ```
   Expected output:
   ```
   Testing installation...
   ✅ OpenCV imported successfully
   ✅ NumPy imported successfully
   ✅ SQLite3 imported successfully
   ✅ Cryptography imported successfully
   ✅ Flask imported successfully
   ✅ Camera detected successfully

   🎉 Basic setup successful!
   ```

## 🚀 Usage

### Starting the System

1. **Start the Web Dashboard**
   ```bash
   python app.py
   ```
   - Opens Flask server on `http://127.0.0.1:5000`
   - Provides web interface for monitoring

2. **Start Face Recognition** (in a separate terminal)
   ```bash
   python face_attendance.py
   ```

### System Controls

When the face recognition window is active:
- **'a' key**: Mark attendance for recognized faces (requires motion detection)
- **'e' key**: Enroll a new user
- **'q' key**: Quit the face recognition system

### User Enrollment Process

1. Press 'e' in the face recognition window
2. Enter the user's name when prompted
3. Look at the camera and press SPACE to capture face samples (30 samples recommended)
4. Press 'q' to finish enrollment

### Web Dashboard

Access the dashboard at `http://127.0.0.1:5000` to:
- View real-time statistics
- Monitor today's attendance
- Check security events
- View registered users
- See recent attendance records

## 📊 API Endpoints

The Flask application provides RESTful API endpoints:

- `GET /api/stats` - System statistics (total users, today's attendance, etc.)
- `GET /api/attendance` - Recent attendance records (last 50)
- `GET /api/users` - Registered users with attendance counts
- `GET /api/security_events` - Recent security events (last 20)
- `GET /api/attendance_today` - Today's attendance records

All timestamps are returned in IST (Indian Standard Time).

## 🔒 Security Features

### Anti-Spoofing Measures
- **Motion Detection**: Requires live motion for attendance marking
- **Face Size Validation**: Filters out distant/small faces
- **Confidence Thresholding**: Only high-confidence recognitions accepted

### Data Protection
- **Encrypted Storage**: Face data encrypted using Fernet cryptography
- **Secure Key Management**: Auto-generated encryption keys
- **Database Security**: Proper SQL injection prevention

### Event Logging
- **Security Events**: Logs unrecognized faces, spoofing attempts
- **Timestamp Tracking**: All events logged with IST timestamps
- **Severity Levels**: High, medium, low priority alerts

## 🗄️ Database Schema

### Tables

#### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    face_data BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### attendance
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'present',
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

#### security_events
```sql
CREATE TABLE security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severity TEXT DEFAULT 'medium'
);
```

## 🛠️ Troubleshooting

### Common Issues

1. **Camera Not Detected**
   - Ensure camera permissions are granted
   - Check if camera is being used by another application
   - Try different camera index in `cv2.VideoCapture(0)`

2. **Face Recognition Not Working**
   - Ensure at least one user is enrolled
   - Check lighting conditions
   - Verify face is clearly visible in camera

3. **Import Errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Database Errors**
   - Delete database: `python clear_database.py`
   - Restart the application to recreate tables

### Performance Optimization

- **Face Detection**: Adjust `minNeighbors` parameter for accuracy vs. speed trade-off
- **Recognition Threshold**: Modify confidence threshold in `run_attendance_system()`
- **Sample Count**: Reduce face samples for faster enrollment (minimum 10 recommended)

## 📈 Future Enhancements

- [ ] Mobile app integration
- [ ] Multi-camera support
- [ ] Advanced anti-spoofing (depth sensing)
- [ ] Cloud backup and synchronization
- [ ] Facial expression analysis
- [ ] Attendance analytics and reporting
- [ ] Integration with existing HR systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open-source. Please check the license file for details.

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the code comments for implementation details

## 🔄 Version History

- **v1.0.0**: Initial release with core face recognition and web dashboard
- Features: Real-time recognition, anti-spoofing, encrypted storage, IST timestamps

---

**Note**: This system is designed for educational and organizational use. Ensure compliance with privacy laws and obtain consent before implementing face recognition systems.
