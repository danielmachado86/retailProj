from sqlalchemy import Column, DateTime, Date, String, Integer, Float, Boolean, ForeignKey, func, and_, UniqueConstraint
from sqlalchemy.orm import relationship
from dbmodel.dbconfig import Base


from functools import partial
partial(Column, nullable=False)


Base.metadata.schema = 'canasta'

class BasketWarehouseList(Base):
    # __table_args__ = {'schema': 'canasta'}
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
    # __table_args__ = {'schema': 'canasta'}
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
    # __table_args__ = {'schema': 'canasta'}
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
    # __table_args__ = {'schema': 'canasta'}
    __tablename__ = 'producto_canasta'

    id_oferta_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_producto = Column(
        Integer, ForeignKey('inventario.producto.id_producto'))
    cantidad = Column(Integer)
    fecha_creacion = Column(DateTime(timezone=True))
    usuario = relationship('User', foreign_keys=[id_usuario])
    producto = relationship('Product', foreign_keys=[id_producto])
