from src.message_cache import CachedMsg, MessageCache


def test_push_and_get():
    cache = MessageCache()
    cache.push("chan", CachedMsg("first", "alice"))
    cache.push("chan", CachedMsg("second", "bob"))

    assert cache.get("chan", 0).message == "second"
    assert cache.get("chan", 1).message == "first"
    # out-of-range index
    assert cache.get("chan", 2) is None
    # non-existent channel
    assert cache.get("other", 0) is None


def test_buffer_capacity_limit():
    cache = MessageCache()
    for i in range(MessageCache.BUFFER_CAPACITY + 10):
        cache.push("chan", CachedMsg(str(i), "user"))

    assert cache.get("chan", MessageCache.BUFFER_CAPACITY) is None
    assert cache.get("chan", MessageCache.BUFFER_CAPACITY - 1).message == "10"
