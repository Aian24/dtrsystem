"""
Settings Page — Application configuration and preferences
"""
from nicegui import ui

from app.pages.layout import app_layout
from app.theme.icons import IC
from app.components.modals import form_dialog
from app.components.notifications import toast_success, toast_error
from app.services.settings_service import get_app_config, update_app_config
import base64

from datetime import datetime

def settings_page():
    with app_layout("Settings", "/settings", ["System", "Settings"]):

        ui.add_css('''
        .my-uploader {
            position: relative;
            background: transparent !important;
            width: 100% !important;
            box-shadow: none !important;
        }
        .my-uploader .q-uploader__header {
            background: #F8FAFC !important;
            border: 2px dashed #CBD5E1 !important;
            border-radius: 12px !important;
            color: #475569 !important;
        }
        .my-uploader .q-uploader__list { background: transparent !important; }
        .my-uploader .q-uploader__file {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }
        ''')

        ui.html('''
        <div class="page-header">
          <h1 class="page-title">Settings</h1>
          <p class="page-subtitle">Application configuration and preferences</p>
        </div>
        ''')

        # ── App Info & General Configuration ──────────────────────────────────────────────────
        with ui.element("div").classes("card"):
            with ui.element("div").classes("card-header"):
                ui.html(f'<span class="card-title"><span class="material-icons-round" style="font-size:16px;vertical-align:middle;margin-right:6px;">{IC.SETTINGS}</span>General Configurations</span>')
            
            with ui.element("div").classes("card-body").style("display:flex; flex-direction: column; gap: 24px;") as config_container:
                
                def render_app_info():
                    config_container.clear()
                    cfg = get_app_config()
                    now = datetime.now()
                    with config_container:
                        
                        # --- Section: Branding ---
                        with ui.element("div").style("display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 20px; border-bottom: 1px solid var(--border);"):
                            with ui.element("div").style("display:flex;align-items:center;gap:20px;"):
                                if cfg.get('app_logo'):
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
                                  <div style="font-size:12.5px;color:var(--text-muted);">Application Name & Branding</div>
                                </div>
                                ''')
                                
                        # --- Section: Attendance Rules ---
                        with ui.element("div").style("display: none; flex-direction: column; gap: 16px;"):
                            ui.html('<div style="font-size:14px;font-weight:700;color:var(--text-primary);">Attendance Rules</div>')
                            
                            with ui.element("div").style("display: grid; grid-template-columns: 1fr 1fr; gap: 16px;"):
                                # Grace Period
                                with ui.element("div").style("background: white; padding: 16px; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 1px 2px rgba(0,0,0,0.05);"):
                                    with ui.element("div").style("display:flex; align-items:center; gap: 12px; margin-bottom: 8px;"):
                                        ui.html('<div style="width:32px;height:32px;border-radius:8px;background:rgba(245, 158, 11, 0.1);display:flex;align-items:center;justify-content:center;color:#f59e0b;"><span class="material-icons-round" style="font-size:18px;">timer</span></div>')
                                        ui.html('<div style="font-size:13px;color:var(--text-primary);font-weight:700;">Grace Period (Late)</div>')
                                    ui.html(f'<div style="font-size:14px;font-weight:500;color:var(--text-secondary); padding-left: 44px;">{cfg.get("grace_period_mins", 15)} mins</div>')

                                # Standard Work Hours
                                with ui.element("div").style("background: white; padding: 16px; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 1px 2px rgba(0,0,0,0.05);"):
                                    with ui.element("div").style("display:flex; align-items:center; gap: 12px; margin-bottom: 8px;"):
                                        ui.html('<div style="width:32px;height:32px;border-radius:8px;background:rgba(59, 130, 246, 0.1);display:flex;align-items:center;justify-content:center;color:#3b82f6;"><span class="material-icons-round" style="font-size:18px;">work</span></div>')
                                        ui.html('<div style="font-size:13px;color:var(--text-primary);font-weight:700;">Standard Work Hours</div>')
                                    ui.html(f'<div style="font-size:14px;font-weight:500;color:var(--text-secondary); padding-left: 44px;">{cfg.get("standard_work_hours", 8)} hours/day</div>')

                                # Auto-deduct Lunch
                                with ui.element("div").style("background: white; padding: 16px; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 1px 2px rgba(0,0,0,0.05);"):
                                    with ui.element("div").style("display:flex; align-items:center; gap: 12px; margin-bottom: 8px;"):
                                        ui.html('<div style="width:32px;height:32px;border-radius:8px;background:rgba(16, 185, 129, 0.1);display:flex;align-items:center;justify-content:center;color:#10b981;"><span class="material-icons-round" style="font-size:18px;">restaurant</span></div>')
                                        ui.html('<div style="font-size:13px;color:var(--text-primary);font-weight:700;">Auto-deduct Lunch</div>')
                                    ui.html(f'<div style="font-size:14px;font-weight:500;color:var(--text-secondary); padding-left: 44px;">{cfg.get("auto_deduct_lunch_mins", 60)} mins</div>')

                                # Overtime
                                with ui.element("div").style("background: white; padding: 16px; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 1px 2px rgba(0,0,0,0.05);"):
                                    with ui.element("div").style("display:flex; align-items:center; gap: 12px; margin-bottom: 8px;"):
                                        ui.html('<div style="width:32px;height:32px;border-radius:8px;background:rgba(139, 92, 246, 0.1);display:flex;align-items:center;justify-content:center;color:#8b5cf6;"><span class="material-icons-round" style="font-size:18px;">more_time</span></div>')
                                        ui.html('<div style="font-size:13px;color:var(--text-primary);font-weight:700;">Enable Overtime</div>')
                                    val = "Yes" if cfg.get("enable_overtime") else "No"
                                    ui.html(f'<div style="font-size:14px;font-weight:500;color:var(--text-secondary); padding-left: 44px;">{val}</div>')

                        with ui.element("div").style("display: flex; justify-content: flex-end; padding-top: 10px;"):
                            # Edit Button
                            def open_edit_config():
                                form = {"logo_b64": cfg.get('app_logo')}
                                
                                def handle_upload(e):
                                    try:
                                        content = e.content.read()
                                        b64_str = base64.b64encode(content).decode('utf-8')
                                        form["logo_b64"] = b64_str
                                        toast_success("Logo Uploaded", "Image ready to save.")
                                    except Exception as ex:
                                        toast_error("Upload Failed", str(ex))

                                def content(dialog):
                                    form["app_name"] = ui.input("App Name *", value=cfg['app_name']).props("outlined dense").style("width:100%;margin-bottom:12px;")
                                    
                                    ui.html('<div style="font-size:13px;font-weight:600;margin-bottom:4px;">App Logo</div>')
                                    ui.upload(on_upload=handle_upload, auto_upload=True, max_files=1, label="Click to upload").props('color="transparent" text-color="primary" flat bordered').style("width:100%;margin-bottom:20px;border-radius:8px;border: 2px dashed var(--border);")
                                    
                                    with ui.element("div").style("display: none;"):
                                        ui.html('<div style="font-size:14px;font-weight:700;margin-top:16px;margin-bottom:12px;border-bottom:1px solid var(--border);padding-bottom:4px;">Attendance Rules</div>')
                                        
                                        with ui.element("div").style("display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 8px;"):
                                            with ui.element("div"):
                                                ui.html('<div style="font-size:13px;font-weight:600;margin-bottom:4px;">Grace Period (mins)</div>')
                                                form["grace_period_mins"] = ui.number(value=cfg.get("grace_period_mins", 15)).props("outlined dense").style("width:100%;")
                                            
                                            with ui.element("div"):
                                                ui.html('<div style="font-size:13px;font-weight:600;margin-bottom:4px;">Standard Work Hours</div>')
                                                form["standard_work_hours"] = ui.number(value=cfg.get("standard_work_hours", 8)).props("outlined dense").style("width:100%;")
                                            
                                            with ui.element("div"):
                                                ui.html('<div style="font-size:13px;font-weight:600;margin-bottom:4px;">Auto-deduct Lunch (mins)</div>')
                                                form["auto_deduct_lunch_mins"] = ui.number(value=cfg.get("auto_deduct_lunch_mins", 60)).props("outlined dense").style("width:100%;")
                                            
                                            with ui.element("div"):
                                                ui.html('<div style="font-size:13px;font-weight:600;margin-bottom:4px;">Enable Overtime</div>')
                                                form["enable_overtime"] = ui.checkbox("Calculate OT", value=cfg.get("enable_overtime", False))
                                    
                                def on_submit(dialog):
                                    new_name = form["app_name"].value.strip()
                                    if not new_name:
                                        toast_error("Missing Name", "App Name cannot be empty.")
                                        return
                                        
                                    success = update_app_config(
                                        app_name=new_name, 
                                        app_logo_base64=form["logo_b64"],
                                        grace_period_mins=int(form.get("grace_period_mins", type("obj", (object,), {"value": 15})).value or 0),
                                        standard_work_hours=int(form.get("standard_work_hours", type("obj", (object,), {"value": 8})).value or 0),
                                        enable_overtime=form.get("enable_overtime", type("obj", (object,), {"value": False})).value,
                                        auto_deduct_lunch_mins=int(form.get("auto_deduct_lunch_mins", type("obj", (object,), {"value": 60})).value or 0)
                                    )
                                    if success:
                                        toast_success("Saved", "App configuration updated.")
                                        dialog.close()
                                        # Refresh UI
                                        render_app_info()
                                    else:
                                        toast_error("Error", "Failed to update configuration.")
                                    
                                form_dialog("Edit App Configuration", content, on_submit, "Save Changes", width="500px")

                            ui.button('Edit Configuration', icon='edit', on_click=open_edit_config).classes("btn btn-primary")
                
                render_app_info()
