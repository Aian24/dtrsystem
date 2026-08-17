import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_render = '''def render_custom_schedule_dialog(state_dict, default_state):
    with ui.dialog() as dlg, ui.card().style("width: 650px; max-width: 95vw; max-height: 90vh; overflow-y: auto;").classes("p-6"):
        ui.label("Employee Schedule").classes("text-xl font-black text-slate-800 mb-4")'''

new_render = '''def render_custom_schedule_dialog(state_dict, default_state, emp_name="New Employee"):
    with ui.dialog() as dlg, ui.card().style("width: 650px; max-width: 95vw; max-height: 90vh; overflow-y: auto;").classes("p-6"):
        ui.label(f"Schedule - {emp_name}").classes("text-xl font-black text-slate-800 mb-4")
        
        savers = []'''
content = content.replace(old_render, new_render)

old_def_saver = '''            def make_def_saver(s1=def_s1, s2=def_s2, s3=def_s3, s4=def_s4, s5=def_s5, s6=def_s6):
                def save_def():
                    default_state["work_start"] = s1.value
                    default_state["break_out_1"] = s2.value
                    default_state["break_in_1"] = s3.value
                    default_state["break_out_2"] = s4.value
                    default_state["break_in_2"] = s5.value
                    default_state["work_end"] = s6.value
                return save_def
            dlg.on("hide", make_def_saver())'''

new_def_saver = '''            def make_def_saver(s1=def_s1, s2=def_s2, s3=def_s3, s4=def_s4, s5=def_s5, s6=def_s6):
                def save_def():
                    default_state["work_start"] = s1.value
                    default_state["break_out_1"] = s2.value
                    default_state["break_in_1"] = s3.value
                    default_state["break_out_2"] = s4.value
                    default_state["break_in_2"] = s5.value
                    default_state["work_end"] = s6.value
                return save_def
            savers.append(make_def_saver())'''
content = content.replace(old_def_saver, new_def_saver)

old_day_saver = '''                def make_saver(d=day, e=enabled, r=is_rest, s1=ws, s2=bo1, s3=bi1, s4=bo2, s5=bi2, s6=we):
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
            ui.button("Done", on_click=dlg.close).props("unelevated color=primary px-6 rounded-md")'''

new_day_saver = '''                def make_saver(d=day, e=enabled, r=is_rest, s1=ws, s2=bo1, s3=bi1, s4=bo2, s5=bi2, s6=we):
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
            ui.button("Done", on_click=save_all_and_close).props("unelevated color=primary px-6 rounded-md")'''
content = content.replace(old_day_saver, new_day_saver)


# Fix the invocations
old_edit_call = 'sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state)'
new_edit_call = 'sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state, emp_name=f"{emp.get(\'first_name\', \'\')} {emp.get(\'last_name\', \'\')}")'
# Wait, for Add employee emp doesn't exist yet, we can use "New Employee"
# So I should only replace the one in open_edit_dialog. Let's do a smart regex or just leave Add employee as "New Employee".
# open_edit_dialog has emp passed in. open_add_dialog doesn't.
import re
# Find the first one in open_edit_dialog which is around line 150.
content = re.sub(r'sched_dlg = render_custom_schedule_dialog\(custom_sched_state, default_state\)', 
                 r'sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state, emp_name=f"{emp.get(\'first_name\', \'\')} {emp.get(\'last_name\', \'\')}")', 
                 content, count=1)


with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Save logic fixed!")
