import time
import uuid
import pytest
import random
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
from fe.access.seller import Seller
from fe.access.buyer import Buyer

class TestHistory:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer
    seller: Seller
    gen_book: GenBook
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_history__buyer_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        yield

    def test_ok(self):
        for i in range(5):
            self.seller_id = "test_history_seller_{}".format(str(uuid.uuid1()))
            self.store_id = "test_history_store_id_{}".format(str(uuid.uuid1()))
            self.gen_book = GenBook(self.seller_id, self.store_id)
            self.seller = self.gen_book.seller
            ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
            self.buy_book_info_list = self.gen_book.buy_book_info_list
            assert ok
            self.total_price = 0
            for item in self.buy_book_info_list:
                book: Book = item[0]
                num = item[1]
                self.total_price = self.total_price + book.price * num
            code = self.buyer.add_funds(self.total_price)
            assert code == 200
            code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            flag = random.randint(0, 2)
            if flag != 0:
                code = self.buyer.payment(self.order_id)
                assert code == 200
                if flag == 1:
                    code = self.seller.receiving(self.seller_id, self.order_id)
                    assert code == 200
                    code = self.buyer.shipping(self.buyer_id, self.order_id)
                    assert code == 200

        code = self.buyer.history(self.buyer_id)
        assert code == 200

    def test_false_buyer(self):
        code = self.buyer.history(self.buyer_id+'s')
        assert code !=200
