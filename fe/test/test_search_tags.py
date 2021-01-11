import pytest
from fe.access.new_searcher import register_new_searcher
import uuid
import time

class TestSearchTags:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.user_id = "test_search_tags_user_{}".format(time.time())
        self.password = "test_search_tags_password_{}".format(time.time())
        self.user = register_new_searcher(self.user_id, self.password)
        self.tags = "小说"
        self.number = 1
        yield
        # do after test

    def test_ok(self):
        code = self.user.search_tags(self.tags, self.number)
        assert code == 200

    def test_error_no_tags(self):
        code = self.user.search_tags(self.tags + "x", self.number)
        assert code != 200


