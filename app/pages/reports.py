"""
Reports Page — Generate and export various attendance reports
"""
from nicegui import ui
from datetime import date

from app.pages.layout import app_layout
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import Company
from app.components.notifications import toast_info, toast_success, toast_error


REPORT_TYPES = [
    ("dtr",       "Employee DTR",          IC.BADGE,    "Individual employee daily time record"),
    ("daily",     "Daily Attendance",      IC.ATTENDANCE,"All employees attendance for a specific day"),
    ("monthly",   "Monthly Attendance",    IC.CALENDAR, "Monthly attendance summary per employee"),
    ("company",   "Company Attendance",    IC.COMPANIES,"Attendance report grouped by company"),
    ("late",      "Late Report",           IC.LATE,     "Employees who arrived late"),
    ("absent",    "Absent Report",         IC.ABSENT,   "Employees with no log entries"),
    ("missing",   "Missing Logs Report",   IC.WARNING,  "Days with incomplete or missing time records"),
]


def reports_page():
    selected = {"type": None}
    form_refs = {}

    with app_layout("Reports", "/reports", ["Reports"]):

        ui.html('''
        <div class="page-header">
          <h1 class="page-title">Reports</h1>
          <p class="page-subtitle">Generate PDF and Excel attendance reports</p>
        </div>
        ''')

        with ui.element("div").style("display:grid;grid-template-columns:300px 1fr;gap:24px;"):

            # ── Report Type Selector ──────────────────────────────────────────
            with ui.element("div"):
                with ui.element("div").classes("card"):
                    with ui.element("div").classes("card-header"):
                        ui.html('<span class="card-title">Report Type</span>')
                    with ui.element("div").classes("card-body").style("padding:12px;"):
                        report_btns = {}
                        form_container = ui.element("div")  # Will be updated below

                        def select_report(rtype, btn_el):
                            selected["type"] = rtype
                            for k, b in report_btns.items():
                                b.style(remove="background:rgba(37,99,235,.1);color:var(--color-primary);font-weight:600;")
                            btn_el.style("background:rgba(37,99,235,.1);color:var(--color-primary);font-weight:600;")
                            render_form(rtype)

                        for rtype, label, icon, desc in REPORT_TYPES:
                            btn = ui.element("div").classes("nav-item").style("border-radius:8px;")
                            with btn:
                                ui.html(f'<span class="material-icons-round" style="font-size:18px;">{icon}</span>')
                                with ui.element("div"):
                                    ui.html(f'<div style="font-size:13px;font-weight:500;">{label}</div>')
                                    ui.html(f'<div style="font-size:11px;color:var(--text-muted);">{desc}</div>')

                            btn.on("click", lambda e, rt=rtype, b=btn: select_report(rt, b))
                            report_btns[rtype] = btn

            # ── Report Form + Generate ────────────────────────────────────────
            with ui.element("div"):
                form_container = ui.element("div").classes("card")

                def render_form(rtype):
                    form_container.clear()
                    with form_container:
                        rtype_label = next((l for t, l, *_ in REPORT_TYPES if t == rtype), rtype)

                        with ui.element("div").classes("card-header"):
                            ui.html(f'<span class="card-title">Generate: {rtype_label}</span>')

                        with ui.element("div").classes("card-body"):
                            db = SessionLocal()
                            try:
                                cos = db.query(Company).filter(Company.is_active == True).all()
                                co_options = {0: "— All Companies —", **{c.id: c.name for c in cos}}
                            finally:
                                db.close()

                            ui.html('<div class="form-label">Company</div>')
                            form_refs["company"] = ui.select(
                                options=co_options, value=0
                            ).props("outlined dense").style("width:100%;margin-bottom:14px;")

                            with ui.element("div").classes("grid-cols-2").style("margin-bottom:14px;"):
                                with ui.element("div"):
                                    ui.html('<div class="form-label">Date From</div>')
                                    form_refs["date_from"] = ui.input(
                                        value=date.today().replace(day=1).isoformat()
                                    ).props("outlined dense type=date").style("width:100%;")

                                with ui.element("div"):
                                    ui.html('<div class="form-label">Date To</div>')
                                    form_refs["date_to"] = ui.input(
                                        value=date.today().isoformat()
                                    ).props("outlined dense type=date").style("width:100%;")

                            # Export buttons
                            ui.element("div").classes("separator")

                            with ui.element("div").style("display:flex;gap:10px;margin-top:4px;"):

                                async def gen_pdf():
                                    try:
                                        from app.services.report_service import generate_report
                                        from app.core.config import REPORTS_DIR
                                        co_id = form_refs["company"].value or None
                                        d_from = date.fromisoformat(form_refs["date_from"].value)
                                        d_to   = date.fromisoformat(form_refs["date_to"].value)
                                        filename = f"{rtype}_report_{d_from}_{d_to}.pdf"
                                        path = REPORTS_DIR / filename
                                        toast_info("Generating PDF…", "Please wait")
                                        generate_report(rtype, co_id, d_from, d_to, str(path), fmt="pdf")
                                        ui.download(str(path), filename)
                                        toast_success("PDF Ready", filename)
                                    except Exception as ex:
                                        toast_error("Error", str(ex))

                                async def gen_excel():
                                    try:
                                        from app.services.report_service import generate_report
                                        from app.core.config import REPORTS_DIR
                                        co_id = form_refs["company"].value or None
                                        d_from = date.fromisoformat(form_refs["date_from"].value)
                                        d_to   = date.fromisoformat(form_refs["date_to"].value)
                                        filename = f"{rtype}_report_{d_from}_{d_to}.xlsx"
                                        path = REPORTS_DIR / filename
                                        toast_info("Generating Excel…", "Please wait")
                                        generate_report(rtype, co_id, d_from, d_to, str(path), fmt="excel")
                                        ui.download(str(path), filename)
                                        toast_success("Excel Ready", filename)
                                    except Exception as ex:
                                        toast_error("Error", str(ex))

                                with ui.element("button").classes("btn btn-primary").on("click", gen_pdf):
                                    ui.html(f'<span class="material-icons-round" style="font-size:16px;">{IC.EXPORT_PDF}</span> Export PDF')

                                with ui.element("button").classes("btn btn-success").on("click", gen_excel):
                                    ui.html(f'<span class="material-icons-round" style="font-size:16px;">{IC.EXPORT_EXCEL}</span> Export Excel')

                # Initial state
                with form_container:
                    with ui.element("div").classes("card-body"):
                        ui.html(f'''
                        <div class="empty-state">
                          <span class="material-icons-round">{IC.REPORTS}</span>
                          <div class="empty-state-title">Select a report type</div>
                          <div class="empty-state-desc">Choose a report from the left panel to get started</div>
                        </div>
                        ''')
