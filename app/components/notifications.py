"""
Toast Notification System — Python-side helpers
Actual rendering done in JS via DTR.showToast() in styles.py
"""
from nicegui import ui


def toast_success(title: str, message: str = "", duration: int = 4000):
    ui.run_javascript(f"DTR.showToast('success', {repr(title)}, {repr(message)}, {duration})")


def toast_error(title: str, message: str = "", duration: int = 5000):
    ui.run_javascript(f"DTR.showToast('error', {repr(title)}, {repr(message)}, {duration})")


def toast_warning(title: str, message: str = "", duration: int = 4500):
    ui.run_javascript(f"DTR.showToast('warning', {repr(title)}, {repr(message)}, {duration})")


def toast_info(title: str, message: str = "", duration: int = 3500):
    ui.run_javascript(f"DTR.showToast('info', {repr(title)}, {repr(message)}, {duration})")
