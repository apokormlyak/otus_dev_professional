import hashlib


import pytest
from .homework_3.my_app.store import Store


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    Store().clear_cache()


@pytest.fixture()
def fill_get_interests_cache():
    k, v = 0, ["cars", "pets"]
    key = "uid:" + hashlib.md5("".join(str(k)).encode("utf-8")).hexdigest()
    return Store().cache_set(key, v, 60)


@pytest.fixture()
def fill_get_score_cache():
    key_parts = ["first_name", "last_name", "", ""]
    key = "uid:" + hashlib.md5("".join(str(key_parts)).encode("utf-8")).hexdigest()
    return Store().cache_set(key, 20, 60)
