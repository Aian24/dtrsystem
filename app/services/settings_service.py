"""
Settings Service — Fetch and update dynamic app configurations
"""
from typing import Dict, Any, Optional
from app.core.database import SessionLocal
from app.core.models import AppSetting

import base64
from pathlib import Path
from app.core.config import ASSETS_DIR

DEFAULT_APP_NAME = "DTR Management System"

def _get_local_default_logo() -> Optional[str]:
    try:
        p = ASSETS_DIR / "logo.png"
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        else:
            print(f"[WARN] Default logo not found at {p}")
    except Exception as e:
        print(f"[ERROR] Error loading default logo: {e}")
    return None

_cached_default_logo = _get_local_default_logo()

def get_app_config() -> Dict[str, Any]:
    """Fetch current app config from database, or return defaults."""
    db = SessionLocal()
    try:
        settings = db.query(AppSetting).all()
        config_map = {s.key: s.value for s in settings}
        
        return {
            "app_name": config_map.get("app_name") or DEFAULT_APP_NAME,
            "app_logo": config_map.get("app_logo") or _cached_default_logo
        }
    except Exception as e:
        print(f"Error fetching app config: {e}")
        return {
            "app_name": DEFAULT_APP_NAME,
            "app_logo": _cached_default_logo
        }
    finally:
        db.close()


def update_app_config(app_name: str, app_logo_base64: Optional[str] = None) -> bool:
    """Update app name and optionally app logo base64 string in DB."""
    db = SessionLocal()
    try:
        # Update or create app_name
        name_setting = db.query(AppSetting).filter(AppSetting.key == "app_name").first()
        if not name_setting:
            name_setting = AppSetting(key="app_name", value=app_name.strip())
            db.add(name_setting)
        else:
            name_setting.value = app_name.strip()
            
        # Update or create app_logo if provided
        if app_logo_base64 is not None:
            logo_setting = db.query(AppSetting).filter(AppSetting.key == "app_logo").first()
            if not logo_setting:
                logo_setting = AppSetting(key="app_logo", value=app_logo_base64)
                db.add(logo_setting)
            else:
                logo_setting.value = app_logo_base64
                
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating app config: {e}")
        return False
    finally:
        db.close()
