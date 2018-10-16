import datetime
from sqlalchemy import (Column, DateTime, Date, String, Integer, Float, Boolean,
                        ForeignKey, func, and_, UniqueConstraint, or_)
from sqlalchemy.orm import relationship
from dbmodel.dbconfig import Base, s

from functools import partial
import numpy as np
partial(Column, nullable=False)


Base.metadata.schema = 'canasta'


class BasketWarehouseList(Base):
    __tablename__ = 'lista_almacen_canasta'

    id_lista_almacen_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_lista_almacen = Column(
        Integer, ForeignKey('lista.lista_almacen.id_lista_almacen'))
    cantidad = Column(Integer)
    fecha_creacion = Column(DateTime(timezone=True))
    usuario = relationship('User', foreign_keys=[id_usuario])
    lista_almacen = relationship('WarehouseList', foreign_keys=[id_lista_almacen])


class BasketUserList(Base):
    __tablename__ = 'lista_usuario_canasta'

    id_lista_usuario_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_lista_usuario = Column(
        Integer, ForeignKey('lista.lista_usuario.id_lista_usuario'))
    cantidad = Column(Integer)
    fecha_creacion = Column(DateTime(timezone=True))
    usuario = relationship('User', foreign_keys=[id_usuario])
    lista_usuario = relationship('UserList', foreign_keys=[id_lista_usuario])


class BasketPromo(Base):
    __tablename__ = 'oferta_canasta'

    id_oferta_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_oferta_especial = Column(
        Integer, ForeignKey('inventario.oferta_especial.id_oferta_especial'))
    cantidad = Column(Integer)
    fecha_creacion = Column(DateTime(timezone=True))
    usuario = relationship('User', foreign_keys=[id_usuario])
    oferta_especial = relationship('Promo', foreign_keys=[id_oferta_especial])


class BasketProduct(Base):
    __tablename__ = 'producto_canasta'

    id_producto_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_producto = Column(
        Integer, ForeignKey('inventario.producto.id_producto'))
    cantidad = Column(Integer, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)
    usuario = relationship('User', foreign_keys=[id_usuario])
    producto = relationship('Product', foreign_keys=[id_producto])
    wh_list = None
    inventario = None

    __table_args__ = (UniqueConstraint('id_usuario', 'id_producto', name='canasta_usuario_producto'),)

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

    @staticmethod
    def get_basket(user):
        basket = s.query(BasketProduct).filter(
            BasketProduct.id_usuario == user).all()
        if not basket:
            error = [404, {'message': 'No existen productos en la canasta',
                           'action': 'Agregue productos a la canasta'}]
            return True, error

        return False, basket

    @staticmethod
    def get_basket_basic(user):
        basket = s.query(BasketProduct).filter(
            BasketProduct.id_usuario == user).all()
        if not basket:
            error = [404, {'message': 'No existen productos en la canasta',
                           'action': 'Agregue productos a la canasta'}]
            return True, error
        return False, basket

    @staticmethod
    def get_item_basket(user, product):
        item = s.query(BasketProduct).filter(
            and_(BasketProduct.id_usuario == user,
                 BasketProduct.id_producto == product)
        ).first()
        if not item:
            error = [404, {'message': 'Este producto no se encuentra en la canasta',
                           'action': 'Agregue este producto o realice la consulta con otro producto'}]
            return True, error
        return False, item

    @staticmethod
    def get_item_basket_by_id(id_item):
        item = s.query(BasketProduct).filter(BasketProduct.id_producto_canasta == id_item).first()
        if not item:
            error = [404, {'message': 'Este item no existe',
                           'action': 'Realice la consulta de nuevo cambiando el valor'}]
            return True, error
        return False, item

    def add_item(self, user, product, quantity):
        self.id_usuario = user
        self.id_producto = product
        self.cantidad = quantity
        self.fecha_creacion = datetime.datetime.now()
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El item de canasta se añadió exitosamente'}]
        return False, resp

    def update_item(self, user, product, quantity):
        error, item = self. get_item_basket(user, product)
        if error:
            return True, item
        item.cantidad = quantity
        s.add(item)
        s.commit()
        resp = [201, {'message': 'El item se actualizó exitosamente'}]
        return False, resp

    def delete_item(self, user, product):
        error, item = self.get_item_basket(user, product)
        if error:
            return True, item
        s.delete(item)
        s.commit()
        resp = [201, {'message': 'El item se eliminó exitosamente'}]
        return False, resp

    def empty_basket(self, user):
        error, basket = self.get_basket_basic(user)
        if error:
            return True, basket
        for item in basket:
            s.delete(item)
        s.commit()

