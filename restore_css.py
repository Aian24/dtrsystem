# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

missing_css = '''
        .preview-table {
            width: 100%;
            border-collapse: collapse;
            font-family: "Inter", "Arial", sans-serif;
            font-size: 10px;
            margin-bottom: 12px;
        }
        .preview-table th, .preview-table td {
            border: 1px solid #CBD5E1;
            padding: 4px;
            text-align: center;
        }
        .preview-table th {
            text-transform: uppercase;
            font-weight: 700;
            font-size: 9px;
            color: #475569;
        }
        .preview-table td {
            color: #1E293B;
            height: 20px;
        }
        .preview-table tr:nth-child(even) {
            background: #F8FAFC;
        }
        .preview-table tr.absent-row td {
            background-color: #fef2f2 !important;
        }
        .preview-table tr.late-row td {
            background-color: #fff7ed !important;
        }
        </style>'''

content = content.replace('        </style>', missing_css)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
