import unittest
from dbmodel.database_init import *


class BasketTest(unittest.TestCase):

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

        BasketProduct().add_item(1, 1, 15)
        BasketProduct().add_item(1, 2, 16)
        BasketProduct().add_item(1, 3, 17)
        BasketProduct().add_item(2, 5, 25)
        BasketProduct().add_item(2, 6, 26)
        BasketProduct().add_item(2, 7, 27)

    def tearDown(self):
        pass
        # drop_database()

    '''Test Inventory.serialize'''

    def test_add_product_to_basket(self):
        BasketProduct().add_item(1, 4, 18)
        BasketProduct().add_item(2, 8, 28)
        error, items = BasketProduct().get_basket(2)

        if not error:
            for item in items:
                print(item.serialize)

        self.assertFalse(error)

    def test_update_product_on_basket(self):
        BasketProduct().update_item(1, 1, 5)
        BasketProduct().update_item(1, 2, 6)

        error, items = BasketProduct().get_basket(1)

        if not error:
            for item in items:
                print(item.serialize)

        self.assertFalse(error)

    def test_delete_product_on_basket(self):
        BasketProduct().delete_item(1, 4)
        BasketProduct().delete_item(2, 8)

        error, items = BasketProduct().get_basket(2)

        if not error:
            for item in items:
                print(item.serialize)

        self.assertFalse(error)


if __name__ == '__main__':
    unittest.main()
