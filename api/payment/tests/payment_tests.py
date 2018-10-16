import unittest

from api.payment.mercadopago_pg import new_customer

class PaymentTest(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_create_new_customer(self):
        new_customer()