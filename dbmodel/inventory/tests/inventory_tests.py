import unittest
from dbmodel.unittest_database_init import *
from dbmodel.inventory.inventorymodel import *


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
        error, resp = Product().add_item(4, 1, 'Endulzante Aldy X 200 Gramos', '258974')
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El producto se ha creado exitosamente'}])


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
if __name__ == '__main__':
    unittest.main()
