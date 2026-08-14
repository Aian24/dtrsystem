"""
Settings Page — App configuration, cutoff periods, user management
"""
from nicegui import ui
from sqlalchemy.orm import joinedload

from app.pages.layout import app_layout
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import User, AppSetting, CutoffPeriod, Company
from app.components.modals import form_dialog
from app.components.notifications import toast_success, toast_error
from app.services.settings_service import get_app_config, update_app_config
import base64


def settings_page():
    with app_layout("Settings", "/settings", ["Settings"]):

        ui.html('''
        <div class="page-header">
          <h1 class="page-title">Settings</h1>
          <p class="page-subtitle">Application configuration and preferences</p>
        </div>
        ''')

        with ui.element("div").style("display:grid;grid-template-columns:1fr 1fr;gap:24px;"):

            # ── User Management ───────────────────────────────────────────────
            with ui.element("div").classes("card"):
                with ui.element("div").classes("card-header"):
                    ui.html(f'<span class="card-title"><span class="material-icons-round" style="font-size:16px;vertical-align:middle;margin-right:6px;">{IC.USER}</span>User Accounts</span>')

                with ui.element("div").classes("card-body"):
                    db = SessionLocal()
                    try:
                        users = db.query(User).all()
                    finally:
                        db.close()

                    user_container = ui.element("div")
                    table_state_users = {"search": "", "page": 1, "limit": 5}

                    def render_users():
                        user_container.clear()
                        with user_container:
                            db2 = SessionLocal()
                            try:
                                users2 = db2.query(User).all()
                            finally:
                                db2.close()

                            with ui.element("div").style("margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;"):
                                with ui.element("div").style("display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted);"):
                                    ui.html("<span>Show</span>")
                                    def update_ulimit(e):
                                        table_state_users["limit"] = e.value
                                        table_state_users["page"] = 1
                                        table_content.refresh()
                                    ui.select(options=[5, 10, 25], value=table_state_users["limit"], on_change=update_ulimit).props('dense outlined').style("width: 70px;")
                                    ui.html("<span>entries</span>")
                                    
                                with ui.element("div"):
                                    def update_usearch(e):
                                        val = e.value or ""
                                        if table_state_users["search"] != val:
                                            table_state_users["search"] = val
                                            table_state_users["page"] = 1
                                            table_content.refresh()
                                    ui.input(placeholder="Search users...", value=table_state_users["search"], on_change=update_usearch).props('dense outlined clearable').style("width: 200px;")

                            @ui.refreshable
                            def table_content():
                                import math
                                term = table_state_users["search"].lower()
                                filtered_users = [u for u in users2 if term in u.username.lower() or term in u.role.lower() or term in (u.full_name or '').lower()] if term else users2
                                
                                total_items = len(filtered_users)
                                total_pages = math.ceil(total_items / table_state_users["limit"]) or 1
                                if table_state_users["page"] > total_pages: table_state_users["page"] = total_pages
                                
                                start_idx = (table_state_users["page"] - 1) * table_state_users["limit"]
                                end_idx = start_idx + table_state_users["limit"]
                                paged_users = filtered_users[start_idx:end_idx]
                                
                                if not filtered_users:
                                    ui.html('''
                                <div class="empty-state" style="padding:30px;">
                                  <div class="empty-state-title">No users yet</div>
                                </div>
                                ''')
                                else:
                                    for u in paged_users:
                                        with ui.element("div").style(
                                            "display:flex;align-items:center;gap:12px;"
                                            "padding:12px 0;border-bottom:1px solid var(--border);"
                                        ):
                                            if getattr(u, 'avatar_base64', None):
                                                ui.html(f'''
                                                <div style="width:36px;height:36px;border-radius:50%;overflow:hidden;
                                                            box-shadow:0 2px 8px rgba(0,0,0,.1);flex-shrink:0;">
                                                  <img src="data:image/png;base64,{u.avatar_base64}" style="width:100%;height:100%;object-fit:cover;" />
                                                </div>
                                                ''')
                                            else:
                                                ui.html(f'''
                                                <div style="width:36px;height:36px;border-radius:50%;
                                                            background:linear-gradient(135deg,#2563EB,#6366F1);
                                                            display:flex;align-items:center;justify-content:center;
                                                            font-weight:700;color:#fff;font-size:14px;flex-shrink:0;">
                                                  {u.username[0].upper()}
                                                </div>
                                                ''')
                                            
                                            ui.html(f'''
                                            <div style="flex:1;">
                                              <div style="font-size:13.5px;font-weight:600;color:var(--text-primary);">{u.full_name or u.username}</div>
                                              <div style="font-size:12px;color:var(--text-muted);">{u.username} &middot; {u.role.title()}</div>
                                            </div>
                                            <span class="badge badge-{"success" if u.is_active else "gray"}">{("Active" if u.is_active else "Inactive")}</span>
                                            ''')
                                        
                                            def open_edit_user(user_id=u.id):
                                                db_edit = SessionLocal()
                                                try:
                                                    user_to_edit = db_edit.query(User).get(user_id)
                                                    if not user_to_edit: return
                                                
                                                    form = {
                                                        "password": "", 
                                                        "avatar_b64": getattr(user_to_edit, 'avatar_base64', None),
                                                        "full_name": user_to_edit.full_name or "",
                                                    }
                                                
                                                    def handle_avatar(e):
                                                        try:
                                                            content = e.content.read()
                                                            b64_str = base64.b64encode(content).decode('utf-8')
                                                            form["avatar_b64"] = b64_str
                                                            toast_success("Avatar Uploaded", "Ready to save.")
                                                        except Exception as ex:
                                                            toast_error("Upload Failed", str(ex))

                                                    def content(dialog):
                                                        form["full_name_input"] = ui.input("Full Name", value=form["full_name"]).props("outlined dense").style("width:100%;margin-bottom:12px;")
                                                        form["password_input"] = ui.input("New Password (leave blank to keep current)", password=True, password_toggle_button=True).props("outlined dense").style("width:100%;margin-bottom:12px;")
                                                        ui.html('<div style="font-size:13px;font-weight:600;margin-bottom:4px;">Profile Image</div>')
                                                        ui.upload(on_upload=handle_avatar, auto_upload=True, max_files=1).props("accept=image/* flat bordered").style("width:100%;")

                                                    def on_submit(dialog):
                                                        db_save = SessionLocal()
                                                        try:
                                                            u_save = db_save.query(User).get(user_id)
                                                            u_save.full_name = form["full_name_input"].value.strip() or None
                                                            if form["password_input"].value:
                                                                u_save.set_password(form["password_input"].value)
                                                            u_save.avatar_base64 = form["avatar_b64"]
                                                            db_save.commit()
                                                            toast_success("User Updated", u_save.username)
                                                            dialog.close()
                                                            render_users()
                                                        except Exception as e:
                                                            db_save.rollback()
                                                            toast_error("Error", str(e))
                                                        finally:
                                                            db_save.close()
                                                        
                                                    form_dialog(f"Edit User: {user_to_edit.username}", content, on_submit, "Save Changes")
                                                finally:
                                                    db_edit.close()

                                            with ui.element("button").classes("icon-btn").on("click", lambda _, uid=u.id: open_edit_user(uid)):
                                                ui.html('<span class="material-icons-round" style="font-size:16px;">edit</span>')

                                    with ui.element("div").style("padding-top: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;"):
                                        showing_start = start_idx + 1 if total_items > 0 else 0
                                        showing_end = min(end_idx, total_items)
                                        ui.html(f'<span style="font-size: 13px; color: var(--text-muted);">Showing {showing_start} to {showing_end} of {total_items} entries</span>')
                                    
                                        def update_upage(e):
                                            table_state_users["page"] = e.value
                                            table_content.refresh()
                                        
                                        ui.pagination(1, total_pages, value=table_state_users["page"], on_change=update_upage).props('color="primary" outline active-color="primary" active-text-color="white"')

                                table_content()
                    
                    render_users()
                    ui.element("div").classes("separator")

                    def open_add_user():
                        form = {}

                        def content(dialog):
                            form["username"]  = ui.input("Username *").props("outlined dense").style("width:100%;margin-bottom:12px;")
                            form["full_name"] = ui.input("Full Name").props("outlined dense").style("width:100%;margin-bottom:12px;")
                            form["password"]  = ui.input("Password *", password=True, password_toggle_button=True).props("outlined dense").style("width:100%;margin-bottom:12px;")
                            form["role"] = ui.select({"admin": "Admin", "hr": "HR Staff", "viewer": "Viewer"}, label="Role", value="hr").props("outlined dense").style("width:100%;")

                        def on_submit(dialog):
                            db2 = SessionLocal()
                            try:
                                u = User(
                                    username=form["username"].value.strip(),
                                    full_name=form["full_name"].value.strip() or None,
                                    role=form["role"].value,
                                )
                                u.set_password(form["password"].value)
                                db2.add(u)
                                db2.commit()
                                toast_success("User Created", u.username)
                                dialog.close()
                                render_users()
                            except Exception as e:
                                db2.rollback()
                                toast_error("Error", str(e))
                            finally:
                                db2.close()

                        form_dialog("Add User", content, on_submit, "Create User")

                    with ui.element("button").classes("btn btn-primary btn-sm").on("click", open_add_user):
                        ui.html(f'<span class="material-icons-round" style="font-size:14px;">{IC.ADD}</span> Add User')

            # ── Cutoff Periods ────────────────────────────────────────────────
            with ui.element("div").classes("card"):
                with ui.element("div").classes("card-header"):
                    ui.html(f'<span class="card-title"><span class="material-icons-round" style="font-size:16px;vertical-align:middle;margin-right:6px;">{IC.DATE_RANGE}</span>Cutoff Periods</span>')

                with ui.element("div").classes("card-body").style("padding:0;"):
                    db = SessionLocal()
                    try:
                        cutoffs = db.query(CutoffPeriod).options(joinedload(CutoffPeriod.company)).order_by(
                            CutoffPeriod.id.desc()
                        ).limit(10).all()
                    finally:
                        db.close()

                    if cutoffs:
                        with ui.element("table").classes("data-table"):
                            with ui.element("thead"):
                                with ui.element("tr"):
                                    for h in ["Label", "Company", "Start", "End"]:
                                        with ui.element("th"): ui.html(h)
                            with ui.element("tbody"):
                                for c in cutoffs:
                                    with ui.element("tr"):
                                        with ui.element("td"): ui.html(c.label)
                                        with ui.element("td"): ui.html(c.company.name if c.company else '—')
                                        with ui.element("td"): ui.html(f"Day {c.start_day}")
                                        with ui.element("td"): ui.html(f"Day {c.end_day}")
                    else:
                        ui.html('''
                        <div class="empty-state" style="padding:30px;">
                          <span class="material-icons-round">date_range</span>
                          <div class="empty-state-title">No cutoff periods defined</div>
                        </div>
                        ''')

                    ui.element("div").classes("separator").style("margin:0 16px;")

                    def open_add_cutoff():
                        form = {}

                        def content(dialog):
                            db2 = SessionLocal()
                            try:
                                cos = {c.id: c.name for c in db2.query(Company).filter(Company.is_active == True).all()}
                            finally:
                                db2.close()

                            form["company"] = ui.select(cos, label="Company *").props("outlined dense").style("width:100%;margin-bottom:12px;")
                            form["label"]   = ui.input("Label (e.g. June 1-15, 2025) *").props("outlined dense").style("width:100%;margin-bottom:12px;")
                            with ui.element("div").classes("grid-cols-2"):
                                form["start"] = ui.input("Start Date *").props("outlined dense type=date")
                                form["end"]   = ui.input("End Date *").props("outlined dense type=date")

                        def on_submit(dialog):
                            from datetime import date as _date
                            db2 = SessionLocal()
                            try:
                                cp = CutoffPeriod(
                                    company_id=form["company"].value,
                                    label=form["label"].value.strip(),
                                    start_date=_date.fromisoformat(form["start"].value),
                                    end_date=_date.fromisoformat(form["end"].value),
                                )
                                db2.add(cp)
                                db2.commit()
                                toast_success("Cutoff Added", cp.label)
                                dialog.close()
                            except Exception as e:
                                db2.rollback()
                                toast_error("Error", str(e))
                            finally:
                                db2.close()

                        form_dialog("Add Cutoff Period", content, on_submit, "Save Cutoff", width="480px")

                    with ui.element("div").style("padding:14px 16px;"):
                        with ui.element("button").classes("btn btn-primary btn-sm").on("click", open_add_cutoff):
                            ui.html(f'<span class="material-icons-round" style="font-size:14px;">{IC.ADD}</span> Add Cutoff Period')

        # ── App Info ──────────────────────────────────────────────────────────
        with ui.element("div").classes("card").style("margin-top:24px;"):
            app_cfg = get_app_config()
            
            with ui.element("div").classes("card-body").style(
                "display:flex;align-items:center;justify-content:space-between;gap:20px;"
            ) as config_container:
                
                def render_app_info():
                    config_container.clear()
                    cfg = get_app_config()
                    with config_container:
                        with ui.element("div").style("display:flex;align-items:center;gap:20px;"):
                            if cfg['app_logo']:
                                ui.html(f'''
                                <div style="width:48px;height:48px;border-radius:12px;
                                            display:flex;align-items:center;justify-content:center;flex-shrink:0;
                                            box-shadow:0 4px 12px rgba(0,0,0,.08);overflow:hidden;">
                                  <img src="data:image/png;base64,{cfg['app_logo']}" style="width:100%;height:100%;object-fit:cover;" />
                                </div>
                                ''')
                            else:
                                ui.html('''
                                <div style="width:48px;height:48px;border-radius:12px;
                                            background:linear-gradient(135deg,#2563EB,#6366F1);
                                            display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                                  <span class="material-icons-round" style="color:#fff;font-size:24px;">schedule</span>
                                </div>
                                ''')
                                
                            ui.html(f'''
                            <div>
                              <div style="font-size:15px;font-weight:700;color:var(--text-primary);">{cfg['app_name']}</div>
                              <div style="font-size:12.5px;color:var(--text-muted);">Version 1.0.0 &nbsp;·&nbsp; Python + NiceGUI &nbsp;·&nbsp; SQLite</div>
                            </div>
                            ''')
                            
                        # Edit Button
                        def open_edit_config():
                            form = {"logo_b64": cfg['app_logo']}
                            
                            def handle_upload(e):
                                try:
                                    import base64
                                    content = e.content.read()
                                    b64_str = base64.b64encode(content).decode('utf-8')
                                    form["logo_b64"] = b64_str
                                    toast_success("Logo Uploaded", "Image ready to save.")
                                except Exception as ex:
                                    toast_error("Upload Failed", str(ex))

                            def content(dialog):
                                form["app_name"] = ui.input("App Name *", value=cfg['app_name']).props("outlined dense").style("width:100%;margin-bottom:12px;")
                                ui.html('<div style="font-size:13px;font-weight:600;margin-bottom:4px;">App Logo</div>')
                                ui.upload(on_upload=handle_upload, auto_upload=True, max_files=1).props("accept=image/* flat bordered").style("width:100%;")
                                
                            def on_submit(dialog):
                                new_name = form["app_name"].value.strip()
                                if not new_name:
                                    toast_error("Missing Name", "App Name cannot be empty.")
                                    return
                                    
                                success = update_app_config(new_name, form["logo_b64"])
                                if success:
                                    toast_success("Saved", "App configuration updated.")
                                    dialog.close()
                                    # Refresh UI
                                    render_app_info()
                                else:
                                    toast_error("Error", "Failed to update configuration.")
                                
                            form_dialog("Edit App Configuration", content, on_submit, "Save Changes")

                        with ui.element("button").classes("btn btn-secondary btn-sm").on("click", open_edit_config):
                            ui.html('<span class="material-icons-round" style="font-size:14px;margin-right:4px;">edit</span> Edit')
                
                render_app_info()
