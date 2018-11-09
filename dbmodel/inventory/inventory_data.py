import collections
import re
import datetime
from sqlalchemy import func, or_, and_
from sqlalchemy.sql.functions import ReturnTypeFromArgs

import numpy as np
from unidecode import unidecode
import difflib

from dbmodel.dbconfig import s
from dbmodel.res.custom_exceptions import ResourceConflict, InvalidArgument
from dbmodel.database_model import ProductCategoryModel, ManufacturerModel, InventoryModel, InventoryInputModel, InventoryOutputModel, ProductModel
from dbmodel.warehouse.warehouse_data import get_warehouse_by_location


class ProductCategory(ProductCategoryModel):

    def __init__(self, parent, category):
        self.parent = parent
        self.categoria = category

    def add_product_category(self):
        s.add(self)
        s.commit()

def get_product_category_id(category):
    item = s.query(ProductCategory).filter(
        ProductCategory.categoria == category).first()
    return item.id_categoria



class Manufacturer(ManufacturerModel):

    def __init__(self, name, description):
        check_manufacturer_exists_by_name(name)
        self.nombre_fabricante = name
        self.descripcion = description

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_fabricante,
            'fabricante': self.nombre_fabricante,
            'descripcion': self.descripcion
        }

    def add_manufacturer(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def check_manufacturer_exists_by_name(name):
    if s.query(Manufacturer).filter(
                    Manufacturer.nombre_fabricante == name).first():
        raise ResourceConflict('Este fabricante ya existe')
    return False


class Inventory(InventoryModel):

    cantidad_entrada = 0
    cantidad_salida = 0

    def __init__(self, product, wh, price):
        self.id_producto = product
        self.id_almacen = wh
        self.precio = price

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_inventario,
            'producto': self.producto.nombre_producto,
            'fabricante': self.producto.fabricante.nombre_fabricante,
            'almacen': self.almacen.nombre,
            'cantidad': self.cantidad_entrada+self.cantidad_salida,
            'precio': self.precio,
            'distancia': self.distancia
        }

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

def get_inventory_quantity_by_id(id_inventario, inventory_sold):
    inventory_inputs = s.query(func.sum(InventoryInput.cantidad_entrada)).filter(InventoryInput.id_inventario == id_inventario)
    inventory_outputs = s.query(func.sum(InventoryOutput.cantidad_salida)).filter(InventoryOutput.id_inventario == id_inventario)
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


def process_inventory_matrix(basket, parameters, location):
    whs = get_warehouse_by_location(location)
    product_filter = [Inventory.id_producto == item.id_producto for item in basket]
    # TODO: Implementar respuesta de error si whs es vacio
    wh_filter = [Inventory.id_almacen == wh.id_almacen for wh in whs]
    b_query = s.query(InventoryInput.id_inventario, func.sum(InventoryInput.cantidad_entrada).label('input')).group_by(
        InventoryInput.id_inventario).subquery()
    c_query = s.query(InventoryOutput.id_inventario, func.sum(InventoryOutput.cantidad_salida).label('output')).group_by(
        InventoryOutput.id_inventario).subquery()
    raw_inventory_list = s.query(Inventory, b_query.c.input, c_query.c.output).outerjoin(
        (b_query, b_query.c.id_inventario == Inventory.id_inventario)).outerjoin(
        (c_query, c_query.c.id_inventario == Inventory.id_inventario)).filter(and_(or_(*product_filter), or_(*wh_filter)))
    inventory_list = []
    for inventory in raw_inventory_list:
        if inventory[1] is None: inventory[0].cantidad_entrada = 0
        else: inventory[0].cantidad_entrada = inventory[1]
        if inventory[2] is None: inventory[0].cantidad_salida = 0
        else: inventory[0].cantidad_salida = inventory[2]
        inventory_list.append(inventory[0])
    active_products = np.asarray([item.id_producto for item in basket])
    basket_item_qty = np.asarray([item.cantidad for item in basket])
    wh_list = np.asarray([item.id_almacen for item in whs])
    wh_distance = np.asarray([item.distancia for item in whs])
    initial_matrix = np.zeros((active_products.size, wh_list.size))
    price_matrix = np.zeros((active_products.size, wh_list.size))
    total_qty = np.zeros((active_products.size, wh_list.size))
    price_matrix[:] = float('infinity')
    inventory_matrix = np.empty( (active_products.size, wh_list.size), dtype=object)

    for item in inventory_list:
        pr_index = np.where(active_products == item.id_producto)[0][0]
        wh_index = np.where(wh_list == item.id_almacen)[0][0]
        total_qty[pr_index, wh_index] += (item.cantidad_entrada - item.cantidad_salida)
        initial_matrix[pr_index, wh_index] = 1
        inventory_matrix[pr_index, wh_index] = item
        price_matrix[pr_index, wh_index] = item.precio * basket_item_qty[pr_index]

    below_ordered_qty = np.less(total_qty, basket_item_qty[:, np.newaxis])
    initial_matrix *= 1 - below_ordered_qty

    pr_quantity = np.sum(initial_matrix, axis=0)
    wh_discarded = np.where(pr_quantity == 0)[0]
    wh_quantity = np.sum(initial_matrix, axis=1)
    pr_not_found = np.where(wh_quantity == 0)[0]

    initial_matrix = np.delete(initial_matrix, wh_discarded, axis=1)
    wh_list = np.delete(wh_list, wh_discarded, axis=0)
    wh_distance = np.delete(wh_distance, wh_discarded, axis=0)
    initial_matrix = np.delete(initial_matrix, pr_not_found, axis=0)
    active_products = np.delete(active_products, pr_not_found, axis=0)
    price_matrix = np.delete(price_matrix, wh_discarded, axis=1)
    price_matrix = np.delete(price_matrix, pr_not_found, axis=0)

    min_price = np.min(price_matrix, axis=1)

    p_weight = 0.25
    d_weight = 0.25

    if parameters['closer'] is True:
        p_weight = 0.1
        d_weight = 0.4

    p_index = (min_price[:, np.newaxis] / price_matrix) * p_weight
    d_index = (np.min(wh_distance) / wh_distance) * d_weight
    q_index = np.zeros((1, wh_list.size))[0]

    quantity = np.sum(initial_matrix, axis=0)
    max_quantity = max(quantity)

    repeated = np.zeros((1, wh_list.size))[0]
    ap = np.ones((1, active_products.size))
    a_wh = np.ones((1, wh_list.size))
    matrix = initial_matrix
    selected_matrix = np.zeros((active_products.size, wh_list.size))

    complete = False
    while not complete:
        q_index = ((quantity - repeated) / max_quantity) * 0.5
        best_indices = np.sum((d_index + q_index + p_index) * matrix, axis=0)
        index = np.argmax(best_indices, axis=0)
        a_wh[0, index] = 0
        selected_matrix[:, index] = matrix[:, index]
        repeated += np.sum(matrix[:, index][:, np.newaxis] * (matrix * a_wh), axis=0)
        ap -= matrix[:, index]
        matrix *= (1 - matrix[:, index][:, np.newaxis])
        if int(np.sum(ap)) == 0:
            complete = True

    final_matrix = (p_index + d_index + q_index) * selected_matrix
    max_index = np.argmax(final_matrix, axis=1)
    selected_inv_matrix = inventory_matrix[np.arange(inventory_matrix.shape[0]), max_index]
    selected_inv_matrix = selected_inv_matrix.tolist()
    inventory_selected = set(zip(selected_inv_matrix, basket_item_qty))
    print(inventory_selected)
    return inventory_selected

class InventoryInput(InventoryInputModel):

    def __init__(self, id_inventario, id_miembro_almacen, cantidad_entrada, fecha_vencimiento):
        self.id_inventario = id_inventario
        self.id_miembro_almacen = id_miembro_almacen
        self.cantidad_entrada = cantidad_entrada
        self.fecha_entrada = datetime.datetime.now()
        self.fecha_vencimiento = fecha_vencimiento

    def add_inventory_input(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


class InventoryOutput(InventoryOutputModel):

    def __init__(self, id_inventario, id_miembro_almacen, cantidad_salida, motivo_salida):
        self.id_inventario = id_inventario
        self.id_miembro_almacen = id_miembro_almacen
        self.cantidad_salida = cantidad_salida
        self.motivo_salida = motivo_salida
        self.fecha_salida = datetime.datetime.now()

    def add_inventory_output(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


class unaccent(ReturnTypeFromArgs):
    pass


class Product(ProductModel):

    search_similarity_index = None

    def __init__(self, category, manufacturer, name, barcode, meas_unit, sku, taxable):
        self.id_categoria = category
        self.id_fabricante = manufacturer
        self.nombre_producto = name
        self.unidad_medida = meas_unit
        self.upc = barcode
        self.sku = sku
        self.taxable = taxable

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_producto,
            'categoria': self.categoria.categoria,
            'fabricante': self.fabricante.nombre_fabricante,
            'nombre': self.nombre_producto
        }

    def add_product(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def modify_item(self, category, manufacturer, name, barcode):
        if self.id_categoria != category:
            self.id_categoria = category
        if self.id_fabricante != manufacturer:
            self.id_fabricante = manufacturer
        if self.nombre_producto != name:
            self.nombre_producto = name
        if self.upc != barcode:
            self.upc = barcode
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_category(self, category):
        if self.id_categoria != category:
            self.id_categoria = category
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_manufacturer(self, manufacturer):
        if self.id_fabricante != manufacturer:
            self.id_fabricante = manufacturer
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_name(self, name):
        if self.nombre_producto != name:
            self.nombre_producto = name
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_barcode(self, barcode):
        if self.upc != barcode:
            self.upc = barcode
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def make_list(item_list):
    final_list = []
    for item in item_list:
        final_list.append(item.serialize)
    return final_list


def search_product(keywords):
    print('Original list: ', keywords)
    keywords = unidecode(keywords).lower()
    keyword_list = re.split("[^a-zA-Z0-9á-ú']+", keywords)

    keyword_list = collections.OrderedDict.fromkeys(keyword_list)
    keyword_list = [keyword for keyword in keyword_list if not (keyword is '' or len(keyword) <= 2)]

    print('Processed list: ', keyword_list)

    mfr_kw_filter = [Manufacturer.nombre_fabricante.ilike("%" + kw + "%") for kw in keyword_list]
    mfrs = s.query(Manufacturer.id_fabricante).filter(or_(*mfr_kw_filter)).all()

    print('Manufacturer list ', [mfr.id_fabricante for mfr in mfrs])

    cat_kw_filter = [ProductCategory.categoria.ilike("%" + kw + "%") for kw in keyword_list]
    categories = s.query(ProductCategory.id_categoria).filter(or_(*cat_kw_filter)).all()
    print('Category list ', [cat.id_categoria for cat in categories])

    keyword_filter = [unaccent(Product.nombre_producto).ilike("%" + keyword + "%") for keyword in keyword_list]
    keyword_filter.extend([Product.id_fabricante == kw for kw in mfrs])
    keyword_filter.extend([Product.id_categoria == kw for kw in categories])
    items = s.query(Product, func.concat(Manufacturer.nombre_fabricante, ' ', Product.nombre_producto, ' ', ProductCategory.categoria)).join(Manufacturer).join(ProductCategory).filter(or_(*keyword_filter)).all()
    for item in items:
        print('Query:', item[1].lower())
        print('Keywords:', keywords.lower())
        item[0].search_similarity_index = difflib.SequenceMatcher(None, item[1].lower().split(), keywords.split()).quick_ratio()
    items.sort(key=lambda item: item[0].search_similarity_index, reverse=True)
    return items


def get_product(item_id):
    if not item_id or '':
        raise InvalidArgument('El campo item_id no puede estar vacio')
    item = s.query(Product).filter(
        Product.id_producto == item_id).first()
    return item


if __name__ == '__main__':
    pass