# -*- coding: utf-8 -*-
import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update edit dialog UI
edit_ui_old = '''        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["work_start"] = ui.select(TIME_OPTIONS, value=emp.get("work_start"), label="Work Start").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
            form["break_out_1"] = ui.select(TIME_OPTIONS, value=emp.get("break_out_1"), label="1st Break Out").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
            form["break_in_1"] = ui.select(TIME_OPTIONS, value=emp.get("break_in_1"), label="1st Break In").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["break_out_2"] = ui.select(TIME_OPTIONS, value=emp.get("break_out_2"), label="2nd Break Out").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
            form["break_in_2"] = ui.select(TIME_OPTIONS, value=emp.get("break_in_2"), label="2nd Break In").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
            form["work_end"] = ui.select(TIME_OPTIONS, value=emp.get("work_end"), label="Work End").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")'''

edit_ui_new = '''        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["work_start"] = ui.select(TIME_OPTIONS, value=emp.get("work_start") or "08:00 AM", label="Work Start").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
            form["break_out_1"] = ui.select(TIME_OPTIONS, value=emp.get("break_out_1") or "12:00 PM", label="1st Break Out").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
            form["break_in_1"] = ui.select(TIME_OPTIONS, value=emp.get("break_in_1") or "12:45 PM", label="1st Break In").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["break_out_2"] = ui.select(TIME_OPTIONS, value=emp.get("break_out_2") or "04:00 PM", label="2nd Break Out").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
            form["break_in_2"] = ui.select(TIME_OPTIONS, value=emp.get("break_in_2") or "04:30 PM", label="2nd Break In").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
            form["work_end"] = ui.select(TIME_OPTIONS, value=emp.get("work_end") or "07:00 PM", label="Work End").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")'''

content = content.replace(edit_ui_old, edit_ui_new)

# Update add dialog UI
add_ui_old = '''                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["work_start"] = ui.select(TIME_OPTIONS, label="Work Start").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                    form["break_out_1"] = ui.select(TIME_OPTIONS, label="1st Break Out").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                    form["break_in_1"] = ui.select(TIME_OPTIONS, label="1st Break In").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["break_out_2"] = ui.select(TIME_OPTIONS, label="2nd Break Out").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                    form["break_in_2"] = ui.select(TIME_OPTIONS, label="2nd Break In").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                    form["work_end"] = ui.select(TIME_OPTIONS, label="Work End").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")'''

add_ui_new = '''                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["work_start"] = ui.select(TIME_OPTIONS, value="08:00 AM", label="Work Start").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                    form["break_out_1"] = ui.select(TIME_OPTIONS, value="12:00 PM", label="1st Break Out").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                    form["break_in_1"] = ui.select(TIME_OPTIONS, value="12:45 PM", label="1st Break In").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["break_out_2"] = ui.select(TIME_OPTIONS, value="04:00 PM", label="2nd Break Out").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                    form["break_in_2"] = ui.select(TIME_OPTIONS, value="04:30 PM", label="2nd Break In").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")
                    form["work_end"] = ui.select(TIME_OPTIONS, value="07:00 PM", label="Work End").props('outlined dense clearable options-dense popup-content-style="max-height:250px"').style("width:100%;")'''

content = content.replace(add_ui_old, add_ui_new)


with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employees.py successfully.")
