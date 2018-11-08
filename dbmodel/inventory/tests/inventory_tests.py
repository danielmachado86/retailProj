import unittest
import datetime
from dbmodel.database_init import create_database, drop_database
from dbmodel.res.custom_exceptions import ResourceConflict
from dbmodel.res.csv_data import save_test_data
from dbmodel.user.user_data import User, get_user_by_mail
from dbmodel.warehouse.warehouse_data import Warehouse, WarehouseOpeningHours, WarehouseMember, get_warehouse_by_name
from dbmodel.inventory.inventory_data import Manufacturer, ProductCategory, Product, Inventory, \
    check_manufacturer_exists_by_name, get_product, get_product_category_id, InventoryInput, InventoryOutput, \
    get_inventory_quantity_by_id, search_product, process_inventory_matrix
from dbmodel.basket.basket_data import BasketProduct, get_basket


class ManufacturerTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()

    def tearDown(self):
        # drop_database()
        pass

    '''Test Manufacturer.serialize'''
    def test_manufacturer_serialize_output(self):
        item = Manufacturer('Aldy', '')
        item.add_manufacturer()

        expected_output = {
            'id': 1,
            'fabricante': 'Aldy',
            'descripcion': ''
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    '''Test Manufacturer.check_manufacturer_exists_by_name'''
    def test_check_manufacturer_exists_by_name(self):
        test_manufacturer = Manufacturer('Aldy', '')
        test_manufacturer.add_manufacturer()

        with self.assertRaises(ResourceConflict):
            check_manufacturer_exists_by_name('Aldy')


    def test_try_create_user_existent_mail(self):
        Manufacturer('Aldy', '').add_manufacturer()
        with self.assertRaises(ResourceConflict):
            Manufacturer('Aldy', '').add_manufacturer()


class ProductTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()
        Manufacturer('Aldy', '').add_manufacturer()
        categories = ['Mercado',
                      'Alimentos',
                      'Despensa',
                      'Azúcar, panela y endulzante',
                      'Endulzantes']
        for category in categories:
            parent_index = categories.index(category) - 1
            if parent_index < 0:
                parent = None
            else:
                parent_name = categories[parent_index]
                parent = get_product_category_id(parent_name)
            ProductCategory(parent, category).add_product_category()

    def tearDown(self):
        pass

    '''Test Product.serialize'''
    def test_product_serialize_output(self):
        Product(5, 1, 'Endulzante Aldy X 200 Gramos', '258974', 1, '5555555').add_product()
        self.assertIsInstance(get_product(1), Product)

    def test_modify_item(self):
        test_product = Product(4, 1, 'Endulzante Aldy X 200 Gramos', '258974', 1, '5555555')
        test_product.add_product()
        test_product.modify_item(5, 1, 'Endulzante Aldy X 1000 Gramos', '987654321')


class InventoryTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()
        Manufacturer('Aldy', '').add_manufacturer()
        categories = ['Mercado',
                      'Alimentos',
                      'Despensa',
                      'Azúcar, panela y endulzante',
                      'Endulzantes']
        for category in categories:
            parent_index = categories.index(category) - 1
            if parent_index < 0:
                parent = None
            else:
                parent_name = categories[parent_index]
                parent = get_product_category_id(parent_name)
            ProductCategory(parent, category).add_product_category()

        Product(5, 1, 'Endulzante Aldy X 200 Gramos', '258974', 1, '5555555').add_product()
        Product(5, 1, 'Endulzante Aldy X 201 Gramos', '258975', 1, '5555556').add_product()
        Product(5, 1, 'Endulzante Aldy X 202 Gramos', '258976', 1, '5555557').add_product()
        Product(5, 1, 'Endulzante Aldy X 203 Gramos', '258977', 1, '5555558').add_product()
        Product(5, 1, 'Endulzante Aldy X 205 Gramos', '258978', 1, '5555559').add_product()


    def tearDown(self):
        pass

    '''Test Inventory.serialize'''
    def test_inventory_serialize_output(self):
        test_user = User('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', 1)
        test_user.add_item()
        test_warehouse = Warehouse(1, 'La Tienda', 'Carrera 13 # 93-68', None, [4.054896, -73.589647], 1,
                                   '+573138966044')
        test_warehouse.add_item()
        test_warehouse_member = WarehouseMember(test_user.id_usuario, test_warehouse.id_almacen, test_user.id_usuario)
        test_warehouse_member.add_warehouse_member()

        WarehouseOpeningHours(test_warehouse.id_almacen, 1, 8, 0, 22, 0).add_warehouse_schedule()
        Inventory(1, test_warehouse.id_almacen, 4500).add_item()


    '''Test Manufacturer.add_item'''
    def test_add_item(self):
        test_user = User('Daniel Machado Castillo', 'danielmcis1@hotmail.com', '+573138966045', 'Freqm0d+', 1)
        test_user.add_item()
        test_warehouse = Warehouse(1, 'La Tienda', 'Carrera 13 # 93-68', None, [4.054896, -73.589647], 1,
                                   '+573138966044')
        test_warehouse.add_item()
        test_warehouse_member = WarehouseMember(test_user.id_usuario, test_warehouse.id_almacen, test_user.id_usuario)
        test_warehouse_member.add_warehouse_member()
        Inventory(2, test_warehouse.id_almacen, 4500).add_item()
        Inventory(3, test_warehouse.id_almacen, 15000).add_item()
        InventoryInput(1, 1, 10, '12-15-2020').add_inventory_input()
        InventoryInput(1, 1, 33, '12-15-2025').add_inventory_input()
        InventoryInput(2, 1, 33, '12-15-2025').add_inventory_input()
        InventoryOutput(1, 1, 5, 1).add_inventory_output()
        InventoryOutput(1, 1, 7, 1).add_inventory_output()
        InventoryOutput(2, 1, 7, 1).add_inventory_output()
        print(get_inventory_quantity_by_id(1))


class InventorySearchTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()
        save_test_data('usuarios.csv', User)
        save_test_data('almacen.csv', Warehouse)
        save_test_data('categoria_producto.csv', ProductCategory)
        save_test_data('fabricante.csv', Manufacturer)
        save_test_data('productos.csv', Product)
        pass

    def tearDown(self):
        pass
        # drop_database()

    '''Test Inventory.serialize'''

    def test_product_keyword_search(self):
        items = search_product("gingerale 355")
        for item in items:
            print("Producto: " + item[0].nombre_producto, "Similitud: " + str(item[0].search_similarity_index))

    '''Test Inventory.add_item'''

class InventoryMatrixTest(unittest.TestCase):

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

    def test_get_inventory_matrix(self):
        location = [4.656185, -74.055333]

        parameters = {
            'closer': False
        }

        basket = get_basket(get_user_by_mail('danielmcis@hotmail.com').id_usuario)
        inventory = process_inventory_matrix(basket, parameters, location)
        print(inventory)

if __name__ == '__main__':
    unittest.main()
