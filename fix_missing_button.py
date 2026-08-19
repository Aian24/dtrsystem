import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# First, fix open_add_dialog which incorrectly got emp.get()
content = content.replace(
    'sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state, emp_name=f"{emp.get(\'first_name\', \'\')} {emp.get(\'last_name\', \'\')}")',
    'sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state, emp_name="New Employee")'
)

# Second, in open_edit_dialog, it currently has:
# sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state)
# Let's replace it properly to include emp_name
content = content.replace(
    'sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state)',
    'sched_dlg = render_custom_schedule_dialog(custom_sched_state, default_state, emp_name=f"{emp.get(\'first_name\', \'\')} {emp.get(\'last_name\', \'\')}")'
)


# Let's verify if the Customize Schedule button is inside a hidden div or something in open_edit_dialog
# By re-writing the end of open_edit_dialog's content function cleanly.

with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed")
