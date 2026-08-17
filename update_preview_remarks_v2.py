# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

remarks_logic_old = '''                    table_html += f'<td>{clean(entry.get("time_out"))}</td>'
                    
                    # Only show important remarks, hide default ones like Absent/Late/Rest Day
                    r_text = entry.get("remarks", "")
                    if r_text in ["Absent", "Late", "Rest Day"]:
                        r_text = ""
                    table_html += f'<td>{clean(r_text)}</td>'
                    
                    table_html += '</tr>'
'''

remarks_logic_new = '''                    table_html += f'<td>{clean(entry.get("time_out"))}</td>'
                    table_html += f'<td></td>'
                    table_html += '</tr>'
'''

content = content.replace(remarks_logic_old, remarks_logic_new)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
