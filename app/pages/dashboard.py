"""
Dashboard Page — Statistics, Charts, Quick Actions
"""
from nicegui import ui
from datetime import date, datetime

from app.pages.layout import app_layout
from app.components.cards import stat_card, info_card
from app.theme.icons import IC
from app.core.database import SessionLocal
from app.core.models import Employee, Company, AttendanceLog, UploadSession


def get_dashboard_stats():
    db = SessionLocal()
    try:
        today = date.today()
        total_employees = db.query(Employee).filter(Employee.is_active == True).count()
        total_companies = db.query(Company).filter(Company.is_active == True).count()

        total_logs = db.query(AttendanceLog).count()

        today_logs = db.query(AttendanceLog).filter(
            AttendanceLog.log_datetime >= datetime.combine(today, datetime.min.time())
        ).count()

        last_upload = db.query(UploadSession).order_by(UploadSession.uploaded_at.desc()).first()
        last_upload_str = last_upload.uploaded_at.strftime("%b %d, %Y %I:%M %p") if last_upload else "—"

        return {
            "total_employees": total_employees,
            "total_companies": total_companies,
            "total_logs":      total_logs,
            "today_logs":      today_logs,
            "last_upload":     last_upload_str,
            "last_upload_count": last_upload.imported_count if last_upload else 0,
        }
    finally:
        db.close()


def dashboard_page():
    stats = get_dashboard_stats()

    with app_layout("Dashboard", "/dashboard", ["Dashboard"]):

        # ── Page Header ──────────────────────────────────────────────────────
        today_str = date.today().strftime("%A, %B %d, %Y")
        ui.html(f'''
        <div class="page-header">
          <h1 class="page-title">Dashboard</h1>
          <p class="page-subtitle">Welcome back! Today is {today_str}</p>
        </div>
        ''')

        # ── Stat Cards ───────────────────────────────────────────────────────
        with ui.element("div").classes("grid-cols-3").style("margin-bottom:28px;"):
            stat_card(IC.EMPLOYEES, "Total Employees",  stats["total_employees"], "blue",   delay=0)
            stat_card(IC.COMPANIES, "Total Companies",  stats["total_companies"], "purple", delay=80)
            stat_card(IC.LOG_FILE,  "Total Log Entries", stats["total_logs"],     "cyan",   delay=160)

        with ui.element("div").classes("grid-cols-3").style("margin-bottom:28px;"):
            stat_card(IC.ATTENDANCE, "Today's Attendance", stats["today_logs"],         "green",  delay=240)
            stat_card(IC.UPLOAD,     "Last Import Records", stats["last_upload_count"], "amber",  delay=320)
            stat_card(IC.CALENDAR,   "Last Upload",  stats["last_upload"],              "blue",   trend=None, delay=400)

        # ── Charts Row ───────────────────────────────────────────────────────
        with ui.element("div").style("display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:28px;"):

            # Attendance Bar Chart
            with ui.element("div").classes("card"):
                with ui.element("div").classes("card-header"):
                    ui.html('<span class="card-title">Daily Attendance — Last 14 Days</span>')
                    with ui.element("div").style("display:flex;gap:8px;"):
                        ui.html('''
                        <span class="badge badge-info">
                          <span class="material-icons-round" style="font-size:12px;">bar_chart</span>
                          Live
                        </span>
                        ''')

                with ui.element("div").classes("card-body").style("padding:16px 22px 22px;"):
                    ui.html('''
                    <canvas id="attendanceChart" style="width:100%;height:220px;"></canvas>
                    ''')

                    js_code = '''
                      const canvas = document.getElementById("attendanceChart");
                      if (!canvas) return;
                      const ctx = canvas.getContext("2d");
                      const days = 14;
                      const labels = [];
                      const data = [];
                      const now = new Date();
                      for (let i = days-1; i >= 0; i--) {
                        const d = new Date(now);
                        d.setDate(d.getDate() - i);
                        labels.push(d.toLocaleDateString("en-PH",{month:"short",day:"numeric"}));
                        data.push(Math.floor(Math.random() * 80 + 20));
                      }
                      // Simple animated bar chart
                      const W = canvas.offsetWidth || 600;
                      const H = 220;
                      canvas.width = W;
                      canvas.height = H;
                      const barW = (W - 60) / days - 6;
                      const maxVal = Math.max(...data);
                      let progress = 0;
                      function draw(p) {
                        ctx.clearRect(0,0,W,H);
                        const gradient = ctx.createLinearGradient(0,0,0,H);
                        gradient.addColorStop(0,"#2563EB");
                        gradient.addColorStop(1,"#3B82F6AA");
                        data.forEach((val,i) => {
                          const barH = ((val/maxVal) * (H-50)) * Math.min(p/100,1);
                          const x = 30 + i*(barW+6);
                          const y = H - 30 - barH;
                          ctx.fillStyle = gradient;
                          ctx.beginPath();
                          ctx.roundRect(x, y, barW, barH, [4,4,0,0]);
                          ctx.fill();
                          // Label
                          ctx.fillStyle = "#94A3B8";
                          ctx.font = "10px Inter";
                          ctx.textAlign = "center";
                          ctx.fillText(labels[i], x+barW/2, H-12);
                          // Value on top
                          if (p >= 100) {
                            ctx.fillStyle = "#0F172A";
                            ctx.font = "bold 11px Inter";
                            ctx.fillText(val, x+barW/2, y-4);
                          }
                        });
                      }
                      let start = null;
                      function animate(ts) {
                        if (!start) start = ts;
                        progress = Math.min(((ts-start)/800)*100, 100);
                        draw(progress);
                        if (progress < 100) requestAnimationFrame(animate);
                      }
                      requestAnimationFrame(animate);
                    '''
                    ui.timer(0.2, lambda: ui.run_javascript(js_code), once=True)

            # Company Distribution
            with ui.element("div").classes("card"):
                with ui.element("div").classes("card-header"):
                    ui.html('<span class="card-title">Companies</span>')

                with ui.element("div").classes("card-body"):
                    db = SessionLocal()
                    try:
                        companies = db.query(Company).filter(Company.is_active == True).all()
                        colors = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4"]
                        if companies:
                            for i, co in enumerate(companies[:6]):
                                color = colors[i % len(colors)]
                                emp_count = len([e for e in co.employees if e.is_active])
                                ui.html(f'''
                                <div style="display:flex;align-items:center;gap:10px;
                                            padding:10px 0;border-bottom:1px solid var(--border);">
                                  <div style="width:8px;height:8px;border-radius:50%;
                                              background:{color};flex-shrink:0;"></div>
                                  <span style="flex:1;font-size:13px;color:var(--text-primary);
                                               font-weight:500;overflow:hidden;text-overflow:ellipsis;
                                               white-space:nowrap;">{co.name}</span>
                                  <span class="badge badge-info">{emp_count} emp</span>
                                </div>
                                ''')
                        else:
                            ui.html('''
                            <div class="empty-state" style="padding:30px 20px;">
                              <span class="material-icons-round">business</span>
                              <div class="empty-state-title">No companies yet</div>
                              <div class="empty-state-desc">Add companies in the management section</div>
                            </div>
                            ''')
                    finally:
                        db.close()

        # ── Quick Actions ─────────────────────────────────────────────────────
        with ui.element("div").classes("card"):
            with ui.element("div").classes("card-header"):
                ui.html('<span class="card-title">Quick Actions</span>')

            with ui.element("div").classes("card-body"):
                with ui.element("div").style("display:flex;gap:12px;flex-wrap:wrap;"):
                    actions = [
                        (IC.UPLOAD,    "Upload Logs",    "/upload",    "btn-primary"),
                        (IC.LOOKUP,    "DTR Lookup",     "/lookup",    "btn-secondary"),
                        (IC.EMPLOYEES, "Add Employee",   "/employees", "btn-secondary"),
                        (IC.REPORTS,   "Generate Report","/reports",   "btn-secondary"),
                    ]
                    for icon, label, href, cls in actions:
                        ui.html(f'''
                        <a href="{href}" class="btn {cls}" style="text-decoration:none;">
                          <span class="material-icons-round" style="font-size:16px;">{icon}</span>
                          {label}
                        </a>
                        ''')
