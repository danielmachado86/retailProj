from sqlalchemy import Column, DateTime, Date, String, Integer, Boolean, ForeignKey, func, and_, UniqueConstraint
from sqlalchemy.orm import relationship
from dbmodel.dbconfig import Base


from functools import partial
partial(Column, nullable=False)

Base.metadata.schema = 'orden'

''' Order subscription '''


class SubscriptionTransaction(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'transaccion_suscripcion'

    id_transaccion_suscripcion = Column(Integer, primary_key=True)
    id_suscripcion_orden = Column(
        Integer, ForeignKey('suscripcion_orden.id_suscripcion_orden'))
    id_metodo_pago = Column(Integer, ForeignKey('metodo_pago.id_metodo_pago'))
    id_estado_transaccion = Column(Integer, ForeignKey('estado_transaccion.id_estado_transaccion'))
    valor_transaccion = Column(Integer)
    referencia_pago = Column(String)
    fecha_transaccion = Column(DateTime(timezone=True))
    suscripcion_orden = relationship('SubscriptionOrder', foreign_keys=[id_suscripcion_orden])
    metodo_pago = relationship('PaymentMethod', foreign_keys=[id_metodo_pago])
    estado_transaccion = relationship('TransactionStatus', foreign_keys=[id_estado_transaccion])


class SubscriptionOrder(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'suscripcion_orden'

    id_suscripcion_orden = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_plan = Column(Integer, ForeignKey('usuario.plan_suscripcion.id_plan'))
    fecha_orden = Column(DateTime(timezone=True))
    usuario = None
    plan = None
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
    orden = relationship('Order', foreign_keys=[id_orden])
    inventario = None


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
    usuario = relationship('User', foreign_keys=[id_usuario])


class ProductTransaction(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'transaccion_productos'

    id_transaccion_productos = Column(Integer, primary_key=True)
    id_orden = Column(
        Integer, ForeignKey('orden.id_orden'))
    id_metodo_pago = Column(Integer, ForeignKey('metodo_pago.id_metodo_pago'))
    id_estado_transaccion = Column(Integer, ForeignKey('estado_transaccion.id_estado_transaccion'))
    valor_transaccion = Column(Integer)
    referencia_pago = Column(String)
    fecha_transaccion = Column(DateTime(timezone=True))
    orden = relationship('Order', foreign_keys=[id_orden])
    metodo_pago = relationship('PaymentMethod', foreign_keys=[id_metodo_pago])
    estado_transaccion = relationship('TransactionStatus', foreign_keys=[id_estado_transaccion])
'''Product order'''


''' Common '''


class TransactionStatus(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'estado_transaccion'

    id_estado_transaccion = Column(Integer, primary_key=True)
    estado_transaccion = Column(String)


class PaymentMethod(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'metodo_pago'

    id_metodo_pago = Column(Integer, primary_key=True)
    metodo_pago = Column(String)
''' Common '''

