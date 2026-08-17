# -*- coding: utf-8 -*-
import re

with open('app/pages/employees.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the broken props with Tailwind classes for height
content = content.replace(
    ".props('outlined dense clearable options-dense popup-content-style=\"max-height:250px\"')",
    ".props('outlined dense clearable options-dense options-cover=\"false\" popup-content-class=\"h-48 overflow-y-auto\"')"
)

with open('app/pages/employees.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated employees.py successfully.")
