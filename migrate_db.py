from sqlalchemy import text
from app.core.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE employees ADD COLUMN work_end VARCHAR(5) NULL;"))
        db.execute(text("ALTER TABLE employees ADD COLUMN break_time_start VARCHAR(5) NULL;"))
        db.execute(text("ALTER TABLE employees ADD COLUMN break_time_end VARCHAR(5) NULL;"))
        db.commit()
        print("Migration successful.")
    except Exception as e:
        db.rollback()
        print(f"Migration failed or already applied: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    migrate()
