# database.py
import sqlite3
import os
from datetime import datetime, timedelta

def init_db():
    """Initialize the database with all required tables and sample data."""
    conn = None
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create all required tables
        tables = {
            'classes': '''
                CREATE TABLE IF NOT EXISTS classes (
                    class_id TEXT PRIMARY KEY,
                    class_name TEXT NOT NULL,
                    class_code TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    building TEXT NOT NULL,
                    room TEXT NOT NULL,
                    teacher_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'students': '''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'class_rosters': '''
                CREATE TABLE IF NOT EXISTS class_rosters (
                    roster_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    FOREIGN KEY (class_id) REFERENCES classes (class_id),
                    FOREIGN KEY (student_id) REFERENCES students (student_id),
                    UNIQUE (class_id, student_id)
                )
            ''',
            'attendance': '''
                CREATE TABLE IF NOT EXISTS attendance (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    check_in TIMESTAMP,
                    check_out TIMESTAMP,
                    check_in_lat REAL,
                    check_in_lng REAL,
                    check_out_lat REAL,
                    check_out_lng REAL,
                    check_in_method TEXT NOT NULL,
                    status TEXT NOT NULL,
                    accuracy_meters REAL,
                    early_checkout BOOLEAN DEFAULT 0,
                    teacher_verified BOOLEAN DEFAULT 0,
                    notes TEXT,
                    FOREIGN KEY (class_id) REFERENCES classes (class_id),
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''',
            'qr_codes': '''
                CREATE TABLE IF NOT EXISTS qr_codes (
                    code_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    teacher_id TEXT NOT NULL,
                    qr_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (class_id) REFERENCES classes (class_id)
                )
            '''
        }
        
        for table_name, create_stmt in tables.items():
            cursor.execute(create_stmt)
        
        # Check if sample data exists
        cursor.execute("SELECT COUNT(*) FROM classes")
        if cursor.fetchone()[0] == 0:
            insert_sample_data(cursor)
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()
            
def insert_sample_data(cursor):
    """Insert sample data for testing purposes"""
    try:
        # Sample class
        cursor.execute('''
        INSERT INTO classes VALUES (
            'MATH101-2024',
            'Advanced Calculus',
            'MATH101',
            'Mon/Wed/Fri',
            '2024-05-27T10:00:00',
            '2024-05-27T12:00:00',
            'Science Building',
            '205',
            'T1001',
            CURRENT_TIMESTAMP
        )
        ''')
        
        # Sample students
        students = [
            ('STU1001', 'Ahmed Mohamed', 'ahmed@example.com'),
            ('STU1002', 'Fatima Ali', 'fatima@example.com'),
            ('STU1003', 'Youssef Hassan', 'youssef@example.com')
        ]
        cursor.executemany('''
        INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)
        ''', students)
        
        # Enroll students in class
        cursor.executemany('''
        INSERT INTO class_rosters (class_id, student_id) VALUES (?, ?)
        ''', [('MATH101-2024', sid) for sid, _, _ in students])
        
        # Sample QR code (expires in 15 minutes)
        expires_at = (datetime.now() + timedelta(minutes=15)).isoformat()
        cursor.execute('''
        INSERT INTO qr_codes (
            class_id, session_id, teacher_id, qr_data, expires_at
        ) VALUES (?, ?, ?, ?, ?)
        ''', (
            'MATH101-2024',
            'QR-20240527-AM',
            'T1001',
            '{"classId":"MATH101-2024","sessionId":"QR-20240527-AM"}',
            expires_at
        ))
        
        # Sample attendance records
        attendance_records = [
            ('MATH101-2024', 'STU1001', '20240527-AM', 
             '2024-05-27T10:05:00', None, 24.7136, 46.6753, None, None,
             'auto', 'present', 5.2, 0, 1, 'On time'),
             
            ('MATH101-2024', 'STU1002', '20240527-AM', 
             '2024-05-27T10:15:00', None, 24.7135, 46.6754, None, None,
             'qr', 'late', 8.7, 0, 0, 'Late arrival')
        ]
        
        cursor.executemany('''
        INSERT INTO attendance (
            class_id, student_id, session_id, check_in, check_out,
            check_in_lat, check_in_lng, check_out_lat, check_out_lng,
            check_in_method, status, accuracy_meters, early_checkout,
            teacher_verified, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', attendance_records)
        
        print("Sample data inserted successfully")
    except sqlite3.Error as e:
        print(f"Error inserting sample data: {e}")

if __name__ == '__main__':
    init_db()