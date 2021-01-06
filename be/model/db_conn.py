from model import store
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=store.engine)
session = Session()

def user_id_exist(user_id):
    query = session.query(store.User).filter(store.User.user_id == user_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True


def book_id_exist(store_id, book_id):
    query = session.query(store.Store).filter(store.Store.store_id == store_id, store.Store.book_id == book_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True


def store_id_exist(store_id):
    query = session.query(store.UserStore).filter(store.UserStore.store_id == store_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True
