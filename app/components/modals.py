"""
Modal / Dialog Components — scale-from-center animation
"""
from nicegui import ui
from typing import Callable


def confirm_dialog(
    title: str,
    message: str,
    on_confirm: Callable,
    confirm_label: str = "Confirm",
    confirm_class: str = "btn-danger",
    on_cancel: Callable | None = None,
):
    """
    Show an animated confirmation dialog.
    Returns a dialog object.
    """
    with ui.dialog().props("persistent") as dialog:
        with ui.element("div").classes("modal-box"):
            # Header
            with ui.element("div").classes("modal-header"):
                ui.html(f'<span class="modal-title">{title}</span>')
                with ui.element("button").classes("icon-btn").on("click", dialog.close):
                    ui.html('<span class="material-icons-round">close</span>')

            # Body
            with ui.element("div").classes("modal-body"):
                ui.html(f'<p style="color:var(--text-secondary);font-size:14px;line-height:1.7;">{message}</p>')

            # Footer
            with ui.element("div").classes("modal-footer"):
                with ui.element("button").classes("btn btn-secondary").on("click", lambda: (
                    dialog.close(), on_cancel() if on_cancel else None
                )):
                    ui.html("Cancel")
                with ui.element("button").classes(f"btn {confirm_class}").on(
                    "click", lambda: (dialog.close(), on_confirm())
                ):
                    ui.html(confirm_label)

    dialog.open()
    return dialog


def form_dialog(
    title: str,
    content_fn: Callable,
    on_submit: Callable,
    submit_label: str = "Save",
    width: str = "560px",
):
    """
    Generic form dialog. content_fn(dialog) should render form fields.
    on_submit() is called when submit button is clicked.
    """
    with ui.dialog().props("persistent") as dialog:
        with ui.element("div").classes("modal-box").style(f"max-width:{width}"):
            with ui.element("div").classes("modal-header"):
                ui.html(f'<span class="modal-title">{title}</span>')
                with ui.element("button").classes("icon-btn").on("click", dialog.close):
                    ui.html('<span class="material-icons-round">close</span>')

            with ui.element("div").classes("modal-body"):
                content_fn(dialog)

            with ui.element("div").classes("modal-footer"):
                with ui.element("button").classes("btn btn-secondary").on("click", dialog.close):
                    ui.html("Cancel")
                with ui.element("button").classes("btn btn-primary").on(
                    "click", lambda: on_submit(dialog)
                ):
                    ui.html(f'<span class="material-icons-round" style="font-size:16px;">save</span> {submit_label}')

    dialog.open()
    return dialog


def alert_dialog(
    title: str,
    message: str,
    icon: str = "info",
    icon_color: str = "#2563EB",
):
    """Simple informational dialog."""
    with ui.dialog() as dialog:
        with ui.element("div").classes("modal-box").style("max-width:420px;text-align:center;"):
            with ui.element("div").classes("modal-body").style("padding:32px 24px;"):
                ui.html(f'''
                <div style="width:56px;height:56px;border-radius:50%;
                            background:{icon_color}20;
                            display:flex;align-items:center;justify-content:center;
                            margin:0 auto 16px;">
                  <span class="material-icons-round" style="font-size:30px;color:{icon_color};">{icon}</span>
                </div>
                <div style="font-size:17px;font-weight:700;color:var(--text-primary);margin-bottom:8px;">{title}</div>
                <p style="color:var(--text-secondary);font-size:13.5px;line-height:1.7;">{message}</p>
                ''')
            with ui.element("div").classes("modal-footer").style("justify-content:center;"):
                with ui.element("button").classes("btn btn-primary").on("click", dialog.close):
                    ui.html("OK")

    dialog.open()
    return dialog
