"""
DTR Management System — Main Entry Point
"""
from __future__ import annotations
import sys
import os
import traceback
from pathlib import Path

# ── 1. Set up emergency crash logger & fatal error dialog IMMEDIATELY ──────────
def show_fatal_error(title: str, message: str):
    try:
        if os.environ.get('_PYI_SPLASH_IPC'):
            import pyi_splash
            if pyi_splash.is_alive():
                pyi_splash.close()
    except Exception:
        pass

    try:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(".")
        log_paths = [
            exe_dir / "crash.log",
            Path(os.environ.get("TEMP", ".")) / "dtr_crash.log",
            Path(os.environ.get("USERPROFILE", ".")) / "dtr_crash.log"
        ]
        for p in log_paths:
            try:
                with open(p, "a", encoding="utf-8") as f:
                    f.write(f"\n==================== CRASH AT {timestamp} ====================\n{message}\n")
            except Exception:
                pass
    except Exception:
        pass

    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, str(message)[:2500], str(title), 0x10)
    except Exception:
        pass

def _global_excepthook(exc_type, exc_value, exc_traceback):
    err = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    show_fatal_error("DTR Management System - Fatal Error", f"Unhandled startup error:\n\n{err}")

sys.excepthook = _global_excepthook

# Fix for --windowed mode crashing on print()
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

# ── Ensure the project root is on sys.path (needed for PyInstaller) ────────────
if getattr(sys, 'frozen', False):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from fastapi import Request
    from nicegui import ui, app as ngapp

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
    from app.pages.users      import users_page
except Exception:
    err = traceback.format_exc()
    show_fatal_error("DTR Management System - Import Error", f"Failed to import application modules:\n\n{err}")
    sys.exit(1)

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


@ui.page("/users")
def route_users():
    if not get_current_user():
        ui.navigate.to("/login"); return
    users_page()


@ui.page("/logout")
def route_logout():
    from app.services.auth_service import logout
    logout()
    ui.navigate.to("/login")


@ngapp.get("/manual")
def route_manual_html():
    from fastapi.responses import FileResponse
    manual_file = ROOT / "manual.html"
    return FileResponse(str(manual_file))


# ── Connection & Process Lifetime Watchdog ─────────────────────────────────────
import threading
import time

active_clients = 0
has_had_client = False
shutdown_timer: threading.Timer | None = None


def _on_client_connect():
    global active_clients, has_had_client, shutdown_timer
    active_clients += 1
    has_had_client = True
    if shutdown_timer:
        try:
            shutdown_timer.cancel()
        except Exception:
            pass
        shutdown_timer = None


def _on_client_disconnect():
    global active_clients, shutdown_timer
    active_clients = max(0, active_clients - 1)
    if has_had_client and active_clients == 0:
        if shutdown_timer:
            try:
                shutdown_timer.cancel()
            except Exception:
                pass
        # 2.5s grace period for page reloads (F5)
        shutdown_timer = threading.Timer(2.5, _trigger_shutdown)
        shutdown_timer.daemon = True
        shutdown_timer.start()


def _trigger_shutdown():
    global active_clients, has_had_client
    if has_had_client and active_clients == 0:
        print("[INFO] Application window closed by user. Terminating process...")
        try:
            ngapp.shutdown()
        except Exception:
            pass
        time.sleep(0.2)
        os._exit(0)


ngapp.on_connect(_on_client_connect)
ngapp.on_disconnect(_on_client_disconnect)


# ── Startup ────────────────────────────────────────────────────────────────────

def launch_app_window():
    """Launch the app in dedicated browser window (App Mode) or default browser."""
    import subprocess
    import webbrowser

    def _launcher():
        time.sleep(1.0)
        url = f"http://{APP_HOST}:{APP_PORT}"
        profile_dir = Path(os.environ.get("TEMP", ".")) / "dtr_app_profile"
        try:
            profile_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        
        # Look for Chrome or Edge to run in dedicated App mode (looks like a native desktop window)
        browser_candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"),
        ]
        
        for exe in browser_candidates:
            if exe and os.path.isfile(exe):
                try:
                    proc = subprocess.Popen([
                        exe,
                        f"--app={url}",
                        f"--user-data-dir={str(profile_dir)}",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--window-size=1400,900"
                    ])
                    print(f"[OK] Launched application window via: {exe} (PID {proc.pid})")
                    
                    # Dedicated window watcher: when window closes, exit process immediately
                    def _watch_proc():
                        try:
                            proc.wait()
                            print("[INFO] Main window process ended. Terminating DTR process...")
                            time.sleep(0.3)
                            os._exit(0)
                        except Exception:
                            pass
                    
                    wt = threading.Thread(target=_watch_proc, daemon=True)
                    wt.start()
                    return
                except Exception:
                    pass
        
        # Fallback to system default browser
        print(f"[INFO] Opening system default browser for: {url}")
        webbrowser.open(url)

    t = threading.Thread(target=_launcher, daemon=True)
    t.start()


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex((host, port)) == 0


def main():
    print(f"[START] {APP_NAME} v{APP_VERSION}")

    # Single-instance guard: if already running, focus existing window and exit duplicate
    if is_port_in_use(APP_PORT, APP_HOST):
        print("[INFO] Application is already running on port. Focusing existing instance...")
        try:
            if os.environ.get('_PYI_SPLASH_IPC'):
                import pyi_splash
                if pyi_splash.is_alive():
                    pyi_splash.close()
        except Exception:
            pass
        launch_app_window()
        time.sleep(1.0)
        sys.exit(0)

    # Ensure required directories exist
    (ROOT / "assets").mkdir(exist_ok=True)

    # Register static files (must be done after directory exists)
    ngapp.add_static_files("/assets", str(ROOT / "assets"))

    # Explicitly ensure NiceGUI internal static files are accessible in frozen mode
    from starlette.staticfiles import StaticFiles
    import nicegui
    
    version = getattr(nicegui, '__version__', '1.4.33') or '1.4.33'
    static_dirs = [
        Path(nicegui.__file__).parent / 'static',
        ROOT / 'nicegui' / 'static',
        ROOT / 'static',
    ]
    found_static = next((p for p in static_dirs if p.exists()), None)
    if found_static:
        try:
            ngapp.mount(f'/_nicegui/{version}/static', StaticFiles(directory=str(found_static), follow_symlink=True), name='nicegui_static_ver')
            ngapp.mount('/_nicegui/1.4.33/static', StaticFiles(directory=str(found_static), follow_symlink=True), name='nicegui_static_fixed')
            print(f"[OK] Mounted NiceGUI static files from {found_static}")
        except Exception as e:
            print(f"[INFO] Static mount notice: {e}")

    # Initialize database (creates tables if not exist)
    init_db()
    print("[OK] Database initialized")

    # Seed default admin user
    seed_default_admin()

    # Close PyInstaller splash screen if it's active
    try:
        if os.environ.get('_PYI_SPLASH_IPC'):
            import pyi_splash
            if pyi_splash.is_alive():
                pyi_splash.close()
    except Exception:
        pass

    # Launch browser window
    launch_app_window()

    # Run NiceGUI web server
    ui.run(
        host=APP_HOST,
        port=APP_PORT,
        title=APP_NAME,
        favicon="📋",
        dark=False,
        storage_secret=SECRET_KEY,
        show=False,
        native=False,
        reload=False,
    )


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    try:
        main()
    except Exception:
        import traceback
        err_msg = traceback.format_exc()
        show_fatal_error("DTR Management System - Startup Error", f"The application encountered an error while starting:\n\n{err_msg}")
        sys.exit(1)
