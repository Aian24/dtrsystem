import re

with open('app/core/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_init_db = '''def init_db():
    """Create all tables if they don't exist."""
    from app.core import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate missing columns for existing SQLite DBs
    from sqlalchemy import text
    with engine.begin() as conn:
        try:
            conn.execute(text("SELECT avatar_base64 FROM users LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_base64 TEXT"))
                print("[OK] Migrated users table: added avatar_base64 column")
            except Exception as e:
                print(f"[WARN] Migration error for users.avatar_base64: {e}")

        # Migrate employees table
        columns_to_check = [
            ("schedule_type", "VARCHAR(50) DEFAULT 'Mon-Sat'"),
            ("work_start", "VARCHAR(5)"),
            ("break_out_1", "VARCHAR(5)"),
            ("break_in_1", "VARCHAR(5)"),
            ("break_out_2", "VARCHAR(5)"),
            ("break_in_2", "VARCHAR(5)"),
            ("work_end", "VARCHAR(5)"),
            ("custom_schedule", "TEXT")
        ]
        
        for col_name, col_type in columns_to_check:
            try:
                conn.execute(text(f"SELECT {col_name} FROM employees LIMIT 1"))
            except Exception:
                try:
                    conn.execute(text(f"ALTER TABLE employees ADD COLUMN {col_name} {col_type}"))
                    print(f"[OK] Migrated employees table: added {col_name} column")
                except Exception as e:
                    print(f"[WARN] Migration error for employees.{col_name}: {e}")
'''

content = re.sub(r'def init_db\(\):[\s\S]*', new_init_db, content)

with open('app/core/database.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated init_db")
