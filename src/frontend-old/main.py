from nicegui import ui
import src.frontend.routes.landing
import src.frontend.routes.session
import src.frontend.routes.health
from src.frontend.config import config

ui.run(reload=(config.ENVIRONMENT == "DEV"), port=config.PORT, title="NS Shift Planner", native=False)
