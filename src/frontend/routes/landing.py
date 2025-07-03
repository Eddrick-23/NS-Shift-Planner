import requests
from nicegui import ui, app, run
from src.frontend.styles.css import custom_css
from src.frontend.config import config

SESSION_EXISTS_URL = f"http://{config.HOST_NAME}:{config.BACKEND_PORT}/session_exists/"
SOURCE_CODE_URL = "https://github.com/Eddrick-23/NS-Shift-Planner"
SESSION_ID_KEY = "session_id"


def built_with_component():
    with ui.element("div").classes("fixed bottom-0 left-0 p-4 bg-white bg-opacity-90"):
        with ui.row().classes("gap-"):
            ui.label("Built using").classes("mt-1 text-gray-700")
            with ui.link("", target="https://nicegui.io", new_tab=True).tooltip(
                "Because I don't want to deal with JS :)"
            ):
                image = ui.image("src/frontend/assets/nicegui-seeklogo.svg").classes(
                    "w-6"
                )
                image.classes(
                    "bounce-hover transition-all duration-300 ease-in-out rounded-xl"
                )
            with ui.link("", target="https://fastapi.tiangolo.com/", new_tab=True):
                image = ui.image("src/frontend/assets/fastapilogo.svg").classes(
                    "w-6 h-6 mt-0.5"
                )
                image.classes(
                    "bounce-hover transition-all duration-300 ease-in-out rounded-xl"
                )
            with ui.link("", target="https://firebase.google.com/", new_tab=True):
                image = ui.image("src/frontend/assets/Logomark_Full Color.svg").classes(
                    "w-6 h-6 mt-0.5"
                )
                image.classes(
                    "bounce-hover transition-all duration-300 ease-in-out rounded-xl"
                )


async def handle_new_session():
    app.storage.tab.clear()
    ui.navigate.to("/session/", new_tab=True)


async def handle_resume_session(session_id: str):
    if session_id == "":
        ui.notify("Enter a session id", type="negative")
        return
    # ui.notify(session_id)
    response = await run.io_bound(
        requests.get, SESSION_EXISTS_URL, params={"session_id": session_id}
    )
    if response.status_code != 200:
        ui.notify("Error in validating session ID", type="negative")
        return
    jresponse: dict = response.json()
    if jresponse.get("exists", False):
        app.storage.tab[SESSION_ID_KEY] = session_id
        ui.navigate.to("/session/", new_tab=True)
    else:
        ui.notify("Invalid session id", type="negative")


@ui.page("/")
def landing():
    # Prevent scrolling by injecting CSS into <head>
    ui.add_head_html("""
    <style>
      html, body {
        overflow: hidden;
        height: 100%;
      }
    </style>
    """)
    ui.add_css(custom_css)

    with ui.element("div").classes("flex w-full h-screen"):
        # Left half
        with ui.element("div").classes("w-1/2 flex flex-col items-center pt-20"):
            with ui.row():
                ui.image("src/frontend/assets/Animation - 1751512589860.gif").classes(
                    "w-10 h-10"
                )
                ui.label("Welcome").classes("text-4xl font-bold")
            with ui.element("div").classes("w-full h-[500px] mb-20 mt-20"):
                with ui.splitter(value=35).classes('w-full h-full') as splitter:
                    with splitter.before:
                        with ui.tabs().props('vertical').classes('w-full h-full') as tabs:
                            version = ui.tab('Version Logs', icon='commit')
                            features = ui.tab('Features', icon='star')
                            tips = ui.tab('Pro tips', icon='lightbulb')
                    with splitter.after:
                        with ui.tab_panels(tabs, value=version) \
                                .props('vertical').classes('w-full h-full'):
                            with ui.tab_panel(version):
                                title = ui.label(f'Version {config.VERSION}').classes('text-h4 hover:underline').tooltip("Click to see source code")
                                title.on("click", lambda: ui.navigate.to(SOURCE_CODE_URL,new_tab=True))
                                ui.label('version content')
                            with ui.tab_panel(features):
                                ui.label('star').classes('text-h4')
                                ui.label('Content of features')
                            with ui.tab_panel(tips):
                                ui.label('lightbulb').classes('text-h4')
                                ui.label('Content of tips')
                # Fixed bottom-left container for logos + text
            built_with_component()

        # Right half
        with ui.element("div").classes("w-1/2 flex items-center justify-center"):
            with ui.column().classes("w-full h-screen max-h-full overflow-hidden p-4"):
                with ui.card(align_items="center") as card:
                    card.classes("flex w-full flex-col h-full p-3")  # adjust size
                    card.classes(
                        "bounce-hover transition-all duration-300 ease-in-out rounded-xl"
                    )  # hover animation
                    ui.label("Start New Session").classes(
                        "text-xl font-semibold mb-4 mt-4"
                    )
                    ui.label("Create a fresh session with a new workspace").classes(
                        "text-gray-600 mb-4"
                    )

                    ui.button(
                        "Create New Session", on_click=handle_new_session
                    ).classes("w-1/2 text-white font-medium py-2 px-4 rounded")
                with ui.card(align_items="center") as card:
                    card.classes("flex w-full flex-col h-full p-3 mb-6")  # adjust size
                    card.classes(
                        "bounce-hover transition-all duration-300 ease-in-out rounded-xl"
                    )  # hover animation
                    ui.label("Resume With Session ID").classes(
                        "text-xl font-semibold mb-4 mt-4"
                    )
                    ui.label(
                        "Enter your session ID to continue where you left off"
                    ).classes("text-gray-600 mb-4")

                    session_input = ui.input(
                        label="Session ID", placeholder="Enter session ID..."
                    ).classes("w-1/2 mb-4")
                    ui.button(
                        text="Resume",
                        on_click=lambda: handle_resume_session(session_input.value),
                    ).classes("w-1/2")


ui.run()
