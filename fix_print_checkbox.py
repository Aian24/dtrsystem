# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

css_old = '''        @media print {
            body, html, #q-app, .q-layout, .q-page-container, .q-page, .page-area, .preview-card, .preview-card-body, .nicegui-content {
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
        }'''

css_new = '''        .preview-table tr.absent-row td {
            background-color: #fef2f2 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        .preview-table tr.late-row td {
            background-color: #fff7ed !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        @media print {
            body, html, #q-app, .q-layout, .q-page-container, .q-page, .page-area, .preview-card, .preview-card-body, .nicegui-content {
                background: white !important;
                background-color: white !important;
            }
            .preview-table tr:nth-child(even) {
                background: white !important;
            }
            .preview-table tr {
                background: white !important;
            }
            .preview-table tr.absent-row td {
                background-color: #fef2f2 !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .preview-table tr.late-row td {
                background-color: #fff7ed !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
        }'''

content = content.replace(css_old, css_new)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
