# helper.py
from nicegui import ui
from nicegui.events import KeyEventArguments

class GridEventHandler:
    def __init__(self):
        self.left_half = False
        self.right_half = False
        
        # Set up keyboard listener
        self.keyboard = ui.keyboard(on_key=self.handle_key)
    
    def handle_key(self, e: KeyEventArguments):
        """Handle keyboard events to track modifier keys"""
        if e.key in ['arrow_left','a']:
            self.left_half = e.action.keydown
        elif e.key in ['arrow_right','d']:
            self.right_half = e.action.keydown
    
    def handle_cell_click(self, event, grid_name="Grid"):
        """Handle cell click events with modifier key detection"""
        cell_value = event.args['value']
        row_index = event.args['rowIndex']
        
        if self.left_half:
            ui.notify(f"Allocate left half for {cell_value} in {grid_name}")
        elif self.right_half:
            ui.notify(f"Allocate right half for {cell_value} in {grid_name}")
        else:
            ui.notify(f"Regular click on {cell_value} in {grid_name}")
    
    def create_click_handler(self, grid_name="Grid"):
        """Create a click handler for a specific grid"""
        return lambda event: self.handle_cell_click(event, grid_name)
