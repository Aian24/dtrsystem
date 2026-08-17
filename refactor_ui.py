# -*- coding: utf-8 -*-
import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()


# 1. Update the render_custom_schedule_dialog function
old_render = '''def render_custom_schedule_dialog(state_dict):
    with ui.dialog() as dlg, ui.card().style("width: 600px; max-width: 95vw; max-height: 90vh; overflow-y: auto;"):
        ui.label("Customize Daily Schedule").classes("text-xl font-black text-slate-800 mb-2")
        ui.label("Override default schedule for specific days. Leave a day unchecked to use the default.").classes("text-xs text-slate-500 mb-4")'''

new_render = '''def render_custom_schedule_dialog(state_dict, default_state):
    with ui.dialog() as dlg, ui.card().style("width: 600px; max-width: 95vw; max-height: 90vh; overflow-y: auto;"):
        ui.label("Employee Schedule").classes("text-xl font-black text-slate-800 mb-2")
        
        ui.label("Default Schedule").classes("text-sm font-bold mt-2")
        with ui.card().classes("w-full mb-4 p-2 bg-slate-50 border border-slate-200"):
            with ui.row().classes("w-full items-center"):
                def_s1 = ui.select(TIME_OPTIONS, value=default_state.get("work_start"), label="In").props("outlined dense clearable").style("flex:1")
                def_s2 = ui.select(TIME_OPTIONS, value=default_state.get("break_out_1"), label="BO1").props("outlined dense clearable").style("flex:1")
                def_s3 = ui.select(TIME_OPTIONS, value=default_state.get("break_in_1"), label="BI1").props("outlined dense clearable").style("flex:1")
                def_s4 = ui.select(TIME_OPTIONS, value=default_state.get("break_out_2"), label="BO2").props("outlined dense clearable").style("flex:1")
                def_s5 = ui.select(TIME_OPTIONS, value=default_state.get("break_in_2"), label="BI2").props("outlined dense clearable").style("flex:1")
                def_s6 = ui.select(TIME_OPTIONS, value=default_state.get("work_end"), label="Out").props("outlined dense clearable").style("flex:1")
            
            def make_def_saver(s1=def_s1, s2=def_s2, s3=def_s3, s4=def_s4, s5=def_s5, s6=def_s6):
                def save_def():
                    default_state["work_start"] = s1.value
                    default_state["break_out_1"] = s2.value
                    default_state["break_in_1"] = s3.value
                    default_state["break_out_2"] = s4.value
                    default_state["break_in_2"] = s5.value
                    default_state["work_end"] = s6.value
                return save_def
            dlg.on("hide", make_def_saver())

        ui.label("Customize Specific Days").classes("text-sm font-bold mt-2")
        ui.label("Override default schedule for specific days. Leave a day unchecked to use the default.").classes("text-xs text-slate-500 mb-2")'''
content = content.replace(old_render, new_render)


# 2. Remove default fields from Edit Modal and inject default_state
edit_old_ui = '''        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["work_start"] = ui.select(TIME_OPTIONS, value=emp.get("work_start") or "08:00 AM", label="Work Start").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
            form["break_out_1"] = ui.select(TIME_OPTIONS, value=emp.get("break_out_1") or "12:00 PM", label="1st Break Out").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
            form["break_in_1"] = ui.select(TIME_OPTIONS, value=emp.get("break_in_1") or "12:45 PM", label="1st Break In").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
        with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
            form["break_out_2"] = ui.select(TIME_OPTIONS, value=emp.get("break_out_2") or "04:00 PM", label="2nd Break Out").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
            form["break_in_2"] = ui.select(TIME_OPTIONS, value=emp.get("break_in_2") or "04:30 PM", label="2nd Break In").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
            form["work_end"] = ui.select(TIME_OPTIONS, value=emp.get("work_end") or "07:00 PM", label="Work End").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
        
        custom_sched_state = {}
        if emp.get("custom_schedule"):
            try: custom_sched_state = json.loads(emp.get("custom_schedule"))
            except: pass
            
        sched_dlg = render_custom_schedule_dialog(custom_sched_state)
        
        with ui.element("div").classes("w-full mt-2"):
            ui.button("Customize Daily Schedule", on_click=sched_dlg.open, icon="calendar_month").props("outline color=primary size=sm").classes("w-full")'''

edit_new_ui = '''        
        custom_sched_state = {}
        if emp.get("custom_schedule"):
            try: custom_sched_state = json.loads(emp.get("custom_schedule"))
            except: pass
            
        default_state = {
            "work_start": emp.get("work_start") or "08:00 AM",
            "break_out_1": emp.get("break_out_1") or "12:00 PM",
            "break_in_1": emp.get("break_in_1") or "12:45 PM",
            "break_out_2": emp.get("break_out_2") or "04:00 PM",
            "break_in_2": emp.get("break_in_2") or "04:30 PM",
            "work_end": emp.get("work_end") or "07:00 PM",
        }
            
        sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state)
        
        with ui.element("div").classes("w-full mt-2"):
            ui.button("Customize Schedule", on_click=sched_dlg.open, icon="calendar_month").props("outline color=primary size=sm").classes("w-full")'''
content = content.replace(edit_old_ui, edit_new_ui)

edit_submit_old = '''            emp_obj.work_start = form["work_start"].value
            emp_obj.break_out_1 = form["break_out_1"].value
            emp_obj.break_in_1 = form["break_in_1"].value
            emp_obj.break_out_2 = form["break_out_2"].value
            emp_obj.break_in_2 = form["break_in_2"].value
            emp_obj.work_end = form["work_end"].value
            emp_obj.custom_schedule = json.dumps(custom_sched_state) if custom_sched_state else None'''

edit_submit_new = '''            emp_obj.work_start = default_state.get("work_start")
            emp_obj.break_out_1 = default_state.get("break_out_1")
            emp_obj.break_in_1 = default_state.get("break_in_1")
            emp_obj.break_out_2 = default_state.get("break_out_2")
            emp_obj.break_in_2 = default_state.get("break_in_2")
            emp_obj.work_end = default_state.get("work_end")
            emp_obj.custom_schedule = json.dumps(custom_sched_state) if custom_sched_state else None'''
content = content.replace(edit_submit_old, edit_submit_new)


# 3. Remove default fields from Add Modal and inject default_state
add_old_ui = '''                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["work_start"] = ui.select(TIME_OPTIONS, value="08:00 AM", label="Work Start").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
                    form["break_out_1"] = ui.select(TIME_OPTIONS, value="12:00 PM", label="1st Break Out").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
                    form["break_in_1"] = ui.select(TIME_OPTIONS, value="12:45 PM", label="1st Break In").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
                with ui.element("div").classes("grid-cols-3").style("margin-top:14px; gap:8px;"):
                    form["break_out_2"] = ui.select(TIME_OPTIONS, value="04:00 PM", label="2nd Break Out").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
                    form["break_in_2"] = ui.select(TIME_OPTIONS, value="04:30 PM", label="2nd Break In").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
                    form["work_end"] = ui.select(TIME_OPTIONS, value="07:00 PM", label="Work End").props('outlined dense clearable options-dense options-cover="false" popup-content-class="h-48 overflow-y-auto"').style("width:100%;")
                    
                custom_sched_state = {}
                sched_dlg = render_custom_schedule_dialog(custom_sched_state)
                with ui.element("div").classes("w-full mt-2"):
                    ui.button("Customize Daily Schedule", on_click=sched_dlg.open, icon="calendar_month").props("outline color=primary size=sm").classes("w-full")'''

add_new_ui = '''                
                custom_sched_state = {}
                default_state = {
                    "work_start": "08:00 AM",
                    "break_out_1": "12:00 PM",
                    "break_in_1": "12:45 PM",
                    "break_out_2": "04:00 PM",
                    "break_in_2": "04:30 PM",
                    "work_end": "07:00 PM",
                }
                sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state)
                with ui.element("div").classes("w-full mt-2"):
                    ui.button("Customize Schedule", on_click=sched_dlg.open, icon="calendar_month").props("outline color=primary size=sm").classes("w-full")'''
content = content.replace(add_old_ui, add_new_ui)

add_submit_old1 = '''                            existing.work_start = form["work_start"].value
                            existing.break_out_1 = form["break_out_1"].value
                            existing.break_in_1 = form["break_in_1"].value
                            existing.break_out_2 = form["break_out_2"].value
                            existing.break_in_2 = form["break_in_2"].value
                            existing.work_end = form["work_end"].value
                            existing.custom_schedule = json.dumps(custom_sched_state) if custom_sched_state else None'''

add_submit_new1 = '''                            existing.work_start = default_state.get("work_start")
                            existing.break_out_1 = default_state.get("break_out_1")
                            existing.break_in_1 = default_state.get("break_in_1")
                            existing.break_out_2 = default_state.get("break_out_2")
                            existing.break_in_2 = default_state.get("break_in_2")
                            existing.work_end = default_state.get("work_end")
                            existing.custom_schedule = json.dumps(custom_sched_state) if custom_sched_state else None'''
content = content.replace(add_submit_old1, add_submit_new1)

add_submit_old2 = '''                            work_start=form["work_start"].value,
                            break_out_1=form["break_out_1"].value,
                            break_in_1=form["break_in_1"].value,
                            break_out_2=form["break_out_2"].value,
                            break_in_2=form["break_in_2"].value,
                            work_end=form["work_end"].value,
                            custom_schedule=json.dumps(custom_sched_state) if custom_sched_state else None,'''

add_submit_new2 = '''                            work_start=default_state.get("work_start"),
                            break_out_1=default_state.get("break_out_1"),
                            break_in_1=default_state.get("break_in_1"),
                            break_out_2=default_state.get("break_out_2"),
                            break_in_2=default_state.get("break_in_2"),
                            work_end=default_state.get("work_end"),
                            custom_schedule=json.dumps(custom_sched_state) if custom_sched_state else None,'''
content = content.replace(add_submit_old2, add_submit_new2)

with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employees.py to centralize schedule successfully.")
