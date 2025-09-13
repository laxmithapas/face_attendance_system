import cv2
import numpy as np
import sqlite3
from cryptography.fernet import Fernet
import flask

print("Testing installation...")

try:
    print("✅ OpenCV imported successfully")
    print("✅ NumPy imported successfully") 
    print("✅ SQLite3 imported successfully")
    print("✅ Cryptography imported successfully")
    print("✅ Flask imported successfully")
    
    # Test camera
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✅ Camera detected successfully")
        cap.release()
    else:
        print("⚠️ Camera not detected - but that's okay for now")
    
    print("\n🎉 Basic setup successful!")
    print("We can proceed without dlib by using OpenCV's built-in face detection.")
    
except ImportError as e:
    print(f"❌ Error: {e}")