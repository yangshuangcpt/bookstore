from sqlalchemy import create_engine, ForeignKey, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, VARCHAR, TEXT
from sqlalchemy.orm import sessionmaker, scoped_session
import error
import store as st
import db_conn as db


def add_book(user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not db.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if db.book_id_exist(store_id, book_id):
            return error.error_exist_book_id(book_id)

        query = db.session.add(
            st.UserStore(store_id=store_id, book_id=book_id, book_info=book_json_str, stock_level=stock_level))
        db.session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


def add_stock_level(user_id: str, store_id: str, book_id: str, add_stock_level: int):
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not db.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if not db.book_id_exist(store_id, book_id):
            return error.error_non_exist_book_id(book_id)

        db.session.query(st.Store).filter(st.Store.store_id == store_id, st.Store.book_id == book_id).update(
            {st.Store.stock_level: add_stock_level}
        )
        db.session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


def create_store(user_id: str, store_id: str) -> (int, str):
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if db.store_id_exist(store_id):
            return error.error_exist_store_id(store_id)
        db.session.add(st.UserStore(store_id=store_id, user_id=user_id))
        db.session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


# def receiving(order_id: str)