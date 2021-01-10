from sqlalchemy import exc
import logging
import uuid
import json
from be.model import db_conn as db, error, store as st
import threading
import datetime
from datetime import timedelta


# 买家下单
def new_order(user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
    order_id = ""
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id) + (order_id,)
        if not db.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id) + (order_id,)
        uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

        for book_id, count in id_and_count:  # 对于订单中的每一类书
            query1 = db.session.query(st.Store).filter(st.Store.store_id == store_id, st.Store.book_id == book_id)
            row = query1.one_or_none()
            if row is None:
                return error.error_non_exist_book_id(book_id) + (order_id,)
            stock_level = row.stock_level
            book_info = row.book_info
            book_info_json = json.loads(book_info)
            price = book_info_json.get("price")

            if stock_level < count:
                return error.error_stock_level_low(book_id) + (order_id,)

            # 减少书店中书的库存量
            query2 = db.session.query(st.Store).filter(
                st.Store.store_id == store_id, st.Store.book_id == book_id, st.Store.stock_level >= count).update(
                {st.Store.stock_level: st.Store.stock_level - count}, synchronize_session="evaluate"
            )
            if query2 == 0:
                return error.error_stock_level_low(book_id) + (order_id,)

            # 新增一条订单详细信息
            db.session.add(st.NewOrderDetail(order_id=uid, book_id=book_id, count=count, price=price))

        # 新增一条订单信息
        db.session.add(st.NewOrder(order_id=uid, store_id=store_id, user_id=user_id, status=0))
        # 新增一条未付款订单消息
        time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        db.session.add(st.NotPayOrder(order_id=uid, ddl=time))
        db.session.commit()
        order_id = uid

    except exc.SQLAlchemyError as e:
        logging.info("528, {}".format(str(e)))
        return 528, "{}".format(str(e)), ""
    except BaseException as e:
        logging.info("530, {}".format(str(e)))
        return 530, "{}".format(str(e)), ""

    return 200, "ok", order_id


# 买家付款
def payment(user_id: str, password: str, order_id: str) -> (int, str):
    # conn = self.conn
    try:
        query = db.session.query(st.NotPayOrder).filter(st.NotPayOrder.order_id == order_id)
        row = query.one_or_none()
        if row is None:
            return error.error_invalid_order_id(order_id)
        # 找到订单信息
        query1 = db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id)
        row = query1.one_or_none()
        if row is None:
            return error.error_invalid_order_id(order_id)

        order_id = row.order_id
        buyer_id = row.user_id
        store_id = row.store_id

        if buyer_id != user_id:
            return error.error_authorization_fail()

        # 查看买家用户余额是否足够
        query2 = db.session.query(st.User).filter(st.User.user_id == buyer_id)
        row = query2.one_or_none()
        if row is None:
            return error.error_non_exist_user_id(buyer_id)
        balance = row.balance
        if password != row.password:
            return error.error_authorization_fail()

        # 获取卖家id
        query3 = db.session.query(st.UserStore).filter(st.UserStore.store_id == store_id)
        row = query3.one_or_none()
        if row is None:
            return error.error_non_exist_store_id(store_id)

        seller_id = row.user_id

        if not db.user_id_exist(seller_id):
            return error.error_non_exist_user_id(seller_id)

        # 获取订单详细信息
        query4 = db.session.query(st.NewOrderDetail).filter(st.NewOrderDetail.order_id == order_id).all()
        total_price = 0
        for row in query4:  # 查看每一本书的情况，计算订单总金额
            count = row.count
            price = row.price
            total_price = total_price + price * count

        if balance < total_price:
            return error.error_not_sufficient_funds(order_id)

        # 买家账户扣钱
        query5 = db.session.query(st.User).filter(st.User.user_id == buyer_id, st.User.balance >= total_price).update(
            {st.User.balance: st.User.balance - total_price}, synchronize_session="evaluate")

        if query5 == 0:
            return error.error_not_sufficient_funds(order_id)

        # 卖家账户加钱
        query6 = db.session.query(st.User).filter(st.User.user_id == seller_id).update(
            {st.User.balance: st.User.balance + total_price}, synchronize_session="evaluate")

        if query6 == 0:
            return error.error_non_exist_user_id(buyer_id)

        #  付款完成，更改订单状态
        query7 = db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id).update(
            {st.NewOrder.status: 1}
        )

        if query7 == 0:
            return error.error_invalid_order_id(order_id)

        # 订单完成删除两个表中的订单信息
        # query7 = db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id).delete()
        # if query7 == 0:
        #    return error.error_invalid_order_id(order_id)

        # query8 = db.session.query(st.NewOrderDetail).filter(st.NewOrderDetail.order_id == order_id).delete()
        # if query8 == 0:
        #    return error.error_invalid_order_id(order_id)
        # 删除未支付表中订单信息
        db.session.query(st.NotPayOrder).filter(st.NotPayOrder.order_id == order_id).delete()
        db.session.commit()

    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))

    except BaseException as e:
        return 530, "{}".format(str(e))

    return 200, "ok"


# 买家充值
def add_funds(user_id, password, add_value) -> (int, str):
    try:
        query1 = db.session.query(st.User).filter(st.User.user_id == user_id)
        row = query1.one_or_none()
        if row is None:
            return error.error_authorization_fail()

        if row.password != password:
            return error.error_authorization_fail()

        query2 = db.session.query(st.User).filter(st.User.user_id == user_id).update(
            {st.User.balance: st.User.balance + add_value}, synchronize_session="evaluate")
        if query2 == 0:
            return error.error_non_exist_user_id(user_id)

        db.session.commit()

    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))

    return 200, "ok"


def shipping(user_id: str, order_id: str):
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        # 订单是否存在
        query1 = db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id)
        row = query1.one_or_none()
        if row is None:
            return error.error_invalid_order_id(order_id)
        # 订单的买卖家信息是否正确
        if not row.user_id == user_id:
            return error.error_authorization_fail()
        # 查看订单是否发货
        if row.status != 2:
            return error.error_not_receive(order_id)

        # 订单完成，更改订单状态
        query2 = db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id).update(
            {st.NewOrder.status: 3}
        )
        if query2 == 0:
            return error.error_invalid_order_id(order_id)
        db.session.commit()

    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))

    except BaseException as e:
        return 530, "{}".format(str(e))

    return 200, "ok"


def history(user_id: str):
    try:
        if not db.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        query1 = db.session.query(st.NewOrder).join(st.NewOrderDetail,st.NewOrder.order_id == st.NewOrderDetail.order_id).filter(
            st.NewOrder.user_id == user_id
        )
        row = query1.all()
        print(row)
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))

    except BaseException as e:
        return 530, "{}".format(str(e))

    return 200, "ok"


def cancel_order(buyer_id: str, order_id: str):
    try:
        if not db.user_id_exist(buyer_id):
            return error.error_non_exist_user_id(buyer_id)
        # 订单是否存在
        query1 = db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id)
        row = query1.one_or_none()
        if row is None:
            return error.error_invalid_order_id(order_id)
        status = row.status  # 订单状态
        store_id = row.store_id  # 卖家店铺
        query2 = db.session.query(st.UserStore).filter(st.UserStore.store_id == store_id).one_or_none()
        seller_id = query2.user_id  # 卖家用户名
        if status == 0:  # 用户下单(0)后取消
            # 查看是否在未付款订单中
            queryx = db.session.query(st.NotPayOrder).filter(st.NotPayOrder.order_id == order_id).one_or_none()
            if queryx is None:
                return error.error_invalid_order_id(order_id)
            # 删除在未付款表中的此订单
            db.session.query(st.NotPayOrder).filter(st.NotPayOrder.order_id == order_id).delete()
            # 更改订单状态
            db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id).update(
                {st.NewOrder.status: -1}
            )
            # 更改卖家库存
            query3 = db.session.query(st.NewOrderDetail).filter(st.NewOrderDetail.order_id == order_id).all()
            for row1 in query3:  # 查看订单中每一类书的情况，更改卖家信息
                count = row1.count
                book_id = row1.book_id
                query4 = db.session.query(st.Store).filter(st.Store.store_id == store_id, st.Store.book_id == book_id)
                row2 = query4.one_or_none()
                if row2 is None:
                    return error.error_non_exist_book_id(book_id)

                # 增加书店中书的库存量
                query5 = db.session.query(st.Store).filter(
                    st.Store.store_id == store_id, st.Store.book_id == book_id).update(
                    {st.Store.stock_level: st.Store.stock_level + count}, synchronize_session="evaluate"
                )
                if query5 == 0:
                     return error.error_stock_level_low(book_id)
        elif status == 1 or status == 2:  # 用户付款，或卖家发货后取消订单
            # 更改订单状态
            db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id).update(
                {st.NewOrder.status: -1}
            )

            # 查找订单金额
            query6 = db.session.query(st.NewOrderDetail).filter(st.NewOrderDetail.order_id == order_id).all()
            total_price = 0
            for row4 in query6:  # 查看每一本书的情况，计算订单总金额
                count = row4.count
                price = row4.price
                total_price = total_price + price * count
            # 更改账户余额
            # 买家加钱
            query7 = db.session.query(st.User).filter(st.User.user_id == buyer_id).update(
                {st.User.balance: st.User.balance + total_price}, synchronize_session="evaluate")

            # 卖家账户扣钱
            query8 = db.session.query(st.User).filter(st.User.user_id == seller_id, st.User.balance>=total_price).update(
                {st.User.balance: st.User.balance - total_price}, synchronize_session="evaluate")
            if query8 == 0:
                return error.error_not_sufficient_funds(order_id)

        else:
            # 用户已付款或订单已经取消，无法取消订单
            return error.error_invalid_order_id(order_id)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))

    except BaseException as e:
        return 530, "{}".format(str(e))

    return 200, "ok"


def auto_cancel_order():
    # time = datetime.utcnow() + datetime.timedelta(minutes=5)
    now = datetime.datetimeutcnow()
    query = db.session.query(st.NotPayOrder).filter(st.NotPayOrder(st.NotPayOrder.ddl >= now)).all()
    if len(query) > 0:
        for row in query:
            order_id = row.order_id
            db.session.query(st.NotPayOrder).filter(st.NotPayOrder == order_id).delete()
            # 更改这些订单的状态
            query1 = db.session.query(st.NewOrder).filter(st.NewOrder.order_id == order_id).update(
                {st.NewOrder.status: -1}
            )
        db.session.commit()
    else:
        return 'no order to cancel'
    return 'ok'


def create_timer():
    while True:
        timer = threading.Timer(1, auto_cancel_order())
        timer.start()
