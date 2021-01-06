import logging
import os
from sqlalchemy import create_engine, ForeignKey, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, TEXT, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('postgresql+psycopg2://postgres:Wypsz.01@localhost/bookstore', encoding='utf-8', echo=True)
base = declarative_base()


class User(base):
    __tablename__ = 'user'
    user_id = Column('user_id', TEXT, primary_key=True)
    password = Column('password', TEXT, nullable=False)
    balance = Column('balance', Integer, nullable=False)
    token = Column('token', TEXT)
    terminal = Column('terminal ', TEXT)


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


base.metadata.create_all(engine)
