"""
Searchable, Sortable, Paginated Data Table Component
"""
from __future__ import annotations
from nicegui import ui
from typing import Any, Callable
from app.components.search_select import search_select


def data_table(
    columns: list[dict],
    rows: list[dict],
    row_key: str = "id",
    page_size: int = 20,
    searchable: bool = True,
    filters: list[dict] | None = None,
    on_row_click: Callable | None = None,
    empty_icon: str = "table_rows",
    empty_message: str = "No records found",
):
    """
    columns: [{"key": "name", "label": "Full Name", "sortable": True}, ...]
    rows:    [{"id": 1, "name": "Dela Cruz, Juan"}, ...]
    filters: [{"key": "status", "label": "Status", "options": {"all": "All Statuses", "active": "Active"}}, ...]
    """
    state = {
        "page":       1,
        "sort_key":   None,
        "sort_asc":   True,
        "search":     "",
        "filter_vals": {f["key"]: list(f["options"].keys())[0] if f.get("options") else "" for f in (filters or [])},
        "filtered":   rows[:],
        "page_size":  page_size,
    }

    container = ui.element("div").classes("card")

    def get_filtered():
        q = state["search"].lower().strip()
        data = rows
        if q:
            data = [
                r for r in data
                if any(q in str(v).lower() for v in r.values())
            ]
        # Apply dropdown filters
        if filters:
            for flt in filters:
                fkey = flt["key"]
                sel_val = state["filter_vals"].get(fkey)
                if sel_val and str(sel_val).lower() not in ("all", "0", ""):
                    custom_fn = flt.get("filter_fn")
                    if custom_fn:
                        data = [r for r in data if custom_fn(r, sel_val)]
                    else:
                        data = [r for r in data if str(r.get(fkey, "")).lower() == str(sel_val).lower()]

        sk = state["sort_key"]
        if sk:
            data = sorted(data, key=lambda r: str(r.get(sk, "")), reverse=not state["sort_asc"])
        state["filtered"] = data
        return data

    def render():
        container.clear()
        filtered = get_filtered()
        total = len(filtered)
        total_pages = max(1, (total + state["page_size"] - 1) // state["page_size"])
        state["page"] = min(state["page"], total_pages)
        page_start = (state["page"] - 1) * state["page_size"]
        page_rows = filtered[page_start: page_start + state["page_size"]]

        with container:
            # ── Toolbar / Filter bar ──────────────────────────────────────────
            if searchable or filters:
                with ui.element("div").style(
                    "padding:12px 18px;border-bottom:1px solid var(--border);"
                    "display:flex;align-items:center;gap:12px;flex-wrap:wrap;"
                ):
                    if searchable:
                        with ui.element("div").style("display:flex;align-items:center;gap:6px;flex:1;min-width:200px;"):
                            ui.html('<span class="material-icons-round" style="color:var(--text-muted);font-size:18px;">search</span>')
                            search_input = ui.input(placeholder="Search…").props(
                                'outlined dense clearable style="flex:1;background:transparent;"'
                            ).style("flex:1;")
                            search_input.value = state["search"]

                            def on_search(e):
                                val = e.value if hasattr(e, 'value') else (search_input.value or "")
                                state["search"] = val or ""
                                state["page"] = 1
                                render()

                            search_input.on_value_change(on_search)

                    if filters:
                        for flt in filters:
                            fkey = flt["key"]
                            flbl = flt.get("label", fkey.title())
                            fopts = flt.get("options", {})
                            cur_val = state["filter_vals"].get(fkey, list(fopts.keys())[0] if fopts else "")
                            
                            def make_filter_change(key):
                                def on_flt_change(e):
                                    val = e.value if hasattr(e, 'value') else e
                                    state["filter_vals"][key] = val
                                    state["page"] = 1
                                    render()
                                return on_flt_change

                            fsel = search_select(
                                options=fopts,
                                value=cur_val,
                                label=flbl,
                            ).props('outlined dense options-dense no-wrap').style("min-width:150px;")
                            fsel.on_value_change(make_filter_change(fkey))

                        # Reset button
                        def on_reset():
                            state["search"] = ""
                            state["filter_vals"] = {f["key"]: list(f["options"].keys())[0] if f.get("options") else "" for f in (filters or [])}
                            state["page"] = 1
                            render()

                        ui.button("Reset", icon="filter_alt_off", on_click=on_reset).classes("btn btn-reset btn-sm").tooltip("Clear filters")

            # ── Table ───────────────────────────────────────────────────────
            with ui.element("div").classes("data-table-wrapper").style(
                "border:none;border-radius:0;"
            ):
                if not page_rows:
                    with ui.element("div").classes("empty-state"):
                        ui.html(f'<span class="material-icons-round">{empty_icon}</span>')
                        ui.html(f'<div class="empty-state-title">{empty_message}</div>')
                        if state["search"] or any(str(v).lower() not in ("all", "0", "") for v in state["filter_vals"].values()):
                            ui.html(f'<div class="empty-state-desc">Try adjusting your search or filters</div>')
                else:
                    with ui.element("table").classes("data-table"):
                        # Head
                        with ui.element("thead"):
                            with ui.element("tr"):
                                for col in columns:
                                    lbl = col.get("label", col["key"].title())
                                    sortable = col.get("sortable", True)
                                    active = state["sort_key"] == col["key"]
                                    sort_icon_html = ""
                                    if sortable and active:
                                        m_icon = "arrow_upward" if state["sort_asc"] else "arrow_downward"
                                        sort_icon_html = f'<span class="material-icons-round" style="font-size:14px;vertical-align:middle;margin-left:4px;color:var(--color-primary);">{m_icon}</span>'

                                    def make_sort_handler(key):
                                        def handler():
                                            if state["sort_key"] == key:
                                                state["sort_asc"] = not state["sort_asc"]
                                            else:
                                                state["sort_key"] = key
                                                state["sort_asc"] = True
                                            render()
                                        return handler

                                    th = ui.element("th").on("click", make_sort_handler(col["key"]) if sortable else None)
                                    with th:
                                        ui.html(f'{lbl}{sort_icon_html}')

                        # Body
                        with ui.element("tbody"):
                            for i, row in enumerate(page_rows):
                                delay = i * 30
                                tr = ui.element("tr").style(f"animation-delay:{delay}ms")
                                if on_row_click:
                                    tr.on("click", lambda e, r=row: on_row_click(r))
                                    tr.style("cursor:pointer")
                                with tr:
                                    for col in columns:
                                        val = row.get(col["key"], "")
                                        render_fn = col.get("render")
                                        with ui.element("td"):
                                            if render_fn:
                                                ui.html(render_fn(val, row))
                                            else:
                                                ui.html(f"<span>{val}</span>")

            # ── Pagination ───────────────────────────────────────────────────
            if total_pages > 1 or total > 0:
                with ui.element("div").classes("pagination").style("justify-content:space-between;"):
                    # Info
                    start = page_start + 1
                    end = min(page_start + state["page_size"], total)
                    ui.html(f'<span style="font-size:12.5px;color:var(--text-muted);">Showing {start}–{end} of {total:,}</span>')

                    # Page buttons
                    with ui.element("div").style("display:flex;gap:4px;"):
                        # Prev
                        prev_btn = ui.element("button").classes("page-btn").on(
                            "click", lambda: (_set(state, "page", state["page"] - 1), render())
                        )
                        if state["page"] <= 1:
                            prev_btn.props("disabled")
                        with prev_btn:
                            ui.html('<span class="material-icons-round" style="font-size:14px;">chevron_left</span>')

                        # Page numbers (show up to 5)
                        p = state["page"]
                        pages_to_show = sorted(set([
                            1, total_pages,
                            *range(max(1, p-1), min(total_pages+1, p+2))
                        ]))
                        prev_p = None
                        for pg in pages_to_show:
                            if prev_p and pg - prev_p > 1:
                                ui.html('<span class="page-btn" style="border:none;cursor:default;">…</span>')
                            active_cls = "active" if pg == p else ""
                            btn = ui.element("button").classes(f"page-btn {active_cls}").on(
                                "click", lambda e, x=pg: (_set(state, "page", x), render())
                            )
                            with btn:
                                ui.html(str(pg))
                            prev_p = pg

                        # Next
                        next_btn = ui.element("button").classes("page-btn").on(
                            "click", lambda: (_set(state, "page", state["page"] + 1), render())
                        )
                        if state["page"] >= total_pages:
                            next_btn.props("disabled")
                        with next_btn:
                            ui.html('<span class="material-icons-round" style="font-size:14px;">chevron_right</span>')

    def _set(d, k, v):
        d[k] = v

    render()
    return container
