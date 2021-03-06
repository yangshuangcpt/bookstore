from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))
    code, message, order_id = buyer.new_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    code, message = buyer.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    code, message = buyer.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code


@bp_buyer.route("/shipping", methods=["POST"])
def shipping():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    code, message = buyer.shipping(user_id, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    buyer_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    code, message = buyer.cancel_order(buyer_id, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/history", methods=["POST"])
def history():
    user_id = request.json.get("user_id")
    code, message = buyer.history(user_id)
    return jsonify({"message": message}), code