import pytest

from ...my_app import api
from ...my_app.store import Store as store


class setUp:
    def __init__(self):
        self.context = {}
        self.headers = {}
        self.store = store


class TestUnits:
    set_up = setUp()

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.set_up.headers},
                                  self.set_up.context, self.set_up.store)

    def test_empty_request(self):
        _, code = self.get_response({})
        assert api.INVALID_REQUEST == code

