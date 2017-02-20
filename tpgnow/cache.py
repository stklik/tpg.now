from datetime import datetime, timedelta

""" there exist better solutions, but I want something easy for now..."""

class CacheEntry(object):
    timestamp = None  # datetime
    timeout = None  # datetime
    value = None  # anything

class Cache(object):
    instance = None  # singleton

    def __init__(self):
        self.store = dict()

    @staticmethod
    def Instance():
        if not Cache.instance:
            Cache.instance = Cache()
        return Cache.instance

    def write(self, key, value, delay=None, timeout=None):
        now = datetime.now()

        entry = CacheEntry()
        entry.value = value
        entry.timestamp = now

        if timeout:
            entry.timeout = timeout
        elif delay:
            entry.timeout = now + timedelta(seconds=delay)

        self.store[key] = entry

    def read(self, key):
        if self.has(key):
            return  self.store[key].value

    def has(self, key):
        now = datetime.now()

        if key not in self.store:  # no entry with this key, return None
            return False

        if not self.store[key].timeout:  # no timeout defined, return value
            return True



        if now < self.store[key].timeout:  # timeout not reached, return value
            return True
        else:  # too late, return None, but delete key first
            self.store.pop(key, None)
            return False
