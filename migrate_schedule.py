import sqlite3

def run_migration():
    conn = sqlite3.connect('data/database/dtr.db')
    cursor = conn.cursor()
    
    # Check if custom_schedule exists
    cursor.execute("PRAGMA table_info(employees)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "custom_schedule" not in columns:
        print("Adding custom_schedule column to employees table...")
        cursor.execute("ALTER TABLE employees ADD COLUMN custom_schedule TEXT DEFAULT NULL")
        conn.commit()
        print("Successfully added custom_schedule column.")
    else:
        print("Column custom_schedule already exists.")
        
    conn.close()

if __name__ == '__main__':
    run_migration()
