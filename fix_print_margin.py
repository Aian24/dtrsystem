# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will update the print css to remove the padding: 0 from .preview-card and add 0.5in padding to it.
css_old = '''        @media print { 
            .no-print { display: none !important; }
            body { padding: 0.5in !important; }
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
            .page-area, .nicegui-content, .preview-table-wrapper, .q-page-container, .q-page, .q-layout { 
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
                margin: 0 !important;
                max-width: none !important;
                width: 100% !important;
                padding: 0.5in !important;
                min-height: 0 !important;
            }
            .preview-card-body {
                padding: 0 !important;
                box-shadow: none !important;
                border: none !important;
            }'''

content = content.replace(css_old, css_new)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
