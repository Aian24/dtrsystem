# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

css_old = '''        @media print {
            body {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
        }
        </style>'''

css_new = '''        @media print {
            body, html, .q-layout, .q-page-container, .q-page {
                background: white !important;
                background-color: white !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .preview-table tr:nth-child(even) {
                background: white !important;
            }
            .preview-table tr {
                background: white !important;
            }
            .preview-table tr.absent-row td, .preview-table tr.late-row td {
                /* we let these keep their color by being more specific */
            }
        }
        </style>'''

content = content.replace(css_old, css_new)

# Update the end body override to only apply to screen
body_old = '''        ui.html("""<style>body { background: #E2E8F0 !important; }</style>""")'''
body_new = '''        ui.html("""<style>@media screen { body { background: #E2E8F0 !important; } }</style>""")'''

content = content.replace(body_old, body_new)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
