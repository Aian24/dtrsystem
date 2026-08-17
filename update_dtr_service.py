# -*- coding: utf-8 -*-
import json
import re

with open('app/services/dtr_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = '''            # Determine if it's a rest day based on employee schedule
            weekday = current.weekday() # 0 = Mon, 6 = Sun
            is_rest_day = False
            schedule = emp.schedule_type if hasattr(emp, 'schedule_type') and emp.schedule_type else "Mon-Sat"
            if schedule == "Mon-Fri" and weekday in (5, 6): # Sat, Sun
                is_rest_day = True
            elif schedule == "Mon-Sat" and weekday == 6: # Sun
                is_rest_day = True


            if not day_logs:
                entries.append({
                    "date":        current,
                    "time_in":     None,
                    "break_out_1": None,
                    "break_in_1":  None,
                    "break_out_2": None,
                    "break_in_2":  None,
                    "time_out":    None,
                    "is_late":     False,
                    "late_minutes": None,
                    "undertime_minutes": 0,
                    "remarks":     "Rest Day" if is_rest_day else "Absent",
                })
                current += timedelta(days=1)
                continue

            # Setup dynamic target boundaries
            w_start_target = _parse_12h_time(getattr(emp, "work_start", None)) or _parse_time(co.work_start)
            bo1_target = _parse_12h_time(getattr(emp, "break_out_1", None)) or time(12, 0)
            bi1_target = _parse_12h_time(getattr(emp, "break_in_1", None)) or time(13, 0)
            bo2_target = _parse_12h_time(getattr(emp, "break_out_2", None)) or time(16, 0)
            bi2_target = _parse_12h_time(getattr(emp, "break_in_2", None)) or time(16, 30)
            w_end_target = _parse_12h_time(getattr(emp, "work_end", None)) or _parse_time(co.work_end) or time(17, 0)'''


new_logic = '''            # Custom schedule processing
            day_name = current.strftime("%A")
            custom_schedule = {}
            if getattr(emp, "custom_schedule", None):
                try:
                    import json
                    parsed_schedule = json.loads(emp.custom_schedule)
                    if day_name in parsed_schedule:
                        custom_schedule = parsed_schedule[day_name]
                except:
                    pass

            # Determine if it's a rest day based on employee schedule
            weekday = current.weekday() # 0 = Mon, 6 = Sun
            is_rest_day = False
            
            if custom_schedule and "is_rest_day" in custom_schedule:
                is_rest_day = custom_schedule["is_rest_day"]
            else:
                schedule = emp.schedule_type if hasattr(emp, 'schedule_type') and emp.schedule_type else "Mon-Sat"
                if schedule == "Mon-Fri" and weekday in (5, 6): # Sat, Sun
                    is_rest_day = True
                elif schedule == "Mon-Sat" and weekday == 6: # Sun
                    is_rest_day = True


            if not day_logs:
                entries.append({
                    "date":        current,
                    "time_in":     None,
                    "break_out_1": None,
                    "break_in_1":  None,
                    "break_out_2": None,
                    "break_in_2":  None,
                    "time_out":    None,
                    "is_late":     False,
                    "late_minutes": None,
                    "undertime_minutes": 0,
                    "remarks":     "Rest Day" if is_rest_day else "Absent",
                })
                current += timedelta(days=1)
                continue

            # Setup dynamic target boundaries
            def get_target(field_name, default_time_obj):
                # 1. Custom Daily Schedule
                if custom_schedule and custom_schedule.get(field_name):
                    parsed = _parse_12h_time(custom_schedule.get(field_name))
                    if parsed: return parsed
                # 2. Employee Default
                parsed = _parse_12h_time(getattr(emp, field_name, None))
                if parsed: return parsed
                # 3. Company Default / Hardcoded
                if field_name == "work_start":
                    return _parse_time(co.work_start) or default_time_obj
                if field_name == "work_end":
                    return _parse_time(co.work_end) or default_time_obj
                return default_time_obj

            w_start_target = get_target("work_start", time(8, 0))
            bo1_target = get_target("break_out_1", time(12, 0))
            bi1_target = get_target("break_in_1", time(13, 0))
            bo2_target = get_target("break_out_2", time(16, 0))
            bi2_target = get_target("break_in_2", time(16, 30))
            w_end_target = get_target("work_end", time(17, 0))'''

content = content.replace(old_logic, new_logic)

with open('app/services/dtr_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated dtr_service.py successfully.")
