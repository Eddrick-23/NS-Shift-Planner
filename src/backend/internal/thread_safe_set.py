from threading import Lock

class ThreadSafeSet():
    def __init__(self):
        self._set = set()
        self._lock = Lock()

    def add(self,item):
        with self._lock:
            self._set.add(item)

    def remove(self,item):
        with self._lock:
            self._set.remove(item)
    
    def __contains__(self,item):
        with self._lock:
            return item in self._set
