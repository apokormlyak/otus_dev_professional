import datetime

import pytest

from ...my_app import api
from ...my_app.store import Store
from ...my_app.scoring import get_score
from ...my_app.scoring import get_interests


class setUp:
    def __init__(self):
        self.context = {}
        self.headers = {}
        self.store = Store()


class TestUnits:
    set_up = setUp()

    def get_response(self, request):
        return api.method_handler(
            {"body": request, "headers": self.set_up.headers},
            self.set_up.context,
            self.set_up.store,
        )

    def test_empty_request(self):
        _, code = self.get_response({})
        assert api.INVALID_REQUEST == code

    @pytest.mark.parametrize(
        "arguments, result",
        [
            ({}, 0),
            ({"phone": 1}, 1.5),
            ({"email": 1}, 1.5),
            ({"birthday": datetime.datetime.strptime("20000102", "%Y%m%d")}, 0),
            ({"gender": 1}, 0),
            (
                {
                    "birthday": datetime.datetime.strptime("20000101", "%Y%m%d"),
                    "gender": 1,
                },
                1.5,
            ),
            ({"first_name": 1}, 0),
            ({"last_name": 1}, 0),
            ({"first_name": 1, "last_name": 1}, 0.5),
            (
                {
                    "phone": 1,
                    "email": 1,
                    "birthday": datetime.datetime.strptime("20000101", "%Y%m%d"),
                    "gender": 1,
                    "first_name": 1,
                    "last_name": 1,
                },
                5,
            ),
        ],
    )
    def test_ok_get_score_no_cache(self, arguments, result):
        arguments.update({"store": self.set_up.store})
        request_result = get_score(**arguments)
        assert request_result == result

    @pytest.mark.parametrize(
        "arguments, result",
        [
            ({"first_name": "first_name", "last_name": "last_name"}, 20),
        ],
    )
    def test_ok_get_score_with_cache(self, fill_get_score_cache, arguments, result):
        arguments.update({"store": self.set_up.store})
        request_result = get_score(**arguments)
        assert request_result == result

    @pytest.mark.parametrize(
        "arguments, result",
        [
            (None, {"None": []}),
            (0, {"0": []}),
            (1, {"1": []}),
        ],
    )
    def test_ok_get_interests_no_cache(self, arguments, result):
        store = self.set_up.store
        request_result = get_interests(store, arguments)
        assert request_result == result

    @pytest.mark.parametrize(
        "arguments, result",
        [
            ("0", ["pets", "cars"]),
        ],
    )
    def test_ok_get_interests_with_cache(
        self, fill_get_interests_cache, arguments, result
    ):
        store = self.set_up.store
        request_result = get_interests(store, arguments)
        assert all(x in result for x in request_result["0"])
        assert len(set(result)) == len(set(request_result["0"]))
