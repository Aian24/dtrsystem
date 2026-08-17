# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Force @page margin to 0
content = content.replace('@page { margin: 0.5in; }', '@page { margin: 0; }')

# Update CSS to force body margin
css_old = '''        @media print { 
            .no-print { display: none !important; }
            .preview-card, .preview-card-body, .page-area, .nicegui-content, .preview-table-wrapper, .q-page-container, .q-page, .q-layout { 
                box-shadow: none !important; 
                border: none !important; 
                margin: 0 !important;
                max-width: none !important;
                width: 100% !important;
                padding: 0 !important;
                min-height: 0 !important;
            }'''

css_new = '''        @media print { 
            .no-print { display: none !important; }
            body, html {
                margin: 0 !important;
                padding: 0 !important;
            }
            .preview-card-body, .page-area, .nicegui-content, .preview-table-wrapper, .q-page-container, .q-page, .q-layout { 
                box-shadow: none !important; 
                border: none !important; 
                margin: 0 !important;
                max-width: none !important;
                width: 100% !important;
                padding: 0 !important;
                min-height: 0 !important;
            }
            .preview-card {
                box-shadow: none !important; 
                border: none !important; 
                margin: 0.5in !important;
                max-width: none !important;
                width: calc(100% - 1in) !important;
                padding: 0 !important;
                min-height: 0 !important;
            }'''

content = content.replace(css_old, css_new)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
