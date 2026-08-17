from nicegui import ui

with ui.dialog().classes('backdrop-blur-sm') as dialog:
    with ui.card().style("width: 400px; height: 300px;"):
        ui.label("Test Select")
        TIME_OPTIONS = [f"{h:02d}:{m:02d} {ampm}" for ampm in ["AM", "PM"] for h in ([12] + list(range(1, 12))) for m in [0, 15, 30, 45]]
        # Test 1: Just options-dense
        ui.select(TIME_OPTIONS, label="Default").props('outlined dense options-dense')
        # Test 2: With menu-props or options-cover
        ui.select(TIME_OPTIONS, label="Fixed height").props('outlined dense options-dense popup-content-style="max-height: 200px"')

ui.button("Open", on_click=dialog.open)
ui.run(port=8766, show=False)
