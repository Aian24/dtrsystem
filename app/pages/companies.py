"""
Companies Page — Manage companies and their settings
"""
from nicegui import ui
from sqlalchemy.orm import Session

from app.pages.layout import app_layout
from app.components.modals import form_dialog
from app.components.notifications import toast_success, toast_error
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import Company, Employee


def _get_companies():
    db = SessionLocal()
    try:
        cos = db.query(Company).filter(Company.is_active == True).all()
        return [
            {
                "id":           c.id,
                "name":         c.name,
                "address":      c.address or "—",
                "grace_period": f"{c.grace_period} min",
                "work_hours":   f"{c.work_start} – {c.work_end}",
                "employees":    len([e for e in c.employees if e.is_active]),
                # raw values for edit
                "_grace":       c.grace_period,
                "_start":       c.work_start,
                "_end":         c.work_end,
                "_address":     c.address or "",
                "_area_manager": c.area_manager or "",
                "_store_supervisor": c.store_supervisor or "",
            }
            for c in cos
        ]
    finally:
        db.close()


def delete_companies(company_ids: list[int], on_success=None):
    db: Session = SessionLocal()
    try:
        # Deactivate companies instead of hard delete, or check if they have employees
        companies = db.query(Company).filter(Company.id.in_(company_ids)).all()
        for c in companies:
            c.is_active = False
        db.commit()
        toast_success("Companies Deleted", f"{len(company_ids)} company(s) removed.")
        if on_success:
            on_success()
    except Exception as e:
        db.rollback()
        toast_error("Deletion Failed", str(e))
    finally:
        db.close()


def confirm_delete_company(company_ids: list[int], name: str, on_success=None):
    with ui.dialog().classes('backdrop-blur-sm') as dialog:
        dialog.props('persistent')
        with ui.card().style("width: 450px; max-width: 90vw; padding: 24px; border-radius: 16px;"):
            ui.html(f'''
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:40px;height:40px;border-radius:50%;background:rgba(239, 68, 68, 0.1);display:flex;align-items:center;justify-content:center;color:#ef4444;">
                    <span class="material-icons-round" style="font-size:24px;">{IC.DELETE}</span>
                </div>
                <div style="font-size:18px;font-weight:600;color:var(--text-primary);">Delete Company</div>
            </div>
            <div style="font-size:14px;color:var(--text-secondary);margin-bottom:24px;line-height:1.5;">
                Are you sure you want to delete <strong>{name}</strong>?
            </div>
            ''')
            
            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=dialog.close).classes("btn btn-secondary")
                ui.button("Delete", on_click=lambda: [dialog.close(), delete_companies(company_ids, on_success)]).classes("btn").style("background-color: #ef4444 !important; color: white !important;")
    dialog.open()


def open_edit_dialog(row, on_success):
    form = {}

    def content(dialog):
        form["name"] = ui.input("Company Name *", value=row["name"]).props("outlined dense").style("width:100%;margin-bottom:14px;")
        form["address"] = ui.textarea("Address", value=row["_address"]).props("outlined").style("width:100%;margin-bottom:14px;")
        with ui.element("div").classes("grid-cols-2"):
            form["area_manager"] = ui.input("Area Manager", value=row["_area_manager"]).props("outlined dense").style("width:100%;margin-bottom:14px;")
            form["store_supervisor"] = ui.input("Store Supervisor", value=row["_store_supervisor"]).props("outlined dense").style("width:100%;margin-bottom:14px;")
        with ui.element("div").classes("grid-cols-3"):
            form["grace"] = ui.number("Grace Period (min)", value=row["_grace"], min=0, max=60).props("outlined dense")
            form["start"] = ui.input("Work Start", value=row["_start"]).props("outlined dense")
            form["end"]   = ui.input("Work End",   value=row["_end"]).props("outlined dense")

    def on_submit(dialog):
        db = SessionLocal()
        try:
            co = db.query(Company).filter(Company.id == row["id"]).first()
            co.name = form["name"].value.strip()
            co.address = form["address"].value.strip() or None
            co.grace_period = int(form["grace"].value or 10)
            co.work_start = form["start"].value.strip() or "08:00"
            co.work_end = form["end"].value.strip() or "17:00"
            co.area_manager = form["area_manager"].value.strip() or None
            co.store_supervisor = form["store_supervisor"].value.strip() or None
            
            db.commit()
            toast_success("Company Updated", co.name)
            dialog.close()
            on_success()
        except Exception as e:
            db.rollback()
            toast_error("Error", str(e))
        finally:
            db.close()

    form_dialog("Edit Company", content, on_submit, "Update Company", width="520px")


def open_add_dialog(on_success):
    form = {}

    def content(dialog):
        form["name"] = ui.input("Company Name *").props("outlined dense").style("width:100%;margin-bottom:14px;")
        form["address"] = ui.textarea("Address").props("outlined").style("width:100%;margin-bottom:14px;")
        with ui.element("div").classes("grid-cols-2"):
            form["area_manager"] = ui.input("Area Manager").props("outlined dense").style("width:100%;margin-bottom:14px;")
            form["store_supervisor"] = ui.input("Store Supervisor").props("outlined dense").style("width:100%;margin-bottom:14px;")
        with ui.element("div").classes("grid-cols-3"):
            form["grace"] = ui.number("Grace Period (min)", value=10, min=0, max=60).props("outlined dense")
            form["start"] = ui.input("Work Start", value="08:00").props("outlined dense")
            form["end"]   = ui.input("Work End",   value="17:00").props("outlined dense")

    def on_submit(dialog):
        db = SessionLocal()
        try:
            co = Company(
                name=form["name"].value.strip(),
                address=form["address"].value.strip() or None,
                grace_period=int(form["grace"].value or 10),
                work_start=form["start"].value.strip() or "08:00",
                work_end=form["end"].value.strip() or "17:00",
                area_manager=form["area_manager"].value.strip() or None,
                store_supervisor=form["store_supervisor"].value.strip() or None,
            )
            db.add(co)
            db.commit()
            toast_success("Company Added", co.name)
            dialog.close()
            on_success()
        except Exception as e:
            db.rollback()
            toast_error("Error", str(e))
        finally:
            db.close()

    form_dialog("Add Company", content, on_submit, "Save Company", width="520px")


def companies_page():

    @ui.refreshable
    def history_container():
        rows = _get_companies()
        
        selected_rows = set()
        checkboxes = []

        def handle_success():
            history_container.refresh()

        def toggle_row(rid, checked):
            if checked: selected_rows.add(rid)
            else: selected_rows.discard(rid)
            update_bulk_actions()

        def toggle_all(e):
            if e.value:
                selected_rows.update(r["id"] for r in rows)
            else:
                selected_rows.clear()
            for cb in checkboxes:
                cb.set_value(e.value)
            update_bulk_actions()

        def trigger_bulk_delete():
            if not selected_rows: return
            confirm_delete_company(list(selected_rows), f"{len(selected_rows)} selected companies", handle_success)

        with ui.element("div").classes("page-header").style("display:flex;align-items:center;justify-content:space-between;"):
            with ui.element("div"):
                ui.html('<h1 class="page-title">Companies</h1>')
                ui.html('<p class="page-subtitle">Manage company profiles, work schedules, and grace periods</p>')
            with ui.element("button").classes("btn btn-primary").on("click", lambda: open_add_dialog(handle_success)):
                ui.html(f'<span class="material-icons-round" style="font-size:16px;">{IC.ADD}</span> Add Company')

        with ui.element("div").classes("card"):
            with ui.element("div").classes("card-header").style("display: flex; justify-content: space-between; align-items: center; min-height: 56px;"):
                ui.html(f'<span class="card-title">Company List</span>')
                
                bulk_actions = ui.element("div").style("display: none;")
                with bulk_actions:
                    bulk_btn = ui.button("Delete Selected", icon=IC.DELETE, on_click=trigger_bulk_delete)
                    bulk_btn.props("size=sm").style("background-color: #ef4444 !important; color: white !important;")

            def update_bulk_actions():
                if len(selected_rows) > 0:
                    bulk_actions.style("display: block;")
                    bulk_btn.set_text(f"Delete Selected ({len(selected_rows)})")
                else:
                    bulk_actions.style("display: none;")

            with ui.element("div").classes("card-body").style("padding: 0; overflow-x: auto;"):
                if not rows:
                    ui.html('''
                    <div class="empty-state">
                      <span class="material-icons-round">business</span>
                      <div class="empty-state-title">No companies found</div>
                      <div class="empty-state-subtitle">Add your first company to get started.</div>
                    </div>
                    ''')
                else:
                    with ui.element("table").classes("data-table").style("min-width: 800px;"):
                        with ui.element("thead"):
                            with ui.element("tr"):
                                with ui.element("th").style("width: 48px; text-align: center;"):
                                    ui.checkbox(on_change=toggle_all)
                                
                                headers = [
                                    ("business", "Company Name"),
                                    ("groups", "Employees"),
                                    ("schedule", "Grace Period"),
                                    ("access_time", "Work Hours"),
                                    ("place", "Address"),
                                    ("settings", "Actions")
                                ]
                                for icon, col in headers:
                                    with ui.element("th"):
                                        ui.html(f'<div style="display:flex;align-items:center;gap:6px;"><span class="material-icons-round" style="font-size:16px;">{icon}</span> {col}</div>')
                        
                        with ui.element("tbody"):
                            for r in rows:
                                with ui.element("tr"):
                                    with ui.element("td").style("text-align: center;"):
                                        cb = ui.checkbox(on_change=lambda ev, rid=r["id"]: toggle_row(rid, ev.value))
                                        checkboxes.append(cb)
                                    with ui.element("td"):
                                        ui.html(f"<strong>{r['name']}</strong>")
                                    with ui.element("td"):
                                        ui.html(f"{r['employees']}")
                                    with ui.element("td"):
                                        ui.html(f"{r['grace_period']}")
                                    with ui.element("td"):
                                        ui.html(f"{r['work_hours']}")
                                    with ui.element("td"):
                                        ui.html(f"{r['address']}")
                                    with ui.element("td"):
                                        with ui.element("div").style("display:flex; gap: 8px; align-items: center;"):
                                            ui.button(
                                                icon=IC.EDIT, 
                                                on_click=lambda r=r: open_edit_dialog(r, handle_success)
                                            ).props('flat round size=sm color="primary"').tooltip("Edit Company")
                                            ui.button(
                                                icon=IC.DELETE, 
                                                on_click=lambda r=r: confirm_delete_company([r["id"]], r["name"], handle_success)
                                            ).props('flat round size=sm color="negative"').style("color: #ef4444 !important;").tooltip("Delete Company")

    with app_layout("Companies", "/companies", ["Management", "Companies"]):
        history_container()
