import datetime
from sqlalchemy import and_
from dbmodel.dbconfig import s
from dbmodel.database_model import BasketProductModel




class BasketProduct(BasketProductModel):

    def __init__(self, user, product, quantity):
        self.id_usuario = user
        self.id_producto = product
        self.cantidad = quantity
        self.fecha_creacion = datetime.datetime.now()

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_producto_canasta,
            'usuario': self.usuario._nombre_completo,
            'producto': self.producto.nombre_producto,
            'cantidad': self.cantidad,
            'fecha': self.fecha_creacion.strftime("%Y-%m-%d")
        }

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def update_item(self, quantity):
        self.cantidad = quantity
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def delete_item(self):
        s.delete(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

def empty_basket(basket):
    for item in basket:
        s.delete(item)
    s.commit()
    return {'success': True}, 200, {'ContentType': 'application/json'}

def empty_basket_by_user_id(user_id):
    basket = get_basket(user_id)
    for item in basket:
        s.delete(item)
    s.commit()
    return {'success': True}, 200, {'ContentType': 'application/json'}

def get_basket(user):
    basket = s.query(BasketProduct).filter(
        BasketProduct.id_usuario == user).all()
    return basket

def get_basket_item(user, product):
    item = s.query(BasketProduct).filter(
        and_(BasketProduct.id_usuario == user,
             BasketProduct.id_producto == product)
    ).first()
    return item

def get_item_basket_by_id(id_item):
    item = s.query(BasketProduct).filter(BasketProduct.id_producto_canasta == id_item).first()
    return item