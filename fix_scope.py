import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix open_edit_dialog
edit_old = '''def open_edit_dialog(emp: dict, on_success):
    companies = _get_companies()
    form = {}

    def content(dialog):
        with ui.element("div").classes("grid-cols-2"):
            form["emp_id"] = ui.input("Employee ID *", value=emp["emp_id"]).props("outlined dense").style("width:100%;")'''

edit_new = '''def open_edit_dialog(emp: dict, on_success):
    companies = _get_companies()
    form = {}
    custom_sched_state = {}
    if emp.get("custom_schedule"):
        try: custom_sched_state.update(json.loads(emp.get("custom_schedule")))
        except: pass
        
    default_state = {
        "work_start": emp.get("work_start") or "08:00 AM",
        "break_out_1": emp.get("break_out_1") or "12:00 PM",
        "break_in_1": emp.get("break_in_1") or "12:45 PM",
        "break_out_2": emp.get("break_out_2") or "04:00 PM",
        "break_in_2": emp.get("break_in_2") or "04:30 PM",
        "work_end": emp.get("work_end") or "07:00 PM",
    }

    def content(dialog):
        with ui.element("div").classes("grid-cols-2"):
            form["emp_id"] = ui.input("Employee ID *", value=emp["emp_id"]).props("outlined dense").style("width:100%;")'''
content = content.replace(edit_old, edit_new)

edit_remove = '''        custom_sched_state = {}
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
        }'''
content = content.replace(edit_remove, "")


# Fix open_add_dialog
add_old = '''        def open_add_dialog():
            companies = _get_companies()
            form = {}
    
            def content(dialog):
                with ui.element("div").classes("grid-cols-2"):
                    form["emp_id"] = ui.input("Employee ID *").props("outlined dense").style("width:100%;")'''

add_new = '''        def open_add_dialog():
            companies = _get_companies()
            form = {}
            custom_sched_state = {}
            default_state = {
                "work_start": "08:00 AM",
                "break_out_1": "12:00 PM",
                "break_in_1": "12:45 PM",
                "break_out_2": "04:00 PM",
                "break_in_2": "04:30 PM",
                "work_end": "07:00 PM",
            }
    
            def content(dialog):
                with ui.element("div").classes("grid-cols-2"):
                    form["emp_id"] = ui.input("Employee ID *").props("outlined dense").style("width:100%;")'''
content = content.replace(add_old, add_new)

add_remove = '''                custom_sched_state = {}
                default_state = {
                    "work_start": "08:00 AM",
                    "break_out_1": "12:00 PM",
                    "break_in_1": "12:45 PM",
                    "break_out_2": "04:00 PM",
                    "break_in_2": "04:30 PM",
                    "work_end": "07:00 PM",
                }'''
content = content.replace(add_remove, "")


with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Scope fixed")
