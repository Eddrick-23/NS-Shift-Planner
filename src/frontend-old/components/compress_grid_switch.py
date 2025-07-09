from nicegui import ui
from src.frontend.components.grid_event_handler import GridEventHandler

class CompressSwitch():
    def __init__(self):
        self.day_3_grid_handler = None
        self.switch = None
    
    def add_day_3_grid_handler(self,handler:GridEventHandler):
        self.day_3_grid_handler = handler
    
    def create_switch(self):
        self.switch = ui.switch(on_change=self.handle_switch_change).tooltip("Compress Night Duty Grid").props("size=lg")

    async def handle_switch_change(self):
        if self.switch.value:
            self.day_3_grid_handler.clicks_enabled = False
            await self.day_3_grid_handler.compress_grid()
        else:
            if self.day_3_grid_handler.grid_compressed:
                await self.day_3_grid_handler.update_grids()
