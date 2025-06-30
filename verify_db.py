# verify_db.py
import sqlite3

def verify_database():
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        print("\nTables in database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for table in cursor.fetchall():
            print(f"- {table[0]}")
            
            # Show table structure
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print(f"  Columns: {[col[1] for col in columns]}")
        
        print("\nSample Data Counts:")
        tables = ['classes', 'students', 'class_rosters', 'attendance', 'qr_codes']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"- {table}: {count} records")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_database()