import unittest
from dbmodel.database_init import *


class ManufacturerTest(unittest.TestCase):

    def setUp(self):
        create_database()

    def tearDown(self):
        drop_database()

    '''Test Manufacturer.serialize'''
    def test_manufacturer_serialize_output(self):
        item = Manufacturer()
        item.add_item('Aldy', '')

        expected_output = {
            'id': 1,
            'fabricante': 'Aldy',
            'descripcion': ''
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    '''Test Manufacturer.check_manufacturer_exists_by_name'''
    def test_check_manufacturer_exists_by_name(self):
        item = Manufacturer()
        item.add_item('Aldy', '')

        error, resp = Manufacturer.check_manufacturer_exists_by_name('Aldy')
        self.assertTrue(error)
        expected_output = [409, {'message': 'Este fabricante existe'}]
        self.assertEqual(expected_output, resp)

    '''Test Manufacturer.add_item'''
    def test_add_item(self):
        error, resp = Manufacturer().add_item('Aldy', '')
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El fabricante se ha creado exitosamente'}])

    def test_try_create_user_existent_mail(self):
        Manufacturer().add_item('Aldy', '')
        error, resp = Manufacturer().add_item('Aldy', '')

        self.assertTrue(error)
        self.assertEqual(resp, [409, {'message': 'Este fabricante existe'}])


class ProductTest(unittest.TestCase):

    def setUp(self):
        create_database()
        Manufacturer().add_item('Aldy', '')
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
                parent = ProductCategory().get_category_id(parent_name)
            ProductCategory().add_item(parent, category)

    def tearDown(self):
        drop_database()

    '''Test Product.serialize'''
    def test_product_serialize_output(self):
        Product().add_item(5, 1, 'Endulzante Aldy X 200 Gramos', '258974')

        expected_output = {
            'id': 1,
            'categoria': 'Endulzantes',
            'fabricante': 'Aldy',
            'nombre': 'Endulzante Aldy X 200 Gramos'
        }
        error, item = Product().get_item(1)
        output = item.serialize
        self.assertEqual(output, expected_output)

    '''Test Manufacturer.add_item'''
    def test_add_item(self):
        error, resp = Product().add_item(5, 1, 'Endulzante Aldy X 200 Gramos', '258974')
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El producto se ha creado exitosamente'}])

    def test_modify_item(self):
        error, item = Product().add_item(4, 1, 'Endulzante Aldy X 200 Gramos', '258974')
        error, resp = item.modify_item(5, 1, 'Endulzante Aldy X 1000 Gramos', '987654321')
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El producto se ha modificado exitosamente'}])

    def test_modify_product_serialize_output(self):
        Product().add_item(4, 1, 'Endulzante Aldy X 200 Gramos', '258974')
        error, item = Product().get_item(1)
        print(item.serialize)
        item.modify_item(5, 1, 'Endulzante Aldy X 1000 Gramos', '987654321')

        expected_output = {
            'id': 1,
            'categoria': 'Endulzantes',
            'fabricante': 'Aldy',
            'nombre': 'Endulzante Aldy X 1000 Gramos'
        }
        error, item = Product().get_item(1)
        output = item.serialize
        print(output)
        self.assertEqual(output, expected_output)


class InventoryTest(unittest.TestCase):

    def setUp(self):
        create_database()
        Manufacturer().add_item('Aldy', '')
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
                parent = ProductCategory().get_category_id(parent_name)
            ProductCategory().add_item(parent, category)

        Product().add_item(5, 1, 'Endulzante Aldy X 200 Gramos', '258974')
        Product().add_item(5, 1, 'Endulzante Aldy X 201 Gramos', '258975')
        Product().add_item(5, 1, 'Endulzante Aldy X 202 Gramos', '258976')
        Product().add_item(5, 1, 'Endulzante Aldy X 203 Gramos', '258977')
        Product().add_item(5, 1, 'Endulzante Aldy X 205 Gramos', '258978')

        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)

        Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)

    def tearDown(self):
        drop_database()

    '''Test Inventory.serialize'''
    def test_inventory_serialize_output(self):
        Inventory().add_item(1, 1, 1, 10, 'un', 4500, '2017-6-15')

        expected_output = {
            'id': 1,
            'producto': 'Endulzante Aldy X 200 Gramos',
            'fabricante': 'Aldy',
            'almacen': 'La Tienda',
            'responsable': 'Daniel Machado Castillo',
            'cantidad': 10,
            'unidades': 'un',
            'precio': 4500.0,
            'vencimiento': '2017-06-15'
        }
        error, item = Inventory().get_item(1)
        output = item.serialize
        self.assertEqual(output, expected_output)

    '''Test Manufacturer.add_item'''
    def test_add_item(self):
        error, resp = Inventory().add_item(1, 1, 1, 10, 'un', 4500, '2017-6-15')
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El inventario se ha creado exitosamente'}])


class InventorySearchTest(unittest.TestCase):

    def setUp(self):
        pass
        create_database()
        Manufacturer().add_item('Aldy', '')
        Manufacturer().add_item('Coca-Cola', '')
        Manufacturer().add_item('Noel', '')
        Manufacturer().add_item('Mexsana', '')
        Manufacturer().add_item('Axe', '')
        Manufacturer().add_item('Johnson & Johnson', '')
        Manufacturer().add_item('Axion', '')
        Manufacturer().add_item('Ariel', '')
        Manufacturer().add_item('Van Camps', '')
        Manufacturer().add_item('Colgate', '')
        Manufacturer().add_item('Rexona', '')
        Manufacturer().add_item('7 up', '')
        Manufacturer().add_item('Oral-b', '')
        Manufacturer().add_item('Postobon', '')
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
                parent = ProductCategory().get_category_id(parent_name)
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
        Inventory().add_item(2, 1, 1, 20, 'un', 'BRL', 2000, '2017-6-15')
        Inventory().add_item(3, 1, 1, 30, 'un', 'BRL', 3000, '2017-6-15')
        Inventory().add_item(4, 1, 1, 40, 'un', 'BRL', 4000, '2017-6-15')
        Inventory().add_item(5, 1, 1, 50, 'un', 'BRL', 5000, '2017-6-15')
        Inventory().add_item(1, 2, 2, 60, 'un', 'BRL', 6000, '2017-6-15')
        Inventory().add_item(2, 2, 2, 70, 'un', 'BRL', 7000, '2017-6-15')
        Inventory().add_item(3, 2, 2, 80, 'un', 'BRL', 8000, '2017-6-15')
        Inventory().add_item(4, 2, 2, 90, 'un', 'BRL', 9000, '2017-6-15')
        Inventory().add_item(5, 2, 2, 100, 'un', 'BRL', 10000, '2017-6-15')
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
        error, items = Product().search_product('Talco Spray')
        if not error:
            for item in items:
                print(item.nombre_producto, item.search_similarity_index)
        self.assertFalse(error)

    '''Test Inventory.serialize'''

    def test_inventory_search(self):
        error, items = Inventory().get_item_by_product_id(3, [4.650302, -74.059776])
        if not error:
            for item in items:
                print(item.serialize)
        self.assertFalse(error)

    '''Test Manufacturer.add_item'''

    def test_add_item(self):
        error, resp = Inventory().add_item(1, 1, 1, 10, 'un', 4500, '2017-6-15')
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El inventario se ha creado exitosamente'}])


if __name__ == '__main__':
    unittest.main()
