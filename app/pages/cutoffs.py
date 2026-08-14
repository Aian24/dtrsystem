from nicegui import ui
from datetime import datetime, date
import calendar
from sqlalchemy.orm import Session
from app.pages.layout import app_layout
from app.components.modals import form_dialog, confirm_dialog
from app.components.notifications import toast_success, toast_error
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import CutoffPeriod, Company

def _get_companies():
    db = SessionLocal()
    try:
        return db.query(Company).filter(Company.is_active == True).all()
    finally:
        db.close()

def _get_cutoffs():
    db = SessionLocal()
    try:
        cutoffs = db.query(CutoffPeriod).join(Company).order_by(Company.name, CutoffPeriod.id).all()
        return [
            {
                "id": c.id,
                "label": c.label,
                "company": c.company.name,
                "start_day": c.start_day,
                "end_day": c.end_day,
                "company_id": c.company_id,
            }
            for c in cutoffs
        ]
    finally:
        db.close()

def delete_cutoffs(cutoff_ids: list[int], on_success=None):
    db: Session = SessionLocal()
    try:
        db.query(CutoffPeriod).filter(CutoffPeriod.id.in_(cutoff_ids)).delete(synchronize_session=False)
        db.commit()
        toast_success("Cutoffs Deleted", f"{len(cutoff_ids)} cutoff(s) deleted.")
        if on_success:
            on_success()
    except Exception as e:
        db.rollback()
        toast_error("Deletion Failed", str(e))
    finally:
        db.close()

def confirm_delete_cutoff(cutoff_ids: list[int], name: str, on_success=None):
    with ui.dialog().classes('backdrop-blur-sm') as dialog:
        dialog.props('persistent')
        with ui.card().style("width: 450px; max-width: 90vw; padding: 24px; border-radius: 16px;"):
            ui.html(f'''
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:40px;height:40px;border-radius:50%;background:rgba(239, 68, 68, 0.1);display:flex;align-items:center;justify-content:center;color:#ef4444;">
                    <span class="material-icons-round" style="font-size:24px;">{IC.DELETE}</span>
                </div>
                <div style="font-size:18px;font-weight:600;color:var(--text-primary);">Delete Cutoff(s)</div>
            </div>
            <div style="font-size:14px;color:var(--text-secondary);margin-bottom:24px;line-height:1.5;">
                Are you sure you want to delete <strong>{name}</strong>?
            </div>
            ''')
            
            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=dialog.close).classes("btn btn-secondary")
                ui.button("Delete", on_click=lambda: [dialog.close(), delete_cutoffs(cutoff_ids, on_success)]).classes("btn").style("background-color: #ef4444 !important; color: white !important;")
    dialog.open()

def open_edit_dialog(row, on_success):
    companies = _get_companies()
    form = {}

    def content(dialog):
        form["company"] = ui.select({c.id: c.name for c in companies}, value=row["company_id"], label="Company *").props("outlined dense").style("width:100%;margin-bottom:14px;")
        form["label"] = ui.input("Label *", value=row["label"]).props("outlined dense").style("width:100%;margin-bottom:8px;")
        with ui.element("div").classes("grid-cols-2"):
            form["start"] = ui.number("Start Day *", value=row["start_day"], min=1, max=31).props('outlined dense').style("width:100%;")
            form["end"] = ui.number("End Day *", value=row["end_day"], min=1, max=31).props('outlined dense').style("width:100%;")

    def on_submit(dialog):
        db = SessionLocal()
        try:
            c = db.query(CutoffPeriod).filter(CutoffPeriod.id == row["id"]).first()
            c.company_id = form["company"].value
            c.label = form["label"].value.strip()
            c.start_day = int(form["start"].value)
            c.end_day = int(form["end"].value)
            
            db.commit()
            toast_success("Cutoff Updated", f"Cutoff {c.label} updated.")
            dialog.close()
            on_success()
        except Exception as e:
            db.rollback()
            toast_error("Error", str(e))
        finally:
            db.close()

    form_dialog("Edit Cutoff", content, on_submit, "Update Cutoff")


def cutoffs_page():
    table_state = {"search": "", "page": 1, "limit": 10}
    
    @ui.refreshable
    def history_container():
        cutoffs = _get_cutoffs()
        
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
                selected_rows.update(r["id"] for r in cutoffs)
            else:
                selected_rows.clear()
            for cb in checkboxes:
                cb.set_value(e.value)
            update_bulk_actions()

        def trigger_bulk_delete():
            if not selected_rows: return
            confirm_delete_cutoff(list(selected_rows), f"{len(selected_rows)} selected cutoffs", handle_success)

        def open_add_dialog():
            companies = _get_companies()
            form = {}

            def content(dialog):
                ui.html('<div style="font-size:13px; color:var(--text-secondary); margin-bottom: 16px; line-height: 1.5;">Configure generic cutoff rules for this company. Use <b>31</b> as the End Day to represent the End of the Month.</div>')
                form["company"] = ui.select({c.id: c.name for c in companies}, label="Company *").props("outlined dense").style("width:100%;margin-bottom:14px;")
                
                ui.html('<div style="font-weight: 600; margin-bottom: 8px; color: var(--text-primary);">Period 1 (e.g. 1st-15th)</div>')
                form["label1"] = ui.input("Label *", placeholder="1st to 15th").props("outlined dense").style("width:100%;margin-bottom:8px;")
                with ui.element("div").classes("grid-cols-2").style("margin-bottom: 16px;"):
                    form["start1"] = ui.number("Start Day *", value=1, min=1, max=31).props('outlined dense').style("width:100%;")
                    form["end1"] = ui.number("End Day *", value=15, min=1, max=31).props('outlined dense').style("width:100%;")

                ui.html('<div style="font-weight: 600; margin-bottom: 8px; color: var(--text-primary);">Period 2 (e.g. 16th-EoM)</div>')
                form["label2"] = ui.input("Label *", placeholder="16th to EoM").props("outlined dense").style("width:100%;margin-bottom:8px;")
                with ui.element("div").classes("grid-cols-2"):
                    form["start2"] = ui.number("Start Day *", value=16, min=1, max=31).props('outlined dense').style("width:100%;")
                    form["end2"] = ui.number("End Day *", value=31, min=1, max=31).props('outlined dense').style("width:100%;")

            def on_submit(dialog):
                db = SessionLocal()
                try:
                    if not form["company"].value: raise ValueError("Please select a company.")
                    if not form["label1"].value.strip() or not form["label2"].value.strip():
                        raise ValueError("Please provide labels for both periods.")
                    if not form["start1"].value or not form["end1"].value or not form["start2"].value or not form["end2"].value:
                        raise ValueError("Please provide all start and end days.")

                    c1 = CutoffPeriod(
                        company_id=form["company"].value,
                        label=form["label1"].value.strip(),
                        start_day=int(form["start1"].value),
                        end_day=int(form["end1"].value)
                    )
                    c2 = CutoffPeriod(
                        company_id=form["company"].value,
                        label=form["label2"].value.strip(),
                        start_day=int(form["start2"].value),
                        end_day=int(form["end2"].value)
                    )
                    
                    db.add(c1)
                    db.add(c2)
                    db.commit()
                    toast_success("Cutoffs Configured", f"Successfully saved rules for {c1.label} and {c2.label}")
                    dialog.close()
                    handle_success()
                except Exception as e:
                    db.rollback()
                    toast_error("Error", str(e))
                finally:
                    db.close()

            form_dialog("Configure Company Cutoffs", content, on_submit, "Save Cutoffs")

        with ui.element("div").classes("page-header").style("display:flex;align-items:center;justify-content:space-between;"):
            with ui.element("div"):
                ui.html('<h1 class="page-title">Cutoff Rules</h1>')
                ui.html('<p class="page-subtitle">Configure generic day ranges for each company</p>')
            with ui.element("button").classes("btn btn-primary").on("click", open_add_dialog):
                ui.html(f'<span class="material-icons-round" style="font-size:16px;">{IC.ADD}</span> Add Cutoffs')

        with ui.element("div").classes("card"):
            with ui.element("div").classes("card-header").style("display: flex; justify-content: space-between; align-items: center; min-height: 56px;"):
                ui.html(f'<span class="card-title">Cutoff List</span>')
                
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
                import math
                term = table_state["search"].lower()
                filtered_cutoffs = [c for c in cutoffs if term in c['company'].lower() or term in c['label'].lower()] if term else cutoffs
                
                total_items = len(filtered_cutoffs)
                total_pages = math.ceil(total_items / table_state["limit"]) or 1
                if table_state["page"] > total_pages:
                    table_state["page"] = total_pages
                    
                start_idx = (table_state["page"] - 1) * table_state["limit"]
                end_idx = start_idx + table_state["limit"]
                paged_cutoffs = filtered_cutoffs[start_idx:end_idx]

                with ui.element("div").style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); gap: 16px; flex-wrap: wrap;"):
                    with ui.element("div").style("display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted);"):
                        ui.html("<span>Show</span>")
                        def update_limit(e):
                            table_state["limit"] = e.value
                            table_state["page"] = 1
                            history_container.refresh()
                        ui.select(options=[10, 25, 50, 100], value=table_state["limit"], on_change=update_limit).props('dense outlined').style("width: 70px;")
                        ui.html("<span>entries</span>")
                        
                    with ui.element("div"):
                        def update_search(e):
                            table_state["search"] = e.value
                            table_state["page"] = 1
                            history_container.refresh()
                        ui.input(placeholder="Search...", value=table_state["search"], on_change=update_search).props('dense outlined clearable').style("width: 250px;")

                if not filtered_cutoffs:
                    ui.html('''
                    <div class="empty-state">
                      <span class="material-icons-round">date_range</span>
                      <div class="empty-state-title">No cutoffs found</div>
                      <div class="empty-state-subtitle">Configure your first cutoff rules to get started.</div>
                    </div>
                    ''')
                else:
                    with ui.element("table").classes("data-table").style("min-width: 800px;"):
                        with ui.element("thead"):
                            with ui.element("tr"):
                                with ui.element("th").style("width: 48px; text-align: center;"):
                                    ui.checkbox(on_change=toggle_all)
                                for col in ["Company", "Label", "Start Day", "End Day", "Actions"]:
                                    with ui.element("th").style("text-align:left;"):
                                        ui.html(col)
                        with ui.element("tbody"):
                            for c in paged_cutoffs:
                                with ui.element("tr"):
                                    with ui.element("td").style("text-align: center;"):
                                        cb = ui.checkbox(on_change=lambda ev, rid=c["id"]: toggle_row(rid, ev.value))
                                        checkboxes.append(cb)
                                    with ui.element("td"):
                                        ui.html(c["company"])
                                    with ui.element("td"):
                                        ui.html(f'<strong>{c["label"]}</strong>')
                                    with ui.element("td"):
                                        ui.html(f'Day {c["start_day"]}')
                                    with ui.element("td"):
                                        ed = "EoM" if c["end_day"] == 31 else f'Day {c["end_day"]}'
                                        ui.html(ed)
                                    with ui.element("td"):
                                        with ui.element("div").style("display:flex; gap: 8px; align-items: center;"):
                                            ui.button(
                                                icon=IC.EDIT, 
                                                on_click=lambda c=c: open_edit_dialog(c, handle_success)
                                            ).props('flat round size=sm color="primary"').tooltip("Edit Cutoff")
                                            ui.button(
                                                icon=IC.DELETE, 
                                                on_click=lambda c=c: confirm_delete_cutoff([c["id"]], c["label"], handle_success)
                                            ).props('flat round size=sm color="negative"').style("color: #ef4444 !important;").tooltip("Delete Cutoff")

                with ui.element("div").style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); flex-wrap: wrap; gap: 16px;"):
                    showing_start = start_idx + 1 if total_items > 0 else 0
                    showing_end = min(end_idx, total_items)
                    ui.html(f'<span style="font-size: 13px; color: var(--text-muted);">Showing {showing_start} to {showing_end} of {total_items} entries</span>')
                    
                    def update_page(e):
                        table_state["page"] = e.value
                        history_container.refresh()
                        
                    ui.pagination(1, total_pages, value=table_state["page"], on_change=update_page).props('color="primary" outline active-color="primary" active-text-color="white"')


    with app_layout("Cutoffs", "/cutoffs", ["Management", "Cutoff Rules"]):
        history_container()
