import unittest
from dbmodel.database_init import *
from dbmodel.warehouse.warehousemodel import *


class WarehouseTest(unittest.TestCase):

    def setUp(self):
        create_database()
        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)

    def tearDown(self):
        drop_database()

    '''Test Warehouse.serialize'''
    def test_warehouse_serialize_output(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        expected_output = {
            'id_almacen': 1,
            'categoria': 'Mercado',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'nombre': 'La Tienda',
            'coordenadas': '4.054896, -73.589647',
            'direccion': 'Carrera 13 # 93-68',
            'telefono': '+5717563322',
            'movil': '+573138966044',
            'url': 'http://localhost:5000/v1.0/tienda/1',
            'horario': [],
            'miembros': [{
                'id_miembro': 1,
                'usuario': 'Daniel Machado Castillo',
                'rol': 'Creador',
                'estado': 'Aprobada'
            }]
        }
        error, output = Warehouse.get_item(1)
        self.assertEqual(output.serialize, expected_output)

    '''Test Warehouse.check_item_exists_by_name'''
    def test_check_warehouse_exists_by_name(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        error, resp = Warehouse.check_item_exists_by_name('La Tienda')
        self.assertTrue(error)
        expected_output = [409, {'message': 'Este almacen existe'}]
        self.assertEqual(expected_output, resp)

    def test_check_warehouse_exists_by_name_not_string_parameter(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        error, resp = Warehouse.check_item_exists_by_name(2)
        expected_output = [400, {'message': 'El valor del campo name debe ser una cadena de texto',
                                 'action': 'Ingrese un valor adecuado'}]
        self.assertTrue(error)
        self.assertEqual(expected_output, resp)

    def test_check_warehouse_exists_by_name_empty_parameter(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        error, resp = Warehouse.check_item_exists_by_name('')
        expected_output = [400, {'message': 'El campo name no puede ser vacio o nulo',
                                 'action': 'Ingrese un valor adecuado'}]
        self.assertTrue(error)
        self.assertEqual(expected_output, resp)

    '''Test Warehouse.get_item_by_name'''
    def test_warehouse_get_item_by_name(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        error, item = Warehouse().get_item_by_name('La Tienda')
        self.assertFalse(error)

    def test_get_item_by_name_empty_name(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        error, resp = Warehouse().get_item_by_name('')
        expected_output = [400, {'message': 'El campo name no puede ser vacio o nulo',
                                 'action': 'Ingrese un valor adecuado'}]
        self.assertTrue(error)
        self.assertEqual(expected_output, resp)

    def test_get_item_by_name_non_string_name(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        error, resp = Warehouse().get_item_by_name(2)
        expected_output = [400, {'message': 'El valor del campo name debe ser una cadena de texto',
                          'action': 'Ingrese un valor adecuado'}]
        self.assertTrue(error)
        self.assertEqual(expected_output, resp)

    '''Test Warehouse.get_item_by_id'''
    def test_warehouse_get_item_by_id(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        item = Warehouse().get_item_by_id(1)
        self.assertIsNotNone(item)

    def test_warehouse_get_item_by_id_not_integer(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        item = Warehouse.get_item_by_id('a')
        self.assertIsNone(item)

    '''Test Warehouse.add_item'''
    def test_create_warehouse(self):
        error, resp = Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                                           'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'La tienda se ha creado exitosamente'}])

    def test_try_create_warehouse_existent_name(self):
        Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        error, resp = Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                                           'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [409, {'message': 'Esta tienda existe'}])

    def test_try_create_warehouse_with_name_field_empty(self):
        error, resp = Warehouse().add_item(1, 1, '', [4.054896, -73.589647],
                                           'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo name no puede ser vacio o nulo',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_warehouse_with_category_field_non_integer(self):
        error, resp = Warehouse().add_item('', 1, 'La Tienda', [4.054896, -73.589647],
                                           'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo category debe ser un numero entero',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_warehouse_with_city_field_non_integer(self):
        error, resp = Warehouse().add_item(1, '', 'La Tienda', [4.054896, -73.589647],
                                           'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo city debe ser un numero entero',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_warehouse_with_wrong_location_field(self):
        error, resp = Warehouse().add_item(1, 1, 'La Tienda', -73.589647,
                                           'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo location debe ser una lista que contiene lat y lon',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_warehouse_with_wrong_lat_field(self):
        error, resp = Warehouse().add_item(1, 1, 'La Tienda', ['a', -73.589647],
                                           'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo lat debe ser tipo float',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_warehouse_with_wrong_lon_field(self):
        error, resp = Warehouse().add_item(1, 1, 'La Tienda', [4.054896, 'a'],
                                           'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo lon debe ser tipo float',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_warehouse_with_address_field_empty(self):
        error, resp = Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                                           '', '+5717563322', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo address no puede ser vacio o nulo',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_warehouse_with_phone_field_empty(self):
        error, resp = Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                                           'Carrera 13 # 93-68', '', '+573138966044', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo phone no puede ser vacio o nulo',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_warehouse_with_mobile_field_empty(self):
        error, resp = Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                                           'Carrera 13 # 93-68', '+5717563322', '', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo mobile no puede ser vacio o nulo',
                                      'action': 'Ingrese un valor adecuado'}])


class WarehouseOpeningHoursTest(unittest.TestCase):

    def setUp(self):
        create_database()
        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)

    def tearDown(self):
        drop_database()

    def test_warehouse_serialize_output(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)

        expected_output = {
            'id_almacen': 1,
            'categoria': 'Mercado',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'nombre': 'La Tienda',
            'coordenadas': '4.054896, -73.589647',
            'direccion': 'Carrera 13 # 93-68',
            'telefono': '+5717563322',
            'movil': '+573138966044',
            'url': 'http://localhost:5000/v1.0/tienda/1',
            'horario': [{'id': 1,
                         'dia': 1,
                         'abre': '8 0',
                         'cierra': '22 0'
                         }],
            'miembros': [{
                'id_miembro': 1,
                'usuario': 'Daniel Machado Castillo',
                'rol': 'Creador',
                'estado': 'Aprobada'
            }]
        }
        self.maxDiff = None
        error, output = Warehouse.get_item(1)
        self.assertEqual(output.serialize, expected_output)

    def test_create_warehouse_opening_hours(self):
        Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        error, resp = WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El horario se ha creado exitosamente'}])

    def test_try_create_warehouse_opening_hours_existent(self):
        Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)

        error, resp = WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)
        self.assertTrue(error)
        self.assertEqual(resp, [409, {'message': 'Este horario existe'}])


class WarehouseOpeningHoursTest(unittest.TestCase):

    def setUp(self):
        create_database()
        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)

    def tearDown(self):
        drop_database()

    def test_warehouse_serialize_output(self):
        item = Warehouse()
        item.add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                      'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)

        expected_output = {
            'id_almacen': 1,
            'categoria': 'Mercado',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'nombre': 'La Tienda',
            'coordenadas': '4.054896, -73.589647',
            'direccion': 'Carrera 13 # 93-68',
            'telefono': '+5717563322',
            'movil': '+573138966044',
            'url': 'http://localhost:5000/v1.0/tienda/1',
            'horario': [{'id': 1,
                         'dia': 1,
                         'abre': '8 0',
                         'cierra': '22 0'
                         }],
            'miembros': [{
                'id_miembro': 1,
                'usuario': 'Daniel Machado Castillo',
                'rol': 'Creador',
                'estado': 'Aprobada'
            }]
        }
        self.maxDiff = None
        error, output = Warehouse.get_item(1)
        self.assertEqual(output.serialize, expected_output)

    def test_create_warehouse_opening_hours(self):
        Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)

        error, resp = WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El horario se ha creado exitosamente'}])

    def test_try_create_warehouse_opening_hours_existent(self):
        Warehouse().add_item(1, 1, 'La Tienda', [4.054896, -73.589647],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)

        error, resp = WarehouseOpeningHours().add_item(1, 1, 8, 0, 22, 0)
        self.assertTrue(error)
        self.assertEqual(resp, [409, {'message': 'Este horario existe'}])
if __name__ == '__main__':
    unittest.main()
