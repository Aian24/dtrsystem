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

            # Determine if it's a rest day based on employee schedule
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
                    "remarks":     "Rest Day" if is_rest_day else "Absent",
                })
                current += timedelta(days=1)
                continue

            # Time In = first I log
            time_in_log  = in_logs[0]  if in_logs  else None
            time_out_log = out_logs[-1] if out_logs else None

            # Break pairs: remaining logs between first-In and last-Out
            # Pair: O → I = break_out / break_in
            middle_logs = [l for l in day_logs
                           if l != time_in_log and l != time_out_log]
            middle_logs.sort(key=lambda l: l.log_datetime)

            bo1 = bi1 = bo2 = bi2 = None
            out_idx = 0
            in_idx  = 0
            breaks  = []
            i = 0
            while i < len(middle_logs):
                log = middle_logs[i]
                if log.direction == "O":
                    # Start of break
                    bo = fmt(log.log_datetime)
                    bi = None
                    # Find next I
                    for j in range(i+1, len(middle_logs)):
                        if middle_logs[j].direction == "I":
                            bi = fmt(middle_logs[j].log_datetime)
                            i = j
                            break
                    breaks.append((bo, bi))
                i += 1

            if breaks:
                bo1, bi1 = breaks[0]
            if len(breaks) > 1:
                bo2, bi2 = breaks[1]

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
                "remarks":      remarks,
            })

            current += timedelta(days=1)

        return entries

    finally:
        if close_db:
            db.close()
