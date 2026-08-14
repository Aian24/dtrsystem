import sys

with open('app/pages/preview.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
collect_bottom = False
bottom_lines = []

for line in lines:
    if 'async def export_pdf():' in line and not collect_bottom:
        collect_bottom = True
    if collect_bottom:
        if line.startswith(' ' * 8):
            bottom_lines.append(line[8:])
        else:
            bottom_lines.append(line)

final_lines = []
for line in lines:
    if 'if is_public:' in line:
        break
    if 'if True:' in line:
        continue
    final_lines.append(line)

final_lines.extend(bottom_lines)
final_lines.append('    if is_public:')
final_lines.append('        ui.html("""<style>body { background: #F8FAFC !important; }</style>""")')
final_lines.append('        with ui.element("div").classes("page-area").style("max-width:1100px;margin:0 auto;"):')
final_lines.append('            render_content()')
final_lines.append('    else:')
final_lines.append('        with app_layout("DTR Preview", "/lookup", ["DTR Lookup", "Preview"]):')
final_lines.append('            render_content()')

with open('app/pages/preview.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))
