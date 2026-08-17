# -*- coding: utf-8 -*-
import re

with open('app/services/dtr_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

categorize_old = '''            for log in day_logs:
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
                    time_out_log = log'''

categorize_new = '''            if len(day_logs) == 1:
                t = day_logs[0].log_datetime.time()
                # If only 1 punch and it's past noon, assume it's a Time Out.
                if t >= time(12, 0):
                    time_out_log = day_logs[0]
                else:
                    time_in_log = day_logs[0]
            else:
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
                        
                # If they left early (no punch after b5), treat the last punch of the day as Time Out
                if not time_out_log and len(day_logs) > 1:
                    last_log = day_logs[-1]
                    fmt_t_last = fmt(last_log.log_datetime)
                    
                    if bo1 == fmt_t_last: bo1 = None
                    elif bi1 == fmt_t_last: bi1 = None
                    elif bo2 == fmt_t_last: bo2 = None
                    elif bi2 == fmt_t_last: bi2 = None
                    
                    time_out_log = last_log'''

content = content.replace(categorize_old, categorize_new)

with open('app/services/dtr_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated dtr_service.py successfully.")
