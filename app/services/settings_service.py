"""
Settings Service — Fetch and update dynamic app configurations
"""
from __future__ import annotations
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
            "auto_deduct_lunch_mins": int(config_map.get("auto_deduct_lunch_mins") or 60),
            # Biometric Device Configurations
            "biometric_ip": config_map.get("biometric_ip") or "192.168.1.201",
            "biometric_port": int(config_map.get("biometric_port") or 4370),
            "biometric_comm_key": str(config_map.get("biometric_comm_key") or "0"),
            "biometric_protocol": config_map.get("biometric_protocol") or "UDP",
        }
    except Exception as e:
        print(f"Error fetching app config: {e}")
        return {
            "app_name": DEFAULT_APP_NAME,
            "app_logo": _cached_default_logo,
            "grace_period_mins": 15,
            "standard_work_hours": 8,
            "enable_overtime": False,
            "auto_deduct_lunch_mins": 60,
            "biometric_ip": "192.168.1.201",
            "biometric_port": 4370,
            "biometric_comm_key": "0",
            "biometric_protocol": "UDP",
        }
    finally:
        db.close()


def update_app_config(
    app_name: str, 
    app_logo_base64: Optional[str] = None, 
    grace_period_mins: int = 15, 
    standard_work_hours: int = 8,
    enable_overtime: bool = False,
    auto_deduct_lunch_mins: int = 60,
    biometric_ip: Optional[str] = None,
    biometric_port: Optional[int] = None,
    biometric_comm_key: Optional[int] = None,
    biometric_protocol: Optional[str] = None,
) -> bool:
    """Update app config including name, logo, rules, and biometric device settings in DB."""
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

        if biometric_ip is not None:
            upsert_setting("biometric_ip", biometric_ip.strip())
        if biometric_port is not None:
            upsert_setting("biometric_port", biometric_port)
        if biometric_comm_key is not None:
            upsert_setting("biometric_comm_key", biometric_comm_key)
        if biometric_protocol is not None:
            upsert_setting("biometric_protocol", biometric_protocol)
                
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error updating app config: {e}")
        return False
    finally:
        db.close()


def update_biometric_config(
    ip: str,
    port: int = 4370,
    comm_key: str | int = "0",
    protocol: str = "UDP"
) -> bool:
    """Convenience helper to save biometric device connection parameters."""
    db = SessionLocal()
    try:
        def upsert_setting(key, value):
            setting = db.query(AppSetting).filter(AppSetting.key == key).first()
            if not setting:
                setting = AppSetting(key=key, value=str(value))
                db.add(setting)
            else:
                setting.value = str(value)

        upsert_setting("biometric_ip", ip.strip())
        upsert_setting("biometric_port", int(port))
        upsert_setting("biometric_comm_key", str(comm_key).strip())
        upsert_setting("biometric_protocol", protocol.strip().upper())
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving biometric config: {e}")
        return False
    finally:
        db.close()
