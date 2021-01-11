# coding: utf-8
import sys
sys.path.append('C:\\Users\\dell\\Desktop\\bookstore')
from be.model import store
from sqlalchemy.orm import sessionmaker
import os
import sqlite3 as sqlite  # 只是为了读取book.db文件
from be.model import store

Session = sessionmaker(bind=store.engine)
session = Session()


# book表格
session.query(store.Book).filter().delete()
session.commit()

parent_path = os.path.dirname(os.path.dirname(__file__))
book_db_path = os.path.join(parent_path, "fe/data/book.db")

conn = sqlite.connect(book_db_path)

cursor = conn.execute(
    "SELECT id, title, author, "
    "publisher, original_title, "
    "translator, pub_year, pages, "
    "price, currency_unit, binding, "
    "isbn, author_intro, book_intro, "
    "content, tags, picture FROM book ORDER BY id "
)

for row in cursor:
    book_id = row[0]
    title = row[1]
    author = row[2]
    publisher = row[3]
    original_title = row[4]
    translator = row[5]
    pub_year = row[6]
    pages = row[7]
    price = row[8]
    currency_unit = row[9]
    binding = row[10]
    isbn = row[11]
    author_intro = row[12]
    book_intro = row[13]
    content = row[14]
    tags_temp = row[15]
    picture_temp = row[16]

    thelist = []  # 由于没有列表类型，故使用将列表转为text的办法
    for tag in tags_temp.split("\n"):
        if tag.strip() != "":
            thelist.append(tag)
    tags = str(thelist)  # 解析成list请使用eval()
    picture = None
    if picture_temp is not None:
        picture = picture_temp

    book_obj = store.Book(book_id=book_id, title=title, author=author, publisher=publisher, original_title=original_title,
                          translator=translator, pub_year=pub_year, pages=pages, price=price,
                          currency_unit=currency_unit, binding=binding, isbn=isbn,
                          author_intro=author_intro, book_intro=book_intro,
                          content=content, tags=tags, picture=picture)
    session.add(book_obj)
session.commit()
