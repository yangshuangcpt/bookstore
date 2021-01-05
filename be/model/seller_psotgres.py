from sqlalchemy import create_engine, ForeignKey, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, VARCHAR, TEXT
from sqlalchemy.orm import sessionmaker, scoped_session
import error

engine = create_engine('postgresql+psycopg2://postgres:Wypsz.01@localhost/bookstore', encoding='utf-8', echo=True)
base = declarative_base()


class User(base):
    __tablename__ = 'user'
    user_id = Column('user_id', TEXT, primary_key=True)
    password = Column('password', TEXT, nullable=False)
    balance = Column('balance', Integer, nullable=False)
    token = Column('token', TEXT)
    terminal = Column('terminal ', TEXT)


class UserStore(base):
    __tablename__ = 'user_store'
    user_id = Column('user_id', TEXT, primary_key=True)
    store_id = Column('store_id', TEXT, primary_key=True)


class Store(base):
    __tablename__ = 'store'
    store_id = Column('store_id', Integer, primary_key=True)
    book_id = Column('book_id', TEXT, primary_key=True)
    book_info = Column('book_info', TEXT)
    stock_level = Column('stock_level', Integer)


class NewOrder(base):
    __tablename__ = 'new_order'
    order_id = Column('order_id', TEXT, primary_key=True)
    user_id = Column('user_id', TEXT)
    store_id = Column('store_id', TEXT)


class NewOrderDetail(base):
    __tablename__ = 'new_order_detail'
    order_id = Column('order_id ', TEXT, primary_key=True)
    book_id = Column('book_id', TEXT, primary_key=True)
    count = Column('count ', Integer)
    price = Column('price ', Integer)


Session = sessionmaker(bind=engine)
session = Session()


def user_id_exist(user_id):
    query = session.query(User).filter(User.user_id==user_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True


def book_id_exist(store_id, book_id):
    query = session.query(Store).filter(Store.store_id==store_id,Store.book_id==book_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True


def store_id_exist(self, store_id):
    query = session.query(UserStore).filter(UserStore.store_id==store_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True


def add_book(user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
    try:
        if not user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if book_id_exist(store_id, book_id):
            return error.error_exist_book_id(book_id)

        query = session.add(UserStore(store_id=store_id,book_id=book_id,book_info = book_json_str,stock_level=stock_level))
        session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


def add_stock_level(user_id: str, store_id: str, book_id: str, add_stock_level: int):
    try:
        if not user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if not book_id_exist(store_id, book_id):
            return error.error_non_exist_book_id(book_id)

        session.query(Store).filter(Store.store_id==store_id,Store.book_id==book_id).update(
            {Store.stock_level:add_stock_level}
        )
        session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


def create_store(user_id: str, store_id: str) -> (int, str):
    try:
        if not user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if store_id_exist(store_id):
            return error.error_exist_store_id(store_id)
        session.add(UserStore(store_id=store_id,user_id=user_id))
        session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"