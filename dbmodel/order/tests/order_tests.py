import unittest
from dbmodel.database_init import *


class OrderTest(unittest.TestCase):

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
        User().add_item('Juliana Nuñez Becerra', 'j.nanu@hotmail.com', '+573124500004', 'julianita123', '', 1)

        Warehouse().add_item(1, 1, 'Nanu+', [4.709260, -74.058230],
                             'Calle 127A # 49-67 Apto 702 Int 2', '+5716136824', '+573124500004', 2)
        WarehouseOpeningHours().add_item(1, 1, 6, 0, 21, 0)

        Warehouse().add_item(1, 1, 'Nanu+ 2', [4.704969, -74.052909],
                             'Calle 127A # 49-67 Apto 702 Int 2', '+5716136824', '+573124500004', 2)
        WarehouseOpeningHours().add_item(1, 1, 6, 0, 21, 0)

        Warehouse().add_item(1, 1, 'La Tienda', [4.659019, -74.056064],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(2, 1, 8, 0, 22, 0)

        Warehouse().add_item(1, 1, 'La Tienda 2', [4.661501, -74.059998],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(2, 1, 8, 0, 22, 0)

        Warehouse().add_item(1, 1, 'La Tienda 3', [4.664688, -74.063313],
                             'Carrera 13 # 93-68', '+5717563322', '+573138966044', 1)
        WarehouseOpeningHours().add_item(2, 1, 8, 0, 22, 0)

        # Inventory().add_item(1, 1, 1, 10, 'un', 'BRL', 1400, '2017-6-15')
        # Inventory().add_item(2, 1, 1, 20, 'un', 'BRL', 2400, '2017-6-15')
        Inventory().add_item(3, 1, 1, 30, 'un', 'BRL', 3400, '2017-6-15')
        # Inventory().add_item(4, 1, 1, 40, 'un', 'BRL', 4400, '2017-6-15')
        # Inventory().add_item(5, 1, 1, 50, 'un', 'BRL', 5400, '2017-6-15')
        Inventory().add_item(6, 1, 1, 60, 'un', 'BRL', 6400, '2017-6-15')
        Inventory().add_item(7, 1, 1, 70, 'un', 'BRL', 7400, '2017-6-15')
        Inventory().add_item(8, 1, 1, 80, 'un', 'BRL', 8400, '2017-6-15')
        Inventory().add_item(9, 1, 1, 90, 'un', 'BRL', 9400, '2017-6-15')
        Inventory().add_item(10, 1, 1, 100, 'un', 'BRL', 10400, '2017-6-15')

        Inventory().add_item(1, 2, 2, 10, 'un', 'BRL', 1200, '2017-6-15')
        # Inventory().add_item(2, 2, 2, 20, 'un', 'BRL', 2200, '2017-6-15')
        # Inventory().add_item(3, 2, 2, 30, 'un', 'BRL', 3200, '2017-6-15')
        # Inventory().add_item(4, 2, 2, 40, 'un', 'BRL', 4200, '2017-6-15')
        # Inventory().add_item(5, 2, 2, 50, 'un', 'BRL', 5200, '2017-6-15')
        Inventory().add_item(6, 2, 2, 60, 'un', 'BRL', 6200, '2017-6-15')
        Inventory().add_item(7, 2, 2, 70, 'un', 'BRL', 7200, '2017-6-15')
        Inventory().add_item(8, 2, 2, 80, 'un', 'BRL', 8200, '2017-6-15')
        Inventory().add_item(9, 2, 2, 90, 'un', 'BRL', 9200, '2017-6-15')
        Inventory().add_item(10, 2, 2, 100, 'un', 'BRL', 10200, '2017-6-15')

        # Inventory().add_item(1, 3, 3, 60, 'un', 'BRL', 1100, '2017-6-15')
        Inventory().add_item(2, 3, 3, 70, 'un', 'BRL', 2100, '2017-6-15')
        Inventory().add_item(2, 3, 3, 3, 'un', 'BRL', 2100, '2017-6-15')
        # Inventory().add_item(3, 3, 3, 80, 'un', 'BRL', 3100, '2017-6-15')
        Inventory().add_item(4, 3, 3, 90, 'un', 'BRL', 4100, '2017-6-15')
        # Inventory().add_item(5, 3, 3, 100, 'un', 'BRL', 5100, '2017-6-15')
        Inventory().add_item(6, 3, 3, 60, 'un', 'BRL', 6100, '2017-6-15')
        Inventory().add_item(7, 3, 3, 70, 'un', 'BRL', 7100, '2017-6-15')
        Inventory().add_item(8, 3, 3, 80, 'un', 'BRL', 8100, '2017-6-15')
        Inventory().add_item(9, 3, 3, 90, 'un', 'BRL', 9100, '2017-6-15')
        Inventory().add_item(10, 3, 3, 100, 'un', 'BRL', 10100, '2017-6-15')

        # Inventory().add_item(1, 4, 4, 60, 'un', 'BRL', 1300, '2017-6-15')
        # Inventory().add_item(2, 4, 4, 70, 'un', 'BRL', 2300, '2017-6-15')
        # Inventory().add_item(3, 4, 4, 80, 'un', 'BRL', 3300, '2017-6-15')
        # Inventory().add_item(4, 4, 4, 90, 'un', 'BRL', 4300, '2017-6-15')
        Inventory().add_item(5, 4, 4, 100, 'un', 'BRL', 5300, '2017-6-15')
        Inventory().add_item(6, 4, 4, 60, 'un', 'BRL', 6300, '2017-6-15')
        Inventory().add_item(7, 4, 4, 70, 'un', 'BRL', 7300, '2017-6-15')
        Inventory().add_item(8, 4, 4, 80, 'un', 'BRL', 8300, '2017-6-15')
        Inventory().add_item(9, 4, 4, 90, 'un', 'BRL', 9300, '2017-6-15')
        Inventory().add_item(10, 4, 4, 100, 'un', 'BRL', 10300, '2017-6-15')

        Inventory().add_item(1, 5, 5, 60, 'un', 'BRL', 1000, '2017-6-15')
        # Inventory().add_item(2, 5, 5, 70, 'un', 'BRL', 2000, '2017-6-15')
        # Inventory().add_item(3, 5, 5, 80, 'un', 'BRL', 3000, '2017-6-15')
        # Inventory().add_item(4, 5, 5, 90, 'un', 'BRL', 4000, '2017-6-15')
        Inventory().add_item(5, 5, 5, 100, 'un', 'BRL', 5000, '2017-6-15')
        Inventory().add_item(6, 5, 5, 60, 'un', 'BRL', 6000, '2017-6-15')
        Inventory().add_item(7, 5, 5, 70, 'un', 'BRL', 7000, '2017-6-15')
        Inventory().add_item(8, 5, 5, 80, 'un', 'BRL', 8000, '2017-6-15')
        Inventory().add_item(9, 5, 5, 90, 'un', 'BRL', 9000, '2017-6-15')
        Inventory().add_item(10, 5, 5, 100, 'un', 'BRL', 10000, '2017-6-15')

        BasketProduct().add_item(1, 1, 15)
        BasketProduct().add_item(1, 2, 16)
        BasketProduct().add_item(1, 3, 17)
        BasketProduct().add_item(1, 4, 18)
        BasketProduct().add_item(1, 5, 19)
        # BasketProduct().add_item(1, 6, 17)
        # BasketProduct().add_item(1, 7, 18)
        # BasketProduct().add_item(1, 8, 18)
        # BasketProduct().add_item(1, 9, 19)
        # BasketProduct().add_item(1, 10, 14)

    def tearDown(self):
        pass
        # drop_database()

    '''Test Inventory.serialize'''

    def test_create_order(self):
        location = [4.650302, -74.059776]

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

        parameters = {'closer': False}

        error, basket = BasketProduct().get_basket(1, location, parameters)

        Order().add_item(1, basket, payment_info)

        error, order = Order().get_item(1)
        self.assertFalse(error)


if __name__ == '__main__':
    unittest.main()
