# -*- coding: utf-8 -*-
import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update _get_employees helper to include the new fields
content = content.replace(
    '                "schedule_type": getattr(e, "schedule_type", "Mon-Sat") or "Mon-Sat",\n                "first_name": e.first_name,',
    '                "schedule_type": getattr(e, "schedule_type", "Mon-Sat") or "Mon-Sat",\n                "work_end": getattr(e, "work_end", None),\n                "break_time_start": getattr(e, "break_time_start", None),\n                "break_time_end": getattr(e, "break_time_end", None),\n                "first_name": e.first_name,'
)

# 2. Update open_edit_dialog - content
edit_dialog_old = '''        with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
            form["position"] = ui.input("Position", value=emp["position"] if emp["position"] != "—" else "").props("outlined dense").style("width:100%;")
            form["schedule"] = ui.select(
                {"Mon-Sat": "Mon - Sat", "Mon-Fri": "Mon - Fri"}, 
                value=emp.get("schedule_type", "Mon-Sat"), 
                label="Work Schedule *"
            ).props("outlined dense").style("width:100%;")'''

edit_dialog_new = '''        with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
            form["position"] = ui.input("Position", value=emp["position"] if emp["position"] != "—" else "").props("outlined dense").style("width:100%;")
            form["schedule"] = ui.select(
                {"Mon-Sat": "Mon - Sat", "Mon-Fri": "Mon - Fri"}, 
                value=emp.get("schedule_type", "Mon-Sat"), 
                label="Work Schedule *"
            ).props("outlined dense").style("width:100%;")

        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["work_end"] = ui.input("Work End (e.g. 17:00)", value=emp.get("work_end") or "").props("outlined dense").style("width:100%;")
            form["break_time_start"] = ui.input("Break Start (e.g. 16:00)", value=emp.get("break_time_start") or "").props("outlined dense").style("width:100%;")
            form["break_time_end"] = ui.input("Break End (e.g. 16:30)", value=emp.get("break_time_end") or "").props("outlined dense").style("width:100%;")'''

content = content.replace(edit_dialog_old, edit_dialog_new)

# 3. Update open_edit_dialog - on_submit
edit_submit_old = '''            emp_obj.position = form["position"].value.strip() or None
            emp_obj.schedule_type = form["schedule"].value'''
            
edit_submit_new = '''            emp_obj.position = form["position"].value.strip() or None
            emp_obj.schedule_type = form["schedule"].value
            emp_obj.work_end = form["work_end"].value.strip() or None
            emp_obj.break_time_start = form["break_time_start"].value.strip() or None
            emp_obj.break_time_end = form["break_time_end"].value.strip() or None'''

content = content.replace(edit_submit_old, edit_submit_new)

# 4. Update open_add_dialog - content
add_dialog_old = '''                  with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
                      form["position"] = ui.input("Position").props("outlined dense").style("width:100%;")
                      form["schedule"] = ui.select(
                          {"Mon-Sat": "Mon - Sat", "Mon-Fri": "Mon - Fri"}, 
                          value="Mon-Sat", 
                          label="Work Schedule *"
                      ).props("outlined dense").style("width:100%;")'''

add_dialog_new = '''                  with ui.element("div").classes("grid-cols-2").style("margin-top:14px;"):
                      form["position"] = ui.input("Position").props("outlined dense").style("width:100%;")
                      form["schedule"] = ui.select(
                          {"Mon-Sat": "Mon - Sat", "Mon-Fri": "Mon - Fri"}, 
                          value="Mon-Sat", 
                          label="Work Schedule *"
                      ).props("outlined dense").style("width:100%;")
                  
                  with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                      form["work_end"] = ui.input("Work End (e.g. 17:00)").props("outlined dense").style("width:100%;")
                      form["break_time_start"] = ui.input("Break Start (e.g. 16:00)").props("outlined dense").style("width:100%;")
                      form["break_time_end"] = ui.input("Break End (e.g. 16:30)").props("outlined dense").style("width:100%;")'''

content = content.replace(add_dialog_old, add_dialog_new)

# 5. Update open_add_dialog - on_submit (existing placeholder)
add_submit_old = '''                              existing.position = form["position"].value.strip() or None
                              existing.schedule_type = form["schedule"].value'''

add_submit_new = '''                              existing.position = form["position"].value.strip() or None
                              existing.schedule_type = form["schedule"].value
                              existing.work_end = form["work_end"].value.strip() or None
                              existing.break_time_start = form["break_time_start"].value.strip() or None
                              existing.break_time_end = form["break_time_end"].value.strip() or None'''

content = content.replace(add_submit_old, add_submit_new)

# 6. Update open_add_dialog - on_submit (new employee)
add_new_old = '''                              position=form["position"].value.strip() or None,
                              schedule_type=form["schedule"].value,
                          )'''

add_new_new = '''                              position=form["position"].value.strip() or None,
                              schedule_type=form["schedule"].value,
                              work_end=form["work_end"].value.strip() or None,
                              break_time_start=form["break_time_start"].value.strip() or None,
                              break_time_end=form["break_time_end"].value.strip() or None,
                          )'''

content = content.replace(add_new_old, add_new_new)


with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employees.py successfully.")
