"""
Top Navigation Bar Component
"""
from nicegui import ui
from app.theme.icons import IC


def navbar(title: str, breadcrumbs: list[str] | None = None):
    """
    Render the sticky top navigation bar.
    breadcrumbs: list of strings, e.g. ['Dashboard', 'Upload Logs']
    """
    with ui.header(elevated=False).classes("topbar bg-surface text-primary"):

        # ── Breadcrumb ────────────────────────────────────────────────────────
        with ui.element("div").classes("topbar-breadcrumb"):
            crumbs = breadcrumbs or [title]
            for i, crumb in enumerate(crumbs):
                if i > 0:
                    ui.html('<span class="material-icons-round" style="font-size:14px;opacity:.4;">chevron_right</span>')
                is_last = i == len(crumbs) - 1
                cls = "crumb-active" if is_last else ""
                ui.html(f'<span class="{cls}">{crumb}</span>')

        # ── Right Actions ─────────────────────────────────────────────────────
        with ui.element("div").classes("topbar-actions"):
            # Clock
            ui.html('<div class="clock-display" id="topbar-clock">--:--:--</div>')

            # Dark mode toggle
            with ui.element("button").classes("icon-btn").props(
                'title="Toggle dark mode" onclick="DTR.toggleDarkMode()"'
            ):
                ui.html(f'<span class="material-icons-round">{IC.MOON}</span>')
                


    # Start the clock
    ui.run_javascript("DTR.startClock(document.getElementById('topbar-clock'));")
