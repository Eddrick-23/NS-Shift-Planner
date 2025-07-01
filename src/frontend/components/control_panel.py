from nicegui import run, ui
import requests
from typing import Literal
from src.frontend.components.grid_event_handler import GridEventHandler
from src.frontend.components.hour_grid_handler import HourGridHandler
from src.frontend.components.upload_file import UploadUI
import asyncio


class ControlPanelHandler:
    INVALID_NAMES = ["MCC", "HCC1", "HCC2", "0", "TOTAL"]

    def __init__(self, session_id: str):
        self.radio_value = "MCC"
        self.radio_options = ["MCC", "HCC1", "HCC2"]
        self.TIMEOUT = 10
        self.ADD_NAME_URL = "http://localhost:8000/grid/add/"
        self.REMOVE_NAME_URL = "http://localhost:8000/grid/remove/"
        self.DOWNLOAD_URL = "http://localhost:8000/download/"
        self.RESET_URL = "http://localhost:8000/reset-all/"
        self.HEADERS = {"X-Session-ID": session_id}
        # Store references to UI elements
        self.grid_option = None
        self.name_input = None
        self.radio_group = None
        # Store GridEventHandler instances
        self.grid_event_handlers = []

    def create_control_panel(self):
        """
        Create control panel UI on the front end
        """
        control_panel = ui.grid(columns=5).classes("w-full")
        with control_panel:
            with ui.element("q-fab").props("icon=menu direction=down"):
                ui.element("q-fab-action").props("icon=book color=teal-8").tooltip(
                    "Read Me"
                ).on("click", lambda: self.handle_read_me_redirect())
                UploadUI(headers=self.HEADERS)
                ui.element("q-fab-action").props("icon=download color=teal-8").tooltip(
                    "Download"
                ).on("click", self.handle_download)
                ui.element("q-fab-action").props(
                    "icon=restart_alt color=red-8"
                ).tooltip("Reset").on("click", self.handle_reset)

            grid_options = {
                "DAY1:MCC": "DAY1:MCC",
                "DAY1:HCC1": "DAY1:HCC1",
                "DAY1:HCC2": "DAY1:HCC2",
                "DAY2:MCC": "DAY2:MCC",
                "DAY2:HCC1": "DAY2:HCC1",
                "DAY2:HCC2": "DAY2:HCC2",
                "DAY3:MCC": "NIGHT DUTY",
            }

            # Store references to UI elements
            self.grid_option = ui.select(
                label="Grid",
                options=grid_options,
                clearable=True,
            ).props("outlined")
            self.name_input = (
                ui.input(label="Name").props("clearable").classes("flex-1")
            ).props("outlined")

            with ui.button_group():
                ui.button(icon="add", on_click=self.handle_add).classes(
                    "flex-1"
                ).tooltip("Add to grid")
                ui.button(icon="remove", on_click=self.handle_remove).classes(
                    "flex-1"
                ).tooltip("Remove from grid")

            self.radio_group = (
                ui.radio(options=self.radio_options, value=self.radio_value)
                .props("inline size=lg")
                .on_value_change(
                    lambda: self.set_grid_event_handler_location(self.radio_group.value)
                )
            )
            with ui.teleport(
                f"#{self.radio_group.html_id} > div:nth-child(1) .q-radio__label"
            ):
                ui.tooltip("Shift + 1")
            with ui.teleport(
                f"#{self.radio_group.html_id} > div:nth-child(2) .q-radio__label"
            ):
                ui.tooltip("Shift + 2")
            with ui.teleport(
                f"#{self.radio_group.html_id} > div:nth-child(3) .q-radio__label"
            ):
                ui.tooltip("Shift + 3")

        return control_panel

    def add_grid_event_handler(self, grid_event_handler: GridEventHandler):
        """
        Add a grid_event_handler instance so that control panel actions can update grids automatically
        """
        self.grid_event_handlers.append(grid_event_handler)

    def add_hour_grid_handler(self, hour_grid_handler: HourGridHandler):
        """
        Add a hour_grid_handler instance so that control panel actions can update the hour grid automatically
        """
        self.hour_grid_handler = hour_grid_handler

    async def trigger_handler_update(self, target_grid: str):
        """
        Update the target grid specified to render changes on frontend.<br>
        This method searches for the GridEventHandler containing the target grid, then updates the grid.

        Args:
            target_grid (str): The grid to update
        """
        target_day = 0
        if "DAY1" in target_grid:
            target_day = 1
        elif "DAY2" in target_grid:
            target_day = 2
        else:  # NIGHT DUTY
            target_day = 3

        await self.hour_grid_handler.update_hour_grid()
        # get target handler
        for grid_event_handler in self.grid_event_handlers:
            if grid_event_handler.day == target_day:
                await grid_event_handler.update_grids()
                return

    def set_radio_value(self, value: Literal["MCC", "HCC1", "HCC2"]):
        """
        Set radio button value. Mainly called for hot keys
        """
        self.radio_group.value = value
        self.radio_group.update()

    def set_grid_event_handler_location(self, location: Literal["MCC", "HCC1", "HCC2"]):
        """
        Set the grid event handlers active location
        """
        for grid_event_handler in self.grid_event_handlers:
            grid_event_handler.active_location = location

    async def handle_add(self):
        """
        add name to specified grid
        """
        name = self.name_input.value.strip().upper()
        target_grid = self.grid_option.value
        if name == "":
            ui.notify("Enter a name")
            return
        if name in self.INVALID_NAMES:
            ui.notify("Invalid name")
            return
        if target_grid is None:
            ui.notify("Select a grid")
            return
        body = {"grid_name": target_grid, "name": name}
        response = await run.io_bound(
            requests.post, self.ADD_NAME_URL, json=body, headers=self.HEADERS
        )
        await self.trigger_handler_update(target_grid)
        ui.notify(response.json()["detail"])

    async def reload_all_grids(self):
        """
        update all grid event handlers and hour_grid_handler. <br>
        This method is normally called after a full page reload to make sure all displayed data is up to date
        """
        tasks = [
            self.trigger_handler_update("DAY1"),
            self.trigger_handler_update("DAY2"),
            self.trigger_handler_update("DAY3"),
            self.hour_grid_handler.update_hour_grid(),
        ]

        await asyncio.gather(*tasks)

    async def handle_remove(self):
        """
        remove name from specified grid
        """
        name = self.name_input.value.strip()
        target_grid = self.grid_option.value
        if name == "":
            ui.notify("Enter a name")
            return
        if target_grid is None:
            ui.notify("Select a grid")
            return
        body = {"grid_name": target_grid, "name": name}
        response = await run.io_bound(
            requests.delete, self.REMOVE_NAME_URL, json=body, headers=self.HEADERS
        )
        await self.trigger_handler_update(target_grid)
        ui.notify(response.json()["detail"])

    def handle_read_me_redirect(self):
        ui.navigate.to("https://github.com/Eddrick-23/NS-Shift-Planner", new_tab=True)

    async def handle_download(self):
        response = await run.io_bound(
            requests.post, self.DOWNLOAD_URL, headers=self.HEADERS
        )
        if response.status_code != 200:
            ui.notify("Error in exporting project", type="negative")
            return
        ui.download.content(response.content, "planning.zip")

    async def handle_reset(self):
        async def handle_reset_confirm():
            response = await run.io_bound(
                requests.delete, self.RESET_URL, headers=self.HEADERS
            )
            if response.status_code != 200:
                ui.notify("Reset error occured", type="negative")
                return
            ui.run_javascript("location.reload();")

        with ui.dialog() as dialog:
            with ui.card():
                ui.label("Reset All").style(
                    "text-align: center; width: 100%; font-size: large"
                )
                ui.label("This action is irreversible!").style(
                    "text-align: center; width: 100%;"
                ).tailwind.text_color("red-600").font_weight("bold")
                with ui.row():
                    ui.button("Cancel").props("color=red").on_click(
                        lambda: dialog.close()
                    )
                    ui.button("Confirm").on_click(handle_reset_confirm)

        dialog.open()


# Usage example:
# handler = ControlPanelHandler()
# control_panel = handler.create_control_panel()
