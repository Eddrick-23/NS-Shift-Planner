import io
import zipfile
import pytest
from typing import cast
from src.backend.internal.grid_handler import GridHandler
from src.backend.internal.grid_manager import GridManager

@pytest.fixture
def handler_factory():
    def _factory(location: str, day: int) -> GridHandler:
        return GridHandler(location, day)

    return _factory

@pytest.fixture
def handler_factory_with_data(handler_factory) -> GridHandler:
    def _factory(location:str,day:int):
        handler = handler_factory(location,day)
        handler = cast(GridHandler,handler)
        handler.add_name("TEST")
        if day != 3:
            handler.allocate_shift(handler.location,time_block="07:00",name="TEST")
            handler.allocate_shift(handler.location,time_block="07:30",name="TEST")
            handler.allocate_shift(handler.location,time_block="08:00",name="TEST")
        elif day == 3:
            handler.allocate_shift(handler.location,time_block="21:00",name="TEST")
            handler.allocate_shift(handler.location,time_block="22:00",name="TEST")
            handler.allocate_shift(handler.location,time_block="22:30",name="TEST")
        return handler
    return _factory

@pytest.fixture
def test_manager(handler_factory_with_data):
    EXISTING_NAMES = {"DAY1": set("TEST"), "DAY2": set("TEST"), "DAY3": set("TEST")}
    manager = GridManager()
    manager.all_grids["DAY1:MCC"] = handler_factory_with_data("MCC",1)
    manager.all_grids["DAY1:HCC1"] = handler_factory_with_data("HCC1",2)
    manager.all_grids["DAY1:HCC2"] = handler_factory_with_data("HCC2",2)
    manager.all_grids["DAY2:MCC"] = handler_factory_with_data("MCC",1)
    manager.all_grids["DAY2:HCC1"] = handler_factory_with_data("HCC1",2)
    manager.all_grids["DAY2:HCC2"] = handler_factory_with_data("HCC2",2)
    manager.all_grids["DAY3:MCC"] = handler_factory_with_data("MCC",1)
    manager.existing_names = EXISTING_NAMES
    manager.all_hours["TEST"] = {
        "Name": "TOTAL",
        "Day 1": 4.5,
        "Day 2": 4.5,
        "Day 3": 1.5,
        "Total": 10.5,
    }
    return manager

def test_serialisation(test_manager):
    zip_data = test_manager.serialise_to_zip()
    buffer = io.BytesIO(zip_data)

    with zipfile.ZipFile(buffer,"r") as zf:
        file_names = zf.namelist()
    
    assert "manager_info.json" in file_names

    parquet_count = sum(name.endswith("dataframe.parquet") for name in file_names)
    assert parquet_count == 7
    metadata_count = sum(name.endswith("metadata.json") for name in file_names)
    assert metadata_count == 7

def test_deserialisation(test_manager):
    zip_data = test_manager.serialise_to_zip()

    deserialised_manager = GridManager.deserialise_from_zip(zip_data)

    for deserialised_handler,original_handler in zip(deserialised_manager.all_grids.values(),test_manager.all_grids.values()):
        assert deserialised_handler.equals(original_handler)
    
    assert deserialised_manager.existing_names == test_manager.existing_names
    assert deserialised_manager.all_hours == test_manager.all_hours
