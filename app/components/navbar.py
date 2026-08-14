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
                
            # User Avatar
            from app.services.auth_service import get_current_user
            from app.core.database import SessionLocal
            from app.core.models import User
            
            c_user = get_current_user()
            if c_user:
                db_nav = SessionLocal()
                try:
                    db_u = db_nav.query(User).get(c_user.get('user_id'))
                    if db_u and db_u.avatar_base64:
                        ui.html(f'''
                        <div style="width:32px;height:32px;border-radius:50%;overflow:hidden;margin-left:8px;box-shadow:0 2px 5px rgba(0,0,0,.1);">
                          <img src="data:image/png;base64,{db_u.avatar_base64}" style="width:100%;height:100%;object-fit:cover;" />
                        </div>
                        ''')
                    else:
                        initial = db_u.username[0].upper() if db_u else "A"
                        ui.html(f'''
                        <div style="width:32px;height:32px;border-radius:50%;margin-left:8px;
                                    background:linear-gradient(135deg,#2563EB,#6366F1);
                                    display:flex;align-items:center;justify-content:center;
                                    font-weight:700;color:#fff;font-size:14px;box-shadow:0 2px 5px rgba(37,99,235,.2);">
                          {initial}
                        </div>
                        ''')
                finally:
                    db_nav.close()

    # Start the clock
    ui.run_javascript("DTR.startClock(document.getElementById('topbar-clock'));")
