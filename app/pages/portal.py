"""
Employee Portal Page — Public landing page for viewing DTR
"""
from nicegui import ui
from datetime import date
from app.core.database import SessionLocal
from app.core.models import Company, CutoffPeriod, Employee
from app.components.notifications import toast_error

def portal_page():
    """Render the public Employee Portal (no sidebar/navbar)."""
    from app.theme.styles import FONT_LINK, GLOBAL_CSS, GLOBAL_JS
    ui.html(f"{FONT_LINK}<style>{GLOBAL_CSS}</style>").classes("hidden")
    ui.add_body_html(f"<script>{GLOBAL_JS}</script>")

    def get_companies():
        db = SessionLocal()
        try:
            comps = db.query(Company).filter(Company.is_active == True).all()
            print("FETCHED COMPANIES:", comps)
            return {c.id: c.name for c in comps}
        except Exception as e:
            print("ERROR IN get_companies:", e)
            return {}
        finally:
            db.close()

    def get_cutoffs(company_id=None):
        if not company_id:
            return {}
        db = SessionLocal()
        try:
            cutoffs = db.query(CutoffPeriod).filter(
                CutoffPeriod.company_id == company_id
            ).order_by(CutoffPeriod.id).all()
            return {c.id: c.label for c in cutoffs}
        finally:
            db.close()

    def check_employee(company_id, emp_id_str):
        db = SessionLocal()
        try:
            emp = db.query(Employee).filter(
                Employee.company_id == company_id,
                Employee.emp_id == emp_id_str,
                Employee.is_active == True
            ).first()
            return emp.id if emp else None
        finally:
            db.close()

    form_state = {
        "company_id": None,
        "cutoff_id": None,
    }

    ui.add_head_html('''
    <style>
      body { 
          background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%) !important; 
          background-attachment: fixed;
      }
      .glass-card {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 24px;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      }
      .glass-input .q-field__control {
          background: rgba(0, 0, 0, 0.2) !important;
          border-radius: 12px;
      }
      .glass-input .q-field__control:before {
          border-color: rgba(255, 255, 255, 0.1) !important;
      }
      .glass-input .q-field__control:hover:before {
          border-color: rgba(255, 255, 255, 0.3) !important;
      }
      .glass-input .q-field__native, .glass-input input {
          color: #ffffff !important;
      }
      /* Hide the native browser calendar icon for month input */
      input[type="month"]::-webkit-calendar-picker-indicator {
          display: none;
          -webkit-appearance: none;
      }
    </style>
    <script>
    // Fix month picker: open native picker when clicking anywhere on the input field
    document.addEventListener("click", function(e) {
        const qField = e.target.closest('.q-field');
        if (qField) {
            const input = qField.querySelector('input[type="month"]');
            if (input) {
                try { input.showPicker(); } catch (err) {}
            }
        }
    });
    </script>
    ''')

    with ui.element("div").classes("login-bg"):
        # Background orbs
        ui.html('''
        <div class="login-orb login-orb-1"></div>
        <div class="login-orb login-orb-2"></div>
        ''')

        # Card
        with ui.element("div").classes("glass-card").style("width: 100%; max-width: 440px; padding: 32px 24px; margin: 0 auto;"):
            
            # Header
            from app.services.settings_service import get_app_config
            cfg = get_app_config()
            
            if cfg['app_logo']:
                logo_html = f'''
                <div style="width:72px;height:72px;
                            border-radius:18px;
                            display:flex;align-items:center;justify-content:center;
                            margin:0 auto 16px;
                            box-shadow:0 10px 25px -5px rgba(0,0,0,.3); overflow:hidden;">
                  <img src="data:image/png;base64,{cfg['app_logo']}" style="width:100%;height:100%;object-fit:cover;" />
                </div>
                '''
            else:
                logo_html = '''
                <div style="width:64px;height:64px;
                            background:linear-gradient(135deg,#38bdf8,#0ea5e9);
                            border-radius:18px;
                            display:flex;align-items:center;justify-content:center;
                            margin:0 auto 16px;
                            box-shadow:0 10px 25px -5px rgba(14,165,233,.5);">
                  <span class="material-icons-round" style="color:#fff;font-size:32px;">fingerprint</span>
                </div>
                '''

            ui.html(f'''
            <div style="text-align:center;margin-bottom:32px;">
              {logo_html}
              <h1 style="font-size:26px;font-weight:800;color:#F8FAFC;letter-spacing:-.5px;margin:0 0 8px;">
                {cfg['app_name']}
              </h1>
              <p style="color:#CBD5E1;font-size:14px;margin:0;font-weight:500;">Access your Daily Time Record</p>
            </div>
            ''')

            companies = get_companies()

            # Form elements
            ui.html('<div style="color:#E2E8F0;font-size:12px;font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">Company</div>')
            company_sel = ui.select(
                options={0: "— Select Company —", **companies},
                value=0,
            ).classes("glass-input").props('dark standout').style("width:100%;margin-bottom:20px;")
            with company_sel.add_slot('prepend'):
                ui.icon('business', color='white')

            ui.html('<div style="color:#E2E8F0;font-size:12px;font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">Cutoff Rule</div>')
            cutoff_sel = ui.select(
                options={0: "— Select Cutoff —"},
                value=0,
            ).classes("glass-input").props('dark standout').style("width:100%;margin-bottom:20px;")
            with cutoff_sel.add_slot('prepend'):
                ui.icon('date_range', color='white')

            from datetime import datetime
            ui.html('<div style="color:#E2E8F0;font-size:12px;font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">Month</div>')
            month_input = ui.input(
                value=datetime.now().strftime("%Y-%m")
            ).classes("glass-input").props('type="month" dark standout').style("width:100%;margin-bottom:20px;cursor:pointer;")
            with month_input.add_slot('prepend'):
                ui.icon('calendar_month', color='white')

            ui.html('<div style="color:#E2E8F0;font-size:12px;font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;">Employee ID Number</div>')
            emp_id_input = ui.input(
                placeholder="Enter your ID Number"
            ).classes("glass-input").props('dark standout').style("width:100%;margin-bottom:32px;")
            with emp_id_input.add_slot('prepend'):
                ui.icon('badge', color='white')

            def on_company_change(e):
                try:
                    cid = int(e.value) if e.value else None
                    form_state["company_id"] = cid
                    cutoffs = get_cutoffs(cid)
                    # Use ints for keys to match company_sel pattern
                    new_options = {0: "— Select Cutoff —"}
                    for k, v in cutoffs.items():
                        new_options[k] = v
                    cutoff_sel.options = new_options
                    cutoff_sel.value = 0
                    cutoff_sel.update()
                except Exception as ex:
                    print(f"ERROR in on_company_change: {ex}")
                    toast_error("Dropdown Error", str(ex))

            company_sel.on_value_change(on_company_change)

            loading = {"value": False}

            def do_generate():
                if loading["value"]: return
                
                cid = company_sel.value
                cut_id = cutoff_sel.value
                eid = emp_id_input.value.strip()

                if cid == 0:
                    toast_error("Missing Info", "Please select your company.")
                    return
                if not cut_id or cut_id == 0:
                    toast_error("Missing Info", "Please select a cutoff period.")
                    return
                if not eid:
                    toast_error("Missing Info", "Please enter your Employee ID.")
                    return
                
                mon = month_input.value
                if not mon:
                    toast_error("Missing Info", "Please select a month.")
                    return
                
                loading["value"] = True
                generate_btn.props("loading disabled")

                # Verify employee
                internal_emp_id = check_employee(cid, eid)

                loading["value"] = False
                generate_btn.props(remove="loading disabled")

                if internal_emp_id:
                    ui.navigate.to(f"/portal/preview?emp={internal_emp_id}&cutoff={cut_id}&month={mon}")
                else:
                    toast_error("Not Found", f"No active employee found with ID '{eid}' in the selected company.")

            emp_id_input.on("keydown.enter", do_generate)

            # Generate button
            with ui.element("div").style("width:100%;margin-top:16px;"):
                generate_btn = ui.button(
                    "Generate DTR", 
                    on_click=do_generate,
                    icon="arrow_forward"
                ).props('unelevated text-color="white"').style(
                    "width:100%; height:54px; font-size:16px; font-weight:800; "
                    "border-radius:12px; letter-spacing:1px; text-transform:uppercase; "
                    "background: linear-gradient(135deg, #0ea5e9, #0284c7); "
                    "box-shadow: 0 8px 20px -6px rgba(14,165,233,.6);"
                    "transition: all 0.3s ease;"
                )

            # Admin Link
            ui.html('''
            <div style="text-align:center;margin-top:32px;">
              <a href="/login" style="color:#CBD5E1;font-size:13px;text-decoration:none;transition:color 0.2s;font-weight:600;">
                <span class="material-icons-round" style="font-size:14px;vertical-align:middle;margin-right:4px;">admin_panel_settings</span>Admin Login
              </a>
            </div>
            ''')
