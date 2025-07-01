import pandas as pd
import io
import pytest
from typing import cast
from src.backend.internal.grid_handler import GridHandler

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

@pytest.mark.parametrize("location, day",[
        ("MCC",1),
        ("MCC",2),
        ("HCC1",1),
        ("HCC1",2),
        ("HCC2",1),
        ("HCC2",2),
        ("MCC",3)
])
def test_serialisation_metadata(handler_factory_with_data, location,day):
    handler = handler_factory_with_data(location,day)
    handler = cast(GridHandler,handler)
    metadata,_ = handler.serialise_for_storage()
    assert metadata["names"] == list(handler.names)
    assert metadata["location"] == handler.location
    assert metadata["identifier"] == handler.identifier
    assert metadata["hours"] == handler.hours
    assert metadata["bit_mask"] == handler.bit_mask.to01()

@pytest.mark.parametrize("location, day",[
        ("MCC",1),
        ("MCC",2),
        ("HCC1",1),
        ("HCC1",2),
        ("HCC2",1),
        ("HCC2",2),
        ("MCC",3)
])
def test_serialisation_dataframe(handler_factory_with_data, location,day):
    handler = handler_factory_with_data(location,day)
    handler = cast(GridHandler,handler)
    _,df_bytes = handler.serialise_for_storage() 
    buffer = io.BytesIO(df_bytes)
    data = pd.read_parquet(buffer)
    assert data.equals(handler.data)

@pytest.mark.parametrize("location, day",[
        ("MCC",1),
        ("MCC",2),
        ("HCC1",1),
        ("HCC1",2),
        ("HCC2",1),
        ("HCC2",2),
        ("MCC",3)
])
def test_deserialisation(handler_factory_with_data,location,day):
    handler = handler_factory_with_data(location,day)
    handler = cast(GridHandler,handler)
    metadata,df_bytes = handler.serialise_for_storage()

    deserialised_handler = GridHandler.deserialise_from_storage(metadata,df_bytes)
    result, details = deserialised_handler.equals(handler)
    if details is not None:
        print(f"Equals failed: {details}")
    assert result
