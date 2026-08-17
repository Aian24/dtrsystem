# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Change back the absent row color to be a very faint red
content = content.replace('background-color: #fee2e2 !important; /* bg-red-100 */', 'background-color: #fef2f2 !important; /* bg-red-50 - very faint */')
content = content.replace('background-color: #ffedd5 !important; /* bg-orange-100 */', 'background-color: #fff7ed !important; /* bg-orange-50 - very faint */')

# Remove Remarks text for Absent, Late, Rest Day
remarks_logic_old = '''                    table_html += f'<td>{clean(entry.get("time_out"))}</td>'
                    table_html += f'<td>{clean(entry.get("remarks"))}</td>'
                    table_html += '</tr>'
'''

remarks_logic_new = '''                    table_html += f'<td>{clean(entry.get("time_out"))}</td>'
                    
                    # Only show important remarks, hide default ones like Absent/Late/Rest Day
                    r_text = entry.get("remarks", "")
                    if r_text in ["Absent", "Late", "Rest Day"]:
                        r_text = ""
                    table_html += f'<td>{clean(r_text)}</td>'
                    
                    table_html += '</tr>'
'''
content = content.replace(remarks_logic_old, remarks_logic_new)


with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
