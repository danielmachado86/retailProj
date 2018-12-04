import unittest

import datetime

from dbmodel.res.csv_data import save_test_data, load_data
from dbmodel.database_init import create_database, drop_database
from dbmodel.user_account.user_data import User, get_user_by_mail
from dbmodel.warehouse.warehouse_data import Store, StoreHours, StoreEmployee,get_warehouse_by_name
from dbmodel.inventory.inventory_data import Brand, ProductCategory, Product, Stock, get_product_category_id,\
    StockInput, StockOutput, get_inventory_quantity_by_id
from dbmodel.basket.basket_data import DynamicBasket, StandardBasket, get_generic_basket, empty_basket, empty_basket_by_user_id, get_basket
from dbmodel.order.order_data import ProductOrder, ProductTransaction, get_inventory_sold, ProductOrderItem, process_order



class BasketTest(unittest.TestCase):

    def setUp(self):
        pass
        drop_database()
        create_database()

        save_test_data('usuarios.csv', User)
        save_test_data('almacen.csv', Store)
        save_test_data('categoria_producto.csv', ProductCategory)
        save_test_data('fabricante.csv', Brand)
        save_test_data('productos.csv', Product)

        test_user_1 = get_user_by_mail('danielmcis@hotmail.com')
        test_warehouse_1 = get_warehouse_by_name('Snaptags')
        test_warehouse_member_1 = StoreEmployee(test_user_1.id_usuario, test_warehouse_1.id_almacen)
        test_user_2 = get_user_by_mail('drivaland0@springer.com')
        test_warehouse_2 = get_warehouse_by_name('Latz')
        test_warehouse_member_2 = StoreEmployee(test_user_2.id_usuario, test_warehouse_2.id_almacen)
        test_user_3 = get_user_by_mail('yrestall0@army.mil')
        test_warehouse_3 = get_warehouse_by_name('Twinte')
        test_warehouse_member_3 = StoreEmployee(test_user_3.id_usuario, test_warehouse_3.id_almacen)
        test_warehouse_member_1.add_warehouse_member(test_user_1.id_usuario)
        test_warehouse_member_2.add_warehouse_member(test_user_2.id_usuario)
        test_warehouse_member_3.add_warehouse_member(test_user_3.id_usuario)

        inventory_test_1 = Stock(1, test_warehouse_1.id_almacen, 1100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(2, test_warehouse_1.id_almacen, 2100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(3, test_warehouse_1.id_almacen, 3100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(4, test_warehouse_1.id_almacen, 4100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(5, test_warehouse_1.id_almacen, 5100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(6, test_warehouse_1.id_almacen, 6100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(7, test_warehouse_1.id_almacen, 7100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(8, test_warehouse_1.id_almacen, 8100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(9, test_warehouse_1.id_almacen, 9100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(10, test_warehouse_1.id_almacen, 10100)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_1.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()

        inventory_test_1 = Stock(1, test_warehouse_2.id_almacen, 1200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(2, test_warehouse_2.id_almacen, 2200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(3, test_warehouse_2.id_almacen, 3200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(4, test_warehouse_2.id_almacen, 4200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(5, test_warehouse_2.id_almacen, 5200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(6, test_warehouse_2.id_almacen, 6200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(7, test_warehouse_2.id_almacen, 7200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(8, test_warehouse_2.id_almacen, 8200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(9, test_warehouse_2.id_almacen, 9200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(10, test_warehouse_2.id_almacen, 10200)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_2.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()

        inventory_test_1 = Stock(1, test_warehouse_3.id_almacen, 1300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(2, test_warehouse_3.id_almacen, 2300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(3, test_warehouse_3.id_almacen, 3300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(4, test_warehouse_3.id_almacen, 4300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(5, test_warehouse_3.id_almacen, 5300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(6, test_warehouse_3.id_almacen, 6300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(7, test_warehouse_3.id_almacen, 7300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(8, test_warehouse_3.id_almacen, 8300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(9, test_warehouse_3.id_almacen, 9300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Stock(10, test_warehouse_3.id_almacen, 10300)
        inventory_test_1.add_item()
        StockInput(inventory_test_1.stock_item_id, test_warehouse_member_3.store_employee_id, 10,
                   datetime.datetime.now()).add_inventory_input()

        DynamicBasket(test_user_1.id_usuario, 1, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 2, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 3, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 4, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 5, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 6, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 7, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 8, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 9, 5).add_item()
        DynamicBasket(test_user_1.id_usuario, 10, 5).add_item()

        StandardBasket(test_user_1.id_usuario, 1, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 2, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 3, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 4, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 5, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 6, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 7, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 8, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 9, 5).add_item()
        StandardBasket(test_user_1.id_usuario, 10, 5).add_item()

    def tearDown(self):
        drop_database()
        pass

    '''Test Stock.serialize'''

    def test_empty_basket(self):
        location = [4.656185, -74.055333]
        test_user = get_user_by_mail('danielmcis@hotmail.com')

        parameters = {
            'closer': False
        }

        get_basket(test_user.id_usuario, parameters, location)
        empty_basket(test_user.id_usuario)

if __name__ == '__main__':
    unittest.main()
