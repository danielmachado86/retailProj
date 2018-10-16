import unittest
from dbmodel.database_init import create_database, drop_database
from dbmodel.res.custom_exceptions import ResourceConflict
from dbmodel.user.user_data import User
from dbmodel.warehouse.warehouse_data import Warehouse, WarehouseOpeningHours, WarehouseMember
from dbmodel.inventory.inventory_data import Manufacturer, ProductCategory, Product, Inventory, \
    check_manufacturer_exists_by_name, get_product, get_product_category_id, InventoryIn, InventoryOut, \
    get_inventory_quantity


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
        test_warehouse = Warehouse(1, 'La Tienda', 'Carrera 13 # 93-68', [4.054896, -73.589647], 1, '+573138966044')
        test_warehouse.add_item()
        test_warehouse_member = WarehouseMember(test_user.id_usuario, test_warehouse.id_almacen, test_user.id_usuario)
        test_warehouse_member.add_warehouse_member()

        WarehouseOpeningHours(test_warehouse.id_almacen, 1, 8, 0, 22, 0).add_warehouse_schedule()
        Inventory(1, test_warehouse.id_almacen, 4500).add_item()


    '''Test Manufacturer.add_item'''
    def test_add_item(self):
        test_user = User('Daniel Machado Castillo', 'danielmcis1@hotmail.com', '+573138966045', 'Freqm0d+', 1)
        test_user.add_item()
        test_warehouse = Warehouse(1, 'La Tienda', 'Carrera 13 # 93-68', [4.054896, -73.589647], 1, '+573138966044')
        test_warehouse.add_item()
        test_warehouse_member = WarehouseMember(test_user.id_usuario, test_warehouse.id_almacen, test_user.id_usuario)
        test_warehouse_member.add_warehouse_member()
        Inventory(2, test_warehouse.id_almacen, 4500).add_item()
        Inventory(3, test_warehouse.id_almacen, 15000).add_item()
        InventoryIn(1, 1, 10, '12-15-2020').add_inventory_in()
        InventoryIn(1, 1, 33, '12-15-2025').add_inventory_in()
        InventoryIn(2, 1, 33, '12-15-2025').add_inventory_in()
        InventoryOut(1, 1, 5, 1).add_inventory_out()
        print(get_inventory_quantity(1))


class InventorySearchTest(unittest.TestCase):

    def setUp(self):
        pass
        create_database()
        Manufacturer('Aldy', '').add_manufacturer()
        Manufacturer('Coca-Cola', '').add_manufacturer()
        Manufacturer('Noel', '').add_manufacturer()
        Manufacturer('Mexsana', '').add_manufacturer()
        Manufacturer('Axe', '').add_manufacturer()
        Manufacturer('Johnson & Johnson', '').add_manufacturer()
        Manufacturer('Axion', '').add_manufacturer()
        Manufacturer('Ariel', '').add_manufacturer()
        Manufacturer('Van Camps', '').add_manufacturer()
        Manufacturer('Colgate', '').add_manufacturer()
        Manufacturer('Rexona', '').add_manufacturer()
        Manufacturer('7 up', '').add_manufacturer()
        Manufacturer('Oral-b', '').add_manufacturer()
        Manufacturer('Postobon', '').add_manufacturer()
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
                parent = ProductCategory(parent_name).get_category_id()
            ProductCategory().add_item(parent, category)

        Product().add_item(5, 1, 'Endulzante Aldy X 200 Gramos', '727500')
        Product().add_item(5, 1, 'Endulzante Aldy Original X 70 Sobres', '251669')
        Product().add_item(4, 2, 'Sixpack Coca Cola Mini Pet 1500 ml', '511329')
        Product().add_item(4, 2, 'Coca-Cola Light 300 ml', '42606')
        Product().add_item(3, 3, 'Galleta Wafer De Vainilla X 490 gr', '522833')
        Product().add_item(3, 3, 'Galletas Crakers Tradicionales X 300 Gr X 3 Tacos', '836412')
        Product().add_item(1, 4, 'Talco Lady Mexsana Spray', '983374')
        Product().add_item(1, 4, 'Talco Mexsana Spray Antitrans', '983311')
        Product().add_item(1, 6, "Aceite Johnson's Baby Hora De Dormir X 100 ml", '629661')
        Product().add_item(1, 6, "Jabón Johnson's Baby Original X 125 gr", '988454')

        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)

        Warehouse().add_item(1, 1, 'La Tienda', [4.650302, -74.059776],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)

        User().add_item('Juliana Nuñez Becerra', 'j.nanu@hotmail.com', '+573124500004', 'julianita123', '', 1)

        Warehouse().add_item(1, 1, 'Nanu+', [4.709260, -74.058230],
                             'Calle 127A # 49-67 Apto 702 Int 2', '+5716136824', '+573124500004', 2)
        WarehouseOpeningHours().add_item(2, 1, 6, 0, 21, 0)

        Inventory().add_item(1, 1, 1, 10, 'un', 'BRL', 1000, '2017-6-15')
        Inventory().add_item(1, 1, 1, 10, 'un', 'BRL', 1000, '2017-6-15')
        Inventory().add_item(2, 1, 1, 20, 'un', 'BRL', 2000, '2017-6-15')
        Inventory().add_item(3, 1, 1, 30, 'un', 'BRL', 3000, '2017-6-15')
        Inventory().add_item(4, 1, 1, 40, 'un', 'BRL', 4000, '2017-6-15')
        Inventory().add_item(5, 1, 1, 50, 'un', 'BRL', 5000, '2017-6-15')
        Inventory().add_item(6, 1, 1, 60, 'un', 'BRL', 6000, '2017-6-15')
        Inventory().add_item(7, 1, 1, 70, 'un', 'BRL', 7000, '2017-6-15')
        Inventory().add_item(8, 1, 1, 80, 'un', 'BRL', 8000, '2017-6-15')
        Inventory().add_item(9, 1, 1, 90, 'un', 'BRL', 9000, '2017-6-15')
        Inventory().add_item(10, 1, 1, 100, 'un', 'BRL', 10000, '2017-6-15')

        Inventory().add_item(1, 2, 2, 10, 'un', 'BRL', 1000, '2017-6-15')
        Inventory().add_item(2, 2, 2, 20, 'un', 'BRL', 2000, '2017-6-15')
        Inventory().add_item(3, 2, 2, 30, 'un', 'BRL', 3000, '2017-6-15')
        Inventory().add_item(4, 2, 2, 40, 'un', 'BRL', 4000, '2017-6-15')
        Inventory().add_item(5, 2, 2, 50, 'un', 'BRL', 5000, '2017-6-15')
        Inventory().add_item(6, 2, 2, 60, 'un', 'BRL', 6000, '2017-6-15')
        Inventory().add_item(7, 2, 2, 70, 'un', 'BRL', 7000, '2017-6-15')
        Inventory().add_item(8, 2, 2, 80, 'un', 'BRL', 8000, '2017-6-15')
        Inventory().add_item(9, 2, 2, 90, 'un', 'BRL', 9000, '2017-6-15')
        Inventory().add_item(10, 2, 2, 100, 'un', 'BRL', 10000, '2017-6-15')

    def tearDown(self):
        pass
        # drop_database()

    '''Test Inventory.serialize'''

    def test_product_keyword_search(self):
        error, items = Product().search_product("Wafer Vainilla 490 gr")
        if not error:
            for item in items:
                print(item.nombre_producto, "Similaridad: " + str(item.search_similarity_index))
        self.assertFalse(error)

    '''Test Inventory.serialize'''

    def test_inventory_search(self):
        error, items = Inventory().get_item_by_product_id(3, [4.650302, -74.059776])
        if not error:
            for item in items:
                print(item.serialize)
        self.assertFalse(error)

    '''Test Inventory.add_item'''

    def test_add_item(self):
        error, resp = Inventory().add_item(1, 1, 1, 10, 'un', 4500, '2017-6-15')
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El inventario se ha creado exitosamente'}])

    def test_get_inventory_availability(self):

        error, items = Product().search_product("Wafer Vainilla 490 gr")

        product_list = [pr.id_producto for pr in items]

        wh = 1
        error, resp = Inventory.get_inventory_availability(product_list, wh)

        print(resp)
        self.assertFalse(True)



if __name__ == '__main__':
    unittest.main()
