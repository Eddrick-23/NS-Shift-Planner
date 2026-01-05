import pytest
from pytest_mock import MockerFixture
import asyncio
from src.backend.app import prune_expired_sessions
from src.backend.app import scan_cache
from src.backend.internal.lru_cache import CustomLRUCache
from src.backend.internal.grid_manager import GridManager
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_db_prune_pops_cache(mocker: MockerFixture):
    """
    During db pruning, when a session is pruned, that id should also be removed from lru cache instance, if present.
    """
    test_manager_cache = CustomLRUCache(10, None)
    mock_db_client = MagicMock()

    # create caches with items
    test_manager_cache["testid"] = None

    # mock db_operation
    mock_database_remove_expired = mocker.patch(
        "src.backend.app.database_remove_expired"
    )
    mock_database_remove_expired.return_value = ["testid"]

    # mock to break loop
    mock_sleep = mocker.patch("asyncio.sleep")
    mock_sleep.side_effect = asyncio.CancelledError

    try:
        await prune_expired_sessions(
            mock_db_client, "mock_collection", test_manager_cache, 24
        )
    except asyncio.CancelledError:
        pass

    assert "testid" not in test_manager_cache

@pytest.mark.asyncio
async def test_scan_cache(mocker: MockerFixture):
    test_manager_cache = CustomLRUCache(2, None)
    test_manager = GridManager()
    test_manager.requires_sync = True

    test_manager_cache["testid"] = test_manager
    mock_cache_sync_to_firebase = mocker.patch.object(
        test_manager_cache, "sync_to_firebase"
    )

    await scan_cache(test_manager_cache, 1, True)

    mock_cache_sync_to_firebase.assert_called_once()
