import nicegui
from nicegui import run, ui
import requests
from src.frontend.api.urls_and_keys import ENDPOINTS,API_KEY

class HourGridHandler:
    def __init__(self, session_id: str, client: nicegui.Client):
        self.FETCH_HOUR_DATA_URL = ENDPOINTS["HOUR_DATA"] 
        self.HEADERS = {"X-Session-ID": session_id, "x-api-key": API_KEY}
        self.CLIENT = client
        self.CLIENT.on_disconnect(self._on_disconnect)
        self.CLIENT.on_connect(self._on_connect)
        self.client_connected = True
        self.grid = None

    async def create_hour_grid(self):
        data = await self.fetch_grid_data()
        if data is None:
            return
        self.grid = ui.aggrid(
            {
                "columnDefs": data["columnDefs"],
                "rowData": data["rowData"],
                "pinnedBottomRowData": data["pinned_bottom_row"],
                "domLayout": "autoHeight",
                "defaultColDef": {
                    "resizable": True,
                },
            }
        ).classes("w-full")

    async def fetch_grid_data(self) -> dict | None:
        response = await run.io_bound(
            requests.get, self.FETCH_HOUR_DATA_URL, headers=self.HEADERS
        )
        if not self.client_connected:
            return 
        if response.status_code != 200:
            ui.notify("Fetch hour data failed!", type="negative")
            return
        return response.json()

    async def update_hour_grid(self):
        new_data = await self.fetch_grid_data()
        if new_data is None:
            return
        self.grid.run_grid_method("setGridOption", "columnDefs", new_data["columnDefs"])
        self.grid.run_grid_method("setGridOption", "rowData", new_data["rowData"])
        self.grid.run_grid_method(
            "setGridOption", "pinnedBottomRowData", new_data["pinned_bottom_row"]
        )

    def _on_disconnect(self):
        self.client_connected = False
    def _on_connect(self):
        self.client_connected = True
