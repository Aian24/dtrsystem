# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

css_old = '''        @media print { 
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

css_new = '''        @media print { 
            .no-print { display: none !important; }
            body, html {
                margin: 0 !important;
                padding: 0 !important;
                background: white !important;
            }
            .page-area {
                padding: 0.5in !important;
                margin: 0 !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
                background: white !important;
            }
            .preview-card, .preview-card-body, .nicegui-content, .preview-table-wrapper, .q-page-container, .q-page, .q-layout { 
                box-shadow: none !important; 
                border: none !important; 
                margin: 0 !important;
                max-width: 100% !important;
                width: 100% !important;
                padding: 0 !important;
                min-height: 0 !important;
                box-sizing: border-box !important;
                background: transparent !important;
            }'''

content = content.replace(css_old, css_new)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
