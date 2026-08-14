"""
Import Service — Parse .log files and insert attendance records into DB
Log format: EmployeeID,Date,Time,Direction
Example:    0050474,07/16/2026,07:29:00,I
"""
import csv
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.core.models import Employee, AttendanceLog, UploadSession, Company


def import_log_file(
    filepath: str,
    progress_cb: Optional[Callable[[int, str], None]] = None,
    uploaded_by: Optional[int] = None,
) -> dict:
    """
    Parse and import a .log file into the database.

    Returns:
        {
          "total":      int,   # total lines read
          "imported":   int,   # successfully inserted
          "duplicates": int,   # already in DB
          "invalid":    int,   # lines that couldn't be parsed / employee not found
        }
    """
    path = Path(filepath)
    filename = path.name

    db = SessionLocal()
    try:
        # Create upload session record
        session = UploadSession(
            filename=filename,
            status="processing",
            uploaded_by=uploaded_by,
        )
        db.add(session)
        db.flush()
        session_id = session.id

        # Read all lines
        lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
        total = len(lines)
        imported = 0
        duplicates = 0
        invalid = 0

        # Ensure a default company exists for auto-created employees
        default_company = db.query(Company).first()
        if not default_company:
            default_company = Company(name="Main Company")
            db.add(default_company)
            db.flush()

        # Cache employee lookup by emp_id string → DB id
        emp_cache: dict[str, Optional[int]] = {}

        def lookup_emp(emp_id_str: str) -> Optional[int]:
            if emp_id_str in emp_cache:
                return emp_cache[emp_id_str]
            emp = db.query(Employee).filter(Employee.emp_id == emp_id_str).first()
            result = emp.id if emp else None
            emp_cache[emp_id_str] = result
            return result

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                invalid += 1
                continue

            # Update progress every 200 lines
            if progress_cb and i % 200 == 0:
                pct = int((i / max(total, 1)) * 90) + 5
                progress_cb(pct, f"Processing line {i:,} / {total:,}…")

            # Parse: EmpID,Date,Time,Direction
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                invalid += 1
                continue

            emp_id_str = parts[0].lstrip("0") or "0"
            # Keep leading zeros for lookup — try both raw and stripped
            raw_emp_id = parts[0].strip()

            date_str  = parts[1].strip()  # MM/DD/YYYY
            time_str  = parts[2].strip()  # HH:MM:SS
            direction = parts[3].strip().upper() if len(parts) >= 4 else "I"

            # Parse datetime
            try:
                log_dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M:%S")
            except ValueError:
                try:
                    log_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    invalid += 1
                    continue

            # Look up employee by raw emp_id first, then stripped
            emp_db_id = lookup_emp(raw_emp_id)
            
            emp_id_str = raw_emp_id.lstrip("0") or "0"
            if emp_db_id is None:
                emp_db_id = lookup_emp(emp_id_str)
                
            # If employee STILL doesn't exist, auto-create them as an INACTIVE placeholder
            if emp_db_id is None:
                new_emp = Employee(
                    emp_id=raw_emp_id,
                    first_name="Unregistered",
                    last_name="Profile",
                    company_id=default_company.id,
                    is_active=False,
                )
                db.add(new_emp)
                db.flush()
                emp_db_id = new_emp.id
                emp_cache[raw_emp_id] = emp_db_id
                emp_cache[emp_id_str] = emp_db_id

            # Validate direction
            if direction not in ("I", "O"):
                direction = "I"  # default to In if unknown

            # Insert log
            log = AttendanceLog(
                employee_id=emp_db_id,
                log_datetime=log_dt,
                direction=direction,
                raw_line=line,
                session_id=session_id,
            )
            db.add(log)
            try:
                db.flush()
                imported += 1
            except IntegrityError:
                db.rollback()
                duplicates += 1
                # re-attach session
                db.add(session)
                continue

        # Update session record
        session.record_count    = total
        session.imported_count  = imported
        session.duplicate_count = duplicates
        session.invalid_count   = invalid
        session.status          = "completed"
        db.commit()

        if progress_cb:
            progress_cb(100, "Import complete!")

        return {
            "total":      total,
            "imported":   imported,
            "duplicates": duplicates,
            "invalid":    invalid,
        }

    except Exception as e:
        db.rollback()
        try:
            session.status = "failed"
            db.commit()
        except Exception:
            pass
        raise e
    finally:
        db.close()
