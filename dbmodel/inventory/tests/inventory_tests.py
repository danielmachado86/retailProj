import unittest
import datetime
from dbmodel.database_init import create_database, drop_database
from dbmodel.res.custom_exceptions import ResourceConflict
from dbmodel.res.csv_data import save_test_data
from dbmodel.user_account.user_data import User, get_user_by_mail
from dbmodel.warehouse.warehouse_data import Store, StoreHours, StoreEmployee, get_warehouse_by_name
from dbmodel.inventory.inventory_data import Brand, ProductCategory, Product, Stock, \
    check_manufacturer_exists_by_name, get_product, get_product_category_id, StockInput, StockOutput, \
    get_inventory_quantity_by_id, search_product
from dbmodel.basket.basket_data import DynamicBasket, get_generic_basket


class ManufacturerTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()

    def tearDown(self):
        # drop_database()
        pass

    '''Test Brand.serialize'''
    def test_manufacturer_serialize_output(self):
        item = Brand('Aldy', '')
        item.add_manufacturer()

        expected_output = {
            'id': 1,
            'fabricante': 'Aldy',
            'descripcion': ''
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    '''Test Brand.check_manufacturer_exists_by_name'''
    def test_check_manufacturer_exists_by_name(self):
        test_manufacturer = Brand('Aldy', '')
        test_manufacturer.add_manufacturer()

        with self.assertRaises(ResourceConflict):
            check_manufacturer_exists_by_name('Aldy')


    def test_try_create_user_existent_mail(self):
        Brand('Aldy', '').add_manufacturer()
        with self.assertRaises(ResourceConflict):
            Brand('Aldy', '').add_manufacturer()


class ProductTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()
        Brand('Aldy', '').add_manufacturer()
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
        Product(5, 1, 'Endulzante Aldy X 200 Gramos', '258974', 1, ).add_product()
        self.assertIsInstance(get_product(1), Product)

    def test_modify_item(self):
        test_product = Product(4, 1, 'Endulzante Aldy X 200 Gramos', '258974', 1, )
        test_product.add_product()
        test_product.modify_item(5, 1, 'Endulzante Aldy X 1000 Gramos', '987654321')


class InventoryTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()
        Brand('Aldy', '').add_manufacturer()
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

        Product(5, 1, 'Endulzante Aldy X 200 Gramos', '258974', 1, ).add_product()
        Product(5, 1, 'Endulzante Aldy X 201 Gramos', '258975', 1, ).add_product()
        Product(5, 1, 'Endulzante Aldy X 202 Gramos', '258976', 1, ).add_product()
        Product(5, 1, 'Endulzante Aldy X 203 Gramos', '258977', 1, ).add_product()
        Product(5, 1, 'Endulzante Aldy X 205 Gramos', '258978', 1, ).add_product()


    def tearDown(self):
        pass

    '''Test Stock.serialize'''
    def test_inventory_serialize_output(self):
        test_user = User('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', 1)
        test_user.add_item()
        test_warehouse = Store(1, 'La Tienda', 'Carrera 13 # 93-68', None, [4.054896, -73.589647], 1,
                                   '+573138966044')
        test_warehouse.add_item()
        test_warehouse_member = StoreEmployee(test_user.id_usuario, test_warehouse.id_almacen, test_user.id_usuario)
        test_warehouse_member.add_warehouse_member()

        StoreHours(test_warehouse.id_almacen, 1, 8, 0, 22, 0).add_warehouse_schedule()
        Stock(1, test_warehouse.id_almacen, 4500).add_item()


    '''Test Brand.add_item'''
    def test_add_item(self):
        test_user = User('Daniel Machado Castillo', 'danielmcis1@hotmail.com', '+573138966045', 'Freqm0d+', 1)
        test_user.add_item()
        test_warehouse = Store(1, 'La Tienda', 'Carrera 13 # 93-68', None, [4.054896, -73.589647], 1,
                                   '+573138966044')
        test_warehouse.add_item()
        test_warehouse_member = StoreEmployee(test_user.id_usuario, test_warehouse.id_almacen, test_user.id_usuario)
        test_warehouse_member.add_warehouse_member()
        Stock(2, test_warehouse.id_almacen, 4500).add_item()
        Stock(3, test_warehouse.id_almacen, 15000).add_item()
        StockInput(1, 1, 10, '12-15-2020').add_inventory_input()
        StockInput(1, 1, 33, '12-15-2025').add_inventory_input()
        StockInput(2, 1, 33, '12-15-2025').add_inventory_input()
        StockOutput(1, 1, 5, 1).add_inventory_output()
        StockOutput(1, 1, 7, 1).add_inventory_output()
        StockOutput(2, 1, 7, 1).add_inventory_output()
        print(get_inventory_quantity_by_id(1))


class InventorySearchTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()
        save_test_data('usuarios.csv', User)
        save_test_data('almacen.csv', Store)
        save_test_data('categoria_producto.csv', ProductCategory)
        save_test_data('fabricante.csv', Brand)
        save_test_data('productos.csv', Product)
        pass

    def tearDown(self):
        pass
        # drop_database()

    '''Test Stock.serialize'''

    def test_product_keyword_search(self):
        items = search_product("gingerale 355")
        for item in items:
            print("Producto: " + item[0].nombre_producto, "Similitud: " + str(item[0].search_similarity_index))

if __name__ == '__main__':
    unittest.main()
