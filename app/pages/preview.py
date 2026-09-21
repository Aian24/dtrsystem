"""
DTR Preview Page — Read-only, printable DTR report with configurable signatures
"""
from __future__ import annotations
from nicegui import ui
from datetime import date, datetime, timedelta

from app.pages.layout import app_layout
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import Employee, Company, CutoffPeriod
from app.services.dtr_service import compute_dtr


def preview_page(request=None, is_public=False):
    """Called from route_preview with a FastAPI Request object."""
    # Parse query params
    params = {}
    if request:
        params = dict(request.query_params)

    emp_id    = int(params.get("emp", 0))
    cutoff_id = int(params.get("cutoff", 0)) if "cutoff" in params else None
    date_from_str = params.get("from", "")
    date_to_str   = params.get("to",   "")
    month_str     = params.get("month", "")

    if not emp_id:
        ui.navigate.to("/" if is_public else "/lookup")
        return

    # Load data
    db = SessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.id == emp_id).first()
        if not emp:
            ui.navigate.to("/" if is_public else "/lookup")
            return

        company = emp.company

        if cutoff_id and month_str:
            import calendar
            cutoff = db.query(CutoffPeriod).filter(CutoffPeriod.id == cutoff_id).first()
            year, month = map(int, month_str.split("-"))
            _, last_day = calendar.monthrange(year, month)
            
            s_day = cutoff.start_day
            e_day = cutoff.end_day if cutoff.end_day != 31 else last_day
            
            # clamp days if user enters 30 but month has 28 etc
            if s_day > last_day: s_day = last_day
            if e_day > last_day: e_day = last_day

            date_from = date(year, month, s_day)
            date_to   = date(year, month, e_day)
            
            d1_str = date_from.strftime("%B %d, %Y").replace(" 0", " ")
            d2_str = date_to.strftime("%B %d, %Y").replace(" 0", " ")
            period_label = f"{d1_str} — {d2_str}"
        else:
            date_from = date.fromisoformat(date_from_str) if date_from_str else date.today().replace(day=1)
            date_to   = date.fromisoformat(date_to_str)   if date_to_str   else date.today()
            d1_str = date_from.strftime("%B %d, %Y").replace(" 0", " ")
            d2_str = date_to.strftime("%B %d, %Y").replace(" 0", " ")
            period_label = f"{d1_str} — {d2_str}"

        dtr_entries = compute_dtr(emp_id, date_from, date_to, db)

    finally:
        db.close()

    # Summary totals
    def has_any_punch(e):
        return any(e.get(k) for k in ["time_in", "break_out_1", "break_in_1", "break_out_2", "break_in_2", "time_out"])

    total_days      = sum(1 for e in dtr_entries if has_any_punch(e))
    total_absents   = sum(1 for e in dtr_entries if not has_any_punch(e) and e.get("remarks") == "Absent")
    total_late      = sum(1 for e in dtr_entries if e.get("is_late"))
    total_late_mins = sum(e.get("late_minutes") or 0 for e in dtr_entries)
    total_undertime_hrs = sum(e.get("undertime_minutes") or 0 for e in dtr_entries) / 60.0

    def render_content():
        ui.add_head_html('''
        <style>
        .preview-card {
            background: #ffffff;
            border: 1px solid #94A3B8;
            border-radius: 12px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        .preview-table-wrapper {
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            overflow: hidden;
        }
        @page { margin: 0; }
        @media print { 
            .no-print { display: none !important; }
            
            /* Hide default headers/footers by setting page margin to 0 */
            @page { margin: 0 !important; }
            
            /* Remove all background colors and shadows from layout wrappers */
            body, html, #q-app, .q-layout, .q-page-container, .q-page, .page-area, .nicegui-content {
                background: white !important;
                background-color: white !important;
                box-shadow: none !important;
                border: none !important;
            }
            
            /* Add our custom margin back via padding on the q-page wrapper */
            .q-page {
                padding: 0.5in !important;
                box-sizing: border-box !important;
                width: 100% !important;
            }
            
            /* Ensure the card itself doesn't have borders or weird margins in print */
            .preview-card {
                border: none !important;
                box-shadow: none !important;
                margin: 0 !important;
                width: 100% !important;
                max-width: 100% !important;
            }
            
            /* Keep the internal padding so the text doesn't touch the edges */
            .preview-card-body {
                padding: 0 !important;
            }
            
            /* Force the red rows to print their background */
            .preview-table tr.absent-row td {
                background-color: #fef2f2 !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            .preview-table tr.late-row td {
                background-color: #fff7ed !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            
            /* Reset table rows to white to avoid gray striping */
            .preview-table tr:nth-child(even) {
                background: white !important;
            }
            .preview-table tr {
                background: white !important;
            }
        }
        .preview-table {
            width: 100%;
            border-collapse: collapse;
            font-family: "Inter", "Arial", sans-serif;
            font-size: 10px;
            margin-bottom: 12px;
        }
        .preview-table th, .preview-table td {
            border: 1px solid #CBD5E1;
            padding: 4px;
            text-align: center;
        }
        .preview-table th {
            text-transform: uppercase;
            font-weight: 700;
            font-size: 9px;
            color: #475569;
        }
        .preview-table td {
            color: #1E293B;
            height: 20px;
        }
        .preview-table tr:nth-child(even) {
            background: #F8FAFC;
        }
        .preview-table tr.absent-row td {
            background-color: #fef2f2 !important;
        }
        .preview-table tr.late-row td {
            background-color: #fff7ed !important;
        }
        </style>
        ''')

        middle_initial = f" {emp.middle_name[0].upper()}." if emp.middle_name else ""
        emp_full_name = f"{emp.last_name.upper()}, {emp.first_name.upper()}{middle_initial}"

        # Editable signature state
        sig_state = {
            "appr1_name": company.area_manager if company and company.area_manager else "",
            "appr1_title": "APPROVED BY",
            "appr2_name": company.store_supervisor if company and company.store_supervisor else "",
            "appr2_title": "APPROVED BY",
            "emp_name": emp_full_name,
            "emp_title": "EMPLOYEE SIGNATURE",
        }

        # ── DTR Report Card ───────────────────────────────────────────────────
        with ui.element("div").classes("preview-card page-fade-in").style("max-width:900px; width:100%; margin:0 auto;"):
            with ui.element("div").classes("preview-card-body").style("padding:40px;"):

                # Header
                dept_part = f" - {emp.department.upper()}" if emp.department else ""
                emp_header_info = f"{emp.emp_id} - {emp_full_name}{dept_part}"
                ui.html(f'''
                <div style="text-align:center; margin-bottom:16px;">
                    <div style="font-family:'Arial', sans-serif; font-size:18px; font-weight:900; color:#0A1931; text-transform:uppercase; line-height:1; margin-bottom:4px;">
                        {company.name if company else "CONQUEROR INTERNATIONAL, INC."}
                    </div>
                    <div style="font-family:'Arial', sans-serif; font-size:11px; color:#6B7280; letter-spacing:0.5px; line-height:1.2; white-space:pre-line;">
                        {company.address if company and company.address else ""}
                    </div>
                </div>
                
                <div style="height:3px; background:#0A1931; margin-bottom:12px;"></div>
                
                <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:16px; font-family:'Arial', sans-serif;">
                    <div>
                        <div style="font-size:10px; font-weight:700; color:#6B7280; letter-spacing:0.5px; margin-bottom:2px;">
                            EMPLOYEE ID - NAME - DEPARTMENT
                        </div>
                        <div style="font-size:13px; font-weight:800; color:#0A1931;">
                            {emp_header_info}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:10px; font-weight:700; color:#6B7280; letter-spacing:0.5px; margin-bottom:2px;">
                            PAYROLL PERIOD
                        </div>
                        <div style="font-size:13px; font-weight:800; color:#0A1931; white-space:nowrap;">
                            {period_label}
                        </div>
                    </div>
                </div>
                ''')

                # DTR Table
                table_html = '<div class="preview-table-wrapper" style="margin-bottom:12px;">'
                table_html += '<table class="preview-table">'
                table_html += '<thead><tr>'
                headers = ["DAY", "DATE", "TIME IN", "1ST BO", "1ST BIN", "2ND BO", "2ND BIN", "TIME OUT", "REMARKS"]
                for h in headers:
                    th_style = ' style="width: 25%;"' if h == "REMARKS" else ''
                    table_html += f'<th{th_style}>{h}</th>'
                table_html += '</tr></thead><tbody>'

                for entry in dtr_entries:
                    row_class = ""
                    if entry.get("remarks") == "Absent":
                        row_class = "absent-row"
                    elif entry.get("is_late"):
                        row_class = "late-row"

                    d: date = entry["date"]
                    day_full = d.strftime("%A")
                    date_str = d.strftime("%m/%d/%Y")
                    
                    def clean(val):
                        if not val or val == "None": return ""
                        return val

                    table_html += f'<tr class="{row_class}">'
                    table_html += f'<td style="text-align:left; padding-left:10px;">{day_full}</td>'
                    table_html += f"<td>{date_str}</td>"
                    table_html += f'<td>{clean(entry.get("time_in"))}</td>'
                    table_html += f'<td>{clean(entry.get("break_out_1"))}</td>'
                    table_html += f'<td>{clean(entry.get("break_in_1"))}</td>'
                    table_html += f'<td>{clean(entry.get("break_out_2"))}</td>'
                    table_html += f'<td>{clean(entry.get("break_in_2"))}</td>'
                    table_html += f'<td>{clean(entry.get("time_out"))}</td>'
                    table_html += f'<td></td>'
                    table_html += '</tr>'

                table_html += '</tbody></table></div>'
                
                ui.html(table_html)
                
                # Signatures Section (Refreshable upon edit)
                @ui.refreshable
                def render_signatures():
                    appr1_display = sig_state["appr1_name"] if sig_state["appr1_name"] else "&nbsp;"
                    appr2_display = sig_state["appr2_name"] if sig_state["appr2_name"] else "&nbsp;"
                    emp_display   = sig_state["emp_name"] if sig_state["emp_name"] else "&nbsp;"

                    ui.html(f'''
                    <div style="display:flex; justify-content:space-between; margin-top:80px; padding: 0 40px; font-family:'Arial', sans-serif;">
                        <div style="text-align:center;">
                            <div style="font-size:12px; font-weight:700; color:#0A1931; text-transform:uppercase; margin-bottom:4px;">{appr1_display}</div>
                            <div style="width:180px; border-bottom:1px solid #0A1931; margin-bottom:6px;"></div>
                            <div style="font-size:10px; font-weight:800; color:#0A1931; text-transform:uppercase;">{sig_state["appr1_title"]}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:12px; font-weight:700; color:#0A1931; text-transform:uppercase; margin-bottom:4px;">{appr2_display}</div>
                            <div style="width:180px; border-bottom:1px solid #0A1931; margin-bottom:6px;"></div>
                            <div style="font-size:10px; font-weight:800; color:#0A1931; text-transform:uppercase;">{sig_state["appr2_title"]}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:12px; font-weight:700; color:#0A1931; text-transform:uppercase; margin-bottom:4px;">{emp_display}</div>
                            <div style="width:180px; border-bottom:1px solid #0A1931; margin-bottom:6px;"></div>
                            <div style="font-size:10px; font-weight:800; color:#0A1931; text-transform:uppercase;">{sig_state["emp_title"]}</div>
                        </div>
                    </div>
                    ''')

                render_signatures()

                # Comprehensive Summary Block (Hidden during print and on public user portal preview)
                if not is_public:
                    ui.html(f'''
                    <div class="no-print" style="margin-top:48px; padding-top:16px; border-top:1px solid #CBD5E1; font-family:'Arial', sans-serif;">
                        <div style="font-size:10px; font-weight:800; color:#475569; margin-bottom:12px; letter-spacing:0.5px;">SUMMARY OF HOURS</div>
                        <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:12px; text-align:center;">
                            <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                                <div style="font-size:16px; font-weight:900; color:#0A1931;">{total_days}</div>
                                <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">DAYS PRESENT</div>
                            </div>
                            <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                                <div style="font-size:16px; font-weight:900; color:#EF4444;">{total_absents}</div>
                                <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">ABSENTS</div>
                            </div>
                            <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                                <div style="font-size:16px; font-weight:900; color:#F59E0B;">{total_late}</div>
                                <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">DAYS LATE</div>
                            </div>
                            <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                                <div style="font-size:16px; font-weight:900; color:#F59E0B;">{total_late_mins}</div>
                                <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">LATE (MINS)</div>
                            </div>
                            <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                                <div style="font-size:16px; font-weight:900; color:#6366F1;">{total_undertime_hrs:.1f}</div>
                                <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">UNDERTIME (HRS)</div>
                            </div>
                        </div>
                    </div>
                    ''')

                # Edit Signatures Dialog Handler
                def open_edit_signatures_dialog():
                    with ui.dialog().classes('backdrop-blur-sm') as dlg:
                        with ui.card().style("width: 540px; max-width: 92vw; padding: 24px; border-radius: 16px;"):
                            ui.html('''
                            <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;">
                                <div style="width:40px;height:40px;border-radius:50%;background:rgba(37, 99, 235, 0.1);display:flex;align-items:center;justify-content:center;color:#2563eb;">
                                    <span class="material-icons-round" style="font-size:24px;">draw</span>
                                </div>
                                <div>
                                    <div style="font-size:18px;font-weight:700;color:var(--text-primary);">Edit Signatures & Approvers</div>
                                    <div style="font-size:12px;color:var(--text-secondary);">Modify sign-off names and roles for this preview or save as company defaults.</div>
                                </div>
                            </div>
                            ''')

                            with ui.column().classes("w-full gap-3"):
                                ui.html('<div style="font-size:13px; font-weight:700; color:var(--text-primary); margin-top:4px;">First Approver</div>')
                                with ui.row().classes("w-full gap-2"):
                                    inp_appr1_name = ui.input("Name", value=sig_state["appr1_name"]).props("outlined dense").classes("flex-1")
                                    inp_appr1_title = ui.input("Title / Role", value=sig_state["appr1_title"]).props("outlined dense").classes("flex-1")

                                ui.html('<div style="font-size:13px; font-weight:700; color:var(--text-primary); margin-top:8px;">Second Approver</div>')
                                with ui.row().classes("w-full gap-2"):
                                    inp_appr2_name = ui.input("Name", value=sig_state["appr2_name"]).props("outlined dense").classes("flex-1")
                                    inp_appr2_title = ui.input("Title / Role", value=sig_state["appr2_title"]).props("outlined dense").classes("flex-1")

                                ui.html('<div style="font-size:13px; font-weight:700; color:var(--text-primary); margin-top:8px;">Employee Signature</div>')
                                with ui.row().classes("w-full gap-2"):
                                    inp_emp_name = ui.input("Employee Name", value=sig_state["emp_name"]).props("outlined dense").classes("flex-1")
                                    inp_emp_title = ui.input("Title / Role", value=sig_state["emp_title"]).props("outlined dense").classes("flex-1")

                                save_default_cb = None
                                if company:
                                    save_default_cb = ui.checkbox(f"Save approver names as default for {company.name}", value=False).style("font-size:13px; margin-top:6px;")

                            def apply_signatures():
                                sig_state["appr1_name"] = (inp_appr1_name.value or "").strip()
                                sig_state["appr1_title"] = (inp_appr1_title.value or "APPROVED BY").strip().upper()
                                sig_state["appr2_name"] = (inp_appr2_name.value or "").strip()
                                sig_state["appr2_title"] = (inp_appr2_title.value or "APPROVED BY").strip().upper()
                                sig_state["emp_name"] = (inp_emp_name.value or "").strip()
                                sig_state["emp_title"] = (inp_emp_title.value or "EMPLOYEE SIGNATURE").strip().upper()

                                if company and save_default_cb and save_default_cb.value:
                                    db_s = SessionLocal()
                                    try:
                                        co_rec = db_s.query(Company).filter(Company.id == company.id).first()
                                        if co_rec:
                                            co_rec.area_manager = sig_state["appr1_name"] or None
                                            co_rec.store_supervisor = sig_state["appr2_name"] or None
                                            db_s.commit()
                                    finally:
                                        db_s.close()

                                render_signatures.refresh()
                                dlg.close()

                            with ui.row().classes("w-full justify-end gap-2").style("margin-top:20px;"):
                                ui.button("Cancel", on_click=dlg.close).classes("btn btn-secondary")
                                ui.button("Apply Changes", icon="check", on_click=apply_signatures).classes("btn btn-primary")

                    dlg.open()

                # Action Buttons
                with ui.element("div").classes("no-print").style("margin-top:32px; padding-top:24px; border-top:1px dashed #CBD5E1; display:flex; justify-content:center; align-items:center; gap:12px; flex-wrap:wrap;"):
                    with ui.element("button").classes("btn").style("background:#2563EB; color:#fff;").props('onclick="window.print()"'):
                        ui.html(f'<span class="material-icons-round" style="font-size:18px;">print</span> Print Sheet')
                    
                    if not is_public:
                        ui.button("Edit Signatures", icon="draw", on_click=open_edit_signatures_dialog).classes("btn btn-secondary").style("font-size:13px; font-weight:600; padding:8px 18px;").tooltip("Change approver names and titles on this sheet")

                    back_route = "/" if is_public else "/lookup"
                    with ui.element("a").props(f'href="{back_route}"').classes("btn").style("background:#F8FAFC; color:#0F172A; border:1px solid #CBD5E1; text-decoration:none; display:inline-flex; align-items:center; gap:6px;"):
                        ui.html(f'<span class="material-icons-round" style="font-size:18px;">arrow_back</span> Go Back')

    if is_public:
        from app.theme.styles import FONT_LINK, GLOBAL_CSS, GLOBAL_JS
        ui.html(f"{FONT_LINK}<style>{GLOBAL_CSS}</style>").classes("hidden")
        ui.add_body_html(f"<script>{GLOBAL_JS}</script>")
        ui.html("""<style>@media screen { body { background: #E2E8F0 !important; } }</style>""")
        with ui.element("div").classes("page-area w-full max-w-full").style("padding: 40px;"):
            render_content()
    else:
        with app_layout("DTR Preview", "/lookup", ["DTR Lookup", "Preview"]):
            render_content()