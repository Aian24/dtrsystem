"""
Manage Logs Page — View, Download Backup, and Delete Upload Sessions
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from nicegui import ui
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.models import UploadSession, AttendanceLog
from app.pages.layout import app_layout
from app.components.notifications import toast_success, toast_error
from app.components.cards import upload_summary_card
from app.components.search_select import search_select
from app.theme.icons import IC


def generate_log_lines(logs: list[AttendanceLog]) -> str:
    """Format attendance logs into standard biometric log file entries."""
    lines = []
    for l in logs:
        if l.raw_line and not l.raw_line.startswith('{'):
            lines.append(l.raw_line.strip())
        else:
            emp_code = l.employee.emp_id if l.employee else "0"
            dt_str = l.log_datetime.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"{emp_code}\t{dt_str}\t{l.direction}\t1")
    return "\n".join(lines) + ("\n" if lines else "")


def download_session_backup(session_id: int, filename: str):
    """Generate and trigger browser download of the backup log file for a specific session."""
    db: Session = SessionLocal()
    try:
        logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == session_id).order_by(AttendanceLog.log_datetime.asc()).all()
        if not logs:
            toast_error("Download Failed", f"No log records found for '{filename}'.")
            return
        
        content = generate_log_lines(logs)
        clean_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        dl_filename = f"{clean_name}_backup.log"
        ui.download(content.encode("utf-8"), filename=dl_filename)
        toast_success("Backup Ready", f"Downloaded {len(logs):,} log records ({dl_filename}).")
    except Exception as e:
        toast_error("Download Error", str(e))
    finally:
        db.close()


def download_all_backup_logs(session_ids: list[int] | None = None):
    """Generate and trigger browser download of consolidated backup logs."""
    db: Session = SessionLocal()
    try:
        query = db.query(AttendanceLog)
        if session_ids:
            query = query.filter(AttendanceLog.session_id.in_(session_ids))
        logs = query.order_by(AttendanceLog.log_datetime.asc()).all()
        
        if not logs:
            toast_error("Download Failed", "No attendance log records available to export.")
            return
        
        content = generate_log_lines(logs)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "selected_logs_backup" if session_ids else "all_biometric_logs_backup"
        dl_filename = f"{prefix}_{timestamp}.log"
        ui.download(content.encode("utf-8"), filename=dl_filename)
        toast_success("Backup Ready", f"Downloaded {len(logs):,} log records ({dl_filename}).")
    except Exception as e:
        toast_error("Download Error", str(e))
    finally:
        db.close()


def delete_sessions(session_ids: list[int], on_success=None):
    db: Session = SessionLocal()
    try:
        # First, delete all associated attendance logs
        db.query(AttendanceLog).filter(AttendanceLog.session_id.in_(session_ids)).delete(synchronize_session=False)
        
        # Then, delete the upload sessions themselves
        db.query(UploadSession).filter(UploadSession.id.in_(session_ids)).delete(synchronize_session=False)
        db.commit()
        toast_success("Sessions Deleted", f"{len(session_ids)} upload session(s) and all associated logs were removed.")
        if on_success:
            on_success()
    except Exception as e:
        db.rollback()
        toast_error("Deletion Failed", str(e))
    finally:
        db.close()


def confirm_delete(session_ids: list[int], filename: str, on_success=None):
    with ui.dialog().classes('backdrop-blur-sm') as dialog:
        dialog.props('persistent')
        with ui.card().style("width: 450px; max-width: 90vw; padding: 24px; border-radius: 16px;"):
            ui.html(f'''
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:40px;height:40px;border-radius:50%;background:rgba(239, 68, 68, 0.1);display:flex;align-items:center;justify-content:center;color:#ef4444;">
                    <span class="material-icons-round" style="font-size:24px;">{IC.DELETE}</span>
                </div>
                <div style="font-size:18px;font-weight:600;color:var(--text-primary);">Delete Upload Session(s)</div>
            </div>
            <div style="font-size:14px;color:var(--text-secondary);margin-bottom:24px;line-height:1.5;">
                Are you sure you want to delete <strong>{filename}</strong>?<br><br>
                This action will permanently remove all imported biometric records from this file. This cannot be undone.
            </div>
            ''')
            
            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=dialog.close).classes("btn btn-secondary")
                ui.button("Delete Permanently", on_click=lambda: [dialog.close(), delete_sessions(session_ids, on_success)]).classes("btn btn-danger")
    dialog.open()


def manage_logs_page():
    with app_layout("Manage Logs", "/manage-logs", ["Manage Logs"]):
        
        with ui.element("div").classes("page-header").style("display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px; margin-bottom:24px;"):
            with ui.element("div"):
                ui.html('''
                <h1 class="page-title" style="margin:0;">Manage Uploaded Logs</h1>
                <p class="page-subtitle" style="margin:4px 0 0 0;">View, download backup logs, and delete imported biometric sessions</p>
                ''')
            
            with ui.element("div").style("display:flex; gap:10px; align-items:center;"):
                ui.button("Download All Backup Logs", icon="cloud_download", on_click=lambda: download_all_backup_logs()).classes("btn btn-secondary").style("font-size:13px; font-weight:600; padding:8px 16px; display:inline-flex; align-items:center; gap:8px;").tooltip("Download all attendance logs from all sessions into a single .log backup file")
        
        def show_summary_modal(s: UploadSession):
            with ui.dialog().classes('backdrop-blur-sm') as dlg:
                with ui.card().style("width: 800px; max-width: 90vw; padding: 0; border-radius: 16px; overflow: hidden; align-items: stretch; max-height: 85vh; display: flex; flex-direction: column;"):
                    with ui.element('div').style("padding: 24px; width: 100%; position: relative; overflow-y: auto;"):
                        
                        ui.html(f'<div style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:16px;">{s.filename} Details</div>')
                        
                        upload_summary_card(
                            filename=s.filename,
                            total=s.record_count or 0,
                            imported=s.imported_count or 0,
                            duplicates=s.duplicate_count or 0,
                            invalid=s.invalid_count or 0,
                        )
                        
                        # Logs Data Table header with Search & Direction filter
                        with ui.element("div").style("margin-top:24px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;"):
                            ui.html('<div style="font-size:14px;font-weight:600;color:var(--text-primary);white-space:nowrap;">Parsed Import Records</div>')
                            with ui.element("div").style("display:flex; gap:10px; align-items:center; flex-wrap:nowrap;"):
                                dir_filter = search_select(
                                    {"all": "All Punches", "I": "Check In Only", "O": "Check Out Only"},
                                    value="all",
                                    label="Direction"
                                ).props('dense outlined options-dense no-wrap').style("min-width: 175px; width: 175px; flex-shrink:0;")
                                search = ui.input(placeholder="Search records...").props('dense outlined clearable').style("min-width: 220px; width: 220px; flex-shrink:0;")
                        
                        db = SessionLocal()
                        raw_rows = []
                        try:
                            logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == s.id).all()
                            if logs:
                                for l in logs:
                                    emp_id = l.employee.emp_id if l.employee else "?"
                                    dir_badge = "Check In" if l.direction == "I" else "Check Out"
                                    raw_rows.append({
                                        'emp_id': str(emp_id),
                                        'date': l.log_datetime.strftime("%m/%d/%Y"),
                                        'time': l.log_datetime.strftime("%I:%M:%S %p"),
                                        'direction': dir_badge,
                                        'raw': str(l.raw_line or "")
                                    })
                        finally:
                            db.close()
                            
                        if raw_rows:
                            columns = [
                                {'name': 'emp_id', 'label': 'Emp ID', 'field': 'emp_id', 'align': 'left', 'sortable': True},
                                {'name': 'date', 'label': 'Date', 'field': 'date', 'align': 'left', 'sortable': True},
                                {'name': 'time', 'label': 'Time', 'field': 'time', 'align': 'left', 'sortable': True},
                                {'name': 'direction', 'label': 'Dir', 'field': 'direction', 'align': 'center', 'sortable': True},
                                {'name': 'raw', 'label': 'Raw Log Entry', 'field': 'raw', 'align': 'left'},
                            ]
                            table = ui.table(
                                columns=columns, 
                                rows=list(raw_rows), 
                                row_key='raw',
                                pagination={'rowsPerPage': 50}
                            ).classes('w-full').style(
                                "font-size: 13px; border: 1px solid var(--border); border-radius: 8px; box-shadow: none;"
                            ).props(':rows-per-page-options="[10, 25, 50, 100, 0]"')
                            
                            def do_filter(*_):
                                term = (search.value or "").lower().strip()
                                d_val = dir_filter.value or "all"
                                filtered = raw_rows
                                if d_val == "I":
                                    filtered = [r for r in filtered if r['direction'] == "Check In"]
                                elif d_val == "O":
                                    filtered = [r for r in filtered if r['direction'] == "Check Out"]
                                if term:
                                    filtered = [
                                        r for r in filtered 
                                        if term in r['emp_id'].lower() 
                                        or term in r['raw'].lower() 
                                        or term in r['date'].lower() 
                                        or term in r['time'].lower()
                                        or term in r['direction'].lower()
                                    ]
                                table.rows = filtered
                                table.update()
                                
                            search.on_value_change(do_filter)
                            dir_filter.on_value_change(do_filter)
                        else:
                            ui.html('''
                            <div style="background:var(--bg-subtle); padding:24px; text-align:center; border:1px dashed var(--border); border-radius:8px;">
                                <div style="font-size:13px; color:var(--text-muted);">No records were imported for this session.</div>
                            </div>
                            ''')
                            
                    with ui.element('div').style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); background: var(--bg-subtle); width: 100%; flex-shrink: 0;"):
                        ui.button("Download Backup (.log)", icon="file_download", on_click=lambda s=s: download_session_backup(s.id, s.filename)).classes("btn btn-secondary").style("font-size:13px; padding: 8px 18px;").tooltip("Download original log entries for this session")
                        ui.button("Close", on_click=dlg.close).classes("btn btn-primary").style("padding: 8px 32px;")
            dlg.open()

        table_state = {"search": "", "status": "all", "page": 1, "limit": 10}
        
        @ui.refreshable
        def history_container():
            db = SessionLocal()
            try:
                sessions = db.query(UploadSession).order_by(UploadSession.uploaded_at.desc()).all()
            finally:
                db.close()

            selected_sessions = set()
            checkboxes = []

            def handle_delete_success():
                history_container.refresh()

            def toggle_session(sid, checked):
                if checked: selected_sessions.add(sid)
                else: selected_sessions.discard(sid)
                update_bulk_actions()

            def toggle_all(e):
                if e.value:
                    selected_sessions.update(s.id for s in sessions)
                else:
                    selected_sessions.clear()
                for cb in checkboxes:
                    cb.set_value(e.value)
                update_bulk_actions()

            def trigger_bulk_delete():
                if not selected_sessions: return
                confirm_delete(list(selected_sessions), f"{len(selected_sessions)} selected sessions", handle_delete_success)

            def trigger_bulk_download():
                if not selected_sessions: return
                download_all_backup_logs(list(selected_sessions))

            with ui.element("div").classes("card"):
                with ui.element("div").classes("card-header").style("display: flex; justify-content: space-between; align-items: center; min-height: 56px;"):
                    ui.html(f'<span class="card-title">Upload History</span>')
                    
                    bulk_actions = ui.element("div").style("display: none;")
                    with bulk_actions:
                        with ui.row().classes("items-center gap-2"):
                            bulk_dl_btn = ui.button("Download Selected", icon="file_download", on_click=trigger_bulk_download).classes("btn btn-secondary btn-sm")
                            bulk_btn = ui.button("Delete Selected", icon=IC.DELETE, on_click=trigger_bulk_delete).classes("btn btn-danger btn-sm")

                def update_bulk_actions():
                    if len(selected_sessions) > 0:
                        bulk_actions.style("display: block;")
                        bulk_dl_btn.set_text(f"Download Selected ({len(selected_sessions)})")
                        bulk_btn.set_text(f"Delete Selected ({len(selected_sessions)})")
                    else:
                        bulk_actions.style("display: none;")

                with ui.element("div").style("padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); gap: 12px; flex-wrap: wrap; background: var(--bg-subtle);"):
                    with ui.element("div").style("display: flex; align-items: center; gap: 10px; flex-wrap: wrap; flex: 1;"):
                        # Show entries
                        with ui.element("div").style("display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--text-muted);"):
                            ui.html("<span>Show</span>")
                            def update_limit(e):
                                table_state["limit"] = e.value
                                table_state["page"] = 1
                                table_content.refresh()
                            ui.select(options=[10, 25, 50, 100], value=table_state["limit"], on_change=update_limit).props('dense outlined options-dense').style("width: 75px;")

                        # Status Filter
                        status_options = {
                            "all": "— All Statuses —",
                            "success": "Success",
                            "failed": "Failed",
                            "partial": "Partial"
                        }
                        def update_status_filter(e):
                            table_state["status"] = e.value
                            table_state["page"] = 1
                            table_content.refresh()
                        status_sel = search_select(
                            options=status_options,
                            value=table_state["status"],
                            on_change=update_status_filter,
                            label="Status",
                        ).props('dense outlined options-dense').style("min-width: 150px;")

                    with ui.element("div").style("display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"):
                        def update_search(e):
                            val = e.value or ""
                            if table_state["search"] != val:
                                table_state["search"] = val
                                table_state["page"] = 1
                                table_content.refresh()
                        search_inp = ui.input(placeholder="Search filename...", value=table_state["search"], on_change=update_search).props('dense outlined clearable').style("width: 220px;")

                        def reset_filters():
                            table_state["search"] = ""
                            table_state["status"] = "all"
                            table_state["page"] = 1
                            search_inp.value = ""
                            status_sel.value = "all"
                            table_content.refresh()

                        ui.button("Reset", icon="filter_alt_off", on_click=reset_filters).classes("btn btn-reset btn-sm").tooltip("Clear all filters")

                with ui.element("div").classes("card-body").style("padding: 0; overflow-x: auto;"):
                    @ui.refreshable
                    def table_content():
                        import math
                        term = table_state["search"].lower().strip()
                        s_filt = table_state["status"]

                        filtered_sessions = sessions
                        if s_filt != "all":
                            filtered_sessions = [s for s in filtered_sessions if s.status and s.status.lower() == s_filt.lower()]
                        if term:
                            filtered_sessions = [s for s in filtered_sessions if term in s.filename.lower()]
                    
                        total_items = len(filtered_sessions)
                        total_pages = math.ceil(total_items / table_state["limit"]) or 1
                        if table_state["page"] > total_pages:
                            table_state["page"] = total_pages
                        
                        start_idx = (table_state["page"] - 1) * table_state["limit"]
                        end_idx = start_idx + table_state["limit"]
                        paged_sessions = filtered_sessions[start_idx:end_idx]

                        if not filtered_sessions:
                            ui.html('''
                            <div class="empty-state">
                              <span class="material-icons-round">history</span>
                              <div class="empty-state-title">No uploads found</div>
                              <div class="empty-state-subtitle">You haven't imported any logs yet.</div>
                            </div>
                            ''')
                        else:
                            with ui.element("table").classes("data-table").style("min-width: 800px;"):
                                with ui.element("thead"):
                                    with ui.element("tr"):
                                        with ui.element("th").style("width: 48px; text-align: center;"):
                                            ui.checkbox(on_change=toggle_all)
                                    
                                        headers = [
                                            ("description", "File Name"),
                                            ("calendar_today", "Date Uploaded"),
                                            ("check_circle", "Imported"),
                                            ("file_copy", "Duplicates"),
                                            ("error", "Invalid"),
                                            ("info", "Status"),
                                            ("settings", "Actions")
                                        ]
                                        for icon, col in headers:
                                            with ui.element("th"):
                                                ui.html(f'<div style="display:flex;align-items:center;gap:6px;"><span class="material-icons-round" style="font-size:16px;">{icon}</span> {col}</div>')
                            
                                with ui.element("tbody"):
                                    for s in paged_sessions:
                                        with ui.element("tr"):
                                            with ui.element("td").style("text-align: center;"):
                                                cb = ui.checkbox(on_change=lambda e, sid=s.id: toggle_session(sid, e.value))
                                                checkboxes.append(cb)
                                            with ui.element("td"):
                                                ui.html(f"<strong>{s.filename}</strong>")
                                            with ui.element("td"):
                                                ui.html(f"{s.uploaded_at.strftime('%b %d, %Y %I:%M %p')}")
                                            with ui.element("td"):
                                                ui.html(f"{s.imported_count:,}")
                                            with ui.element("td"):
                                                ui.html(f"{s.duplicate_count:,}")
                                            with ui.element("td"):
                                                ui.html(f"{s.invalid_count:,}")
                                            with ui.element("td"):
                                                ui.html(f'<span class="badge badge-success" style="background: rgba(16, 185, 129, 0.1); color: #10B981;">{s.status.upper()}</span>')
                                            with ui.element("td"):
                                                with ui.element("div").style("display:flex; gap: 8px;"):
                                                    ui.button(
                                                        icon="visibility", 
                                                        on_click=lambda s=s: show_summary_modal(s)
                                                    ).classes("action-btn-view").props('flat round dense').tooltip("View Details")
                                                    ui.button(
                                                        icon="file_download",
                                                        on_click=lambda s=s: download_session_backup(s.id, s.filename)
                                                    ).classes("action-btn-download").props('flat round dense').tooltip("Download Backup Log (.log)")
                                                    ui.button(
                                                        icon=IC.DELETE, 
                                                        on_click=lambda s=s: confirm_delete([s.id], s.filename, handle_delete_success)
                                                    ).classes("action-btn-delete").props('flat round dense').tooltip("Delete Session")

                        with ui.element("div").style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); flex-wrap: wrap; gap: 16px;"):
                            showing_start = start_idx + 1 if total_items > 0 else 0
                            showing_end = min(end_idx, total_items)
                            ui.html(f'<span style="font-size: 13px; color: var(--text-muted);">Showing {showing_start} to {showing_end} of {total_items} entries</span>')
                        
                            def update_page(e):
                                table_state["page"] = e.value
                                table_content.refresh()
                            
                            ui.pagination(1, total_pages, value=table_state["page"], on_change=update_page).props('color="primary" outline active-color="primary" active-text-color="white"')

                table_content()

        history_container()
