"""
Settings Page — Application configuration and preferences
"""
from __future__ import annotations
from nicegui import ui

from app.pages.layout import app_layout
from app.theme.icons import IC
from app.components.modals import form_dialog
from app.components.notifications import toast_success, toast_error
from app.services.settings_service import get_app_config, update_app_config
from app.components.search_select import search_select
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

        # ── Biometric Device Configuration ──────────────────────────────────────────────────
        with ui.element("div").classes("card").style("margin-top: 24px;"):
            with ui.element("div").classes("card-header"):
                ui.html(f'<span class="card-title"><span class="material-icons-round" style="font-size:16px;vertical-align:middle;margin-right:6px;">fingerprint</span>IntelliSmart / Biometric Device Settings</span>')
            
            with ui.element("div").classes("card-body").style("display:flex; flex-direction: column; gap: 20px;") as bio_container:
                
                def render_bio_settings():
                    bio_container.clear()
                    cfg = get_app_config()
                    from app.services.biometric_service import test_device_connection, discover_biometric_devices, clear_device_attendance, get_device_log_count
                    from app.services.settings_service import update_biometric_config
                    import asyncio

                    with bio_container:
                        ui.html('''
                        <div style="font-size:13.5px;color:var(--text-secondary);line-height:1.5;">
                          Configure your <strong>IntelliSmart / ZKTeco</strong> biometric fingerprint terminal for direct network synchronization over LAN/Wi-Fi (Port 4370).
                        </div>
                        ''')

                        with ui.element("div").style("display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px;"):
                            # IP Input with Auto-Detect
                            with ui.element("div").style("display: flex; gap: 8px; align-items: flex-start;"):
                                ip_input = ui.input("Device IP Address *", value=cfg.get("biometric_ip", "192.168.1.2")).props("outlined dense").style("flex:1;")
                                auto_btn = ui.button("Auto-Detect", icon="radar").classes("btn btn-secondary btn-sm").style("margin-top:2px;white-space:nowrap;")

                            # Port Input
                            port_input = ui.number("Port", value=cfg.get("biometric_port", 4370)).props("outlined dense").style("width:100%;")
                            
                            # Comm Key / Password
                            key_input = ui.input("Comm Key", value=str(cfg.get("biometric_comm_key", "0"))).props("outlined dense").style("width:100%;")
                            
                            # Protocol
                            proto_select = search_select(["UDP", "TCP"], value=cfg.get("biometric_protocol", "UDP"), label="Protocol").props("outlined dense options-dense").style("width:100%;")

                        test_status = ui.html('<div style="font-size:13px;color:var(--text-muted);">Status: Ready to test connection</div>')

                        async def handle_auto_detect():
                            test_status.content = '<div style="font-size:13px;color:#2563eb;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;animation:spin 1s linear infinite;">radar</span> Scanning network for biometric terminals…</div>'
                            auto_btn.props('loading')
                            await asyncio.sleep(0.1)

                            loop = asyncio.get_event_loop()
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as pool:
                                devices = await loop.run_in_executor(pool, discover_biometric_devices)

                            auto_btn.props(remove='loading')
                            if devices:
                                first_ip = devices[0]["ip"]
                                first_proto = devices[0].get("protocol", "UDP")
                                ip_input.value = first_ip
                                proto_select.value = first_proto
                                test_status.content = f'<div style="font-size:13px;color:#10b981;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;">check_circle</span> Found device at <strong>{first_ip}</strong> ({first_proto})</div>'
                                toast_success("Device Found", f"Auto-detected biometric device at {first_ip}")
                            else:
                                test_status.content = '<div style="font-size:13px;color:#d97706;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;">search_off</span> No device found automatically. Check LAN cable.</div>'
                                toast_error("Not Found", "No biometric terminal responded on the network.")

                        auto_btn.on("click", handle_auto_detect)

                        with ui.element("div").style("display: flex; justify-content: space-between; align-items: center; padding-top: 10px; border-top: 1px solid var(--border); flex-wrap: wrap; gap: 12px;"):
                            async def handle_test_conn():
                                test_status.content = '<div style="font-size:13px;color:#2563eb;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;animation:spin 1s linear infinite;">sync</span> Testing connection to device…</div>'
                                ip = ip_input.value.strip()
                                port = int(port_input.value or 4370)
                                raw_k = str(key_input.value or '0').strip()
                                key = int(raw_k) if raw_k.isdigit() else 0
                                proto = str(proto_select.value or 'UDP')

                                await asyncio.sleep(0.1)

                                def run_test():
                                    return test_device_connection(ip, port, key, proto)

                                import concurrent.futures
                                loop = asyncio.get_event_loop()
                                with concurrent.futures.ThreadPoolExecutor() as pool:
                                    ok, msg = await loop.run_in_executor(pool, run_test)

                                if ok:
                                    test_status.content = f'<div style="font-size:13px;color:#10b981;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;">check_circle</span> {msg}</div>'
                                    toast_success("Connected", f"Connected to {ip}:{port}")
                                else:
                                    test_status.content = f'<div style="font-size:13px;color:#ef4444;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;">error</span> {msg}</div>'
                                    toast_error("Connection Failed", msg)

                            def handle_clear_device():
                                ip = ip_input.value.strip()
                                if not ip:
                                    toast_error("Error", "Device IP is required.")
                                    return
                                port = int(port_input.value or 4370)
                                raw_k = str(key_input.value or '0').strip()
                                key = int(raw_k) if raw_k.isdigit() else 0
                                proto = str(proto_select.value or 'UDP')

                                with ui.dialog().classes('backdrop-blur-sm') as clear_dlg:
                                    clear_dlg.props('persistent')
                                    with ui.card().style("width: 460px; max-width: 90vw; padding: 24px; border-radius: 16px;"):
                                        ui.html(f'''
                                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                                          <div style="width:40px;height:40px;border-radius:10px;background:#FEE2E2;color:#EF4444;display:flex;align-items:center;justify-content:center;">
                                            <span class="material-icons-round" style="font-size:24px;">delete_forever</span>
                                          </div>
                                          <div>
                                            <div style="font-size:16.5px;font-weight:700;color:#1E293B;">Clear Biometric Device Memory</div>
                                            <div style="font-size:12px;color:#64748B;">Target Device: {ip}:{port} ({proto})</div>
                                          </div>
                                        </div>
                                        ''')

                                        count_badge = ui.html('''
                                        <div style="display:flex;align-items:center;gap:8px;padding:9px 12px;background:#EFF6FF;border-radius:8px;border:1px solid #DBEAFE;margin-bottom:12px;font-size:12.5px;color:#2563EB;">
                                          <span class="material-icons-round" style="font-size:16px;animation:spin 1s linear infinite;">sync</span>
                                          <span>Querying device for stored punch records...</span>
                                        </div>
                                        ''')

                                        ui.html('''
                                        <div style="font-size:13px;color:#475569;line-height:1.5;margin-bottom:14px;">
                                          Are you sure you want to clear all punch logs on the physical machine?
                                          <div style="margin-top:10px;padding:10px 12px;background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;font-size:12px;color:#92400E;line-height:1.4;display:flex;align-items:flex-start;gap:8px;">
                                            <span class="material-icons-round" style="font-size:18px;color:#D97706;flex-shrink:0;">warning</span>
                                            <div><strong>Warning:</strong> Make sure you have synced or backed up your records in DTRSYS first. User PINs and fingerprint templates will <strong>NOT</strong> be deleted.</div>
                                          </div>
                                        </div>
                                        ''')
                                        with ui.element("div").style("display:flex;justify-content:flex-end;gap:8px;margin-top:8px;"):
                                            ui.button("Cancel", on_click=clear_dlg.close).props("flat dense color=grey-8").style("padding:6px 16px;text-transform:none;")
                                            
                                            async def do_clear():
                                                clear_dlg.close()
                                                test_status.content = '<div style="font-size:13px;color:#ef4444;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;animation:spin 1s linear infinite;">sync</span> Purging punch logs on biometric machine…</div>'
                                                await asyncio.sleep(0.1)

                                                import concurrent.futures
                                                loop = asyncio.get_event_loop()
                                                with concurrent.futures.ThreadPoolExecutor() as pool:
                                                    ok, msg = await loop.run_in_executor(pool, lambda: clear_device_attendance(ip, port, key, proto))

                                                if ok:
                                                    test_status.content = f'<div style="font-size:13px;color:#10b981;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;">check_circle</span> {msg}</div>'
                                                    toast_success("Logs Cleared", msg)
                                                else:
                                                    test_status.content = f'<div style="font-size:13px;color:#ef4444;font-weight:600;"><span class="material-icons-round" style="font-size:14px;vertical-align:middle;">error</span> {msg}</div>'
                                                    toast_error("Clear Failed", msg)

                                            action_btn = ui.button("Yes, Clear Machine Logs", on_click=do_clear).props("unelevated dense color=negative").style("padding:6px 16px;text-transform:none;font-weight:600;background:#EF4444 !important;color:#fff !important;")

                                        async def fetch_settings_count_async():
                                            await asyncio.sleep(0.05)
                                            loop = asyncio.get_event_loop()
                                            import concurrent.futures
                                            with concurrent.futures.ThreadPoolExecutor() as pool:
                                                ok, rec_count, msg = await loop.run_in_executor(pool, lambda: get_device_log_count(ip, port, key, proto))
                                            if ok:
                                                if rec_count > 0:
                                                    count_badge.content = f'''
                                                    <div style="display:flex;align-items:center;gap:8px;padding:10px 14px;background:#FEE2E2;border-radius:8px;border:1px solid #FECACA;margin-bottom:12px;font-size:13px;color:#991B1B;">
                                                      <span class="material-icons-round" style="font-size:20px;color:#EF4444;">receipt_long</span>
                                                      <div><strong>{rec_count:,} punch logs</strong> currently stored on machine</div>
                                                    </div>
                                                    '''
                                                    action_btn.set_text(f"Yes, Clear {rec_count:,} Records")
                                                else:
                                                    count_badge.content = '''
                                                    <div style="display:flex;align-items:center;gap:8px;padding:9px 12px;background:#F0FDF4;border-radius:8px;border:1px solid #DCFCE7;margin-bottom:12px;font-size:12.5px;color:#15803D;">
                                                      <span class="material-icons-round" style="font-size:18px;color:#16A34A;">check_circle</span>
                                                      <span>Device attendance log buffer is currently empty (0 records).</span>
                                                    </div>
                                                    '''
                                                    action_btn.set_text("Clear Device (0 Records)")
                                            else:
                                                count_badge.content = f'''
                                                <div style="padding:8px 12px;background:#F1F5F9;border-radius:8px;border:1px solid #E2E8F0;margin-bottom:12px;font-size:12px;color:#64748B;">
                                                  Device reachable. Proceeding will wipe all attendance records on the machine.
                                                </div>
                                                '''

                                        asyncio.create_task(fetch_settings_count_async())
                                clear_dlg.open()

                            def handle_save_bio():
                                ip = ip_input.value.strip()
                                if not ip:
                                    toast_error("Error", "Device IP is required.")
                                    return
                                port = int(port_input.value or 4370)
                                raw_k = str(key_input.value or '0').strip()
                                proto = str(proto_select.value or 'UDP')

                                if update_biometric_config(ip, port, raw_k, proto):
                                    toast_success("Saved", "Biometric device settings saved.")
                                else:
                                    toast_error("Error", "Failed to save biometric settings.")

                            with ui.element("div").style("display:flex; gap:10px; flex-wrap:wrap;"):
                                ui.button("Test Connection", icon="wifi", on_click=handle_test_conn).classes("btn btn-secondary")
                                ui.button("Clear Machine Logs", icon="delete_sweep", on_click=handle_clear_device).classes("btn btn-danger btn-sm")
                            
                            ui.button("Save Device Settings", icon="save", on_click=handle_save_bio).classes("btn btn-primary")

                render_bio_settings()
