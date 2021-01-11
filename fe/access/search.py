import requests
import simplejson
from urllib.parse import urljoin
from fe.access.auth import Auth


class Searcher:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "search/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def search_title(self,  title: str, number: int) -> int:
        json = {
            "title": title,
            "number": number
        }
        url = urljoin(self.url_prefix, "search_title")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def search_author(self,  author: str, number: int) -> int:
        json = {
            "author": author,
            "number": number
        }
        url = urljoin(self.url_prefix, "search_author")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def search_tags(self,  tags: str, number: int) -> int:
        json = {
            "tags": tags,
            "number": number
        }
        url = urljoin(self.url_prefix, "search_tags")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def search_details(self,  details: str, number: int) -> int:
        json = {
            "details": details,
            "number": number
        }
        url = urljoin(self.url_prefix, "search_details")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
