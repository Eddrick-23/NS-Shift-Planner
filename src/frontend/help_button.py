from nicegui import ui


def create_help_button():
    with ui.dialog() as popup, ui.card():
        ui.markdown("""
        ## ❓ Frequently Asked Questions

        ---

        ### 1)How do I add or remove names?

        To modify a grid, follow these steps:

        1. Select the grid in the dropdown
        2. Type the name to add in the text box.(It will be formatted to upper case)
        3. Click the **+ / -** button

        ---

        ### 2)How do I allocate a shift?

        To allocate a shift:

        - Select the location in the radio button on the top right
        - Click on the cell box
        - Use __'a' + left click__ to allocate the __first__ 30 mins
        - Use __'d' + left click__ to allocate the __last__ 30 mins

        _Pro Tip: Use **Shift + [1,2,3]** to quickly set the location._

        ---

        ### 3)How do I save my work?

        Your changes are automatically saved periodically.

        To manually save:

        - Click the **Save** icon in the top-right corner.
        - Or use the shortcut **Ctrl + S** (Cmd + S on Mac).

        ---

        ### 4) How do I upload my work?

        To upload:

        1. Go to the **Upload** section in the menu.
        2. Drag and drop your `.json` or `.xlsx` file.
        3. Click **Upload** and confirm.

        _Once uploaded, your data will be processed and integrated into the system._

        ---
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
