import datetime

from api.payment.mercadopago_pg import payment, store_card

from dbmodel.dbconfig import s
from dbmodel.database_model import ProductOrderModel, ProductOrderItemModel, ProductOrderItemErrorModel,ProductTransactionModel

from dbmodel.res.custom_exceptions import ResourceConflict

from dbmodel.inventory.inventory_data import StockInput, StockOutput
from dbmodel.basket.basket_data import get_basket, empty_basket

from sqlalchemy import func
import pytz


# class SubscriptionTransaction(SubscriptionTransactionModel):
#
#     def get_payment_method(self):
#         payment_method = {1: 'Efectivo',
#                           2: 'Tarjeta de crédito'}
#         return payment_method.get(self.id_metodo_pago)
#
#     def get_transaction_status(self):
#         transaction_status = {1: 'Procesando',
#                               2: 'Aprobada',
#                               3: 'Rechazada'}
#         return transaction_status.get(self.id_estado_transaccion)

    # def __init__(self, order, payment_info):
    #     self.id_suscripcion_orden = order
    #     self.id_metodo_pago = payment_info[0]
    #     self.id_estado_transaccion = 1
    #     self.moneda = payment_info[1].get('currency')
    #     self.valor_transaccion = payment_info[1].get('amount')
    #     self.fecha_transaccion = datetime.datetime.now()
    #     s.add(self)
    #     s.flush()
    #     payment_info[1]['merchantTransactionId'] = self.id_transaccion_suscripcion
    #     error, resp = payment.transaction(payment_info[1])
    #     if error:
    #         self.id_estado_transaccion = 3
    #     else:
    #         self.id_estado_transaccion = 2
    #
    #     self.referencia_pago = resp[2]

    # # def add_item(self, order, payment_info):
    # #     self.id_suscripcion_orden = order
    # #     self.id_metodo_pago = 2
    # #     self.id_estado_transaccion = 1
    # #     self.moneda = "COP"
    # #     self.valor_transaccion = payment_info.get('transaction_amount')
    # #     self.fecha_transaccion = datetime.datetime.now()
    # #     error, resp = payment(payment_info)
    # #     if error:
    # #         self.id_estado_transaccion = 3
    # #     else:
    # #         self.id_estado_transaccion = 2
    # #
    # #     self.referencia_pago = resp['response']['id']
    # #
    # #     s.add(self)
    # #     s.commit()
    # #     return error, self.id_estado_transaccion
    #
    #
    # @property
    # def serialize(self):
    #     """Return object data in easily serializeable format"""
    #
    #     return {
    #         'id_transaccion': self.id_transaccion_suscripcion,
    #         'metodo_pago': self.get_payment_method(),
    #         'estado': self.get_transaction_status(),
    #         'fecha_transaccion': self.fecha_transaccion.strftime("%Y-%m-%d %H:%M:%S %Z"),
    #         'valor': self.valor_transaccion,
    #         'referencia_pago': self.referencia_pago
    #     }


# class SubscriptionOrder(SubscriptionOrderModel):
#
#     @property
#     def serialize(self):
#         """Return object data in easily serializeable format"""
#         return {
#             'id_orden': self.id_suscripcion_orden,
#             'transaccion': self.make_list(self.transaccion)
#         }
#
#     @staticmethod
#     def get_item(order_id):
#         item = s.query(SubscriptionOrder).filter(
#             SubscriptionOrder.id_suscripcion_orden == order_id).first()
#         if not item:
#             error = [404, {'message': 'Esta orden no existe',
#                            'action': 'Realice una nueva consulta'}]
#             return True, error
#         return False, item
#
#     @staticmethod
#     def make_list(item_list):
#         final_list = []
#         for item in item_list:
#             final_list.append(item.serialize)
#         return final_list
#
#     def add_item(self, user_id, plan, payment_info, renew):
#         error, plan = SubscriptionPlan().get_plan_info(plan)
#         if error:
#             return True, plan
#         payment_info['description'] = 'Plan ' + plan.nombre_plan
#         payment_info['transaction_amount'] = plan.precio_plan
#         error, user_account = get_user_by_id(user_id)
#         if error:
#             return True, user_account
#         payment_info['payer']= {'email': user_account.correo_electronico}
#         error, member = SubscriptionMember().get_item_titular(user_id)
#         if error:
#             return True, member
#         group_id = member.id_grupo_suscripcion
#         error, group = SubscriptionGroup().get_item(group_id)
#         if error:
#             return True, group
#         self.id_grupo_suscripcion = group_id
#         self.fecha_orden = datetime.datetime.now()
#         s.add(self)
#         s.commit()
#         if renew:
#             error, resp = group.renew_subscription()
#         else:
#             error, resp = group.change_item(plan)
#         if error:
#             return True, resp
#         error, resp = SubscriptionTransaction().add_item(self.id_suscripcion_orden, payment_info)
#         if error:
#             return True, resp
#         error, resp = group.change_subscription_status(1)
#         if error:
#             return True, resp
#         error, resp = store_card(user_account.correo_electronico, payment_info['token'])
#         if error:
#             return True, resp
#         resp = [201, {'message': 'La orden se ha creado exitosamente'}]
#         return False, resp
''' ProductOrderModel subscription '''


'''Product order'''


class ProductOrderItem(ProductOrderItemModel):

    def __init__(self, product_order_id, store_stock_item_id, quantity, price):
        self.product_order_id = product_order_id
        self.store_stock_item_id = store_stock_item_id
        self.product_order_item_quantity = quantity
        self.product_order_item_price = price

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

class ProductOrderItemError(ProductOrderItemErrorModel):

    def __init__(self, order, store_stock_item_id, product_order_error_quantity):
        self.product_order_id = order
        self.store_stock_item_id = store_stock_item_id
        self.product_order_error_quantity = product_order_error_quantity

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def get_inventory_quantity_by_id(stock_item_id):
    inventory_inputs = s.query(
        func.sum(StockInput.stock_input_quantity)).filter(
        StockInput.stock_item_id == stock_item_id)
    inventory_outputs = s.query(
        func.sum(StockOutput.stock_output_quantity)).filter(
        StockOutput.stock_item_id == stock_item_id)
    inventory_sold = s.query(
        func.sum(ProductOrderItem.product_order_item_quantity)).filter(
        ProductOrderItem.product_order_item_quantity == stock_item_id)
    '''Doble for para desempaquetar el tuple dentro de lista, resultado de query '''
    inventory_quantity = 0
    for inventory_input, in inventory_inputs:
        for inventory_output, in inventory_outputs:
            for sold, in inventory_sold:
                if inventory_input is None:
                    inventory_input = 0
                if inventory_output is None:
                    inventory_output = 0
                if sold is None:
                    sold = 0
                inventory_quantity = inventory_input - inventory_output - sold
    return inventory_quantity

class ProductOrder(ProductOrderModel):

    def __init__(self, user_id):
        self.id_usuario = user_id
        self.fecha_orden = datetime.datetime.now(tz=pytz.utc)

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def get_item(item_id):
    item = s.query(ProductOrder).filter(
        ProductOrder.product_order_id == item_id).first()
    if not item:
        error = [404, {'message': 'Esta orden no existe',
                       'action': 'Realice una nueva consulta'}]
        return True, error
    return False, item

def process_order(user_id, parameters, payment_info, location):
    basket = get_basket(user_id, parameters, location)
    order = ProductOrder(user_id)
    order.add_item()
    order.total = 0
    for basket_item in basket:
        stock_quantity = get_inventory_quantity_by_id(basket_item.stock_item_id)
        if stock_quantity - basket_item.standard_basket_quantity >= 0:
            order_item = ProductOrderItem(
                order.product_order_id, basket_item.stock_item_id,
                int(basket_item.standard_basket_quantity),
                basket_item.inventory.stock_price)
            order.total += (basket_item.standard_basket_quantity * basket_item.inventory.stock_price)
            s.add(order_item)
        else:
            order_item_error = ProductOrderItemError(
                order.product_order_id,
                basket_item.inventory.product_id,
                int(basket_item.standard_basket_quantity))
            s.add(order_item_error)
    s.commit()
    if order.total <= 0:
        order.cancelled = True
        s.commit()
        raise ResourceConflict('Orden no procesada. El valor total debe ser mayor a 0')
    payment_info['transaction_amount'] = order.total
    transaccion = ProductTransaction(order.product_order_id, payment_info)
    transaccion.add_item()
    error, response = payment(payment_info)
    if error:
        transaccion.id_estado_transaccion = 3
        s.commit()
        raise ResourceConflict('Pago rechazado')
    transaccion.referencia_pago = response
    transaccion.id_estado_transaccion = 2
    s.commit()
    empty_basket(user_id)
    return {'success': True}, 200, {'ContentType': 'application/json'}

class ProductTransaction(ProductTransactionModel):

    def get_payment_method(self):
        payment_method = {1: 'Efectivo',
                          2: 'Tarjeta de credito'}
        return payment_method.get(self.payment_method_id)

    def get_transaction_status(self):
        transaction_status = {1: 'Procesando',
                              2: 'Aprobada',
                              3: 'Rechazada'}
        return transaction_status.get(self.transaction_status_id)

    def __init__(self, order, payment_info):
        self.product_order_id = order
        self.payment_method_id = 2
        self.transaction_status_id = 1
        self.transaction_currency = 'COP'
        self.transaction_amount = payment_info.get('transaction_amount')
        self.transaction_date = datetime.datetime.now(tz=pytz.utc)
        self.payment_reference = None

    def add_item(self):
        s.add(self)
        s.commit()
        print("Estado transaccion de productos: Procesando")
        return {'success': True}, 200, {'ContentType': 'application/json'}
