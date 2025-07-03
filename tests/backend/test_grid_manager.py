import pytest
from typing import cast
import itertools
from src.backend.internal.grid_manager import GridManager
from src.backend.internal.grid_handler import GridHandler
import src.backend.internal.time_blocks as tb


@pytest.fixture
def test_manager():
    return GridManager()


@pytest.fixture
def handler_factory():
    def _factory(location: str, day: int) -> GridHandler:
        return GridHandler(location, day)

    return _factory


@pytest.fixture
def manager_with_grid_with_name(test_manager, handler_factory, request):
    TEST_NAMES = ["TEST_A", "TEST_B", "TEST_C", "TEST_D"]
    day = request.param
    if day == 3:
        handler = handler_factory(location="MCC", day=3)
        for name in TEST_NAMES:
            handler.add_name(name)
        test_manager.all_grids["DAY3:MCC"] = handler
        return test_manager

    handler1 = handler_factory(location="MCC", day=day)
    handler2 = handler_factory(location="HCC1", day=day)
    handler3 = handler_factory(location="HCC2", day=day)
    handler1.add_name("TEST_A")
    handler1.add_name("TEST_B")
    handler2.add_name("TEST_C")
    handler3.add_name("TEST_D")
    test_manager.all_grids[f"DAY{day}:MCC"] = handler1
    test_manager.all_grids[f"DAY{day}:HCC1"] = handler2
    test_manager.all_grids[f"DAY{day}:HCC2"] = handler3
    return test_manager


@pytest.fixture
def manager_all_grid_with_name(test_manager, handler_factory):
    TEST_NAMES = [
        "TEST_D1_MCC",
        "TEST_D1_HCC1",
        "TEST_D1_HCC2",
        "TEST_D2_MCC",
        "TEST_D2_HCC1",
        "TEST_D2_HCC2",
        "TEST_D3_MCC",
    ]
    handler1 = handler_factory(location="MCC", day=1)
    handler2 = handler_factory(location="HCC1", day=1)
    handler3 = handler_factory(location="HCC2", day=1)
    handler4 = handler_factory(location="MCC", day=1)
    handler5 = handler_factory(location="HCC1", day=2)
    handler6 = handler_factory(location="HCC2", day=2)
    handler7 = handler_factory(location="MCC", day=3)
    handler1.add_name(TEST_NAMES[0])
    handler2.add_name(TEST_NAMES[1])
    handler3.add_name(TEST_NAMES[2])
    handler4.add_name(TEST_NAMES[3])
    handler5.add_name(TEST_NAMES[4])
    handler6.add_name(TEST_NAMES[5])
    handler7.add_name(TEST_NAMES[6])
    test_manager.all_grids[f"DAY{1}:MCC"] = handler1
    test_manager.all_grids[f"DAY{1}:HCC1"] = handler2
    test_manager.all_grids[f"DAY{1}:HCC2"] = handler3
    test_manager.all_grids[f"DAY{2}:MCC"] = handler4
    test_manager.all_grids[f"DAY{2}:HCC1"] = handler5
    test_manager.all_grids[f"DAY{2}:HCC2"] = handler6
    test_manager.all_grids[f"DAY{3}:MCC"] = handler7
    for i in range(1, 4):
        test_manager.update_existing_names(i)
    return test_manager


def test_class_init(test_manager: "GridManager"):
    grid_handlers = test_manager.all_grids

    assert len(grid_handlers) == 7

    expected_configs = set()
    LOCATIONS = ["MCC", "HCC1", "HCC2"]
    for loc in LOCATIONS:
        for i in range(1, 4):
            if i == 3 and loc != "MCC":
                continue
            expected_configs.add((loc, i))

    for handler in grid_handlers.values():
        location, day = handler.location, handler.day

        if (location, day) in expected_configs:
            expected_configs.remove((location, day))

    assert expected_configs == set()

def test_format_keys_join_time_block_one_dataframe(test_manager, handler_factory):
    handler = handler_factory(location="MCC", day=3)
    handler = cast(GridHandler, handler)

    handler.add_name("TEST1")
    handler.add_name("TEST2")
    handler.add_name("TEST3")

    handler.allocate_shift("MCC", "22:00", "TEST1")
    handler.allocate_shift("MCC", "22:30", "TEST1")
    handler.allocate_shift("MCC", "06:00", "TEST2")
    handler.allocate_shift("MCC", "06:30", "TEST2")

    blocks_to_remove = test_manager.format_keys(
        tb.HALF_DAY_BLOCK_MAP[3], handler.data
    )

    for time_block in blocks_to_remove:  # every 1h block can be combined
        assert ":00" not in time_block


def test_format_keys_cannot_join_time_block_one_dataframe(
    test_manager, handler_factory
):
    handler = handler_factory(location="MCC", day=3)
    handler = cast(GridHandler, handler)

    handler.add_name("TEST1")
    handler.add_name("TEST2")
    handler.add_name("TEST3")

    handler.allocate_shift("MCC", "22:00", "TEST1")
    handler.allocate_shift("MCC", "06:00", "TEST2")
    handler.allocate_shift("MCC", "06:30", "TEST2")
    handler.allocate_shift("MCC", "06:30", "TEST3")

    blocks_to_remove = test_manager.format_keys(
        tb.HALF_DAY_BLOCK_MAP[3], handler.bit_mask
    )

    assert "22:30" not in blocks_to_remove
    assert "06:30" not in blocks_to_remove

    total_1h_blocks = len(handler.data) / 2
    num_cannot_join = 2

    assert len(blocks_to_remove) == total_1h_blocks - num_cannot_join


def generate_day_location_combinatons():
    DAY = [1, 2]
    LOCATIONS = ["MCC", "HCC1", "HCC2"]

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
    handler1 = handler_factory(location="MCC", day=day)
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

    blocks_to_remove = test_manager.format_keys(
        tb.HALF_DAY_BLOCK_MAP[day],
        handler1.bit_mask,
        handler2.bit_mask,
        handler3.bit_mask,
    )

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
    handler1 = handler_factory(location="MCC", day=day)
    handler2 = handler_factory(location="HCC1", day=day)
    handler3 = handler_factory(location="HCC2", day=day)
    handler1 = cast(GridHandler, handler1)
    handler2 = cast(GridHandler, handler2)
    handler3 = cast(GridHandler, handler3)

    handler1.add_name("TEST1_1")
    handler1.add_name("TEST1_2")
    handler1.allocate_shift(location=allocate_loc1, time_block="08:00", name="TEST1_1")
    handler1.allocate_shift(location=allocate_loc1, time_block="08:30", name="TEST1_1")

    handler2.add_name("TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:00", name="TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:30", name="TEST2")

    handler3.add_name("TEST3_1")
    handler3.add_name("TEST3_2")
    handler3.add_name("TEST3_3")
    handler3.allocate_shift(location=allocate_loc3, time_block="17:00", name="TEST3_1")
    handler3.allocate_shift(location=allocate_loc3, time_block="17:30", name="TEST3_1")
    handler3.allocate_shift(location=allocate_loc3, time_block="18:00", name="TEST3_3")
    handler3.allocate_shift(location=allocate_loc3, time_block="18:30", name="TEST3_3")

    blocks_to_remove = test_manager.format_keys(
        tb.HALF_DAY_BLOCK_MAP[day],
        handler1.bit_mask,
        handler2.bit_mask,
        handler3.bit_mask,
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
    handler1 = handler_factory(location="MCC", day=day)
    handler2 = handler_factory(location="HCC1", day=day)
    handler3 = handler_factory(location="HCC2", day=day)
    handler1 = cast(GridHandler, handler1)
    handler2 = cast(GridHandler, handler2)
    handler3 = cast(GridHandler, handler3)

    handler1.add_name("TEST1_1")
    handler1.add_name("TEST1_2")
    handler1.allocate_shift(location=allocate_loc1, time_block="08:00", name="TEST1_1")
    handler1.allocate_shift(location=allocate_loc1, time_block="08:30", name="TEST1_2")

    handler2.add_name("TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:00", name="TEST2")
    handler2.allocate_shift(location=allocate_loc2, time_block="09:30", name="TEST2")

    handler3.add_name("TEST3_1")
    handler3.add_name("TEST3_2")
    handler3.add_name("TEST3_3")
    handler3.allocate_shift(location=allocate_loc3, time_block="17:00", name="TEST3_1")
    handler3.allocate_shift(location=allocate_loc3, time_block="18:30", name="TEST3_1")
    handler3.allocate_shift(location=allocate_loc3, time_block="18:00", name="TEST3_3")
    handler3.allocate_shift(location=allocate_loc3, time_block="18:30", name="TEST3_3")

    blocks_to_remove = test_manager.format_keys(
        tb.HALF_DAY_BLOCK_MAP[day],
        handler1.bit_mask,
        handler2.bit_mask,
        handler3.bit_mask,
    )

    assert "17:30" not in blocks_to_remove
    assert "18:30" not in blocks_to_remove
    assert "08:30" not in blocks_to_remove

    total_1h_blocks = len(handler1.data) / 2
    num_cannot_join = 3
    assert len(blocks_to_remove) == total_1h_blocks - num_cannot_join


def test_update_existing_names_empty_grids(test_manager: "GridManager"):
    existing_names = test_manager.existing_names
    for names in existing_names.values():
        assert names == set()
    test_manager.update_existing_names(day=1)
    test_manager.update_existing_names(day=2)
    test_manager.update_existing_names(day=3)
    for names in existing_names.values():
        assert names == set()


@pytest.mark.parametrize("manager_with_grid_with_name", [1], indirect=True)
def test_update_existing_names_day_1(manager_with_grid_with_name: "GridManager"):
    day = 1
    manager = manager_with_grid_with_name
    assert manager.existing_names[f"DAY{day}"] == set()
    manager.update_existing_names(day)
    original = manager.existing_names[f"DAY{day}"]
    assert len(original) == 4
    manager.all_grids[f"DAY{day}:MCC"].add_name("TEST_MCC")
    manager.all_grids[f"DAY{day}:HCC1"].add_name("TEST_HCC1")
    manager.all_grids[f"DAY{day}:HCC2"].add_name("TEST_HCC2")
    manager.update_existing_names(day)
    after_adding = manager.existing_names[f"DAY{day}"]
    assert len(after_adding) == 7
    manager.all_grids[f"DAY{day}:MCC"].remove_name("TEST_MCC")
    manager.all_grids[f"DAY{day}:HCC1"].remove_name("TEST_HCC1")
    manager.all_grids[f"DAY{day}:HCC2"].remove_name("TEST_HCC2")
    manager.update_existing_names(day)
    after_removing = manager.existing_names[f"DAY{day}"]
    assert len(after_removing) == 4


@pytest.mark.parametrize("manager_with_grid_with_name", [2], indirect=True)
def test_existing_names_day_2(manager_with_grid_with_name: "GridManager"):
    day = 2
    manager = manager_with_grid_with_name
    assert manager.existing_names[f"DAY{day}"] == set()
    manager.update_existing_names(day)
    original = manager.existing_names[f"DAY{day}"]
    assert len(original) == 4
    manager.all_grids[f"DAY{day}:MCC"].add_name("TEST_MCC")
    manager.all_grids[f"DAY{day}:HCC1"].add_name("TEST_HCC1")
    manager.all_grids[f"DAY{day}:HCC2"].add_name("TEST_HCC2")
    manager.update_existing_names(day)
    after_adding = manager.existing_names[f"DAY{day}"]
    assert len(after_adding) == 7
    manager.all_grids[f"DAY{day}:MCC"].remove_name("TEST_MCC")
    manager.all_grids[f"DAY{day}:HCC1"].remove_name("TEST_HCC1")
    manager.all_grids[f"DAY{day}:HCC2"].remove_name("TEST_HCC2")
    manager.update_existing_names(day)
    after_removing = manager.existing_names[f"DAY{day}"]
    assert len(after_removing) == 4


@pytest.mark.parametrize("manager_with_grid_with_name", [3], indirect=True)
def test_update_existing_names_day_3(manager_with_grid_with_name: "GridManager"):
    day = 3
    manager = manager_with_grid_with_name
    assert manager.existing_names[f"DAY{day}"] == set()
    manager.update_existing_names(day)
    original = manager.existing_names[f"DAY{day}"]
    assert len(original) == 4
    manager.all_grids[f"DAY{day}:MCC"].add_name("TEST_ADD")
    manager.update_existing_names(day)
    after_adding = manager.existing_names[f"DAY{day}"]
    assert "TEST_ADD" in after_adding
    manager.all_grids[f"DAY{day}:MCC"].remove_name("TEST_ADD")
    manager.update_existing_names(day)
    after_removing = manager.existing_names[f"DAY{day}"]
    assert "TEST_ADD" not in after_removing


def test_get_all_hours(manager_all_grid_with_name: "GridManager"):
    manager = manager_all_grid_with_name
    grid_handler_name_map = {
        "DAY1:MCC": "TEST_D1_MCC",
        "DAY1:HCC1": "TEST_D1_HCC1",
        "DAY1:HCC2": "TEST_D1_HCC2",
        "DAY2:MCC": "TEST_D2_MCC",
        "DAY2:HCC1": "TEST_D2_HCC1",
        "DAY2:HCC2": "TEST_D2_HCC2",
        "DAY3:MCC": "TEST_D3_MCC",
    }
    for key, name in grid_handler_name_map.items():
        grid_handler = manager.all_grids[key]
        grid_handler = cast(GridHandler, grid_handler)
        time_block_1 = "12:00"
        time_block_2 = "12:30"
        if grid_handler.day == 3:
            time_block_1 = "00:00"
            time_block_2 = "00:30"
        grid_handler.allocate_shift(
            location=grid_handler.location, time_block=time_block_1, name=name
        )
        grid_handler.allocate_shift(
            location=grid_handler.location, time_block=time_block_2, name=name
        )
    
    all_hour_data, _ =  manager.get_all_hours()
    for hour_list in all_hour_data:
        assert sum(hour_list) == 1.0
