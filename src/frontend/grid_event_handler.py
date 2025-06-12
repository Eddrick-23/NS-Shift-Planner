import requests
from nicegui import run, ui
from nicegui.events import KeyEventArguments


class GridEventHandler:
    def __init__(self, day: int):
        self.FETCH_GRID_DATA_URL = "http://localhost:8000/grid/"
        self.ALLOCATE_SHIFT_URL = "http://localhost:8000/grid/allocate/"
        self.left_half = False
        self.right_half = False
        self.day = day
        self.active_location = "MCC"

        # set up grid instances
        self.MCC_grid = None
        self.HCC1_grid = None
        self.HCC2_grid = None

        # Set up keyboard listener
        self.keyboard = ui.keyboard(on_key=self.handle_key, active=True)

    async def generate_grids(self):
        """
        Creates required grids, called once on class instantiation
        """
        json_data = await self.fetch_grid_data()
        self.MCC_grid = self.create_grid(
            column_defs=json_data["DAY1:MCC"]["columnDefs"],
            row_data=json_data["DAY1:MCC"]["rowData"],
        )
        self.HCC1_grid = self.create_grid(
            column_defs=json_data["DAY1:HCC1"]["columnDefs"],
            row_data=json_data["DAY1:HCC1"]["rowData"],
        )
        self.HCC2_grid = self.create_grid(
            column_defs=json_data["DAY1:HCC2"]["columnDefs"],
            row_data=json_data["DAY1:HCC2"]["rowData"],
        )

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
        #if time_block is :30 --> don't need to consider left or right half we force allocation size 0.75
        #if time_block is :00 --> left half 0.25, right_half 0.75, full 1
        if ":30" in time_block:
            body["allocation_size"] = "0.75"

        else:
            if self.left_half:
                body["allocation_size"] = "0.25"
            elif self.right_half:
                body["allocation_size"] = "0.75"
            else: #normal click
                second_half_time_block = time_block[:3] + "30"
                #allocate full
                if second_half_time_block not in event.args["data"]:
                    body["allocation_size"] = "1"
                else:
                    body["allocation_size"] = "0.25"
        response = await run.io_bound(requests.post,self.ALLOCATE_SHIFT_URL, json=body)
        await self.update_grids()
        if response.status_code != 200:
            ui.notify("Internal Server Error when allocating shift")

    async def update_grids(self):
        """
        fetch updated grid data and updates the aggrids
        """

        new_data = await self.fetch_grid_data()

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
            self.HCC2_grid.run_grid_method(
                "setGridOption", "columnDefs", new_data["DAY1:HCC2"]["columnDefs"]
            )
            self.HCC2_grid.run_grid_method(
                "setGridOption", "rowData", new_data["DAY1:HCC2"]["rowData"]
            )
            self.update_grid_height(self.HCC2_grid, row_data)

    def create_click_handler(self, grid: ui.aggrid):
        """Create a click handler for a specific grid"""
        return lambda event: self.handle_cell_click(event, grid)

    async def fetch_grid_data(self):
        """Fetch grid data from FastAPI backend"""

        day = self.day

        response = await run.io_bound(
            requests.post, self.FETCH_GRID_DATA_URL, json={"day": day}
        )
        if response.status_code != 200:
            ui.notify(f"Fetch grid data for day{day} failed.")
        return response.json()

    def update_grid_height(self, grid: ui.aggrid, row_data: list[dict]):
        """
        Set new grid height

        Args:
            grid (ui.aggrid): aggrid instance to update
            row_data (list[dict]): updated row data for the grid
        """

        # compute height based on row_data
        num_rows = len(row_data)
        calculated_rem_height = 4 + 1.75 * (max(0, num_rows - 1))
        # update style
        grid.style(f"height: {calculated_rem_height}rem")
