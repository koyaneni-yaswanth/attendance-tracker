from flask import Flask, render_template, request, jsonify
from twilio.rest import Client
import sqlite3

app = Flask(__name__)

# Twilio Configuration
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+your_twilio_number'

def send_sms(to, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=to)

# Database Initialization
def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Students (
                        student_id INTEGER PRIMARY KEY,
                        name TEXT,
                        class TEXT,
                        parent_contact TEXT)
                   ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Attendance (
                        attendance_id INTEGER PRIMARY KEY,
                        student_id INTEGER,
                        date TEXT,
                        morning_session TEXT,
                        evening_session TEXT)
                   ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    student_id = request.form['student_id']
    session = request.form['session']  # morning or evening
    status = request.form['status']  # present or absent
    
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    date = request.form['date']

    # Check if attendance already exists for this date and session
    cursor.execute(f"SELECT * FROM Attendance WHERE student_id = ? AND date = ?", (student_id, date))
    record = cursor.fetchone()

    if record:
        # Update the specific session
        if session == 'morning':
            cursor.execute("UPDATE Attendance SET morning_session = ? WHERE attendance_id = ?", (status, record[0]))
        elif session == 'evening':
            cursor.execute("UPDATE Attendance SET evening_session = ? WHERE attendance_id = ?", (status, record[0]))
    else:
        # Insert new record
        morning_status = status if session == 'morning' else 'N/A'
        evening_status = status if session == 'evening' else 'N/A'
        cursor.execute("INSERT INTO Attendance (student_id, date, morning_session, evening_session) VALUES (?, ?, ?, ?)", 
                       (student_id, date, morning_status, evening_status))

    conn.commit()
    conn.close()
    return jsonify({"message": "Attendance marked successfully!"})

@app.route('/send_alerts', methods=['POST'])
def send_alerts():
    date = request.form['date']
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Find students absent in the evening session
    cursor.execute("SELECT s.name, s.parent_contact FROM Students s \
                    JOIN Attendance a ON s.student_id = a.student_id \
                    WHERE a.date = ? AND a.evening_session = 'absent'", (date,))
    absentees = cursor.fetchall()

    for name, contact in absentees:
        message = f"Dear Parent, your ward {name} was absent in the evening session on {date}. Please check."
        send_sms(contact, message)

    conn.close()
    return jsonify({"message": "Alerts sent successfully!"})

if __name__ == '__main__':
    # To make the Flask app accessible from any device in your network:
    app.run(host='0.0.0.0', port=5000, debug=True)
