"""
Import Service — Parse .log, .dat, .txt, .csv files and direct biometric device sync.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any

from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.core.models import Employee, AttendanceLog, UploadSession, Company
from app.services.biometric_service import (
    parse_universal_log,
    BiometricDeviceClient,
)


def import_biometric_records(
    records: List[Dict[str, Any]],
    session_title: str,
    progress_cb: Optional[Callable[[int, str], None]] = None,
    uploaded_by: Optional[int] = None,
) -> dict:
    """
    Core function: insert a list of parsed record dicts into the database,
    handling employee auto-creation, duplicate suppression, and upload session logging.
    """
    total = len(records)
    imported = 0
    duplicates = 0
    invalid = 0

    db = SessionLocal()
    try:
        # Create upload session record
        session = UploadSession(
            filename=session_title,
            status="processing",
            uploaded_by=uploaded_by,
        )
        db.add(session)
        db.commit()
        session_id = session.id

        # Ensure a default company exists for auto-created employees
        default_company = db.query(Company).first()
        if not default_company:
            default_company = Company(name="Main Company")
            db.add(default_company)
            db.commit()

        # Cache existing employees (both raw and stripped emp_ids)
        all_emps = db.query(Employee).all()
        emp_cache: dict[str, int] = {}
        for emp in all_emps:
            if emp.emp_id:
                emp_cache[emp.emp_id] = emp.id
                emp_cache[emp.emp_id.lstrip("0") or "0"] = emp.id

        # Cache existing log fingerprints to avoid duplicates
        existing_log_set = set(
            db.query(AttendanceLog.employee_id, AttendanceLog.log_datetime, AttendanceLog.direction).all()
        )

        logs_to_insert = []
        new_emps_to_create = {}

        for i, rec in enumerate(records):
            if progress_cb and i % 2000 == 0 and total > 0:
                pct = min(85, int((i / max(total, 1)) * 75) + 10)
                progress_cb(pct, f"Preparing record {i:,} / {total:,}…")

            raw_emp_id = str(rec.get("emp_id", "")).strip()
            log_dt = rec.get("datetime")
            direction = str(rec.get("direction", "I")).upper()
            raw_line = rec.get("raw", f"{raw_emp_id},{log_dt},{direction}")

            if not raw_emp_id or not log_dt:
                invalid += 1
                continue

            if direction not in ("I", "O"):
                direction = "I"

            # Look up employee DB id
            emp_db_id = emp_cache.get(raw_emp_id)
            if emp_db_id is None:
                emp_id_stripped = raw_emp_id.lstrip("0") or "0"
                emp_db_id = emp_cache.get(emp_id_stripped)

            # Auto-create unregistered employee if needed
            if emp_db_id is None:
                if raw_emp_id not in new_emps_to_create:
                    new_emp = Employee(
                        emp_id=raw_emp_id,
                        first_name="Biometric",
                        last_name=f"User {raw_emp_id}",
                        company_id=default_company.id,
                        is_active=True,
                    )
                    db.add(new_emp)
                    db.flush()
                    emp_db_id = new_emp.id
                    emp_cache[raw_emp_id] = emp_db_id
                    emp_cache[raw_emp_id.lstrip("0") or "0"] = emp_db_id
                    new_emps_to_create[raw_emp_id] = emp_db_id
                else:
                    emp_db_id = new_emps_to_create[raw_emp_id]

            # Check duplicate in O(1)
            log_key = (emp_db_id, log_dt, direction)
            if log_key in existing_log_set:
                duplicates += 1
                continue

            existing_log_set.add(log_key)
            logs_to_insert.append(AttendanceLog(
                employee_id=emp_db_id,
                log_datetime=log_dt,
                direction=direction,
                raw_line=raw_line,
                session_id=session_id,
            ))
            imported += 1

            # Batch insert in chunks of 2,000 for maximum SQLite speed
            if len(logs_to_insert) >= 2000:
                db.bulk_save_objects(logs_to_insert)
                db.commit()
                logs_to_insert.clear()

        if logs_to_insert:
            db.bulk_save_objects(logs_to_insert)
            db.commit()
            logs_to_insert.clear()

        # Update session record
        session.record_count    = total
        session.imported_count  = imported
        session.duplicate_count = duplicates
        session.invalid_count   = invalid
        session.status          = "completed"
        db.commit()

        if progress_cb:
            progress_cb(100, f"Sync complete! {imported:,} records imported ({duplicates:,} duplicates skipped).")

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


def import_log_file(
    filepath: str,
    progress_cb: Optional[Callable[[int, str], None]] = None,
    uploaded_by: Optional[int] = None,
) -> dict:
    """
    Parse and import any log file (.log, .dat, .txt, .csv, .bin, .rec) into the DB.
    Automatically decrypts binary DAT structs, XOR scrambling, and Chinese character sets.
    """
    path = Path(filepath)
    filename = path.name

    if progress_cb:
        progress_cb(5, f"Reading and analyzing {filename}…")

    # Read raw bytes
    raw_bytes = path.read_bytes()

    # Parse using universal decryption & decoding engine
    records = parse_universal_log(raw_bytes)

    if not records:
        # Fallback to standard text lines if universal parser found nothing
        try:
            lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    try:
                        dt = datetime.strptime(f"{parts[1]} {parts[2]}", "%m/%d/%Y %H:%M:%S")
                    except ValueError:
                        try:
                            dt = datetime.strptime(f"{parts[1]} {parts[2]}", "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            continue
                    direction = parts[3].upper() if len(parts) >= 4 else "I"
                    records.append({
                        "emp_id": parts[0],
                        "datetime": dt,
                        "direction": direction,
                        "raw": line,
                    })
        except Exception:
            pass

    return import_biometric_records(
        records=records,
        session_title=filename,
        progress_cb=progress_cb,
        uploaded_by=uploaded_by,
    )


def sync_biometric_device(
    ip: str,
    port: int = 4370,
    comm_key: int = 0,
    protocol: str = "UDP",
    start_date: Optional[Union[datetime, str, Any]] = None,
    end_date: Optional[Union[datetime, str, Any]] = None,
    progress_cb: Optional[Callable[[int, str], None]] = None,
    uploaded_by: Optional[int] = None,
) -> dict:
    """
    Directly connects to IntelliSmart / ZKTeco device over LAN IP,
    pulls attendance logs, decrypts/decodes them, and imports into the database.
    Optionally filters records within [start_date, end_date].
    """
    if progress_cb:
        progress_cb(5, f"Connecting to Biometric Device at {ip}:{port}…")

    client = BiometricDeviceClient(ip=ip, port=port, comm_key=comm_key, protocol=protocol)
    
    # Download logs from device with optional date range filter
    records = client.read_attendance_logs(
        progress_cb=progress_cb,
        start_date=start_date,
        end_date=end_date,
    )

    if start_date and end_date:
        session_title = f"Biometric Sync ({ip}) [{start_date} to {end_date}]"
    elif start_date:
        session_title = f"Biometric Sync ({ip}) [from {start_date}]"
    elif end_date:
        session_title = f"Biometric Sync ({ip}) [until {end_date}]"
    else:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        session_title = f"Biometric Sync ({ip}) - {now_str}"

    return import_biometric_records(
        records=records,
        session_title=session_title,
        progress_cb=progress_cb,
        uploaded_by=uploaded_by,
    )
