# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the specific print backgrounds
css_old = '''        @media print {
            body, html, .q-layout, .q-page-container, .q-page {
                background: white !important;
                background-color: white !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }'''

css_new = '''        @media print {
            body, html, #q-app, .q-layout, .q-page-container, .q-page, .page-area, .preview-card, .preview-card-body, .nicegui-content {
                background: white !important;
                background-color: white !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }'''

content = content.replace(css_old, css_new)


with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
