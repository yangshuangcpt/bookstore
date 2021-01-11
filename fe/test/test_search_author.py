import pytest
from fe.access.new_searcher import register_new_searcher
import uuid
import time

class TestSearchAuthor:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.user_id = "test_search_author_user_{}".format(time.time())
        self.password = "test_search_author_password_{}".format(time.time())
        self.user = register_new_searcher(self.user_id, self.password)
        self.author = "杨红樱"
        self.number = 1
        yield
        # do after test

    def test_ok(self):
        code = self.user.search_author(self.author, self.number)
        assert code == 200

    def test_error_no_author(self):
        code = self.user.search_author(self.author + "x", self.number)
        assert code != 200


