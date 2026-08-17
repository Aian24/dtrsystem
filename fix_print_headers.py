# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Change @page margin to 0
css_old_page = '''        @page { margin: 0.5in; }'''
css_new_page = '''        @page { margin: 0; }'''
content = content.replace(css_old_page, css_new_page)

# 2. Add padding to body in @media print so it doesn't touch the edges
css_old_print = '''        @media print { 
            .no-print { display: none !important; }'''

css_new_print = '''        @media print { 
            .no-print { display: none !important; }
            body { padding: 0.5in !important; }'''
content = content.replace(css_old_print, css_new_print)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
