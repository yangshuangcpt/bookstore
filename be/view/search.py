from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import search

bp_search = Blueprint("search", __name__, url_prefix="/search")


@bp_search.route("/search_title", methods=["POST"])
def search_title():
    title: str = request.json.get("title")
    number: int = request.json.get("number")
    code, message = search.search_title(title)
    if code != 200:
        return jsonify({"message": message}), code
    else:
        final_dict = {}
        result = eval(message)
        len_result = len(result)
        page_number = 10
        start = (number-1)*page_number
        if len_result <= start:
            return jsonify({"message": "this page have no information"}), code
        else:
            end = min(len_result, start+page_number)
            for index in range(start, end):
                temp_dict = {"book_id": result[index][0], "store_id": result[index][1],
                             "book_info": result[index][2], "stock_level": result[index][3]}
                final_dict[index+1] = temp_dict
            return jsonify(final_dict), code


@bp_search.route("/search_author", methods=["POST"])
def search_author():
    author: str = request.json.get("author")
    number: int = request.json.get("number")
    code, message = search.search_author(author)
    if code != 200:
        return jsonify({"message": message}), code
    else:
        final_dict = {}
        result = eval(message)
        len_result = len(result)
        page_number = 10
        start = (number - 1) * page_number
        if len_result <= start:
            return jsonify({"message": "this page have no information"}), code
        else:
            end = min(len_result, start + page_number)
            for index in range(start, end):
                temp_dict = {"book_id": result[index][0], "store_id": result[index][1],
                             "book_info": result[index][2], "stock_level": result[index][3]}
                final_dict[index + 1] = temp_dict
            return jsonify(final_dict), code


@bp_search.route("/search_tags", methods=["POST"])
def search_tags():
    tags: str = request.json.get("tags")
    number: int = request.json.get("number")
    code, message = search.search_tags(tags)
    if code != 200:
        return jsonify({"message": message}), code
    else:
        final_dict = {}
        result = eval(message)
        len_result = len(result)
        page_number = 10
        start = (number - 1) * page_number
        if len_result <= start:
            return jsonify({"message": "this page have no information"}), code
        else:
            end = min(len_result, start + page_number)
            for index in range(start, end):
                temp_dict = {"book_id": result[index][0], "store_id": result[index][1],
                             "book_info": result[index][2], "stock_level": result[index][3]}
                final_dict[index + 1] = temp_dict
            return jsonify(final_dict), code


@bp_search.route("search_details", methods=["POST"])
def search_details():
    details: str = request.json.get("details")
    number: int = request.json.get("number")
    code, message = search.search_details(details)
    if code != 200:
        return jsonify({"message": message}), code
    else:
        final_dict = {}
        result = eval(message)
        len_result = len(result)
        page_number = 10
        start = (number - 1) * page_number
        if len_result <= start:
            return jsonify({"message": "this page have no information"}), code
        else:
            end = min(len_result, start + page_number)
            for index in range(start, end):
                temp_dict = {"book_id": result[index][0], "store_id": result[index][1],
                             "book_info": result[index][2], "stock_level": result[index][3]}
                final_dict[index + 1] = temp_dict
            return jsonify(final_dict), code


