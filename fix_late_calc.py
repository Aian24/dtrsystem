# -*- coding: utf-8 -*-
import re

with open('app/services/dtr_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

late_calc_old = '''            if time_in_log:
                t_in = time_in_log.log_datetime.time()
                deadline = (
                    datetime.combine(current, w_start_target) + timedelta(minutes=grace)
                ).time()
                if t_in > deadline:
                    is_late = True
                    in_dt = datetime.combine(current, t_in)
                    deadline_dt = datetime.combine(current, deadline)
                    late_min = int((in_dt - deadline_dt).total_seconds() / 60)'''

late_calc_new = '''            if time_in_log:
                t_in = time_in_log.log_datetime.time()
                deadline = (
                    datetime.combine(current, w_start_target) + timedelta(minutes=grace)
                ).time()
                if t_in > deadline:
                    is_late = True
                    in_dt = datetime.combine(current, t_in)
                    start_dt = datetime.combine(current, w_start_target)
                    late_min = int((in_dt - start_dt).total_seconds() / 60)'''

content = content.replace(late_calc_old, late_calc_new)

with open('app/services/dtr_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated dtr_service.py successfully.")
