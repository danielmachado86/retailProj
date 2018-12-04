import unittest

import datetime

from api.payment.mercadopago_pg import payment, get_card_token, store_card

from dbmodel.res.custom_exceptions import InvalidArgument, ResourceConflict

from dbmodel.res.csv_data import save_test_data, load_data
from dbmodel.database_init import create_database, drop_database
from dbmodel.user_account.user_data import User, get_user_by_mail
from dbmodel.warehouse.warehouse_data import Store, StoreHours, StoreEmployee,get_warehouse_by_name
from dbmodel.inventory.inventory_data import Brand, ProductCategory, Product, Stock, get_product_category_id, \
    StockInput, StockOutput
from dbmodel.basket.basket_data import DynamicBasket, StandardBasket, get_generic_basket, empty_basket
from dbmodel.order.order_data import ProductOrder, ProductTransaction, ProductOrderItem, process_order

class OrderTest(unittest.TestCase):

    def setUp(self):
        pass
        drop_database()
        create_database()

        # save_test_data('usuarios.csv', User)
        # save_test_data('almacen.csv', Store)
        # save_test_data('categoria_producto.csv', ProductCategory)
        # save_test_data('fabricante.csv', Brand)
        # save_test_data('productos.csv', Product)
        #
        # test_user_1 = get_user_by_mail('danielmcis@hotmail.com')
        # test_warehouse_1 = get_warehouse_by_name('Snaptags')
        # test_warehouse_member_1 = StoreEmployee(test_user_1.user_id, test_warehouse_1.store_id)
        # test_user_2 = get_user_by_mail('drivaland0@springer.com')
        # test_warehouse_2 = get_warehouse_by_name('Latz')
        # test_warehouse_member_2 = StoreEmployee(test_user_2.user_id, test_warehouse_2.store_id)
        # test_user_3 = get_user_by_mail('yrestall0@army.mil')
        # test_warehouse_3 = get_warehouse_by_name('Twinte')
        # test_warehouse_member_3 = StoreEmployee(test_user_3.user_id, test_warehouse_3.store_id)
        # test_warehouse_member_1.add_warehouse_member(test_user_1.user_id)
        # test_warehouse_member_2.add_warehouse_member(test_user_2.user_id)
        # test_warehouse_member_3.add_warehouse_member(test_user_3.user_id)
        #
        # inventory_test_1 = Stock(1, test_warehouse_1.store_id, 1100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(2, test_warehouse_1.store_id, 2100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(3, test_warehouse_1.store_id, 3100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(4, test_warehouse_1.store_id, 4100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(5, test_warehouse_1.store_id, 5100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(6, test_warehouse_1.store_id, 6100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(7, test_warehouse_1.store_id, 7100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(8, test_warehouse_1.store_id, 8100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(9, test_warehouse_1.store_id, 9100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(10, test_warehouse_1.store_id, 10100)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        #
        # inventory_test_1 = Stock(1, test_warehouse_2.store_id, 1200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(2, test_warehouse_2.store_id, 2200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(3, test_warehouse_2.store_id, 3200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(4, test_warehouse_2.store_id, 4200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(5, test_warehouse_2.store_id, 5200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(6, test_warehouse_2.store_id, 6200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(7, test_warehouse_2.store_id, 7200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(8, test_warehouse_2.store_id, 8200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(9, test_warehouse_2.store_id, 9200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(10, test_warehouse_2.store_id, 10200)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        #
        # inventory_test_1 = Stock(1, test_warehouse_3.store_id, 1300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(2, test_warehouse_3.store_id, 2300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(3, test_warehouse_3.store_id, 3300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(4, test_warehouse_3.store_id, 4300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(5, test_warehouse_3.store_id, 5300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(6, test_warehouse_3.store_id, 6300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(7, test_warehouse_3.store_id, 7300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(8, test_warehouse_3.store_id, 8300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(9, test_warehouse_3.store_id, 9300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        # inventory_test_1 = Stock(10, test_warehouse_3.store_id, 10300)
        # inventory_test_1.add_item()
        # StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10, datetime.datetime.now()).add_inventory_input()
        #
        # DynamicBasket(test_user_1.user_id, 1, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 2, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 3, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 4, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 5, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 6, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 7, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 8, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 9, 5).add_item()
        # DynamicBasket(test_user_1.user_id, 10, 5).add_item()
        #
        # StandardBasket(test_user_1.user_id, 1, 6).add_item()
        # StandardBasket(test_user_1.user_id, 2, 5).add_item()
        # StandardBasket(test_user_1.user_id, 3, 6).add_item()
        # StandardBasket(test_user_1.user_id, 4, 5).add_item()
        # StandardBasket(test_user_1.user_id, 5, 6).add_item()
        # StandardBasket(test_user_1.user_id, 6, 5).add_item()
        # StandardBasket(test_user_1.user_id, 7, 6).add_item()
        # StandardBasket(test_user_1.user_id, 8, 5).add_item()
        # StandardBasket(test_user_1.user_id, 9, 6).add_item()
        # StandardBasket(test_user_1.user_id, 10, 5).add_item()

    def tearDown(self):
        # drop_database()
        pass

    '''Test Stock.serialize'''

    def test_create_order(self):
        pass
        # location = [4.656185, -74.055333]
        # test_user_1 = get_user_by_mail('danielmcis@hotmail.com')
        #
        # card_info = {
        #     "cardNumber":"5254133674403564",
        #     "email":test_user_1.email_address,
        #     "cardholder":{
        #         "name":"APRO"
        #     },
        #     "expirationYear":"2021",
        #     "expirationMonth":"12",
        #     "securityCode":"123"
        # }
        #
        # payment_info = {
        #     "token": get_card_token(card_info),
        #     "payer": {"email": test_user_1.email_address}
        # }
        #
        # parameters = {
        #     'closer': False
        # }
        #
        # process_order(test_user_1.user_id, parameters, payment_info, location)

if __name__ == '__main__':
    unittest.main()
