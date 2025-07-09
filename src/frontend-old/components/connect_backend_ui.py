from nicegui import ui
import httpx
import asyncio
from src.frontend.api.urls_and_keys import ENDPOINTS
from src.frontend.config import config

async def on_startup():
    """
    This function is called when the application starts.
    Pings backend to ensure it is running and ready.
    Then closes the card that shows the loading state.
    """
    with ui.card().classes("w-full h-[95vh] mt-2 items-center justify-center") as loading_card:
        spinner = ui.spinner(type="Grid",size="xl")
        ui.label("Connecting to backend, please wait...").classes("text-lg")
        ui.label("This may take awhile if the backend is cold starting.").classes("text-lg")
        linear_progress = ui.linear_progress(size="lg", show_value=False).classes("w-1/2")

    attempts = 0
    max_attempts = 15
    connected_to_backend = False
    async with httpx.AsyncClient(timeout=1) as client:
        while attempts <= max_attempts:
            linear_progress.value = attempts / max_attempts
            try:
                response = await client.get(
                    ENDPOINTS["HEALTH"],
                    headers={"x-api-key": config.API_KEY},
                )
                if response.status_code == 200:
                    linear_progress.value = 1.0
                    linear_progress.props("color=green")
                    spinner.props("color=green")
                    await asyncio.sleep(0.5)  # Let UI update
                    loading_card.delete()
                    connected_to_backend = True
                    break
                else:
                    attempts += 1  # <-- retry on non-200
            except httpx.RequestError as e:
                attempts += 1  # <-- retry on request error

            if attempts > max_attempts:
                with loading_card:
                    linear_progress.props("color=red")
                    spinner.props("color=red")
                    ui.label("Failed to connect to backend after multiple attempts").classes("text-red-500")
                    ui.label("Refresh the page to try again").classes("text-red-500")
                break
            await asyncio.sleep(4)


    return connected_to_backend
