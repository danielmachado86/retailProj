from sqlalchemy import Column, DateTime, Date, String, Integer, Float, Boolean, ForeignKey, func, and_, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from dbmodel.dbconfig import Base, s
from dbmodel.warehouse.warehousemodel import Warehouse, WarehouseMember

Base.metadata.schema = 'inventario'


class ProductCategory(Base):
    __tablename__ = 'categoria_producto'

    id_categoria = Column(Integer, primary_key=True)
    parent = Column(
        Integer, ForeignKey('categoria_producto.id_categoria'), nullable=True)
    categoria = Column(String, nullable=False, unique=True)
    parent_rs = relationship('ProductCategory', foreign_keys=[parent])

    def add_item(self, parent, category):
        self.parent = parent
        self.categoria = category
        s.add(self)
        s.commit()

    @staticmethod
    def get_category_id(category):
        item = s.query(ProductCategory).filter(
            ProductCategory.categoria == category).first()
        return item.id_categoria


class ProductSpecification(Base):
    __tablename__ = 'especificacion_producto'

    id_especificacion_producto = Column(Integer, primary_key=True)
    id_producto = Column(
        Integer, ForeignKey('producto.id_producto'), nullable=False)
    atributo = Column(String, nullable=False)
    valor = Column(String, nullable=False)
    producto = relationship('Product', foreign_keys=[id_producto])


class Manufacturer(Base):
    __tablename__ = 'fabricante'

    id_fabricante = Column(Integer, primary_key=True)
    nombre_fabricante = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String, nullable=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_fabricante,
            'fabricante': self.nombre_fabricante,
            'descripcion': self.descripcion
        }

    @staticmethod
    def check_manufacturer_exists_by_name(name):
        if s.query(Manufacturer).filter(
                        Manufacturer.nombre_fabricante == name).first():
            mssg = [409, {'message': 'Este fabricante existe'}]
            return True, mssg
        mssg = [200, {'message': 'Este fabricante no existe'}]
        return False, mssg

    def add_item(self, name, description):
        error, mssg = Manufacturer.check_manufacturer_exists_by_name(name)
        if error:
            return True, mssg
        self.nombre_fabricante = name
        self.descripcion = description
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El fabricante se ha creado exitosamente'}]
        return False, resp


class ManufacturerImage(Base):
    __tablename__ = 'imagen_fabricante'

    id_imagen_fabricante = Column(Integer, primary_key=True)
    id_fabricante = Column(
        Integer, ForeignKey('fabricante.id_fabricante'), nullable=False)
    descripcion = Column(String, nullable=False)
    archivo = Column(String, nullable=False)
    fabricante = relationship('Manufacturer', foreign_keys=[id_fabricante])


class ProductImage(Base):
    __tablename__ = 'imagen_producto'

    id_imagen_producto = Column(Integer, primary_key=True)
    id_producto = Column(
        Integer, ForeignKey('producto.id_producto'), nullable=False)
    descripcion = Column(String, nullable=False)
    archivo = Column(String, nullable=False)
    producto = relationship('Product', foreign_keys=[id_producto])


class Inventory(Base):
    __tablename__ = 'inventario'

    id_inventario = Column(Integer, primary_key=True)
    id_producto = Column(
        Integer, ForeignKey('producto.id_producto'), nullable=False)
    id_almacen = Column(
        Integer, ForeignKey('almacen.almacen.id_almacen'), nullable=False)
    id_miembro_almacen = Column(
        Integer, ForeignKey('almacen.miembro_almacen.id_miembro_almacen'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    unidades = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    fecha_vencimiento = Column(DateTime, nullable=False)
    producto = relationship('Product', foreign_keys=[id_producto])
    almacen = relationship('Warehouse', foreign_keys=[id_almacen])
    miembro_almacen = relationship('WarehouseMember', foreign_keys=[id_miembro_almacen])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_inventario,
            'producto': self.producto.nombre_producto,
            'fabricante': self.producto.fabricante.nombre_fabricante,
            'almacen': self.almacen.nombre,
            'responsable': self.miembro_almacen.usuario.nombre_completo,
            'cantidad': self.cantidad,
            'unidades': self.unidades,
            'precio': self.precio,
            'vencimiento': self.fecha_vencimiento.strftime("%Y-%m-%d")
        }

    @staticmethod
    def get_item(item_id):
        item = s.query(Inventory).filter(
            Inventory.id_inventario == item_id).first()
        if not item:
            error = [404, {'message': 'Este inventario no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item

    def add_item(self, product, wh, wh_member, quantity, units, price, exp_date):
        self.id_producto = product
        self.id_almacen = wh
        self.id_miembro_almacen = wh_member
        self.cantidad = quantity
        self.unidades = units
        self.precio = price
        self.fecha_vencimiento = exp_date
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El inventario se ha creado exitosamente'}]
        return False, resp


class Promo(Base):
    __tablename__ = 'oferta_especial'

    id_oferta_especial = Column(Integer, primary_key=True)
    id_miembro_almacen = Column(
        Integer, ForeignKey('almacen.miembro_almacen.id_miembro_almacen'), nullable=False)
    id_inventario = Column(
        Integer, ForeignKey('inventario.id_inventario'), nullable=False)
    id_tipo_oferta = Column(
        Integer, ForeignKey('tipo_oferta.id_tipo_oferta'), nullable=False)
    cantidad_disponible = Column(Integer, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_final = Column(DateTime(timezone=True), nullable=False)
    miembro_almacen = None
    inventario = relationship('Inventory', foreign_keys=[id_inventario])
    tipo_oferta = relationship('PromoType', foreign_keys=[id_tipo_oferta])


class Product(Base):
    __tablename__ = 'producto'

    id_producto = Column(Integer, primary_key=True)
    id_categoria = Column(
        Integer, ForeignKey('categoria_producto.id_categoria'), nullable=False)
    id_fabricante = Column(
        Integer, ForeignKey('fabricante.id_fabricante'), nullable=False)
    nombre_producto = Column(String, index=True, unique=True, nullable=False)
    codigo_barras = Column(String, index=True, unique=True, nullable=False)
    categoria = relationship('ProductCategory', foreign_keys=[id_categoria])
    fabricante = relationship('Manufacturer', foreign_keys=[id_fabricante])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_producto,
            'categoria': self.categoria.categoria,
            'fabricante': self.fabricante.nombre_fabricante,
            'nombre': self.nombre_producto
        }

    @staticmethod
    def get_item(item_id):
        item = s.query(Product).filter(
            Product.id_producto == item_id).first()
        if not item:
            error = [404, {'message': 'Esta membresia no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item

    def add_item(self, category, manufacturer, name, barcode):
        self.id_categoria = category
        self.id_fabricante = manufacturer
        self.nombre_producto = name
        self.codigo_barras = barcode
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El producto se ha creado exitosamente'}]
        return False, resp


class PromoType(Base):
    __tablename__ = 'tipo_oferta'

    id_tipo_oferta = Column(Integer, primary_key=True)
    nombre_oferta = Column(String, nullable=False)
    descuento = Column(Float, nullable=False)
