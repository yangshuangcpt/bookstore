from sqlalchemy import create_engine, ForeignKey, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, VARCHAR, TEXT
from sqlalchemy.orm import sessionmaker, scoped_session
import error
import logging
import uuid
import json

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
    query = session.query(User).filter(User.user_id == user_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True


def book_id_exist(store_id, book_id):
    query = session.query(Store).filter(Store.store_id == store_id, Store.book_id == book_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True


def store_id_exist(self, store_id):
    query = session.query(UserStore).filter(UserStore.store_id == store_id)
    row = query.one_or_none()
    if row is None:
        return False
    else:
        return True


def new_order(user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
    order_id = ""
    try:
        if not user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id) + (order_id,)
        if not store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id) + (order_id,)
        uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

        for book_id, count in id_and_count:
            query1 = session.query(Store).filter(Store.store_id == store_id, Store.book_id == book_id)
            row = query1.one_or_none()
            if row is None:
                return error.error_non_exist_book_id(book_id) + (order_id,)
            stock_level = row.stock_level
            book_info = row.book_info
            book_info_json = json.loads(book_info)
            price = book_info_json.get("price")

            if stock_level < count:
                return error.error_stock_level_low(book_id) + (order_id,)

            query2 = session.query(Store).filter(
                Store.store_id == store_id, Store.book_id == book_id, Store.stock_level >= count).undate(
                {Store.stock_level: Store.stock_level - count}
            )
            if query2 == 0:
                return error.error_stock_level_low(book_id) + (order_id,)

            session.add(NewOrderDetail(order_id=uid, book_id=book_id, count=count, price=price))

        session.add(NewOrder(order_id=uid, store_id=store_id, user_id=user_id))
        session.commit()
        order_id = uid
    except exc.SQLAlchemyError as e:
        logging.info("528, {}".format(str(e)))
        return 528, "{}".format(str(e)), ""
    except BaseException as e:
        logging.info("530, {}".format(str(e)))
        return 530, "{}".format(str(e)), ""

    return 200, "ok", order_id


def payment(user_id: str, password: str, order_id: str) -> (int, str):
    # conn = self.conn
    try:
        query1 = session.query(NewOrder).filter(NewOrder.order_id == order_id)
        row = query1.one_or_none()
        if row is None:
            return error.error_invalid_order_id(order_id)

        order_id = row.order_id
        buyer_id = row.buyer_id
        store_id = row.store_id

        if buyer_id != user_id:
            return error.error_authorization_fail()

        query2 = session.query(User).filter(User.user_id == buyer_id)
        row = query2.one_or_none()
        if row is None:
            return error.error_non_exist_user_id(buyer_id)
        balance = row.balance
        if password != row.password:
            return error.error_authorization_fail()

        query3 = session.query(UserStore).filter(UserStore.store_id == store_id)
        row = query3.one_or_none()
        if row is None:
            return error.error_non_exist_store_id(store_id)

        seller_id = row.user_id

        if not user_id_exist(seller_id):
            return error.error_non_exist_user_id(seller_id)

        query4 = session.query(NewOrderDetail).filter(NewOrderDetail.order_id == order_id).all()
        # cursor = conn.execute("SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;", (order_id,))
        total_price = 0
        for row in query4:
            count = row.count
            price = row.price
            total_price = total_price + price * count

        if balance < total_price:
            return error.error_not_sufficient_funds(order_id)

        query5 = session.query(User).filter(User.user_id == buyer_id, User.balance >= total_price).update(
            {User.balance: User.balance - total_price})

        if query5 == 0:
            return error.error_not_sufficient_funds(order_id)

        query6 = session.query(User).filter(User.user_id == buyer_id).update({User.balance: User.balance + total_price})

        if query6 == 0:
            return error.error_non_exist_user_id(buyer_id)

        query7 = session.query(NewOrder).filter(NewOrder.order_id == order_id).delete()
        if query7 == 0:
            return error.error_invalid_order_id(order_id)

        query8 = session.query(NewOrderDetail).filter(NewOrderDetail.order_id == order_id).delete()
        if query8 == 0:
            return error.error_invalid_order_id(order_id)

        session.commit()

    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))

    except BaseException as e:
        return 530, "{}".format(str(e))

    return 200, "ok"


def add_funds(user_id, password, add_value) -> (int, str):
    try:
        query1 = session.query(User).filter(User.user_id == user_id)
        row = query1.one_or_none()
        if row is None:
            return error.error_authorization_fail()

        if row.password != password:
            return error.error_authorization_fail()

        query2 = session.query(User).filter(User.user_id == user_id).update({User.balance: User.balance + add_value})
        if query2 == 0:
            return error.error_non_exist_user_id(user_id)

        session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))

    return 200, "ok"
