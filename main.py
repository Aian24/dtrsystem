"""
DTR Management System — Main Entry Point
"""
import sys
import os
from pathlib import Path

# Fix for --windowed mode crashing on print()
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from fastapi import Request
from nicegui import ui, app as ngapp

# ── Ensure the project root is on sys.path (needed for PyInstaller) ────────────
if getattr(sys, 'frozen', False):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Core init ─────────────────────────────────────────────────────────────────
from app.core.database import init_db
from app.core.config import APP_NAME, APP_VERSION, APP_HOST, APP_PORT
from app.theme.styles import FONT_LINK, GLOBAL_CSS, GLOBAL_JS
from app.services.auth_service import seed_default_admin, get_current_user

from app.pages.portal     import portal_page
from app.pages.login      import login_page
from app.pages.dashboard  import dashboard_page
from app.pages.upload     import upload_page
from app.pages.employees  import employees_page
from app.pages.companies  import companies_page
from app.pages.cutoffs    import cutoffs_page
from app.pages.lookup     import lookup_page
from app.pages.preview    import preview_page
from app.pages.reports    import reports_page
from app.pages.settings   import settings_page
from app.pages.manage_logs import manage_logs_page

# ── NiceGUI App Config ─────────────────────────────────────────────────────────
SECRET_KEY = "dtr-sys-2025-secret-key-change-me"


# ── Auth guard decorator ───────────────────────────────────────────────────────
def protected(page_fn):
    """Wrap a page function with auth check."""
    def wrapper(*args, **kwargs):
        if not get_current_user():
            ui.navigate.to("/login")
            return
        page_fn(*args, **kwargs)
    return wrapper


# ── Routes ────────────────────────────────────────────────────────────────────

@ui.page("/")
def route_portal():
    portal_page()

@ui.page("/login")
def route_login():
    login_page()

@ui.page("/dashboard")
def route_dashboard():
    if not get_current_user():
        ui.navigate.to("/login")
        return
    dashboard_page()

@ui.page("/portal/preview")
async def route_portal_preview(request: Request):
    # Public preview access via portal
    preview_page(request=request, is_public=True)


@ui.page("/upload")
def route_upload():
    if not get_current_user():
        ui.navigate.to("/login"); return
    upload_page()


@ui.page("/manage-logs")
def route_manage_logs():
    if not get_current_user():
        ui.navigate.to("/login"); return
    manage_logs_page()


@ui.page("/employees")
def route_employees():
    if not get_current_user():
        ui.navigate.to("/login"); return
    employees_page()


@ui.page("/companies")
def route_companies():
    if not get_current_user():
        ui.navigate.to("/login"); return
    companies_page()


@ui.page("/cutoffs")
def route_cutoffs():
    if not get_current_user():
        ui.navigate.to("/login"); return
    cutoffs_page()


@ui.page("/lookup")
def route_lookup():
    if not get_current_user():
        ui.navigate.to("/login"); return
    lookup_page()


@ui.page("/preview")
async def route_preview(request: Request):
    if not get_current_user():
        ui.navigate.to("/login"); return
    preview_page(request=request)


@ui.page("/reports")
def route_reports():
    if not get_current_user():
        ui.navigate.to("/login"); return
    reports_page()


@ui.page("/settings")
def route_settings():
    if not get_current_user():
        ui.navigate.to("/login"); return
    settings_page()


@ui.page("/logout")
def route_logout():
    from app.services.auth_service import logout
    logout()
    ui.navigate.to("/login")


# ── Startup ────────────────────────────────────────────────────────────────────

import subprocess
import threading
import time


def main(is_main_process=True):
    print(f"[START] {APP_NAME} v{APP_VERSION}")

    # Ensure required directories exist
    (ROOT / "assets").mkdir(exist_ok=True)

    # Register static files (must be done after directory exists)
    ngapp.add_static_files("/assets", str(ROOT / "assets"))



    # Initialize database (creates tables if not exist)
    init_db()
    print("[OK] Database initialized")

    # Seed default admin user
    seed_default_admin()

    # Close PyInstaller splash screen if it's active
    try:
        import pyi_splash
        if pyi_splash.is_alive():
            pyi_splash.close()
    except Exception:
        pass

    # Launch NiceGUI
    ui.run(
        host=APP_HOST,
        port=APP_PORT,
        title=APP_NAME,
        favicon="📋",
        dark=False,
        storage_secret=SECRET_KEY,
        show=True,
        native=True,        
        window_size=(1400, 900),
        reload=False,
    )


if __name__ in ("__main__", "__mp_main__"):
    import multiprocessing
    multiprocessing.freeze_support()
    try:
        is_main = (__name__ == "__main__")
        main(is_main_process=is_main)
    except Exception as e:
        import traceback
        print("\n\nCRITICAL ERROR:")
        traceback.print_exc()
        input("\nPress Enter to close this window...")
        sys.exit(1)
