"""
Upload Logs Page — Drag & Drop with animated progress bar
"""
import asyncio
import threading
from pathlib import Path
from nicegui import ui, events

from app.pages.layout import app_layout
from app.components.cards import upload_summary_card
from app.components.notifications import toast_success, toast_error
from app.theme.icons import IC
from app.services.import_service import import_log_file
from app.core.config import LOGS_DIR
from app.core.database import SessionLocal
from app.core.models import UploadSession, AttendanceLog


def upload_page():
    state = {
        "uploading": False,
        "result":    None,
        "filename":  "",
    }

    with app_layout("Upload Logs", "/upload", ["Upload Logs"]):

        ui.add_css('''
        .upload-wrapper {
            position: relative;
            width: 100%;
        }

        .upload-zone {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 280px;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 2px dashed var(--border);
            border-radius: 12px;
            background: var(--surface);
            transition: all 0.2s ease;
        }
        
        .my-uploader {
            position: relative;
            z-index: 2;
            background: transparent !important;
            width: 100% !important;
            box-shadow: none !important;
        }

        /* Make the header invisible but perfectly sized to cover the upload-zone */
        .my-uploader .q-uploader__header {
            opacity: 0.001 !important;
            height: 280px !important;
            position: relative !important; /* containing block for the stretched input */
            background: transparent !important;
        }

        /* Break out of inner constraints so input can fill the header */
        .my-uploader .q-btn,
        .my-uploader .q-btn__content,
        .my-uploader .q-focus-helper,
        .my-uploader .q-icon {
            position: static !important;
            transform: none !important;
            overflow: visible !important;
            clip: auto !important;
            contain: none !important;
        }
        
        /* Force Quasar's hidden file input to cover the 280px header entirely */
        .my-uploader input[type="file"] {
            display: block !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            max-width: none !important;
            max-height: none !important;
            z-index: 9999 !important;
            opacity: 0 !important;
            cursor: pointer !important;
        }

        /* Ensure the file list shows up cleanly */
        .my-uploader .q-uploader__list {
            background: transparent !important;
            padding: 0 !important;
            border: none !important;
            margin-top: 16px !important;
        }
        
        .my-uploader .q-uploader__file {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            margin-bottom: 8px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
            display: flex !important;
            align-items: center !important;
        }
        
        .my-uploader .q-uploader__file::before {
            content: "\\e873"; /* material icon for 'description' */
            font-family: "Material Icons Round", "Material Icons";
            font-size: 24px;
            color: var(--color-primary);
            margin-right: 16px;
        }

        .my-uploader .q-uploader__file-header {
            background: transparent !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }
        
        .my-uploader .q-uploader__file-header-content {
            padding-right: 16px !important;
        }

        .my-uploader .q-uploader__title {
            font-weight: 500 !important;
            color: var(--text-primary) !important;
            font-size: 14px !important;
            margin-bottom: 0 !important;
        }

        .my-uploader .q-uploader__subtitle {
            display: none !important; /* Hide the size/progress text */
        }
        
        /* Style the delete button */
        .my-uploader .q-uploader__file .q-btn {
            color: var(--text-muted) !important;
            transition: color 0.2s;
        }
        .my-uploader .q-uploader__file .q-btn:hover {
            color: #ef4444 !important;
        }

        /* Remove the Quasar grey background for file items */
        .q-uploader__file--light {
            color: inherit !important;
        }
        
        .history-row {
            transition: background 0.2s ease;
            cursor: pointer;
        }
        .history-row:hover {
            background: #F1F5F9 !important;
        }
        ''')

        ui.html('''
        <div class="page-header">
          <h1 class="page-title">Upload Attendance Logs</h1>
          <p class="page-subtitle">Import biometric log files (.log) from your attendance machines</p>
        </div>
        ''')

        with ui.element("div").style("display:grid;grid-template-columns:1fr 380px;gap:24px;"):

            # ── Left: Upload area ─────────────────────────────────────────────
            with ui.element("div"):

                # Upload zone
                with ui.element("div").classes("card").style("margin-bottom:20px;"):
                    with ui.element("div").classes("card-body"):

                        # Result card (rendered on main thread when done)
                        result_container = ui.element("div").style("margin-top:20px;")

                        # Create the Progress Modal OUTSIDE the event handler
                        with ui.dialog().classes('backdrop-blur-sm') as progress_modal:
                            progress_modal.props('persistent')
                            with ui.card().style("width: 400px; max-width: 90vw; padding: 24px; border-radius: 16px;"):
                                ui.html('''
                                <div style="font-size: 18px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">
                                    Uploading Logs
                                </div>
                                <div id="modal-filename-display" style="font-size: 13.5px; color: var(--text-muted); margin-bottom: 24px;">
                                    Processing...
                                </div>
                                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:13px;font-weight:500;">
                                  <span id="modal-progress-label" style="color:var(--text-primary);">Processing…</span>
                                  <span id="modal-progress-pct" style="color:var(--color-primary);">0%</span>
                                </div>
                                ''')
                                with ui.element("div").classes("progress-bar-wrapper"):
                                    modal_progress_bar = ui.element("div").classes("progress-bar-fill").style("width:0%; transition: width 0.2s;")

                        # Lock to process multiple files sequentially without DB locks
                        upload_lock = asyncio.Lock()

                        async def handle_multi_upload(e: events.MultiUploadEventArguments):
                            async with upload_lock:
                                total_res = {"total": 0, "imported": 0, "duplicates": 0, "invalid": 0}
                                file_names = []
                                
                                ui.run_javascript('document.getElementById("modal-filename-display").innerHTML = "Processing files...";')
                                progress_modal.open()
                                
                                for file_name, file_content_obj in zip(e.names, e.contents):
                                    file_names.append(file_name)
                                    ui.run_javascript(f'document.getElementById("modal-filename-display").innerHTML = "Processing <strong>{file_name}</strong>";')
                                    
                                    # Save file
                                    save_path = LOGS_DIR / file_name
                                    file_content = file_content_obj.read() if hasattr(file_content_obj, "read") else await file_content_obj.read()
                                    save_path.write_bytes(file_content)
                                    
                                    import_state = {"pct": 0, "msg": "Reading file...", "done": False, "error": None, "result": None}
                                    
                                    def progress_cb(pct: int, msg: str = ""):
                                        import_state["pct"] = pct
                                        import_state["msg"] = msg
                                        
                                    def run_import():
                                        try:
                                            result = import_log_file(str(save_path), progress_cb)
                                            import_state["result"] = result
                                            import_state["done"] = True
                                        except Exception as ex:
                                            import_state["error"] = str(ex)
                                            import_state["done"] = True
                                            
                                    thread = threading.Thread(target=run_import, daemon=True)
                                    thread.start()
                                    
                                    while not import_state["done"]:
                                        modal_progress_bar.style(f"width:{import_state['pct']}%;")
                                        ui.run_javascript(f'''
                                          let p = document.getElementById("modal-progress-pct");
                                          let l = document.getElementById("modal-progress-label");
                                          if (p) p.textContent = "{import_state['pct']}%";
                                          if (l) l.textContent = "{import_state['msg']}";
                                        ''')
                                        await asyncio.sleep(0.2)
                                        
                                    if import_state["result"]:
                                        res = import_state["result"]
                                        total_res["total"] += res["total"]
                                        total_res["imported"] += res["imported"]
                                        total_res["duplicates"] += res["duplicates"]
                                        total_res["invalid"] += res["invalid"]
                                    elif import_state["error"]:
                                        toast_error(f"Import Failed for {file_name}", import_state["error"])
                                
                                progress_modal.close()
                                
                                display_name = f"{len(file_names)} file{'s' if len(file_names) > 1 else ''} uploaded" if len(file_names) > 1 else (file_names[0] if file_names else "Batch Upload")
                                
                                with ui.dialog().classes('backdrop-blur-sm') as success_modal:
                                    success_modal.props('persistent')
                                    with ui.card().style("width: 450px; max-width: 90vw; padding: 0; border-radius: 16px; overflow: hidden; align-items: stretch;"):
                                        with ui.element('div').style("padding: 24px; width: 100%; position: relative;"):
                                            # Removed the X button as requested!
                                            upload_summary_card(
                                                filename=display_name,
                                                total=total_res["total"],
                                                imported=total_res["imported"],
                                                duplicates=total_res["duplicates"],
                                                invalid=total_res["invalid"],
                                            )
                                        
                                        with ui.element('div').style("padding: 16px 24px; display: flex; justify-content: flex-end; border-top: 1px solid var(--border); background: var(--bg-subtle); width: 100%;"):
                                            ui.button("OK", on_click=success_modal.close).classes("btn btn-primary").style("padding: 8px 32px;")
                                            
                                success_modal.open()
                                
                                # Wait for user to dismiss modal before allowing next batch
                                while success_modal.value:
                                    await asyncio.sleep(0.1)
                                    
                                history_table.refresh()

                        with ui.element("div").classes("upload-wrapper"):
                            # The Beautiful UI
                            ui.html(f'''
                            <div class="upload-zone" id="upload-zone">
                              <div class="upload-icon">
                                <span class="material-icons-round">{IC.DRAG_DROP}</span>
                              </div>
                              <div style="font-size:16px;font-weight:600;color:var(--text-primary);margin-bottom:8px;">
                                Drag & drop your log file here
                              </div>
                              <div style="color:var(--text-muted);font-size:13.5px;margin-bottom:20px;">
                                or click to browse — supports <strong>.log</strong>, <strong>.txt</strong>, <strong>.csv</strong>
                              </div>
                              <div class="btn btn-primary" style="display:inline-flex;">
                                <span class="material-icons-round" style="font-size:16px;">{IC.UPLOAD}</span>
                                Browse File
                              </div>
                            </div>
                            ''')

                            # The Functional Uploader Layered On Top
                            upload = ui.upload(
                                label="",
                                auto_upload=False,
                                multiple=True,
                                on_multi_upload=handle_multi_upload,
                                on_rejected=lambda e: ui.notify(
                                    "Invalid file type. Please select a .log, .txt, or .csv file", 
                                    type="negative", 
                                    icon="error", 
                                    position="top-right"
                                )
                            ).props(
                                'accept=".log,.txt,.csv" color="primary" hide-upload-btn'
                            ).classes("my-uploader")
                            
                            # Custom Manual Submit Button
                            with ui.element("div").style("display:flex; justify-content:flex-end; margin-top: 16px;"):
                                submit_btn = ui.button(
                                    "Process Logs", 
                                    icon="publish",
                                    on_click=lambda: upload.run_method("upload")
                                ).classes("btn btn-primary").style("padding: 8px 24px; font-weight: 600; font-size: 14px; position: relative; z-index: 10;")


                # Upload history
                with ui.element("div").classes("card"):
                    with ui.element("div").classes("card-header"):
                        ui.html(f'''
                        <span class="card-title">Recent Uploads</span>
                        ''')
                    with ui.element("div").classes("card-body").style("padding:0;"):
                        
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
                        
                        @ui.refreshable
                        def history_table():
                            db = SessionLocal()
                            try:
                                sessions = db.query(UploadSession).order_by(
                                    UploadSession.uploaded_at.desc()
                                ).limit(10).all()
                            finally:
                                db.close()
    
                            if sessions:
                                with ui.element("table").classes("data-table"):
                                    with ui.element("thead"):
                                        with ui.element("tr"):
                                            for col in ["File", "Date", "Imported", "Duplicates", "Status"]:
                                                with ui.element("th"):
                                                    ui.html(col)
                                    with ui.element("tbody"):
                                        for s in sessions:
                                            with ui.element("tr").classes("history-row").on("click", lambda e, session=s: show_summary_modal(session)):
                                                with ui.element("td"):
                                                    ui.html(f"{s.filename}")
                                                with ui.element("td"):
                                                    ui.html(f"{s.uploaded_at.strftime('%b %d %Y %I:%M %p')}")
                                                with ui.element("td"):
                                                    ui.html(f"{s.imported_count:,}")
                                                with ui.element("td"):
                                                    ui.html(f"{s.duplicate_count:,}")
                                                with ui.element("td"):
                                                    ui.html(f'<span class="badge badge-success" style="background: rgba(16, 185, 129, 0.1); color: #10B981;">{s.status.upper()}</span>')
                            else:
                                ui.html('''
                                <div class="empty-state">
                                  <span class="material-icons-round">history</span>
                                  <div class="empty-state-title">No uploads yet</div>
                                </div>
                                ''')
                                
                        history_table()

            # ── Right: Instructions ───────────────────────────────────────────
            with ui.element("div"):
                with ui.element("div").classes("card").style("margin-bottom:16px;"):
                    with ui.element("div").classes("card-header"):
                        ui.html('<span class="card-title">Instructions</span>')
                    with ui.element("div").classes("card-body"):
                        ui.html('''
                        <div style="display:flex;flex-direction:column;gap:14px;">
                          <div style="display:flex;gap:12px;align-items:flex-start;">
                            <div style="width:28px;height:28px;border-radius:50%;
                                        background:linear-gradient(135deg,#2563EB,#3B82F6);
                                        display:flex;align-items:center;justify-content:center;
                                        flex-shrink:0;font-size:12px;font-weight:700;color:#fff;">1</div>
                            <div>
                              <div style="font-size:13.5px;font-weight:600;color:var(--text-primary);">Export from machine</div>
                              <div style="font-size:12.5px;color:var(--text-muted);margin-top:2px;">Export the attendance log file from your biometric machine</div>
                            </div>
                          </div>
                          <div style="display:flex;gap:12px;align-items:flex-start;">
                            <div style="width:28px;height:28px;border-radius:50%;
                                        background:linear-gradient(135deg,#2563EB,#3B82F6);
                                        display:flex;align-items:center;justify-content:center;
                                        flex-shrink:0;font-size:12px;font-weight:700;color:#fff;">2</div>
                            <div>
                              <div style="font-size:13.5px;font-weight:600;color:var(--text-primary);">Drop or browse</div>
                              <div style="font-size:12.5px;color:var(--text-muted);margin-top:2px;">Drag the .log file into the upload area or click Browse</div>
                            </div>
                          </div>
                          <div style="display:flex;gap:12px;align-items:flex-start;">
                            <div style="width:28px;height:28px;border-radius:50%;
                                        background:linear-gradient(135deg,#2563EB,#3B82F6);
                                        display:flex;align-items:center;justify-content:center;
                                        flex-shrink:0;font-size:12px;font-weight:700;color:#fff;">3</div>
                            <div>
                              <div style="font-size:13.5px;font-weight:600;color:var(--text-primary);">Review summary</div>
                              <div style="font-size:12.5px;color:var(--text-muted);margin-top:2px;">Check imported, duplicate, and invalid record counts</div>
                            </div>
                          </div>
                        </div>
                        ''')

                with ui.element("div").classes("card"):
                    with ui.element("div").classes("card-header"):
                        ui.html('<span class="card-title">Supported Format</span>')
                    with ui.element("div").classes("card-body"):
                        ui.html('''
                        <div style="background:var(--bg-subtle);border-radius:8px;padding:12px 14px;
                                    font-family:monospace;font-size:12.5px;color:var(--text-secondary);
                                    border:1px solid var(--border);">
                          <div style="color:var(--text-muted);font-size:11px;margin-bottom:6px;">Example rows:</div>
                          0050474,07/16/2026,07:29:00,I<br>
                          0006623,07/16/2026,07:35:00,I<br>
                          0050474,07/16/2026,17:01:00,O
                        </div>
                        <div style="margin-top:12px;font-size:12.5px;color:var(--text-muted);">
                          Format: <code>EmpID,Date,Time,Direction</code><br>
                          Direction: <strong>I</strong> = Check In, <strong>O</strong> = Check Out
                        </div>
                        ''')
