"""
DTR Computation Service

Rules:
  - The first 'I' log of the day = Time In
  - The last 'O' log of the day  = Time Out
  - Intermediate logs = break out / break in pairs
  - Late = Time In > (work_start + grace_period)
  - Absent = no logs for that calendar day
"""
from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.models import AttendanceLog, Employee, Company


def _parse_time(t_str: str) -> time:
    h, m = map(int, t_str.split(":"))
    return time(h, m)


def _parse_12h_time(t_str: str) -> time:
    """Parses '08:00 AM' into datetime.time object."""
    if not t_str: return None
    try:
        from datetime import datetime
        return datetime.strptime(t_str, "%I:%M %p").time()
    except Exception:
        return None

def compute_dtr(
    employee_id: int,
    date_from: date,
    date_to: date,
    db: Optional[Session] = None,
) -> list[dict]:
    """
    Compute DTR entries for an employee over a date range.

    Returns a list of dicts (one per calendar day):
    {
      "date":         date,
      "time_in":      str | None,   # "08:02"
      "break_out_1":  str | None,
      "break_in_1":   str | None,
      "break_out_2":  str | None,
      "break_in_2":   str | None,
      "time_out":     str | None,
      "is_late":      bool,
      "late_minutes": int | None,
      "remarks":      str,          # "", "Late", "Absent", "No Time Out"
    }
    """
    close_db = db is None
    if db is None:
        db = SessionLocal()

    try:
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            return []

        co: Company = emp.company
        grace   = co.grace_period if co else 10
        w_start = _parse_time(co.work_start) if co else time(8, 0)

        # Handle duplicate profiles: matching logs from auto-created placeholders (e.g. "0018844" vs "18844")
        stripped_id = emp.emp_id.lstrip("0") or "0"
        all_emps = db.query(Employee.id, Employee.emp_id).all()
        matching_emp_ids = [
            e.id for e in all_emps
            if (e.emp_id and e.emp_id.lstrip("0") == stripped_id) or e.id == employee_id
        ]

        # Fetch all logs in range for ANY of the matching employee profiles
        logs = db.query(AttendanceLog).filter(
            AttendanceLog.employee_id.in_(matching_emp_ids),
            AttendanceLog.log_datetime >= datetime.combine(date_from, time.min),
            AttendanceLog.log_datetime <= datetime.combine(date_to,   time.max),
        ).order_by(AttendanceLog.log_datetime).all()

        # Group logs by date
        logs_by_date: dict[date, list[AttendanceLog]] = {}
        for log in logs:
            d = log.log_datetime.date()
            logs_by_date.setdefault(d, []).append(log)

        entries = []
        current = date_from
        while current <= date_to:
            day_logs = logs_by_date.get(current, [])

            # Separate In and Out logs
            in_logs  = [l for l in day_logs if l.direction == "I"]
            out_logs = [l for l in day_logs if l.direction == "O"]

            # Sort
            in_logs.sort(key=lambda l: l.log_datetime)
            out_logs.sort(key=lambda l: l.log_datetime)

            def fmt(dt: datetime) -> str:
                return dt.strftime("%I:%M %p")

            # Custom schedule processing
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
            w_end_target = get_target("work_end", time(17, 0))

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
                if t_in > deadline and not is_rest_day:
                    is_late = True
                    in_dt = datetime.combine(current, t_in)
                    start_dt = datetime.combine(current, w_start_target)
                    late_min = int((in_dt - start_dt).total_seconds() / 60)

            # Undertime computation (Employee specific)
            undertime_min = 0
            
            # Use the very last punch of the day to calculate undertime, 
            # even if it wasn't classified as a time out log (e.g. they left at 3:35 PM and it landed in 2nd BO)
            last_punch_for_undertime = time_out_log or (day_logs[-1] if len(day_logs) > 0 else None)
            
            if last_punch_for_undertime and not is_rest_day:
                t_out = last_punch_for_undertime.log_datetime.time()
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

            remarks = ""
            if is_rest_day:
                remarks = "Rest Day Duty"
            elif is_late:
                remarks = "Late"
            
            if not time_out_log and time_in_log:
                if is_rest_day:
                    remarks = "Rest Day Duty / No Time Out"
                else:
                    remarks = "No Time Out" if not is_late else "Late / No Time Out"

            entries.append({
                "date":         current,
                "time_in":      fmt(time_in_log.log_datetime) if time_in_log else None,
                "break_out_1":  bo1,
                "break_in_1":   bi1,
                "break_out_2":  bo2,
                "break_in_2":   bi2,
                "time_out":     fmt(time_out_log.log_datetime) if time_out_log else None,
                "is_late":      is_late,
                "late_minutes": late_min,
                "undertime_minutes": undertime_min,
                "remarks":      remarks,
            })


            current += timedelta(days=1)

        return entries

    finally:
        if close_db:
            db.close()
