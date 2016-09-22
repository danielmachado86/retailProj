import re
from sqlalchemy import Column, DateTime, Date, String, Integer, Float, Boolean, ForeignKey, func, and_, UniqueConstraint, or_, and_
from sqlalchemy.orm import relationship, backref

from dbmodel.dbconfig import Base, s

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


class InventoryObj:
    warehouse_id = None
    product_id = None
    inventory_list = []
    total_quantity = 0
    distance = float('infinity')
    price = 0

    def __init__(self, product_list):
        product_list.sort(key=lambda x: x.cantidad, reverse=False)
        self.inventory_list = product_list
        for item in product_list:
            self.warehouse_id = item.id_almacen
            self.product_id = item.id_producto
            self.total_quantity += item.cantidad
            self.distance = item.almacen.distancia
            if item.precio > self.price:
                self.price = item.precio

    def get_warehouse_id(self):
        return self.warehouse_id


class Inventory(Base):
    __tablename__ = 'inventario'

    id_inventario = Column(Integer, primary_key=True)
    id_producto = Column(
        Integer, ForeignKey('producto.id_producto'), nullable=False, index=True)
    id_almacen = Column(
        Integer, ForeignKey('almacen.almacen.id_almacen'), nullable=False)
    id_miembro_almacen = Column(
        Integer, ForeignKey('almacen.miembro_almacen.id_miembro_almacen'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    unidades = Column(String, nullable=False)
    moneda = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    fecha_vencimiento = Column(DateTime, nullable=False)
    distancia = float('infinity')
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
            'moneda': self.moneda,
            'precio': self.precio,
            'vencimiento': self.fecha_vencimiento.strftime("%Y-%m-%d"),
            'distancia': self.distancia
        }

    @staticmethod
    def get_item(item_id):
        item = s.query(Inventory).filter(
            Inventory.id_inventario == item_id).first()
        if not item:
            error = [404, {'message': 'Este producto no existe en inventario',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item

    @staticmethod
    def get_item_by_product_id(product_id, whs):
        inventory = None
        if whs:
            inventory_wh_filter = [Inventory.id_almacen == wh.id_almacen for wh in whs]
            inventory = s.query(Inventory).filter(
                and_(Inventory.id_producto == product_id, or_(*inventory_wh_filter), Inventory.cantidad > 0)).all()
        if not inventory:
            error = [404, {'message': 'Este producto no existe en inventario',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        wh_list = []
        wh_dict = {}
        for i in range(len(inventory)):
            for wh in whs:
                if inventory[i].id_almacen == wh.id_almacen:
                    inventory[i].almacen.distancia = wh.distancia
            if inventory[i].id_almacen not in wh_dict:
                wh_dict[inventory[i].id_almacen] = [inventory[i]]
            else:
                wh_dict[inventory[i].id_almacen].append(inventory[i])
        for k in wh_dict:
            wh_list.append(InventoryObj(wh_dict[k]))
        return False, wh_list

    def add_item(self, product, wh, wh_member, quantity, units, currency, price, exp_date):
        self.id_producto = product
        self.id_almacen = wh
        self.id_miembro_almacen = wh_member
        self.cantidad = quantity
        self.unidades = units
        self.moneda = currency
        self.precio = price
        self.fecha_vencimiento = exp_date
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El inventario se ha creado exitosamente'}]
        return False, resp

    def reduce_inventory(self, quantity):
        self.cantidad -= quantity
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El inventario se ha reducido exitosamente'}]
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
        Integer, ForeignKey('categoria_producto.id_categoria'), nullable=False, index=True)
    id_fabricante = Column(
        Integer, ForeignKey('fabricante.id_fabricante'), nullable=True, index=True)
    nombre_producto = Column(String, index=True, unique=True, nullable=False)
    upc = Column(String, index=True, unique=True, nullable=True)
    sku = Column(String, unique=True, nullable=True)
    taxable = Column(Boolean, index=True, unique=True, nullable=True)
    categoria = relationship('ProductCategory', foreign_keys=[id_categoria])
    fabricante = relationship('Manufacturer', foreign_keys=[id_fabricante])
    search_similarity_index = None

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
    def make_list(item_list):
        final_list = []
        for item in item_list:
            final_list.append(item.serialize)
        return final_list

    def search_product(self, keywords):
        from difflib import SequenceMatcher
        keyword_list = re.split("[^a-zA-Z0-9]+", keywords)
        print('Keyword list ', keyword_list)

        checked = []
        i = 0
        while i < len(keyword_list):
            if keyword_list[i] is '' or len(keyword_list[i]) == 1:
                keyword_list.pop(i)
            if not i < len(keyword_list):
                break
            if keyword_list[i] not in checked:
                checked.append(keyword_list[i])
            i += 1
        keyword_list = checked

        print('Keyword list ', keyword_list)

        mfrs = []
        cat = []
        if keyword_list:
            mfr_kw_filter = [Manufacturer.nombre_fabricante.ilike("%" + kw + "%") for kw in keyword_list]
            mfrs.extend(s.query(Manufacturer.id_fabricante).filter(or_(*mfr_kw_filter)).all())
            for i in range(len(mfrs)):
                mfrs[i - 1] = mfrs[i - 1].id_fabricante
            print('Manufacturer list ', mfrs)

            cat_kw_filter = [ProductCategory.categoria.ilike("%" + kw + "%") for kw in keyword_list]
            cat.extend(s.query(ProductCategory.id_categoria).filter(or_(*cat_kw_filter)).all())
            for i in range(len(cat)):
                cat[i - 1] = cat[i - 1].id_categoria
            print('Category list ', cat)

        kw_filter = [Product.nombre_producto.ilike("%" + kw + "%") for kw in keyword_list]
        if mfrs:
            kw_filter.extend([Product.id_fabricante == kw for kw in mfrs])
        if cat:
            kw_filter.extend([Product.id_categoria == kw for kw in cat])
        items = []
        if kw_filter:
            items = s.query(Product).filter(or_(*kw_filter)).all()
            for item in items:
                item.search_similarity_index = SequenceMatcher(None, item.nombre_producto.lower().split(), keywords.lower().split()).quick_ratio()
            items.sort(key=lambda item: item.search_similarity_index, reverse=True)

        if not items:
            error = [404, {'message': 'No se encontraron resultados',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, items

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
        self.upc = barcode
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El producto se ha creado exitosamente'}]
        return False, resp

    def modify_item(self, category, manufacturer, name, barcode):
        self.id_categoria = category
        self.id_fabricante = manufacturer
        self.nombre_producto = name
        self.upc = barcode
        s.commit()
        resp = [201, {'message': 'El producto se ha modificado exitosamente'}]
        return False, resp

    def change_category(self, category):
        self.id_categoria = category
        s.commit()
        resp = [201, {'message': 'La categoría se ha cambiado exitosamente'}]
        return False, resp

    def change_manufacturer(self, manufacturer):
        self.id_fabricante = manufacturer
        s.commit()
        resp = [201, {'message': 'La categoría se ha cambiado exitosamente'}]
        return False, resp

    def change_name(self, name):
        self.nombre_producto = name
        s.commit()
        resp = [201, {'message': 'El nombre se ha cambiado exitosamente'}]
        return False, resp

    def change_barcode(self, barcode):
        self.upc = barcode
        s.commit()
        resp = [201, {'message': 'El código de barras se ha cambiado exitosamente'}]
        return False, resp


class PromoType(Base):
    __tablename__ = 'tipo_oferta'

    id_tipo_oferta = Column(Integer, primary_key=True)
    nombre_oferta = Column(String, nullable=False)
    descuento = Column(Float, nullable=False)
