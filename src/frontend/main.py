# main.py
from nicegui import ui
from helper import GridEventHandler

# Create a single event handler instance for all grids
grid_handler = GridEventHandler()

# First grid
ui.label("First Grid - People")
ui.aggrid({
    'columnDefs': [
        {'headerName': 'Name', 'field': 'name'},
        {'headerName': 'Age', 'field': 'age'},
    ],
    'rowData': [
        {'name': 'Alice', 'age': 18},
        {'name': 'Bob', 'age': 21},
        {'name': 'Carol', 'age': 42},
    ],
}).on('cellClicked', grid_handler.create_click_handler("People Grid"))

# Second grid
ui.label("Second Grid - Products")
ui.aggrid({
    'columnDefs': [
        {'headerName': 'Product', 'field': 'product'},
        {'headerName': 'Price', 'field': 'price'},
    ],
    'rowData': [
        {'product': 'Laptop', 'price': 999},
        {'product': 'Mouse', 'price': 25},
        {'product': 'Keyboard', 'price': 75},
    ],
}).on('cellClicked', grid_handler.create_click_handler("Products Grid"))

ui.run()
