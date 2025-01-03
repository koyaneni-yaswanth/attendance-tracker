from flask import Flask, request, jsonify, render_template
from twilio.rest import Client
import sqlite3
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Twilio Configuration (Replace these with your credentials)
TWILIO_ACCOUNT_SID = 'AC2eab7434d658c4741725d7f111be166e'  # Replace with your Twilio account SID
TWILIO_AUTH_TOKEN = '1fd00f90ada6469f0b8f237624507b09'  # Replace with your Twilio auth token
TWILIO_PHONE_NUMBER = '+12695337903'  # Replace with your Twilio phone number

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Send SMS function
def send_sms(to_number, body):
    try:
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print(f"SMS sent to {to_number}")
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None

# Database initialization
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
        status TEXT,
        FOREIGN KEY (student_id) REFERENCES Students (student_id)
    )''')

    conn.commit()
    conn.close()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Route to mark attendance
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    student_id = request.form['student_id']
    date = request.form['date']
    status = request.form['status']

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Insert attendance record
    cursor.execute('''
        INSERT INTO Attendance (student_id, date, status)
        VALUES (?, ?, ?)
    ''', (student_id, date, status))

    conn.commit()
    conn.close()

    if status.lower() == 'absent':
        # Send SMS alert to parent
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, parent_phone FROM Students WHERE student_id = ?', (student_id,))
        student = cursor.fetchone()
        conn.close()

        if student:
            student_name, parent_phone = student
            message_body = f"Dear Parent, your ward {student_name} was marked absent on {date}. Please check."
            send_sms(parent_phone, message_body)

    return jsonify({"message": "Attendance marked and alerts sent (if necessary)."})

# Route to add student records
@app.route('/add_student', methods=['POST'])
def add_student():
    student_id = request.form['student_id']
    name = request.form['name']
    parent_phone = request.form['parent_phone']

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Insert student record
    cursor.execute('''
        INSERT INTO Students (student_id, name, parent_phone)
        VALUES (?, ?, ?)
    ''', (student_id, name, parent_phone))

    conn.commit()
    conn.close()

    return jsonify({"message": "Student added successfully!"})

# Route to view attendance records
@app.route('/view_attendance', methods=['GET'])
def view_attendance():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Fetch attendance records
    cursor.execute('''
        SELECT s.student_id, s.name, a.date, a.status
        FROM Students s
        JOIN Attendance a ON s.student_id = a.student_id
    ''')
    records = cursor.fetchall()
    conn.close()

    return jsonify(records)

# Initialize database and run app
if __name__ == '__main__':
    init_db()  # Initialize the database when starting the app
    app.run(debug=True, port=5000)
