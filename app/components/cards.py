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
    with ui.element("div").style("animation: fadeInUp .4s ease; width: 100%;"):
        # Header with animated SVG checkmark
        ui.html('''
        <style>
          .success-svg { width: 56px; height: 56px; border-radius: 50%; display: block; margin: 0 auto 16px; stroke-width: 3; stroke: #fff; stroke-miterlimit: 10; box-shadow: inset 0px 0px 0px #10B981; animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both; }
          .success-svg circle { stroke-dasharray: 166; stroke-dashoffset: 166; stroke-width: 3; stroke-miterlimit: 10; stroke: #10B981; fill: none; animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards; }
          .success-svg path { transform-origin: 50% 50%; stroke-dasharray: 48; stroke-dashoffset: 48; animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards; }
          @keyframes stroke { 100% { stroke-dashoffset: 0; } }
          @keyframes scale { 0%, 100% { transform: none; } 50% { transform: scale3d(1.1, 1.1, 1); } }
          @keyframes fill { 100% { box-shadow: inset 0px 0px 0px 30px #10B981; } }
        </style>
        <div style="text-align: center; padding-bottom: 24px;">
          <svg class="success-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
            <circle cx="26" cy="26" r="25" fill="none"/>
            <path fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
          </svg>
          <h2 style="margin: 0; font-size: 22px; font-weight: 700; color: #0F172A;">Upload Successful</h2>
          <p style="margin: 6px 0 0; color: #64748B; font-size: 14px;">Processed <strong>{filename}</strong></p>
        </div>
        '''.replace('{filename}', filename))

        stats = [
            ("Total Records",    total,      "#2563EB", "#EFF6FF"),
            ("Records Imported", imported,   "#10B981", "#ECFDF5"),
            ("Duplicates Skipped",duplicates,"#F59E0B", "#FFFBEB"),
            ("Invalid Records",  invalid,    "#EF4444", "#FEF2F2"),
        ]
        with ui.element("div").style("display:grid;grid-template-columns:repeat(2,1fr);gap:12px;"):
            for lbl, val, color, bg in stats:
                ui.html(f'''
                <div style="padding:16px;background:{bg};border-radius:12px;text-align:center;border:1px solid rgba(0,0,0,0.03);">
                  <div style="font-size:24px;font-weight:800;color:{color};font-variant-numeric:tabular-nums;line-height:1;">{val:,}</div>
                  <div style="font-size:11.5px;color:var(--text-secondary);font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-top:6px;">{lbl}</div>
                </div>
                ''')
