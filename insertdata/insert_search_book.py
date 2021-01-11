# coding: utf-8
import re
import sys
sys.path.append('C:\\Users\\dell\\Desktop\\bookstore')
from be.model import store
from sqlalchemy.orm import sessionmaker
import os
import sqlite3 as sqlite  # 只是为了读取book.db文件
from be.model import store
import jieba
import jieba.analyse
Session = sessionmaker(bind=store.engine)
session = Session()


# search_title表格
session.query(store.SearchTitle).filter().delete()
session.commit()
title_dic = {}
result = session.query(store.Book).filter().all()
for item in result:
    # title_list.append({item.title:item.book_id})
    title = item.title
    book_id = item.book_id
    title = re.sub(r'[\(\[\{（【][^)）】]*[\)\]\{\】\）]\s?', '', title)
    title = re.sub(r'[^\w\s]', '', title)
    # 处理空标题
    if len(title) == 0:
        continue
    title_dic.setdefault(title, []).append(book_id)
# print(title_dic)

temp_dic = {}
for key, value in title_dic.items():
    seg_list = jieba.cut(key, cut_all=False)
    temp_str = "/ ".join(seg_list)  # 精确模式
    word_list = temp_str.split("/ ")  # 分词
    if len(word_list) != 1:
        for word in word_list:
            temp_dic.setdefault(word, []).append(value[0])

for key, value in temp_dic.items():
    title_dic.setdefault(key, []).extend(value)

for key, value in title_dic.items():
    value1 = list(set(value))  # 删除重复文档号
    value1.sort()
    title_dic[key] = value1

print(title_dic)

for key, value in title_dic.items():
    for book_id in value:
        # print(book_id, type(book_id))
        search_title_obj = store.SearchTitle(title=key, book_id=book_id)
        session.add(search_title_obj)
session.commit()


# search_tags表格
session.query(store.SearchTags).filter().delete()
session.commit()
result = session.query(store.Book).filter().all()
for item in result:
    tags = item.tags
    book_id = item.book_id
    tags_list = tags.replace("'", "").replace("[", "").replace("]", "").split(", ")
    for tag in tags_list:
        search_tags_obj = store.SearchTags(tags=tag, book_id=book_id)
        session.add(search_tags_obj)
session.commit()

# search_author表格
session.query(store.SearchAuthor).filter().delete()
session.commit()
result = session.query(store.Book).filter().all()
for item in result:
    author = item.author
    book_id = item.book_id
    if author is not None:
        author = re.sub(r'[\(\[\{（【][^)）】]*[\)\]\{\】\）]\s?', '', author)
        author = re.sub(r'[^\w\s]', '', author)
        search_author_obj = store.SearchAuthor(author=author, book_id=book_id)
        session.add(search_author_obj)
session.commit()

# search_detail表格
session.query(store.SearchDetails).filter().delete()
session.commit()
result = session.query(store.Book).filter().all()
for item in result:
    detail = item.book_intro
    book_id = item.book_id
    if detail is not None:
        keywords = jieba.analyse.extract_tags(detail, topK=5)
        keywords = list(set(keywords))
        if len(keywords) != 0:
            for word in keywords:
                search_details_obj = store.SearchDetails(details=word, book_id=book_id)
                session.add(search_details_obj)
session.commit()