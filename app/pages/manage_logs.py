"""
Manage Logs Page — View and Delete Upload Sessions
"""
from nicegui import ui
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.models import UploadSession, AttendanceLog
from app.pages.layout import app_layout
from app.components.notifications import toast_success, toast_error
from app.components.cards import upload_summary_card
from app.theme.icons import IC


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
                ui.button("Delete Permanently", on_click=lambda: [dialog.close(), delete_sessions(session_ids, on_success)]).classes("btn").style("background-color: #ef4444 !important; color: white !important;")
    dialog.open()


def manage_logs_page():
    with app_layout("Manage Logs", "/manage-logs", ["Manage Logs"]):
        
        ui.html('''
        <div class="page-header">
          <h1 class="page-title">Manage Uploaded Logs</h1>
          <p class="page-subtitle">View and delete imported biometric log files</p>
        </div>
        ''')
        
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
                        
                        # Logs Data Table header with Search
                        with ui.element("div").style("margin-top:24px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;"):
                            ui.html('<div style="font-size:14px;font-weight:600;color:var(--text-primary);">Parsed Import Records</div>')
                            search = ui.input(placeholder="Search records...").props('dense outlined debounce="300"').style("width: 250px;")
                        
                        db = SessionLocal()
                        rows = []
                        try:
                            logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == s.id).all()
                            if logs:
                                for l in logs:
                                    emp_id = l.employee.emp_id if l.employee else "?"
                                    dir_badge = "Check In" if l.direction == "I" else "Check Out"
                                    rows.append({
                                        'emp_id': emp_id,
                                        'date': l.log_datetime.strftime("%m/%d/%Y"),
                                        'time': l.log_datetime.strftime("%I:%M:%S %p"),
                                        'direction': dir_badge,
                                        'raw': l.raw_line
                                    })
                        finally:
                            db.close()
                            
                        if rows:
                            columns = [
                                {'name': 'emp_id', 'label': 'Emp ID', 'field': 'emp_id', 'align': 'left'},
                                {'name': 'date', 'label': 'Date', 'field': 'date', 'align': 'left'},
                                {'name': 'time', 'label': 'Time', 'field': 'time', 'align': 'left'},
                                {'name': 'direction', 'label': 'Dir', 'field': 'direction', 'align': 'center'},
                                {'name': 'raw', 'label': 'Raw Log Entry', 'field': 'raw', 'align': 'left'},
                            ]
                            table = ui.table(
                                columns=columns, 
                                rows=rows, 
                                row_key='raw',
                                pagination={'rowsPerPage': 50}
                            ).classes('w-full').style(
                                "font-size: 13px; border: 1px solid var(--border); border-radius: 8px; box-shadow: none;"
                            ).props(':rows-per-page-options="[10, 25, 50, 100, 0]"')
                            
                            def filter_rows(e):
                                term = (e.value or "").lower()
                                table.rows = [r for r in rows if term in r['emp_id'].lower() or term in r['raw'].lower() or term in r['date'].lower()]
                                table.update()
                                
                            search.on_value_change(filter_rows)
                        else:
                            ui.html('''
                            <div style="background:var(--bg-subtle); padding:24px; text-align:center; border:1px dashed var(--border); border-radius:8px;">
                                <div style="font-size:13px; color:var(--text-muted);">No records were imported for this session.</div>
                            </div>
                            ''')
                            
                    with ui.element('div').style("padding: 16px 24px; display: flex; justify-content: flex-end; border-top: 1px solid var(--border); background: var(--bg-subtle); width: 100%; flex-shrink: 0;"):
                        ui.button("Close", on_click=dlg.close).classes("btn btn-primary").style("padding: 8px 32px;")
            dlg.open()

        table_state = {"search": "", "page": 1, "limit": 10}
        
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

            with ui.element("div").classes("card"):
                with ui.element("div").classes("card-header").style("display: flex; justify-content: space-between; align-items: center; min-height: 56px;"):
                    ui.html(f'<span class="card-title">Upload History</span>')
                    
                    bulk_actions = ui.element("div").style("display: none;")
                    with bulk_actions:
                        bulk_btn = ui.button("Delete Selected", icon=IC.DELETE, on_click=trigger_bulk_delete)
                        bulk_btn.props("size=sm").style("background-color: #ef4444 !important; color: white !important;")

                def update_bulk_actions():
                    if len(selected_sessions) > 0:
                        bulk_actions.style("display: block;")
                        bulk_btn.set_text(f"Delete Selected ({len(selected_sessions)})")
                    else:
                        bulk_actions.style("display: none;")

                with ui.element("div").style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); gap: 16px; flex-wrap: wrap;"):
                    with ui.element("div").style("display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted);"):
                        ui.html("<span>Show</span>")
                        def update_limit(e):
                            table_state["limit"] = e.value
                            table_state["page"] = 1
                            table_content.refresh()
                        ui.select(options=[10, 25, 50, 100], value=table_state["limit"], on_change=update_limit).props('dense outlined').style("width: 70px;")
                        ui.html("<span>entries</span>")
                        
                    with ui.element("div"):
                        def update_search(e):
                            val = e.value or ""
                            if table_state["search"] != val:
                                table_state["search"] = val
                                table_state["page"] = 1
                                table_content.refresh()
                        ui.input(placeholder="Search filename...", value=table_state["search"], on_change=update_search).props('dense outlined clearable').style("width: 250px;")

                with ui.element("div").classes("card-body").style("padding: 0; overflow-x: auto;"):
                    @ui.refreshable
                    def table_content():
                        import math
                        term = table_state["search"].lower()
                        filtered_sessions = [s for s in sessions if term in s.filename.lower()] if term else sessions
                    
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
                                                    ).props('flat round size=sm color="primary"').tooltip("View Details")
                                                    ui.button(
                                                        icon=IC.DELETE, 
                                                        on_click=lambda s=s: confirm_delete([s.id], s.filename, handle_delete_success)
                                                    ).props('flat round size=sm color="negative"').style("color: #ef4444 !important;").tooltip("Delete Session")

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
