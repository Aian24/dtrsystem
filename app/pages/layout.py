"""
Shared page layout helper — wraps content with sidebar + navbar
"""
from nicegui import ui
from app.components.sidebar import sidebar
from app.components.navbar import navbar
from contextlib import contextmanager


@contextmanager
def app_layout(title: str, current_path: str, breadcrumbs: list[str] | None = None):
    """
    Context manager that renders the sidebar + navbar, then yields the page area
    for the caller to fill with content.

    Usage:
        with app_layout("Dashboard", "/dashboard", ["Dashboard"]):
            ui.html("<h1>Hello</h1>")
    """
    from app.theme.styles import FONT_LINK, GLOBAL_CSS, GLOBAL_JS
    ui.html(f"{FONT_LINK}<style>{GLOBAL_CSS}</style>").classes("hidden")
    ui.add_body_html(f"<script>{GLOBAL_JS}</script>")

    sidebar(current_path=current_path)
    navbar(title=title, breadcrumbs=breadcrumbs or [title])

    # Remove NiceGUI's default max-width and force full width
    ui.query('.nicegui-content').classes(remove='max-w-[1200px]', add='max-w-full w-full')

    with ui.element("div").classes("page-area w-full max-w-full"):
        with ui.element("div").classes("page-fade-in w-full max-w-full"):
            yield
