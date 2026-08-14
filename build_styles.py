import pathlib

css_content = pathlib.Path('app/theme/_css.txt').read_text(encoding='utf-8')
js_content = pathlib.Path('app/theme/_js.txt').read_text(encoding='utf-8')

new_content = '"""\n'
new_content += 'Global CSS Theme — NiceGUI 3.x (Quasar) Compatible\n'
new_content += '"""\n\n'

new_content += 'FONT_LINK = """\n'
new_content += '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
new_content += '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">\n'
new_content += '<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Round">\n'
new_content += '"""\n\n'

new_content += 'GLOBAL_CSS = """\n'
new_content += css_content + '\n'
new_content += '"""\n\n'

new_content += 'GLOBAL_JS = """\n'
new_content += js_content + '\n'
new_content += '"""\n'

pathlib.Path('app/theme/styles.py').write_text(new_content, encoding='utf-8')
print("Successfully wrote styles.py")
