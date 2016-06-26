from datetime import datetime

from sqlalchemy.orm import relationship
import sqlalchemy.exc

from dbmodel.user.usermodel import SubscriptionGroup, User, Relationship
from dbmodel.order.ordermodel import SubscriptionOrder, Item, UserListOrder
from dbmodel.warehouse.warehousemodel import WarehouseMemberHistory, Warehouse, WarehouseMember
from dbmodel.inventory.inventorymodel import Inventory, Product, Promo
from dbmodel.list.listmodel import UserList, WarehouseList


'''External relationship initialize'''
SubscriptionGroup.transaccion_suscripcion = relationship(
    "SubscriptionTransaction", foreign_keys=[SubscriptionGroup.id_transaccion_suscripcion])

SubscriptionOrder.usuario = relationship(
    "User", foreign_keys=[SubscriptionOrder.id_usuario])

SubscriptionOrder.plan = relationship(
    "SubscriptionPlan", foreign_keys=[SubscriptionOrder.id_plan])

WarehouseMemberHistory.estado_solicitud = relationship(
    "RequestStatus", foreign_keys=[WarehouseMemberHistory.id_estado_solicitud])

Item.inventario = relationship(
    'Inventory', foreign_keys=[Item.id_inventario])

UserListOrder.lista_usuario = relationship(
    'UserList', foreign_keys=[UserListOrder.id_lista_usuario])

WarehouseList.miembro_almacen = relationship(
    'Member', foreign_keys=[WarehouseList.id_miembro_almacen])

Inventory.miembro_almacen = relationship(
    'Member', foreign_keys=[Inventory.id_miembro_almacen])

Promo.miembro_almacen = relationship(
    'Member', foreign_keys=[Promo.id_miembro_almacen])
'''End External relationship initialize'''
