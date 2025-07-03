from nicegui import ui
from typing import Literal


class LeftDrawerToggle:
    def __init__(self, drawer: ui.left_drawer, direction: Literal["left", "right"]):
        self.drawer = drawer
        self.create_toggle(direction)

    # Bottom-left floating toggle button
    def create_toggle(self, direction: Literal["left", "right"]):
        icons = {"right": "chevron_right", "left": "chevron_left"}

        ui.button(icon=icons[direction], on_click=self.drawer.toggle).classes(
            "w-12 h-10 px-2 py-1 rounded bg-blue-500 text-white shadow-md"
        ).tooltip("Toggle menu")
