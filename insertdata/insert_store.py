import sys
import os
this_path = os.path.dirname(__file__)
root_path = os.path.dirname(this_path)
sys.path.append(root_path)
from be.model import store
from sqlalchemy.orm import sessionmaker
from be.model import user
import random

Session = sessionmaker(bind=store.engine)
session = Session()

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: str
    pictures: str


seller_number = 50
user_id = []
password = []
terminal = []
balance = []
token = []
store_id = []
book_id = []
book_info = []
stock_level = []

for i in range(seller_number):
    user_id.append("seller_"+str(i))
    password.append("password_"+str(i))
    terminal.append("terminal_"+str(i))
    balance.append(i)
    token.append(user.jwt_encode(user_id[i], terminal[i]))
    store_id.append("test_store_id_" + str(i))

    result = session.query(store.Book).filter().all()
    list_book_id = []
    list_book_info = []
    list_stock_level = []
    for item in result:
        flag = random.randint(1, 3)
        if flag == 1:
            new_book_id = item.book_id

            information = Book()
            information.book_id = item.book_id
            information.title = item.title
            information.author = item.author
            information.publisher = item.publisher
            information.original_title = item.original_title
            information.translator = item.translator
            information.pub_year = item.pub_year
            information.pages = item.pages
            information.price = item.price
            information.currency_unit = item.currency_unit
            information.binding = item.binding
            information.isbn = item.isbn
            information.author_intro = item.author_intro
            information.book_intro = item.book_intro
            information.content = item.content
            information.tags = item.tags
            information.picture = str(item.picture)

            new_book_info = information.__dict__
            new_book_info = str(new_book_info)

            list_book_id.append(new_book_id)
            list_book_info.append(new_book_info)
            list_stock_level.append(random.randint(0, 9))
    book_id.append(list_book_id)
    book_info.append(list_book_info)
    stock_level.append(list_stock_level)


# users表格
session.query(store.User).filter().delete()
session.commit()
for j in range(seller_number):
    user_obj = store.User(user_id=user_id[j], password=password[j], balance=balance[j],
                          terminal=terminal[j], token=token[j])
    session.add(user_obj)
session.commit()

# user_store表格
session.query(store.UserStore).filter().delete()
session.commit()
for j in range(seller_number):
    user_store_obj = store.UserStore(user_id=user_id[j], store_id=store_id[j])
    session.add(user_store_obj)
session.commit()

# store表格
session.query(store.Store).filter().delete()
session.commit()
for j in range(seller_number):
    for k in range(len(book_id[j])):
        store_obj = store.Store(store_id=store_id[j], book_id=book_id[j][k],
                                book_info=book_info[j][k], stock_level=stock_level[j][k])
        session.add(store_obj)
session.commit()

