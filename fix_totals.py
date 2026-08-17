# -*- coding: utf-8 -*-
import re

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update the total days and absents logic
old_totals = '''    total_days      = len([e for e in dtr_entries if e.get("time_in")])
    total_absents   = sum(1 for e in dtr_entries if not e.get("time_in") and not e.get("time_out") and e.get("remarks") != "Rest Day")'''

new_totals = '''    def has_any_punch(e):
        return any(e.get(k) for k in ["time_in", "break_out_1", "break_in_1", "break_out_2", "break_in_2", "time_out"])

    total_days      = sum(1 for e in dtr_entries if has_any_punch(e))
    # Count as absent if no punches and not marked as Rest Day. (Assuming the backend populates "Absent" in remarks if truly absent)
    # But wait, the user's remarks might be blanked out later, but right here we still have the raw DTR dict.
    # Actually, dtr_service sets remarks to "Absent" if there are no logs and it's not a rest day.
    total_absents   = sum(1 for e in dtr_entries if not has_any_punch(e) and e.get("remarks") == "Absent")'''

content = content.replace(old_totals, new_totals)

# 2. Remove "Total OT (HRS)" from the summary grid
old_grid = '''                    <div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:12px; text-align:center;">
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#0A1931;">{total_days}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">DAYS PRESENT</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#EF4444;">{total_absents}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">ABSENTS</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#F59E0B;">{total_late}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">DAYS LATE</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#F59E0B;">{total_late_mins}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">LATE (MINS)</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#10B981;">0</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">TOTAL OT (HRS)</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#6366F1;">{total_undertime_hrs:.1f}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">UNDERTIME (HRS)</div>
                        </div>
                    </div>'''

new_grid = '''                    <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:12px; text-align:center;">
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#0A1931;">{total_days}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">DAYS PRESENT</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#EF4444;">{total_absents}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">ABSENTS</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#F59E0B;">{total_late}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">DAYS LATE</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#F59E0B;">{total_late_mins}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">LATE (MINS)</div>
                        </div>
                        <div style="border:1px solid #E2E8F0; padding:10px; border-radius:6px; background:#F8FAFC;">
                            <div style="font-size:16px; font-weight:900; color:#6366F1;">{total_undertime_hrs:.1f}</div>
                            <div style="font-size:8px; font-weight:700; color:#6B7280; margin-top:4px;">UNDERTIME (HRS)</div>
                        </div>
                    </div>'''

content = content.replace(old_grid, new_grid)

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated preview.py successfully.")
