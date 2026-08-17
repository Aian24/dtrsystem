# -*- coding: utf-8 -*-

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = '''def render_custom_schedule_dialog(state_dict, default_state):
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
        ui.label("Override default schedule for specific days. Leave a day unchecked to use the default.").classes("text-xs text-slate-500 mb-2")
        
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
            
    return dlg'''


new_func = '''def render_custom_schedule_dialog(state_dict, default_state):
    with ui.dialog() as dlg, ui.card().style("width: 650px; max-width: 95vw; max-height: 90vh; overflow-y: auto;").classes("p-6"):
        ui.label("Employee Schedule").classes("text-xl font-black text-slate-800 mb-4")
        
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
            dlg.on("hide", make_def_saver())

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
            ui.button("Done", on_click=dlg.close).props("unelevated color=primary px-6 rounded-md")
            
    return dlg'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed layout")
else:
    print("old_func not found!")
