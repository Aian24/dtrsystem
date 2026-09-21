"""
User Accounts Page — System user management
"""
from __future__ import annotations
from nicegui import ui
from sqlalchemy.orm import Session
import base64

from app.pages.layout import app_layout
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import User
from app.components.modals import form_dialog
from app.components.notifications import toast_success, toast_error
from app.components.search_select import search_select


def users_page():
    table_state_users = {"search": "", "page": 1, "limit": 10}

    @ui.refreshable
    def history_container():
        db = SessionLocal()
        try:
            users2 = db.query(User).all()
        finally:
            db.close()

        selected_users = set()
        checkboxes = []

        def handle_success():
            history_container.refresh()

        def delete_selected_users(user_ids, on_success):
            db = SessionLocal()
            try:
                # Do not allow deleting user id 1 or username 'admin'
                admins = db.query(User).filter(User.id.in_(user_ids)).all()
                for a in admins:
                    if a.id == 1 or a.username == 'admin':
                        toast_error("Cannot Delete", "The default admin account cannot be deleted.")
                        return

                db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
                db.commit()
                toast_success("Users Deleted", f"{len(user_ids)} user(s) removed.")
                if on_success:
                    on_success()
            except Exception as e:
                db.rollback()
                toast_error("Error", str(e))
            finally:
                db.close()

        def confirm_delete_users(user_ids, on_success):
            with ui.dialog().classes('backdrop-blur-sm') as dialog:
                dialog.props('persistent')
                with ui.card().style("width: 450px; max-width: 90vw; padding: 24px; border-radius: 16px;"):
                    ui.html(f'''
                    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                        <div style="width:40px;height:40px;border-radius:50%;background:rgba(239, 68, 68, 0.1);display:flex;align-items:center;justify-content:center;color:#ef4444;">
                            <span class="material-icons-round" style="font-size:24px;">delete</span>
                        </div>
                        <div style="font-size:18px;font-weight:600;color:var(--text-primary);">Delete User(s)</div>
                    </div>
                    <div style="font-size:14px;color:var(--text-secondary);margin-bottom:24px;line-height:1.5;">
                        Are you sure you want to delete {len(user_ids)} user(s)?<br><br>
                        This action cannot be undone.
                    </div>
                    ''')
                    
                    with ui.row().classes("w-full justify-end"):
                        ui.button("Cancel", on_click=dialog.close).classes("btn btn-secondary")
                        ui.button("Delete Permanently", on_click=lambda: [dialog.close(), delete_selected_users(user_ids, on_success)]).classes("btn btn-danger")
            dialog.open()

        def toggle_user(uid, checked):
            if checked: selected_users.add(uid)
            else: selected_users.discard(uid)
            update_bulk_actions()

        def toggle_all(e):
            if e.value:
                selected_users.update(u.id for u in users2 if u.username != 'admin' and u.id != 1)
            else:
                selected_users.clear()
            for cb in checkboxes:
                cb.set_value(e.value)
            update_bulk_actions()

        def trigger_bulk_delete():
            if not selected_users: return
            confirm_delete_users(list(selected_users), handle_success)

        def open_add_user():
            form = {}

            def content(dialog):
                form["username"]  = ui.input("Username *").props("outlined dense").style("width:100%;margin-bottom:12px;")
                form["full_name"] = ui.input("Full Name").props("outlined dense").style("width:100%;margin-bottom:12px;")
                form["password"]  = ui.input("Password *", password=True, password_toggle_button=True).props("outlined dense").style("width:100%;margin-bottom:12px;")
                form["role"] = search_select({"admin": "Admin", "hr": "HR"}, label="Role", value="hr").props("outlined dense options-dense").style("width:100%;")

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
                    handle_success()
                except Exception as e:
                    db2.rollback()
                    toast_error("Error", str(e))
                finally:
                    db2.close()

            form_dialog("Add User", content, on_submit, "Create User")

        with ui.element("div").classes("page-header").style("display:flex;align-items:center;justify-content:space-between;"):
            with ui.element("div"):
                ui.html('<h1 class="page-title">User Accounts</h1>')
                ui.html('<p class="page-subtitle">Manage system access and roles</p>')
            with ui.element("button").classes("btn btn-primary").on("click", open_add_user):
                ui.html(f'<span class="material-icons-round" style="font-size:16px;">{IC.ADD}</span> Add User')

        with ui.element("div").classes("card"):
            with ui.element("div").classes("card-header").style("display: flex; justify-content: space-between; align-items: center; min-height: 56px;"):
                ui.html(f'<span class="card-title">System Users</span>')
                
                bulk_actions = ui.element("div").style("display: none;")
                with bulk_actions:
                    bulk_btn = ui.button("Delete Selected", icon="delete", on_click=trigger_bulk_delete).classes("btn btn-danger btn-sm")

            def update_bulk_actions():
                if len(selected_users) > 0:
                    bulk_actions.style("display: block;")
                    bulk_btn.set_text(f"Delete Selected ({len(selected_users)})")
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
                        def update_ulimit(e):
                            table_state_users["limit"] = e.value
                            table_state_users["page"] = 1
                            table_content.refresh()
                        ui.select(options=[10, 25, 50, 100], value=table_state_users["limit"], on_change=update_ulimit).props('dense outlined options-dense').style("width: 75px;")

                    # Role Filter
                    role_options = {"all": "— All Roles —", "admin": "Admin", "hr": "HR"}
                    def update_role_filter(e):
                        table_state_users["role"] = e.value
                        table_state_users["page"] = 1
                        table_content.refresh()
                    role_filter_sel = search_select(
                        options=role_options,
                        value=table_state_users.get("role", "all"),
                        on_change=update_role_filter,
                        label="Role",
                    ).props('dense outlined options-dense').style("min-width: 150px;")

                    # Status Filter
                    status_options = {"all": "— All Statuses —", "active": "Active", "inactive": "Inactive"}
                    def update_status_filter(e):
                        table_state_users["status"] = e.value
                        table_state_users["page"] = 1
                        table_content.refresh()
                    status_filter_sel = search_select(
                        options=status_options,
                        value=table_state_users.get("status", "all"),
                        on_change=update_status_filter,
                        label="Status",
                    ).props('dense outlined options-dense').style("min-width: 150px;")

                with ui.element("div").style("display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"):
                    def update_usearch(e):
                        val = e.value or ""
                        if table_state_users["search"] != val:
                            table_state_users["search"] = val
                            table_state_users["page"] = 1
                            table_content.refresh()
                    search_inp = ui.input(placeholder="Search users...", value=table_state_users["search"], on_change=update_usearch).props('dense outlined clearable').style("width: 220px;")

                    # Reset filters button
                    def reset_filters():
                        table_state_users["search"] = ""
                        table_state_users["role"] = "all"
                        table_state_users["status"] = "all"
                        table_state_users["page"] = 1
                        search_inp.value = ""
                        role_filter_sel.value = "all"
                        status_filter_sel.value = "all"
                        table_content.refresh()

                    ui.button("Reset", icon="filter_alt_off", on_click=reset_filters).classes("btn btn-reset btn-sm").tooltip("Clear all filters")

            with ui.element("div").classes("card-body").style("padding: 0; overflow-x: auto;"):
                @ui.refreshable
                def table_content():
                    import math
                    term = table_state_users["search"].lower().strip()
                    r_filt = table_state_users.get("role", "all")
                    s_filt = table_state_users.get("status", "all")

                    filtered_users = users2

                    # 1. Search term
                    if term:
                        filtered_users = [u for u in filtered_users if term in u.username.lower() or term in u.role.lower() or term in (u.full_name or '').lower()]
                    
                    # 2. Role filter
                    if r_filt != "all":
                        filtered_users = [u for u in filtered_users if u.role and u.role.lower() == r_filt.lower()]

                    # 3. Status filter
                    if s_filt == "active":
                        filtered_users = [u for u in filtered_users if u.is_active]
                    elif s_filt == "inactive":
                        filtered_users = [u for u in filtered_users if not u.is_active]

                    total_items = len(filtered_users)
                    total_pages = math.ceil(total_items / table_state_users["limit"]) or 1
                    if table_state_users["page"] > total_pages: table_state_users["page"] = total_pages
                    
                    start_idx = (table_state_users["page"] - 1) * table_state_users["limit"]
                    end_idx = start_idx + table_state_users["limit"]
                    paged_users = filtered_users[start_idx:end_idx]
                    
                    checkboxes.clear()
                    
                    if not filtered_users:
                        ui.html('''
                        <div class="empty-state">
                          <span class="material-icons-round">person_search</span>
                          <div class="empty-state-title">No users match your filters</div>
                          <div class="empty-state-subtitle">Try adjusting your search criteria or resetting filters.</div>
                        </div>
                        ''')
                    else:
                        with ui.element("table").classes("data-table").style("min-width: 600px;"):
                            with ui.element("thead"):
                                with ui.element("tr"):
                                    with ui.element("th").style("width: 48px; text-align: center;"):
                                        ui.checkbox(on_change=toggle_all)
                                
                                    headers = [
                                        ("badge", "User Info"),
                                        ("verified_user", "Role"),
                                        ("check_circle", "Status"),
                                        ("settings", "Actions")
                                    ]
                                    for icon, col in headers:
                                        with ui.element("th"):
                                            ui.html(f'<div style="display:flex;align-items:center;gap:6px;"><span class="material-icons-round" style="font-size:16px;">{icon}</span> {col}</div>')
                        
                            with ui.element("tbody"):
                                for u in paged_users:
                                    with ui.element("tr"):
                                        is_admin_user = (u.username == 'admin' or u.id == 1)

                                        with ui.element("td").style("text-align: center;"):
                                            if not is_admin_user:
                                                cb = ui.checkbox(value=u.id in selected_users, on_change=lambda e, uid=u.id: toggle_user(uid, e.value))
                                                checkboxes.append(cb)
                                            else:
                                                ui.checkbox().props("disable")

                                        with ui.element("td"):
                                            with ui.element("div").style("display:flex;align-items:center;gap:12px;"):
                                                if getattr(u, 'avatar_base64', None):
                                                    ui.html(f'''
                                                    <div style="width:32px;height:32px;border-radius:50%;overflow:hidden;
                                                                box-shadow:0 2px 8px rgba(0,0,0,.1);flex-shrink:0;">
                                                        <img src="data:image/png;base64,{u.avatar_base64}" style="width:100%;height:100%;object-fit:cover;" />
                                                    </div>
                                                    ''')
                                                else:
                                                    ui.html(f'''
                                                    <div style="width:32px;height:32px;border-radius:50%;
                                                                background:linear-gradient(135deg,#2563EB,#6366F1);
                                                                display:flex;align-items:center;justify-content:center;
                                                                font-weight:700;color:#fff;font-size:12px;flex-shrink:0;">
                                                        {u.username[0].upper()}
                                                    </div>
                                                    ''')
                                                
                                                ui.html(f'''
                                                <div>
                                                    <div style="font-weight:600;color:var(--text-primary);">{u.full_name or u.username}</div>
                                                    <div style="font-size:12px;color:var(--text-muted);">{u.username}</div>
                                                </div>
                                                ''')

                                        with ui.element("td"):
                                            ui.html(f"<span style='text-transform: capitalize;' class='badge badge-info'>{u.role}</span>")

                                        with ui.element("td"):
                                            ui.html(f'<span class="badge badge-{"success" if u.is_active else "gray"}">{("Active" if u.is_active else "Inactive")}</span>')

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
                                                    ui.upload(on_upload=handle_avatar, auto_upload=True, max_files=1).props("accept=image/* flat bordered").classes("my-uploader").style("width:100%;")

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
                                                        handle_success()
                                                    except Exception as e:
                                                        db_save.rollback()
                                                        toast_error("Error", str(e))
                                                    finally:
                                                        db_save.close()
                                                    
                                                form_dialog(f"Edit User: {user_to_edit.username}", content, on_submit, "Save Changes")
                                            finally:
                                                db_edit.close()

                                        with ui.element("td"):
                                            with ui.element("div").style("display:flex; gap: 8px; align-items: center;"):
                                                ui.button(
                                                    icon=IC.EDIT, 
                                                    on_click=lambda uid=u.id: open_edit_user(uid)
                                                ).classes("action-btn-edit").props('flat round dense').tooltip("Edit User")
                                                if not is_admin_user:
                                                    ui.button(
                                                        icon=IC.DELETE, 
                                                        on_click=lambda uid=u.id: confirm_delete_users([uid], handle_success)
                                                    ).classes("action-btn-delete").props('flat round dense').tooltip("Delete User")


                    with ui.element("div").style("padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); flex-wrap: wrap; gap: 16px;"):
                        showing_start = start_idx + 1 if total_items > 0 else 0
                        showing_end = min(end_idx, total_items)
                        filtered_text = f" (filtered from {len(users2)} total)" if total_items != len(users2) else ""
                        ui.html(f'<span style="font-size: 13px; color: var(--text-muted);">Showing {showing_start} to {showing_end} of {total_items} entries{filtered_text}</span>')
                    
                        def update_page(e):
                            table_state_users["page"] = e.value
                            table_content.refresh()
                        
                        ui.pagination(1, total_pages, value=table_state_users["page"], on_change=update_page).props('color="primary" outline active-color="primary" active-text-color="white"')

                table_content()

    with app_layout("User Accounts", "/users", ["System", "User Accounts"]):
        history_container()
