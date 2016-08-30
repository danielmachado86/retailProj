import unittest
from dbmodel.database_init import create_database, drop_database
from dbmodel.user.usermodel import *


class UserTest(unittest.TestCase):

    def setUp(self):
        create_database()

    def tearDown(self):
        drop_database()

    '''Test User.serialize'''
    def test_user_serialize_output(self):
        item = User()
        item.add_item('Daniel Machado Castillo Castillo', 'danielmcis@gmail.com1', '+5731389660441',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('Juliana Nuñez Becerra', 'danielmcis@gmail.com2', '+5731389660442',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('Daniel Machado', 'danielmcis@gmail.com3', '+5731389660443',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('Daniel', 'danielmcis@gmail.com4', '+5731389660444',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('', 'danielmcis@gmail.com5', '+5731389660445',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item(' ', 'danielmcis@gmail.com6', '+5731389660446',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('Daniel Machado Castillo Castillo', 'danielmcis@gmail.com7', '+5731389660447',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('Daniel Machado Castillo Castillo', 'danielmcis@gmail.com8', '+5731389660448',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('Daniel Machado Castillo Castillo', 'danielmcis@gmail.com9', '+5731389660449',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('Daniel Machado Castillo Castillo', 'danielmcis@gmail.com0', '+5731389660440',
                      'Freqm0d+', '', 1)
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573046628054',
                      'Freqm0d+', '', 1)

        expected_output = {
            'id': 9,
            'nombre': 'Daniel Machado Castillo',
            'username': item.nombre_usuario
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
        expected_output = [400, {'message': 'El campo mail no puede ser vacío o nulo',
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

    def test_modify_name(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573046628054',
                      'Freqm0d+', '', 1)
        item = User().get_item_by_mail('danielmcis@gmail.com', 1)
        error, resp = item.modify_name('Daniel Machado')

        self.assertFalse(error)
        self.assertEqual(resp, [200, {'message': 'El nombre se actualizó correctamente'}])

    def test_change_password(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573046628054',
                      'Freqm0d+', '', 1)
        item = User().get_item_by_mail('danielmcis@gmail.com', 1)
        error, resp = item.change_password('Amplm0d+')

        self.assertFalse(error)
        self.assertEqual(resp, [200, {'message': 'La contraseña se actualizó correctamente'}])

    def test_change_username(self):
        item = User()
        item.add_item('Daniel Machado Castillo', 'danielmcis@gmail.com', '+573046628054',
                      'Freqm0d+', '', 1)
        item = User().get_item_by_mail('danielmcis@gmail.com', 1)
        error, resp = item.change_username('Amplm0d+')

        self.assertFalse(error)
        self.assertEqual(resp, [200, {'message': 'El nombre de usuario se actualizó correctamente'}])


class SubscriptionTest(unittest.TestCase):

    def setUp(self):
        create_database()
        User().add_item('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', '', 1)
        User().add_item('Juliana Nuñez Becerra', 'j.nanu@hotmail.com', '+573124500004', 'julianita123', '', 1)
        User().add_item('Humberto Machado Ramirez', 'humbertomachador@gmail.com', '+573112327313', 'octubres', '', 1)

    def tearDown(self):
        drop_database()

    '''Test Subscription.add_item'''

    def test_create_subscription(self):
        error, resp = SubscriptionGroup().add_item(5, 1)
        self.assertFalse(error)
        self.assertEqual(resp, [201, {'message': 'La suscripción se ha creado exitosamente'}])

    '''Test SubscriptionGroup.serialize'''

    def test_subscription_plan_1_serialize_output(self):
        self.maxDiff = None
        SubscriptionGroup().add_item(1, 1)

        error, mssg = SubscriptionMember().add_item(1, 2)
        if error:
            print(mssg)

        error, item = SubscriptionGroup().get_item(1)

        expected_output = {
            'id_suscripcion': 1,
            'plan': {'id_plan': 1,
                     'nombre': 'Gratis',
                     'cantidad_miembros': 1,
                     'limite_servicios': -1,
                     'precio_plan': 0,
                     'duracion_plan': -1},
            'estado': 'Activa',
            'fecha_inicio': datetime.datetime.now().strftime("%Y-%m-%d"),
            'fecha_final': '',
            'miembros': [{'id_miembro': 1,
                          'usuario': 'Daniel Machado Castillo',
                          'titular': True,
                          'estado': 'Activo'}],
            'renovar': True,
            'orden': [],
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    def test_subscription_plan_2_serialize_output(self):
        self.maxDiff = None

        payment_info = [2, {'authentication.userId': '8a8294174d2e4980014d3403230d09ab',
                            'authentication.password': 'qtJ2awEnBA',
                            'authentication.entityId': '8a8294174d2e4980014d340322fa09a7',
                            'paymentBrand': 'MASTER',
                            'paymentType': 'DB',
                            'card.number': '5454545454545454',
                            'card.holder': 'Jane Jones',
                            'card.expiryMonth': '05',
                            'card.expiryYear': '2018',
                            'card.cvv': '123',
                            'testMode': 'EXTERNAL'}]
        SubscriptionGroup().add_item(2, 1, payment_info)

        error, mssg = SubscriptionMember().add_item(1, 2)
        if error:
            print(mssg)

        error, item = SubscriptionGroup().get_item(1)

        expected_output = {
            'id_suscripcion': 1,
            'plan': {'id_plan': 2,
                     'nombre': 'Básico mensual',
                     'cantidad_miembros': 2,
                     'limite_servicios': 15,
                     'precio_plan': 6500,
                     'duracion_plan': 1},
            'estado': 'Activa',
            'fecha_inicio': datetime.datetime.now().strftime("%Y-%m-%d"),
            'fecha_final': '',
            'miembros': [{'id_miembro': 1,
                          'usuario': 'Daniel Machado Castillo',
                          'titular': True,
                          'estado': 'Activo'},
                         {'id_miembro': 2,
                          'usuario': 'Juliana Nuñez Becerra',
                          'titular': False,
                          'estado': 'Pendiente'}],
            'renovar': True,
            'orden': [{'id_orden': 1,
                       'transaccion': [{'estado': 'Aprobada',
                                        'fecha_transaccion': datetime.datetime.now().strftime("%Y-%m-%d"),
                                        'id_transaccion': 1,
                                        'metodo_pago': 'Tarjeta de credito',
                                        'referencia_pago': item.orden[0].transaccion[0].referencia_pago,
                                        'valor': 6500}]
                       }],
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    def test_change_subscription_plan_1_to_2_serialize_output(self):
        self.maxDiff = None
        SubscriptionGroup().add_item(1, 1)

        error, mssg = SubscriptionMember().add_item(1, 2)
        if error:
            print('Intento 1', mssg)

        error, item = SubscriptionGroup().get_item(1)

        payment_info = [2, {'authentication.userId': '8a8294174d2e4980014d3403230d09ab',
                            'authentication.password': 'qtJ2awEnBA',
                            'authentication.entityId': '8a8294174d2e4980014d340322fa09a7',
                            'paymentBrand': 'MASTER',
                            'paymentType': 'DB',
                            'card.number': '5454545454545454',
                            'card.holder': 'Jane Jones',
                            'card.expiryMonth': '05',
                            'card.expiryYear': '2018',
                            'card.cvv': '123',
                            'testMode': 'EXTERNAL'}]

        item.change_item(2, payment_info)

        error, mssg = SubscriptionMember().add_item(1, 2)
        if error:
            print('Intento 2', mssg)

        expected_output = {
            'id_suscripcion': 1,
            'plan': {'id_plan': 2,
                     'nombre': 'Básico mensual',
                     'cantidad_miembros': 2,
                     'limite_servicios': 15,
                     'precio_plan': 6500,
                     'duracion_plan': 1},
            'estado': 'Activa',
            'fecha_inicio': datetime.datetime.now().strftime("%Y-%m-%d"),
            'fecha_final': '',
            'miembros': [{'id_miembro': 1,
                          'usuario': 'Daniel Machado Castillo',
                          'titular': True,
                          'estado': 'Activo'},
                         {'id_miembro': 2,
                          'usuario': 'Juliana Nuñez Becerra',
                          'titular': False,
                          'estado': 'Pendiente'}],
            'renovar': True,
            'orden': [{'id_orden': 1,
                       'transaccion': [{'estado': 'Aprobada',
                                        'fecha_transaccion': datetime.datetime.now().strftime("%Y-%m-%d"),
                                        'id_transaccion': 1,
                                        'metodo_pago': 'Tarjeta de credito',
                                        'referencia_pago': item.orden[0].transaccion[0].referencia_pago,
                                        'valor': 6500}]
                       }],
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    def test_change_subscription_plan_2_to_1_serialize_output(self):
        self.maxDiff = None

        payment_info = [2, {'authentication.userId': '8a8294174d2e4980014d3403230d09ab',
                            'authentication.password': 'qtJ2awEnBA',
                            'authentication.entityId': '8a8294174d2e4980014d340322fa09a7',
                            'paymentBrand': 'MASTER',
                            'paymentType': 'DB',
                            'card.number': '5454545454545454',
                            'card.holder': 'Jane Jones',
                            'card.expiryMonth': '05',
                            'card.expiryYear': '2018',
                            'card.cvv': '123',
                            'testMode': 'EXTERNAL'}]

        SubscriptionGroup().add_item(2, 1, payment_info)

        error, mssg = SubscriptionMember().add_item(1, 2)
        if error:

            print('Intento 1', mssg)

        error, item = SubscriptionGroup().get_item(1)

        print(item.change_item(1))

        item.miembro[1].delete_item()

        print(item.change_item(1))

        error, mssg = SubscriptionMember().add_item(1, 2)
        if error:
            print('Intento 2', mssg)

        expected_output = {
            'id_suscripcion': 1,
            'plan': {'id_plan': 1,
                     'nombre': 'Gratis',
                     'cantidad_miembros': 1,
                     'limite_servicios': -1,
                     'precio_plan': 0,
                     'duracion_plan': -1},
            'estado': 'Activa',
            'fecha_inicio': datetime.datetime.now().strftime("%Y-%m-%d"),
            'fecha_final': '',
            'miembros': [{'id_miembro': 1,
                          'usuario': 'Daniel Machado Castillo',
                          'titular': True,
                          'estado': 'Activo'}],
            'renovar': True,
            'orden': [{'id_orden': 1,
                       'transaccion': [{'estado': 'Aprobada',
                                        'fecha_transaccion': datetime.datetime.now().strftime("%Y-%m-%d"),
                                        'id_transaccion': 1,
                                        'metodo_pago': 'Tarjeta de credito',
                                        'referencia_pago': item.orden[0].transaccion[0].referencia_pago,
                                        'valor': 6500}]
                       }],
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    def test_change_subscription_plan_2_to_4_serialize_output(self):
        self.maxDiff = None

        payment_info = [2, {'authentication.userId': '8a8294174d2e4980014d3403230d09ab',
                            'authentication.password': 'qtJ2awEnBA',
                            'authentication.entityId': '8a8294174d2e4980014d340322fa09a7',
                            'paymentBrand': 'MASTER',
                            'paymentType': 'DB',
                            'card.number': '5454545454545454',
                            'card.holder': 'Jane Jones',
                            'card.expiryMonth': '05',
                            'card.expiryYear': '2018',
                            'card.cvv': '123',
                            'testMode': 'EXTERNAL'}]

        SubscriptionGroup().add_item(2, 1, payment_info)

        error, mssg = SubscriptionMember().add_item(1, 2)
        if error:
            print('Intento 1', mssg)

        error, item = SubscriptionGroup().get_item(1)

        item.change_item(4, payment_info)

        error, mssg = SubscriptionMember().add_item(1, 3)
        if error:
            print('Intento 2', mssg)

        expected_output = {
            'id_suscripcion': 1,
            'plan': {'id_plan': 4,
                     'nombre': 'Avanzado mensual',
                     'cantidad_miembros': 5,
                     'limite_servicios': 45,
                     'precio_plan': 12500,
                     'duracion_plan': 1},
            'estado': 'Activa',
            'fecha_inicio': datetime.datetime.now().strftime("%Y-%m-%d"),
            'fecha_final': '',
            'miembros': [{'id_miembro': 1,
                          'usuario': 'Daniel Machado Castillo',
                          'titular': True,
                          'estado': 'Activo'},
                         {'id_miembro': 2,
                          'usuario': 'Juliana Nuñez Becerra',
                          'titular': False,
                          'estado': 'Pendiente'},
                         {'id_miembro': 3,
                          'usuario': 'Humberto Machado Ramirez',
                          'titular': False,
                          'estado': 'Pendiente'}],
            'renovar': True,
            'orden': [{'id_orden': 1,
                       'transaccion': [{'estado': 'Aprobada',
                                        'fecha_transaccion': datetime.datetime.now().strftime("%Y-%m-%d"),
                                        'id_transaccion': 1,
                                        'metodo_pago': 'Tarjeta de credito',
                                        'referencia_pago': item.orden[0].transaccion[0].referencia_pago,
                                        'valor': 6500}]
                       },
                      {'id_orden': 2,
                       'transaccion': [{'estado': 'Aprobada',
                                        'fecha_transaccion': datetime.datetime.now().strftime("%Y-%m-%d"),
                                        'id_transaccion': 2,
                                        'metodo_pago': 'Tarjeta de credito',
                                        'referencia_pago': item.orden[1].transaccion[0].referencia_pago,
                                        'valor': 12500}]
                       }
                      ],
        }
        output = item.serialize
        self.assertEqual(output, expected_output)

    def test_renew_suscription(self):
        self.maxDiff = None

        payment_info = [2, {'authentication.userId': '8a8294174d2e4980014d3403230d09ab',
                            'authentication.password': 'qtJ2awEnBA',
                            'authentication.entityId': '8a8294174d2e4980014d340322fa09a7',
                            'paymentBrand': 'MASTER',
                            'paymentType': 'DB',
                            'card.number': '5454545454545454',
                            'card.holder': 'Jane Jones',
                            'card.expiryMonth': '05',
                            'card.expiryYear': '2018',
                            'card.cvv': '123',
                            'testMode': 'EXTERNAL'}]
        SubscriptionGroup().add_item(2, 1, payment_info)

        error, item = SubscriptionGroup().get_item(1)

        item.renew_subscription(payment_info)

        expected_output = {
            'id_suscripcion': 1,
            'plan': {'id_plan': 2,
                     'nombre': 'Básico mensual',
                     'cantidad_miembros': 2,
                     'limite_servicios': 15,
                     'precio_plan': 6500,
                     'duracion_plan': 1},
            'estado': 'Activa',
            'fecha_inicio': datetime.datetime.now().strftime("%Y-%m-%d"),
            'fecha_final': '',
            'miembros': [{'id_miembro': 1,
                          'usuario': 'Daniel Machado Castillo',
                          'titular': True,
                          'estado': 'Activo'},
                         {'id_miembro': 2,
                          'usuario': 'Juliana Nuñez Becerra',
                          'titular': False,
                          'estado': 'Pendiente'}],
            'renovar': True,
            'orden': [{'id_orden': 1,
                       'transaccion': [{'estado': 'Aprobada',
                                        'fecha_transaccion': datetime.datetime.now().strftime("%Y-%m-%d"),
                                        'id_transaccion': 1,
                                        'metodo_pago': 'Tarjeta de credito',
                                        'referencia_pago': item.orden[0].transaccion[0].referencia_pago,
                                        'valor': 6500}]
                       }],
        }
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
