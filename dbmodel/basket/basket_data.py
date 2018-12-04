import datetime
import numpy as np
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import relationship

from dbmodel.dbconfig import s
from dbmodel.database_model import DynamicBasketModel, StandardBasketModel
from dbmodel.inventory.inventory_data import Stock, StockInput, StockOutput, Product
from dbmodel.warehouse.warehouse_data import get_warehouse_by_location


def get_dynamic_basket(user, parameters, location):
    whs = get_warehouse_by_location(location)
    basket = get_generic_basket(user)
    product_filter = [Stock.product_id == item.product_id for item in basket]
    # TODO: Implementar respuesta de error si whs es vacio
    wh_filter = [Stock.store_id == wh.store_id for wh in whs]
    b_query = s.query(StockInput.stock_item_id, func.sum(StockInput.stock_input_quantity).label('input')).group_by(
        StockInput.stock_item_id).subquery()
    c_query = s.query(StockOutput.stock_item_id, func.sum(StockOutput.stock_output_quantity).label('output')).group_by(
        StockOutput.stock_item_id).subquery()
    raw_inventory_list = s.query(Stock, b_query.c.input, c_query.c.output).outerjoin(
        (b_query, b_query.c.stock_item_id == Stock.stock_item_id)).outerjoin(
        (c_query, c_query.c.stock_item_id == Stock.stock_item_id)).filter(
        and_(or_(*product_filter), or_(*wh_filter)))
    inventory_list = []
    for inventory in raw_inventory_list:
        if inventory[1] is None:
            inventory[0].stock_input_quantity = 0
        else:
            inventory[0].stock_input_quantity = inventory[1]
        if inventory[2] is None:
            inventory[0].stock_output_quantity = 0
        else:
            inventory[0].stock_output_quantity = inventory[2]
        inventory_list.append(inventory[0])
    active_products = np.asarray([item.product_id for item in basket])
    basket_item_qty = np.asarray([item.dynamic_basket_quantity for item in basket])
    wh_list = np.asarray([item.store_id for item in whs])
    wh_distance = np.asarray([item.distancia for item in whs])
    initial_matrix = np.zeros((active_products.size, wh_list.size))
    price_matrix = np.zeros((active_products.size, wh_list.size))
    total_qty = np.zeros((active_products.size, wh_list.size))
    price_matrix[:] = float('infinity')
    inventory_matrix = np.empty( (active_products.size, wh_list.size), dtype=object)

    for item in inventory_list:
        pr_index = np.where(active_products == item.product_id)[0][0]
        wh_index = np.where(wh_list == item.store_id)[0][0]
        total_qty[pr_index, wh_index] += (item.stock_input_quantity - item.stock_output_quantity)
        initial_matrix[pr_index, wh_index] = 1
        inventory_matrix[pr_index, wh_index] = item
        price_matrix[pr_index, wh_index] = item.stock_price * basket_item_qty[pr_index]

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
    inventory_selected = [StandardBasket(user, val.stock_item_id, int(qty), dinamico=True, inventory=val) for val, qty in zip(selected_inv_matrix, basket_item_qty)]
    return inventory_selected

class DynamicBasket(DynamicBasketModel):

    def __init__(self, user_id, product_id, dynamic_basket_quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.dynamic_basket_quantity = dynamic_basket_quantity
        self.dynamic_basket_date = datetime.datetime.now()

    def __repr__(self):
        return 'StandardBasket (p:' + str(self.product_id) + ' c:' + str(self.dynamic_basket_quantity) + ')'

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def update_item(self, quantity):
        self.dynamic_basket_quantity = quantity
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def delete_item(self):
        s.delete(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

class StandardBasket(StandardBasketModel):

    def __init__(self, user_id, inventory_id, standard_basket_quantity, dinamico=False, inventory=None):
        self.user_id = user_id
        self.stock_item_id = inventory_id
        self.standard_basket_quantity = standard_basket_quantity
        self.standard_basket_date = datetime.datetime.now()
        self.dinamico = dinamico
        self.inventory = inventory


    def __repr__(self):
        return 'StandardBasket (i:' + str(self.stock_item_id) + ' c:' + str(self.standard_basket_quantity) + ')'

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.standard_basket_id,
            'cantidad': self.standard_basket_quantity,
            'fecha': self.fecha_creacion.strftime("%Y-%m-%d")
        }

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def update_item(self, standard_basket_quantity):
        self.standard_basket_quantity += standard_basket_quantity
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def delete_item(self):
        s.delete(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

def get_generic_basket(user):
    generic_basket = s.query(DynamicBasket).filter(
        DynamicBasket.user_id == user).all()
    return generic_basket

def get_standard_basket(user):
    raw_basket = s.query(StandardBasket, Stock).filter(
        StandardBasket.user_id == user).join(Stock).all()
    basket = []
    for basket_item, inventory  in raw_basket:
        basket_item.inventory = inventory
        basket.append(basket_item)
    return basket

def get_basket(user, parameters, location):
    dynamic_basket = get_dynamic_basket(user, parameters, location)
    standard_basket = get_standard_basket(user)
    basket = dynamic_basket + standard_basket
    for basket_item in basket:
        for basket_temp in basket:
            if basket_temp == basket_item:
                pass
            else:
                if basket_item.user_id == basket_temp.user_id and basket_item.stock_item_id == basket_temp.stock_item_id:
                    basket_item.standard_basket_quantity += basket_temp.standard_basket_quantity
                    basket.remove(basket_temp)
    return basket

def empty_basket(user):
    standard_basket = get_standard_basket(user)
    for item in standard_basket:
        s.delete(item)
    generic_basket = get_generic_basket(user)
    for item in generic_basket:
        s.delete(item)
    s.commit()
    return {'success': True}, 200, {'ContentType': 'application/json'}

def empty_basket_by_user_id(basket):
    for item in basket:
        s.delete(item)
    s.commit()
    return {'success': True}, 200, {'ContentType': 'application/json'}

def get_basket_item(user, inventory):
    item = s.query(StandardBasket).filter(
        and_(StandardBasket.user_id == user,
             StandardBasket.stock_item_id == inventory)
    ).first()
    return item

def get_item_basket_by_id(id_item):
    item = s.query(DynamicBasket).filter(DynamicBasket.dynamic_basket_id == id_item).first()
    return item