from __future__ import annotations
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
from app.components.search_select import search_select

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
                ui.button("Delete", on_click=lambda: [dialog.close(), delete_cutoffs(cutoff_ids, on_success)]).classes("btn btn-danger")
    dialog.open()

def open_edit_dialog(row, on_success):
    companies = _get_companies()
    form = {}

    def content(dialog):
        form["company"] = search_select(
            {c.id: c.name for c in companies}, value=row["company_id"], label="Company *"
        ).props("outlined dense options-dense").style("width:100%;margin-bottom:14px;")
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
    table_state = {
        "search": "",
        "company": 0,
        "period_type": "all",
        "page": 1,
        "limit": 10
    }
    
    @ui.refreshable
    def history_container():
        cutoffs = _get_cutoffs()
        companies = _get_companies()
        company_options = {0: "— All Companies —", **{c.id: c.name for c in companies}}
        period_options = {
            "all": "— All Periods —",
            "1-15": "1st Period (1st – 15th)",
            "16-eom": "2nd Period (16th – EoM)",
            "custom": "Custom Ranges"
        }
        
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
            form = {}

            def content(dialog):
                ui.html('<div style="font-size:13px; color:var(--text-secondary); margin-bottom: 16px; line-height: 1.5;">Configure generic cutoff rules for this company. Use <b>31</b> as the End Day to represent the End of the Month.</div>')
                form["company"] = search_select(
                    {c.id: c.name for c in companies}, label="Company *"
                ).props("outlined dense options-dense").style("width:100%;margin-bottom:14px;")
                
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
                    bulk_btn = ui.button("Delete Selected", icon=IC.DELETE, on_click=trigger_bulk_delete).classes("btn btn-danger btn-sm")

            def update_bulk_actions():
                if len(selected_rows) > 0:
                    bulk_actions.style("display: block;")
                    bulk_btn.set_text(f"Delete Selected ({len(selected_rows)})")
                else:
                    bulk_actions.style("display: none;")

            # ── Multi-criteria Filter Bar ──────────────────────────────────────────
            with ui.element("div").style(
                "padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; "
                "border-bottom: 1px solid var(--border); gap: 12px; flex-wrap: wrap; background: var(--bg-subtle);"
            ):
                with ui.element("div").style("display: flex; align-items: center; gap: 10px; flex-wrap: wrap; flex: 1;"):
                    # Show entries
                    with ui.element("div").style("display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--text-muted);"):
                        ui.html("<span>Show</span>")
                        def update_limit(e):
                            table_state["limit"] = e.value
                            table_state["page"] = 1
                            table_content.refresh()
                        ui.select(options=[10, 25, 50, 100], value=table_state["limit"], on_change=update_limit).props('dense outlined options-dense').style("width: 75px;")

                    # Company Filter
                    def update_co_filter(e):
                        table_state["company"] = e.value
                        table_state["page"] = 1
                        table_content.refresh()
                    co_filter_sel = search_select(
                        options=company_options,
                        value=table_state["company"],
                        on_change=update_co_filter,
                        label="Company",
                    ).props('dense outlined options-dense').style("min-width: 170px;")

                    # Period Type Filter
                    def update_period_filter(e):
                        table_state["period_type"] = e.value
                        table_state["page"] = 1
                        table_content.refresh()
                    period_filter_sel = search_select(
                        options=period_options,
                        value=table_state["period_type"],
                        on_change=update_period_filter,
                        label="Period Type",
                    ).props('dense outlined options-dense').style("min-width: 170px;")

                with ui.element("div").style("display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"):
                    def update_search(e):
                        val = e.value or ""
                        if table_state["search"] != val:
                            table_state["search"] = val
                            table_state["page"] = 1
                            table_content.refresh()
                    search_inp = ui.input(placeholder="Search cutoffs...", value=table_state["search"], on_change=update_search).props('dense outlined clearable').style("width: 220px;")

                    # Reset filters button
                    def reset_filters():
                        table_state["search"] = ""
                        table_state["company"] = 0
                        table_state["period_type"] = "all"
                        table_state["page"] = 1
                        search_inp.value = ""
                        co_filter_sel.value = 0
                        period_filter_sel.value = "all"
                        table_content.refresh()

                    ui.button("Reset", icon="filter_alt_off", on_click=reset_filters).classes("btn btn-reset btn-sm").tooltip("Clear all filters")

            with ui.element("div").classes("card-body").style("padding: 0; overflow-x: auto;"):
                @ui.refreshable
                def table_content():
                    import math
                    term = table_state["search"].lower().strip()
                    sel_co = table_state["company"]
                    sel_pt = table_state["period_type"]

                    filtered_cutoffs = cutoffs
                    # 1. Search term
                    if term:
                        filtered_cutoffs = [c for c in filtered_cutoffs if term in c['company'].lower() or term in c['label'].lower()]
                    # 2. Company filter
                    if sel_co and sel_co != 0:
                        filtered_cutoffs = [c for c in filtered_cutoffs if c['company_id'] == sel_co]
                    # 3. Period type filter
                    if sel_pt == "1-15":
                        filtered_cutoffs = [c for c in filtered_cutoffs if c['start_day'] == 1 and c['end_day'] == 15]
                    elif sel_pt == "16-eom":
                        filtered_cutoffs = [c for c in filtered_cutoffs if c['start_day'] == 16 and c['end_day'] in (30, 31)]
                    elif sel_pt == "custom":
                        filtered_cutoffs = [c for c in filtered_cutoffs if not ((c['start_day'] == 1 and c['end_day'] == 15) or (c['start_day'] == 16 and c['end_day'] in (30, 31)))]
                
                    total_items = len(filtered_cutoffs)
                    total_pages = math.ceil(total_items / table_state["limit"]) or 1
                    if table_state["page"] > total_pages:
                        table_state["page"] = total_pages
                    
                    start_idx = (table_state["page"] - 1) * table_state["limit"]
                    end_idx = start_idx + table_state["limit"]
                    paged_cutoffs = filtered_cutoffs[start_idx:end_idx]

                    checkboxes.clear()

                    if not filtered_cutoffs:
                        ui.html('''
                        <div class="empty-state">
                          <span class="material-icons-round">date_range</span>
                          <div class="empty-state-title">No cutoffs match your filters</div>
                          <div class="empty-state-subtitle">Try adjusting your search criteria or resetting filters.</div>
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
                                            cb = ui.checkbox(value=c["id"] in selected_rows, on_change=lambda ev, rid=c["id"]: toggle_row(rid, ev.value))
                                            checkboxes.append(cb)
                                        with ui.element("td"):
                                            ui.html(c["company"])
                                        with ui.element("td"):
                                            ui.html(f'<strong>{c["label"]}</strong>')
                                        with ui.element("td"):
                                            ui.html(f'<span class="badge badge-info">Day {c["start_day"]}</span>')
                                        with ui.element("td"):
                                            ed = "End of Month" if c["end_day"] == 31 else f'Day {c["end_day"]}'
                                            ui.html(f'<span class="badge badge-gray">{ed}</span>')
                                        with ui.element("td"):
                                            with ui.element("div").style("display:flex; gap: 8px; align-items: center;"):
                                                ui.button(
                                                    icon=IC.EDIT, 
                                                    on_click=lambda c=c: open_edit_dialog(c, handle_success)
                                                ).classes("action-btn-edit").props('flat round dense').tooltip("Edit Cutoff")
                                                ui.button(
                                                    icon=IC.DELETE, 
                                                    on_click=lambda c=c: confirm_delete_cutoff([c["id"]], c["label"], handle_success)
                                                ).classes("action-btn-delete").props('flat round dense').tooltip("Delete Cutoff")

                    with ui.element("div").style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); flex-wrap: wrap; gap: 16px;"):
                        showing_start = start_idx + 1 if total_items > 0 else 0
                        showing_end = min(end_idx, total_items)
                        filtered_text = f" (filtered from {len(cutoffs)} total)" if total_items != len(cutoffs) else ""
                        ui.html(f'<span style="font-size: 13px; color: var(--text-muted);">Showing {showing_start} to {showing_end} of {total_items} entries{filtered_text}</span>')
                    
                        def update_page(e):
                            table_state["page"] = e.value
                            table_content.refresh()
                        
                        ui.pagination(1, total_pages, value=table_state["page"], on_change=update_page).props('color="primary" outline active-color="primary" active-text-color="white"')
            
            table_content()


    with app_layout("Cutoffs", "/cutoffs", ["Management", "Cutoff Rules"]):
        history_container()
