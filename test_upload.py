from nicegui import ui

@ui.page('/')
def index():
    ui.html("<h1>Test Upload</h1>")
    
    upload = ui.upload(on_upload=lambda e: ui.notify(e.name)).style('display: none')
    
    with ui.element('div').style('padding: 50px; background: #eee; cursor: pointer;').on('click', lambda: upload.run_method('pickFiles')):
        ui.label("CLICK ME TO UPLOAD")

ui.run(port=8080, show=False)
