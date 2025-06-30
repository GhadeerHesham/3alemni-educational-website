from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import os
import json
import time

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure CORS (Cross-Origin Resource Sharing)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5500", "http://127.0.0.1:5500"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Database configuration
DATABASE = 'attendance.db'

# ========================
# Database Helper Functions
# ========================

def get_db():
    """Get a database connection with proper error handling"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        app.logger.error(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute('''
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
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS class_rosters (
            roster_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes (class_id),
            FOREIGN KEY (student_id) REFERENCES students (student_id),
            UNIQUE (class_id, student_id)
        )''')

        cursor.execute('''
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
        )''')

        cursor.execute('''
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
        )''')

        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM classes")
        if cursor.fetchone()[0] == 0:
            insert_sample_data(cursor)
            app.logger.info("Sample data inserted successfully")

        conn.commit()
        return True

    except sqlite3.Error as e:
        app.logger.error(f"Database initialization error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def insert_sample_data(cursor):
    """Insert sample data for testing"""
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
        )''')

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

        # Sample attendance records
        attendance_records = [
            ('MATH101-2024', 'STU1001', 'SESS-001', 
             '2024-05-27T10:05:00', None, 24.7136, 46.6753, None, None,
             'auto', 'present', 5.2, 0, 1, 'On time'),
             
            ('MATH101-2024', 'STU1002', 'SESS-001', 
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

    except sqlite3.Error as e:
        app.logger.error(f"Error inserting sample data: {e}")
        raise

# =====================
# Error Handling
# =====================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "message": str(error.description) if hasattr(error, 'description') else str(error)
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": str(error.description) if hasattr(error, 'description') else str(error)
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500

# =====================
# API Routes
# =====================

@app.route('/')
def index():
    """Serve the student attendance interface"""
    return render_template('geo.html')

@app.route('/api/mark-attendance', methods=['POST'])
def mark_attendance():
    """Manually mark student attendance (teacher override)"""
    conn = None
    try:
        data = request.json
        class_id = data.get('classId')
        student_id = data.get('studentId')
        status = data.get('status')
        method = data.get('method')

        if not all([class_id, student_id, status, method]):
            abort(400, description="Missing required fields")

        conn = get_db()
        cursor = conn.cursor()

        # Get current session ID
        cursor.execute('''
            SELECT session_id FROM qr_codes 
            WHERE class_id = ?
            ORDER BY expires_at DESC 
            LIMIT 1
        ''', (class_id,))
        session = cursor.fetchone()
        session_id = session['session_id'] if session else 'MANUAL-'+datetime.now().isoformat()

        # Insert or update attendance
        cursor.execute('''
            INSERT OR REPLACE INTO attendance (
                class_id, student_id, session_id,
                check_in, check_out,
                check_in_method, status, teacher_verified
            ) VALUES (
                ?, ?, ?,
                CASE WHEN ? = 'present' THEN CURRENT_TIMESTAMP ELSE NULL END,
                CASE WHEN ? = 'absent' THEN CURRENT_TIMESTAMP ELSE NULL END,
                ?, ?, 1
            )
        ''', (
            class_id, student_id, session_id,
            status, status,
            method, status
        ))

        conn.commit()
        return jsonify({"success": True}), 200

    except sqlite3.Error as e:
        app.logger.error(f"Database error: {e}")
        abort(500)
    except Exception as e:
        app.logger.error(f"Error marking attendance: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()

@app.route('/api/check-in', methods=['POST'])
@app.route('/api/check-in', methods=['POST'])
def check_in():
    """Handle student check-in"""
    conn = None
    try:
        data = request.json
        student_id = data.get('student_id')
        lat = data.get('lat')
        lng = data.get('lng')
        method = data.get('method', 'auto')
        
        if not student_id:
            abort(400, description="Student ID is required")
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Close any existing open sessions first
        cursor.execute('''
            UPDATE attendance SET
                check_out = CURRENT_TIMESTAMP,
                check_out_lat = ?,
                check_out_lng = ?,
                early_checkout = 1,
                notes = 'Auto-closed by new check-in'
            WHERE student_id = ? 
            AND check_out IS NULL
        ''', (lat, lng, student_id))
        
        # Rest of original check-in logic here...
        # [Keep the class lookup and new check-in insertion]
        
        conn.commit()
        return jsonify({
            "success": True,
            "message": "Checked in successfully" + (" (previous session closed)" if cursor.rowcount > 0 else ""),
            "status": status
        }), 200
        
    except Exception as e:
        app.logger.error(f"Check-in error: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()

@app.route('/api/check-out', methods=['POST'])
def check_out():
    """Handle student check-out"""
    conn = None
    try:
        data = request.json
        student_id = data.get('student_id')
        lat = data.get('lat')
        lng = data.get('lng')
        
        if not student_id:
            abort(400, description="Student ID is required")
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get active check-in
        cursor.execute('''
        SELECT a.record_id, a.class_id, c.end_time 
        FROM attendance a
        JOIN classes c ON a.class_id = c.class_id
        WHERE a.student_id = ? 
        AND a.check_out IS NULL
        ORDER BY a.check_in DESC
        LIMIT 1
        ''', (student_id,))
        
        record = cursor.fetchone()
        if not record:
            abort(400, description="No active check-in found")
        
        # Check if early checkout
        early_checkout = False
        if record['end_time']:
            class_end_time = datetime.fromisoformat(record['end_time'])
            if datetime.now() < class_end_time:
                early_checkout = True
        
        # Update check-out record
        cursor.execute('''
        UPDATE attendance SET
            check_out = ?,
            check_out_lat = ?,
            check_out_lng = ?,
            early_checkout = ?
        WHERE record_id = ?
        ''', (
            datetime.now().isoformat(),
            lat, lng,
            1 if early_checkout else 0,
            record['record_id']
        ))
        
        conn.commit()
        return jsonify({
            "success": True,
            "message": "Checked out successfully",
            "early_checkout": early_checkout
        }), 200
        
    except Exception as e:
        app.logger.error(f"Check-out error: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()

@app.route('/api/attendance-history/<student_id>', methods=['GET'])
def get_attendance_history(student_id):
    """Get attendance history for a student"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            date(check_in) as date,
            time(check_in) as check_in_time,
            time(check_out) as check_out_time,
            check_in_method as method,
            status,
            CASE 
                WHEN check_out IS NULL THEN 'In Progress'
                ELSE 'Completed'
            END as session_status
        FROM attendance 
        WHERE student_id = ?
        ORDER BY check_in DESC
        LIMIT 30
        ''', (student_id,))
        
        records = [dict(row) for row in cursor.fetchall()]
        return jsonify(records), 200
        
    except Exception as e:
        app.logger.error(f"Attendance history error: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()

@app.route('/api/class-info', methods=['GET'])
def get_class_info():
    """Get information about a class"""
    conn = None
    try:
        class_id = request.args.get('classId')  # Note: Matches frontend's 'classId'
        if not class_id:
            abort(400, description="Class ID is required")
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            class_id, class_name, class_code, 
            strftime('%Y-%m-%d', start_time) as date,
            strftime('%H:%M', start_time) as start_time,
            strftime('%H:%M', end_time) as end_time,
            building, room
        FROM classes 
        WHERE class_id = ?
        ''', (class_id,))
        
        class_info = cursor.fetchone()
        if not class_info:
            abort(404, description="Class not found")
        
        return jsonify(dict(class_info)), 200
        
    except Exception as e:
        app.logger.error(f"Class info error: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()

@app.route('/api/class-attendance', methods=['GET'])
def get_class_attendance():
    """Get attendance data for a class"""
    conn = None
    try:
        class_id = request.args.get('classId')  # Note: Matches frontend's 'classId'
        if not class_id:
            abort(400, description="Class ID is required")
            
        conn = get_db()
        cursor = conn.cursor()
        
        # Get all students in class
        cursor.execute('''
        SELECT s.student_id, s.name 
        FROM students s
        JOIN class_rosters cr ON s.student_id = cr.student_id
        WHERE cr.class_id = ?
        ORDER BY s.name
        ''', (class_id,))
        
        students = [dict(row) for row in cursor.fetchall()]
        
        # Get today's attendance
        # In the existing get_class_attendance route, change the SQL to:
        cursor.execute('''
            SELECT 
                a.student_id, 
                time(a.check_in) as check_in,
                time(a.check_out) as check_out,
                a.check_in_method as method,
                a.status
            FROM attendance a
            WHERE a.class_id = ?
            AND date(a.check_in) = date('now')
        ''', (class_id,))
        
        attendance = {row['student_id']: dict(row) for row in cursor.fetchall()}
        
        # Combine data
        for student in students:
            if student['student_id'] in attendance:
                student.update(attendance[student['student_id']])
            else:
                student.update({
                    'check_in': None,
                    'check_out': None,
                    'method': None,
                    'status': 'absent'
                })
        
        # Calculate summary
        present = sum(1 for s in students if s['status'] == 'present')
        absent = sum(1 for s in students if s['status'] == 'absent')
        late = sum(1 for s in students if s['status'] == 'late')
        
        return jsonify({
            "students": students,
            "summary": {
                "present": present,
                "absent": absent,
                "late": late,
                "total": len(students)
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Class attendance error: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()

@app.route('/api/generate-qr', methods=['POST'])
def generate_qr():
    """Generate a new QR code for attendance"""
    conn = None
    try:
        data = request.json
        class_id = data.get('classId')  # Note: Matches frontend's 'classId'
        teacher_id = data.get('teacherId')
        
        if not all([class_id, teacher_id]):
            abort(400, description="Class ID and Teacher ID are required")
            
        # Generate unique session ID
        session_id = f"QR-{int(time.time())}"
        expires_at = (datetime.now() + timedelta(minutes=15)).isoformat()
        
        # QR code data
        qr_data = {
            "classId": class_id,
            "sessionId": session_id,
            "teacherId": teacher_id,
            "expiresAt": expires_at
        }
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Insert into database
        cursor.execute('''
            INSERT INTO qr_codes (
                class_id, session_id, teacher_id, 
                qr_data, expires_at, is_active
            ) VALUES (?, ?, ?, ?, ?, 1)
        ''', (
            class_id, session_id, teacher_id,
            json.dumps(qr_data), expires_at
        ))
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "qrData": qr_data,
            "sessionId": session_id,
            "expiresAt": expires_at
        }), 200
        
    except Exception as e:
        app.logger.error(f"QR generation error: {e}")
        abort(500)
    finally:
        if conn:
            conn.close()
            
@app.route('/api/checkin-status/<student_id>', methods=['GET'])
def checkin_status(student_id):
    """Check if student is currently checked in"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM attendance
            WHERE student_id = ?
            AND check_out IS NULL
        ''', (student_id,))
        
        is_checked_in = cursor.fetchone()[0] > 0
        return jsonify({"checked_in": is_checked_in}), 200
        
    except Exception as e:
        app.logger.error(f"Status check error: {e}")
        abort(500)

# =====================
# Main Execution
# =====================

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists(DATABASE):
        print("Initializing database...")
        init_db()
        print("Database initialized with sample data")
    else:
        print("Using existing database")
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)