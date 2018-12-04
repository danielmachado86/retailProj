from sqlalchemy import event
from sqlalchemy.schema import DDL
from dbmodel.dbconfig import engine


from dbmodel.database_model import Base


def create_database():
    print('Creando base de datos...')
    Base.metadata.schema = 'public'
    # engine.execute(
    #     "CREATE SCHEMA audit AUTHORIZATION qbxzyxxpozarvq;"
    #     "CREATE EXTENSION unaccent;")

    Base.metadata.create_all()

    print('Base de datos creada')

    engine.execute(
        "INSERT INTO store_category(store_category_id, store_category) VALUES (1, 'Mercado');"
        "INSERT INTO store_category(store_category_id, store_category) VALUES (2, 'Drogueria');"
        "INSERT INTO store_category(store_category_id, store_category) VALUES (3, 'Papeleria');"
        "INSERT INTO continent(continent_id, continent_locale, continent_code, continent_name) VALUES (1, 'es', 'AF', 'África');"
        "INSERT INTO continent(continent_id, continent_locale, continent_code, continent_name) VALUES (2, 'es', 'AN', 'Antártida');"
        "INSERT INTO continent(continent_id, continent_locale, continent_code, continent_name) VALUES (3, 'es', 'AS', 'Asia');"
        "INSERT INTO continent(continent_id, continent_locale, continent_code, continent_name) VALUES (4, 'es', 'EU', 'Europa');"
        "INSERT INTO continent(continent_id, continent_locale, continent_code, continent_name) VALUES (5, 'es', 'NA', 'Norteamérica');"
        "INSERT INTO continent(continent_id, continent_locale, continent_code, continent_name) VALUES (6, 'es', 'OC', 'Oceanía');"
        "INSERT INTO continent(continent_id, continent_locale, continent_code, continent_name) VALUES (7, 'es', 'SA', 'Sudamérica');"
        "INSERT INTO country(country_id, country_locale, continent_id, country_iso_code, country_name) VALUES (1, 'ES', 7, 'CO', 'Colombia');"
        "INSERT INTO city(city_id, country_id, city_name, city_iso_code) VALUES (1, 1, 'Bogotá', 'BOG');"
    )


def drop_database():
    print('Borrando base de datos...')
    engine.execute("drop owned by qbxzyxxpozarvq")
    print('Base de datos borrada')
