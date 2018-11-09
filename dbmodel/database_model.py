from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, String, Integer, Boolean, ForeignKey, UniqueConstraint, Float, Date, Time

import datetime

from functools import partial
partial(Column, nullable=False)

from dbmodel.dbconfig import Base
from dbmodel.res.UUID import GUID

Base.metadata.schema = 'usuario'


class RelationshipModel(Base):
    __tablename__ = 'relacion'

    id_relacion = Column(Integer, primary_key=True)
    id_usuario = Column(GUID, ForeignKey('usuario.id_usuario'), nullable=False)
    id_usuario_amigo = Column(GUID, ForeignKey('usuario.id_usuario'), nullable=False)

    __table_args__ = (UniqueConstraint('id_usuario', 'id_usuario_amigo', name='relacion_unica'),)


class RelationshipStatusModel(Base):
    __tablename__ = 'estado_relacion'

    id_estado_relacion = Column(Integer, primary_key=True)
    id_relacion = Column(Integer, ForeignKey('relacion.id_relacion'), nullable=False)
    id_estado_solicitud = Column(Integer, ForeignKey('estado_solicitud.id_estado_solicitud'), nullable=False)
    creado = Column(DateTime(timezone=True))


class MembershipModel(Base):
    __tablename__ = 'miembro'

    """Definición de campos en base de datos"""

    id_miembro = Column(Integer, primary_key=True)
    id_usuario = Column(GUID, ForeignKey('usuario.id_usuario'), nullable=False)
    id_grupo = Column(Integer, ForeignKey('grupo.id_grupo'), nullable=False)
    id_rol_grupo = Column(Integer, ForeignKey('rol_grupo.id_rol_grupo'), nullable=False)
    """
    la variable historia almacena los resultados de la tabla historia_miembro asociados
    a esta membresia usando una clausula JOIN. Los resultados se ordenan con la columna
    'creado' de manera descendiente. Se especifica un backref a tabla 'miembro'. Esto
    permite acceder a 'miembro' desde historia_miembro sin realizar consulta.
    """

    __table_args__ = (UniqueConstraint('id_usuario', 'id_grupo', name='miembro_unica'),)



class MembershipHistoryModel(Base):
    __tablename__ = 'historia_miembro'

    id_historia_miembro = Column(Integer, primary_key=True)
    id_miembro = Column(Integer, ForeignKey('miembro.id_miembro'), nullable=False)
    id_estado_solicitud = Column(Integer, ForeignKey('estado_solicitud.id_estado_solicitud'), nullable=False)
    id_actualizado_por = Column(Integer, ForeignKey('miembro.id_miembro'), nullable=False)
    creado = Column(DateTime(timezone=True), nullable=False)


class GroupModel(Base):
    __tablename__ = 'grupo'

    id_grupo = Column(Integer, primary_key=True)
    id_tipo_grupo = Column(Integer, ForeignKey('tipo_grupo.id_tipo_grupo'), nullable=False)
    nombre_grupo = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    creado = Column(DateTime(timezone=True), nullable=False)

class GroupTypeModel(Base):
    __tablename__ = 'tipo_grupo'

    id_tipo_grupo = Column(Integer, primary_key=True)
    tipo_grupo = Column(String, nullable=False)


class GroupRoleModel(Base):
    __tablename__ = 'rol_grupo'

    id_rol_grupo = Column(Integer, primary_key=True)
    rol_grupo = Column(String, nullable=False)
'''Membership'''

'''Common'''


class RequestStatus(Base):
    __tablename__ = 'estado_solicitud'

    id_estado_solicitud = Column(Integer, primary_key=True)
    estado_solicitud = Column(String, nullable=False)
'''Common'''

'''User'''


class AuthenticationType(Base):
    __tablename__ = 'tipo_autenticacion'

    id_tipo_autenticacion = Column(Integer, primary_key=True)
    tipo_autenticacion = Column(String, nullable=False)


class UserModel(Base):
    __tablename__ = 'usuario'

    id_usuario = Column(GUID, primary_key=True, autoincrement=False)
    _id_tipo_autenticacion = Column(Integer, ForeignKey('tipo_autenticacion.id_tipo_autenticacion'), nullable=False)
    _nombre_completo = Column(String, nullable=False)
    _correo_electronico = Column(String, unique=True, index=True, nullable=False)
    _numero_movil = Column(String, unique=True, index=True, nullable=False)
    _nombre_usuario = Column(String, unique=True, index=True, nullable=False)
    contrasena_hash = Column(String, nullable=True)
    contrasena_salt = Column(String, nullable=True)
    verificado = Column(Boolean, default=False, nullable=False)
    modificado = Column(DateTime(timezone=True), nullable=False)


class UserImageModel(Base):
    # __table_args__ = {'schema': 'usuario'}
    __tablename__ = 'imagen_usuario'

    id_imagen_usuario = Column(Integer, primary_key=True)
    _id_usuario = Column(GUID, ForeignKey('usuario.id_usuario'), nullable=False)
    descripcion = Column(String, nullable=True)
    _url = Column(String, nullable=False)


class UserLocationModel(Base):
    __tablename__ = 'direccion_usuario'

    id_direccion = Column(Integer, primary_key=True)
    _id_usuario = Column(GUID, ForeignKey('usuario.id_usuario'), index=True, nullable=False)
    _id_ciudad = Column(Integer, ForeignKey('comun.ciudad.id_ciudad'), nullable=False)
    _nombre_direccion = Column(String, nullable=True)
    coordenadas = Column(Geometry(geometry_type='POINT'), nullable=False)
    _direccion = Column(String, nullable=False)
    referencia = Column(String, nullable=True)
    _fecha_registro = Column(DateTime(timezone=True), nullable=False)
    _favorito = Column(Boolean, nullable=False)


class SubscriptionGroupModel(Base):
    __tablename__ = 'grupo_suscripcion'

    id_grupo_suscripcion = Column(Integer, primary_key=True)
    id_plan_suscripcion = Column(Integer, ForeignKey('plan_suscripcion.id_plan'), nullable=False)
    id_estado_suscripcion = Column(Integer, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    renovar = Column(Boolean, nullable=False)


class SubscriptionMemberModel(Base):
    __tablename__ = 'miembro_suscripcion'

    id_miembro_suscripcion = Column(Integer, primary_key=True)
    id_usuario = Column(GUID, ForeignKey('usuario.id_usuario'), nullable=False)
    id_grupo_suscripcion = Column(Integer, ForeignKey('grupo_suscripcion.id_grupo_suscripcion'), nullable=False)
    titular = Column(Boolean, default=False, nullable=False)

    __table_args__ = (UniqueConstraint('id_usuario', 'id_grupo_suscripcion', name='miembro_suscripcion_unico'),)


class SubscriptionMemberHistoryModel(Base):
    __tablename__ = 'historia_miembro_suscripcion'

    id_historia_miembro_suscripcion = Column(Integer, primary_key=True)
    id_miembro_suscripcion = Column(Integer, ForeignKey('miembro_suscripcion.id_miembro_suscripcion'), nullable=False)
    id_estado_miembro_suscripcion = Column(Integer, nullable=False)
    id_actualizado_por = Column(GUID, ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), nullable=False)


class MembershipSubscriptionStatus(Base):
    __tablename__ = 'estado_miembro_suscripcion'

    id_estado_miembro_suscripcion = Column(Integer, primary_key=True)
    estado_miembro_suscripcion = Column(String, nullable=False)


class SubscriptionPlanModel(Base):
    __tablename__ = 'plan_suscripcion'

    id_plan = Column(Integer, primary_key=True)
    nombre_plan = Column(String, nullable=False)
    cantidad_beneficiarios = Column(Integer, nullable=False)
    limite_servicios = Column(Integer, nullable=False)
    moneda = Column(String, nullable=False)
    precio_plan = Column(Integer, nullable=False)
    duracion_plan = Column(Integer, nullable=False)


class Credit(Base):
    __tablename__ = 'credito'

    id_credito = Column(Integer, primary_key=True)
    id_usuario = Column(GUID, ForeignKey('usuario.id_usuario'), nullable=False)
    id_usuario_origen = Column(GUID, ForeignKey('usuario.id_usuario'), nullable=False)
    id_origen_credito = Column(Integer, ForeignKey('origen_credito.id_origen_credito'), nullable=False)
    valor = Column(Float, nullable=False)
    valido_desde = Column(DateTime(timezone=True), nullable=False)
    valido_hasta = Column(DateTime(timezone=True), nullable=False)

class CreditOrigin(Base):
    __tablename__ = 'origen_credito'

    id_origen_credito = Column(Integer, primary_key=True)
    origen_credito = Column(String, nullable=False)


Base.metadata.schema = 'comun'

class CountryModel(Base):
    __tablename__ = 'pais'

    id_pais = Column(Integer, primary_key=True)
    locale = Column(String, nullable=False)
    id_continente = Column(Integer, ForeignKey('continente.id_continente'), nullable=False)
    codigo_pais_iso = Column(String, nullable=False)
    nombre_pais = Column(String, nullable=False)


class ContinentModel(Base):
    __tablename__ = 'continente'

    id_continente = Column(Integer, primary_key=True)
    codigo_continente = Column(String, nullable=False)
    nombre_continente = Column(String, nullable=False)
    locale = Column(String, nullable=False)


class CityModel(Base):
    __tablename__ = 'ciudad'

    id_ciudad = Column(Integer, primary_key=True)
    id_pais = Column(Integer, ForeignKey('pais.id_pais'), nullable=False)
    ciudad = Column(String, nullable=False)
    codigo_ciudad_iso = Column(String, nullable=False)

Base.metadata.schema = 'orden'


class SubscriptionTransactionModel(Base):
    __tablename__ = 'transaccion_suscripcion'

    id_transaccion_suscripcion = Column(Integer, primary_key=True)
    id_suscripcion_orden = Column(
        Integer, ForeignKey('suscripcion_orden.id_suscripcion_orden'), nullable=False)
    id_metodo_pago = Column(Integer, nullable=False)
    id_estado_transaccion = Column(Integer,  nullable=False)
    moneda = Column(String,  nullable=False)
    valor_transaccion = Column(Integer, nullable=False)
    referencia_pago = Column(String)
    fecha_transaccion = Column(DateTime(timezone=True), nullable=False)


class SubscriptionOrderModel(Base):
    __tablename__ = 'suscripcion_orden'

    id_suscripcion_orden = Column(Integer, primary_key=True)
    id_grupo_suscripcion = Column(Integer, ForeignKey('usuario.grupo_suscripcion.id_grupo_suscripcion'), nullable=False)
    fecha_orden = Column(DateTime(timezone=True), nullable=False)


class OrderItemModel(Base):
    __tablename__ = 'item_orden'

    id_item_orden = Column(Integer, primary_key=True)
    id_orden = Column(
        Integer, ForeignKey('orden.id_orden'), nullable=False)
    id_inventario = Column(Integer, ForeignKey('inventario.inventario.id_inventario'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Integer, nullable=False)


class WarehouseListOrder(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'lista_almacen_orden'

    id_lista_almacen_orden = Column(Integer, primary_key=True)
    id_item_orden = Column(
        Integer, ForeignKey('item_orden.id_item_orden'))
    id_lista_almacen = Column(Integer, ForeignKey('lista.lista_almacen.id_lista_almacen'))
    cantidad = Column(Integer)


class UserListOrder(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'lista_usuario_orden'

    id_lista_usuario_orden = Column(Integer, primary_key=True)
    id_item_orden = Column(
        Integer, ForeignKey('item_orden.id_item_orden'))
    id_lista_usuario = Column(Integer, ForeignKey('lista.lista_usuario.id_lista_usuario'))
    cantidad = Column(Integer)


class PromoOrder(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'oferta_orden'

    id_oferta_orden = Column(Integer, primary_key=True)
    id_item_orden = Column(
        Integer, ForeignKey('item_orden.id_item_orden'))
    id_oferta_especial = Column(Integer, ForeignKey('inventario.oferta_especial.id_oferta_especial'))
    cantidad = Column(Integer)


class OrderModel(Base):
    __tablename__ = 'orden'

    id_orden = Column(Integer, primary_key=True)
    id_usuario = Column(
        GUID, ForeignKey('usuario.usuario.id_usuario'))
    fecha_orden = Column(DateTime(timezone=True))


class ProductTransactionModel(Base):
    __tablename__ = 'transaccion_productos'

    id_transaccion_productos = Column(Integer, primary_key=True)
    id_orden = Column(
        Integer, ForeignKey('orden.id_orden'))
    id_metodo_pago = Column(Integer, nullable=False)
    id_estado_transaccion = Column(Integer, nullable=False)
    valor_transaccion = Column(Integer)
    referencia_pago = Column(String)
    fecha_transaccion = Column(DateTime(timezone=True))


# class TransactionStatus(Base):
#     # __table_args__ = {'schema': 'orden'}
#     __tablename__ = 'estado_transaccion'
#
#     id_estado_transaccion = Column(Integer, primary_key=True)
#     estado_transaccion = Column(String)


class PaymentMethod(Base):
    # __table_args__ = {'schema': 'orden'}
    __tablename__ = 'metodo_pago'

    id_metodo_pago = Column(Integer, primary_key=True)
    metodo_pago = Column(String)


Base.metadata.schema = 'inventario'


class ProductCategoryModel(Base):
    __tablename__ = 'categoria_producto'

    id_categoria = Column(Integer, primary_key=True)
    parent = Column(
        Integer, ForeignKey('categoria_producto.id_categoria'), nullable=True)
    categoria = Column(String, nullable=False, unique=True)


class ProductSpecification(Base):
    __tablename__ = 'especificacion_producto'

    id_especificacion_producto = Column(Integer, primary_key=True)
    id_producto = Column(
        Integer, ForeignKey('producto.id_producto'), nullable=False)
    atributo = Column(String, nullable=False)
    valor = Column(String, nullable=False)


class ManufacturerModel(Base):
    __tablename__ = 'fabricante'

    id_fabricante = Column(Integer, primary_key=True)
    nombre_fabricante = Column(String, unique=True, nullable=False, index=True)
    descripcion = Column(String, nullable=True)


class ManufacturerImage(Base):
    __tablename__ = 'imagen_fabricante'

    id_imagen_fabricante = Column(Integer, primary_key=True)
    id_fabricante = Column(
        Integer, ForeignKey('fabricante.id_fabricante'), nullable=False)
    descripcion = Column(String, nullable=False)
    archivo = Column(String, nullable=False)


class ProductImage(Base):
    __tablename__ = 'imagen_producto'

    id_imagen_producto = Column(Integer, primary_key=True)
    id_producto = Column(
        Integer, ForeignKey('producto.id_producto'), nullable=False)
    descripcion = Column(String, nullable=False)
    archivo = Column(String, nullable=False)


class InventoryModel(Base):
    __tablename__ = 'inventario'

    id_inventario = Column(Integer, primary_key=True)
    id_producto = Column(
        Integer, ForeignKey('producto.id_producto'), nullable=False, index=True)
    id_almacen = Column(
        GUID, ForeignKey('almacen.almacen.id_almacen'), nullable=False)
    precio = Column(Float, nullable=False)
    distancia = float('infinity')

    __table_args__ = (UniqueConstraint('id_producto', 'id_almacen', name='producto_inventario_almacen'),)

class InventoryInputModel(Base):
    __tablename__ = 'inventario_entrada'

    id_entrada_inventario = Column(Integer, primary_key=True)
    id_inventario = Column(
        Integer, ForeignKey('inventario.id_inventario'), nullable=False, index=True)
    id_miembro_almacen = Column(
        Integer, ForeignKey('almacen.miembro_almacen.id_miembro_almacen'), nullable=False)
    cantidad_entrada = Column(Integer, nullable=False)
    fecha_entrada = Column(DateTime, nullable=False)
    fecha_vencimiento = Column(DateTime, nullable=False)


class InventoryOutputModel(Base):
    __tablename__ = 'inventario_salida'

    id_salida_inventario = Column(Integer, primary_key=True)
    id_inventario = Column(
        Integer, ForeignKey('inventario.id_inventario'), nullable=False, index=True)
    id_miembro_almacen = Column(
        Integer, ForeignKey('almacen.miembro_almacen.id_miembro_almacen'), nullable=False)
    cantidad_salida = Column(Integer, nullable=False)
    motivo_salida = Column(Integer, nullable=False)
    fecha_salida = Column(DateTime, nullable=False)


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


class ProductModel(Base):
    __tablename__ = 'producto'

    id_producto = Column(Integer, primary_key=True)
    id_categoria = Column(
        Integer, ForeignKey('categoria_producto.id_categoria'), nullable=False, index=True)
    id_fabricante = Column(
        Integer, ForeignKey('fabricante.id_fabricante'), nullable=True, index=True)
    nombre_producto = Column(String, index=True, nullable=False)
    unidad_medida = Column(Integer, nullable=False)
    upc = Column(String, index=True, unique=True, nullable=True)
    sku = Column(String, unique=True, nullable=True)
    taxable = Column(Boolean, nullable=True)



class PromoType(Base):
    __tablename__ = 'tipo_oferta'

    id_tipo_oferta = Column(Integer, primary_key=True)
    nombre_oferta = Column(String, nullable=False)
    descuento = Column(Float, nullable=False)


Base.metadata.schema = 'canasta'


class BasketWarehouseList(Base):
    __tablename__ = 'lista_almacen_canasta'

    id_lista_almacen_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        GUID, ForeignKey('usuario.usuario.id_usuario'))
    id_lista_almacen = Column(
        Integer, ForeignKey('lista.lista_almacen.id_lista_almacen'))
    cantidad = Column(Integer)
    fecha_creacion = Column(DateTime(timezone=True))


class BasketUserList(Base):
    __tablename__ = 'lista_usuario_canasta'

    id_lista_usuario_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        GUID, ForeignKey('usuario.usuario.id_usuario'))
    id_lista_usuario = Column(
        Integer, ForeignKey('lista.lista_usuario.id_lista_usuario'))
    cantidad = Column(Integer)
    fecha_creacion = Column(DateTime(timezone=True))


class BasketPromo(Base):
    __tablename__ = 'oferta_canasta'

    id_oferta_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        GUID, ForeignKey('usuario.usuario.id_usuario'))
    id_oferta_especial = Column(
        Integer, ForeignKey('inventario.oferta_especial.id_oferta_especial'))
    cantidad = Column(Integer)
    fecha_creacion = Column(DateTime(timezone=True))


class BasketProductModel(Base):
    __tablename__ = 'producto_canasta'

    id_producto_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        GUID, ForeignKey('usuario.usuario.id_usuario'))
    id_producto = Column(
        Integer, ForeignKey('inventario.producto.id_producto'))
    cantidad = Column(Integer, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint('id_usuario', 'id_producto', name='canasta_usuario_producto'),)

class BasketWarehouseProductModel(Base):
    __tablename__ = 'producto_almacen_canasta'

    id_producto_almacen_canasta = Column(Integer, primary_key=True)
    id_usuario = Column(
        GUID, ForeignKey('usuario.usuario.id_usuario'))
    id_inventario = Column(
        Integer, ForeignKey('inventario.inventario.id_inventario'))
    cantidad = Column(Integer, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint('id_usuario', 'id_inventario', name='canasta_usuario_producto_almacen'),)


Base.metadata.schema = 'lista'

class ListCategory(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'categoria_lista'

    id_categoria_lista = Column(Integer, primary_key=True)
    parent = Column(
        Integer, ForeignKey('categoria_lista.id_categoria_lista'))
    categoria_lista = Column(String)


class WarehouseListItem(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'item_lista_almacen'

    id_item_lista_almacen = Column(Integer, primary_key=True)
    id_lista_almacen = Column(
        Integer, ForeignKey('lista_almacen.id_lista_almacen'))
    id_inventario = Column(
        Integer, ForeignKey('inventario.inventario.id_inventario'))
    cantidad = Column(Integer)


class UserListItem(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'item_lista_usuario'

    id_item_lista_usuario = Column(Integer, primary_key=True)
    id_lista_usuario = Column(
        Integer, ForeignKey('lista_almacen.id_lista_almacen'))
    id_producto = Column(
        Integer, ForeignKey('inventario.producto.id_producto'))
    cantidad = Column(Integer)


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


class UserList(Base):
    # __table_args__ = {'schema': 'lista'}
    __tablename__ = 'lista_usuario'

    id_lista_usuario = Column(Integer, primary_key=True)
    id_usuario = Column(
        GUID, ForeignKey('usuario.usuario.id_usuario'))
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


Base.metadata.schema = 'servicio'


class ServiceCancellation(Base):
    __tablename__ = 'cancelacion_servicio'

    id_cancelacion_servicio = Column(Integer, primary_key=True)
    id_servicio = Column(
        Integer, ForeignKey('servicio.id_servicio'))
    id_credito = Column(
        Integer, ForeignKey('usuario.credito.id_credito'))
    id_motivo_cancelacion = Column(
        Integer, ForeignKey('motivo_cancelacion.id_motivo_cancelacion'))
    fecha_cancelacion = Column(DateTime(timezone=True))


class ServiceStatus(Base):
    __tablename__ = 'estado_servicio'

    id_estado_servicio = Column(Integer, primary_key=True)
    estado_servicio = Column(String)


class ReasonCancellation(Base):
    __tablename__ = 'motivo_cancelacion'

    id_motivo_cancelacion = Column(Integer, primary_key=True)
    motivo_cancelacion = Column(String)


class ServiceProvider(Base):
    __tablename__ = 'prestador_servicio'

    id_prestador_servicio = Column(Integer, primary_key=True)
    id_usuario = Column(GUID, ForeignKey('usuario.usuario.id_usuario'), nullable=False)
    id_rol = Column(Integer, nullable=False)
    id_tipo_documento = Column(Integer, nullable=False)
    documento_identidad = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    direccion_residencia = Column(String, nullable=False)
    telefono_residencia = Column(String, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)
    ultima_ubicacion = Column(Geometry(geometry_type='POINT'), nullable=True)


class ServiceProviderSchedule(Base):
    __tablename__ = 'programacion_prestador_servicio'

    id_programacion_prestador_servicio = Column(Integer, primary_key=True)
    id_prestador_servicio = Column(Integer, ForeignKey('prestador_servicio.id_prestador_servicio'), nullable=False)
    id_almacen = Column(GUID, ForeignKey('almacen.almacen.id_almacen'), nullable=False)
    inicio = Column(DateTime(timezone=True), nullable=False)
    fin = Column(DateTime(timezone=True), nullable=False)


class Service(Base):
    __tablename__ = 'servicio'

    id_servicio = Column(Integer, primary_key=True)
    id_prestador_servicio = Column(Integer, ForeignKey('prestador_servicio.id_prestador_servicio'),  nullable=False)
    id_direccion = Column(Integer, ForeignKey('usuario.direccion_usuario.id_direccion'),  nullable=False)
    id_orden = Column(Integer, ForeignKey('orden.orden.id_orden'),  nullable=False)
    id_estado_servicio = Column(Integer,  nullable=False)
    inicio = Column(DateTime(timezone=True),  nullable=False)
    fin = Column(DateTime(timezone=True),  nullable=True)


class Vehicle(Base):
    __tablename__ = 'vehiculo'

    id_vehiculo = Column(Integer, primary_key=True)
    id_prestador_servicio = Column(Integer, ForeignKey('prestador_servicio.id_prestador_servicio'), nullable=False)
    id_tipo_vehiculo = Column(Integer, nullable=False)
    matricula = Column(String, nullable=True)
    descripcion = Column(String, nullable=False)


Base.metadata.schema = 'almacen'


class WarehouseModel(Base):
    __tablename__ = 'almacen'

    id_almacen = Column(GUID, primary_key=True)
    _id_categoria_almacen = Column(Integer, ForeignKey('categoria_almacen.id_categoria_almacen'), nullable=False)
    _nombre = Column(String, nullable=False, unique=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)



class WarehouseLocationModel(Base):
    __tablename__ = 'ubicacion_almacen'

    _id_almacen = Column(GUID, ForeignKey('almacen.id_almacen'), nullable=False, primary_key=True)
    _id_ciudad = Column(Integer, ForeignKey('comun.ciudad.id_ciudad'), nullable=False)
    coordenadas = Column(Geometry(geometry_type='POINT'), nullable=False)
    _direccion = Column(String, nullable=False)
    _contacto = Column(String, nullable=False)


class WarehouseCategoryModel(Base):
    __tablename__ = 'categoria_almacen'

    id_categoria_almacen = Column(Integer, primary_key=True)
    categoria_almacen = Column(String, nullable=False)

class WarehouseMemberModel(Base):
    __tablename__ = 'miembro_almacen'

    id_miembro_almacen = Column(Integer, primary_key=True)
    _id_usuario = Column(GUID, ForeignKey('usuario.usuario.id_usuario'), index=True, nullable=False)
    _id_almacen = Column(GUID, ForeignKey('almacen.id_almacen'), index=True, nullable=False)

    __table_args__ = (UniqueConstraint('_id_usuario', '_id_almacen', name='miembro_unico'),)


class WarehouseMemberStatusModel(Base):
    __tablename__ = 'estado_miembro_almacen'

    id_estado_miembro_almacen = Column(Integer, primary_key=True)
    _id_miembro_almacen = Column(Integer, ForeignKey('miembro_almacen.id_miembro_almacen'), nullable=False)
    _estado_solicitud = Column(Integer, nullable=False)
    _id_actualizado_por = Column(GUID, ForeignKey('usuario.usuario.id_usuario'), nullable=False)
    fecha_modificacion = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)

class WarehouseMemberRoleModel(Base):
    __tablename__ = 'rol_miembro_almacen'

    id_rol_miembro_almacen = Column(Integer, primary_key=True)
    _id_miembro_almacen = Column(Integer, ForeignKey('miembro_almacen.id_miembro_almacen'), nullable=False)
    _rol_miembro_almacen = Column(Integer, nullable=False)
    _id_actualizado_por = Column(GUID, ForeignKey('usuario.usuario.id_usuario'), nullable=False)
    fecha_modificacion = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)

class WarehouseOpeningHoursModel(Base):
    __tablename__ = 'horario_atencion'

    id_horario_atencion = Column(Integer, primary_key=True)
    _id_almacen = Column(GUID, ForeignKey('almacen.id_almacen'), nullable=False)
    _dia = Column(Integer, nullable=False)
    desde = Column(Time, default=datetime.time(8, 0), nullable=False)
    hasta = Column(Time, default=datetime.time(22, 0), nullable=False)

    __table_args__ = (UniqueConstraint('_id_almacen', '_dia', name='unico_horario'),)