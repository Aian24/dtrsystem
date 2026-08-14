"""
Authentication Service
"""
from datetime import datetime
from typing import Optional

from app.core.database import SessionLocal
from app.core.models import User
from nicegui import app as ngapp


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Verify credentials. Returns User if valid, None otherwise."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.username == username,
            User.is_active == True,
        ).first()
        if user and user.check_password(password):
            user.last_login = datetime.now()
            db.commit()
            db.refresh(user)
            db.expunge(user)
            return user
        return None
    finally:
        db.close()


def create_session(user: User) -> None:
    """Store user session in NiceGUI app storage."""
    ngapp.storage.user.update({
        "user_id":   user.id,
        "username":  user.username,
        "full_name": user.full_name or user.username,
        "role":      user.role,
        "logged_in": True,
    })


def get_current_user() -> Optional[dict]:
    """Return current session user dict or None."""
    try:
        if ngapp.storage.user.get("logged_in"):
            return dict(ngapp.storage.user)
    except Exception:
        pass
    return None


def logout() -> None:
    """Clear session."""
    ngapp.storage.user.clear()


def require_auth() -> bool:
    """Return True if user is authenticated, otherwise redirect to login."""
    from nicegui import ui
    if not get_current_user():
        ui.navigate.to("/login")
        return False
    return True


def seed_default_admin():
    """Create a default admin user if none exists."""
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username="admin",
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )
            admin.set_password("R4styL0p3z")
            db.add(admin)
            db.commit()
            print("[OK] Default admin created (admin / R4styL0p3z)")
    finally:
        db.close()
