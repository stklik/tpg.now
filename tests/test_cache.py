import pytest
from datetime import datetime, timedelta
from time import sleep
from tpgnow.cache import Cache
from tpgnow.model import Stop

TIME_DELAY = 5

class TestCache(object):

    @pytest.fixture
    def cache(self):
        return Cache()

    @pytest.fixture
    def key(self):
        return "key"

    @pytest.fixture
    def value(self):
        return "value"

    def test_noWrite_read(self, cache, key):
        assert cache.read(key) is None

    def test_writeAndReadString(self, cache, key, value):
        cache.write(key, value)
        assert cache.read(key) is value

    def test_writeAndReadObject(self, cache, key):
        value = Stop("code", "name")
        cache.write(key, value)
        assert cache.read(key) is value

    def test_cacheReadBeforeTimeoutDelay(self, cache, key, value):
        cache.write(key, value, delay=5)  # seconds
        sleep(TIME_DELAY-2)
        assert cache.read(key) is value

    def test_cacheReadBeforeTimeoutDate(self, cache, key, value):
        inTenSeconds = datetime.now() + timedelta(seconds=TIME_DELAY)
        cache.write(key, value, timeout=inTenSeconds)  # seconds
        sleep(TIME_DELAY-2)
        assert cache.read(key) is value

    def test_cacheReadAfterTimeout(self, cache, key, value):
        cache.write(key, value, delay=TIME_DELAY)  # seconds
        sleep(TIME_DELAY+2)
        assert cache.read(key) is None

    def test_cacheReadAfterTimeout_assertKeyDeleted(self, cache, key, value):
        cache.write(key, value, delay=TIME_DELAY)  # seconds
        sleep(TIME_DELAY+2)
        cache.read(key)
        assert key not in cache.store

    def test_noWriteHas(self, cache, key):
        assert not cache.has(key)

    def test_writeHas(self, cache, key, value):
        cache.write(key, value)
        assert cache.has(key)

    def test_hasBeforeTimeoutDelay(self, cache, key, value):
        cache.write(key, value, delay=5)  # seconds
        sleep(TIME_DELAY-2)
        assert cache.has(key)

    def test_hasBeforeTimeoutDate(self, cache, key, value):
        inTenSeconds = datetime.now() + timedelta(seconds=TIME_DELAY)
        cache.write(key, value, timeout=inTenSeconds)  # seconds
        sleep(TIME_DELAY-2)
        assert cache.has(key)

    def test_hasAfterTimeout(self, cache, key, value):
        cache.write(key, value, delay=TIME_DELAY)  # seconds
        sleep(TIME_DELAY+2)
        assert not cache.has(key)

    def test_cacheReadAfterTimeout_assertKeyDeleted(self, cache, key, value):
        cache.write(key, value, delay=TIME_DELAY)  # seconds
        sleep(TIME_DELAY+2)
        cache.has(key)
        assert key not in cache.store

    def test_singleton(self):
        cache1 = Cache.Instance()
        cache2 = Cache.Instance()
        assert cache1 is cache2
