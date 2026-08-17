# -*- coding: utf-8 -*-
import re

with open('app/services/dtr_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = """
            # Categorize logs strictly by time boundaries
            day_logs.sort(key=lambda l: l.log_datetime)
            time_in_log = None
            time_out_log = None
            bo1 = bi1 = bo2 = bi2 = None
            
            for log in day_logs:
                t = log.log_datetime.time()
                fmt_t = fmt(log.log_datetime)
                if t < time(11, 0):
                    if not time_in_log: time_in_log = log
                elif time(11, 0) <= t < time(13, 0):
                    if not bo1: bo1 = fmt_t
                    elif not bi1: bi1 = fmt_t
                elif time(13, 0) <= t < time(16, 30):
                    if not bo2: bo2 = fmt_t
                    elif not bi2: bi2 = fmt_t
                elif t >= time(16, 30):
                    time_out_log = log

            # Late computation
            is_late = False
            late_min = None
            if time_in_log:
                t_in = time_in_log.log_datetime.time()
                deadline = (
                    datetime.combine(current, w_start) + timedelta(minutes=grace)
                ).time()
                if t_in > deadline:
                    is_late = True
                    in_dt = datetime.combine(current, t_in)
                    deadline_dt = datetime.combine(current, deadline)
                    late_min = int((in_dt - deadline_dt).total_seconds() / 60)

            # Undertime computation (Employee specific)
            undertime_min = 0
            
            e_w_end = getattr(emp, "work_end", None)
            w_end = _parse_time(e_w_end) if e_w_end else (_parse_time(co.work_end) if co and co.work_end else time(17, 0))
            
            if time_out_log:
                t_out = time_out_log.log_datetime.time()
                if t_out < w_end:
                    out_dt = datetime.combine(current, t_out)
                    end_dt = datetime.combine(current, w_end)
                    total_under = int((end_dt - out_dt).total_seconds() / 60)
                    
                    # Deduct break time
                    e_b_start = getattr(emp, "break_time_start", None)
                    e_b_end = getattr(emp, "break_time_end", None)
                    
                    b_start_time = _parse_time(e_b_start) if e_b_start else time(16, 0)
                    b_end_time = _parse_time(e_b_end) if e_b_end else time(16, 30)
                    
                    break_start = datetime.combine(current, b_start_time)
                    break_end = datetime.combine(current, b_end_time)
                    
                    overlap_start = max(out_dt, break_start)
                    overlap_end = min(end_dt, break_end)
                    if overlap_start < overlap_end:
                        overlap_mins = int((overlap_end - overlap_start).total_seconds() / 60)
                        total_under -= overlap_mins
                    
                    if total_under > 0:
                        undertime_min = total_under
"""

pattern = re.compile(r'            # Check for Time In and Time Out.*?                    if total_under > 0:\n                        undertime_min = total_under', re.DOTALL)
new_content = pattern.sub(new_logic.strip('\n'), content)

with open('app/services/dtr_service.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated dtr_service.py successfully.")
