"""
DTR Management System
Application Configuration
"""
import os
from pathlib import Path

# ─── Paths ──────────────────────────────────────────────────────────────────
import sys

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running in normal python environment
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = DATA_DIR / "database"
REPORTS_DIR = DATA_DIR / "reports"
LOGS_DIR = DATA_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
for _dir in [DATA_DIR, DATABASE_DIR, REPORTS_DIR, LOGS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'dtr.db'}"

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
