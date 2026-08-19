"""
DTR Lookup Page — Search employee & generate DTR preview
"""
from nicegui import ui
from datetime import date, timedelta

from app.pages.layout import app_layout
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import Employee, Company, CutoffPeriod
from app.components.notifications import toast_error


def lookup_page():

    def get_companies():
        db = SessionLocal()
        try:
            return {c.id: c.name for c in db.query(Company).filter(Company.is_active == True).all()}
        finally:
            db.close()

    def get_employees(company_id=None):
        db = SessionLocal()
        try:
            q = db.query(Employee).filter(Employee.is_active == True)
            if company_id:
                q = q.filter(Employee.company_id == company_id)
            return q.all()
        finally:
            db.close()

    def get_cutoffs(company_id=None):
        if not company_id:
            return {}
        db = SessionLocal()
        try:
            cutoffs = db.query(CutoffPeriod).filter(
                CutoffPeriod.company_id == company_id
            ).order_by(CutoffPeriod.id.desc()).limit(24).all()
            return {c.id: c.label for c in cutoffs}
        finally:
            db.close()

    form_state = {
        "company_id":  None,
        "employee_id": None,
        "cutoff_id":   None,
        "date_from":   (date.today().replace(day=1)).isoformat(),
        "date_to":     date.today().isoformat(),
        "use_cutoff":  False,
    }

    with app_layout("DTR Lookup", "/lookup", ["DTR Lookup"]):

        ui.html('''
        <div class="page-header">
          <h1 class="page-title">DTR Lookup</h1>
          <p class="page-subtitle">Search employee attendance records and generate DTR reports</p>
        </div>
        ''')

        with ui.element("div").style("display:grid;grid-template-columns:340px 1fr;gap:24px;"):

            # ── Filter Panel ──────────────────────────────────────────────────
            with ui.element("div"):
                with ui.element("div").classes("card"):
                    with ui.element("div").classes("card-header"):
                        ui.html(f'<span class="card-title"><span class="material-icons-round" style="font-size:16px;vertical-align:middle;margin-right:6px;">{IC.FILTER}</span>Search Filters</span>')
                    with ui.element("div").classes("card-body"):

                        companies = get_companies()

                        # Company select
                        ui.html('<div class="form-label">Company</div>')
                        company_sel = ui.select(
                            options={0: "— All Companies —", **companies},
                            value=0,
                        ).props("outlined dense").style("width:100%;margin-bottom:14px;")

                        # Employee select
                        ui.html('<div class="form-label" style="margin-top:4px;">Employee</div>')
                        emp_options = {"": "— Select Employee —"}
                        employee_sel = ui.select(
                            options=emp_options,
                            value="",
                        ).props("outlined dense").style("width:100%;margin-bottom:14px;")

                        # Cutoff vs Date Range toggle
                        use_cutoff_chk = ui.checkbox("Use Cutoff Period").style("margin-bottom:10px;")

                        # Date range
                        date_section = ui.element("div")
                        with date_section:
                            ui.html('<div class="form-label">Date From</div>')
                            date_from = ui.input(
                                value=form_state["date_from"],
                                placeholder="YYYY-MM-DD"
                            ).props("outlined dense type=date").style("width:100%;margin-bottom:10px;")

                            ui.html('<div class="form-label">Date To</div>')
                            date_to = ui.input(
                                value=form_state["date_to"],
                                placeholder="YYYY-MM-DD"
                            ).props("outlined dense type=date").style("width:100%;")

                        # Cutoff section (hidden by default)
                        cutoff_section = ui.element("div").style("display:none;")
                        cutoff_sel = None
                        month_sel = None
                        with cutoff_section:
                            ui.html('<div class="form-label">Cutoff Month</div>')
                            month_sel = ui.input(
                                value=date.today().strftime("%Y-%m"),
                                placeholder="YYYY-MM"
                            ).props("outlined dense type=month").style("width:100%;margin-bottom:10px;")

                            ui.html('<div class="form-label">Cutoff Period</div>')
                            cutoff_sel = ui.select(
                                options={"": "— Select Cutoff —"},
                                value="",
                            ).props("outlined dense").style("width:100%;")

                        def on_company_change(e):
                            cid = getattr(e, 'value', e.sender.value) if getattr(e, 'value', e.sender.value) != 0 else None
                            form_state["company_id"] = cid
                            # Update employee list
                            emps = get_employees(cid)
                            emp_options_new = {"": "— Select Employee —"}
                            emp_options_new.update({
                                str(emp.id): f"{emp.last_name}, {emp.first_name} [{emp.emp_id}]"
                                for emp in emps
                            })
                            employee_sel.set_options(emp_options_new, value="")
                            # Update cutoffs
                            cutoffs = get_cutoffs(cid)
                            if cutoff_sel:
                                cutoff_sel.set_options({"": "— Select Cutoff —", **{str(k): v for k,v in cutoffs.items()}}, value="")

                        def on_cutoff_toggle(e):
                            form_state["use_cutoff"] = getattr(e, 'value', e.sender.value)
                            if form_state["use_cutoff"]:
                                date_section.style("display:none;")
                                cutoff_section.style("display:block;")
                            else:
                                date_section.style("display:block;")
                                cutoff_section.style("display:none;")

                        company_sel.on("update:model-value", on_company_change)
                        use_cutoff_chk.on("update:model-value", on_cutoff_toggle)

                        ui.element("div").classes("separator")

                        # Buttons
                        def do_preview():
                            emp_id_str = employee_sel.value
                            if not emp_id_str:
                                toast_error("No Employee Selected", "Please select an employee first.")
                                return
                            form_state["employee_id"] = int(emp_id_str)

                            if form_state["use_cutoff"] and cutoff_sel:
                                if not cutoff_sel.value:
                                    toast_error("No Cutoff", "Please select a cutoff period.")
                                    return
                                form_state["cutoff_id"] = int(cutoff_sel.value)
                                form_state["date_from"] = None
                                form_state["date_to"]   = None
                            else:
                                form_state["date_from"] = date_from.value
                                form_state["date_to"]   = date_to.value
                                form_state["cutoff_id"] = None

                            # Navigate to preview with query params
                            params = f"emp={form_state['employee_id']}"
                            if form_state["cutoff_id"]:
                                if not month_sel.value:
                                    toast_error("No Month", "Please select a cutoff month.")
                                    return
                                params += f"&cutoff={form_state['cutoff_id']}&month={month_sel.value}"
                            else:
                                params += f"&from={form_state['date_from']}&to={form_state['date_to']}"
                            ui.navigate.to(f"/preview?{params}")

                        with ui.element("div").style("display:flex;gap:8px;margin-top:16px;"):
                            with ui.element("button").classes("btn btn-primary").style("flex:1;").on("click", do_preview):
                                ui.html(f'<span class="material-icons-round" style="font-size:15px;">{IC.LOOKUP}</span> Preview DTR')
                            with ui.element("button").classes("btn btn-secondary").on(
                                "click", lambda: company_sel.set_value(0)
                            ):
                                ui.html(f'<span class="material-icons-round" style="font-size:15px;">{IC.CANCEL}</span>')

            # ── Right: Instructions / Recent ──────────────────────────────────
            with ui.element("div"):
                with ui.element("div").classes("card"):
                    with ui.element("div").classes("card-body"):
                        ui.html(f'''
                        <div class="empty-state" style="padding:40px 20px;">
                          <span class="material-icons-round" style="color:var(--color-primary);opacity:.6;">{IC.LOOKUP}</span>
                          <div class="empty-state-title">Select filters and click Preview DTR</div>
                          <div class="empty-state-desc">
                            The DTR report will be generated and displayed in a new page.<br>
                            You can then print or export as PDF.
                          </div>
                        </div>
                        ''')
