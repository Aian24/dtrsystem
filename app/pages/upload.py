"""
Upload Logs Page — Multi-format log decryption (.log, .dat, .txt, .csv, .bin, .rec)
and direct biometric device IP synchronization.
"""
from __future__ import annotations
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from nicegui import ui, events

from app.pages.layout import app_layout
from app.components.cards import upload_summary_card
from app.components.notifications import toast_success, toast_error
from app.theme.icons import IC
from app.services.import_service import import_log_file, sync_biometric_device
from app.services.biometric_service import test_device_connection, clear_device_attendance, get_device_log_count
from app.services.settings_service import get_app_config, update_biometric_config
from app.core.config import LOGS_DIR
from app.core.database import SessionLocal
from app.core.models import UploadSession, AttendanceLog
from app.components.search_select import search_select
from app.components.date_picker import modern_date_picker


def upload_page():
    state = {
        "uploading": False,
        "result":    None,
        "filename":  "",
    }

    with app_layout("Upload Logs", "/upload", ["Upload Logs"]):

        ui.add_css('''
        .upload-wrapper {
            position: relative;
            width: 100%;
        }

        .upload-zone {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 180px;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 2px dashed #CBD5E1;
            border-radius: 16px;
            background: #F8FAFC;
            transition: all 0.2s ease;
        }
        
        .upload-zone:hover {
            border-color: var(--color-primary);
            background: #EFF6FF;
        }
        
        .my-uploader {
            position: relative;
            z-index: 2;
            background: transparent !important;
            width: 100% !important;
            box-shadow: none !important;
            max-height: none !important;
        }

        /* Make the header invisible but perfectly sized to cover the upload-zone */
        .my-uploader .q-uploader__header {
            opacity: 0.001 !important;
            height: 180px !important;
            min-height: 180px !important;
            max-height: 180px !important;
            position: relative !important;
            background: transparent !important;
            flex-shrink: 0 !important;
        }

        /* Break out of inner constraints so input can fill the header */
        .my-uploader .q-uploader__header .q-btn,
        .my-uploader .q-uploader__header .q-btn__content,
        .my-uploader .q-uploader__header .q-focus-helper,
        .my-uploader .q-uploader__header .q-icon {
            position: static !important;
            transform: none !important;
            overflow: visible !important;
            clip: auto !important;
            contain: none !important;
        }
        
        /* Force Quasar's hidden file input to cover the header entirely */
        .my-uploader input[type="file"] {
            display: block !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            max-width: none !important;
            max-height: none !important;
            z-index: 9999 !important;
            opacity: 0 !important;
            cursor: pointer !important;
        }

        /* Ensure the file list shows up cleanly */
        .my-uploader .q-uploader__list {
            background: transparent !important;
            padding: 0 !important;
            border: none !important;
            margin-top: 16px !important;
            display: grid !important;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)) !important;
            gap: 16px !important;
        }
        
        .my-uploader .q-uploader__file {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            padding: 16px !important;
            margin-bottom: 0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05) !important;
            display: flex !important;
            align-items: center !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .my-uploader .q-uploader__file:hover {
            border-color: var(--color-primary) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1) !important;
        }
        
        .my-uploader .q-uploader__file::before {
            content: "\\e873";
            font-family: "Material Icons Round", "Material Icons" !important;
            font-size: 22px;
            color: #fff;
            background: linear-gradient(135deg, #3B82F6, #2563EB);
            border-radius: 10px;
            width: 42px;
            height: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            flex-shrink: 0;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        }

        .my-uploader .q-uploader__file-header {
            background: transparent !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }
        
        .my-uploader .q-uploader__file-header-content {
            padding-right: 16px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            flex-grow: 1 !important;
        }

        .my-uploader .q-uploader__title {
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            font-size: 14.5px !important;
            margin-bottom: 4px !important;
            line-height: 1.2 !important;
        }

        .my-uploader .q-uploader__subtitle {
            display: block !important;
            font-size: 12.5px !important;
            color: var(--text-muted) !important;
            font-weight: 500 !important;
        }
        
        .my-uploader .q-uploader__file .q-btn {
            color: var(--text-muted) !important;
            background: #F1F5F9 !important;
            border-radius: 50% !important;
            width: 36px !important;
            height: 36px !important;
            min-height: 36px !important;
            padding: 0 !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        .my-uploader .q-uploader__file .q-btn:hover {
            color: #EF4444 !important;
            background: #FEE2E2 !important;
            transform: rotate(90deg) !important;
        }

        .q-uploader__file--light {
            color: inherit !important;
        }
        
        .history-row {
            transition: background 0.2s ease;
            cursor: pointer;
        }
        .history-row:hover {
            background: #F1F5F9 !important;
        }

        .decryption-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            background: rgba(16, 185, 129, 0.1);
            color: #059669;
            font-size: 12px;
            font-weight: 600;
        }
        ''')

        ui.html('''
        <div class="page-header" style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
          <div>
            <h1 class="page-title">Attendance Logs & Biometric Sync</h1>
            <p class="page-subtitle">Upload log files (.log, .dat, .txt, .csv) or sync directly with your IntelliSmart biometric device</p>
          </div>
          <div class="decryption-badge">
            <span class="material-icons-round" style="font-size:16px;">lock_open</span>
            Universal Auto-Decryption Active
          </div>
        </div>
        ''')

        # ── Progress Dialog for Upload/Sync ──────────────────────────────────
        with ui.dialog().classes('backdrop-blur-sm') as progress_modal:
            progress_modal.props('persistent')
            with ui.card().style("width: 420px; max-width: 90vw; padding: 24px; border-radius: 16px;"):
                ui.html('''
                <div style="font-size: 18px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">
                    Processing Attendance Records
                </div>
                <div id="modal-filename-display" style="font-size: 13.5px; color: var(--text-muted); margin-bottom: 24px;">
                    Processing...
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:13px;font-weight:500;">
                  <span id="modal-progress-label" style="color:var(--text-primary);">Processing…</span>
                  <span id="modal-progress-pct" style="color:var(--color-primary);">0%</span>
                </div>
                ''')
                with ui.element("div").classes("progress-bar-wrapper"):
                    modal_progress_bar = ui.element("div").classes("progress-bar-fill").style("width:0%; transition: width 0.2s;")

        # ── Biometric Direct IP Sync Dialog ──────────────────────────────────
        with ui.dialog().classes('backdrop-blur-sm') as bio_sync_modal:
            with ui.card().classes('w-full').style("width: 660px; max-width: 95vw; padding: 24px 28px; border-radius: 16px; align-items: stretch; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.05);"):
                cfg = get_app_config()
                
                # Header with Title and 'X' close button (Full Width)
                with ui.element("div").style("display:flex;align-items:center;justify-content:space-between;width:100%;margin-bottom:16px;"):
                    with ui.element("div").style("display:flex;align-items:center;gap:12px;"):
                        ui.html('''
                        <div style="width:38px;height:38px;border-radius:10px;background:#EFF6FF;color:#2563EB;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(37,99,235,0.12);">
                          <span class="material-icons-round" style="font-size:22px;">fingerprint</span>
                        </div>
                        ''')
                        with ui.element("div"):
                            ui.html('''
                            <div style="font-size:16.5px;font-weight:700;color:var(--text-primary);line-height:1.2;">Direct Biometric Sync</div>
                            <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">Connect to IntelliSmart / ZKTeco machine over LAN/Wi-Fi</div>
                            ''')
                    ui.button(icon="close", on_click=bio_sync_modal.close).props("flat round dense color=grey-7").style("margin-top:-2px;")

                from app.services.biometric_service import discover_biometric_devices

                # Row 1: Device IP Address + Auto-Detect button (Full Width)
                with ui.element("div").style("display:flex;gap:10px;align-items:center;width:100%;margin-bottom:10px;"):
                    bio_ip = ui.input("Device IP Address *", value=cfg.get("biometric_ip", "192.168.1.2")).props("outlined dense").style("flex:1;")
                    auto_btn = ui.button("Auto-Detect IP", icon="radar").classes("btn btn-secondary btn-sm").style("height:40px;white-space:nowrap;")

                # Row 2: Equal Width 3-Column Inputs (Port | Comm Key | Protocol) (Full Width)
                with ui.element("div").style("display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;width:100%;margin-bottom:12px;"):
                    bio_port = ui.number("Port", value=cfg.get("biometric_port", 4370)).props("outlined dense")
                    bio_key = ui.input("Comm Key", value=str(cfg.get("biometric_comm_key", "0"))).props("outlined dense")
                    bio_proto = search_select(["UDP", "TCP"], value=cfg.get("biometric_protocol", "UDP"), label="Protocol").props("outlined dense options-dense")

                # Row 3: Sync Date Range Card (Full Width)
                with ui.element("div").style("background:#F8FAFC;padding:14px 16px;border-radius:12px;border:1px solid #E2E8F0;width:100%;margin-bottom:14px;"):
                    ui.html('''
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                      <div style="font-size:13px;font-weight:600;color:#1E293B;display:flex;align-items:center;gap:6px;">
                        <span class="material-icons-round" style="font-size:17px;color:#2563EB;">date_range</span>
                        Sync Date Range
                      </div>
                      <div style="font-size:11.5px;color:#64748B;">Leave blank to sync all</div>
                    </div>
                    ''')
                    with ui.element("div").style("display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%;"):
                        bio_start_date = modern_date_picker("Start Date", placeholder="YYYY-MM-DD")
                        bio_end_date = modern_date_picker("End Date", placeholder="YYYY-MM-DD")

                    with ui.element("div").style("display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;align-items:center;width:100%;"):
                        ui.html('<span style="font-size:11px;font-weight:600;color:#64748B;margin-right:2px;">Presets:</span>')
                        
                        def set_today():
                            t = datetime.now().strftime("%Y-%m-%d")
                            bio_start_date.value = t
                            bio_end_date.value = t

                        def set_current_month():
                            now = datetime.now()
                            bio_start_date.value = now.replace(day=1).strftime("%Y-%m-%d")
                            bio_end_date.value = now.strftime("%Y-%m-%d")

                        def set_current_cutoff():
                            now = datetime.now()
                            if now.day <= 15:
                                bio_start_date.value = now.replace(day=1).strftime("%Y-%m-%d")
                                bio_end_date.value = now.replace(day=15).strftime("%Y-%m-%d")
                            else:
                                bio_start_date.value = now.replace(day=16).strftime("%Y-%m-%d")
                                bio_end_date.value = now.strftime("%Y-%m-%d")

                        def clear_dates():
                            bio_start_date.value = ""
                            bio_end_date.value = ""

                        ui.button("This Cutoff", on_click=set_current_cutoff).props("flat dense").style("font-size:11px;text-transform:none;padding:2px 8px;background:#fff;border:1px solid #CBD5E1;border-radius:5px;color:#334155;font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,0.04);")
                        ui.button("This Month", on_click=set_current_month).props("flat dense").style("font-size:11px;text-transform:none;padding:2px 8px;background:#fff;border:1px solid #CBD5E1;border-radius:5px;color:#334155;font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,0.04);")
                        ui.button("Today", on_click=set_today).props("flat dense").style("font-size:11px;text-transform:none;padding:2px 8px;background:#fff;border:1px solid #CBD5E1;border-radius:5px;color:#334155;font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,0.04);")
                        ui.button("All Time", on_click=clear_dates).props("flat dense").style("font-size:11px;text-transform:none;padding:2px 8px;background:transparent;border:1px dashed #CBD5E1;border-radius:5px;color:#64748B;")

                # Status box (Full Width)
                sync_status_box = ui.html('''
                <div style="font-size:12px;color:#475569;margin-bottom:14px;padding:8px 12px;background:#F1F5F9;border-radius:8px;border:1px solid #E2E8F0;display:flex;align-items:center;gap:8px;width:100%;box-sizing:border-box;">
                  <span class="material-icons-round" style="font-size:15px;color:#64748B;">info</span>
                  <span>Ready to connect (Default: UDP Port 4370)</span>
                </div>
                ''')

                async def handle_auto_detect():
                    sync_status_box.content = '<div style="font-size:12px;color:#2563EB;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;animation:spin 1s linear infinite;">radar</span> Scanning local network for biometric device…</div>'
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
                        bio_ip.value = first_ip
                        bio_proto.value = first_proto
                        sync_status_box.content = f'<div style="font-size:12px;color:#059669;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;">check_circle</span> Discovered {len(devices)} device(s)! Selected: <strong>{first_ip}</strong> ({first_proto})</div>'
                        toast_success("Device Found", f"Auto-detected biometric device at {first_ip}")
                    else:
                        sync_status_box.content = '<div style="font-size:12px;color:#D97706;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;">search_off</span> No device responded on network. Check LAN cable or enter IP manually.</div>'
                        toast_error("Not Found", "No biometric device found automatically.")

                auto_btn.on("click", handle_auto_detect)

                async def test_bio_conn():
                    sync_status_box.content = '<div style="font-size:12px;color:#2563EB;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;animation:spin 1s linear infinite;">sync</span> Testing connection…</div>'
                    ip = bio_ip.value.strip()
                    port = int(bio_port.value or 4370)
                    raw_k = str(bio_key.value or '0').strip()
                    key = int(raw_k) if raw_k.isdigit() else 0
                    proto = str(bio_proto.value or 'UDP')

                    await asyncio.sleep(0.1)

                    def run():
                        return test_device_connection(ip, port, key, proto)

                    loop = asyncio.get_event_loop()
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        ok, msg = await loop.run_in_executor(pool, run)

                    if ok:
                        sync_status_box.content = f'<div style="font-size:12px;color:#059669;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;">check_circle</span> {msg}</div>'
                        toast_success("Connected", f"Device reached at {ip}:{port}")
                    else:
                        sync_status_box.content = f'<div style="font-size:12px;color:#EF4444;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;">error</span> {msg}</div>'
                        toast_error("Connection Failed", msg)

                async def execute_bio_sync():
                    ip = bio_ip.value.strip()
                    if not ip:
                        toast_error("Missing IP", "Please enter biometric device IP.")
                        return
                    port = int(bio_port.value or 4370)
                    raw_k = str(bio_key.value or '0').strip()
                    key = int(raw_k) if raw_k.isdigit() else 0
                    proto = str(bio_proto.value or 'UDP')
                    s_date = str(bio_start_date.value or "").strip() or None
                    e_date = str(bio_end_date.value or "").strip() or None

                    # Save config for next time
                    update_biometric_config(ip, port, raw_k, proto)
                    bio_sync_modal.close()

                    ui.run_javascript(f'document.getElementById("modal-filename-display").innerHTML = "Syncing from device <strong>{ip}:{port}</strong>...";')
                    progress_modal.open()

                    sync_state = {"pct": 0, "msg": "Connecting to machine…", "done": False, "error": None, "result": None}

                    def progress_cb(pct: int, msg: str = ""):
                        sync_state["pct"] = pct
                        sync_state["msg"] = msg

                    def run_sync():
                        try:
                            res = sync_biometric_device(
                                ip=ip,
                                port=port,
                                comm_key=key,
                                protocol=proto,
                                start_date=s_date,
                                end_date=e_date,
                                progress_cb=progress_cb,
                            )
                            sync_state["result"] = res
                            sync_state["done"] = True
                        except Exception as ex:
                            sync_state["error"] = str(ex)
                            sync_state["done"] = True

                    thread = threading.Thread(target=run_sync, daemon=True)
                    thread.start()

                    while not sync_state["done"]:
                        modal_progress_bar.style(f"width:{sync_state['pct']}%;")
                        ui.run_javascript(f'''
                          let p = document.getElementById("modal-progress-pct");
                          let l = document.getElementById("modal-progress-label");
                          if (p) p.textContent = "{sync_state['pct']}%";
                          if (l) l.textContent = "{sync_state['msg']}";
                        ''')
                        await asyncio.sleep(0.2)

                    progress_modal.close()

                    if sync_state["result"]:
                        res = sync_state["result"]
                        history_table.refresh()
                        toast_success("Sync Complete", f"Successfully synced {res['imported']:,} new records ({res['duplicates']:,} duplicates skipped).")

                        with ui.dialog().classes('backdrop-blur-sm') as success_modal:
                            success_modal.props('persistent')
                            with ui.card().style("width: 450px; max-width: 90vw; padding: 0; border-radius: 16px; overflow: hidden; align-items: stretch;"):
                                with ui.element('div').style("padding: 24px; width: 100%; position: relative;"):
                                    upload_summary_card(
                                        filename=f"Biometric Sync ({ip})",
                                        total=res["total"],
                                        imported=res["imported"],
                                        duplicates=res["duplicates"],
                                        invalid=res["invalid"],
                                    )
                                with ui.element('div').style("padding: 16px 24px; display: flex; justify-content: flex-end; border-top: 1px solid var(--border); background: var(--bg-subtle); width: 100%;"):
                                    def close_and_reload():
                                        success_modal.close()
                                        ui.run_javascript('setTimeout(() => { window.location.reload(); }, 200);')
                                    ui.button("OK", on_click=close_and_reload).classes("btn btn-primary").style("padding: 8px 32px;")
                        success_modal.open()
                        while success_modal.value:
                            await asyncio.sleep(0.1)
                        ui.run_javascript('setTimeout(() => { window.location.reload(); }, 200);')
                    elif sync_state["error"]:
                        toast_error("Biometric Sync Failed", sync_state["error"])

                def confirm_clear_device():
                    ip = bio_ip.value.strip()
                    if not ip:
                        toast_error("Missing IP", "Please enter biometric device IP.")
                        return
                    port = int(bio_port.value or 4370)
                    raw_k = str(bio_key.value or '0').strip()
                    key = int(raw_k) if raw_k.isdigit() else 0
                    proto = str(bio_proto.value or 'UDP')

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

                            # Live count display badge
                            count_badge = ui.html('''
                            <div style="display:flex;align-items:center;gap:8px;padding:9px 12px;background:#EFF6FF;border-radius:8px;border:1px solid #DBEAFE;margin-bottom:12px;font-size:12.5px;color:#2563EB;">
                              <span class="material-icons-round" style="font-size:16px;animation:spin 1s linear infinite;">sync</span>
                              <span>Querying device for stored punch records...</span>
                            </div>
                            ''')

                            ui.html('''
                            <div style="font-size:13px;color:#475569;line-height:1.5;margin-bottom:14px;">
                              Are you sure you want to wipe all attendance punch records stored in the physical biometric machine?
                              <div style="margin-top:10px;padding:10px 12px;background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;font-size:12px;color:#92400E;line-height:1.4;display:flex;align-items:flex-start;gap:8px;">
                                <span class="material-icons-round" style="font-size:18px;color:#D97706;flex-shrink:0;">warning</span>
                                <div><strong>Important:</strong> Ensure you have clicked <strong>Sync Now</strong> or exported a backup before clearing. Registered employee users, names, and fingerprint templates will <strong>NOT</strong> be deleted.</div>
                              </div>
                            </div>
                            ''')

                            with ui.element("div").style("display:flex;justify-content:flex-end;gap:8px;margin-top:8px;"):
                                ui.button("Cancel", on_click=clear_dlg.close).props("flat dense color=grey-8").style("padding:6px 16px;text-transform:none;font-weight:500;")
                                
                                async def run_clear():
                                    clear_dlg.close()
                                    sync_status_box.content = '<div style="font-size:12px;color:#EF4444;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;animation:spin 1s linear infinite;">sync</span> Purging punch logs from biometric machine…</div>'
                                    await asyncio.sleep(0.1)

                                    loop = asyncio.get_event_loop()
                                    import concurrent.futures
                                    with concurrent.futures.ThreadPoolExecutor() as pool:
                                        ok, msg = await loop.run_in_executor(pool, lambda: clear_device_attendance(ip, port, key, proto))

                                    if ok:
                                        sync_status_box.content = f'<div style="font-size:12px;color:#059669;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;">check_circle</span> {msg}</div>'
                                        toast_success("Logs Cleared", f"Device at {ip} attendance log memory was reset to 0.")
                                    else:
                                        sync_status_box.content = f'<div style="font-size:12px;color:#EF4444;font-weight:600;display:flex;align-items:center;gap:6px;width:100%;"><span class="material-icons-round" style="font-size:15px;">error</span> {msg}</div>'
                                        toast_error("Clear Failed", msg)

                                action_btn = ui.button("Yes, Clear Machine Logs", on_click=run_clear).props("unelevated dense color=negative").style("padding:6px 16px;text-transform:none;font-weight:600;background:#EF4444 !important;color:#fff !important;")

                            async def fetch_count_async():
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

                            asyncio.create_task(fetch_count_async())
                    clear_dlg.open()

                # Dialog action buttons (Full Width with space-between)
                with ui.element("div").style("display:flex;justify-content:space-between;align-items:center;width:100%;margin-top:12px;gap:12px;"):
                    with ui.element("div").style("display:flex;gap:10px;align-items:center;"):
                        ui.button("Test Connection", icon="wifi", on_click=test_bio_conn).classes("btn btn-secondary btn-sm").style("white-space:nowrap;padding:8px 16px;")
                        ui.button("Clear Device Logs", icon="delete_sweep", on_click=confirm_clear_device).classes("btn btn-danger btn-sm").style("white-space:nowrap;padding:8px 16px;")
                    ui.button("Sync Now", icon="cloud_download", on_click=execute_bio_sync).classes("btn btn-primary").style("white-space:nowrap;padding:9px 24px;")

        # ── Main Grid Layout ─────────────────────────────────────────────────
        with ui.element("div").style("display:grid;grid-template-columns:1fr 380px;gap:24px;"):

            # ── Left: Upload & Action area ───────────────────────────────────
            with ui.element("div"):

                # Quick Direct Sync Banner Card
                with ui.element("div").classes("card").style("margin-bottom:20px;background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%);color:#fff;border:none;box-shadow:0 10px 25px -5px rgba(15,23,42,0.3);"):
                    with ui.element("div").classes("card-body").style("display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;padding:20px 24px;"):
                        with ui.element("div").style("display:flex;align-items:center;gap:16px;"):
                            ui.html('''
                            <div style="width:48px;height:48px;border-radius:14px;background:rgba(37,99,235,0.25);display:flex;align-items:center;justify-content:center;color:#60A5FA;flex-shrink:0;">
                              <span class="material-icons-round" style="font-size:28px;">fingerprint</span>
                            </div>
                            ''')
                            with ui.element("div"):
                                ui.html('<div style="font-size:16px;font-weight:700;color:#F8FAFC;">IntelliSmart Direct Network Sync</div>')
                                ui.html('<div style="font-size:13px;color:#94A3B8;">Pull punches directly from your biometric terminal over IP without USB drives</div>')
                        
                        ui.button(
                            "Sync from Device (IP)", 
                            icon="sync", 
                            on_click=bio_sync_modal.open
                        ).classes("btn btn-primary").style("background:linear-gradient(135deg,#3B82F6,#2563EB);padding:10px 24px;font-size:14px;font-weight:600;box-shadow:0 4px 14px rgba(37,99,235,0.4);")

                # File Upload Card
                with ui.element("div").classes("card").style("margin-bottom:20px;"):
                    with ui.element("div").classes("card-body"):

                        upload_lock = asyncio.Lock()

                        async def handle_multi_upload(e: events.MultiUploadEventArguments):
                            async with upload_lock:
                                total_res = {"total": 0, "imported": 0, "duplicates": 0, "invalid": 0}
                                file_names = []
                                
                                ui.run_javascript('document.getElementById("modal-filename-display").innerHTML = "Processing files...";')
                                progress_modal.open()
                                
                                for file_name, file_content_obj in zip(e.names, e.contents):
                                    file_names.append(file_name)
                                    ui.run_javascript(f'document.getElementById("modal-filename-display").innerHTML = "Processing <strong>{file_name}</strong>";')
                                    
                                    # Save file
                                    save_path = LOGS_DIR / file_name
                                    file_content = file_content_obj.read() if hasattr(file_content_obj, "read") else await file_content_obj.read()
                                    save_path.write_bytes(file_content)
                                    
                                    import_state = {"pct": 0, "msg": "Analyzing file…", "done": False, "error": None, "result": None}
                                    
                                    def progress_cb(pct: int, msg: str = ""):
                                        import_state["pct"] = pct
                                        import_state["msg"] = msg
                                        
                                    def run_import():
                                        try:
                                            result = import_log_file(str(save_path), progress_cb)
                                            import_state["result"] = result
                                            import_state["done"] = True
                                        except Exception as ex:
                                            import_state["error"] = str(ex)
                                            import_state["done"] = True
                                            
                                    thread = threading.Thread(target=run_import, daemon=True)
                                    thread.start()
                                    
                                    while not import_state["done"]:
                                        modal_progress_bar.style(f"width:{import_state['pct']}%;")
                                        ui.run_javascript(f'''
                                          let p = document.getElementById("modal-progress-pct");
                                          let l = document.getElementById("modal-progress-label");
                                          if (p) p.textContent = "{import_state['pct']}%";
                                          if (l) l.textContent = "{import_state['msg']}";
                                        ''')
                                        await asyncio.sleep(0.2)
                                        
                                    if import_state["result"]:
                                        res = import_state["result"]
                                        total_res["total"] += res["total"]
                                        total_res["imported"] += res["imported"]
                                        total_res["duplicates"] += res["duplicates"]
                                        total_res["invalid"] += res["invalid"]
                                    elif import_state["error"]:
                                        toast_error(f"Import Failed for {file_name}", import_state["error"])
                                
                                progress_modal.close()
                                
                                display_name = f"{len(file_names)} file{'s' if len(file_names) > 1 else ''} uploaded" if len(file_names) > 1 else (file_names[0] if file_names else "Batch Upload")
                                
                                with ui.dialog().classes('backdrop-blur-sm') as success_modal:
                                    success_modal.props('persistent')
                                    with ui.card().style("width: 450px; max-width: 90vw; padding: 0; border-radius: 16px; overflow: hidden; align-items: stretch;"):
                                        with ui.element('div').style("padding: 24px; width: 100%; position: relative;"):
                                            upload_summary_card(
                                                filename=display_name,
                                                total=total_res["total"],
                                                imported=total_res["imported"],
                                                duplicates=total_res["duplicates"],
                                                invalid=total_res["invalid"],
                                            )
                                        
                                        with ui.element('div').style("padding: 16px 24px; display: flex; justify-content: flex-end; border-top: 1px solid var(--border); background: var(--bg-subtle); width: 100%;"):
                                            def close_and_reload_upload():
                                                success_modal.close()
                                                ui.run_javascript('setTimeout(() => { window.location.reload(); }, 200);')
                                            ui.button("OK", on_click=close_and_reload_upload).classes("btn btn-primary").style("padding: 8px 32px;")
                                            
                                success_modal.open()
                                
                                while success_modal.value:
                                    await asyncio.sleep(0.1)
                                    
                                upload.reset()
                                ui.run_javascript('setTimeout(() => { window.location.reload(); }, 200);')

                        with ui.element("div").classes("upload-wrapper"):
                            ui.html(f'''
                            <div class="upload-zone" id="upload-zone">
                              <div style="width: 56px; height: 56px; border-radius: 50%; background: #DBEAFE; color: #2563EB; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.1);">
                                <span class="material-icons-round" style="font-size: 28px;">{IC.DRAG_DROP}</span>
                              </div>
                              <div style="font-size: 18px; font-weight: 700; color: #0F172A; margin-bottom: 6px;">
                                Drag & drop logs or USB exports here
                              </div>
                              <div style="color: #64748B; font-size: 13.5px; margin-bottom: 24px;">
                                Supports <strong>.log, .dat (attlog), .txt, .csv, .bin, .rec</strong> with automatic decryption
                              </div>
                              <div class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 32px; font-size: 15px; font-weight: 600; border-radius: 100px; box-shadow: 0 4px 12px rgba(37,99,235,0.3); pointer-events: none;">
                                <span class="material-icons-round" style="font-size: 20px;">{IC.UPLOAD}</span>
                                Select Files
                              </div>
                            </div>
                            ''')

                            upload = ui.upload(
                                label="",
                                auto_upload=False,
                                multiple=True,
                                on_multi_upload=handle_multi_upload,
                                on_rejected=lambda e: ui.notify(
                                    "Invalid file type. Supported: .log, .dat, .txt, .csv, .bin, .rec", 
                                    type="negative", 
                                    icon="error", 
                                    position="top-right"
                                )
                            ).props(
                                'accept=".log,.dat,.txt,.csv,.bin,.rec,.glog" color="primary" hide-upload-btn'
                            ).classes("my-uploader")
                            
                            with ui.element("div").style("display:flex; justify-content:flex-end; margin-top: 16px;"):
                                submit_btn = ui.button(
                                    "Process & Decrypt Logs", 
                                    icon="lock_open",
                                    on_click=lambda: upload.run_method("upload")
                                ).classes("btn btn-primary").style("padding: 8px 24px; font-weight: 600; font-size: 14px; position: relative; z-index: 10;")

                # Upload history
                with ui.element("div").classes("card"):
                    with ui.element("div").classes("card-header"):
                        ui.html('<span class="card-title">Recent Import History</span>')
                    with ui.element("div").classes("card-body").style("padding:0;"):
                        
                        def show_summary_modal(s: UploadSession):
                            with ui.dialog().classes('backdrop-blur-sm') as dlg:
                                with ui.card().style("width: 800px; max-width: 90vw; padding: 0; border-radius: 16px; overflow: hidden; align-items: stretch; max-height: 85vh; display: flex; flex-direction: column;"):
                                    with ui.element('div').style("padding: 24px; width: 100%; position: relative; overflow-y: auto;"):
                                        
                                        ui.html(f'<div style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:16px;">{s.filename} Details</div>')
                                        
                                        upload_summary_card(
                                            filename=s.filename,
                                            total=s.record_count or 0,
                                            imported=s.imported_count or 0,
                                            duplicates=s.duplicate_count or 0,
                                            invalid=s.invalid_count or 0,
                                        )
                                        
                                        with ui.element("div").style("margin-top:24px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;"):
                                            ui.html('<div style="font-size:14px;font-weight:600;color:var(--text-primary);white-space:nowrap;">Parsed Import Records</div>')
                                            with ui.element("div").style("display:flex; gap:10px; align-items:center; flex-wrap:nowrap;"):
                                                dir_filter = search_select(
                                                    {"all": "All Punches", "I": "Check In Only", "O": "Check Out Only"},
                                                    value="all",
                                                    label="Direction"
                                                ).props('dense outlined options-dense no-wrap').style("min-width: 175px; width: 175px; flex-shrink:0;")
                                                search = ui.input(placeholder="Search records...").props('dense outlined clearable').style("min-width: 220px; width: 220px; flex-shrink:0;")
                                        
                                        db = SessionLocal()
                                        raw_rows = []
                                        try:
                                            logs = db.query(AttendanceLog).filter(AttendanceLog.session_id == s.id).all()
                                            if logs:
                                                for l in logs:
                                                    emp_id = l.employee.emp_id if l.employee else "?"
                                                    dir_badge = "Check In" if l.direction == "I" else "Check Out"
                                                    raw_rows.append({
                                                        'emp_id': str(emp_id),
                                                        'date': l.log_datetime.strftime("%m/%d/%Y"),
                                                        'time': l.log_datetime.strftime("%I:%M:%S %p"),
                                                        'direction': dir_badge,
                                                        'raw': str(l.raw_line or "")
                                                    })
                                        finally:
                                            db.close()
                                            
                                        if raw_rows:
                                            columns = [
                                                {'name': 'emp_id', 'label': 'Emp ID', 'field': 'emp_id', 'align': 'left', 'sortable': True},
                                                {'name': 'date', 'label': 'Date', 'field': 'date', 'align': 'left', 'sortable': True},
                                                {'name': 'time', 'label': 'Time', 'field': 'time', 'align': 'left', 'sortable': True},
                                                {'name': 'direction', 'label': 'Dir', 'field': 'direction', 'align': 'center', 'sortable': True},
                                                {'name': 'raw', 'label': 'Raw Log Entry', 'field': 'raw', 'align': 'left'},
                                            ]
                                            table = ui.table(
                                                columns=columns, 
                                                rows=list(raw_rows), 
                                                row_key='raw',
                                                pagination={'rowsPerPage': 50}
                                            ).classes('w-full').style(
                                                "font-size: 13px; border: 1px solid var(--border); border-radius: 8px; box-shadow: none;"
                                            ).props(':rows-per-page-options="[10, 25, 50, 100, 0]"')
                                            
                                            def do_filter(*_):
                                                term = (search.value or "").lower().strip()
                                                d_val = dir_filter.value or "all"
                                                filtered = raw_rows
                                                if d_val == "I":
                                                    filtered = [r for r in filtered if r['direction'] == "Check In"]
                                                elif d_val == "O":
                                                    filtered = [r for r in filtered if r['direction'] == "Check Out"]
                                                if term:
                                                    filtered = [
                                                        r for r in filtered 
                                                        if term in r['emp_id'].lower() 
                                                        or term in r['raw'].lower() 
                                                        or term in r['date'].lower() 
                                                        or term in r['time'].lower()
                                                        or term in r['direction'].lower()
                                                    ]
                                                table.rows = filtered
                                                table.update()

                                            search.on_value_change(do_filter)
                                            dir_filter.on_value_change(do_filter)
                                            
                                        else:
                                            ui.html('<div style="color:var(--text-muted);font-size:13px;padding:16px 0;">No individual records found in database.</div>')
                                            
                                    with ui.element('div').style("padding: 16px 24px; display: flex; justify-content: flex-end; border-top: 1px solid var(--border); background: var(--bg-subtle); width: 100%; flex-shrink: 0;"):
                                        ui.button("Close", on_click=dlg.close).classes("btn btn-secondary")

                            dlg.open()

                        # Filter state for upload history
                        hist_filter_state = {"status": "all", "search": ""}

                        # Toolbar for Recent Import History
                        with ui.element("div").style("padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--bg-subtle); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;"):
                            with ui.element("div").style("display: flex; gap: 8px; align-items: center; flex-wrap: wrap;"):
                                hist_status_sel = search_select(
                                    {"all": "All Statuses", "success": "Success", "failed": "Failed", "partial": "Partial"},
                                    value="all",
                                    label="Status",
                                ).props("dense outlined options-dense no-wrap").style("min-width: 150px; width: 150px; flex-shrink:0;")
                                
                                hist_search_input = ui.input(
                                    placeholder="Search filename..."
                                ).props("dense outlined clearable").style("min-width: 200px; width: 200px; flex-shrink:0;")

                                with hist_search_input.add_slot("append"):
                                    ui.icon("search", color="grey-6")

                                def on_hist_filter_change(*_):
                                    hist_filter_state["status"] = hist_status_sel.value or "all"
                                    hist_filter_state["search"] = (hist_search_input.value or "").strip().lower()
                                    history_table.refresh()

                                hist_status_sel.on_value_change(on_hist_filter_change)
                                hist_search_input.on_value_change(on_hist_filter_change)

                            def reset_hist_filters():
                                hist_status_sel.value = "all"
                                hist_search_input.value = ""
                                hist_filter_state["status"] = "all"
                                hist_filter_state["search"] = ""
                                history_table.refresh()

                            ui.button("Reset", icon="filter_alt_off", on_click=reset_hist_filters).classes("btn btn-reset btn-sm")

                        @ui.refreshable
                        def history_table():
                            db = SessionLocal()
                            try:
                                query = db.query(UploadSession)
                                st = hist_filter_state["status"]
                                if st != "all":
                                    query = query.filter(UploadSession.status == st)
                                term = hist_filter_state["search"]
                                if term:
                                    query = query.filter(UploadSession.filename.ilike(f"%{term}%"))
                                sessions = query.order_by(
                                    UploadSession.uploaded_at.desc()
                                ).limit(20).all()
                            finally:
                                db.close()

                            if sessions:
                                with ui.element("table").classes("data-table"):
                                    with ui.element("thead"):
                                        with ui.element("tr"):
                                            for col in ["Source / File", "Date", "Imported", "Duplicates", "Status"]:
                                                with ui.element("th"):
                                                    ui.html(col)
                                    with ui.element("tbody"):
                                        for s in sessions:
                                            with ui.element("tr").classes("history-row").on("click", lambda e, session=s: show_summary_modal(session)):
                                                with ui.element("td"):
                                                    ui.html(f"<strong>{s.filename}</strong>")
                                                with ui.element("td"):
                                                    ui.html(f"{s.uploaded_at.strftime('%b %d %Y %I:%M %p')}")
                                                with ui.element("td"):
                                                    ui.html(f"{s.imported_count:,}")
                                                with ui.element("td"):
                                                    ui.html(f"{s.duplicate_count:,}")
                                                with ui.element("td"):
                                                    badge_color = "#10B981" if s.status.lower() == "success" else ("#EF4444" if s.status.lower() == "failed" else "#F59E0B")
                                                    badge_bg = "rgba(16, 185, 129, 0.1)" if s.status.lower() == "success" else ("rgba(239, 68, 68, 0.1)" if s.status.lower() == "failed" else "rgba(245, 158, 11, 0.1)")
                                                    ui.html(f'<span class="badge" style="background: {badge_bg}; color: {badge_color};">{s.status.upper()}</span>')
                            else:
                                ui.html('''
                                <div class="empty-state">
                                  <span class="material-icons-round">history</span>
                                  <div class="empty-state-title">No matching uploads</div>
                                </div>
                                ''')
                                
                        history_table()

            # ── Right: Instructions & Formats ────────────────────────────────
            with ui.element("div"):
                with ui.element("div").classes("card").style("margin-bottom:16px;"):
                    with ui.element("div").classes("card-header"):
                        ui.html('<span class="card-title">How It Works</span>')
                    with ui.element("div").classes("card-body"):
                        ui.html('''
                        <div style="display:flex;flex-direction:column;gap:14px;">
                          <div style="display:flex;gap:12px;align-items:flex-start;">
                            <div style="width:28px;height:28px;border-radius:50%;
                                        background:linear-gradient(135deg,#2563EB,#3B82F6);
                                        display:flex;align-items:center;justify-content:center;
                                        flex-shrink:0;font-size:12px;font-weight:700;color:#fff;">1</div>
                            <div>
                              <div style="font-size:13.5px;font-weight:600;color:var(--text-primary);">Direct IP Sync (Fastest)</div>
                              <div style="font-size:12.5px;color:var(--text-muted);margin-top:2px;">Click <strong>Sync from Device (IP)</strong> to pull logs directly across your local network.</div>
                            </div>
                          </div>
                          <div style="display:flex;gap:12px;align-items:flex-start;">
                            <div style="width:28px;height:28px;border-radius:50%;
                                        background:linear-gradient(135deg,#2563EB,#3B82F6);
                                        display:flex;align-items:center;justify-content:center;
                                        flex-shrink:0;font-size:12px;font-weight:700;color:#fff;">2</div>
                            <div>
                              <div style="font-size:13.5px;font-weight:600;color:var(--text-primary);">USB / File Decryption</div>
                              <div style="font-size:12.5px;color:var(--text-muted);margin-top:2px;">Drop any USB export file (<code>attlog.dat</code>, <code>*.log</code>, <code>*.txt</code>) into the upload box.</div>
                            </div>
                          </div>
                          <div style="display:flex;gap:12px;align-items:flex-start;">
                            <div style="width:28px;height:28px;border-radius:50%;
                                        background:linear-gradient(135deg,#2563EB,#3B82F6);
                                        display:flex;align-items:center;justify-content:center;
                                        flex-shrink:0;font-size:12px;font-weight:700;color:#fff;">3</div>
                            <div>
                              <div style="font-size:13.5px;font-weight:600;color:var(--text-primary);">Automatic Parsing</div>
                              <div style="font-size:12.5px;color:var(--text-muted);margin-top:2px;">Binary structs, Chinese charsets, and encrypted files are automatically decoded and inserted into the DTR database.</div>
                            </div>
                          </div>
                        </div>
                        ''')

                with ui.element("div").classes("card"):
                    with ui.element("div").classes("card-header"):
                        ui.html('<span class="card-title">Supported Formats</span>')
                    with ui.element("div").classes("card-body"):
                        ui.html('''
                        <div style="display:flex;flex-direction:column;gap:10px;font-size:12.5px;">
                          <div style="background:var(--bg-subtle);padding:10px 12px;border-radius:8px;border:1px solid var(--border);">
                            <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                              <span class="material-icons-round" style="font-size:16px;color:#3B82F6;">bolt</span>
                              <strong style="color:var(--text-primary);">Direct Network Sync:</strong>
                            </div>
                            <span style="color:var(--text-muted);">IntelliSmart, ZKTeco, Granding, Realand (Port 4370 TCP/UDP)</span>
                          </div>
                          <div style="background:var(--bg-subtle);padding:10px 12px;border-radius:8px;border:1px solid var(--border);">
                            <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                              <span class="material-icons-round" style="font-size:16px;color:#6366F1;">inventory_2</span>
                              <strong style="color:var(--text-primary);">Binary .DAT Structs:</strong>
                            </div>
                            <span style="color:var(--text-muted);"><code>attlog.dat</code>, <code>attendance.dat</code> (16-byte, 24-byte, 40-byte C-structures)</span>
                          </div>
                          <div style="background:var(--bg-subtle);padding:10px 12px;border-radius:8px;border:1px solid var(--border);">
                            <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                              <span class="material-icons-round" style="font-size:16px;color:#EC4899;">translate</span>
                              <strong style="color:var(--text-primary);">Chinese & Scrambled Files:</strong>
                            </div>
                            <span style="color:var(--text-muted);">GBK, GB2312, GB18030, Big5, UTF-16, XOR encrypted streams</span>
                          </div>
                          <div style="background:var(--bg-subtle);padding:10px 12px;border-radius:8px;border:1px solid var(--border);">
                            <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                              <span class="material-icons-round" style="font-size:16px;color:#10B981;">description</span>
                              <strong style="color:var(--text-primary);">Standard Text / CSV:</strong>
                            </div>
                            <span style="color:var(--text-muted);">Comma, Tab, Space, Pipe separated <code>EmpID, Date, Time, In/Out</code></span>
                          </div>
                        </div>
                        ''')
