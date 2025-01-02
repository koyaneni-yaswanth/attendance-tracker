from flask import Flask, request, jsonify
from twilio.rest import Client
import sqlite3
from datetime import datetime
from database import init_db

app = Flask(__name__)

# Twilio Configuration (replace with actual values)
TWILIO_ACCOUNT_SID = 'AC2eab7434d658c4741725d7f111be166e'
TWILIO_AUTH_TOKEN = '1fd00f90ada6469f0b8f237624507b09'
TWILIO_PHONE_NUMBER = '+12695337903'

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(to_number, body):
    """Send SMS to the specified phone number."""
    message = client.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=to_number
    )
    return message.sid

@app.route('/')
def index():
    return "Attendance Tracker is Running"

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    # Get data from request
    student_id = request.form['student_id']
    date = request.form['date']
    morning = request.form['morning_session']
    afternoon = request.form['afternoon_session']
    evening = request.form['evening_session']

    # Insert attendance into the database
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Attendance (student_id, date, morning_session, afternoon_session, evening_session)
    VALUES (?, ?, ?, ?, ?)''', (student_id, date, morning, afternoon, evening))
    conn.commit()
    conn.close()

    return jsonify({"message": "Attendance marked successfully!"})

@app.route('/send_alerts', methods=['POST'])
def send_alerts():
    date = request.form['date']
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Query absent students for the evening session
    cursor.execute("""
    SELECT s.name, s.parent_phone, a.date
    FROM Students s
    JOIN Attendance a ON s.student_id = a.student_id
    WHERE a.date = ? AND a.evening_session = 'absent'
    """, (date,))
    students = cursor.fetchall()
    conn.close()

    # Send alerts to parents of absent students
    for student in students:
        student_name, parent_phone, _ = student
        message_body = f"Dear Parent, your ward {student_name} was absent in the evening session on {date}. Please check."
        send_sms(parent_phone, message_body)

    return jsonify({"message": "Alerts sent successfully!"})

if __name__ == '__main__':
    init_db()  # Initialize the database when starting the app
    app.run(host='0.0.0.0', port=5000, debug=True)
