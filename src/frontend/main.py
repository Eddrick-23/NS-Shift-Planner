from nicegui import ui
from nicegui.events import KeyEventArguments
from grid_event_handler import GridEventHandler
from control_panel import ControlPanelHandler
from hour_grid_handler import HourGridHandler
from help_button import create_help_button,create_keybinds_button
from compress_grid_switch import CompressSwitch
from css import custom_css

# Define custom CSS for borders

def handle_key(e: KeyEventArguments, control_panel_handler: ControlPanelHandler):
    if e.modifiers.shift and e.action.keydown:
        if e.key == "!":  # shift + 1
            ui.notify("MCC")
            control_panel_handler.set_radio_value("MCC")
        if e.key == "@":  # shift + 2
            ui.notify("HCC1")
            control_panel_handler.set_radio_value("HCC1")
        if e.key == "#":  # shift + 3
            ui.notify("HCC2")
            control_panel_handler.set_radio_value("HCC2")


@ui.page("/")
async def main_page():
    # Add the CSS to the page
    ui.add_head_html(custom_css)
    # Control Panel
    control_panel_handler = ControlPanelHandler()
    ui.keyboard(on_key=lambda e: handle_key(e, control_panel_handler))
    control_panel = control_panel_handler.create_control_panel()
    ui.separator()
    # Create a single event handler instance for all grids
    container1 = ui.column().classes("w-full gap-1")
    container2 = ui.column().classes("w-full gap-1")
    container3 = ui.row().classes("w-full flex-nowrap")
    with container3:
        container3_left = ui.column().classes("w-2/6 gap-1")
        container3_right = ui.column().classes("w-4/6 gap-1")

    with container1:
        grid_handler_1 = GridEventHandler(day=1)
        await grid_handler_1.generate_grids()
    with container2:
        grid_handler_2 = GridEventHandler(day=2)
        await grid_handler_2.generate_grids()
    with container3_right:
        grid_handler_3 = GridEventHandler(day=3)
        await grid_handler_3.generate_grids()
    with container3_left:
        hour_grid_handler = HourGridHandler()
        await hour_grid_handler.create_hour_grid()

    grid_handler_1.add_hour_grid_handler(hour_grid_handler)
    grid_handler_2.add_hour_grid_handler(hour_grid_handler)
    grid_handler_3.add_hour_grid_handler(hour_grid_handler)
    control_panel_handler.add_grid_event_handler(grid_handler_1)
    control_panel_handler.add_grid_event_handler(grid_handler_2)
    control_panel_handler.add_grid_event_handler(grid_handler_3)
    control_panel_handler.add_hour_grid_handler(hour_grid_handler)

    switch = CompressSwitch()
    switch.add_day_3_grid_handler(grid_handler_3)
    with ui.row().classes("fixed right-4 bottom-4"):
        switch.create_switch()
        create_keybinds_button()
        create_help_button() 

ui.run()
