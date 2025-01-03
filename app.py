from flask import Flask, request, jsonify
from twilio.rest import Client
from flask import Flask, send_from_directory
import os
import sqlite3
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Twilio Configuration
TWILIO_ACCOUNT_SID = 'AC2eab7434d658c4741725d7f111be166e'  # Replace with your Twilio account SID
TWILIO_AUTH_TOKEN = '1fd00f90ada6469f0b8f237624507b09'  # Replace with your Twilio auth token
TWILIO_PHONE_NUMBER = '+12695337903'  # Replace with your Twilio phone number

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(to_number, body):
    """Function to send SMS using Twilio"""
    message = client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=to_number
    )
    return message.sid

def init_db():
    """Function to initialize the SQLite database"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY,
        name TEXT,
        parent_phone TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        morning_session TEXT,
        afternoon_session TEXT,
        evening_session TEXT,
        FOREIGN KEY (student_id) REFERENCES Students (student_id)
    )''')
    
    conn.commit()
    conn.close()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
    return "Attendance Tracker is Running"

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    """Endpoint to mark attendance for students"""
    student_id = request.form['student_id']
    date = request.form['date']
    morning = request.form['morning_session']
    afternoon = request.form['afternoon_session']
    evening = request.form['evening_session']

    # Store attendance data in SQLite database
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Attendance (student_id, date, morning_session, afternoon_session, evening_session)
    VALUES (?, ?, ?, ?, ?)
    ''', (student_id, date, morning, afternoon, evening))
    conn.commit()
    conn.close()

    return jsonify({"message": "Attendance marked successfully!"})

@app.route('/send_alerts', methods=['POST'])
def send_alerts():
    """Endpoint to send SMS alerts to parents for absences in the evening session"""
    date = request.form['date']
    
    # Query students who were absent in the evening session
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT s.name, s.parent_phone, a.date
    FROM Students s
    JOIN Attendance a ON s.student_id = a.student_id
    WHERE a.date = ? AND a.evening_session = 'absent'
    ''', (date,))
    students = cursor.fetchall()
    conn.close()

    # Send SMS alerts to parents of absent students
    for student in students:
        student_name, parent_phone, _ = student
        message_body = f"Dear Parent, your ward {student_name} was absent in the evening session on {date}. Please check."
        send_sms(parent_phone, message_body)

    return jsonify({"message": "Alerts sent successfully!"})

if __name__ == '__main__':
    init_db()  # Initialize the database when starting the app
    app.run(host='0.0.0.0', port=10000, debug=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
