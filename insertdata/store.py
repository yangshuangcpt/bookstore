import logging
import os
import time
from sqlalchemy import create_engine, ForeignKey, exc, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, TEXT, Boolean, LargeBinary, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('postgresql+psycopg2://postgres:cpt1005,@localhost/bookstore', encoding='utf-8', echo=True)
base = declarative_base()


class User(base):
    __tablename__ = 'users'  # postgres中表格名不能为user
    user_id = Column('user_id', TEXT, primary_key=True)
    password = Column('password', TEXT, nullable=False)
    balance = Column('balance', Integer, nullable=False)  # 余额
    token = Column('token', TEXT)  # 登录缓存令牌
    terminal = Column('terminal ', TEXT)  # 标记终端


class UserStore(base):
    __tablename__ = 'user_store'
    user_id = Column('user_id', TEXT, primary_key=True)
    store_id = Column('store_id', TEXT, primary_key=True)


class Store(base):
    __tablename__ = 'store'
    store_id = Column('store_id', TEXT, primary_key=True)
    book_id = Column('book_id', TEXT, primary_key=True)
    book_info = Column('book_info', TEXT)
    stock_level = Column('stock_level', Integer)


class NewOrder(base):
    __tablename__ = 'new_order'
    order_id = Column('order_id', TEXT, primary_key=True)
    user_id = Column('user_id', TEXT)
    store_id = Column('store_id', TEXT)
    status = Column('status', Integer)


class NewOrderDetail(base):
    __tablename__ = 'new_order_detail'
    order_id = Column('order_id ', TEXT, primary_key=True)
    book_id = Column('book_id', TEXT, primary_key=True)
    count = Column('count ', Integer)
    price = Column('price ', Integer)


class NotPayOrder(base):
    __tablename__ = 'not_pay_order'
    order_id = Column('order_id', TEXT, primary_key=True)
    ddl = Column('ddl', DateTime, nullable=False)


class Book(base):
    __tablename__ = 'book'
    book_id = Column('book_id', TEXT, primary_key=True)
    title = Column('title', TEXT)
    author = Column('author', TEXT)
    publisher = Column('publisher', TEXT)
    original_title = Column('original_title', TEXT)
    translator = Column('translator', TEXT)
    pub_year = Column('pub_year', TEXT)
    pages = Column('pages', Integer)
    price = Column('price', Integer)
    currency_unit = Column('currency_unit', TEXT)
    binding = Column('binding', TEXT)
    isbn = Column('isbn', TEXT)
    author_intro = Column('author_intro', TEXT)
    book_intro = Column('book_intro', TEXT)
    content = Column('content', TEXT)
    tags = Column('tags', TEXT)
    picture = Column('picture', LargeBinary)  # 二进制图片类型


# 搜索标题表
class SearchTitle(base):
    __tablename__ = 'search_title'
    title = Column("title", TEXT, nullable=False, index=True)
    book_id = Column("book_id", TEXT, ForeignKey('book.book_id'), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('title', 'book_id'),
        {},
    )


# 搜索标签表
class SearchTags(base):
    __tablename__ = 'search_tags'
    tags = Column("tags", TEXT, nullable=False, index=True)
    book_id = Column("book_id", TEXT, ForeignKey('book.book_id'), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('tags', 'book_id'),
        {},
    )


# 搜索作者表
class SearchAuthor(base):
    __tablename__ = 'search_author'
    author = Column("author", TEXT, nullable=False, index=True)
    book_id = Column("book_id", TEXT, ForeignKey('book.book_id'), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('author', 'book_id'),
        {},
    )


# 搜索内容表
class SearchDetails(base):
    __tablename__ = 'search_details'
    details = Column("details", TEXT, nullable=False, index=True)
    book_id = Column("book_id", TEXT, ForeignKey('book.book_id'), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('details', 'book_id'),
        {},
    )


base.metadata.create_all(engine)  # 创建表结构

