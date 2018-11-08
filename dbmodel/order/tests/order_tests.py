import unittest

import datetime

from api.payment.mercadopago_pg import payment, get_card_token, store_card

from dbmodel.res.custom_exceptions import InvalidArgument, ResourceConflict

from dbmodel.res.csv_data import save_test_data, load_data
from dbmodel.database_init import create_database, drop_database
from dbmodel.user.user_data import User, get_user_by_mail
from dbmodel.warehouse.warehouse_data import Warehouse, WarehouseOpeningHours, WarehouseMember,get_warehouse_by_name
from dbmodel.inventory.inventory_data import Manufacturer, ProductCategory, Product, Inventory, get_product_category_id, \
    process_inventory_matrix, InventoryInput, InventoryOutput, get_inventory_quantity_by_id
from dbmodel.basket.basket_data import BasketProduct, get_basket, empty_basket
from dbmodel.order.order_data import Order, ProductTransaction, get_inventory_sold, OrderItem, process_product_order

class OrderTest(unittest.TestCase):

    def setUp(self):
        pass
        drop_database()
        create_database()

        save_test_data('usuarios.csv', User)
        save_test_data('almacen.csv', Warehouse)
        save_test_data('categoria_producto.csv', ProductCategory)
        save_test_data('fabricante.csv', Manufacturer)
        save_test_data('productos.csv', Product)

        test_user_1 = get_user_by_mail('danielmcis@hotmail.com')
        test_warehouse_1 = get_warehouse_by_name('Snaptags')
        test_warehouse_member_1 = WarehouseMember(test_user_1.id_usuario, test_warehouse_1.id_almacen,
                                                  test_user_1.id_usuario)
        test_user_2 = get_user_by_mail('drivaland0@springer.com')
        test_warehouse_2 = get_warehouse_by_name('Latz')
        test_warehouse_member_2 = WarehouseMember(test_user_2.id_usuario, test_warehouse_2.id_almacen,
                                                  test_user_2.id_usuario)
        test_user_3 = get_user_by_mail('yrestall0@army.mil')
        test_warehouse_3 = get_warehouse_by_name('Twinte')
        test_warehouse_member_3 = WarehouseMember(test_user_3.id_usuario, test_warehouse_3.id_almacen,
                                                  test_user_3.id_usuario)
        test_warehouse_member_1.add_warehouse_member()
        test_warehouse_member_2.add_warehouse_member()
        test_warehouse_member_3.add_warehouse_member()

        inventory_test_1 = Inventory(1, test_warehouse_1.id_almacen, 1100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario,test_warehouse_member_1.id_miembro_almacen,10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(2, test_warehouse_1.id_almacen, 2100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(3, test_warehouse_1.id_almacen, 3100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(4, test_warehouse_1.id_almacen, 4100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(5, test_warehouse_1.id_almacen, 5100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(6, test_warehouse_1.id_almacen, 6100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(7, test_warehouse_1.id_almacen, 7100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(8, test_warehouse_1.id_almacen, 8100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(9, test_warehouse_1.id_almacen, 9100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(10, test_warehouse_1.id_almacen, 10100)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_1.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()

        inventory_test_1 = Inventory(1, test_warehouse_2.id_almacen, 1200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(2, test_warehouse_2.id_almacen, 2200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(3, test_warehouse_2.id_almacen, 3200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(4, test_warehouse_2.id_almacen, 4200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(5, test_warehouse_2.id_almacen, 5200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(6, test_warehouse_2.id_almacen, 6200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(7, test_warehouse_2.id_almacen, 7200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(8, test_warehouse_2.id_almacen, 8200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(9, test_warehouse_2.id_almacen, 9200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(10, test_warehouse_2.id_almacen, 10200)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_2.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()

        inventory_test_1 = Inventory(1, test_warehouse_3.id_almacen, 1300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(2, test_warehouse_3.id_almacen, 2300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(3, test_warehouse_3.id_almacen, 3300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(4, test_warehouse_3.id_almacen, 4300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(5, test_warehouse_3.id_almacen, 5300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(6, test_warehouse_3.id_almacen, 6300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(7, test_warehouse_3.id_almacen, 7300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(8, test_warehouse_3.id_almacen, 8300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(9, test_warehouse_3.id_almacen, 9300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()
        inventory_test_1 = Inventory(10, test_warehouse_3.id_almacen, 10300)
        inventory_test_1.add_item()
        InventoryInput(inventory_test_1.id_inventario, test_warehouse_member_3.id_miembro_almacen, 10, datetime.datetime.now()).add_inventory_input()

        BasketProduct(test_user_1.id_usuario, 1, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 2, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 3, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 4, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 5, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 6, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 7, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 8, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 9, 5).add_item()
        BasketProduct(test_user_1.id_usuario, 10, 5).add_item()

    def tearDown(self):
        pass
        # drop_database()

    '''Test Inventory.serialize'''

    def test_create_order(self):
        location = [4.656185, -74.055333]
        test_user_1 = get_user_by_mail('danielmcis@hotmail.com')

        card_info = {
            "cardNumber":"5254133674403564",
            "email":test_user_1.correo_electronico,
            "cardholder":{
                "name":"APRO"
            },
            "expirationYear":"2021",
            "expirationMonth":"12",
            "securityCode":"123"
        }

        payment_info = {
            "token": get_card_token(card_info),
            "payer": {"email": test_user_1.correo_electronico}
        }

        parameters = {
            'closer': False
        }

        process_product_order(test_user_1.id_usuario, parameters, payment_info, location)


class SubscriptionOrderTest(unittest.TestCase):

    def setUp(self):
        pass
        create_database()

        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)


    def tearDown(self):
        pass
        # drop_database()

    '''Test Inventory.serialize'''

    def test_create_subscription_order(self):
        payment_info = {
            "token": "ddb08a8722953e73092128612537a91b",
            "payment_method_id": "master"
        }
        error, order = SubscriptionOrder().add_item(1, 2, payment_info, False)
        print(order)
        self.assertFalse(error)

    def test_downgrade_subscription_order(self):

        payment_info = {
            "token": "4e747a32cbec22df597a347d88e2bf84",
            "payment_method_id": "master"
        }
        SubscriptionOrder().add_item(1, 2, payment_info, False)

        error, order = SubscriptionOrder().add_item(1, 2, payment_info, False)

        self.assertTrue(error)


if __name__ == '__main__':
    unittest.main()
