# -*- coding: utf-8 -*-
import re

with open('app/pages/companies.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"work_hours":   f"{c.work_start} - {c.work_end}",\n', '')
content = content.replace('                "_start":       c.work_start,\n                "_end":         c.work_end,\n', '')

content = content.replace('            form["start"] = ui.input("Work Start", value=row["_start"]).props("outlined dense")\n            form["end"]   = ui.input("Work End",   value=row["_end"]).props("outlined dense")', '')
content = content.replace('            form["start"] = ui.input("Work Start", value="08:00").props("outlined dense")\n            form["end"]   = ui.input("Work End",   value="17:00").props("outlined dense")', '')

content = content.replace('            co.work_start = form["start"].value.strip() or "08:00"\n            co.work_end = form["end"].value.strip() or "17:00"\n', '')

content = content.replace('                work_start=form["start"].value.strip() or "08:00",\n                work_end=form["end"].value.strip() or "17:00",\n', '')

content = content.replace('                                        ("access_time", "Work Hours"),\n', '')

content = content.replace('                                        with ui.element("td"):\n                                            ui.html(f"{r[\'work_hours\']}")\n', '')

with open('app/pages/companies.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated companies.py successfully.")
