"""
Animated Sidebar Component
"""
from nicegui import ui, app as ngapp
from app.theme.icons import IC

NAV_ITEMS = [
    ("main", [
        (IC.DASHBOARD,  "Dashboard",       "/dashboard"),
        (IC.ATTENDANCE, "DTR Lookup",      "/lookup"),
        (IC.UPLOAD,     "Upload Logs",     "/upload"),
        (IC.REPORTS,    "Manage Logs",     "/manage-logs"),
    ]),
    ("management", [
        (IC.EMPLOYEES,  "Employees",       "/employees"),
        (IC.COMPANIES,  "Companies",       "/companies"),
        (IC.CALENDAR,   "Cutoff Periods",  "/cutoffs"),
    ]),
    ("analytics", [
        (IC.REPORTS,    "Reports",         "/reports"),
    ]),
    ("system", [
        (IC.SETTINGS,   "Settings",        "/settings"),
    ]),
]

SECTION_LABELS = {
    "main":       "Main",
    "management": "Management",
    "analytics":  "Analytics",
    "system":     "System",
}


def sidebar(current_path: str = "/dashboard"):
    """Render the sidebar using NiceGUI's native left_drawer."""
    with ui.left_drawer(value=True).props('bordered :width="260"').classes("q-pa-none bg-surface"):
        # ── Logo ─────────────────────────────────────────────────────────────
        from app.services.settings_service import get_app_config
        cfg = get_app_config()
        
        with ui.element("div").classes("sidebar-logo"):
            if cfg['app_logo']:
                with ui.element("div").classes("sidebar-logo-icon").style("padding:0;background:transparent;box-shadow:none;"):
                    ui.html(f'<img src="data:image/png;base64,{cfg["app_logo"]}" style="width:24px;height:24px;object-fit:contain;border-radius:6px;" />')
            else:
                with ui.element("div").classes("sidebar-logo-icon"):
                    ui.html('<span class="material-icons-round" style="color:#fff;font-size:20px;">schedule</span>')
            
            ui.html(f'<span class="sidebar-logo-text" style="font-size:15px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{cfg["app_name"]}">{cfg["app_name"]}</span>')

        # ── Navigation ───────────────────────────────────────────────────────
        with ui.element("div").classes("sidebar-nav"):
            for section_key, items in NAV_ITEMS:
                label = SECTION_LABELS.get(section_key, section_key.title())
                ui.html(f'<div class="nav-section-label">{label}</div>')

                for icon, nav_label, route in items:
                    is_active = current_path == route
                    active_cls = "active" if is_active else ""

                    with ui.element("a").props(f'href="{route}"').classes(f"nav-item {active_cls}"):
                        ui.html(f'<span class="material-icons-round">{icon}</span>')
                        ui.html(f'<span class="nav-label">{nav_label}</span>')

        # ── Footer ────────────────────────────────────────────────────────────
        with ui.element("div").classes("sidebar-footer"):
            from app.services.auth_service import get_current_user
            from app.core.database import SessionLocal
            from app.core.models import User
            
            c_user = get_current_user()
            if c_user:
                db_sb = SessionLocal()
                try:
                    db_u = db_sb.query(User).get(c_user.get('user_id'))
                    user_name = db_u.full_name or db_u.username if db_u else "Admin"
                    user_role = db_u.role.title() if db_u else "User"
                    
                    with ui.element("div").style("display:flex;align-items:center;gap:12px;padding:8px 12px;margin-bottom:12px;background:var(--bg-light);border-radius:12px;width:100%;box-sizing:border-box;"):
                        if db_u and db_u.avatar_base64:
                            ui.html(f'''
                            <div style="width:36px;height:36px;border-radius:50%;overflow:hidden;flex-shrink:0;">
                              <img src="data:image/png;base64,{db_u.avatar_base64}" style="width:100%;height:100%;object-fit:cover;" />
                            </div>
                            ''')
                        else:
                            ui.html(f'''
                            <div style="width:36px;height:36px;border-radius:50%;
                                        background:linear-gradient(135deg,#2563EB,#6366F1);
                                        display:flex;align-items:center;justify-content:center;
                                        font-weight:700;color:#fff;font-size:14px;flex-shrink:0;">
                              {user_name[0].upper()}
                            </div>
                            ''')
                            
                        ui.html(f'''
                        <div style="flex:1;overflow:hidden;">
                          <div style="font-size:13px;font-weight:600;color:var(--text-primary);white-space:nowrap;text-overflow:ellipsis;overflow:hidden;">{user_name}</div>
                          <div style="font-size:11.5px;color:var(--text-muted);">{user_role}</div>
                        </div>
                        ''')
                finally:
                    db_sb.close()

            with ui.element("a").props('href="/logout"').classes("nav-item"):
                ui.html(f'<span class="material-icons-round">{IC.LOGOUT}</span>')
                ui.html('<span class="nav-label">Logout</span>')
