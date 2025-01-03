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
import sqlite3
from twilio.rest import Client

# Function to create the SQLite database and table
def create_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Create a 'students' table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        parent_phone TEXT NOT NULL)''')
    
    # Create an 'attendance' table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        FOREIGN KEY(student_id) REFERENCES students(id))''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to add a student to the 'students' table
def add_student(name, parent_phone):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Insert student into the 'students' table
    cursor.execute("INSERT INTO students (name, parent_phone) VALUES (?, ?)", (name, parent_phone))
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to mark attendance for a student
def mark_attendance(student_name, status):
    # Connect to the database to get student ID
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Get the student ID for the provided student name
    cursor.execute("SELECT id, parent_phone FROM students WHERE name = ?", (student_name,))
    student = cursor.fetchone()
    
    if student:
        student_id, parent_phone = student
        # Insert attendance record into 'attendance' table
        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, DATE('now'), ?)",
                       (student_id, status))
        conn.commit()
        
        if status.lower() == 'absent':
            send_sms_notification(parent_phone, student_name)
        
        print(f"Attendance for {student_name} marked as {status}.")
    else:
        print(f"No student found with the name {student_name}.")
    
    conn.close()

# Function to send SMS notification to the parent
def send_sms_notification(parent_phone, student_name):
    # Twilio credentials (replace with your actual credentials)
    account_sid = 'AC2eab7434d658c4741725d7f111be166e'
    auth_token = '1fd00f90ada6469f0b8f237624507b09'
    client = Client(account_sid, auth_token)

    # Send the SMS
    message = client.messages.create(
        body=f"Dear Parent, your ward {student_name} was marked absent on {date.today()}. Please check.",
        from_='+your_twilio_phone_number',
        to=parent_phone
    )

    print(f"SMS sent to {parent_phone}.")

# Main function to interact with the user
def main():
    create_database()

    while True:
        action = input("Choose an action: (1) Add Student (2) Mark Attendance (3) Exit: ")
        
        if action == '1':
            name = input("Enter student name: ")
            parent_phone = input("Enter parent's phone number: ")
            add_student(name, parent_phone)
            print(f"Student {name} added to the database.")

        elif action == '2':
            student_name = input("Enter student's name: ")
            status = input("Enter attendance status (Present/Absent): ")
            mark_attendance(student_name, status)

        elif action == '3':
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
    create_database.debug = True

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

