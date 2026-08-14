"""
Employees Page — Searchable table with Add/Edit/Delete
"""
from nicegui import ui
from sqlalchemy.orm import Session

from app.pages.layout import app_layout
from app.components.modals import confirm_dialog, form_dialog
from app.components.notifications import toast_success, toast_error
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import Employee, Company, AttendanceLog


def _get_companies():
    db = SessionLocal()
    try:
        return db.query(Company).filter(Company.is_active == True).all()
    finally:
        db.close()


def _get_employees():
    db = SessionLocal()
    try:
        emps = db.query(Employee).join(Company).filter(Employee.is_active == True).all()
        return [
            {
                "id":         e.id,
                "emp_id":     e.emp_id,
                "name":       f"{e.last_name}, {e.first_name}" + (f" {e.middle_name[0]}." if e.middle_name else ""),
                "company":    e.company.name if e.company else "—",
                "department": e.department or "—",
                "position":   e.position or "—",
                "company_id": e.company_id,
                "schedule_type": getattr(e, "schedule_type", "Mon-Sat") or "Mon-Sat",
                "first_name": e.first_name,
                "last_name":  e.last_name,
                "middle_name": e.middle_name or "",
            }
            for e in emps
        ]
    finally:
        db.close()


def delete_employees(emp_ids: list[int], on_success=None):
    db: Session = SessionLocal()
    try:
        # First, delete all associated attendance logs
        db.query(AttendanceLog).filter(AttendanceLog.employee_id.in_(emp_ids)).delete(synchronize_session=False)
        
        # Then, delete the employees themselves
        db.query(Employee).filter(Employee.id.in_(emp_ids)).delete(synchronize_session=False)
        db.commit()
        toast_success("Employees Deleted", f"{len(emp_ids)} employee(s) and their logs were removed.")
        if on_success:
            on_success()
    except Exception as e:
        db.rollback()
        toast_error("Deletion Failed", str(e))
    finally:
        db.close()


def confirm_delete_emp(emp_ids: list[int], name: str, on_success=None):
    with ui.dialog().classes('backdrop-blur-sm') as dialog:
        dialog.props('persistent')
        with ui.card().style("width: 450px; max-width: 90vw; padding: 24px; border-radius: 16px;"):
            ui.html(f'''
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:40px;height:40px;border-radius:50%;background:rgba(239, 68, 68, 0.1);display:flex;align-items:center;justify-content:center;color:#ef4444;">
                    <span class="material-icons-round" style="font-size:24px;">{IC.DELETE}</span>
                </div>
                <div style="font-size:18px;font-weight:600;color:var(--text-primary);">Delete Employee(s)</div>
            </div>
            <div style="font-size:14px;color:var(--text-secondary);margin-bottom:24px;line-height:1.5;">
                Are you sure you want to delete <strong>{name}</strong>?<br><br>
                This will permanently remove the employee(s) and all their associated biometric logs.
            </div>
            ''')
            
            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=dialog.close).classes("btn btn-secondary")
                ui.button("Delete Permanently", on_click=lambda: [dialog.close(), delete_employees(emp_ids, on_success)]).classes("btn").style("background-color: #ef4444 !important; color: white !important;")
    dialog.open()


def open_edit_dialog(emp: dict, on_success):
    companies = _get_companies()
    form = {}

    def content(dialog):
        with ui.element("div").classes("grid-cols-2"):
            form["emp_id"] = ui.input("Employee ID *", value=emp["emp_id"]).props("outlined dense").style("width:100%;")
            form["first_name"] = ui.input("First Name *", value=emp["first_name"]).props("outlined dense").style("width:100%;")
        with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
            form["last_name"] = ui.input("Last Name *", value=emp["last_name"]).props("outlined dense").style("width:100%;")
            form["middle_name"] = ui.input("Middle Name", value=emp["middle_name"]).props("outlined dense").style("width:100%;")
        with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
            form["company"] = ui.select(
                {c.id: c.name for c in companies}, value=emp["company_id"], label="Company *"
            ).props("outlined dense").style("width:100%;")
            form["department"] = ui.input("Department", value=emp["department"] if emp["department"] != "—" else "").props("outlined dense").style("width:100%;")
        
        with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
            form["position"] = ui.input("Position", value=emp["position"] if emp["position"] != "—" else "").props("outlined dense").style("width:100%;")
            form["schedule"] = ui.select(
                {"Mon-Sat": "Mon - Sat", "Mon-Fri": "Mon - Fri"}, 
                value=emp.get("schedule_type", "Mon-Sat"), 
                label="Work Schedule *"
            ).props("outlined dense").style("width:100%;")

    def on_submit(dialog):
        db = SessionLocal()
        try:
            emp_obj = db.query(Employee).filter(Employee.id == emp["id"]).first()
            emp_obj.emp_id = form["emp_id"].value.strip()
            emp_obj.first_name = form["first_name"].value.strip()
            emp_obj.last_name = form["last_name"].value.strip()
            emp_obj.middle_name = form["middle_name"].value.strip() or None
            emp_obj.company_id = form["company"].value
            emp_obj.department = form["department"].value.strip() or None
            emp_obj.position = form["position"].value.strip() or None
            emp_obj.schedule_type = form["schedule"].value
            
            db.commit()
            toast_success("Employee Updated", f"{emp_obj.last_name}, {emp_obj.first_name} has been updated.")
            dialog.close()
            on_success()
        except Exception as e:
            db.rollback()
            toast_error("Error", str(e))
        finally:
            db.close()

    form_dialog("Edit Employee", content, on_submit, "Update Employee")


def employees_page():
    
    @ui.refreshable
    def history_container():
        emps = _get_employees()

        selected_emps = set()
        checkboxes = []

        def handle_success():
            history_container.refresh()

        def toggle_emp(eid, checked):
            if checked: selected_emps.add(eid)
            else: selected_emps.discard(eid)
            update_bulk_actions()

        def toggle_all(e):
            if e.value:
                selected_emps.update(emp["id"] for emp in emps)
            else:
                selected_emps.clear()
            for cb in checkboxes:
                cb.set_value(e.value)
            update_bulk_actions()

        def trigger_bulk_delete():
            if not selected_emps: return
            confirm_delete_emp(list(selected_emps), f"{len(selected_emps)} selected employees", handle_success)
            
        def open_add_dialog():
            companies = _get_companies()
            form = {}
    
            def content(dialog):
                with ui.element("div").classes("grid-cols-2"):
                    form["emp_id"] = ui.input("Employee ID *").props("outlined dense").style("width:100%;")
                    form["first_name"] = ui.input("First Name *").props("outlined dense").style("width:100%;")
                with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
                    form["last_name"] = ui.input("Last Name *").props("outlined dense").style("width:100%;")
                    form["middle_name"] = ui.input("Middle Name").props("outlined dense").style("width:100%;")
                with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
                    form["company"] = ui.select(
                        {c.id: c.name for c in companies}, label="Company *"
                    ).props("outlined dense").style("width:100%;")
                    form["department"] = ui.input("Department").props("outlined dense").style("width:100%;")
                
                with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
                    form["position"] = ui.input("Position").props("outlined dense").style("width:100%;")
                    form["schedule"] = ui.select(
                        {"Mon-Sat": "Mon - Sat", "Mon-Fri": "Mon - Fri"}, 
                        value="Mon-Sat", 
                        label="Work Schedule *"
                    ).props("outlined dense").style("width:100%;")
    
            def on_submit(dialog):
                db = SessionLocal()
                try:
                    emp_id_val = form["emp_id"].value.strip()
                    company_id_val = form["company"].value
                    
                    # Check if an inactive placeholder exists
                    existing = db.query(Employee).filter(
                        Employee.emp_id == emp_id_val, 
                        Employee.company_id == company_id_val
                    ).first()
                    
                    if existing:
                        if existing.is_active:
                            toast_error("Error", "Employee ID already exists in this company.")
                            return
                        else:
                            # Re-activate and update the placeholder!
                            existing.first_name = form["first_name"].value.strip()
                            existing.last_name = form["last_name"].value.strip()
                            existing.middle_name = form["middle_name"].value.strip() or None
                            existing.department = form["department"].value.strip() or None
                            existing.position = form["position"].value.strip() or None
                            existing.schedule_type = form["schedule"].value
                            existing.is_active = True
                            emp = existing
                    else:
                        emp = Employee(
                            emp_id=emp_id_val,
                            first_name=form["first_name"].value.strip(),
                            last_name=form["last_name"].value.strip(),
                            middle_name=form["middle_name"].value.strip() or None,
                            company_id=company_id_val,
                            department=form["department"].value.strip() or None,
                            position=form["position"].value.strip() or None,
                            schedule_type=form["schedule"].value,
                            is_active=True
                        )
                        db.add(emp)
                        
                    db.commit()
                    toast_success("Employee Added", f"{emp.last_name}, {emp.first_name} has been added.")
                    dialog.close()
                    handle_success()
                except Exception as e:
                    db.rollback()
                    toast_error("Error", str(e))
                finally:
                    db.close()
    
            form_dialog("Add Employee", content, on_submit, "Save Employee")

        with ui.element("div").classes("page-header").style("display:flex;align-items:center;justify-content:space-between;"):
            with ui.element("div"):
                ui.html('<h1 class="page-title">Employees</h1>')
                ui.html('<p class="page-subtitle">Manage employee records across all companies</p>')
            with ui.element("button").classes("btn btn-primary").on("click", open_add_dialog):
                ui.html(f'<span class="material-icons-round" style="font-size:16px;">{IC.ADD}</span> Add Employee')

        with ui.element("div").classes("card"):
            with ui.element("div").classes("card-header").style("display: flex; justify-content: space-between; align-items: center; min-height: 56px;"):
                ui.html(f'<span class="card-title">Employee Directory</span>')
                
                bulk_actions = ui.element("div").style("display: none;")
                with bulk_actions:
                    bulk_btn = ui.button("Delete Selected", icon=IC.DELETE, on_click=trigger_bulk_delete)
                    bulk_btn.props("size=sm").style("background-color: #ef4444 !important; color: white !important;")

            def update_bulk_actions():
                if len(selected_emps) > 0:
                    bulk_actions.style("display: block;")
                    bulk_btn.set_text(f"Delete Selected ({len(selected_emps)})")
                else:
                    bulk_actions.style("display: none;")

            with ui.element("div").classes("card-body").style("padding: 0; overflow-x: auto;"):
                if not emps:
                    ui.html('''
                    <div class="empty-state">
                      <span class="material-icons-round">groups</span>
                      <div class="empty-state-title">No employees found</div>
                      <div class="empty-state-subtitle">Add your first employee to get started.</div>
                    </div>
                    ''')
                else:
                    with ui.element("table").classes("data-table").style("min-width: 800px;"):
                        with ui.element("thead"):
                            with ui.element("tr"):
                                with ui.element("th").style("width: 48px; text-align: center;"):
                                    ui.checkbox(on_change=toggle_all)
                                
                                headers = [
                                    ("badge", "Employee ID"),
                                    ("person", "Full Name"),
                                    ("business", "Company"),
                                    ("work", "Department"),
                                    ("engineering", "Position"),
                                    ("settings", "Actions")
                                ]
                                for icon, col in headers:
                                    with ui.element("th"):
                                        ui.html(f'<div style="display:flex;align-items:center;gap:6px;"><span class="material-icons-round" style="font-size:16px;">{icon}</span> {col}</div>')
                        
                        with ui.element("tbody"):
                            for e in emps:
                                with ui.element("tr"):
                                    with ui.element("td").style("text-align: center;"):
                                        cb = ui.checkbox(on_change=lambda ev, eid=e["id"]: toggle_emp(eid, ev.value))
                                        checkboxes.append(cb)
                                    with ui.element("td"):
                                        ui.html(f"<strong>{e['emp_id']}</strong>")
                                    with ui.element("td"):
                                        ui.html(f"{e['name']}")
                                    with ui.element("td"):
                                        ui.html(f"{e['company']}")
                                    with ui.element("td"):
                                        ui.html(f"{e['department']}")
                                    with ui.element("td"):
                                        ui.html(f"{e['position']}")
                                    with ui.element("td"):
                                        with ui.element("div").style("display:flex; gap: 8px; align-items: center;"):
                                            ui.button(
                                                icon=IC.EDIT, 
                                                on_click=lambda e=e: open_edit_dialog(e, handle_success)
                                            ).props('flat round size=sm color="primary"').tooltip("Edit Employee")
                                            ui.button(
                                                icon=IC.DELETE, 
                                                on_click=lambda e=e: confirm_delete_emp([e["id"]], e["name"], handle_success)
                                            ).props('flat round size=sm color="negative"').style("color: #ef4444 !important;").tooltip("Delete Employee")


    with app_layout("Employees", "/employees", ["Management", "Employees"]):
        history_container()
