import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.backend.app import create_app
from src.backend.routes import get_manager
from src.backend.internal.grid_manager import GridManager
from unittest.mock import Mock
from src.backend.internal.time_blocks import DAY_BLOCK_MAP,HALF_DAY_BLOCK_MAP


@pytest.fixture()
def test_client_factory(request):
    """
    Need to pass in a GridManager instance
    """

    def _create_test_client(manager: GridManager):
        app = create_app(use_lifespan=False)

        def override_get_manager():
            return manager

        app.dependency_overrides[get_manager] = override_get_manager

        client = TestClient(app)
        return client

    return _create_test_client


def test_health(test_client_factory):
    manager = GridManager()
    client = test_client_factory(manager)
    response = client.get("/health/")
    assert response.status_code == 200


def test_cached_items(test_client_factory):
    manager = GridManager()
    client = test_client_factory(manager)
    response = client.get("/cached_items/")
    assert response.status_code == 200
    jresponse = response.json()

    assert jresponse["current_size"] == 0
    assert jresponse["num_items"] == 0


@pytest.mark.parametrize(
    "grid_name",
    [
        "DAY1:MCC",
        "DAY1:HCC1",
        "DAY1:HCC2",
        "DAY2:MCC",
        "DAY2:HCC1",
        "DAY2:HCC2",
        "DAY3:MCC",
    ],
)
def test_add_name(test_client_factory, grid_name):
    body = {
        "grid_name": grid_name,
    }
    manager = GridManager()
    client = test_client_factory(manager)
    TEST_NAMES = ["TEST1", "TEST2"]

    for name in TEST_NAMES:
        body["name"] = name
        response = client.post("/grid/add/", json=body)
        assert response.status_code == 201


@pytest.mark.parametrize(
    "grid_name, location, allocation_size, time_block",
    [
        ("DAY1:MCC", "MCC", "1", "09:00"),
        ("DAY1:HCC1", "HCC1", "1", "09:00"),
        ("DAY1:HCC2", "HCC2", "1", "09:00"),
        ("DAY2:MCC", "MCC", "1", "12:00"),
        ("DAY2:HCC1", "HCC1", "1", "14:00"),
        ("DAY2:HCC2", "HCC2", "1", "20:00"),
        ("DAY3:MCC", "MCC", "1", "00:00"),
    ],
)
def test_allocate_full_second_half_not_allocated(
    test_client_factory, grid_name, location, allocation_size, time_block
):
    add_name_body = {"grid_name": grid_name, "name": "TEST"}
    manager = GridManager()
    client = test_client_factory(manager)
    response = client.post("/grid/add", json=add_name_body)
    assert response.status_code == 201

    body = {
        "grid_name": grid_name,
        "name": "TEST",
        "location": location,
        "allocation_size": "1",
        "time_block": time_block,
    }

    response = client.post("/grid/allocate/", json=body)
    assert response.status_code == 200
    assert response.json()["allocation_size"] == "1"

@pytest.mark.parametrize("allocation_size, day",[
    ("1",1),
    ("0.25",1),
    ("0.75",1),
    ("1",2),
    ("0.25",2),
    ("0.75",2),
    ("1",3),
    ("0.25",3),
    ("0.75",3),
])
def test_allocate_second_half_time_block(test_client_factory, allocation_size, day):
    manager = GridManager()
    client = test_client_factory(manager)
    #should default to 0.75 so long as ending with :30
    grids = ["DAY1:MCC","DAY1:HCC1","DAY1:HCC2","DAY2:MCC","DAY2:HCC1","DAY2:HCC2","DAY3:MCC"]


    for grid in grids:
        time_blocks = HALF_DAY_BLOCK_MAP[int(grid[3])]
        add_name_body = {"grid_name": grid, "name": "TEST"}
        response = client.post("/grid/add/", json=add_name_body)
        assert response.status_code == 201
        #add name first

        for tb in time_blocks:
            body = {
                "grid_name": grid,
                "name": "TEST",
                "location": grid[5:],
                "allocation_size": "1",
                "time_block": tb,
            }
            response = client.post("/grid/allocate/", json=body)
            assert response.status_code == 200
            assert response.json()["allocation_size"] == "0.75"
        manager = GridManager()
        client = test_client_factory(manager) #reset 


@pytest.mark.parametrize(
        "grid_name, location, allocation_size,time_block",
        [
            ("DAY1:MCC", "MCC", "1", "09:00"),
            ("DAY1:HCC1", "HCC1", "1", "09:00"),
            ("DAY1:HCC2", "HCC2", "1", "09:00"),
            ("DAY2:MCC", "MCC", "1", "12:00"),
            ("DAY2:HCC1", "HCC1", "1", "14:00"),
            ("DAY2:HCC2", "HCC2", "1", "20:00"),
            ("DAY3:MCC", "MCC", "1", "00:00"),
        ],
)
def test_allocate_grid_full_right_half_allocated(test_client_factory, grid_name, location, allocation_size, time_block):
    #expecting "0.25"
    add_name_body = {"grid_name": grid_name, "name": "TEST"}
    manager = GridManager()
    client = test_client_factory(manager)
    response = client.post("/grid/add/", json=add_name_body)
    assert response.status_code == 201

    allocate_right_body = {
        "grid_name": grid_name,
        "name": "TEST",
        "location": location,
        "allocation_size": "0.75",
        "time_block": time_block[:-2] + "30", 
    }

    response = client.post("/grid/allocate/", json=allocate_right_body)
    assert response.status_code == 200
    assert response.json()["allocation_size"] == "0.75"

    body = {
        "grid_name": grid_name,
        "name": "TEST",
        "location": location,
        "allocation_size": "1",
        "time_block": time_block,
    }

    response = client.post("/grid/allocate/", json=body)
    assert response.status_code == 200 
    assert response.json()["allocation_size"] == "0.25"

@pytest.mark.parametrize(
    "day, time_block, allocation_size, target_grid",[
        (1,"08:00", "0.25", "DAY1:MCC"),
        (1,"08:00", "0.75", "DAY1:MCC"),
        (1,"08:00", "1", "DAY1:MCC"),
        (1,"12:30", "0.25", "DAY1:HCC1"),
        (1,"20:30", "0.75", "DAY1:HCC2"),
        (1,"15:00", "1", "DAY2:HCC1"),
        (1,"06:00", "0.25", "DAY3:MCC"),
        (1,"06:00", "0.75", "DAY3:MCC"),
        (1,"06:00", "1", "DAY3:MCC"),
    ]
)
def test_allocate_grid_both_not_allocated_but_displayed(test_client_factory,day,time_block,allocation_size,target_grid):
    # occurs when another row needs to split that time block
    # but this row has not been allocated yet so we get two empty cells
    # [left half (empty)][right half (empty)]
    # expect allocation size to be the clicked cell
    # e.g. :00 -> always 0.25, :30 -> always 0.75
    add_name_body1 = {"grid_name": target_grid, "name": "TEST"}
    add_name_body2 = {"grid_name": target_grid, "name": "TEST2"}
    manager = GridManager()
    client = test_client_factory(manager)
    response = client.post("/grid/add/", json=add_name_body1)
    assert response.status_code == 201
    response = client.post("/grid/add/", json=add_name_body2)
    assert response.status_code == 201

    allocate_right_body = {
        "grid_name": target_grid,
        "name": "TEST",
        "location": target_grid[5:],
        "allocation_size": "0.75",
        "time_block": time_block[:-2] + "30", 
    }

    response = client.post("/grid/allocate", json = allocate_right_body)
    assert response.status_code == 200

    body = {
        "grid_name": target_grid,
        "name": "TEST2",
        "location": target_grid[5:],
        "allocation_size": allocation_size,
        "time_block": time_block, 
    } 

    response = client.post("/grid/allocate", json = body)

    assert response.status_code == 200
    assert response.json()["allocation_size"] == ("0.25" if ":00" in time_block else "0.75")


