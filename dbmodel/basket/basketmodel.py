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
        # wh_list = []
        # distance = []
        # product_list = []
        # active_products = []
        # not_found = []
        # item_list = []
        # min_price = []
        # for item in basket:
        #     error, inventory_result = Inventory().get_item_by_product_id(item.id_producto, whs)
        #     zone_inventory = []
        #     product_list.append(item.id_producto)
        #     if not error:
        #         for item1 in inventory_result:
        #             if item1.total_quantity >= item.cantidad:
        #                 zone_inventory.append(item1)
        #         if len(zone_inventory) > 0:
        #             for item1 in zone_inventory:
        #                 if item1.warehouse_id not in wh_list:
        #                     wh_list.append(item1.warehouse_id)
        #                     distance.append(item1.distance)
        #             item_list.append(zone_inventory)
        #             active_products.append(item.id_producto)
        #             min_price.append(float('infinity'))
        #     else:
        #         not_found.append(item.id_producto)
        # w, h = len(wh_list), len(active_products)
        # inventory_matrix = [[0 for x in range(w)] for y in range(h)]
        # initial_matrix = [[0 for x in range(w)] for y in range(h)]
        # price_matrix = [[float('infinity') for x in range(w)] for y in range(h)]
        #
        # for j in range(len(item_list)):
        #     for z in range(len(item_list[j])):
        #         for i in range(len(wh_list)):
        #             if wh_list[i] == item_list[j][z].warehouse_id:
        #                 initial_matrix[j][i] = 1
        #                 inventory_matrix[j][i] = item_list[j][z]
        #                 price_matrix[j][i] = item_list[j][z].price
        #
        # print(initial_matrix)
        #
        # min_price = np.min(price_matrix, axis=1)
        #
        # p_weight = 0.4
        # d_weight = 0.1
        #
        # if parameters['closer'] is True:
        #     p_weight = 0.1
        #     d_weight = 0.4
        #
        # p_index = (min_price[:, np.newaxis] / price_matrix) * p_weight
        # d_index = (np.min(distance) / distance) * d_weight
        #
        # quantity = np.sum(initial_matrix, axis=0)
        # max_quantity = max(quantity)
        #
        # repeated = np.zeros((1, np.asarray(active_products).size))
        # ap = np.ones((1, np.asarray(active_products).size))
        # a_wh = np.ones((1, np.asarray(wh_list).size))
        # matrix = np.asarray(initial_matrix)
        # selected_matrix = np.zeros((np.asarray(active_products).size, np.asarray(wh_list).size))
        #
        # complete = False
        # while not complete:
        #     q_index = ((quantity - repeated) / max_quantity) * 0.5
        #     best_indices = np.sum((d_index + q_index + p_index) * matrix, axis=0)
        #     index = np.argmax(best_indices, axis=0)
        #     a_wh[0, index] = 0
        #     selected_matrix[:, index] = matrix[:, index]
        #     repeated += np.sum(matrix[:, index] * matrix * a_wh, axis=1)
        #     ap = ap - matrix[:, index]
        #     matrix *= (1 - matrix[:, index][:, np.newaxis])
        #     if int(np.sum(ap)) == 0:
        #         complete = True
        # final_matrix = (p_index + d_index + q_index) * selected_matrix
        # max_index = np.argmax(final_matrix, axis=1)
        # for i in range(len(matrix)):
        #     basket[i].inventario = inventory_matrix[i][max_index[i]].inventory_list

        # wh_list = []
        # distance = []
        # product_list = []
        # active_products = []
        # not_found = []
        # item_list = []
        # min_price = []
        # for item in basket:
        #     error, inventory_result = Inventory().get_item_by_product_id(item.id_producto, whs)
        #     zone_inventory = []
        #     product_list.append(item.id_producto)
        #     if not error:
        #         for item1 in inventory_result:
        #             if item1.total_quantity >= item.cantidad:
        #                 zone_inventory.append(item1)
        #         if len(zone_inventory) > 0:
        #             for item1 in zone_inventory:
        #                 if item1.warehouse_id not in wh_list:
        #                     wh_list.append(item1.warehouse_id)
        #                     distance.append(item1.distance)
        #             item_list.append(zone_inventory)
        #             active_products.append(item.id_producto)
        #             min_price.append(float('infinity'))
        #     else:
        #         not_found.append(item.id_producto)
        # w, h = len(wh_list), len(active_products)
        # quantity = [0] * len(wh_list)
        # inventory_matrix = [[0 for x in range(w)] for y in range(h)]
        # matrix = [[0 for x in range(w)] for y in range(h)]
        # q_index = [[0 for x in range(w)] for y in range(h)]
        # d_index = [[0 for x in range(w)] for y in range(h)]
        # p_index = [[0 for x in range(w)] for y in range(h)]
        # price_matrix = [[float('infinity') for x in range(w)] for y in range(h)]
        # final_matrix = [[0 for x in range(w)] for y in range(h)]
        #
        # for j in range(len(item_list)):
        #     for z in range(len(item_list[j])):
        #         for i in range(len(wh_list)):
        #             if wh_list[i] == item_list[j][z].warehouse_id:
        #                 matrix[j][i] = 1
        #                 inventory_matrix[j][i] = item_list[j][z]
        #                 q_index[j][i] = 1
        #                 d_index[j][i] = 1
        #                 p_index[j][i] = 1
        #                 price_matrix[j][i] = item_list[j][z].price
        #                 if item_list[j][z].price < min_price[j]:
        #                     min_price[j] = item_list[j][z].price
        #                 quantity[i] += 1
        #
        # p_weight = 0.4
        # d_weight = 0.1
        #
        # if parameters['closer'] is True:
        #     p_weight = 0.1
        #     d_weight = 0.4
        #
        # for i in range(len(matrix)):
        #     for j in range(len(wh_list)):
        #         d_index[i][j] = (min(distance) / distance[j]) * d_weight
        #         p_index[i][j] = (min_price[i] / price_matrix[i][j]) * p_weight
        #
        # complete = False
        # selected_wh = []
        # repeated = [0] * len(wh_list)
        # visited = []
        # ap = list(active_products)
        #
        # while not complete:
        #
        #     best_indices = [0] * len(wh_list)
        #
        #     for i in range(len(matrix)):
        #         for j in range(len(wh_list)):
        #             if matrix[i][j] != 0:
        #                 q_index[i][j] = ((quantity[j] - repeated[j]) / max(quantity)) * 0.5
        #                 best_indices[j] += q_index[i][j] + d_index[i][j] + p_index[i][j]
        #
        #     max_indice = 0
        #
        #     for i in range(len(wh_list)):
        #         if i not in selected_wh:
        #             if best_indices[i] > max_indice:
        #                 max_indice = best_indices[i]
        #
        #     for i in range(len(wh_list)):
        #         if best_indices[i] == max_indice and i not in selected_wh:
        #             selected_wh.append(i)
        #
        #     for i in range(len(matrix)):
        #         for j in range(len(wh_list)):
        #             actual = i, j
        #             if j not in selected_wh:
        #                 if (matrix[i][selected_wh[-1]] == 1) and (matrix[i][j] == 1) and (actual not in visited):
        #                     visited.append(actual)
        #                     repeated[j] += 1
        #
        #     for j in range(len(selected_wh)):
        #         for i in range(len(matrix)):
        #             if matrix[i][selected_wh[j]] == 1 and active_products[i] in ap:
        #                 ap.remove(active_products[i])
        #
        #     if not ap:
        #         complete = True
        #
        # for i in range(len(matrix)):
        #     for j in range(len(wh_list)):
        #         if matrix[i][j] != 0:
        #             final_matrix[i][j] = q_index[i][j] + d_index[i][j] + p_index[i][j]
        # print(final_matrix)
        #
        # for i in range(len(matrix)):
        #     max_index = final_matrix[i].index(max(final_matrix[i]))
        #     print(max_index)
        #     basket[i].inventario = inventory_matrix[i][max_index].inventory_list
        #
        # print('Basket', basket)
        # print('Not found', not_found)
        # print('Active', active_products)
        # print('Warehouse', wh_list)
        # print('Distancia', distance)
        # print('Cantidad', quantity)
        # print('Matrix', matrix)
        # print('Matrix Precio', price_matrix)
        # print('Min Precio', min_price)
        # print('Quantity Indices', q_index)
        # print('Distance Indices', d_index)
        # print('Price Indices', p_index)
        # print('Final Matrix', final_matrix)
        # print('Best Indices', best_indices)
        # # print('Selected WH', selected_wh)
        # print('Repeated', repeated)
        # # print('Visited', visited)

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

