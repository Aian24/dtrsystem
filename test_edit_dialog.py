from app.pages.employees import open_edit_dialog
from nicegui import ui

emp = {
    "id": 1,
    "emp_id": "20000",
    "first_name": "Tops",
    "last_name": "Sorilla",
    "middle_name": "",
    "company_id": 2,
    "department": "IT",
    "position": "Test",
    "schedule_type": "Mon-Fri",
}

def success(): pass

@ui.page('/')
def index():
    ui.button("Open Edit", on_click=lambda: open_edit_dialog(emp, success))

ui.run(port=8080, show=False)
