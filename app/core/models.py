"""
ORM Models — DTR Management System
"""
from __future__ import annotations

import bcrypt
from datetime import datetime, date, time
from typing import Optional, List

from sqlalchemy import (
    Integer, String, Boolean, DateTime, Date, Time,
    Float, Text, ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ─── Company ─────────────────────────────────────────────────────────────────

class Company(Base):
    __tablename__ = "companies"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True)
    name:          Mapped[str]           = mapped_column(String(200), nullable=False, unique=True)
    logo_path:     Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    address:       Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Grace period in minutes (e.g. 10)
    grace_period:  Mapped[int]           = mapped_column(Integer, default=10)
    # Default work schedule
    work_start:    Mapped[str]           = mapped_column(String(5), default="08:00")
    work_end:      Mapped[str]           = mapped_column(String(5), default="17:00")
    area_manager:  Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    store_supervisor: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at:    Mapped[datetime]      = mapped_column(DateTime, default=func.now())
    is_active:     Mapped[bool]          = mapped_column(Boolean, default=True)

    employees:     Mapped[List["Employee"]]    = relationship("Employee", back_populates="company", cascade="all, delete-orphan")
    cutoff_periods: Mapped[List["CutoffPeriod"]] = relationship("CutoffPeriod", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name!r}>"


# ─── Employee ─────────────────────────────────────────────────────────────────

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (UniqueConstraint("emp_id", "company_id", name="uq_emp_company"),)

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True)
    emp_id:       Mapped[str]           = mapped_column(String(50), nullable=False, index=True)
    first_name:   Mapped[str]           = mapped_column(String(100), nullable=False)
    last_name:    Mapped[str]           = mapped_column(String(100), nullable=False)
    middle_name:  Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department:   Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    position:     Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_id:   Mapped[int]           = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    schedule_type: Mapped[str]          = mapped_column(String(50), default="Mon-Sat")
    is_active:    Mapped[bool]          = mapped_column(Boolean, default=True)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, default=func.now())

    company:       Mapped["Company"]           = relationship("Company", back_populates="employees")
    logs:          Mapped[List["AttendanceLog"]] = relationship("AttendanceLog", back_populates="employee", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name[0] + ".")
        return ", ".join(parts[:2]) + (f" {self.middle_name[0]}." if self.middle_name else "")

    def __repr__(self) -> str:
        return f"<Employee {self.emp_id} {self.full_name}>"


# ─── AttendanceLog ────────────────────────────────────────────────────────────

class AttendanceLog(Base):
    """Raw biometric log entry parsed from .log file."""
    __tablename__ = "attendance_logs"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True)
    employee_id:  Mapped[int]           = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    log_datetime: Mapped[datetime]      = mapped_column(DateTime, nullable=False, index=True)
    direction:    Mapped[str]           = mapped_column(String(1), nullable=False)   # 'I' or 'O'
    device_id:    Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    raw_line:     Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_id:   Mapped[Optional[int]] = mapped_column(ForeignKey("upload_sessions.id"), nullable=True)

    employee:     Mapped["Employee"]        = relationship("Employee", back_populates="logs")
    session:      Mapped[Optional["UploadSession"]] = relationship("UploadSession", back_populates="logs")

    def __repr__(self) -> str:
        return f"<Log emp={self.employee_id} {self.log_datetime} {self.direction}>"


# ─── UploadSession ────────────────────────────────────────────────────────────

class UploadSession(Base):
    __tablename__ = "upload_sessions"

    id:              Mapped[int]           = mapped_column(Integer, primary_key=True)
    filename:        Mapped[str]           = mapped_column(String(500), nullable=False)
    uploaded_at:     Mapped[datetime]      = mapped_column(DateTime, default=func.now())
    record_count:    Mapped[int]           = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int]           = mapped_column(Integer, default=0)
    invalid_count:   Mapped[int]           = mapped_column(Integer, default=0)
    imported_count:  Mapped[int]           = mapped_column(Integer, default=0)
    status:          Mapped[str]           = mapped_column(String(20), default="completed")  # processing, completed, failed
    uploaded_by:     Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    logs:            Mapped[List["AttendanceLog"]] = relationship("AttendanceLog", back_populates="session")

    def __repr__(self) -> str:
        return f"<UploadSession id={self.id} file={self.filename!r}>"


# ─── CutoffPeriod ─────────────────────────────────────────────────────────────

class CutoffPeriod(Base):
    """Custom cutoff date ranges per company."""
    __tablename__ = "cutoff_periods"

    id:          Mapped[int]  = mapped_column(Integer, primary_key=True)
    company_id:  Mapped[int]  = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    label:       Mapped[str]  = mapped_column(String(100), nullable=False)  # e.g. "Period 1 (1st - 15th)"
    start_day:   Mapped[int]  = mapped_column(Integer, nullable=False)      # e.g. 1
    end_day:     Mapped[int]  = mapped_column(Integer, nullable=False)      # e.g. 15 (use 31 for EoM)
    created_at:  Mapped[datetime] = mapped_column(DateTime, default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="cutoff_periods")

    def __repr__(self) -> str:
        return f"<CutoffPeriod {self.label} (Day {self.start_day} to {self.end_day})>"


# ─── User (Auth) ──────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True)
    username:     Mapped[str]           = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str]          = mapped_column(String(200), nullable=False)
    full_name:    Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    role:         Mapped[str]           = mapped_column(String(20), default="admin")  # admin, hr, viewer
    avatar_base64:Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active:    Mapped[bool]          = mapped_column(Boolean, default=True)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, default=func.now())
    last_login:   Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


# ─── AppSetting ───────────────────────────────────────────────────────────────

class AppSetting(Base):
    """Key-value store for app-wide settings."""
    __tablename__ = "app_settings"

    id:    Mapped[int] = mapped_column(Integer, primary_key=True)
    key:   Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<AppSetting {self.key}={self.value!r}>"
