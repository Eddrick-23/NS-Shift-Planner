import requests
from nicegui import run, ui
from nicegui.events import KeyEventArguments
from src.frontend.components.hour_grid_handler import HourGridHandler
from src.frontend.api.urls_and_keys import ENDPOINTS


class GridEventHandler:
    def __init__(self, day: int, session_id: str):
        self.FETCH_GRID_DATA_URL = ENDPOINTS["FETCH_GRID"]
        self.FETCH_COMPRESSED_GRID_DATA_URL = ENDPOINTS["FETCH_GRID_COMPRESSED"]
        self.ALLOCATE_SHIFT_URL = ENDPOINTS["ALLOCATE_SHIFT"]
        self.HEADERS = {"X-Session-ID": session_id}
        self.left_half = False
        self.right_half = False
        self.day = day
        self.active_location = "MCC"
        self.clicks_enabled = True
        self.compress_switch = None
        self.grid_compressed = False

        # set up grid instances
        self.MCC_grid = None
        self.HCC1_grid = None
        self.HCC2_grid = None

        # Set up keyboard listener
        self.keyboard = ui.keyboard(on_key=self.handle_key, active=True)

    async def generate_grids(self):
        """
        Creates required grids, called once on class inself.stantiation
        """
        json_data = await self.fetch_grid_data()
        self.MCC_grid = self.create_grid(
            column_defs=json_data[f"DAY{self.day}:MCC"]["columnDefs"],
            row_data=json_data[f"DAY{self.day}:MCC"]["rowData"],
        )
        if self.day == 3:
            return
        self.HCC1_grid = self.create_grid(
            column_defs=json_data[f"DAY{self.day}:HCC1"]["columnDefs"],
            row_data=json_data[f"DAY{self.day}:HCC1"]["rowData"],
        )
        self.HCC2_grid = self.create_grid(
            column_defs=json_data[f"DAY{self.day}:HCC2"]["columnDefs"],
            row_data=json_data[f"DAY{self.day}:HCC2"]["rowData"],
        ).classes("hidden" if not json_data[f"DAY{self.day}:HCC2"]["rowData"] else "")

    def create_grid(self, column_defs: list[dict], row_data: list[dict]):
        """
        Helper function to create an interactive grid

        Args:
            column_defs (list[dict]): column definition from json_response[grid_name]["columnDefs"]
            row_data (list[dict]): row data form json_response[grid_name]["rowData"]
        """
        grid = ui.aggrid(
            {
                "columnDefs": column_defs,
                "rowData": row_data,
            }
        ).classes("w-full")
        self.update_grid_height(grid, row_data)
        grid.on("cellClicked", self.create_click_handler(grid))

        return grid

    def handle_key(self, e: KeyEventArguments):
        """Handle keyboard events to track modifier keys"""
        if e.key in ["arrow_left", "a"]:
            self.left_half = e.action.keydown
        elif e.key in ["arrow_right", "d"]:
            self.right_half = e.action.keydown

    async def handle_cell_click(self, event, grid: ui.aggrid):
        """Handle cell click events with modifier key detection"""
        if not self.clicks_enabled:
            ui.notify("Clicks are disabled")
            return
        if event.args["value"] not in {"0", "MCC", "HCC1", "HCC2"}:
            return
        data = next(iter(event.args["data"].items()))
        target_grid, name = data[0], data[1]
        time_block = event.args["colId"]

        body = {
            "grid_name": target_grid,
            "name": name,
            "location": self.active_location,
            "time_block": time_block,
        }
        # if time_block is :30 --> don't need to consider left or right half we force allocation size 0.75
        # if time_block is :00 --> left half 0.25, right_half 0.75, full 1
        if ":30" in time_block:
            body["allocation_size"] = "0.75"

        else:
            if self.left_half:
                body["allocation_size"] = "0.25"
            elif self.right_half:
                body["allocation_size"] = "0.75"
            else:  # normal click
                second_half_time_block = time_block[:3] + "30"
                # allocate full
                if second_half_time_block not in event.args["data"]:
                    body["allocation_size"] = "1"
                else:
                    body["allocation_size"] = "0.25"
        response = await run.io_bound(
            requests.post, self.ALLOCATE_SHIFT_URL, json=body, headers=self.HEADERS
        )
        await self.update_grids()
        await self.hour_grid_handler.update_hour_grid()
        if response.status_code != 200:
            ui.notify("Internal Server Error when allocating shift")

    async def update_grids(self):
        """
        fetch updated grid data and updates the aggrids
        """
        new_data = await self.fetch_grid_data()
        self.clicks_enabled = True
        if self.compress_switch is not None:
            self.compress_switch.set_value(False)

        if self.MCC_grid is not None:
            column_defs, row_data = (
                new_data[f"DAY{self.day}:MCC"]["columnDefs"],
                new_data[f"DAY{self.day}:MCC"]["rowData"],
            )
            self.MCC_grid.run_grid_method("setGridOption", "columnDefs", column_defs)
            self.MCC_grid.run_grid_method("setGridOption", "rowData", row_data)
            self.update_grid_height(self.MCC_grid, row_data)

        if self.HCC1_grid is not None:
            column_defs, row_data = (
                new_data[f"DAY{self.day}:HCC1"]["columnDefs"],
                new_data[f"DAY{self.day}:HCC1"]["rowData"],
            )
            self.HCC1_grid.run_grid_method("setGridOption", "columnDefs", column_defs)
            self.HCC1_grid.run_grid_method("setGridOption", "rowData", row_data)
            self.update_grid_height(self.HCC1_grid, row_data)
        if self.HCC2_grid is not None:
            column_defs, row_data = (
                new_data[f"DAY{self.day}:HCC2"]["columnDefs"],
                new_data[f"DAY{self.day}:HCC2"]["rowData"],
            )
            self.HCC2_grid.run_grid_method("setGridOption", "columnDefs", column_defs)
            self.HCC2_grid.run_grid_method("setGridOption", "rowData", row_data)
            if len(row_data) > 0:
                self.HCC2_grid.classes(remove="hidden")
            else:
                self.HCC2_grid.classes(add="hidden")
            self.update_grid_height(self.HCC2_grid, row_data)

    def create_click_handler(self, grid: ui.aggrid):
        """Create a click handler for a specific grid"""
        return lambda event: self.handle_cell_click(event, grid)

    async def fetch_grid_data(self):
        """Fetch grid data from FastAPI backend"""

        day = self.day

        response = await run.io_bound(
            requests.post,
            self.FETCH_GRID_DATA_URL,
            json={"day": day},
            headers=self.HEADERS,
        )
        if response.status_code != 200:
            ui.notify(f"Fetch grid data for day{day} failed.")
        return response.json()

    def update_grid_height(self, grid: ui.aggrid, row_data: list[dict],extra_rows:int=0,default_height:int=4):
        """
        Set new grid height

        Args:
            grid (ui.aggrid): aggrid instance to update
            row_data (list[dict]): updated row data for the grid
            extra_rows (int): force add extra rows(Used for compressed_grid height adjustment)
            default_height (int): Default height in rem
        """

        # compute height based on row_data
        num_rows = len(row_data) + extra_rows
        calculated_rem_height = default_height + 1.75 * (max(0, num_rows - 1))
        # update style
        grid.style(f"height: {calculated_rem_height}rem")

    def add_hour_grid_handler(self, handler: HourGridHandler):
        """
        Add hour grid handler to this grid event handler
        - Events that occur to this grid will trigger an update on the hour grid
        """
        self.hour_grid_handler = handler

    def add_compress_switch(self, switch: ui.switch):
        """
        Add switch handler to this grid
        """
        self.compress_switch = switch

    async def compress_grid(self):
        """
        Change grid to compressed format
        - Grid will not be editable in this state
        - This is meant for day 3 grid only
        - To be called by compress_grid_switch component
        """
        body = {"day": 3}
        response = await run.io_bound(
            requests.post,
            url=self.FETCH_COMPRESSED_GRID_DATA_URL,
            json=body,
            headers=self.HEADERS,
        )
        if response.status_code != 200:
            ui.notify("Error in getting compressed grid data", type="negative")
        data = response.json()
        column_defs = data["columnDefs"]
        row_data = data["rowData"]
        self.MCC_grid.run_grid_method("setGridOption", "columnDefs", column_defs)
        self.MCC_grid.run_grid_method("setGridOption", "rowData", row_data)
        self.update_grid_height(self.MCC_grid, row_data,default_height=6)
        self.grid_compressed = True
