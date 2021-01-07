from sqlalchemy import exc
from model import db_conn as db, error, store as st


# 添加书籍信息
def add_book(user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not db.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if db.book_id_exist(store_id, book_id):
            return error.error_exist_book_id(book_id)

        query = db.session.add(
            st.Store(store_id=store_id, book_id=book_id, book_info=book_json_str, stock_level=stock_level))
        db.session.commit()

    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


# 增加库存
def add_stock_level(user_id: str, store_id: str, book_id: str, add_stock_level: int):
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not db.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if not db.book_id_exist(store_id, book_id):
            return error.error_non_exist_book_id(book_id)

        db.session.query(st.Store).filter(st.Store.store_id == store_id, st.Store.book_id == book_id).update(
            {st.Store.stock_level: st.Store.stock_level+add_stock_level}, synchronize_session="evaluate"
        )
        db.session.commit()

    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


# 创建商铺
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


def receiving(user_id: str, store_id: str, order_id: str):
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if db.store_id_exist(store_id):
            return error.error_exist_store_id(store_id)
        # 订单是否存在
        query1 = db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id)
        row = query1.one_or_none()
        if row is None:
            return error.error_invalid_order_id(order_id)
        # 订单的买卖家信息是否正确
        if not (row.user_id == user_id and row.store_id == store_id):
            return error.error_authorization_fail()
        # 查看订单是否付款
        if row.status!=1:
            return error.error_not_pay(order_id)
        # 更改订单状态：已发货
        db.session.query(st.NewOrder).filter(st.NewOrder.order_id==order_id).update(
            {st.NewOrder.status:2}
        )
        db.session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
