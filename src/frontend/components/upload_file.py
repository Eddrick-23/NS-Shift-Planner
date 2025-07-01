from nicegui import ui, run
from nicegui import events
import asyncio
import requests

UPLOAD_FILE_URL = "http://localhost:8000/upload/"


async def handle_rejected_file(message: str | None = None):
    """
    Handle rejected file on upload
    """
    if message is None:
        message = "Invalid file type"
    notification = ui.notification(
        timeout=None, position="center", type="warning", message=message
    )
    await asyncio.sleep(3)
    notification.dismiss()


async def handle_on_upload(e: events.UploadEventArguments, dialog: ui.dialog):
    uploaded_contents = e.content.read()
    response = await run.io_bound(
        requests.post,
        url=UPLOAD_FILE_URL,
        data=uploaded_contents,
        headers={"Content-Type": "application/octet-stream"},
    )
    if response.status_code == 200:
        dialog.close()
        ui.run_javascript('location.reload();') #reload the page 
    else:
        await handle_rejected_file(message=response.json()["detail"])


def handle_upload_click():
    with ui.dialog() as dialog:
        with ui.card():
            ui.label("Select or drag & drop a .zip file").style(
                "color: grey; text-align: center; width: 100%; margin-top: 8px;"
            )
            ui.label("Current work will be overriden").style(
                "text-align: center; width: 100%;"
            ).tailwind.text_color("red-600").font_weight("bold")
            ui.upload(
                max_files=1,
                on_upload=lambda e: handle_on_upload(e, dialog),
                on_rejected=handle_rejected_file,
            ).props("accept=.zip")
    dialog.classes("Clearable")
    dialog.open()


def create_upload_button():
    ui.element("q-fab-action").props("icon=upload color=teal-8").tooltip("Upload").on(
        "click", handle_upload_click
    )
