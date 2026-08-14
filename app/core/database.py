"""
SQLAlchemy Database Engine & Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
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
    from app.core import models  # noqa: F401 — import to register models
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate missing columns for existing SQLite DBs
    from sqlalchemy import text
    with engine.begin() as conn:
        try:
            # Check if column exists by trying to select it
            conn.execute(text("SELECT avatar_base64 FROM users LIMIT 1"))
        except Exception:
            # If it fails, add the column
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar_base64 TEXT"))
                print("[OK] Migrated users table: added avatar_base64 column")
            except Exception as e:
                print(f"[WARN] Migration error for users.avatar_base64: {e}")
