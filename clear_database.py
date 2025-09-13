import sqlite3
import os

# Delete database file
if os.path.exists('attendance_system.db'):
    os.remove('attendance_system.db')
    print("✅ Database deleted")

# Delete encryption key (will create new one)
if os.path.exists('encryption_key.key'):
    os.remove('encryption_key.key')
    print("✅ Encryption key deleted")

print("🎉 All user data cleared! You can now enroll fresh users.")