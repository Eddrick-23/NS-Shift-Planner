import pytest
from typing import cast
import itertools
from src.backend.internal.grid_manager import GridManager
from src.backend.internal.grid_handler import GridHandler


@pytest.fixture
def test_manager():
    return GridManager()


@pytest.fixture
def handler_factory():
    def _factory(location: str, day: int) -> GridHandler:
        return GridHandler(location, day)

    return _factory


def test_class_init(test_manager: "GridManager"):
    grid_handlers = test_manager.all_grids

    assert len(grid_handlers) == 7

    expected_configs = set()
    LOCATIONS = ["MCC ", "HCC1", "HCC2"]
    for loc in LOCATIONS:
        for i in range(1, 4):
            if i == 3 and loc != "MCC ":
                continue
            expected_configs.add((loc, i))

    for handler in grid_handlers:
        location, day = handler.location, handler.day

        if (location, day) in expected_configs:
            expected_configs.remove((location, day))

    assert expected_configs == set()


def test_format_keys_join_time_block_one_dataframe(test_manager, handler_factory):
    handler = handler_factory(location="MCC ", day=3)
    handler = cast(GridHandler, handler)

    handler.add_name("TEST1")
    handler.add_name("TEST2")
    handler.add_name("TEST3")

    handler.allocate_shift("MCC", "22:00", "TEST1")
    handler.allocate_shift("MCC", "22:30", "TEST1")
    handler.allocate_shift("MCC", "06:00", "TEST2")
    handler.allocate_shift("MCC", "06:30", "TEST2")

    blocks_to_remove = test_manager.format_keys(handler.data)

    for time_block in blocks_to_remove:  # every 1h block can be combined
        assert ":00" not in time_block


def test_format_keys_cannot_join_time_block_one_dataframe(
    test_manager, handler_factory
):
    handler = handler_factory(location="MCC ", day=3)
    handler = cast(GridHandler, handler)

    handler.add_name("TEST1")
    handler.add_name("TEST2")
    handler.add_name("TEST3")

    handler.allocate_shift("MCC", "22:00", "TEST1")
    handler.allocate_shift("MCC", "06:00", "TEST2")
    handler.allocate_shift("MCC", "06:30", "TEST2")
    handler.allocate_shift("MCC", "06:30", "TEST3")

    blocks_to_remove = test_manager.format_keys(handler.data)

    assert "22:30" not in blocks_to_remove
    assert "06:30" not in blocks_to_remove

    total_1h_blocks = len(handler.data) / 2
    num_cannot_join = 2

    assert len(blocks_to_remove) == total_1h_blocks - num_cannot_join


def generate_day_location_combinatons():
    DAY = [1, 2]
    LOCATIONS = ["MCC ", "HCC1", "HCC2"]

    all_location_permutations = itertools.permutations(LOCATIONS)

    combinations = []
    for location_permuation in all_location_permutations:
        for day in DAY:
            final_tuple = (day,) + location_permuation
            combinations.append(final_tuple)

    return combinations


@pytest.mark.parametrize(
    "day, allocate_loc1,allocate_loc2, allocate_loc3",
    generate_day_location_combinatons(),
)
def test_format_keys_join_time_block(
    test_manager, handler_factory, day, allocate_loc1, allocate_loc2, allocate_loc3
):
    handler1 = handler_factory(location="MCC ", day=day)
    handler2 = handler_factory(location="HCC1", day=day)
    handler3 = handler_factory(location="HCC2", day=day)
    handler1 = cast(GridHandler, handler1)
    handler2 = cast(GridHandler, handler2)
    handler3 = cast(GridHandler, handler3)

    handler1.add_name("TEST1")
    handler1.allocate_shift(location=allocate_loc1, time_block="08:00", name="TEST1")
    handler1.allocate_shift(location=allocate_loc1, time_block="08:30", name="TEST1")

    handler2.add_name("TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:00", name="TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:30", name="TEST2")

    handler3.add_name("TEST3")
    handler3.allocate_shift(location=allocate_loc3, time_block="17:00", name="TEST3")
    handler3.allocate_shift(location=allocate_loc3, time_block="17:30", name="TEST3")

    blocks_to_remove = test_manager.format_keys(handler1.data, handler2.data)

    total_1h_blocks = len(handler1.data) / 2
    assert len(blocks_to_remove) == total_1h_blocks

    for time_block in blocks_to_remove:
        assert ":00" not in time_block


@pytest.mark.parametrize(
    "day, allocate_loc1,allocate_loc2, allocate_loc3",
    generate_day_location_combinatons(),
)
def test_format_keys_join_time_block_multiple_names(
    test_manager, handler_factory, day, allocate_loc1, allocate_loc2, allocate_loc3
):
    handler1 = handler_factory(location="MCC ", day=day)
    handler2 = handler_factory(location="HCC1", day=day)
    handler3 = handler_factory(location="HCC2", day=day)
    handler1 = cast(GridHandler, handler1)
    handler2 = cast(GridHandler, handler2)
    handler3 = cast(GridHandler, handler3)

    handler1.add_name("TEST1_1")
    handler1.add_name("TEST1_2")
    handler1.allocate_shift(
        location=allocate_loc1, time_block="08:00", name="TEST1_1"
    )
    handler1.allocate_shift(
        location=allocate_loc1, time_block="08:30", name="TEST1_1"
    )

    handler2.add_name("TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:00", name="TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:30", name="TEST2")

    handler3.add_name("TEST3_1")
    handler3.add_name("TEST3_2")
    handler3.add_name("TEST3_3")
    handler3.allocate_shift(
        location=allocate_loc3, time_block="17:00", name="TEST3_1"
    )
    handler3.allocate_shift(
        location=allocate_loc3, time_block="17:30", name="TEST3_1"
    )
    handler3.allocate_shift(
        location=allocate_loc3, time_block="18:00", name="TEST3_3"
    )
    handler3.allocate_shift(
        location=allocate_loc3, time_block="18:30", name="TEST3_3"
    )

    blocks_to_remove = test_manager.format_keys(
        handler1.data, handler2.data, handler3.data
    )

    total_1h_blocks = len(handler1.data) / 2
    assert len(blocks_to_remove) == total_1h_blocks

    for time_block in blocks_to_remove:
        assert ":00" not in time_block


@pytest.mark.parametrize(
    "day, allocate_loc1,allocate_loc2, allocate_loc3",
    generate_day_location_combinatons(),
)
def test_format_keys_cannot_join_time_block(
    test_manager, handler_factory, day, allocate_loc1, allocate_loc2, allocate_loc3
):
    handler1 = handler_factory(location="MCC ", day=day)
    handler2 = handler_factory(location="HCC1", day=day)
    handler3 = handler_factory(location="HCC2", day=day)
    handler1 = cast(GridHandler, handler1)
    handler2 = cast(GridHandler, handler2)
    handler3 = cast(GridHandler, handler3)

    handler1.add_name("TEST1_1")
    handler1.add_name("TEST1_2")
    handler1.allocate_shift(
        location=allocate_loc1, time_block="08:00", name="TEST1_1"
    )
    handler1.allocate_shift(
        location=allocate_loc1, time_block="08:30", name="TEST1_2"
    )

    handler2.add_name("TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:00", name="TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:30", name="TEST2")

    handler3.add_name("TEST3_1")
    handler3.add_name("TEST3_2")
    handler3.add_name("TEST3_3")
    handler3.allocate_shift(
        location=allocate_loc3, time_block="17:00", name="TEST3_1"
    )
    handler3.allocate_shift(
        location=allocate_loc3, time_block="18:30", name="TEST3_1"
    )
    handler3.allocate_shift(
        location=allocate_loc3, time_block="18:00", name="TEST3_3"
    )
    handler3.allocate_shift(
        location=allocate_loc3, time_block="18:30", name="TEST3_3"
    )

    blocks_to_remove = test_manager.format_keys(
        handler1.data, handler2.data, handler3.data
    )

    assert "17:30" not in blocks_to_remove
    assert "18:30" not in blocks_to_remove
    assert "08:30" not in blocks_to_remove

    total_1h_blocks = len(handler1.data) / 2
    num_cannot_join = 3
    assert len(blocks_to_remove) == total_1h_blocks - num_cannot_join
