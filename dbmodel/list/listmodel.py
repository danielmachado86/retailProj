from sqlalchemy import Column, DateTime, Date, String, Integer, Boolean, ForeignKey, func, and_, UniqueConstraint
from sqlalchemy.orm import relationship
from dbmodel.dbconfig import Base


from functools import partial
partial(Column, nullable=False)


Base.metadata.schema = 'lista'

class ListCategory(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'categoria_lista'

    id_categoria_lista = Column(Integer, primary_key=True)
    parent = Column(
        Integer, ForeignKey('categoria_lista.id_categoria_lista'))
    categoria_lista = Column(String)
    parent_rs = relationship('ListCategory', foreign_keys=[parent])


class WarehouseListItem(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'item_lista_almacen'

    id_item_lista_almacen = Column(Integer, primary_key=True)
    id_lista_almacen = Column(
        Integer, ForeignKey('lista_almacen.id_lista_almacen'))
    id_inventario = Column(
        Integer, ForeignKey('inventario.inventario.id_inventario'))
    cantidad = Column(Integer)
    lista_almacen = relationship('WarehouseList', foreign_keys=[id_lista_almacen])
    inventario = relationship('Stock', foreign_keys=[id_inventario])


class UserListItem(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'item_lista_usuario'

    id_item_lista_usuario = Column(Integer, primary_key=True)
    id_lista_usuario = Column(
        Integer, ForeignKey('lista_almacen.id_lista_almacen'))
    id_producto = Column(
        Integer, ForeignKey('inventario.producto.id_producto'))
    cantidad = Column(Integer)
    lista_usuario = None
    producto = None


class WarehouseList(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'lista_almacen'

    id_lista_almacen = Column(Integer, primary_key=True)
    id_miembro_almacen = Column(
        Integer, ForeignKey('almacen.miembro_almacen.id_miembro_almacen'))
    id_categoria_lista = Column(
        Integer, ForeignKey('categoria_lista.id_categoria_lista'))
    id_tipo_oferta = Column(
        Integer, ForeignKey('inventario.tipo_oferta.id_tipo_oferta'))
    id_tipo_lista = Column(
        Integer, ForeignKey('tipo_lista.id_tipo_lista'))
    nombre_lista = Column(String)
    cantidad_disponible = Column(Integer)
    fecha_inicio = Column(DateTime(timezone=True))
    fecha_final = Column(DateTime(timezone=True))
    fecha_creacion = Column(DateTime(timezone=True))
    miembro_almacen = None
    categoria_lista = relationship('ListCategory', foreign_keys=[id_categoria_lista])
    tipo_oferta = relationship('PromoType', foreign_keys=[id_tipo_oferta])
    tipo_lista = relationship('ListType', foreign_keys=[id_tipo_lista])


class UserList(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'lista_usuario'

    id_lista_usuario = Column(Integer, primary_key=True)
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_miembro = Column(
        Integer, ForeignKey('usuario.miembro.id_miembro'))
    id_tipo_lista = Column(
        Integer, ForeignKey('tipo_lista.id_tipo_lista'))
    id_tipo_distribucion_lista = Column(
        Integer, ForeignKey('tipo_distribucion_lista.id_tipo_distribucion_lista'))
    id_categoria_lista = Column(
        Integer, ForeignKey('categoria_lista.id_categoria_lista'))
    nombre_lista = Column(String)
    descripcion = Column(String)
    fecha_creacion = Column(DateTime(timezone=True))
    usuario = relationship('User', foreign_keys=[id_usuario])
    miembro = relationship('Membership', foreign_keys=[id_miembro])
    tipo_lista = relationship('ListType', foreign_keys=[id_tipo_lista])
    tipo_distribucion_lista = relationship('ListDistributionType', foreign_keys=[id_tipo_distribucion_lista])
    categoria_lista = relationship('ListCategory', foreign_keys=[id_categoria_lista])


class ListDistributionType(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'tipo_distribucion_lista'

    id_tipo_distribucion_lista = Column(Integer, primary_key=True)
    tipo_distribucion_lista = Column(String)


class ListType(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'tipo_lista'

    id_tipo_lista = Column(Integer, primary_key=True)
    tipo_lista = Column(String)
