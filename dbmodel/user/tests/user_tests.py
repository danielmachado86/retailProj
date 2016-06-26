import unittest
from dbmodel.unittest_database_init import *
from dbmodel.user.usermodel import *


class UserTest(unittest.TestCase):

    def setUp(self):
        create_database()

    def tearDown(self):
        drop_database()

    '''Test User.serialize'''
    def test_user_serialize_output(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                        'Freqm0d+', '', 1)

        expected_output = {
            'id': 1,
            'nombre': 'Daniel Machado Castillo',
            'url': 'http://localhost:5000/v1.0/usuarios'
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    '''Test User.check_user_exists_by_id'''
    def test_check_user_exists_by_id(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                                      'Freqm0d+', '', 1)
        error, resp = User.check_user_exists_by_id(1)
        self.assertTrue(error)
        expected_output = [409, {'message': 'Este usuario existe'}]
        self.assertEqual(expected_output, resp)

    def test_check_user_exists_by_id_not_integer_parameter(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        error, resp = User.check_user_exists_by_id('a')
        expected_output = [400, {'message': 'El valor del campo item_id debe ser un numero entero',
                                 'action': 'Ingrese un valor adecuado'}]
        self.assertTrue(error)
        self.assertEqual(expected_output, resp)

    def test_check_user_exists_by_id_empty_parameter(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        error, resp = User.check_user_exists_by_id('')
        expected_output = [400, {'message': 'El campo item_id no puede ser vacio o nulo',
                                 'action': 'Ingrese un valor adecuado'}]
        self.assertTrue(error)
        self.assertEqual(expected_output, resp)

    '''Test User.check_user_exists_by_mail'''
    def test_check_user_exists_by_mail(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        error, resp = User.check_user_exists_by_mail('danielmcis@gmail.com')
        self.assertTrue(error)
        expected_output = [409, {'message': 'Este usuario existe'}]
        self.assertEqual(expected_output, resp)

    def test_check_user_exists_by_mail_empty_parameter(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        error, resp = User.check_user_exists_by_mail('')
        expected_output = [400, {'message': 'El campo mail no puede ser vacio o nulo',
                                 'action': 'Ingrese un valor adecuado'}]
        self.assertTrue(error)
        self.assertEqual(expected_output, resp)

    '''Test User.check_user_exists_by_phone'''
    def test_check_user_exists_by_phone(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        error, resp = User.check_user_exists_by_phone('+573138966044')
        self.assertTrue(error)
        expected_output = [409, {'message': 'Este usuario existe'}]
        self.assertEqual(expected_output, resp)

    def test_check_user_exists_by_phone_empty_parameter(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        error, resp = User.check_user_exists_by_phone('')
        expected_output = [400, {'message': 'El campo phone no puede ser vacio o nulo',
                                 'action': 'Ingrese un valor adecuado'}]
        self.assertTrue(error)
        self.assertEqual(expected_output, resp)

    '''Test User.get_item_by_mail'''
    def test_get_item_by_mail(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        item = User().get_item_by_mail('danielmcis@gmail.com', 1)
        self.assertIsNotNone(item)

    def test_get_item_by_mail_empty_mail(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        item = User().get_item_by_mail('', 1)
        self.assertIsNone(item)

    def test_get_item_by_mail_parameter_auth_type_not_integer(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        item = User().get_item_by_mail('danielmcis@gmail.com', 'a')
        self.assertIsNone(item)

    def test_get_item_by_mail_parameter_auth_type_out_of_range(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 3)
        item = User().get_item_by_mail('danielmcis@gmail.com', 4)
        self.assertIsNone(item)

    '''Test User.get_item'''
    def test_get_item_by_user_id(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        item = User().get_item(1)
        self.assertIsNotNone(item)

    def test_get_item_by_user_id_parameter_user_id_not_integer(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        item = User().get_item('a')
        self.assertIsNone(item)

    '''Test User.verify_account'''
    def test_verify_account(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        error, resp = item.verify_account()
        self.assertFalse(error)
        self.assertEqual(resp, [200, {'message': 'La cuenta se verifico exitosamente'}])

    def test_try_verify_verified_account(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        item.verify_account()
        error, resp = item.verify_account()
        self.assertTrue(error)
        self.assertEqual(resp, [409, {'message': 'La cuenta ya se encuentra verificada'}])

    def test_verify_database_response(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                      'Freqm0d+', '', 1)
        self.assertEqual(item.verificado, False)
        item.verify_account()
        self.assertEqual(item.verificado, True)

    '''Test User.add_item'''
    def test_create_user(self):
        error, resp = User().add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                                      'Freqm0d+', '', 1)
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'El usuario se ha creado exitosamente'}])

    def test_try_create_user_existent_mail(self):
        User().add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                        'Freqm0d+', '', 1)
        error, resp = User().add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573046628054',
                                      'Freqm0d+', '', 1)
        self.assertTrue(error)
        self.assertEqual(resp, [409, {'message': 'Este usuario existe'}])

    def test_try_create_user_existent_phone(self):
        User().add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573138966044',
                        'Freqm0d+', '', 1)
        error, resp = User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044',
                                      'Freqm0d+', '', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [409, {'message': 'Este usuario existe'}])

    def test_try_create_user_with_name_field_empty(self):
        error, resp = User().add_item('', 'danielmcis@gmail.com', '+573138966044',
                                      'Freqm0d+', '', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo name no puede ser vacio o nulo',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_user_with_mail_field_empty(self):
        error, resp = User().add_item('Daniel Machado Castillo', '', '+573138966044',
                                      'Freqm0d+', '', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo mail no puede ser vacio o nulo',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_user_with_phone_field_empty(self):
        error, resp = User().add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '',
                                      'Freqm0d+', '', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'El campo phone no puede ser vacio o nulo',
                                      'action': 'Ingrese un valor adecuado'}])

    def test_try_create_user_with_password_field_empty(self):
        error, resp = User().add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573046628054',
                                      '', '', 1)

        self.assertTrue(error)
        self.assertEqual(resp, [400, {'message': 'La contraseña no cuenta con las características requeridas',
                                      'action': 'Vuelva a intentarlo ingresando una contraseña valida'}])


class SubscriptionTest(unittest.TestCase):

    def setUp(self):
        create_database()
        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)

    def tearDown(self):
        drop_database()

    '''Test Subscription.add_item'''

    def test_create_subscription(self):
        error, resp = SubscriptionGroup().add_item(1, 1, 1, 1)
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'La suscripción se ha creado exitosamente'}])

    '''Test SubscriptionGroup.serialize'''

    def test_inventory_serialize_output(self):
        self.maxDiff = None
        SubscriptionGroup().add_item(1, 1, 1, 1)

        expected_output = {
            'id_suscripcion': 1,
            'plan': {
                'id_plan': 1,
                'nombre': 'Gratis',
                'cantidad_miembros': 1,
                'limite_servicios': -1,
                'precio_plan': 0,
                'duracion_plan': -1
            },
            'estado': 'Activa',
            'fecha_inicio': datetime.datetime.now().strftime("%Y-%m-%d"),
            'fecha_final': '',
            'miembros': [{
                'id_miembro': 1,
                'usuario': 'Daniel Machado Castillo',
                'titular': True,
                'estado': 'Pendiente'
            }, {
                'id_miembro': 2,
                'usuario': 'Daniel Machado Castillo',
                'titular': False,
                'estado': 'Pendiente'
            }],
            'renovar': True
        }
        SubscriptionMember().add_item(1, 1)
        error, item = SubscriptionGroup().get_item(1)
        output = item.serialize
        self.assertEqual(output, expected_output)


class LocationTest(unittest.TestCase):

    def setUp(self):
        create_database()
        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)

    def tearDown(self):
        drop_database()

    '''Test Subscription.add_item'''

    def test_create_location(self):
        error, resp = UserLocation().add_item(1, 1, 'Casa', [4.054896, -73.589647], 'Cra 8 # 65-73', 'CCB')
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'La dirección se ha creado exitosamente'}])

    '''Test SubscriptionGroup.serialize'''

    def test_location_serialize_output(self):
        self.maxDiff = None
        UserLocation().add_item(1, 1, 'Casa', [4.054896, -73.589647], 'Cra 8 # 65-73', 'CCB')

        expected_output = {
            'id_direccion': 1,
            'usuario': 'Daniel Machado Castillo',
            'ciudad': 'Bogotá',
            'pais': 'Colombia',
            'continente': 'Sudamérica',
            'nombre': 'Casa',
            'coordenadas': '4.054896, -73.589647',
            'direccion': 'Cra 8 # 65-73',
            'referencia': 'CCB',
            'fecha': datetime.datetime.now().strftime("%Y-%m-%d"),
            'favorito': False
        }
        error, item = UserLocation().get_item(1)
        output = item.serialize
        self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main()
