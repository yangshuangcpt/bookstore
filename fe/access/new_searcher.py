from fe import conf
from fe.access import search, auth


def register_new_searcher(user_id, password) -> search.Searcher:
    a = auth.Auth(conf.URL)
    code = a.register(user_id, password)
    assert code == 200
    s = search.Searcher(conf.URL, user_id, password)
    return s
