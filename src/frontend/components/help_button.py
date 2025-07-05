from nicegui import ui


def create_help_button():
    with ui.dialog() as popup, ui.card():
        ui.markdown("""
        ## ❓ Frequently Asked Questions

        ---

        ### 1) How do I add or remove names?

        To modify a grid, follow these steps:

        1. Select the grid in the dropdown
        2. Type the name to add in the text box.(It will be formatted to upper case)
        3. Click the **+ / -** button

        ---

        ### 2) How do I allocate a shift?

        To allocate a shift:

        - Select the location in the radio button on the top right
        - Click on the cell box
        - Use __'a' + left click__ to allocate the __first__ 30 mins
        - Use __'d' + left click__ to allocate the __last__ 30 mins

        _Pro Tip: Use **Shift + [1,2,3]** to quickly set the location._

        ---

        ### 3) Where is the HCC2 Grid?
        
        The HCC2 grid is automatically hidden when the grid is empty. <br>
        It will be displayed when a name is allocated to it.

        ---

        ### 4) How do I save my work?

        Your changes are automatically saved periodically, just log back on with your session id.

        To manually save:

        1. Open the sidebar and click on the menu bar on the top left.
        2. Click the download button to download your project as a ZIP file.

        ---

        ### 5) How do I upload my work?

        To upload:

        1. Open the sidebar and click on the menu bar on the top left.
        2. Drag and drop or upload your ZIP file.
        3. Click the upload icon on the top right of the widget.

        _Once uploaded, your data will be processed and saved to your current session._
                    
                       
                    


                    

        ---
                    
        ### 6) I cannot edit the Night Duty Grid when it is compressed
        - Cell clicks are disabled in compressed view
        - Switch back to the regular view to edit the grid
        """).classes("text-sm text-gray-800")

    ui.button(icon="help", on_click=popup.open).props("fab")


def create_keybinds_button():
    with ui.dialog() as popup, ui.card():
        ui.markdown("""
        ### ⌨️ Keybinds
        
        #### Radio Button
        - **Shift + 1** \u2192 Select **MCC**
        - **Shift + 2** \u2192 Select **HCC1**
        - **Shift + 3** \u2192 Select **HCC2**
        
        #### Shift Selection
        - **a + left click**  \u2192 Allocate first 30min, E.g. 0800 - 0830
        - **d + left click**  \u2192 Allocate last 30min, E.g. 0830 - 0900

                """).classes("text-sm text-gray-800")
    ui.button(icon="keyboard", on_click=popup.open).props("fab")

