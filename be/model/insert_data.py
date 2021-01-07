from be.model import store
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=store.engine)
session = Session()

# users表格
session.query(store.User).filter().delete()
session.commit()

user_id = ["Cindy", "Zoe", "Andy"]
password = ["123", "456", "abc"]
balance = [30, 50, 100]

for i in range(0, len(user_id)):
    user_obj = store.User(user_id=user_id[i], password=password[i], balance=balance[i])
    session.add(user_obj)
session.commit()

# user_store表格
session.query(store.UserStore).filter().delete()
session.commit()

user_id = ["Cindy", "Zoe"]
store_id = ["11111111", "22222222"]

for i in range(0, len(user_id)):
    user_store_obj = store.UserStore(user_id=user_id[i], store_id=store_id[i])
    session.add(user_store_obj)
session.commit()

# store表格
# store_id = Column('store_id', TEXT, primary_key=True)
#     book_id = Column('book_id', TEXT, primary_key=True)
#     book_info = Column('book_info', TEXT)
#     stock_level = Column('stock_level', Integer)
session.query(store.Store).filter().delete()
session.commit()

store_id = ["11111111", "22222222"]
book_id = ["csapp_111", "cv_111"]
book_info = ["test1", "test2"]
stock_level = [3, 4]

for i in range(0, len(store_id)):
    store_obj = store.Store(store_id=user_id[i], book_id=store_id[i], book_info=book_info[i], stock_level=stock_level[i])
    session.add(store_obj)
session.commit()