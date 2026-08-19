from app.pages.employees import render_custom_schedule_dialog
from nicegui import ui

default_state = {
    "work_start": "08:00 AM",
    "break_out_1": "12:00 PM",
    "break_in_1": "01:00 PM",
    "break_out_2": "04:00 PM",
    "break_in_2": "04:30 PM",
    "work_end": "07:00 PM",
}

try:
    dlg = render_custom_schedule_dialog({}, default_state, "Test Employee")
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
