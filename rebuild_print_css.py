# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the entire @media print block
# First find the block
old_media_start = content.find('        @media print {')
old_media_end = content.find('        </style>', old_media_start)

if old_media_start != -1 and old_media_end != -1:
    old_css = content[old_media_start:old_media_end]
    
    new_css = '''        @media print { 
            .no-print { display: none !important; }
            
            /* Hide default headers/footers by setting page margin to 0 */
            @page { margin: 0 !important; }
            
            /* Remove all background colors and shadows from layout wrappers */
            body, html, #q-app, .q-layout, .q-page-container, .q-page, .page-area, .nicegui-content {
                background: white !important;
                background-color: white !important;
                box-shadow: none !important;
                border: none !important;
            }
            
            /* Add our custom margin back via padding on the q-page wrapper */
            .q-page {
                padding: 0.5in !important;
                box-sizing: border-box !important;
                width: 100% !important;
            }
            
            /* Ensure the card itself doesn't have borders or weird margins in print */
            .preview-card {
                border: none !important;
                box-shadow: none !important;
                margin: 0 !important;
                width: 100% !important;
                max-width: 100% !important;
            }
            
            /* Keep the internal padding so the text doesn't touch the edges */
            .preview-card-body {
                padding: 0 !important; /* we remove padding here since q-page has it */
            }
            
            /* Force the red rows to print their background */
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
            
            /* Reset table rows to white to avoid gray striping */
            .preview-table tr:nth-child(even) {
                background: white !important;
            }
            .preview-table tr {
                background: white !important;
            }
        }'''
    
    content = content.replace(old_css, new_css)
    
    with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated preview.py successfully.")
else:
    print("Could not find @media print block.")
