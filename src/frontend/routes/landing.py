from nicegui import ui

@ui.page('/')
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

    with ui.element('div').classes('flex w-full h-screen'):
        # Left half
        with ui.element('div').classes('w-1/2 flex flex-col items-center pt-20'):
            ui.label('Welcome').classes('text-4xl font-bold')
            # Animated logos
             # Fixed bottom-left container for logos + text
            with ui.element('div').classes('fixed bottom-0 left-0 p-4 bg-white bg-opacity-90'):
                    with ui.row().classes('gap-'):
                        ui.label('Built using').classes('mt-2 text-gray-700')
                        with ui.link('', target='https://nicegui.io',new_tab=True).tooltip("Because I don't want to deal with JS :)"):
                            ui.image('src/frontend/assets/nicegui-seeklogo.svg').classes('w-6')
                        with ui.link('', target='https://fastapi.tiangolo.com/',new_tab=True):
                            ui.image('src/frontend/assets/fastapilogo.svg').classes('w-6 h-6')
                        with ui.link('', target='https://firebase.google.com/',new_tab=True):
                            ui.image('src/frontend/assets/Logomark_Full Color.svg').classes('w-6 h-6')

        # Right half
        with ui.element('div').classes('w-1/2 flex items-center justify-center bg-gray-100'):
            with ui.column().classes('w-full max-h-full overflow-hidden ml-4 mr-4'):
                with ui.card(align_items='center').classes("flex w-full"):
                    ui.label("Start New Session").classes("text-xl font-semibold mb-4")
                    ui.label("Create a fresh session with a new workspace").classes("text-gray-600 mb-4")

                    async def create_new_session():
                        pass

                    ui.button("Create New Session", on_click=create_new_session).classes(
                        "w-1/2 text-white font-medium py-2 px-4 rounded"
                    )
                with ui.card(align_items='center').classes("flex w-full"):
                    ui.label("Join With Session ID").classes("text-xl font-semibold mb-4")
                    ui.label("Enter your session ID to continue where you left off").classes("text-gray-600 mb-4")
                    
                    session_input = ui.input(
                        label="Session ID", 
                        placeholder="Enter session ID..."
                    ).classes("w-1/2 mb-4")

ui.run()
