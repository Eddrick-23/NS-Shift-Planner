
import uuid
from nicegui import ui, app
from fastapi import HTTPException
from typing import Dict, Set

@ui.page("/")
async def landing_page():
    """Landing page for creating or joining sessions"""
    ui.add_head_html("""
        <style>
            .landing-container {
                max-width: 500px;
                margin: 0 auto;
                padding: 2rem;
            }
            .session-card {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                padding: 2rem;
                margin: 1rem 0;
            }
        </style>
    """)
    
    with ui.column().classes("landing-container"):
        ui.label("Welcome").classes("text-3xl font-bold")
        
        # New Session Card
        with ui.card().classes("session-card"):
            ui.label("Start New Session").classes("text-xl font-semibold mb-4")
            ui.label("Create a fresh session with a new workspace").classes("text-gray-600 mb-4")
            
            async def create_new_session():
                pass
                # ui.open(f"/session/{session_id}")
            
            ui.button("Create New Session", on_click=create_new_session).classes(
                "w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded"
            )
        
        # Join Existing Session Card
        with ui.card().classes("session-card"):
            ui.label("Join With Session ID").classes("text-xl font-semibold mb-4")
            ui.label("Enter your session ID to continue where you left off").classes("text-gray-600 mb-4")
            
            session_input = ui.input(
                label="Session ID", 
                placeholder="Enter session ID..."
            ).classes("w-full mb-4")
            
            error_label = ui.label("").classes("text-red-500 text-sm")
            error_label.visible = False

ui.run()
