from nicegui import ui, run
import requests
from src.frontend.components.upload_file import UploadUI
from src.frontend.api.urls_and_keys import ENDPOINTS,SOURCE_CODE_URL,API_KEY


class MenuWidget:
    def __init__(self, session_id):
        self.HEADERS = {"X-Session-ID": session_id, "x-api-key":API_KEY}
        self.DOWNLOAD_URL = ENDPOINTS["DOWNLOAD"]
        self.RESET_URL = ENDPOINTS["RESET"]
        self.SOURCE_CODE_URL = SOURCE_CODE_URL

    def create_menu_widget(self):
        with ui.element("q-fab").props("icon=menu direction=down").classes("w-full"):
            ui.element("q-fab-action").props("icon=home color=teal-8").tooltip("Home page").on("click", lambda: ui.navigate.to("/", new_tab=True))
            ui.element("q-fab-action").props("icon=code color=teal-8").tooltip(
                "Source Code"
            ).on("click", lambda: self.handle_read_me_redirect())
            UploadUI(headers=self.HEADERS)
            ui.element("q-fab-action").props("icon=download color=teal-8").tooltip(
                "Download"
            ).on("click", self.handle_download)
            ui.element("q-fab-action").props("icon=restart_alt color=red-8").tooltip(
                "Reset"
            ).on("click", self.handle_reset)

    def handle_read_me_redirect(self):
        ui.navigate.to(self.SOURCE_CODE_URL, new_tab=True)

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
