import sqlite3

def init_db():
    # Initialize the database and create tables if they don't exist
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Create Students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        parent_phone TEXT NOT NULL
    )''')

    # Create Attendance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        morning_session TEXT,
        afternoon_session TEXT,
        evening_session TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
    )''')

    conn.commit()
    conn.close()

