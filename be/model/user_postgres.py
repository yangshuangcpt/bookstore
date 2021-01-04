import jwt
import time
import logging
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


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.decode("utf-8")


def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


token_lifetime: int = 3600


def check_token(user_id, db_token, token) -> bool:
    try:
        if db_token != token:
            return False
        jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
        ts = jwt_text["timestamp"]
        if ts is not None:
            now = time.time()
            if token_lifetime > now - ts >= 0:
                return True
    except jwt.exceptions.InvalidSignatureError as e:
        logging.error(str(e))
        return False


def register(user_id: str, password: str):
    try:
        terminal = "terminal_{}".format(str(time.time()))
        token = jwt_encode(user_id, terminal)
        session.add(User(user_id=user_id, password=password, balance=0, token=token, terminal=terminal))
        session.commit()
    except exc.SQLAlchemyError:
        return error.error_exist_user_id(user_id)
    return 200, "ok"


def check_token(self, user_id: str, token: str) -> (int, str):
    query1 = session.query(User.token).filter(User.user_id == user_id)
    row = query1.one_or_none()
    if row is None:
        return error.error_authorization_fail()
    db_token = row[0]
    if not check_token(user_id, db_token, token):
        return error.error_authorization_fail()
    return 200, "ok"


def check_password(user_id: str, password: str) -> (int, str):
    query1 = session.query(User.password).filter(User.user_id == user_id)
    row = query1.one_or_none()
    if row is None:
        return error.error_authorization_fail()
    if password != row[0]:
        return error.error_authorization_fail()

    return 200, "ok"


def login(user_id: str, password: str, terminal: str) -> (int, str, str):
    token = ""
    try:
        code, message = check_password(user_id, password)
        if code != 200:
            return code, message, ""

        token = jwt_encode(user_id, terminal)
        query1 = session.query(User).filter(User.user_id == user_id).update(
            {User.token: token, User.terminal: terminal}
        )
        if query1 == 0:
            return error.error_authorization_fail() + ("",)
        session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e)), ""
    except BaseException as e:
        return 530, "{}".format(str(e)), ""
    return 200, "ok", token


def logout(user_id: str, token: str) -> bool:
    try:
        code, message = check_token(user_id, token)
        if code != 200:
            return code, message

        terminal = "terminal_{}".format(str(time.time()))
        dummy_token = jwt_encode(user_id, terminal)

        query1 = session.query(User).filter(User.user_id==user_id).update(
            {User.token:dummy_token,User.terminal:terminal}
        )
        if query1 == 0:
            return error.error_authorization_fail()

        session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


def unregister(user_id: str, password: str) -> (int, str):
    try:
        code, message = check_password(user_id, password)
        if code != 200:
            return code, message

        query1 = session.query(User).filter(User.user_id==user_id).delete()
        if query1 == 1:
            session.commit()
        else:
            return error.error_authorization_fail()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"

def change_password(user_id: str, old_password: str, new_password: str) -> bool:
    try:
        code, message = check_password(user_id, old_password)
        if code != 200:
            return code, message

        terminal = "terminal_{}".format(str(time.time()))
        token = jwt_encode(user_id, terminal)
        query1 = session.query(User).filter(User.user_id==user_id).update(
            {User.password:new_password,User.token:token,User.terminal:terminal}
        )
        if query1 == 0:
            return error.error_authorization_fail()

        session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
