import datetime

from api.payment.mercadopago_pg import payment, store_card

from dbmodel.dbconfig import s
from dbmodel.database_model import OrderModel, OrderItemModel, SubscriptionOrderModel,ProductTransactionModel, SubscriptionTransactionModel

from dbmodel.res.custom_exceptions import ResourceConflict

from dbmodel.inventory.inventory_data import get_inventory_quantity_by_id, process_inventory_matrix
from dbmodel.user.user_data import get_user_by_id
from dbmodel.basket.basket_data import empty_basket, get_basket
from dbmodel.user.subscription_data import SubscriptionMember, SubscriptionGroup, SubscriptionPlan

from sqlalchemy import func
import pytz


class SubscriptionTransaction(SubscriptionTransactionModel):

    def get_payment_method(self):
        payment_method = {1: 'Efectivo',
                          2: 'Tarjeta de crédito'}
        return payment_method.get(self.id_metodo_pago)

    def get_transaction_status(self):
        transaction_status = {1: 'Procesando',
                              2: 'Aprobada',
                              3: 'Rechazada'}
        return transaction_status.get(self.id_estado_transaccion)

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

    def add_item(self, order, payment_info):
        self.id_suscripcion_orden = order
        self.id_metodo_pago = 2
        self.id_estado_transaccion = 1
        self.moneda = "COP"
        self.valor_transaccion = payment_info.get('transaction_amount')
        self.fecha_transaccion = datetime.datetime.now()
        error, resp = payment(payment_info)
        if error:
            self.id_estado_transaccion = 3
        else:
            self.id_estado_transaccion = 2

        self.referencia_pago = resp['response']['id']

        s.add(self)
        s.commit()
        return error, self.id_estado_transaccion


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""

        return {
            'id_transaccion': self.id_transaccion_suscripcion,
            'metodo_pago': self.get_payment_method(),
            'estado': self.get_transaction_status(),
            'fecha_transaccion': self.fecha_transaccion.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'valor': self.valor_transaccion,
            'referencia_pago': self.referencia_pago
        }


class SubscriptionOrder(SubscriptionOrderModel):

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_orden': self.id_suscripcion_orden,
            'transaccion': self.make_list(self.transaccion)
        }

    @staticmethod
    def get_item(order_id):
        item = s.query(SubscriptionOrder).filter(
            SubscriptionOrder.id_suscripcion_orden == order_id).first()
        if not item:
            error = [404, {'message': 'Esta orden no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item

    @staticmethod
    def make_list(item_list):
        final_list = []
        for item in item_list:
            final_list.append(item.serialize)
        return final_list

    def add_item(self, user_id, plan, payment_info, renew):
        error, plan = SubscriptionPlan().get_plan_info(plan)
        if error:
            return True, plan
        payment_info['description'] = 'Plan ' + plan.nombre_plan
        payment_info['transaction_amount'] = plan.precio_plan
        error, user = get_user_by_id(user_id)
        if error:
            return True, user
        payment_info['payer']= {'email': user.correo_electronico}
        error, member = SubscriptionMember().get_item_titular(user_id)
        if error:
            return True, member
        group_id = member.id_grupo_suscripcion
        error, group = SubscriptionGroup().get_item(group_id)
        if error:
            return True, group
        self.id_grupo_suscripcion = group_id
        self.fecha_orden = datetime.datetime.now()
        s.add(self)
        s.commit()
        if renew:
            error, resp = group.renew_subscription()
        else:
            error, resp = group.change_item(plan)
        if error:
            return True, resp
        error, resp = SubscriptionTransaction().add_item(self.id_suscripcion_orden, payment_info)
        if error:
            return True, resp
        error, resp = group.change_subscription_status(1)
        if error:
            return True, resp
        error, resp = store_card(user.correo_electronico, payment_info['token'])
        if error:
            return True, resp
        resp = [201, {'message': 'La orden se ha creado exitosamente'}]
        return False, resp
''' OrderModel subscription '''


'''Product order'''


class OrderItem(OrderItemModel):

    def __init__(self, order, inventory, quantity, price):
        self.id_orden = order
        self.id_inventario = inventory
        self.cantidad = quantity
        self.precio = price

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

def get_inventory_sold(item):
    inventory_sold = s.query(func.sum(OrderItem.cantidad)).filter(OrderItem.id_inventario == item.id_inventario)
    return inventory_sold

class Order(OrderModel):

    payment_info = None
    total = 0

    def __init__(self, user_id):
        self.id_usuario = user_id
        self.fecha_orden = datetime.datetime.now(tz=pytz.utc)

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def get_item(item_id):
    item = s.query(Order).filter(
        Order.id_orden == item_id).first()
    if not item:
        error = [404, {'message': 'Esta orden no existe',
                       'action': 'Realice una nueva consulta'}]
        return True, error
    return False, item

def process_product_order(user_id, parameters, payment_info, location):
    basket = get_basket(user_id)
    inventory = process_inventory_matrix(basket, parameters, location)
    test_order = Order(user_id)
    test_order.add_item()
    for item, ordered_qty in inventory:
        inventory_sold = get_inventory_sold(item)
        cantidad = get_inventory_quantity_by_id(item.id_inventario, inventory_sold)
        if cantidad - ordered_qty >= 0:
            order_item = OrderItem(test_order.id_orden, item.id_inventario, int(ordered_qty),
                                   item.precio)
            order_item.add_item()
            test_order.total += (cantidad * item.precio)
    payment_info['transaction_amount'] = test_order.total
    transaccion = ProductTransaction(test_order.id_orden, payment_info)
    transaccion.add_item()
    error, response = payment(payment_info)
    if error:
        transaccion.id_estado_transaccion = 3
        s.commit()
        raise ResourceConflict('Pago rechazado')
    transaccion.referencia_pago = response
    transaccion.id_estado_transaccion = 2
    s.commit()
    empty_basket(basket)
    return {'success': True}, 200, {'ContentType': 'application/json'}

class ProductTransaction(ProductTransactionModel):

    def get_payment_method(self):
        payment_method = {1: 'Efectivo',
                          2: 'Tarjeta de credito'}
        return payment_method.get(self.id_metodo_pago)

    def get_transaction_status(self):
        transaction_status = {1: 'Procesando',
                              2: 'Aprobada',
                              3: 'Rechazada'}
        return transaction_status.get(self.id_estado_transaccion)

    def __init__(self, order, payment_info):
        self.id_orden = order
        self.id_metodo_pago = 2
        self.id_estado_transaccion = 1
        self.moneda = 'COP'
        self.valor_transaccion = payment_info.get('transaction_amount')
        self.fecha_transaccion = datetime.datetime.now(tz=pytz.utc)
        self.id_estado_transaccion = 1
        self.referencia_pago = None

    def add_item(self):
        s.add(self)
        s.commit()
        print("Estado transaccion de productos: Procesando")
        return {'success': True}, 200, {'ContentType': 'application/json'}
