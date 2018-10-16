import unittest
from dbmodel.res.custom_exceptions import *
from dbmodel.database_init import create_database, drop_database
from dbmodel.user.user_data import User, UserImage, UserLocation, \
    get_address_list_by_user, get_address_list_by_user_location, \
    get_address_by_id, generate_auth_token


class UserBadDataTest(unittest.TestCase):

    def setUp(self):
        create_database()

    def tearDown(self):
        drop_database()

    '''Test User.serialize'''
    def test_construct_user_object_with_bad_argument(self):
        with self.assertRaises(InvalidArgument):
            User("", 'danielmcis@hotmail.com', '+573046628054',
                      'Freqm0d+', 1)
        with self.assertRaises(InvalidArgument):
            User("Daniel Machado", '', '+573046628054',
                      'Freqm0d+', 1)
        with self.assertRaises(InvalidArgument):
            User("Daniel Machado", 'danielmcis@hotmail.com', '',
                      'Freqm0d+', 1)
        with self.assertRaises(InvalidArgument):
            User("Daniel Machado", 'danielmcis@hotmail.com', '+573046628054',
                      '', 1)
        with self.assertRaises(InvalidArgument):
            User("Daniel Machado", 'danielmcis@hotmail.com', '+573046628054',
                 '', 4)

    def test_construct_image_object_with_bad_argument(self):
        test_user = User("Daniel Machado", 'danielmcis1@gmail.com', '+573138966044',
                              'Freqm0d+', 1)
        test_user.add_item()
        with self.assertRaises(InvalidArgument):
            UserImage("", "Descripcion", "URL")
        with self.assertRaises(InvalidArgument):
            UserImage(test_user.id_usuario, "Descripcion", "")

    def test_construct_location_with_bad_argument(self):
        test_user = User("Daniel Machado", 'danielmcis1@gmail.com', '+573138966044',
                              'Freqm0d+', 1)
        with self.assertRaises(InvalidArgument):
            UserLocation("", 1, "Casa", [74.51, 4.12],
                         "Calle 73 # 7-51, Apto 401", "FNC, JW Marriot")
        with self.assertRaises(InvalidArgument):
            UserLocation(test_user.id_usuario, "", "Casa", [74.51, 4.12],
                         "Calle 73 # 7-51, Apto 401", "FNC, JW Marriot")
        with self.assertRaises(InvalidArgument):
            UserLocation(test_user.id_usuario, 1, "", [74.51, 4.12],
                         "Calle 73 # 7-51, Apto 401", "FNC, JW Marriot")
        with self.assertRaises(InvalidArgument):
            UserLocation(test_user.id_usuario, 1, "Casa", "",
                         "Calle 73 # 7-51, Apto 401", "FNC, JW Marriot")
        with self.assertRaises(InvalidArgument):
            UserLocation(test_user.id_usuario, 1, "Casa", [74.51, 4.12],
                         "", "FNC, JW Marriot")

class UserDataTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()

    def tearDown(self):
        drop_database()
        pass

    def test_user_data(self):
        test_user = User("Daniel Machado", 'danielmcis2@gmail.com', '+573138966044',
                         'Freqm0d+', 1)
        test_user.add_item()
        # auth_token = generate_auth_token(test_user.id_usuario)
        # print(auth_token)

    def test_location(self):
        test_user = User("Daniel Machado", 'danielmcis1@gmail.com', '+573138966044',
                         'Freqm0d+', 1)
        test_user.add_item()
        '''Coordenadas dadas en longitud, latitud'''
        test_location = UserLocation(test_user.id_usuario, 1, "Casa", [-74.055353, 4.656351],
                         "Calle 73 # 7-51, Apto 401", "FNC, JW Marriot")
        test_location.add_location()
        test_locations_1 = get_address_list_by_user(test_user.id_usuario)
        for test_location in test_locations_1:
            self.assertIsInstance(test_location, UserLocation)
        '''Coordenadas dadas en longitud, latitud'''
        test_locations_1 = get_address_list_by_user_location(test_user.id_usuario, [-74.054437, 4.659212])
        for test_location in test_locations_1:
            test_location, distance = test_location
            self.assertIsInstance(test_location, UserLocation)
        test_location_2, lon, lat, coordenadas = get_address_by_id(test_location.id_direccion)
        self.assertIsInstance(test_location_2, UserLocation)




if __name__ == '__main__':
    unittest.main()
