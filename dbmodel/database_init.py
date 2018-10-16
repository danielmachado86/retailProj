from sqlalchemy import event
from sqlalchemy.schema import DDL
from dbmodel.dbconfig import engine, s


from dbmodel.database_model import Base


def create_database():
    print('Creando base de datos...')
    event.listen(
        Base.metadata,
        'before_create',
        DDL('CREATE OR REPLACE FUNCTION usuario.update_created_column()'
            'RETURNS TRIGGER AS $$ BEGIN NEW.creado = now(); RETURN NEW;'
            'END; $$ language "plpgsql";')
    )

    event.listen(
        Base.metadata,
        'before_create',
        DDL('CREATE OR REPLACE FUNCTION usuario.update_modified_column()'
            'RETURNS TRIGGER AS $$ BEGIN NEW.modificado = now(); RETURN NEW;'
            'END; $$ language "plpgsql";')
    )

    Base.metadata.create_all()
    trigger_text = 'CREATE TRIGGER fecha_creado_relacion ' \
                   'BEFORE INSERT ON usuario.estado_relacion '\
                   'FOR EACH ROW EXECUTE PROCEDURE  '\
                   'usuario.update_created_column();'\
                   'CREATE TRIGGER fecha_creado_miembro '\
                   'BEFORE INSERT ON usuario.historia_miembro '\
                   'FOR EACH ROW EXECUTE PROCEDURE  '\
                   'usuario.update_created_column();'\
                   'CREATE TRIGGER fecha_modificado_usuario '\
                   'BEFORE INSERT OR UPDATE ON usuario.usuario '\
                   'FOR EACH ROW EXECUTE PROCEDURE '\
                   'usuario.update_modified_column();'

    engine.execute(trigger_text)
    print('Base de datos creada')

    engine.execute(
        "INSERT INTO almacen.categoria_almacen(id_categoria_almacen, categoria_almacen) VALUES (1, 'Mercado');"
        "INSERT INTO almacen.categoria_almacen(id_categoria_almacen, categoria_almacen) VALUES (2, 'Drogueria');"
        "INSERT INTO almacen.categoria_almacen(id_categoria_almacen, categoria_almacen) VALUES (3, 'Papeleria');"
        "INSERT INTO usuario.tipo_autenticacion(id_tipo_autenticacion, tipo_autenticacion) VALUES (1, 'Local');"
        "INSERT INTO usuario.tipo_autenticacion(id_tipo_autenticacion, tipo_autenticacion) VALUES (2, 'Google');"
        "INSERT INTO usuario.tipo_autenticacion(id_tipo_autenticacion, tipo_autenticacion) VALUES (3, 'Facebook');"
        # "INSERT INTO orden.metodo_pago(id_metodo_pago, metodo_pago) VALUES (1, 'Efectivo');"
        # "INSERT INTO orden.metodo_pago(id_metodo_pago, metodo_pago) VALUES (2, 'Tarjeta de credito');"
        # "INSERT INTO orden.metodo_pago(id_metodo_pago, metodo_pago) VALUES (3, 'Ahorros');"
        # "INSERT INTO orden.metodo_pago(id_metodo_pago, metodo_pago) VALUES (4, 'PayPal');"
        # "INSERT INTO usuario.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (1, 'es', 'AF', 'África');"
        # "INSERT INTO usuario.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (2, 'es', 'AN', 'Antártida');"
        # "INSERT INTO usuario.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (3, 'es', 'AS', 'Asia');"
        # "INSERT INTO usuario.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (4, 'es', 'EU', 'Europa');"
        # "INSERT INTO usuario.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (5, 'es', 'NA', 'Norteamérica');"
        # "INSERT INTO usuario.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (6, 'es', 'OC', 'Oceanía');"
        # "INSERT INTO usuario.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (7, 'es', 'SA', 'Sudamérica');"
        # "INSERT INTO almacen.continente_almacen(id_continente_almacen, locale, codigo_continente, nombre_continente) VALUES (1, 'es', 'AF', 'África');"
        # "INSERT INTO almacen.continente_almacen(id_continente_almacen, locale, codigo_continente, nombre_continente) VALUES (2, 'es', 'AN', 'Antártida');"
        # "INSERT INTO almacen.continente_almacen(id_continente_almacen, locale, codigo_continente, nombre_continente) VALUES (3, 'es', 'AS', 'Asia');"
        # "INSERT INTO almacen.continente_almacen(id_continente_almacen, locale, codigo_continente, nombre_continente) VALUES (4, 'es', 'EU', 'Europa');"
        # "INSERT INTO almacen.continente_almacen(id_continente_almacen, locale, codigo_continente, nombre_continente) VALUES (5, 'es', 'NA', 'Norteamérica');"
        # "INSERT INTO almacen.continente_almacen(id_continente_almacen, locale, codigo_continente, nombre_continente) VALUES (6, 'es', 'OC', 'Oceanía');"
        # "INSERT INTO almacen.continente_almacen(id_continente_almacen, locale, codigo_continente, nombre_continente) VALUES (7, 'es', 'SA', 'Sudamérica');"
        # "INSERT INTO almacen.pais_almacen(id_continente_almacen, locale, codigo_pais_iso, nombre_pais) VALUES (7, 'ES', 'CO', 'Colombia');"
        # "INSERT INTO almacen.ciudad_almacen(id_pais_almacen, ciudad, codigo_ciudad_iso) VALUES (1, 'Bogotá', 'BOG');"
        "INSERT INTO comun.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (1, 'es', 'AF', 'África');"
        "INSERT INTO comun.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (2, 'es', 'AN', 'Antártida');"
        "INSERT INTO comun.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (3, 'es', 'AS', 'Asia');"
        "INSERT INTO comun.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (4, 'es', 'EU', 'Europa');"
        "INSERT INTO comun.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (5, 'es', 'NA', 'Norteamérica');"
        "INSERT INTO comun.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (6, 'es', 'OC', 'Oceanía');"
        "INSERT INTO comun.continente(id_continente, locale, codigo_continente, nombre_continente) VALUES (7, 'es', 'SA', 'Sudamérica');"
        "INSERT INTO comun.pais(id_pais, locale, id_continente, codigo_pais_iso, nombre_pais) VALUES (1, 'ES', 7, 'CO', 'Colombia');"
        "INSERT INTO comun.ciudad(id_ciudad, id_pais, ciudad, codigo_ciudad_iso) VALUES (1, 1, 'Bogotá', 'BOG');"
        # "INSERT INTO almacen.rol_miembro_almacen(id_rol_miembro_almacen, rol_miembro_almacen) VALUES (1, 'Creador');"
        # "INSERT INTO almacen.rol_miembro_almacen(id_rol_miembro_almacen, rol_miembro_almacen) VALUES (2, 'Administrador');"
        # "INSERT INTO almacen.rol_miembro_almacen(id_rol_miembro_almacen, rol_miembro_almacen) VALUES (3, 'Operador');"
        "INSERT INTO usuario.tipo_grupo(id_tipo_grupo, tipo_grupo) VALUES (1, 'Creador');"
        "INSERT INTO usuario.tipo_grupo(id_tipo_grupo, tipo_grupo) VALUES (2, 'Administrador');"
        "INSERT INTO usuario.tipo_grupo(id_tipo_grupo, tipo_grupo) VALUES (3, 'Participante');"
        "INSERT INTO usuario.rol_grupo(id_rol_grupo, rol_grupo) VALUES (1, 'Creador');"
        "INSERT INTO usuario.rol_grupo(id_rol_grupo, rol_grupo) VALUES (2, 'Administrador');"
        "INSERT INTO usuario.rol_grupo(id_rol_grupo, rol_grupo) VALUES (3, 'Participante');"
        "INSERT INTO usuario.estado_solicitud(id_estado_solicitud, estado_solicitud) VALUES (1, 'Enviada');"
        "INSERT INTO usuario.estado_solicitud(id_estado_solicitud, estado_solicitud) VALUES (2, 'Aceptada');"
        "INSERT INTO usuario.estado_solicitud(id_estado_solicitud, estado_solicitud) VALUES (3, 'Rechazada');"
        "INSERT INTO usuario.estado_solicitud(id_estado_solicitud, estado_solicitud) VALUES (4, 'Bloqueada');"
        # "INSERT INTO orden.estado_transaccion(id_estado_transaccion, estado_transaccion) VALUES (1, 'En proceso');"
        # "INSERT INTO orden.estado_transaccion(id_estado_transaccion, estado_transaccion) VALUES (2, 'Aprobada');"
        # "INSERT INTO orden.estado_transaccion(id_estado_transaccion, estado_transaccion) VALUES (3, 'Rechazada');"
        "INSERT INTO lista.tipo_lista(id_tipo_lista, tipo_lista) VALUES (1, 'Receta');"
        "INSERT INTO lista.tipo_lista(id_tipo_lista, tipo_lista) VALUES (2, 'Lista de compras');"
        "INSERT INTO lista.tipo_distribucion_lista(id_tipo_distribucion_lista, tipo_distribucion_lista) VALUES (1, 'Publica');"
        "INSERT INTO lista.tipo_distribucion_lista(id_tipo_distribucion_lista, tipo_distribucion_lista) VALUES (2, 'Privada');"
        "INSERT INTO lista.tipo_distribucion_lista(id_tipo_distribucion_lista, tipo_distribucion_lista) VALUES (3, 'Amigos');"
        # "INSERT INTO servicio.rol_prestador_servicio(id_rol, rol) VALUES (1, 'Coordinador');"
        # "INSERT INTO servicio.rol_prestador_servicio(id_rol, rol) VALUES (2, 'Transportador');"
        # "INSERT INTO servicio.tipo_documento(id_tipo_documento, tipo_documento) VALUES (1, 'Cédula de ciudadanía');"
        # "INSERT INTO servicio.tipo_documento(id_tipo_documento, tipo_documento) VALUES (2, 'Pasaporte');"
        # "INSERT INTO servicio.tipo_documento(id_tipo_documento, tipo_documento) VALUES (3, 'Cédula de extranjeria');"
        # "INSERT INTO servicio.estado_servicio(id_estado_servicio, estado_servicio) VALUES (1, 'Pendiente');"
        # "INSERT INTO servicio.estado_servicio(id_estado_servicio, estado_servicio) VALUES (2, 'En proceso');"
        # "INSERT INTO servicio.estado_servicio(id_estado_servicio, estado_servicio) VALUES (3, 'En tránsito');"
        # "INSERT INTO servicio.estado_servicio(id_estado_servicio, estado_servicio) VALUES (4, 'Entregado');"
        # "INSERT INTO servicio.estado_servicio(id_estado_servicio, estado_servicio) VALUES (5, 'Aceptado');"
        # "INSERT INTO servicio.estado_servicio(id_estado_servicio, estado_servicio) VALUES (6, 'Cancelado');"
        "INSERT INTO usuario.origen_credito(id_origen_credito, origen_credito) VALUES (1, 'Cancelacion de servicio');"
        "INSERT INTO usuario.origen_credito(id_origen_credito, origen_credito) VALUES (2, 'Transferencia');"
        # "INSERT INTO servicio.motivo_cancelacion(id_motivo_cancelacion, motivo_cancelacion) VALUES (1, 'Exedió TEE');"
        # "INSERT INTO servicio.motivo_cancelacion(id_motivo_cancelacion, motivo_cancelacion) VALUES (2, 'Producto defectuoso');"
        # "INSERT INTO servicio.motivo_cancelacion(id_motivo_cancelacion, motivo_cancelacion) VALUES (3, 'Producto no ordenado');"
        # "INSERT INTO servicio.motivo_cancelacion(id_motivo_cancelacion, motivo_cancelacion) VALUES (4, 'Decision de usuario');"
        "INSERT INTO usuario.estado_miembro_suscripcion(id_estado_miembro_suscripcion, estado_miembro_suscripcion) VALUES (1, 'Activo');"
        "INSERT INTO usuario.estado_miembro_suscripcion(id_estado_miembro_suscripcion, estado_miembro_suscripcion) VALUES (2, 'Retirado');"
        "INSERT INTO usuario.estado_miembro_suscripcion(id_estado_miembro_suscripcion, estado_miembro_suscripcion) VALUES (3, 'Transferido');"
        "INSERT INTO usuario.plan_suscripcion (nombre_plan, cantidad_beneficiarios, limite_servicios, moneda, precio_plan, duracion_plan) VALUES ('Gratis', 1, -1, 'BRL', 0, -1);"
        "INSERT INTO usuario.plan_suscripcion (nombre_plan, cantidad_beneficiarios, limite_servicios, moneda, precio_plan, duracion_plan) VALUES ('Básico mensual', 2, 15, 'BRL', 6500, 1);"
        "INSERT INTO usuario.plan_suscripcion (nombre_plan, cantidad_beneficiarios, limite_servicios, moneda, precio_plan, duracion_plan) VALUES ('Básico anual', 2, 15, 'BRL', 71500, 12);"
        "INSERT INTO usuario.plan_suscripcion (nombre_plan, cantidad_beneficiarios, limite_servicios, moneda, precio_plan, duracion_plan) VALUES ('Avanzado mensual', 5, 45, 'BRL', 12500, 1);"
        "INSERT INTO usuario.plan_suscripcion (nombre_plan, cantidad_beneficiarios, limite_servicios, moneda, precio_plan, duracion_plan) VALUES ('Avanzado anual', 5, 45, 'BRL', 137500, 12);"
    )


def drop_database():

    event.listen(
        Base.metadata,
        'after_drop',
        DDL('DROP FUNCTION IF EXISTS usuario.update_created_column();')
    )

    event.listen(
        Base.metadata,
        'after_drop',
        DDL('DROP FUNCTION IF EXISTS usuario.update_modified_column();')
    )
    print('Borrando base de datos...')
    s.rollback()
    s.close()
    Base.metadata.drop_all(engine)
    print('Base de datos borrada')


if __name__ == '__main__':
    create_database()
