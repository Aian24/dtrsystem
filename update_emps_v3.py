# -*- coding: utf-8 -*-
import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace .props("outlined dense clearable") with .props("outlined dense clearable options-dense popup-content-style=\"max-height:250px\"")
content = content.replace('.props("outlined dense clearable")', '.props(\'outlined dense clearable options-dense popup-content-style="max-height:250px"\')')

with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employees.py successfully.")
