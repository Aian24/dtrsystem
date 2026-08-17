# -*- coding: utf-8 -*-
import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update defaults to "01:00 PM" from "12:45 PM"
content = content.replace('"break_in_1": emp.get("break_in_1") or "12:45 PM"', '"break_in_1": emp.get("break_in_1") or "01:00 PM"')
content = content.replace('"break_in_1": "12:45 PM"', '"break_in_1": "01:00 PM"')

# 2. Add the auto-fill logic to render_custom_schedule_dialog
old_logic = '''                        bo2 = ui.select(TIME_OPTIONS, value=day_data.get("break_out_2"), label="2nd Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        bi2 = ui.select(TIME_OPTIONS, value=day_data.get("break_in_2"), label="2nd Break In").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                        we = ui.select(TIME_OPTIONS, value=day_data.get("work_end"), label="Work End").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
                
                def make_saver(d=day, e=enabled, r=is_rest, s1=ws, s2=bo1, s3=bi1, s4=bo2, s5=bi2, s6=we):'''

new_logic = '''                        bo2 = ui.select(TIME_OPTIONS, value=day_data.get("break_out_2"), label="2nd Break Out").props('outlined dense clearable options-dense popup-content-class="h-48 overflow-y-auto"')
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

                def make_saver(d=day, e=enabled, r=is_rest, s1=ws, s2=bo1, s3=bi1, s4=bo2, s5=bi2, s6=we):'''
content = content.replace(old_logic, new_logic)


# Let's also add 15-minute intervals to TIME_OPTIONS just in case they need them in the dropdown!
old_time_options = '''TIME_OPTIONS = [
    "06:00 AM", "06:30 AM", "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM", "10:00 AM", 
    "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", 
    "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM", 
    "07:30 PM", "08:00 PM", "08:30 PM", "09:00 PM", "09:30 PM", "10:00 PM"
]'''

new_time_options = '''TIME_OPTIONS = [f"{h:02d}:{m:02d} {ampm}" for ampm in ["AM", "PM"] for h in ([12] + list(range(1, 12))) for m in [0, 15, 30, 45]]'''
content = content.replace(old_time_options, new_time_options)


with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixes applied.")
