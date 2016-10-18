import datetime

from shapely import wkt, wkb
from binascii import unhexlify
from sqlalchemy import Column, DateTime, Date, String, Integer, Boolean, ForeignKey, func, and_, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from dbmodel.dbconfig import Base, s

import pytz
from tzlocal import get_localzone


from functools import partial
import api.payment.subscription_payment as payment
partial(Column, nullable=False)

Base.metadata.schema = 'orden'

''' Order subscription '''


class SubscriptionTransaction(Base):
    __tablename__ = 'transaccion_suscripcion'

    id_transaccion_suscripcion = Column(Integer, primary_key=True)
    id_suscripcion_orden = Column(
        Integer, ForeignKey('suscripcion_orden.id_suscripcion_orden'), nullable=False)
    id_metodo_pago = Column(Integer, nullable=False)
    id_estado_transaccion = Column(Integer,  nullable=False)
    moneda = Column(String,  nullable=False)
    valor_transaccion = Column(Integer, nullable=False)
    referencia_pago = Column(String)
    fecha_transaccion = Column(DateTime(timezone=True), nullable=False)
    # suscripcion_orden = relationship('SubscriptionOrder', foreign_keys=[id_suscripcion_orden])

    def get_payment_method(self):
        payment_method = {1: 'Efectivo',
                          2: 'Tarjeta de crédito'}
        return payment_method.get(self.id_metodo_pago)

    def get_transaction_status(self):
        transaction_status = {1: 'Procesando',
                              2: 'Aprobada',
                              3: 'Rechazada'}
        return transaction_status.get(self.id_estado_transaccion)

    def __init__(self, order, payment_info):
        self.id_suscripcion_orden = order
        self.id_metodo_pago = payment_info[0]
        self.id_estado_transaccion = 1
        self.moneda = payment_info[1].get('currency')
        self.valor_transaccion = payment_info[1].get('amount')
        self.fecha_transaccion = datetime.datetime.now()
        s.add(self)
        s.flush()
        payment_info[1]['merchantTransactionId'] = self.id_transaccion_suscripcion
        error, resp = payment.transaction(payment_info[1])
        if error:
            self.id_estado_transaccion = 3
        else:
            self.id_estado_transaccion = 2

        self.referencia_pago = resp[2]

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


class SubscriptionOrder(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'suscripcion_orden'

    id_suscripcion_orden = Column(Integer, primary_key=True)
    id_grupo_suscripcion = Column(Integer, ForeignKey('usuario.grupo_suscripcion.id_grupo_suscripcion'), nullable=False)
    fecha_orden = Column(DateTime(timezone=True), nullable=False)

    transaccion = relationship('SubscriptionTransaction',
                         primaryjoin="SubscriptionOrder.id_suscripcion_orden==SubscriptionTransaction.id_suscripcion_orden",
                         backref=backref('suscripcion_orden', uselist=False), cascade="all, delete-orphan",
                         lazy='subquery')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_orden': self.id_suscripcion_orden,
            'transaccion': self.make_list(self.transaccion)
        }

    @staticmethod
    def make_list(item_list):
        final_list = []
        for item in item_list:
            final_list.append(item.serialize)
        return final_list

    def __init__(self, group, payment_info):
        self.id_grupo_suscripcion = group
        self.fecha_orden = datetime.datetime.now()
        s.add(self)
        s.flush()
        transaccion = SubscriptionTransaction(self.id_suscripcion_orden, payment_info)
        self.transaccion.append(transaccion)

    def add_item(self, group):
        self.fecha_orden = datetime.datetime.now()
        self.id_grupo_suscripcion = group
        s.add(self)
        s.commit()
        resp = [201, {'message': 'La orden se ha creado exitosamente'}]
        return False, resp
''' Order subscription '''


'''Product order'''


class Item(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'item_orden'

    id_item_orden = Column(Integer, primary_key=True)
    id_orden = Column(
        Integer, ForeignKey('orden.id_orden'))
    id_inventario = Column(Integer, ForeignKey('inventario.inventario.id_inventario'))
    cantidad = Column(Integer)
    precio = Column(Integer)

    def __init__(self, order, inventory, quantity, price):
        self.id_orden = order
        self.id_inventario = inventory
        self.cantidad = quantity
        self.precio = price

    def add_item(self, user, inventory, quantity, price):
        self.id_orden = user
        self.id_inventario = inventory
        self.cantidad = quantity
        self.precio = price
        s.add(self)
        s.commit()
        resp = [201, {'message': 'Este item se agregó exitosamente'}]
        return False, resp


class WarehouseListOrder(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'lista_almacen_orden'

    id_lista_almacen_orden = Column(Integer, primary_key=True)
    id_item_orden = Column(
        Integer, ForeignKey('item_orden.id_item_orden'))
    id_lista_almacen = Column(Integer, ForeignKey('lista.lista_almacen.id_lista_almacen'))
    cantidad = Column(Integer)
    item_orden = relationship('Item', foreign_keys=[id_item_orden])
    lista_almacen = relationship('WarehouseList', foreign_keys=[id_lista_almacen])


class UserListOrder(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'lista_usuario_orden'

    id_lista_usuario_orden = Column(Integer, primary_key=True)
    id_item_orden = Column(
        Integer, ForeignKey('item_orden.id_item_orden'))
    id_lista_usuario = Column(Integer, ForeignKey('lista.lista_usuario.id_lista_usuario'))
    cantidad = Column(Integer)
    item_orden = relationship('Item', foreign_keys=[id_item_orden])
    lista_usuario = None


class PromoOrder(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'oferta_orden'

    id_oferta_orden = Column(Integer, primary_key=True)
    id_item_orden = Column(
        Integer, ForeignKey('item_orden.id_item_orden'))
    id_oferta_especial = Column(Integer, ForeignKey('inventario.oferta_especial.id_oferta_especial'))
    cantidad = Column(Integer)
    item_orden = relationship('Item', foreign_keys=[id_item_orden])
    oferta_especial = relationship('Promo', foreign_keys=[id_oferta_especial])


class Order(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'orden'

    id_orden = Column(Integer, primary_key=True)
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    fecha_orden = Column(DateTime(timezone=True))

    transaccion = relationship('ProductTransaction',
                               primaryjoin="Order.id_orden==ProductTransaction.id_orden",
                               backref=backref('orden', uselist=False), cascade="all, delete-orphan",
                               lazy='subquery')

    item = relationship('Item',
                        primaryjoin="Order.id_orden==Item.id_orden",
                        backref=backref('orden', uselist=False), cascade="all, delete-orphan",
                        lazy='subquery')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_producto_canasta,
            'usuario': self.usuario.nombre_completo,
            'producto': self.producto.nombre_producto,
            'cantidad': self.cantidad,
            'fecha': self.fecha_creacion.strftime("%Y-%m-%d"),
            'lista_almacen': self.wh_list,
            'inventario': self.inventario,
            'moneda': self.inventario.moneda,
            'precio': self.inventario.precio
        }

    # TODO: Arreglar procesamiento de inventario seleccionado
    def add_item(self, user, inventory, ordered_qty, payment_info):
        self.id_usuario = user
        self.fecha_orden = datetime.datetime.now(tz=pytz.utc)
        s.add(self)
        s.flush()
        total = 0
        moneda = None
        inventory_list = []
        wh_set = set()
        for i in range(len(inventory)):
            for item1 in inventory[i].inventory_list:
                point = wkb.loads(bytes(item1.almacen.coordenadas.data))
                wh_set.add((item1.almacen.id_almacen, point.x, point.y))
            quantity_remainder = ordered_qty[i]
            j = 0
            while quantity_remainder > 0:
                if quantity_remainder - inventory[i].inventory_list[j].cantidad <= 0:
                    cantidad = quantity_remainder
                    quantity_remainder = 0
                else:
                    cantidad = inventory[i].inventory_list[j].cantidad
                    quantity_remainder -= inventory[i].inventory_list[j].cantidad
                inventory_list.append([inventory[i].inventory_list[j], cantidad])
                order_item = Item(self.id_orden, inventory[i].inventory_list[j].id_inventario, cantidad,
                                  inventory[i].inventory_list[j].precio)
                self.item.append(order_item)
                total += (cantidad * inventory[i].inventory_list[j].precio)
                moneda = inventory[i].inventory_list[j].moneda
                j += 1
        print('Almacen!!!', wh_set)
        payment_info[1]['currency'] = moneda
        payment_info[1]['amount'] = int(total)
        transaccion = ProductTransaction(self.id_orden, payment_info)
        self.transaccion.append(transaccion)
        s.add(self)
        s.commit()
        if transaccion.id_estado_transaccion == 2:
            print('Generando tickets!')
            for item in inventory_list:
                item[0].reduce_inventory(item[1])
            from dbmodel.basket.basketmodel import BasketProduct
            BasketProduct().empty_basket(user)
        resp = [201, {'message': 'La orden se creo exitosamente'}]
        return False, resp

    @staticmethod
    def get_item(item_id):
        item = s.query(Order).filter(
            Order.id_orden == item_id).first()
        if not item:
            error = [404, {'message': 'Esta orden no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item


class ProductTransaction(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'transaccion_productos'

    id_transaccion_productos = Column(Integer, primary_key=True)
    id_orden = Column(
        Integer, ForeignKey('orden.id_orden'))
    id_metodo_pago = Column(Integer, nullable=False)
    id_estado_transaccion = Column(Integer, nullable=False)
    valor_transaccion = Column(Integer)
    referencia_pago = Column(String)
    fecha_transaccion = Column(DateTime(timezone=True))
    # orden = relationship('Order', foreign_keys=[id_orden])

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
        self.id_metodo_pago = payment_info[0]
        self.id_estado_transaccion = 1
        self.moneda = payment_info[1].get('currency')
        self.valor_transaccion = payment_info[1].get('amount')
        self.fecha_transaccion = datetime.datetime.now(tz=pytz.utc)
        s.add(self)
        s.flush()
        payment_info[1]['merchantTransactionId'] = self.id_transaccion_productos
        error, resp = payment.transaction(payment_info[1])
        if error:
            self.id_estado_transaccion = 3
        else:
            self.id_estado_transaccion = 2

        self.referencia_pago = resp[2]

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

'''Product order'''


''' Common '''


# class TransactionStatus(Base):
#     # __table_args__ = {'schema': 'orden'}
#     __tablename__ = 'estado_transaccion'
#
#     id_estado_transaccion = Column(Integer, primary_key=True)
#     estado_transaccion = Column(String)


class PaymentMethod(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'metodo_pago'

    id_metodo_pago = Column(Integer, primary_key=True)
    metodo_pago = Column(String)
''' Common '''

