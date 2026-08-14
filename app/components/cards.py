"""
Card Components — Stat Cards, Info Cards, File Cards
"""
from nicegui import ui


# ─── Gradient configs per card type ──────────────────────────────────────────
_GRADIENTS = {
    "blue":    ("linear-gradient(135deg,#2563EB,#3B82F6)", "#2563EB"),
    "green":   ("linear-gradient(135deg,#10B981,#059669)", "#10B981"),
    "amber":   ("linear-gradient(135deg,#F59E0B,#D97706)", "#F59E0B"),
    "red":     ("linear-gradient(135deg,#EF4444,#DC2626)", "#EF4444"),
    "purple":  ("linear-gradient(135deg,#8B5CF6,#6D28D9)", "#8B5CF6"),
    "cyan":    ("linear-gradient(135deg,#06B6D4,#0284C7)", "#06B6D4"),
}


def stat_card(
    icon: str,
    label: str,
    value: int | str,
    color: str = "blue",
    trend: str | None = None,
    trend_up: bool = True,
    delay: int = 0,
):
    """
    Animated statistics card with icon, value counter, label, and optional trend.
    color: 'blue' | 'green' | 'amber' | 'red' | 'purple' | 'cyan'
    delay: animation delay in ms (for staggered entrance)
    """
    grad, accent = _GRADIENTS.get(color, _GRADIENTS["blue"])
    trend_icon = "trending_up" if trend_up else "trending_down"
    trend_color = "#10B981" if trend_up else "#EF4444"
    card_id = f"stat-{label.lower().replace(' ', '-')}"

    with ui.element("div").classes("stat-card").style(f"animation-delay:{delay}ms"):
        # Background orb
        ui.html(f'<div class="stat-card-gradient" style="background:{accent};"></div>')

        # Icon
        with ui.element("div").classes("stat-icon").style(f"background:{grad};box-shadow:0 4px 14px {accent}44"):
            ui.html(f'<span class="material-icons-round">{icon}</span>')

        # Value (animated counter)
        numeric = value if isinstance(value, int) else 0
        display = str(value)
        ui.html(f'<div class="stat-value" id="{card_id}-val">{display}</div>')

        # Label
        ui.html(f'<div class="stat-label">{label}</div>')

        # Trend badge
        if trend:
            ui.html(f'''
            <div class="stat-trend" style="color:{trend_color}">
              <span class="material-icons-round" style="font-size:14px;">{trend_icon}</span>
              <span>{trend}</span>
            </div>
            ''')

    # Animate counter if numeric
    if isinstance(value, int) and value > 0:
        ui.run_javascript(f"""
        (function() {{
          const el = document.getElementById('{card_id}-val');
          if (el) setTimeout(() => DTR.animateCounter(el, {value}), {delay + 100});
        }})();
        """)


def info_card(title: str, actions_html: str = ""):
    """Card wrapper with header and optional action buttons. Returns context manager."""
    return _InfoCard(title, actions_html)


class _InfoCard:
    def __init__(self, title: str, actions_html: str = ""):
        self.title = title
        self.actions_html = actions_html

    def __enter__(self):
        self._card = ui.element("div").classes("card")
        self._card.__enter__()
        with ui.element("div").classes("card-header"):
            ui.html(f'<span class="card-title">{self.title}</span>')
            if self.actions_html:
                ui.html(self.actions_html)
        self._body = ui.element("div").classes("card-body")
        self._body.__enter__()
        return self

    def __exit__(self, *args):
        self._body.__exit__(*args)
        self._card.__exit__(*args)


def upload_summary_card(filename: str, total: int, imported: int, duplicates: int, invalid: int):
    """Animated upload result summary card."""
    with ui.element("div").classes("card").style(
        "border-left: 4px solid #10B981; animation: fadeInUp .4s ease;"
    ):
        with ui.element("div").classes("card-header"):
            ui.html('''
            <div style="display:flex;align-items:center;gap:10px;">
              <div style="width:32px;height:32px;background:linear-gradient(135deg,#10B981,#059669);
                          border-radius:8px;display:flex;align-items:center;justify-content:center;">
                <span class="material-icons-round" style="color:#fff;font-size:18px;">check</span>
              </div>
              <span class="card-title" style="color:#10B981;">Upload Successful</span>
            </div>
            ''')

        with ui.element("div").classes("card-body"):
            ui.html(f'<p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px;">File: <strong>{filename}</strong></p>')

            stats = [
                ("upload_file", "Total Records",    total,      "#2563EB"),
                ("check_circle","Records Imported", imported,   "#10B981"),
                ("content_copy","Duplicates Skipped",duplicates,"#F59E0B"),
                ("error",       "Invalid Records",  invalid,    "#EF4444"),
            ]
            with ui.element("div").style("display:grid;grid-template-columns:repeat(2,1fr);gap:12px;"):
                for icon, lbl, val, color in stats:
                    ui.html(f'''
                    <div style="padding:14px;background:var(--bg-subtle);border-radius:10px;
                                border-left:3px solid {color};">
                      <div style="font-size:20px;font-weight:800;color:{color};
                                  font-variant-numeric:tabular-nums;">{val:,}</div>
                      <div style="font-size:11.5px;color:var(--text-muted);font-weight:600;
                                  text-transform:uppercase;letter-spacing:.5px;margin-top:2px;">{lbl}</div>
                    </div>
                    ''')
