"""
DTR Management System
Application Configuration
"""
from __future__ import annotations
import os
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────────────
import sys

if getattr(sys, 'frozen', False):
    EXE_DIR = Path(sys.executable).resolve().parent
    BASE_DIR = Path(getattr(sys, '_MEIPASS', EXE_DIR))
else:
    EXE_DIR = Path(__file__).resolve().parent.parent.parent
    BASE_DIR = EXE_DIR

def _determine_data_dir() -> Path:
    appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
    fallback_dir = Path(appdata) / "DTR_Management_System" / "data"

    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).resolve().parent
    else:
        exe_dir = Path(__file__).resolve().parent.parent.parent

    # UNC paths (\\server\share) cannot host SQLite databases reliably via SMB locking
    exe_str = str(exe_dir)
    if exe_str.startswith(r"\\") or exe_str.startswith("//"):
        return fallback_dir

    local_data = exe_dir / "data"
    try:
        local_data.mkdir(parents=True, exist_ok=True)
        test_file = local_data / ".write_test"
        test_file.touch()
        test_file.unlink(missing_ok=True)
        return local_data
    except Exception:
        return fallback_dir

DATA_DIR = _determine_data_dir()
DATABASE_DIR = DATA_DIR / "database"
REPORTS_DIR = DATA_DIR / "reports"
LOGS_DIR = DATA_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

for _dir in [DATA_DIR, DATABASE_DIR, REPORTS_DIR, LOGS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

DATABASE_FILE = DATABASE_DIR / "dtr.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"

# ─── App Info ────────────────────────────────────────────────────────────────
APP_NAME = "DTR Management System"
APP_VERSION = "1.0.0"
APP_HOST = "127.0.0.1"
APP_PORT = 8765

# ─── Theme Colors ────────────────────────────────────────────────────────────
COLOR = {
    "primary":    "#2563EB",
    "secondary":  "#3B82F6",
    "success":    "#10B981",
    "warning":    "#F59E0B",
    "danger":     "#EF4444",
    "info":       "#6366F1",
    "bg_light":   "#F8FAFC",
    "bg_dark":    "#0F172A",
    "surface":    "#FFFFFF",
    "surface_dark": "#1E293B",
    "border":     "#E2E8F0",
    "border_dark": "#334155",
    "text_primary": "#0F172A",
    "text_secondary": "#64748B",
    "text_dark":  "#F1F5F9",
    "text_muted_dark": "#94A3B8",
}

# ─── DTR Settings ─────────────────────────────────────────────────────────────
DEFAULT_GRACE_PERIOD_MINUTES = 10
DEFAULT_WORK_START = "08:00"
DEFAULT_WORK_END   = "17:00"
