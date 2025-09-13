from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime, date
import pytz
import json

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

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('attendance_system.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_ist_date():
    """Get current date in IST"""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).date()

def get_ist_time():
    """Get current datetime in IST"""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    
    # Get total users
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    
    # Get today's attendance (IST)
    today = get_ist_date()
    today_attendance = conn.execute(
        'SELECT COUNT(*) FROM attendance WHERE date(timestamp) = ?', 
        (today,)
    ).fetchone()[0]
    
    # Get total attendance records
    total_attendance = conn.execute('SELECT COUNT(*) FROM attendance').fetchone()[0]
    
    # Get security events today (IST)
    security_events_today = conn.execute(
        'SELECT COUNT(*) FROM security_events WHERE date(timestamp) = ?', 
        (today,)
    ).fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_users': total_users,
        'today_attendance': today_attendance,
        'total_attendance': total_attendance,
        'security_events_today': security_events_today
    })

@app.route('/api/attendance')
def get_attendance():
    conn = get_db_connection()

    attendance_records = conn.execute('''
        SELECT u.name, a.timestamp, a.status
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC
        LIMIT 50
    ''').fetchall()

    conn.close()

    ist = pytz.timezone('Asia/Kolkata')
    records = []
    for record in attendance_records:
        ts_utc = datetime.fromisoformat(record['timestamp']).replace(tzinfo=pytz.UTC)
        ts_ist = ts_utc.astimezone(ist)
        records.append({
            'name': record['name'],
            'timestamp': ts_ist.isoformat(),
            'status': record['status']
        })

    return jsonify(records)

@app.route('/api/users')
def get_users():
    conn = get_db_connection()

    users = conn.execute('''
        SELECT u.name, u.created_at,
               (SELECT COUNT(*) FROM attendance WHERE user_id = u.id) as attendance_count
        FROM users u
        ORDER BY u.created_at DESC
    ''').fetchall()

    conn.close()

    ist = pytz.timezone('Asia/Kolkata')
    user_list = []
    for user in users:
        ts_utc = datetime.fromisoformat(user['created_at']).replace(tzinfo=pytz.UTC)
        ts_ist = ts_utc.astimezone(ist)
        user_list.append({
            'name': user['name'],
            'created_at': ts_ist.isoformat(),
            'attendance_count': user['attendance_count']
        })

    return jsonify(user_list)

@app.route('/api/security_events')
def get_security_events():
    conn = get_db_connection()

    events = conn.execute('''
        SELECT event_type, description, severity, timestamp
        FROM security_events
        ORDER BY timestamp DESC
        LIMIT 20
    ''').fetchall()

    conn.close()

    ist = pytz.timezone('Asia/Kolkata')
    event_list = []
    for event in events:
        ts_utc = datetime.fromisoformat(event['timestamp']).replace(tzinfo=pytz.UTC)
        ts_ist = ts_utc.astimezone(ist)
        event_list.append({
            'event_type': event['event_type'],
            'description': event['description'],
            'severity': event['severity'],
            'timestamp': ts_ist.isoformat()
        })

    return jsonify(event_list)

@app.route('/api/attendance_today')
def get_today_attendance():
    conn = get_db_connection()
    today = get_ist_date()

    attendance_today = conn.execute('''
        SELECT u.name, a.timestamp
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE date(a.timestamp) = ?
        ORDER BY a.timestamp DESC
    ''', (today,)).fetchall()

    conn.close()

    ist = pytz.timezone('Asia/Kolkata')
    records = []
    for record in attendance_today:
        ts_utc = datetime.fromisoformat(record['timestamp']).replace(tzinfo=pytz.UTC)
        ts_ist = ts_utc.astimezone(ist)
        records.append({
            'name': record['name'],
            'timestamp': ts_ist.isoformat()
        })

    return jsonify(records)

if __name__ == '__main__':
    app.run(debug=True, port=5000)