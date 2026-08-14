import sqlite3
import os

db_path = r"c:\xampp\htdocs\DTRSYS\data\database\dtr.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar_base64 TEXT")
        conn.commit()
        print("Successfully added avatar_base64 column.")
    except sqlite3.OperationalError as e:
        print(f"Error (possibly column already exists): {e}")
    finally:
        conn.close()
else:
    print(f"Database not found at {db_path}")
