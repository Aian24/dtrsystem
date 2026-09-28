"""
DTR Computation Service

Rules:
  - The first 'I' log of the day = Time In
  - The last 'O' log of the day  = Time Out
  - Intermediate logs = break out / break in pairs
  - Late = Time In > (work_start + grace_period)
  - Absent = no logs for that calendar day
"""
from __future__ import annotations
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

            # Setup target for late calculation
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

            # Deduplicate logs within 60 seconds
            day_logs.sort(key=lambda l: l.log_datetime)
            unique_day_logs = []
            for l in day_logs:
                if not unique_day_logs:
                    unique_day_logs.append(l)
                else:
                    diff = (l.log_datetime - unique_day_logs[-1].log_datetime).total_seconds()
                    if diff >= 60 or l.direction != unique_day_logs[-1].direction:
                        unique_day_logs.append(l)

            # Categorize punches sequentially without limiting first/second break by time of day
            time_in_log = None
            time_out_log = None
            bo1 = bi1 = bo2 = bi2 = None
            n_logs = len(unique_day_logs)

            if n_logs == 1:
                # If only 1 log and direction is explicitly OUT, treat as time out
                if unique_day_logs[0].direction == "O":
                    time_out_log = unique_day_logs[0]
                else:
                    time_in_log = unique_day_logs[0]
            elif n_logs == 2:
                if unique_day_logs[0].direction == "O" and unique_day_logs[1].direction == "O":
                    bo1 = fmt(unique_day_logs[0].log_datetime)
                    time_out_log = unique_day_logs[1]
                else:
                    time_in_log = unique_day_logs[0]
                    time_out_log = unique_day_logs[1]
            elif n_logs == 3:
                time_in_log = unique_day_logs[0]
                bo1 = fmt(unique_day_logs[1].log_datetime)
                time_out_log = unique_day_logs[2]
            elif n_logs == 4:
                time_in_log = unique_day_logs[0]
                bo1 = fmt(unique_day_logs[1].log_datetime)
                bi1 = fmt(unique_day_logs[2].log_datetime)
                time_out_log = unique_day_logs[3]
            elif n_logs == 5:
                time_in_log = unique_day_logs[0]
                bo1 = fmt(unique_day_logs[1].log_datetime)
                bi1 = fmt(unique_day_logs[2].log_datetime)
                bo2 = fmt(unique_day_logs[3].log_datetime)
                time_out_log = unique_day_logs[4]
            elif n_logs >= 6:
                time_in_log = unique_day_logs[0]
                bo1 = fmt(unique_day_logs[1].log_datetime)
                bi1 = fmt(unique_day_logs[2].log_datetime)
                bo2 = fmt(unique_day_logs[3].log_datetime)
                bi2 = fmt(unique_day_logs[4].log_datetime)
                time_out_log = unique_day_logs[-1]

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
            elif not time_in_log and time_out_log:
                if is_rest_day:
                    remarks = "Rest Day Duty / No Time In"
                else:
                    remarks = "No Time In"

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
                "undertime_minutes": 0,
                "remarks":      remarks,
            })

            current += timedelta(days=1)

        return entries

    finally:
        if close_db:
            db.close()
