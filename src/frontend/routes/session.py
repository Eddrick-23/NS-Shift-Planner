import nicegui
from nicegui import ui, app
from uuid import uuid4
from nicegui.events import KeyEventArguments
from src.frontend.components.grid_event_handler import GridEventHandler
from src.frontend.components.control_panel import ControlPanelHandler
from src.frontend.components.hour_grid_handler import HourGridHandler
from src.frontend.components.menu_widget import MenuWidget
from src.frontend.components.left_drawer_toggle import LeftDrawerToggle
from src.frontend.components.help_button import (
    create_help_button,
    create_keybinds_button,
)
from src.frontend.components.compress_grid_switch import CompressSwitch
from src.frontend.components.swap_grid_name import SwapGridNameUI
from src.frontend.styles.css import custom_css
from src.frontend.api.urls_and_keys import SESSION_ID_KEY,CLIENT_KEY
from src.frontend.components.connect_backend_ui import on_startup


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


def copy_to_clipboard(text: str):
    ui.run_javascript(f'navigator.clipboard.writeText("{text}")')
    ui.notify("Copied to clipboard!")


def create_session_id_element(session_id: str):
    with (
        ui.element("div")
        .classes("fixed bottom-4 left-4 cursor-pointer text-xs hover:underline")
        .on("click", lambda: copy_to_clipboard(session_id))
        .tooltip("Save this to resume later! Keep this secret!")
    ):
        with ui.row().classes("gap-1"):
            ui.icon("content_copy")
            label = ui.label(session_id)
            return label


def get_session() -> tuple[str, str]:
    session_id = app.storage.tab.get(SESSION_ID_KEY, None)
    if not session_id or not session_id:
        session_id = str(uuid4())
        app.storage.tab[SESSION_ID_KEY] = session_id
        ui.notify(f"New session created:{session_id}")
    return session_id



async def handle_connect(client:nicegui.Client):
    await ui.context.client.connected()
    app.storage.tab["client"] = client

async def handle_disconnect(client:nicegui.Client):
    await ui.context.client.connected()
    app.storage.tab.pop("client", None)

app.on_connect(handle_connect)
app.on_disconnect(handle_disconnect)

@ui.page("/session/")
async def session_page():
    await ui.context.client.connected()
    SESSION_ID = get_session()
    CLIENT = app.storage.tab.get(CLIENT_KEY, None)
    backend_conected = await on_startup()  # Ensure backend is ready before rendering the page
    if not backend_conected:
        return
    # Add the CSS to the page
    ui.add_head_html(custom_css)

    #create grid handlers
    grid_handler_1 = GridEventHandler(day=1, session_id=SESSION_ID, client=CLIENT)
    grid_handler_2 = GridEventHandler(day=2, session_id=SESSION_ID, client=CLIENT)
    grid_handler_3 = GridEventHandler(day=3, session_id=SESSION_ID, client=CLIENT)

    #create left drawer
    with (
        ui.left_drawer(value=False)
        .classes("bg-gray-100 shadow-lg p-4")
        .props("width=400") as left_drawer
    ):
        menu_widget = MenuWidget(SESSION_ID, CLIENT)
        menu_widget.create_menu_widget()
        create_session_id_element(SESSION_ID)

        #ui for swapping names
        swap_name_ui = SwapGridNameUI(SESSION_ID, CLIENT)
        swap_name_ui.grid_event_handlers["DAY1"] = grid_handler_1
        swap_name_ui.grid_event_handlers["DAY2"] = grid_handler_2
        swap_name_ui.grid_event_handlers["DAY3"] = grid_handler_3
        await swap_name_ui.create_ui()


        with ui.element("div").classes("fixed bottom-2 right-0 z-50"):
            LeftDrawerToggle(left_drawer,direction="left")
    with ui.element("div").classes(
        "fixed bottom-2 left-4 z-50"
    ): 
        LeftDrawerToggle(left_drawer,direction="right")

    # Control Panel
    control_panel_handler = ControlPanelHandler(session_id=SESSION_ID, client=CLIENT)
    ui.keyboard(on_key=lambda e: handle_key(e, control_panel_handler))
    control_panel = control_panel_handler.create_control_panel()
    ui.separator()
    # Create a single event handler instance for all grids
    container1 = ui.column().classes("w-full gap-1")
    container2 = ui.column().classes("w-full gap-1")
    container3 = ui.row().classes("w-full gap -1")

    with container1:
        await grid_handler_1.generate_grids()
    with container2:
        await grid_handler_2.generate_grids()
    with container3:
        await grid_handler_3.generate_grids()
    hour_grid_handler = HourGridHandler(session_id=SESSION_ID, client=CLIENT)
    with left_drawer:
        await hour_grid_handler.create_hour_grid()

    grid_handler_1.add_hour_grid_handler(hour_grid_handler)
    grid_handler_2.add_hour_grid_handler(hour_grid_handler)
    grid_handler_3.add_hour_grid_handler(hour_grid_handler)
    control_panel_handler.add_grid_event_handler(grid_handler_1)
    control_panel_handler.add_grid_event_handler(grid_handler_2)
    control_panel_handler.add_grid_event_handler(grid_handler_3)
    control_panel_handler.add_hour_grid_handler(hour_grid_handler)

    switch = CompressSwitch()
    with ui.row().classes("fixed right-4 bottom-4"):
        switch.create_switch()
        create_keybinds_button()
        create_help_button()
    switch.add_day_3_grid_handler(grid_handler_3)
    grid_handler_3.add_compress_switch(switch.switch)
