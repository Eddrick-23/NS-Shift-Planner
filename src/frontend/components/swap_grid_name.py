import asyncio
import requests
from nicegui import ui,run
from src.frontend.components.grid_event_handler import GridEventHandler
from src.frontend.api.urls_and_keys import ENDPOINTS,API_KEY

class SwapGridNameUI:
    GRID_OPTIONS = [
        "DAY1:MCC",
        "DAY1:HCC1",
        "DAY1:HCC2",
        "DAY2:MCC",
        "DAY2:HCC1",
        "DAY2:HCC2",
        "DAY3:MCC",
    ]

    def __init__(self,session_id:str):
        self.HEADERS = {"X-Session-ID": session_id, "x-api-key":API_KEY}
        self.grid_event_handlers = {}
        self.available_names = []

    async def create_ui(self):
        with ui.row().classes("w-full"):
            self.grid_select = ui.select(
                options=self.GRID_OPTIONS,
                label="Select grid",
                clearable=True,
            ).classes("flex-1")

            self.name_select = ui.select(
                options=self.available_names,
                multiple=True,
                clearable=True,
                label="Choose name",
                on_change=self.handle_name_select,
            ).classes("flex-1")
            self.name_select.on(
                "click", lambda: self.set_available_names(self.grid_select.value)
            )
            self.name_select.bind_enabled_from(self.grid_select,'value',lambda x: x is not None)

        self.swap_button = (
            ui.button("Swap", icon="compare_arrows",on_click=lambda : self.handle_swap_click(self.name_select.value,self.grid_select.value))
            .classes("w-full")
            .bind_enabled_from(
                self.name_select,
                'value',
                lambda x: len(x) == 2 if x else False,
            )
        )

    async def set_available_names(self, grid: str | None):
        """
        Sets the avaliable names for the name select ui

        Args:
            grid(str|None): the target grid from self.grid_select or None if self.grid_select is empty
        """
        key = grid[:4]
        grid_location = grid.split(":")[1]
        grid_event_handler: GridEventHandler = self.grid_event_handlers.get(key, None)
        if grid_event_handler is None:
            ui.notify("Could not find grid event handler", type="negative")
            return
        names = grid_event_handler.names[grid_location]
        self.name_select.set_options(names)

    def handle_name_select(self, e):
        if len(e.value) >= 2:
            # Keep only the first 2 selections
            e.sender.value = e.value[:2]
            # Close the select dropdown
            e.sender.run_method("hidePopup")
    
    async def handle_swap_click(self,names:list[str],target_grid:str):
        body = {
            "names":names,
            "grid_name":target_grid
        }
        response = await run.io_bound(requests.post, ENDPOINTS["SWAP_NAMES"], json=body,headers=self.HEADERS)

        if response.status_code != 200:
            ui.notify("Swap failed due to internal server error!", type="negative")
            return
        
        #successful swap update grids
        key = target_grid[:4]
        grid_event_handler:GridEventHandler = self.grid_event_handlers[key]
        await asyncio.gather(
            grid_event_handler.update_grids(),
            grid_event_handler.hour_grid_handler.update_hour_grid()
        )

