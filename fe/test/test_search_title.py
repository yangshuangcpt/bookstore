import pytest
from fe.access.new_searcher import register_new_searcher
import uuid
import time


class TestSearchTitle:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.user_id = "test_search_title_user_{}".format(time.time())
        self.password = "test_search_title_password_{}".format(time.time())
        self.user = register_new_searcher(self.user_id, self.password)
        self.title = "美丽心灵"
        self.number = 1
        yield
        # do after test

    def test_ok(self):
        code = self.user.search_title(self.title, self.number)
        assert code == 200

    def test_error_no_title(self):
        code = self.user.search_title(self.title + "x", self.number)
        assert code != 200


