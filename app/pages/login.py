"""
Login Page — Glassmorphism dark card with animated background orbs
"""
from nicegui import ui, app as ngapp
from app.services.auth_service import authenticate_user, create_session
from app.components.notifications import toast_error


def login_page():
    """Render the login page (no sidebar/navbar)."""
    from app.theme.styles import FONT_LINK, GLOBAL_CSS, GLOBAL_JS
    ui.html(f"{FONT_LINK}<style>{GLOBAL_CSS}</style>").classes("hidden")
    ui.add_body_html(f"<script>{GLOBAL_JS}</script>")

    ui.html("""
    <style>
      body { background: #0F172A !important; }
      .q-field__control { background: rgba(255,255,255,.06) !important; border-radius: 10px !important; }
      .q-field__native, .q-field__label { color: #F1F5F9 !important; }
      .q-field--outlined .q-field__control:before { border-color: rgba(255,255,255,.15) !important; }
      .q-field--focused .q-field__control:before  { border-color: #3B82F6 !important; }
    </style>
    """)

    with ui.element("div").classes("login-bg"):
        # Background orbs
        ui.html('''
        <div class="login-orb login-orb-1"></div>
        <div class="login-orb login-orb-2"></div>
        ''')

        # Card
        with ui.element("div").classes("login-card"):
            # Logo + Title
            from app.services.settings_service import get_app_config
            cfg = get_app_config()
            
            if cfg['app_logo']:
                logo_html = f'''
                <div style="width:64px;height:64px;
                            border-radius:14px;
                            display:flex;align-items:center;justify-content:center;
                            margin:0 auto 16px;
                            box-shadow:0 8px 24px rgba(0,0,0,.2); overflow:hidden;">
                  <img src="data:image/png;base64,{cfg['app_logo']}" style="width:100%;height:100%;object-fit:cover;" />
                </div>
                '''
            else:
                logo_html = '''
                <div style="width:56px;height:56px;
                            background:linear-gradient(135deg,#2563EB,#6366F1);
                            border-radius:14px;
                            display:flex;align-items:center;justify-content:center;
                            margin:0 auto 16px;
                            box-shadow:0 8px 24px rgba(37,99,235,.4);">
                  <span class="material-icons-round" style="color:#fff;font-size:28px;">schedule</span>
                </div>
                '''

            ui.html(f'''
            <div style="text-align:center;margin-bottom:32px;">
              {logo_html}
              <h1 style="font-size:22px;font-weight:800;color:#F1F5F9;letter-spacing:-.4px;margin:0 0 6px;">
                {cfg['app_name']}
              </h1>
              <p style="color:#64748B;font-size:13.5px;margin:0;">Sign in to manage the system</p>
            </div>
            ''')

            # Form
            form_data = {"username": "", "password": "", "show_pw": False}

            username_input = ui.input(
                label="Username",
                placeholder="Enter your username"
            ).props('outlined color="blue-6"').style("width:100%;margin-bottom:14px;")
            username_input.on("keydown.enter", lambda: pw_input.run_method("focus"))

            pw_input = ui.input(
                label="Password",
                placeholder="Enter your password",
                password=True,
                password_toggle_button=True,
            ).props('outlined color="blue-6"').style("width:100%;margin-bottom:24px;")

            # Login button
            btn_container = ui.element("div").style("width:100%;")
            loading = {"value": False}

            def do_login():
                if loading["value"]:
                    return
                username = username_input.value.strip()
                password = pw_input.value

                if not username or not password:
                    toast_error("Missing Fields", "Please enter both username and password.")
                    return

                loading["value"] = True
                login_btn.props("loading disabled")

                user = authenticate_user(username, password)
                loading["value"] = False
                login_btn.props(remove="loading disabled")

                if user:
                    create_session(user)
                    ui.navigate.to("/dashboard")
                else:
                    toast_error("Login Failed", "Invalid username or password.")
                    pw_input.value = ""

            pw_input.on("keydown.enter", do_login)

            with btn_container:
                login_btn = ui.button("Sign In", on_click=do_login).props(
                    'color="blue-6" unelevated'
                ).style(
                    "width:100%;height:46px;font-size:15px;font-weight:700;"
                    "border-radius:10px;letter-spacing:.2px;"
                )

            # Footer note
            ui.html('''
            <div style="text-align:center;margin-top:24px;">
              <a href="/" style="color:#64748B;font-size:12.5px;text-decoration:none;transition:color 0.2s;">
                &larr; Back to Employee Portal
              </a>
            </div>
            ''')
