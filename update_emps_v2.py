# -*- coding: utf-8 -*-
import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add TIME_OPTIONS list at the top after imports
time_opts = '''from app.core.models import Employee, Company, AttendanceLog

TIME_OPTIONS = [f"{h:02d}:{m:02d} {ampm}" for ampm in ["AM", "PM"] for h in ([12] + list(range(1, 12))) for m in [0, 30]]
# We can also add other intervals if needed, but 30 min is standard. For this, let's use 15 min intervals.
TIME_OPTIONS = [f"{h:02d}:{m:02d} {ampm}" for ampm in ["AM", "PM"] for h in ([12] + list(range(1, 12))) for m in [0, 15, 30, 45]]'''
content = content.replace('from app.core.models import Employee, Company, AttendanceLog', time_opts)

# Update _get_employees
get_emps_old = '''                "work_end": getattr(e, "work_end", None),
                "break_time_start": getattr(e, "break_time_start", None),
                "break_time_end": getattr(e, "break_time_end", None),'''
get_emps_new = '''                "work_start": getattr(e, "work_start", None),
                "break_out_1": getattr(e, "break_out_1", None),
                "break_in_1": getattr(e, "break_in_1", None),
                "break_out_2": getattr(e, "break_out_2", None),
                "break_in_2": getattr(e, "break_in_2", None),
                "work_end": getattr(e, "work_end", None),'''
content = content.replace(get_emps_old, get_emps_new)

# Update edit dialog UI
edit_ui_old = '''        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["work_end"] = ui.input("Work End (e.g. 17:00)", value=emp.get("work_end") or "").props("outlined dense").style("width:100%;")
            form["break_time_start"] = ui.input("Break Start (e.g. 16:00)", value=emp.get("break_time_start") or "").props("outlined dense").style("width:100%;")
            form["break_time_end"] = ui.input("Break End (e.g. 16:30)", value=emp.get("break_time_end") or "").props("outlined dense").style("width:100%;")'''
edit_ui_new = '''        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["work_start"] = ui.select(TIME_OPTIONS, value=emp.get("work_start"), label="Work Start").props("outlined dense clearable").style("width:100%;")
            form["break_out_1"] = ui.select(TIME_OPTIONS, value=emp.get("break_out_1"), label="1st Break Out").props("outlined dense clearable").style("width:100%;")
            form["break_in_1"] = ui.select(TIME_OPTIONS, value=emp.get("break_in_1"), label="1st Break In").props("outlined dense clearable").style("width:100%;")
        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["break_out_2"] = ui.select(TIME_OPTIONS, value=emp.get("break_out_2"), label="2nd Break Out").props("outlined dense clearable").style("width:100%;")
            form["break_in_2"] = ui.select(TIME_OPTIONS, value=emp.get("break_in_2"), label="2nd Break In").props("outlined dense clearable").style("width:100%;")
            form["work_end"] = ui.select(TIME_OPTIONS, value=emp.get("work_end"), label="Work End").props("outlined dense clearable").style("width:100%;")'''
content = content.replace(edit_ui_old, edit_ui_new)

# Update edit dialog logic
edit_submit_old = '''            emp_obj.work_end = form["work_end"].value.strip() or None
            emp_obj.break_time_start = form["break_time_start"].value.strip() or None
            emp_obj.break_time_end = form["break_time_end"].value.strip() or None'''
edit_submit_new = '''            emp_obj.work_start = form["work_start"].value
            emp_obj.break_out_1 = form["break_out_1"].value
            emp_obj.break_in_1 = form["break_in_1"].value
            emp_obj.break_out_2 = form["break_out_2"].value
            emp_obj.break_in_2 = form["break_in_2"].value
            emp_obj.work_end = form["work_end"].value'''
content = content.replace(edit_submit_old, edit_submit_new)


# Update add dialog UI
add_ui_old = '''                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["work_end"] = ui.input("Work End (e.g. 17:00)").props("outlined dense").style("width:100%;")
                    form["break_time_start"] = ui.input("Break Start (e.g. 16:00)").props("outlined dense").style("width:100%;")
                    form["break_time_end"] = ui.input("Break End (e.g. 16:30)").props("outlined dense").style("width:100%;")'''
add_ui_new = '''                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["work_start"] = ui.select(TIME_OPTIONS, label="Work Start").props("outlined dense clearable").style("width:100%;")
                    form["break_out_1"] = ui.select(TIME_OPTIONS, label="1st Break Out").props("outlined dense clearable").style("width:100%;")
                    form["break_in_1"] = ui.select(TIME_OPTIONS, label="1st Break In").props("outlined dense clearable").style("width:100%;")
                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["break_out_2"] = ui.select(TIME_OPTIONS, label="2nd Break Out").props("outlined dense clearable").style("width:100%;")
                    form["break_in_2"] = ui.select(TIME_OPTIONS, label="2nd Break In").props("outlined dense clearable").style("width:100%;")
                    form["work_end"] = ui.select(TIME_OPTIONS, label="Work End").props("outlined dense clearable").style("width:100%;")'''
content = content.replace(add_ui_old, add_ui_new)

# Update add dialog logic (existing)
add_exist_old = '''                            existing.work_end = form["work_end"].value.strip() or None
                            existing.break_time_start = form["break_time_start"].value.strip() or None
                            existing.break_time_end = form["break_time_end"].value.strip() or None'''
add_exist_new = '''                            existing.work_start = form["work_start"].value
                            existing.break_out_1 = form["break_out_1"].value
                            existing.break_in_1 = form["break_in_1"].value
                            existing.break_out_2 = form["break_out_2"].value
                            existing.break_in_2 = form["break_in_2"].value
                            existing.work_end = form["work_end"].value'''
content = content.replace(add_exist_old, add_exist_new)

# Update add dialog logic (new)
add_new_old = '''                            work_end=form["work_end"].value.strip() or None,
                            break_time_start=form["break_time_start"].value.strip() or None,
                            break_time_end=form["break_time_end"].value.strip() or None,'''
add_new_new = '''                            work_start=form["work_start"].value,
                            break_out_1=form["break_out_1"].value,
                            break_in_1=form["break_in_1"].value,
                            break_out_2=form["break_out_2"].value,
                            break_in_2=form["break_in_2"].value,
                            work_end=form["work_end"].value,'''
content = content.replace(add_new_old, add_new_new)

with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employees.py successfully.")
