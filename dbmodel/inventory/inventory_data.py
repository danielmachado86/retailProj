import re
import datetime
from sqlalchemy import func, or_, and_
from sqlalchemy.sql.functions import ReturnTypeFromArgs

import numpy as np
from unidecode import unidecode

from dbmodel.dbconfig import s
from dbmodel.res.custom_exceptions import ResourceConflict, InvalidArgument
from dbmodel.database_model import ProductCategoryModel, ManufacturerModel, InventoryModel, InventoryInModel, InventoryOutModel, ProductModel
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

class InventoryObj:
    def __init__(self):
        self.inventory_list = []
        self.warehouse_id = None
        self.product_id = None
        self.price = 0

    def add_item(self, item):
        self.inventory_list.append(item)
        self.warehouse_id = item.id_almacen
        self.product_id = item.id_producto
        if item.precio > self.price:
            self.price = item.precio


class Inventory(InventoryModel):

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
            'cantidad': self.cantidad,
            'precio': self.precio,
            'distancia': self.distancia
        }

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def reduce_inventory(self, quantity):
        self.cantidad -= quantity
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El inventario se ha reducido exitosamente'}]
        return False, resp

def get_inventory_quantity(id_inventario):
    inventory_inputs = s.query(func.sum(InventoryIn.cantidad_entrada)).filter(InventoryIn.id_inventario == id_inventario)
    inventory_outputs = s.query(func.sum(InventoryOut.cantidad_salida)).filter(InventoryOut.id_inventario == id_inventario)
    '''Doble for para desempaquetar el tuple dentro de lista, resultado de query '''
    for inventory_input, in inventory_inputs:
        for inventory_output, in inventory_outputs:
            print(inventory_input - inventory_output)
    return inventory_inputs, inventory_outputs


def get_inventory_matrix(basket, location):
    whs = get_warehouse_by_location(location)
    product_filter = [Inventory.id_producto == item.id_producto for item in basket]
    # TODO: Implementar respuesta de error si whs es vacio
    if not whs:
        return True, 'error'
    wh_filter = [Inventory.id_almacen == wh.id_almacen for wh in whs]
    inventory = s.query(Inventory).filter(and_(or_(*product_filter), or_(*wh_filter), Inventory.cantidad > 0)).all()
    active_products = np.asarray([item.id_producto for item in basket])
    basket_item_qty = np.asarray([item.cantidad for item in basket])
    wh_list = np.asarray([item.id_almacen for item in whs])
    wh_distance = np.asarray([item.distancia for item in whs])
    matrix = np.zeros((active_products.size, wh_list.size))
    inventory_vector = []
    price_matrix = np.zeros((active_products.size, wh_list.size))
    total_qty = np.zeros((active_products.size, wh_list.size))
    price_matrix[:] = float('infinity')

    for item in inventory:
        pr_index = np.where(active_products == item.id_producto)[0][0]
        wh_index = np.where(wh_list == item.id_almacen)[0][0]
        total_qty[pr_index, wh_index] += item.cantidad
        if matrix[pr_index, wh_index] == 0:
            inv_obj = InventoryObj()
            inventory_vector.append(inv_obj)
            matrix[pr_index, wh_index] = 1
        else:
            inv_obj = find_inventory_obj(inventory_vector, item.id_producto, item.id_almacen)
        inv_obj.add_item(item)
        price_matrix[pr_index, wh_index] = inv_obj.price * basket_item_qty[pr_index]

    below_ordered_qty = np.less(total_qty, basket_item_qty[:, np.newaxis])
    matrix *= 1 - below_ordered_qty

    pr_quantity = np.sum(matrix, axis=0)
    wh_discarded = np.where(pr_quantity == 0)[0]
    wh_quantity = np.sum(matrix, axis=1)
    pr_not_found = np.where(wh_quantity == 0)[0]

    matrix = np.delete(matrix, wh_discarded, axis=1)
    wh_list = np.delete(wh_list, wh_discarded, axis=0)
    wh_distance = np.delete(wh_distance, wh_discarded, axis=0)
    matrix = np.delete(matrix, pr_not_found, axis=0)
    active_products = np.delete(active_products, pr_not_found, axis=0)
    price_matrix = np.delete(price_matrix, wh_discarded, axis=1)
    price_matrix = np.delete(price_matrix, pr_not_found, axis=0)

    if np.sum(np.sum(matrix, axis=1), axis=0) == 0:
        resp = [404, {'message': 'No se encontraron resultados',
                      'action': 'Realice una nueva consulta'}]
        error = True
    else:
        resp = [201, {'message': 'El inventario se ha creado exitosamente'}]
        error = False
    return error, resp, active_products, pr_not_found, wh_list, inventory_vector, matrix, price_matrix, wh_distance


def find_inventory_obj(item_list, pr_id, wh_id):
    for item in item_list:
        if item.product_id == pr_id and item.warehouse_id == wh_id:
            return item


def process_inventory_matrix(basket, parameters, location):
    error, resp, active_products, pr_not_found, wh_list, inventory_matrix, initial_matrix, price_matrix, distance = \
        get_inventory_matrix(basket, location)

    if error:
        return True, resp

    min_price = np.min(price_matrix, axis=1)

    p_weight = 0.25
    d_weight = 0.25

    if parameters['closer'] is True:
        p_weight = 0.1
        d_weight = 0.4

    p_index = (min_price[:, np.newaxis] / price_matrix) * p_weight
    d_index = (np.min(distance) / distance) * d_weight
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
        ap = ap - matrix[:, index]
        matrix *= (1 - matrix[:, index][:, np.newaxis])
        if int(np.sum(ap)) == 0:
            complete = True

    final_matrix = (p_index + d_index + q_index) * selected_matrix
    max_index = np.argmax(final_matrix, axis=1)

    selected_inv_matrix = []
    for i in range(len(active_products)):
        selected_inv_matrix.append(find_inventory_obj(inventory_matrix, active_products[i], wh_list[max_index[i]]))
    return False, selected_inv_matrix

class InventoryIn(InventoryInModel):

    def __init__(self, id_inventario, id_miembro_almacen, cantidad_entrada, fecha_vencimiento):
        self.id_inventario = id_inventario
        self.id_miembro_almacen = id_miembro_almacen
        self.cantidad_entrada = cantidad_entrada
        self.fecha_entrada = datetime.datetime.now()
        self.fecha_vencimiento = fecha_vencimiento

    def add_inventory_in(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


class InventoryOut(InventoryOutModel):

    def __init__(self, id_inventario, id_miembro_almacen, cantidad_salida, motivo_salida):
        self.id_inventario = id_inventario
        self.id_miembro_almacen = id_miembro_almacen
        self.cantidad_salida = cantidad_salida
        self.motivo_salida = motivo_salida
        self.fecha_salida = datetime.datetime.now()

    def add_inventory_out(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


class unaccent(ReturnTypeFromArgs):
    pass


class Product(ProductModel):

    def __init__(self, category, manufacturer, name, barcode, meas_unit,  sku):
        self.id_categoria = category
        self.id_fabricante = manufacturer
        self.nombre_producto = name
        self.unidad_medida = meas_unit
        self.upc = barcode
        self.sku = sku

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
    from difflib import SequenceMatcher
    print('Original list: ', keywords)
    keywords = unidecode(keywords).lower()
    keywords = re.sub(r'\b(el|la|los|las|lo|un|uno|una|unos|unas|de|del|al)\b\s+',"", keywords)
    keyword_list = re.split("[^a-zA-Z0-9á-ú']+", keywords)

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

    print('Processed list: ', keyword_list)

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

    kw_filter = [unaccent(Product.nombre_producto).ilike("%" + kw + "%") for kw in keyword_list]
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


def get_product(item_id):
    if not item_id or '':
        raise InvalidArgument('El campo item_id no puede estar vacio')
    item = s.query(Product).filter(
        Product.id_producto == item_id).first()
    return item


if __name__ == '__main__':
    pass