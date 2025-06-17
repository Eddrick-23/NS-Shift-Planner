from nicegui import ui,run
import asyncio


async def handle_upload(dialog:ui.dialog):
    """
    Send uploaded file to api
    """
    ui.notify("upload file!")

    dialog.close()

async def handle_rejected_file():
    notification = ui.notification(timeout=None,position="center",type="warning",message="Invalid file type")
    await asyncio.sleep(1.5)
    notification.dismiss()

def handle_upload_click():
    with ui.dialog() as dialog:
        with ui.card():
            ui.label("Select or drag & drop a .zip file").style(
                "color: grey; text-align: center; width: 100%; margin-top: 8px;"
            )
            ui.label("Current work will be overriden").style(
                "text-align: center; width: 100%;"
            ).tailwind.text_color("red-600").font_weight("bold")
            ui.upload(max_files=1, on_rejected=handle_rejected_file).props("accept=.zip")
            with ui.row().classes("w-full"):
                ui.button(icon="cancel",on_click=lambda:dialog.close()).classes("flex-1").tooltip("Close").props("color=red")
                ui.button(icon="upload",on_click=lambda:handle_upload(dialog)).classes("flex-1").tooltip("Upload")
    dialog.open()


def create_upload_button():
    ui.element("q-fab-action").props("icon=upload color=teal-8").tooltip(
                    "Upload"
                ).on("click", handle_upload_click)
