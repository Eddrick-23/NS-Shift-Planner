"""
LRU cache that wraps cachetools LRUCache

On evict, the GridManager class is intercepted and the data is saved to firebase
"""

import logging
import base64
import threading
from cachetools import LRUCache
from datetime import datetime, timedelta, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from src.backend.internal.grid_manager import GridManager
from src.backend.config import config


class CustomLRUCache(LRUCache):
    def __init__(self, maxsize, firebase_client=None, **kwargs):
        super().__init__(maxsize, **kwargs)
        self._lock = threading.RLock()
        self.firebase = firebase_client
        self.__DB_COLLECTION_NAME = config.DB_COLLECTION_NAME

    # keep method synchronous to override original
    def popitem(self):
        with self._lock:
            session_id, grid_manager = super().popitem()
            if grid_manager.requires_sync:
                self.sync_to_firebase(session_id, grid_manager)
            return session_id, grid_manager
    
    def __getitem__(self, key):
        with self._lock:
            return super().__getitem__(key)

    def __setitem__(self, key, value):
        with self._lock:
            return super().__setitem__(key, value)

    def __delitem__(self, key):
        with self._lock:
            return super().__delitem__(key)

    def __contains__(self, key):
        with self._lock:
            return super().__contains__(key)

    def get(self, key, default=None):
        with self._lock:
            return super().get(key, default)

    def sync_to_firebase(self, session_id: str, manager: GridManager) -> bool:
        """
        Sync GridManager data to firebase

        Args:
            session_id(str): session id to sync data under
            manager(str): GridManager instance for this session id
        """
        try:
            zip_bytes = manager.serialise_to_zip()
            encoded_zip = base64.b64encode(zip_bytes).decode("utf-8")

            doc_id = f"session_id:{session_id}"
            doc_ref = self.firebase.collection(self.__DB_COLLECTION_NAME).document(doc_id)
            updated = datetime.now(timezone.utc)
            expire_at = updated + timedelta(days=1)

            doc_ref.set(
                {
                    "updated": updated,
                    "expireAt": expire_at,
                    "data": encoded_zip,
                    "size": len(zip_bytes),
                    "session_id":session_id
                }
            )
            manager.requires_sync = False
            logging.info("Synced session %s to Firestore", session_id)

        except Exception as e:
            logging.error(
                "Failed to sync session %s to Firestore: %s", session_id, e
            )


if __name__ == "__main__":
    cred_path = config.GOOGLE_APPLICATION_CREDENTIALS
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

    # Initialize Firestore client
    db = firestore.client()

    cache = CustomLRUCache(2, db)

    manager1 = GridManager()
    manager2 = GridManager()
    manager3 = GridManager()

    cache["session-A"] = manager1  # should be popped and synced
    cache["session-B"] = manager2
    cache["session-C"] = manager3
