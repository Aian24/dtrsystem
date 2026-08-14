"""
DTR Preview Page — Read-only, printable DTR report
"""
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

    # Summary totals (Keeping these in case they are needed elsewhere)
    total_days      = len([e for e in dtr_entries if e.get("time_in")])
    total_absents   = sum(1 for e in dtr_entries if not e.get("time_in") and e.get("remarks") != "Rest Day")
    total_late      = sum(1 for e in dtr_entries if e.get("is_late"))
    total_late_mins = sum(e.get("late_minutes") or 0 for e in dtr_entries)

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
        @page { margin: 0.5in; }
        @media print { 
            .no-print { display: none !important; }
            .preview-card, .preview-card-body, .page-area, .nicegui-content, .preview-table-wrapper, .q-page-container, .q-page, .q-layout { 
                box-shadow: none !important; 
                border: none !important; 
                background: transparent !important; 
                border-radius: 0 !important;
                margin: 0 !important;
                max-width: none !important;
                width: 100% !important;
                padding: 0 !important;
                min-height: 0 !important;
            }
            body, html { background: white !important; padding: 0 !important; margin: 0 !important; }
            .q-drawer, .q-header { display: none !important; }
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
        </style>
        ''')

        middle_initial = f" {emp.middle_name[0].upper()}." if emp.middle_name else ""
        emp_full_name = f"{emp.last_name.upper()}, {emp.first_name.upper()}{middle_initial}"

        # ── DTR Report Card ───────────────────────────────────────────────────
        with ui.element("div").classes("preview-card page-fade-in").style("max-width:900px; width:100%; margin:0 auto;"):
            with ui.element("div").classes("preview-card-body").style("padding:40px;"):

                # Header
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
                            EMPLOYEE CODE & NAME
                        </div>
                        <div style="font-size:13px; font-weight:800; color:#0A1931;">
                            {emp.emp_id} / {emp_full_name}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:10px; font-weight:700; color:#6B7280; letter-spacing:0.5px; margin-bottom:2px;">
                            PAYROLL PERIOD
                        </div>
                        <div style="font-size:13px; font-weight:800; color:#0A1931;">
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
                    row_bg = ""
                    if not entry.get("time_in"):
                        row_bg = "background:rgba(239,68,68,.04);"
                    elif entry.get("is_late"):
                        row_bg = "background:rgba(245,158,11,.04);"

                    d: date = entry["date"]
                    day_full = d.strftime("%A")
                    date_str = d.strftime("%m/%d/%Y")
                    
                    def clean(val):
                        if not val or val == "None": return ""
                        return val

                    table_html += f'<tr style="{row_bg}">'
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
                
                # Signature
                ui.html(f'''
                <div style="display:flex; justify-content:space-between; margin-top:80px; padding: 0 40px; font-family:'Arial', sans-serif;">
                    <div style="text-align:center;">
                        <div style="font-size:12px; font-weight:700; color:#0A1931; text-transform:uppercase; margin-bottom:4px;">{(company.area_manager if company and company.area_manager else "&nbsp;")}</div>
                        <div style="width:180px; border-bottom:1px solid #0A1931; margin-bottom:6px;"></div>
                        <div style="font-size:10px; font-weight:800; color:#0A1931; text-transform:uppercase;">Area Manager</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:12px; font-weight:700; color:#0A1931; text-transform:uppercase; margin-bottom:4px;">{(company.store_supervisor if company and company.store_supervisor else "&nbsp;")}</div>
                        <div style="width:180px; border-bottom:1px solid #0A1931; margin-bottom:6px;"></div>
                        <div style="font-size:10px; font-weight:800; color:#0A1931; text-transform:uppercase;">Store Supervisor</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:12px; font-weight:700; color:#0A1931; text-transform:uppercase; margin-bottom:4px;">{emp_full_name}</div>
                        <div style="width:180px; border-bottom:1px solid #0A1931; margin-bottom:6px;"></div>
                        <div style="font-size:10px; font-weight:800; color:#0A1931; text-transform:uppercase;">Employee Signature</div>
                    </div>
                </div>
                ''')

                # Comprehensive Summary Block
                ui.html(f'''
                <div style="margin-top:48px; padding-top:16px; border-top:1px solid #CBD5E1; font-family:'Arial', sans-serif;">
                    <div style="font-size:10px; font-weight:800; color:#475569; margin-bottom:12px; letter-spacing:0.5px;">SUMMARY OF HOURS</div>
                    <div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:12px; text-align:center;">
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
                            <div style="font-size:16px; font-weight:900; color:#10B981;">0</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">TOTAL OT (HRS)</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#6366F1;">0</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">UNDERTIME (HRS)</div>
                        </div>
                    </div>
                </div>
                ''')

                # Action Buttons
                with ui.element("div").classes("no-print").style("margin-top:32px; padding-top:24px; border-top:1px dashed #CBD5E1; display:flex; justify-content:center; gap:12px;"):
                    with ui.element("button").classes("btn").style("background:#2563EB; color:#fff;").props('onclick="window.print()"'):
                        ui.html(f'<span class="material-icons-round" style="font-size:18px;">print</span> Print Sheet')
                    
                    back_route = "/" if is_public else "/lookup"
                    with ui.element("a").props(f'href="{back_route}"').classes("btn").style("background:#F8FAFC; color:#0F172A; border:1px solid #CBD5E1; text-decoration:none;"):
                        ui.html(f'<span class="material-icons-round" style="font-size:18px;">arrow_back</span> Go Back')

    if is_public:
        from app.theme.styles import FONT_LINK, GLOBAL_CSS, GLOBAL_JS
        ui.html(f"{FONT_LINK}<style>{GLOBAL_CSS}</style>").classes("hidden")
        ui.add_body_html(f"<script>{GLOBAL_JS}</script>")
        ui.html("""<style>body { background: #E2E8F0 !important; }</style>""")
        with ui.element("div").classes("page-area w-full max-w-full").style("padding: 40px;"):
            render_content()
    else:
        with app_layout("DTR Preview", "/lookup", ["DTR Lookup", "Preview"]):
            render_content()