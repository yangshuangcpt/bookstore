from sqlalchemy import exc
from be.model import db_conn as db, error, store as st


# 搜索书名
def search_title(title: str):
    try:
        search = []
        result = db.session.query(st.SearchTitle).filter(st.SearchTitle.title == title).all()
        if len(result) == 0:
            return error.error_no_title(title)
        else:
            for item in result:
                book_id = item.book_id
                result1 = db.session.query(st.Store).filter(st.Store.book_id == book_id).all()
                if len(result1) == 0:
                    continue
                else:
                    for item1 in result1:
                        store_id = item1.store_id
                        book_info = item1.book_info
                        stock_level = item1.stock_level
                        temp_list = [book_id, store_id, book_info, stock_level]
                        search.append(temp_list)
        if len(search) == 0:
            return error.error_no_title(title)
        return 200, str(search)
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))


# 搜索作者名
def search_author(author: str):
    try:
        search = []
        result = db.session.query(st.SearchAuthor).filter(st.SearchAuthor.author == author).all()
        if len(result) == 0:
            return error.error_no_author(author)
        else:
            for item in result:
                book_id = item.book_id
                result1 = db.session.query(st.Store).filter(st.Store.book_id == book_id).all()
                if len(result1) == 0:
                    continue
                else:
                    for item1 in result1:
                        store_id = item1.store_id
                        book_info = item1.book_info
                        stock_level = item1.stock_level
                        temp_list = [book_id, store_id, book_info, stock_level]
                        search.append(temp_list)
        if len(search) == 0:
            return error.error_no_author(author)
        return 200, str(search)
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))


# 搜索标签名
def search_tags(tags: str):
    try:
        search = []
        result = db.session.query(st.SearchTags).filter(st.SearchTags.tags == tags).all()
        if len(result) == 0:
            return error.error_no_tags(tags)
        else:
            for item in result:
                book_id = item.book_id
                result1 = db.session.query(st.Store).filter(st.Store.book_id == book_id).all()
                if len(result1) == 0:
                    continue
                else:
                    for item1 in result1:
                        store_id = item1.store_id
                        book_info = item1.book_info
                        stock_level = item1.stock_level
                        temp_list = [book_id, store_id, book_info, stock_level]
                        search.append(temp_list)
        if len(search) == 0:
            return error.error_no_tags(tags)
        return 200, str(search)
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))


# 搜索标签名
def search_details(details: str):
    try:
        search = []
        result = db.session.query(st.SearchDetails).filter(st.SearchDetails.details == details).all()
        if len(result) == 0:
            return error.error_no_details(details)
        else:
            for item in result:
                book_id = item.book_id
                result1 = db.session.query(st.Store).filter(st.Store.book_id == book_id).all()
                if len(result1) == 0:
                    continue
                else:
                    for item1 in result1:
                        store_id = item1.store_id
                        book_info = item1.book_info
                        stock_level = item1.stock_level
                        temp_list = [book_id, store_id, book_info, stock_level]
                        search.append(temp_list)
        if len(search) == 0:
            return error.error_no_details(details)
        return 200, str(search)
    except exc.SQLAlchemyError as e:
        return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))