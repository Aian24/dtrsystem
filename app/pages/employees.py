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
import json



TIME_OPTIONS = [f"{h:02d}:{m:02d} {ampm}" for ampm in ["AM", "PM"] for h in ([12] + list(range(1, 12))) for m in [0, 15, 30, 45]]

def render_custom_schedule_dialog(state_dict, default_state, emp_name="New Employee"):
    with ui.dialog() as dlg, ui.card().style("width: 650px; max-width: 95vw; max-height: 90vh; overflow-y: auto;").classes("p-6"):
        ui.label(f"Schedule - {emp_name}").classes("text-xl font-black text-slate-800 mb-4")
        
        savers = []
        
        ui.label("Default Schedule").classes("text-sm font-bold text-slate-700")
        with ui.card().classes("w-full mb-6 p-4 bg-slate-50 border border-slate-200 shadow-none"):
            with ui.element("div").classes("grid grid-cols-3 gap-3 w-full"):
                def_s1 = ui.select(TIME_OPTIONS, value=default_state.get("work_start"), label="Work Start").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s2 = ui.select(TIME_OPTIONS, value=default_state.get("break_out_1"), label="1st Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s3 = ui.select(TIME_OPTIONS, value=default_state.get("break_in_1"), label="1st Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s4 = ui.select(TIME_OPTIONS, value=default_state.get("break_out_2"), label="2nd Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s5 = ui.select(TIME_OPTIONS, value=default_state.get("break_in_2"), label="2nd Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s6 = ui.select(TIME_OPTIONS, value=default_state.get("work_end"), label="Work End").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
            
            def make_def_saver(s1=def_s1, s2=def_s2, s3=def_s3, s4=def_s4, s5=def_s5, s6=def_s6):
                def save_def():
                    default_state["work_start"] = s1.value
                    default_state["break_out_1"] = s2.value
                    default_state["break_in_1"] = s3.value
                    default_state["break_out_2"] = s4.value
                    default_state["break_in_2"] = s5.value
                    default_state["work_end"] = s6.value
                return save_def
            savers.append(make_def_saver())

        ui.label("Customize Specific Days").classes("text-sm font-bold text-slate-700 mt-2")
        ui.label("Override default schedule for specific days. Leave a day unchecked to use the default.").classes("text-xs text-slate-500 mb-4")
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            with ui.card().classes("w-full mb-3 p-3 bg-white border border-slate-200 shadow-none"):
                day_data = state_dict.get(day, {})
                
                with ui.row().classes("w-full items-center justify-between"):
                    enabled = ui.checkbox(day).props("dense size=sm").classes("font-medium text-slate-700")
                    is_rest = ui.checkbox("Set as Rest Day").props("dense size=sm color=red-5").classes("text-red-500 font-medium").bind_visibility_from(enabled, "value")
                    
                    if day in state_dict:
                        enabled.value = True
                        is_rest.value = state_dict[day].get("is_rest_day", False)
                        
                with ui.column().classes("w-full mt-3").bind_visibility_from(enabled, "value"):
                    with ui.element("div").classes("grid grid-cols-3 gap-3 w-full").bind_visibility_from(is_rest, "value", value=False):
                        ws = ui.select(TIME_OPTIONS, value=day_data.get("work_start"), label="Work Start").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bo1 = ui.select(TIME_OPTIONS, value=day_data.get("break_out_1"), label="1st Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bi1 = ui.select(TIME_OPTIONS, value=day_data.get("break_in_1"), label="1st Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bo2 = ui.select(TIME_OPTIONS, value=day_data.get("break_out_2"), label="2nd Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bi2 = ui.select(TIME_OPTIONS, value=day_data.get("break_in_2"), label="2nd Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        we = ui.select(TIME_OPTIONS, value=day_data.get("work_end"), label="Work End").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                
                # Auto-fill defaults when day is checked
                def make_on_enable(e_ui=enabled, s1_ui=ws, s2_ui=bo1, s3_ui=bi1, s4_ui=bo2, s5_ui=bi2, s6_ui=we):
                    def handle_enable():
                        if e_ui.value and not s1_ui.value: # if newly checked and blank
                            s1_ui.value = default_state.get("work_start")
                            s2_ui.value = default_state.get("break_out_1")
                            s3_ui.value = default_state.get("break_in_1")
                            s4_ui.value = default_state.get("break_out_2")
                            s5_ui.value = default_state.get("break_in_2")
                            s6_ui.value = default_state.get("work_end")
                    return handle_enable
                enabled.on("update:model-value", make_on_enable())

                def make_saver(d=day, e=enabled, r=is_rest, s1=ws, s2=bo1, s3=bi1, s4=bo2, s5=bi2, s6=we):
                    def save_day():
                        if not e.value:
                            if d in state_dict:
                                del state_dict[d]
                        else:
                            state_dict[d] = {
                                "is_rest_day": r.value,
                                "work_start": s1.value,
                                "break_out_1": s2.value,
                                "break_in_1": s3.value,
                                "break_out_2": s4.value,
                                "break_in_2": s5.value,
                                "work_end": s6.value
                            }
                    return save_day
                
                savers.append(make_saver())
                
        def save_all_and_close():
            for s in savers:
                s()
            dlg.close()
                
        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Done", on_click=save_all_and_close).props("unelevated color=primary px-6 rounded-md")
            
    return dlg

_IGNORE_TIME_OPTS_ = [f"{h:02d}:{m:02d} {ampm}" for ampm in ["AM", "PM"] for h in ([12] + list(range(1, 12))) for m in [0, 30]]
# We can also add other intervals if needed, but 30 min is standard. For this, let's use 15 min intervals.


TIME_OPTIONS = [f"{h:02d}:{m:02d} {ampm}" for ampm in ["AM", "PM"] for h in ([12] + list(range(1, 12))) for m in [0, 15, 30, 45]]

def render_custom_schedule_dialog(state_dict, default_state, emp_name="New Employee"):
    with ui.dialog() as dlg, ui.card().style("width: 650px; max-width: 95vw; max-height: 90vh; overflow-y: auto;").classes("p-6"):
        ui.label(f"Schedule - {emp_name}").classes("text-xl font-black text-slate-800 mb-4")
        
        savers = []
        
        ui.label("Default Schedule").classes("text-sm font-bold text-slate-700")
        with ui.card().classes("w-full mb-6 p-4 bg-slate-50 border border-slate-200 shadow-none"):
            with ui.element("div").classes("grid grid-cols-3 gap-3 w-full"):
                def_s1 = ui.select(TIME_OPTIONS, value=default_state.get("work_start"), label="Work Start").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s2 = ui.select(TIME_OPTIONS, value=default_state.get("break_out_1"), label="1st Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s3 = ui.select(TIME_OPTIONS, value=default_state.get("break_in_1"), label="1st Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s4 = ui.select(TIME_OPTIONS, value=default_state.get("break_out_2"), label="2nd Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s5 = ui.select(TIME_OPTIONS, value=default_state.get("break_in_2"), label="2nd Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                def_s6 = ui.select(TIME_OPTIONS, value=default_state.get("work_end"), label="Work End").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
            
            def make_def_saver(s1=def_s1, s2=def_s2, s3=def_s3, s4=def_s4, s5=def_s5, s6=def_s6):
                def save_def():
                    default_state["work_start"] = s1.value
                    default_state["break_out_1"] = s2.value
                    default_state["break_in_1"] = s3.value
                    default_state["break_out_2"] = s4.value
                    default_state["break_in_2"] = s5.value
                    default_state["work_end"] = s6.value
                return save_def
            savers.append(make_def_saver())

        ui.label("Customize Specific Days").classes("text-sm font-bold text-slate-700 mt-2")
        ui.label("Override default schedule for specific days. Leave a day unchecked to use the default.").classes("text-xs text-slate-500 mb-4")
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            with ui.card().classes("w-full mb-3 p-3 bg-white border border-slate-200 shadow-none"):
                day_data = state_dict.get(day, {})
                
                with ui.row().classes("w-full items-center justify-between"):
                    enabled = ui.checkbox(day).props("dense size=sm").classes("font-medium text-slate-700")
                    is_rest = ui.checkbox("Set as Rest Day").props("dense size=sm color=red-5").classes("text-red-500 font-medium").bind_visibility_from(enabled, "value")
                    
                    if day in state_dict:
                        enabled.value = True
                        is_rest.value = state_dict[day].get("is_rest_day", False)
                        
                with ui.column().classes("w-full mt-3").bind_visibility_from(enabled, "value"):
                    with ui.element("div").classes("grid grid-cols-3 gap-3 w-full").bind_visibility_from(is_rest, "value", value=False):
                        ws = ui.select(TIME_OPTIONS, value=day_data.get("work_start"), label="Work Start").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bo1 = ui.select(TIME_OPTIONS, value=day_data.get("break_out_1"), label="1st Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bi1 = ui.select(TIME_OPTIONS, value=day_data.get("break_in_1"), label="1st Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bo2 = ui.select(TIME_OPTIONS, value=day_data.get("break_out_2"), label="2nd Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bi2 = ui.select(TIME_OPTIONS, value=day_data.get("break_in_2"), label="2nd Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        we = ui.select(TIME_OPTIONS, value=day_data.get("work_end"), label="Work End").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                
                # Auto-fill defaults when day is checked
                def make_on_enable(e_ui=enabled, s1_ui=ws, s2_ui=bo1, s3_ui=bi1, s4_ui=bo2, s5_ui=bi2, s6_ui=we):
                    def handle_enable():
                        if e_ui.value and not s1_ui.value: # if newly checked and blank
                            s1_ui.value = default_state.get("work_start")
                            s2_ui.value = default_state.get("break_out_1")
                            s3_ui.value = default_state.get("break_in_1")
                            s4_ui.value = default_state.get("break_out_2")
                            s5_ui.value = default_state.get("break_in_2")
                            s6_ui.value = default_state.get("work_end")
                    return handle_enable
                enabled.on("update:model-value", make_on_enable())

                def make_saver(d=day, e=enabled, r=is_rest, s1=ws, s2=bo1, s3=bi1, s4=bo2, s5=bi2, s6=we):
                    def save_day():
                        if not e.value:
                            if d in state_dict:
                                del state_dict[d]
                        else:
                            state_dict[d] = {
                                "is_rest_day": r.value,
                                "work_start": s1.value,
                                "break_out_1": s2.value,
                                "break_in_1": s3.value,
                                "break_out_2": s4.value,
                                "break_in_2": s5.value,
                                "work_end": s6.value
                            }
                    return save_day
                
                savers.append(make_saver())
                
        def save_all_and_close():
            for s in savers:
                s()
            dlg.close()
                
        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Done", on_click=save_all_and_close).props("unelevated color=primary px-6 rounded-md")
            
    return dlg

_IGNORE_TIME_OPTS_ = [f"{h:02d}:{m:02d} {ampm}" for ampm in ["AM", "PM"] for h in ([12] + list(range(1, 12))) for m in [0, 15, 30, 45]]


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
                "work_start": getattr(e, "work_start", None),
                "break_out_1": getattr(e, "break_out_1", None),
                "break_in_1": getattr(e, "break_in_1", None),
                "break_out_2": getattr(e, "break_out_2", None),
                "break_in_2": getattr(e, "break_in_2", None),
                "work_end": getattr(e, "work_end", None),
                "custom_schedule": getattr(e, "custom_schedule", None),
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
    custom_sched_state = {}
    if emp.get("custom_schedule"):
        try: custom_sched_state.update(json.loads(emp.get("custom_schedule")))
        except: pass
        
    default_state = {
        "work_start": emp.get("work_start") or "08:00 AM",
        "break_out_1": emp.get("break_out_1") or "12:00 PM",
        "break_in_1": emp.get("break_in_1") or "01:00 PM",
        "break_out_2": emp.get("break_out_2") or "04:00 PM",
        "break_in_2": emp.get("break_in_2") or "04:30 PM",
        "work_end": emp.get("work_end") or "07:00 PM",
    }

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
            
        

            
        sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state, emp_name="New Employee")
        
        with ui.element("div").classes("w-full mt-2"):
            ui.button("Customize Schedule", on_click=sched_dlg.open, icon="calendar_month").props("unelevated color=primary size=md").classes("w-full font-bold rounded-lg shadow-sm")

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
            emp_obj.work_start = default_state.get("work_start")
            emp_obj.break_out_1 = default_state.get("break_out_1")
            emp_obj.break_in_1 = default_state.get("break_in_1")
            emp_obj.break_out_2 = default_state.get("break_out_2")
            emp_obj.break_in_2 = default_state.get("break_in_2")
            emp_obj.work_end = default_state.get("work_end")
            emp_obj.custom_schedule = json.dumps(custom_sched_state) if custom_sched_state else None
            
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
    table_state = {"search": "", "page": 1, "limit": 10}

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
            custom_sched_state = {}
            default_state = {
                "work_start": "08:00 AM",
                "break_out_1": "12:00 PM",
                "break_in_1": "01:00 PM",
                "break_out_2": "04:00 PM",
                "break_in_2": "04:30 PM",
                "work_end": "07:00 PM",
            }
    
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
                    
                

                sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state, emp_name="New Employee")
                with ui.element("div").classes("w-full mt-2"):
                    ui.button("Customize Schedule", on_click=sched_dlg.open, icon="calendar_month").props("unelevated color=primary size=md").classes("w-full font-bold rounded-lg shadow-sm")
    
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
                            existing.work_start = default_state.get("work_start")
                            existing.break_out_1 = default_state.get("break_out_1")
                            existing.break_in_1 = default_state.get("break_in_1")
                            existing.break_out_2 = default_state.get("break_out_2")
                            existing.break_in_2 = default_state.get("break_in_2")
                            existing.work_end = default_state.get("work_end")
                            existing.custom_schedule = json.dumps(custom_sched_state) if custom_sched_state else None
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
                            work_start=default_state.get("work_start"),
                            break_out_1=default_state.get("break_out_1"),
                            break_in_1=default_state.get("break_in_1"),
                            break_out_2=default_state.get("break_out_2"),
                            break_in_2=default_state.get("break_in_2"),
                            work_end=default_state.get("work_end"),
                            custom_schedule=json.dumps(custom_sched_state) if custom_sched_state else None,
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

            with ui.element("div").style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); gap: 16px; flex-wrap: wrap;"):
                with ui.element("div").style("display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted);"):
                    ui.html("<span>Show</span>")
                    def update_limit(e):
                        table_state["limit"] = e.value
                        table_state["page"] = 1
                        table_content.refresh()
                    ui.select(options=[10, 25, 50, 100], value=table_state["limit"], on_change=update_limit).props('dense outlined').style("width: 70px;")
                    ui.html("<span>entries</span>")
                    
                with ui.element("div"):
                    def update_search(e):
                        val = e.value or ""
                        if table_state["search"] != val:
                            table_state["search"] = val
                            table_state["page"] = 1
                            table_content.refresh()
                    ui.input(placeholder="Search...", value=table_state["search"], on_change=update_search).props('dense outlined clearable').style("width: 250px;")

            with ui.element("div").classes("card-body").style("padding: 0; overflow-x: auto;"):
                @ui.refreshable
                def table_content():
                    import math
                    term = table_state["search"].lower()
                    filtered_emps = [e for e in emps if term in e['emp_id'].lower() or term in e['name'].lower() or term in e['department'].lower() or term in e['position'].lower() or term in e['company'].lower()] if term else emps
                
                    total_items = len(filtered_emps)
                    total_pages = math.ceil(total_items / table_state["limit"]) or 1
                    if table_state["page"] > total_pages:
                        table_state["page"] = total_pages
                    
                    start_idx = (table_state["page"] - 1) * table_state["limit"]
                    end_idx = start_idx + table_state["limit"]
                    paged_emps = filtered_emps[start_idx:end_idx]


                    if not filtered_emps:
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
                                for e in paged_emps:
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

                    with ui.element("div").style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); flex-wrap: wrap; gap: 16px;"):
                        showing_start = start_idx + 1 if total_items > 0 else 0
                        showing_end = min(end_idx, total_items)
                        ui.html(f'<span style="font-size: 13px; color: var(--text-muted);">Showing {showing_start} to {showing_end} of {total_items} entries</span>')
                    
                        def update_page(e):
                            table_state["page"] = e.value
                            table_content.refresh()
                        
                        ui.pagination(1, total_pages, value=table_state["page"], on_change=update_page).props('color="primary" outline active-color="primary" active-text-color="white"')

            table_content()



    with app_layout("Employees", "/employees", ["Management", "Employees"]):
        history_container()
