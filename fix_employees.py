# -*- coding: utf-8 -*-
import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure json is imported
if 'import json' not in content:
    content = content.replace('from datetime import date', 'from datetime import date\nimport json')

# We'll inject a helper function at the top level
helper_ui = '''

TIME_OPTIONS = [
    "06:00 AM", "06:30 AM", "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM", "10:00 AM", 
    "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", 
    "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM", 
    "07:30 PM", "08:00 PM", "08:30 PM", "09:00 PM", "09:30 PM", "10:00 PM"
]

def render_custom_schedule_dialog(state_dict):
    with ui.dialog() as dlg, ui.card().style("width: 600px; max-width: 95vw; max-height: 90vh; overflow-y: auto;"):
        ui.label("Customize Daily Schedule").classes("text-xl font-black text-slate-800 mb-2")
        ui.label("Override default schedule for specific days. Leave a day unchecked to use the default.").classes("text-xs text-slate-500 mb-4")
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            with ui.card().classes("w-full mb-2 p-2 bg-slate-50 border border-slate-200"):
                day_data = state_dict.get(day, {})
                
                with ui.row().classes("w-full items-center justify-between"):
                    enabled = ui.checkbox(day).props("dense")
                    is_rest = ui.checkbox("Set as Rest Day").props("dense text-red-500 color=red").bind_visibility_from(enabled, "value")
                    
                    if day in state_dict:
                        enabled.value = True
                        is_rest.value = state_dict[day].get("is_rest_day", False)
                        
                with ui.column().classes("w-full mt-2").bind_visibility_from(enabled, "value"):
                    with ui.row().classes("w-full items-center").bind_visibility_from(is_rest, "value", value=False):
                        ws = ui.select(TIME_OPTIONS, value=day_data.get("work_start"), label="In").props("outlined dense clearable").style("flex:1")
                        bo1 = ui.select(TIME_OPTIONS, value=day_data.get("break_out_1"), label="BO1").props("outlined dense clearable").style("flex:1")
                        bi1 = ui.select(TIME_OPTIONS, value=day_data.get("break_in_1"), label="BI1").props("outlined dense clearable").style("flex:1")
                        bo2 = ui.select(TIME_OPTIONS, value=day_data.get("break_out_2"), label="BO2").props("outlined dense clearable").style("flex:1")
                        bi2 = ui.select(TIME_OPTIONS, value=day_data.get("break_in_2"), label="BI2").props("outlined dense clearable").style("flex:1")
                        we = ui.select(TIME_OPTIONS, value=day_data.get("work_end"), label="Out").props("outlined dense clearable").style("flex:1")
                
                # We need to bind these values back to the state dict when dialog closes
                # But ui controls in NiceGUI are stateful, so we can just grab them on close.
                # Actually, the easiest way is to bind the values back on every change, but doing it on "Save" is better.
                # To keep it simple, we store the UI elements in a local dict for this day
                # Since we are rendering, we'll just mutate state_dict directly in a save function.
                
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
                
                dlg.on("hide", make_saver())
                
        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Done", on_click=dlg.close).props("unelevated color=primary")
            
    return dlg
'''

if 'def render_custom_schedule_dialog' not in content:
    content = content.replace('TIME_OPTIONS = [', helper_ui + '\n_IGNORE_TIME_OPTS_ = [')


# 1. Edit Employee Modal
edit_str = '''            form["work_end"] = ui.select(TIME_OPTIONS, value=emp.get("work_end") or "07:00 PM", label="Work End").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")'''

edit_new = '''            form["work_end"] = ui.select(TIME_OPTIONS, value=emp.get("work_end") or "07:00 PM", label="Work End").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
        
        custom_sched_state = {}
        if emp.get("custom_schedule"):
            try: custom_sched_state = json.loads(emp.get("custom_schedule"))
            except: pass
            
        sched_dlg = render_custom_schedule_dialog(custom_sched_state)
        
        with ui.element("div").classes("w-full mt-2"):
            ui.button("Customize Daily Schedule", on_click=sched_dlg.open, icon="calendar_month").props("outline color=primary size=sm").classes("w-full")'''

content = content.replace(edit_str, edit_new)


edit_submit_str = '''            emp_obj.work_end = form["work_end"].value'''
edit_submit_new = '''            emp_obj.work_end = form["work_end"].value
            emp_obj.custom_schedule = json.dumps(custom_sched_state) if custom_sched_state else None'''
content = content.replace(edit_submit_str, edit_submit_new)


# 2. Add Employee Modal
add_str = '''                    form["work_end"] = ui.select(TIME_OPTIONS, value="07:00 PM", label="Work End").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")'''

add_new = '''                    form["work_end"] = ui.select(TIME_OPTIONS, value="07:00 PM", label="Work End").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
                    
                custom_sched_state = {}
                sched_dlg = render_custom_schedule_dialog(custom_sched_state)
                with ui.element("div").classes("w-full mt-2"):
                    ui.button("Customize Daily Schedule", on_click=sched_dlg.open, icon="calendar_month").props("outline color=primary size=sm").classes("w-full")'''

content = content.replace(add_str, add_new)

add_submit_str = '''                            existing.work_end = form["work_end"].value'''
add_submit_new = '''                            existing.work_end = form["work_end"].value
                            existing.custom_schedule = json.dumps(custom_sched_state) if custom_sched_state else None'''
content = content.replace(add_submit_str, add_submit_new)

add_submit_str2 = '''                            work_end=form["work_end"].value,'''
add_submit_new2 = '''                            work_end=form["work_end"].value,
                            custom_schedule=json.dumps(custom_sched_state) if custom_sched_state else None,'''
content = content.replace(add_submit_str2, add_submit_new2)

with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employees.py successfully.")
