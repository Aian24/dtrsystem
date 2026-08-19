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
            "app_logo": config_map.get("app_logo") or _cached_default_logo,
            "grace_period_mins": int(config_map.get("grace_period_mins") or 15),
            "standard_work_hours": int(config_map.get("standard_work_hours") or 8),
            "enable_overtime": config_map.get("enable_overtime") == "True",
            "auto_deduct_lunch_mins": int(config_map.get("auto_deduct_lunch_mins") or 60)
        }
    except Exception as e:
        print(f"Error fetching app config: {e}")
        return {
            "app_name": DEFAULT_APP_NAME,
            "app_logo": _cached_default_logo,
            "grace_period_mins": 15,
            "standard_work_hours": 8,
            "enable_overtime": False,
            "auto_deduct_lunch_mins": 60
        }
    finally:
        db.close()


def update_app_config(
    app_name: str, 
    app_logo_base64: Optional[str] = None, 
    grace_period_mins: int = 15, 
    standard_work_hours: int = 8,
    enable_overtime: bool = False,
    auto_deduct_lunch_mins: int = 60
) -> bool:
    """Update app config including name, logo, and rules in DB."""
    db = SessionLocal()
    try:
        def upsert_setting(key, value):
            setting = db.query(AppSetting).filter(AppSetting.key == key).first()
            if not setting:
                setting = AppSetting(key=key, value=str(value))
                db.add(setting)
            else:
                setting.value = str(value)

        upsert_setting("app_name", app_name.strip())
        upsert_setting("grace_period_mins", grace_period_mins)
        upsert_setting("standard_work_hours", standard_work_hours)
        upsert_setting("enable_overtime", enable_overtime)
        upsert_setting("auto_deduct_lunch_mins", auto_deduct_lunch_mins)
        
        if app_logo_base64 is not None:
            upsert_setting("app_logo", app_logo_base64)
                
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating app config: {e}")
        return False
    finally:
        db.close()
