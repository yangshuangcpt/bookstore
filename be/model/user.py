import jwt  # 用户认证
import time
import logging
from sqlalchemy import exc
from be.model import db_conn as db, error, store as st


def jwt_encode(user_id: str, terminal: str) -> str:  # ->是函数返回类型的注释，无实际意义
    encoded = jwt.encode(   # 生成 jwt， bytes 类型的 base64 编码
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded   # .decode("utf-8")  # 以utf-8解码


def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


token_lifetime: int = 3600  # 3600 second


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


# 检查token是否有效
def _check_token(user_id, db_token, token) -> bool:
    try:
        if db_token != token:
            return False
        jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
        ts = jwt_text["timestamp"]
        if ts is not None:
            now = time.time()
            if token_lifetime > now - ts >= 0:  # token有效
                return True
    except jwt.exceptions.InvalidSignatureError as e:
        logging.error(str(e))
        return False


# 用户注册
def register(user_id: str, password: str):
    try:
        terminal = "terminal_{}".format(str(time.time()))
        token = jwt_encode(user_id, terminal)
        db.session.add(st.User(user_id=user_id, password=password, balance=0, token=token, terminal=terminal))
        db.session.commit()
    except exc.SQLAlchemyError:
        return error.error_exist_user_id(user_id)
    return 200, "ok"


def check_token(user_id: str, token: str) -> (int, str):
    query1 = db.session.query(st.User).filter(st.User.user_id == user_id)
    row = query1.one_or_none()
    if row is None:
        return error.error_authorization_fail()
    db_token = row.token
    if not _check_token(user_id, db_token, token):
        return error.error_authorization_fail()
    return 200, "ok"


def check_password(user_id: str, password: str) -> (int, str):
    query1 = db.session.query(st.User).filter(st.User.user_id == user_id)
    row = query1.one_or_none()
    if row is None:
        return error.error_authorization_fail()
    if password != row.password:
        return error.error_authorization_fail()

    return 200, "ok"


# 用户登录
def login(user_id: str, password: str, terminal: str) -> (int, str, str):
    token = ""
    try:
        code, message = check_password(user_id, password)
        if code != 200:
            return code, message, ""

        token = jwt_encode(user_id, terminal)
        query1 = db.session.query(st.User).filter(st.User.user_id == user_id).update(
            {st.User.token: token, st.User.terminal: terminal}
        )
        if query1 == 0:
            return error.error_authorization_fail() + ("",)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e)), ""
    except BaseException as e:
        return 530, "{}".format(str(e)), ""
    return 200, "ok", token


# 退出登录
def logout(user_id: str, token: str) -> (int, str):  # 此处原本是bool
    try:
        code, message = check_token(user_id, token)
        if code != 200:
            return code, message

        terminal = "terminal_{}".format(str(time.time()))
        dummy_token = jwt_encode(user_id, terminal)

        query1 = db.ession.query(st.User).filter(st.User.user_id == user_id).update(
            {st.User.token: dummy_token, st.User.terminal: terminal}
        )
        if query1 == 0:
            return error.error_authorization_fail()

        db.session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


# 用户注销
def unregister(user_id: str, password: str) -> (int, str):
    try:
        code, message = check_password(user_id, password)
        if code != 200:
            return code, message

        query1 = db.session.query(st.User).filter(st.User.user_id == user_id).delete()
        if query1 == 1:
            db.session.commit()
        else:
            return error.error_authorization_fail()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


# 更改密码
def change_password(user_id: str, old_password: str, new_password: str) -> (int, str):  # 此处原本是bool
    try:
        code, message = check_password(user_id, old_password)
        if code != 200:
            return code, message

        terminal = "terminal_{}".format(str(time.time()))
        token = jwt_encode(user_id, terminal)
        query1 = db.session.query(st.User).filter(st.User.user_id == user_id).update(
            {st.User.password: new_password, st.User.token: token, st.User.terminal: terminal}
        )
        if query1 == 0:
            return error.error_authorization_fail()

        db.session.commit()
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
