import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_btn = 'ui.button("Customize Schedule", on_click=sched_dlg.open, icon="calendar_month").props("outline color=primary size=sm").classes("w-full")'
new_btn = 'ui.button("Customize Schedule", on_click=sched_dlg.open, icon="calendar_month").props("unelevated color=primary size=md").classes("w-full font-bold rounded-lg shadow-sm")'

content = content.replace(old_btn, new_btn)

with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Button fixed")
