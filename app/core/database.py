"""
SQLAlchemy Database Engine & Session Management
"""
from __future__ import annotations
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import DATABASE_FILE, DATABASE_URL


class Base(DeclarativeBase):
    pass


# Use creator to connect cleanly to local / UNC / special paths
engine = create_engine(
    "sqlite://",
    creator=lambda: sqlite3.connect(str(DATABASE_FILE), check_same_thread=False),
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency-style DB session (use as context manager)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
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
                    
        # Migrate companies table
        company_cols = [
            ("work_start", "VARCHAR(5) DEFAULT '08:00'"),
            ("work_end", "VARCHAR(5) DEFAULT '17:00'"),
            ("area_manager", "VARCHAR(100)"),
            ("store_supervisor", "VARCHAR(100)")
        ]
        for col_name, col_type in company_cols:
            try:
                conn.execute(text(f"SELECT {col_name} FROM companies LIMIT 1"))
            except Exception:
                try:
                    conn.execute(text(f"ALTER TABLE companies ADD COLUMN {col_name} {col_type}"))
                    print(f"[OK] Migrated companies table: added {col_name} column")
                except Exception as e:
                    print(f"[WARN] Migration error for companies.{col_name}: {e}")
