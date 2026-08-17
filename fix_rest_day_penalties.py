# -*- coding: utf-8 -*-
import re

with open('app/services/dtr_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Skip late computation on rest days
late_old = '''                if t_in > deadline:
                    is_late = True
                    in_dt = datetime.combine(current, t_in)
                    start_dt = datetime.combine(current, w_start_target)
                    late_min = int((in_dt - start_dt).total_seconds() / 60)'''

late_new = '''                if t_in > deadline and not is_rest_day:
                    is_late = True
                    in_dt = datetime.combine(current, t_in)
                    start_dt = datetime.combine(current, w_start_target)
                    late_min = int((in_dt - start_dt).total_seconds() / 60)'''
content = content.replace(late_old, late_new)

# 2. Skip undertime computation on rest days
under_old = '''            if last_punch_for_undertime:
                t_out = last_punch_for_undertime.log_datetime.time()'''

under_new = '''            if last_punch_for_undertime and not is_rest_day:
                t_out = last_punch_for_undertime.log_datetime.time()'''
content = content.replace(under_old, under_new)

with open('app/services/dtr_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated dtr_service.py successfully.")
