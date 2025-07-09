from nicegui import ui

@ui.page("/health")
def health():
    """Health check page."""
    ui.label("OK")
    ui.label("This is a health check endpoint to verify the server is running.")
