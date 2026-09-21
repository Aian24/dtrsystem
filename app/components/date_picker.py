"""
Modern Date Picker Component — NiceGUI & Quasar modern popup calendar
"""
from __future__ import annotations
from typing import Any, Callable, Optional
from nicegui import ui


def modern_date_picker(
    label: Optional[str] = None,
    value: Optional[str] = None,
    placeholder: str = "YYYY-MM-DD",
    on_change: Optional[Callable[..., Any]] = None,
    clearable: bool = True,
) -> ui.input:
    """
    Renders an outlined, dense date input with a modern Quasar calendar popup (<q-date>).
    Clicking anywhere on the input box or the calendar icon immediately opens the popup.
    """
    inp = ui.input(
        label=label,
        value=value,
        placeholder=placeholder
    ).props("outlined dense" + (" clearable" if clearable else ""))

    with inp:
        with inp.add_slot("append"):
            ui.icon("calendar_month").classes("cursor-pointer text-primary").style("font-size: 19px; margin-left: 2px;")

        with ui.menu() as menu:
            with ui.card().classes('p-0').style("border-radius: 14px; overflow: hidden; box-shadow: 0 16px 36px -4px rgba(15,23,42,0.18); border: 1px solid var(--border);"):
                def on_date_selected(e):
                    inp.value = e.value
                    if on_change:
                        on_change(e.value)
                    menu.close()

                d = ui.date(value=value or None, on_change=on_date_selected).props('minimal today-btn color="primary"')
                d.bind_value(inp)

    return inp
