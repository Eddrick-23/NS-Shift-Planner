from nicegui import ui
from nicegui.events import KeyEventArguments
from grid_event_handler import GridEventHandler
from control_panel import ControlPanelHandler
from help_button import create_help_button,create_keybinds_button


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
    # Control Panel
    control_panel_handler = ControlPanelHandler()
    ui.keyboard(on_key=lambda e: handle_key(e, control_panel_handler))
    control_panel = control_panel_handler.create_control_panel()
    ui.separator()
    # Create a single event handler instance for all grids
    container = ui.column().classes("w-full gap-1")
    with container:
        grid_handler = GridEventHandler(day=1)
        await grid_handler.generate_grids()

    control_panel_handler.add_grid_event_handler(grid_handler)
    with ui.row().classes("fixed right-4 bottom-4"):
        create_keybinds_button()
        create_help_button()


ui.run()
