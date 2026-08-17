# -*- coding: utf-8 -*-
import re

with open('app/services/dtr_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add _parse_12h_time right before compute_dtr
parse_12h = '''def _parse_12h_time(t_str: str) -> time:
    """Parses '08:00 AM' into datetime.time object."""
    if not t_str: return None
    try:
        from datetime import datetime
        return datetime.strptime(t_str, "%I:%M %p").time()
    except Exception:
        return None

def compute_dtr('''

content = content.replace('def compute_dtr(', parse_12h)

# Replace the categorizer and undertime logic
# from:             # Categorize logs strictly by time boundaries
# to:                     undertime_min = total_under

new_logic = """
            # Setup dynamic target boundaries
            w_start_target = _parse_12h_time(getattr(emp, "work_start", None)) or _parse_time(co.work_start)
            bo1_target = _parse_12h_time(getattr(emp, "break_out_1", None)) or time(12, 0)
            bi1_target = _parse_12h_time(getattr(emp, "break_in_1", None)) or time(13, 0)
            bo2_target = _parse_12h_time(getattr(emp, "break_out_2", None)) or time(16, 0)
            bi2_target = _parse_12h_time(getattr(emp, "break_in_2", None)) or time(16, 30)
            w_end_target = _parse_12h_time(getattr(emp, "work_end", None)) or _parse_time(co.work_end) or time(17, 0)

            def get_midpoint(t1, t2):
                if not t1 or not t2: return None
                dt1 = datetime.combine(current, t1)
                dt2 = datetime.combine(current, t2)
                return (dt1 + (dt2 - dt1) / 2).time()
                
            b1 = get_midpoint(w_start_target, bo1_target) or time(10, 0)
            b2 = get_midpoint(bo1_target, bi1_target) or time(12, 30)
            b3 = get_midpoint(bi1_target, bo2_target) or time(14, 30)
            b4 = get_midpoint(bo2_target, bi2_target) or time(16, 15)
            b5 = get_midpoint(bi2_target, w_end_target) or time(16, 45)

            # Categorize logs dynamically
            day_logs.sort(key=lambda l: l.log_datetime)
            time_in_log = None
            time_out_log = None
            bo1 = bi1 = bo2 = bi2 = None
            
            for log in day_logs:
                t = log.log_datetime.time()
                fmt_t = fmt(log.log_datetime)
                if t < b1:
                    if not time_in_log: time_in_log = log
                elif b1 <= t < b2:
                    if not bo1: bo1 = fmt_t
                elif b2 <= t < b3:
                    if not bi1: bi1 = fmt_t
                elif b3 <= t < b4:
                    if not bo2: bo2 = fmt_t
                elif b4 <= t < b5:
                    if not bi2: bi2 = fmt_t
                elif t >= b5:
                    time_out_log = log

            # Late computation
            is_late = False
            late_min = None
            if time_in_log:
                t_in = time_in_log.log_datetime.time()
                deadline = (
                    datetime.combine(current, w_start_target) + timedelta(minutes=grace)
                ).time()
                if t_in > deadline:
                    is_late = True
                    in_dt = datetime.combine(current, t_in)
                    deadline_dt = datetime.combine(current, deadline)
                    late_min = int((in_dt - deadline_dt).total_seconds() / 60)

            # Undertime computation (Employee specific)
            undertime_min = 0
            
            if time_out_log:
                t_out = time_out_log.log_datetime.time()
                if t_out < w_end_target:
                    out_dt = datetime.combine(current, t_out)
                    end_dt = datetime.combine(current, w_end_target)
                    total_under = int((end_dt - out_dt).total_seconds() / 60)
                    
                    # Deduct break times if they overlap
                    def deduct_break(b_start, b_end, t_under):
                        if not b_start or not b_end: return t_under
                        bs = datetime.combine(current, b_start)
                        be = datetime.combine(current, b_end)
                        overlap_start = max(out_dt, bs)
                        overlap_end = min(end_dt, be)
                        if overlap_start < overlap_end:
                            return t_under - int((overlap_end - overlap_start).total_seconds() / 60)
                        return t_under

                    total_under = deduct_break(bo1_target, bi1_target, total_under)
                    total_under = deduct_break(bo2_target, bi2_target, total_under)
                    
                    if total_under > 0:
                        undertime_min = total_under
"""

pattern = re.compile(r'            # Categorize logs strictly by time boundaries.*?                    if total_under > 0:\n                        undertime_min = total_under', re.DOTALL)
new_content = pattern.sub(new_logic.strip('\n'), content)

with open('app/services/dtr_service.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated dtr_service.py successfully.")
