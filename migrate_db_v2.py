from sqlalchemy import text
from app.core.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE employees ADD COLUMN work_start VARCHAR(10) NULL;"))
        db.execute(text("ALTER TABLE employees ADD COLUMN break_out_1 VARCHAR(10) NULL;"))
        db.execute(text("ALTER TABLE employees ADD COLUMN break_in_1 VARCHAR(10) NULL;"))
        db.execute(text("ALTER TABLE employees ADD COLUMN break_out_2 VARCHAR(10) NULL;"))
        db.execute(text("ALTER TABLE employees ADD COLUMN break_in_2 VARCHAR(10) NULL;"))
        # work_end is already there, but we might want to change it. SQLite doesn't support ALTER COLUMN TYPE.
        # But SQLite ignores varchar length limits anyway.
        db.commit()
        print("Migration successful.")
    except Exception as e:
        db.rollback()
        print(f"Migration failed or already applied: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    migrate()
