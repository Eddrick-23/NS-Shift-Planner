import pytest
import random
import logging
from typing import cast
from src.backend.internal.grid_handler import GridHandler


@pytest.fixture
def empty_grid(request):
    default_params = {"location": "MCC", "day": 1}

    params = getattr(request, "param", default_params)
    test_db = GridHandler(location=params["location"], day=params["day"])

    return test_db


@pytest.fixture
def grid_with_names(empty_grid: "GridHandler"):
    """
    Creates a GridHandler instance with names
    """
    NAMES = ["Hello", "test", "bob"]
    for name in NAMES:
        empty_grid.add_name(name)

    return empty_grid


@pytest.fixture
def grid_with_shifts(empty_grid: "GridHandler"):
    """
    Creates a GridHandler with shifts allocated
    """
    NAMES = ["Hello", "test", "bob"]
    SHIFTS = ["MCC"] * len(empty_grid.data.index)
    for name in NAMES:
        empty_grid.add_name(name, shifts=SHIFTS)

    return empty_grid


@pytest.fixture
def handler_factory():
    def _factory(location: str, day: int) -> GridHandler:
        return GridHandler(location, day)

    return _factory


@pytest.mark.parametrize(
    "empty_grid",
    [
        {"location": "MCC", "day": 1},
        {"location": "MCC", "day": 2},
        {"location": "HCC1", "day": 1},
        {"location": "HCC1", "day": 2},
        {"location": "HCC2", "day": 1},
        {"location": "HCC2", "day": 2},
        {"location": "MCC", "day": 3},
    ],
    indirect=True,
)
def test_grid_handler_instance(empty_grid: "GridHandler"):
    # check the start times
    if empty_grid.day == 1:
        assert empty_grid.data.iloc[0].Time == "07:00"
    elif empty_grid.day == 2:
        assert empty_grid.data.iloc[0].Time == "06:00"
    elif empty_grid.day == 3:
        assert empty_grid.data.iloc[0].Time == "21:00"

    # check the end times
    if empty_grid.day in [1, 2]:
        assert empty_grid.data.iloc[-1].Time == "20:30"
    elif empty_grid.day == 3:
        assert empty_grid.data.iloc[-1].Time == "06:30"


def test_add_name(empty_grid: "GridHandler"):
    names = ["Hello", "Bob", "Test", "test"]

    for name in names:
        empty_grid.add_name(name)

    db_names = empty_grid.get_names()

    # check that all names are uppercase, and they exist in the hours dict
    for name in db_names:
        assert name.isupper()
        assert name in empty_grid.hours

    # check the correct number of names
    assert len(db_names) == len(set(map(str.upper, names)))

    # check that the names exist in the grid
    name_in_columns = empty_grid.data.columns[2:].to_list()
    assert set(name_in_columns) == set(map(str.upper, names))


@pytest.mark.parametrize("num_allocated", [4, 8, 5, 0])
def test_add_name_with_shifts(empty_grid: "GridHandler", num_allocated):
    NUM_SHIFTS = len(empty_grid.data.index)
    SHIFTS = ["0   "] * NUM_SHIFTS
    replace_indeces = random.sample(range(len(SHIFTS)), num_allocated)
    for idx in replace_indeces:
        SHIFTS[idx] = empty_grid.location

    empty_grid.add_name(name="TEST", shifts=SHIFTS)
    print(empty_grid.data)
    assert empty_grid.hours["TEST"] == num_allocated * 0.5


@pytest.mark.parametrize("name_to_remove", ["HELLO", "BOB", "TEST"])
def test_remove_name(grid_with_names: "GridHandler", name_to_remove):
    original_num_names = len(grid_with_names.get_names())
    grid_with_names.remove_name(name_to_remove)

    db_names = grid_with_names.get_names()

    assert name_to_remove not in db_names
    assert len(db_names) == original_num_names - 1
    assert name_to_remove not in grid_with_names.hours


def test_remove_name_non_existing_name(empty_grid: "GridHandler", caplog):
    names = ["HELLO", "BOB", "TEST"]

    for name in names:
        empty_grid.add_name(name)
    with caplog.at_level(logging.WARNING):
        empty_grid.remove_name("doesnotexist")

    assert set(empty_grid.get_names()) == set(names)
    assert caplog.records[0].levelname == "WARNING"


@pytest.mark.parametrize(
    "new_name,old_name", [("TEST", "BOB"), ("HELLO", "BOB"), ("TEST", "TEST")]
)
def test_rename_existing_name(
    grid_with_names: "GridHandler", new_name, old_name, caplog
):
    grid_with_names.rename(new_name, old_name)

    assert f"New name {new_name} already exists" in caplog.text
    assert len(caplog.records) == 1


@pytest.mark.parametrize(
    "new_name,old_name", [("NEW_TEST", "NOT_IN_DB"), ("TEST_NEW", "DOES_NOT_EXIST")]
)
def test_rename_name_not_in_database(
    grid_with_names: "GridHandler", new_name, old_name, caplog
):
    grid_with_names.rename(new_name, old_name)

    assert f"Old name {old_name} does not exist" in caplog.text
    assert len(caplog.records) == 1


@pytest.mark.parametrize(
    "new_name,old_name", [("NEW_TEST", "BOB"), ("TEST_NEW", "HELLO")]
)
def test_rename_successful(grid_with_names: "GridHandler", new_name, old_name):
    grid_with_names.rename(new_name, old_name)

    assert new_name in grid_with_names.hours
    assert old_name not in grid_with_names.hours

    assert new_name in grid_with_names.get_names()
    assert old_name not in grid_with_names.get_names()


@pytest.mark.parametrize(
    "name1,name2",
    [("NEW_TEST", "BOB"), ("HELLO", "TEST_NEW"), ("NEW_TEST", "TEST_NEW")],
)
def test_swap_names_name_does_not_exist(
    grid_with_names: "GridHandler", name1, name2, caplog
):
    grid_with_names.swap_names(name1, name2)

    assert "does not exist in grid" in caplog.text
    assert len(caplog.records) == 1


@pytest.mark.parametrize(
    "name1,name2", [("HELLO", "BOB"), ("HELLO", "BOB"), ("TEST", "HELLO")]
)
def test_swap_names_successful(grid_with_names: "GridHandler", name1, name2):
    # set some hours
    hours = grid_with_names.hours
    hours[name1] = 5
    hours[name2] = 3.5

    name1_orginal = hours[name1]
    name2_original = hours[name2]

    # swap names
    grid_with_names.swap_names(name1, name2)

    new_hours = grid_with_names.hours
    assert name1 in new_hours
    assert name2 in new_hours

    assert new_hours[name2] == name1_orginal
    assert new_hours[name1] == name2_original


@pytest.mark.parametrize("name", ["TEST_NOT", "NOT_TEST"])
def test_is_shift_allocated_invalid_name(grid_with_names: "GridHandler", name, caplog):
    TIME_BLOCK = "12:00"
    result = grid_with_names.is_shift_allocated(time_block=TIME_BLOCK, name=name)

    assert not result
    assert f"{name} does not exist in the grid" in caplog.text
    assert len(caplog.records) == 1


@pytest.mark.parametrize("time_block", ["76:00", "12:45", "00:00"])
def test_is_shift_allocated_invalid_time_block(
    grid_with_names: "GridHandler", time_block, caplog
):
    NAME = "TEST"
    result = grid_with_names.is_shift_allocated(time_block=time_block, name=NAME)
    assert not result
    assert f"{time_block} is not a valid time block" in caplog.text
    assert len(caplog.records) == 1


@pytest.mark.parametrize(
    "time_block, name",
    [("12:00", "TEST"), ("14:30", "HELLO"), ("07:00", "BOB")],
)
def test_is_shift_allocated_false(
    grid_with_names: "GridHandler", time_block, name, caplog
):
    result = grid_with_names.is_shift_allocated(time_block=time_block, name=name)

    assert not result
    assert len(caplog.records) == 0


@pytest.mark.parametrize("time_block", ["12:00", "07:30", "18:00"])
def test_is_shift_allocated_true(grid_with_shifts: "GridHandler", time_block):
    NAME = "TEST"
    result = grid_with_shifts.is_shift_allocated(time_block=time_block, name=NAME)

    assert result


@pytest.mark.parametrize("time_block", ["12:00", "07:30", "18:00"])
def test_allocate_shift_new_shift(grid_with_names: "GridHandler", time_block):
    NAME = "TEST"
    LOCATIONS = ["MCC", "HCC1", "HCC2"]
    loc = random.choice(LOCATIONS)
    grid_with_names.allocate_shift(location=loc, name=NAME, time_block=time_block)
    assert grid_with_names.hours[NAME] == 0.5


@pytest.mark.parametrize("time_block", ["12:00", "07:30", "18:00"])
def test_allocate_shift_removing_shift(grid_with_shifts: "GridHandler", time_block):
    NAME = "TEST"
    LOCATION = "0   "
    original_hours = grid_with_shifts.hours[NAME]
    grid_with_shifts.allocate_shift(location=LOCATION, name=NAME, time_block=time_block)

    assert grid_with_shifts.hours[NAME] == original_hours - 0.5


@pytest.mark.parametrize("time_block", ["12:00", "07:30", "18:00"])
def test_allocate_shift_replacing_shift(grid_with_shifts: "GridHandler", time_block):
    NAME = "TEST"
    LOCATION1 = "HCC1"
    LOCATION2 = "HCC2"
    original_hours = grid_with_shifts.hours[NAME]
    grid_with_shifts.allocate_shift(
        location=LOCATION1, name=NAME, time_block=time_block
    )
    assert grid_with_shifts.hours[NAME] == original_hours
    grid_with_shifts.allocate_shift(
        location=LOCATION2, name=NAME, time_block=time_block
    )
    assert grid_with_shifts.hours[NAME] == original_hours


@pytest.mark.parametrize(
    "empty_grid",
    [
        {"location": "HCC1", "day": 3},
        {"location": "HCC2", "day": 3},
        {"location": "MCC", "day": 3},
    ],
    indirect=True,
)
def test_allocate_shift_day_3(empty_grid: "GridHandler"):
    NAME = "TEST"
    empty_grid.add_name(NAME)
    TIME_BLOCK1 = "22:00"
    LOC1 = "HCC1"
    TIME_BLOCK2 = "05:00"
    LOC2 = "HCC2"

    empty_grid.allocate_shift(location=LOC1, time_block=TIME_BLOCK1, name="TEST")
    assert empty_grid.hours[NAME] == 0.5
    assert empty_grid.get_shift_location(time_block=TIME_BLOCK1, name=NAME) == "MCC"

    empty_grid.allocate_shift(location=LOC2, time_block=TIME_BLOCK2, name=NAME)
    assert empty_grid.hours[NAME] == 1
    assert empty_grid.get_shift_location(time_block=TIME_BLOCK2, name=NAME) == "MCC"


def generate_location_day_combinations():
    LOCATION = ["MCC", "HCC1", "HCC2"]
    DAY = [1, 2]
    combinations = []
    for loc in LOCATION:
        for day in DAY:
            combinations.append((loc, day))
    return combinations


@pytest.mark.parametrize("location,day", generate_location_day_combinations())
def test_check_lunch_and_dinner(handler_factory, location, day):
    handler = handler_factory(location=location, day=day)
    handler = cast(GridHandler, handler)

    handler.add_name("NO_LUNCH")
    handler.add_name("LUNCH_CONTROL1")
    handler.add_name("LUNCH_CONTROL2")
    handler.add_name("NO_DINNER")
    handler.add_name("DINNER_CONTROL1")
    handler.add_name("DINNER_CONTROL2")
    handler.add_name("NO_LUNCH_DINNER")

    # lunch from 1100 to 1330, start 1100, end 1330 == no lunch break
    full_lunch_time_blocks = ["11:00", "11:30", "12:00", "12:30", "13:00"]
    full_dinner_time_blocks = ["17:00", "17:30", "18:00"]

    for time_block in full_lunch_time_blocks:
        handler.allocate_shift(
            location=location, time_block=time_block, name="NO_LUNCH"
        )
        handler.allocate_shift(
            location=location, time_block=time_block, name="NO_LUNCH_DINNER"
        )
        if time_block != full_lunch_time_blocks[0]:
            handler.allocate_shift(
                location=location, time_block=time_block, name="LUNCH_CONTROL1"
            )
        if time_block != full_lunch_time_blocks[-1]:
            handler.allocate_shift(
                location=location, time_block=time_block, name="LUNCH_CONTROL2"
            )

    for time_block in full_dinner_time_blocks:
        handler.allocate_shift(
            location=location,
            time_block=time_block,
            name="NO_DINNER",
        )
        handler.allocate_shift(
            location=location, time_block=time_block, name="NO_LUNCH_DINNER"
        )
        if time_block != full_dinner_time_blocks[0]:
            handler.allocate_shift(
                location=location, time_block=time_block, name="DINNER_CONTROL1"
            )
        if time_block != full_dinner_time_blocks[-1]:
            handler.allocate_shift(
                location=location, time_block=time_block, name="DINNER_CONTROL2"
            )

    result = handler.check_lunch_and_dinner()

    assert len(result) == 3
    assert "NO_DINNER" in result
    assert "NO_LUNCH" in result
    assert "NO_LUNCH_DINNER" in result


def test_generate_formatted_df(handler_factory):
    handler = handler_factory(location="MCC", day=1)
    handler = cast(GridHandler, handler)

    handler.add_name("TEST")
    blocks_to_remove = ["08:30", "09:30"]
    result = handler.generate_formatted_dataframe(blocks_to_remove)
    cols = result.columns.to_list()

    for time_block in blocks_to_remove:
        assert time_block not in cols

def test_df_to_aggrid_format(handler_factory):
    handler = handler_factory(location="MCC", day=1)
    handler = cast(GridHandler, handler)

    handler.add_name("TEST")
    blocks_to_remove = ["08:30", "09:30"]
    result = handler.generate_formatted_dataframe(blocks_to_remove) 

    aggrid_format = handler.df_to_aggrid_format(result)

    print(aggrid_format)
