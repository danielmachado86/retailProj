import collections
import re
import datetime
from sqlalchemy import func, or_
from sqlalchemy.sql.functions import ReturnTypeFromArgs

from unidecode import unidecode
import difflib

from dbmodel.dbconfig import s
from dbmodel.res.custom_exceptions import ResourceConflict, InvalidArgument
from dbmodel.database_model import ProductCategoryModel, BrandModel, StockModel, StockInputModel, StockOutputModel, ProductModel


class ProductCategory(ProductCategoryModel):

    def __init__(self, product_category_parent, product_category_name):
        self.product_category_parent = product_category_parent
        self.product_category_name = product_category_name

    def add_product_category(self):
        s.add(self)
        s.commit()

def get_product_category_id(category):
    item = s.query(ProductCategory).filter(
        ProductCategory.product_category_name == category).first()
    return item.id_categoria



class Brand(BrandModel):

    def __init__(self, brand_name, brand_description):
        check_manufacturer_exists_by_name(brand_name)
        self.brand_name = brand_name
        self.brand_description = brand_description

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.brand_id,
            'fabricante': self.brand_name,
            'descripcion': self.brand_description
        }

    def add_manufacturer(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def check_manufacturer_exists_by_name(name):
    if s.query(Brand).filter(
            Brand.brand_name == name).first():
        raise ResourceConflict('Este fabricante ya existe')
    return False


class Stock(StockModel):

    def __init__(self, product_id, store_id, price):
        self.product_id = product_id
        self.store_id = store_id
        self.stock_price = price

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.stock_item_id,
            'stock_price': self.stock_price,
        }

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

class StockInput(StockInputModel):

    def __init__(self, stock_item_id, store_member_id, stock_input_quantity, stock_expiration_date):
        self.stock_item_id = stock_item_id
        self.store_member_id = store_member_id
        self.stock_input_quantity = stock_input_quantity
        self.stock_input_date = datetime.datetime.now()
        self.stock_expiration_date = stock_expiration_date

    def add_inventory_input(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


class StockOutput(StockOutputModel):

    def __init__(self, stock_item_id, store_member_id, stock_output_quantity, stock_output_reason):
        self.stock_item_id = stock_item_id
        self.store_member_id = store_member_id
        self.stock_output_quantity = stock_output_quantity
        self.stock_output_reason = stock_output_reason
        self.stock_output_date = datetime.datetime.now()

    def add_inventory_output(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


class unaccent(ReturnTypeFromArgs):
    pass


class Product(ProductModel):

    search_similarity_index = None

    def __init__(self, product_category_id, brand_id, product_name, product_upc, product_unit_measure, product_is_taxable):
        self.product_category_id = product_category_id
        self.brand_id = brand_id
        self.product_name = product_name
        self.product_unit_measure = product_unit_measure
        self.product_upc = product_upc
        self.product_is_taxable = product_is_taxable

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.product_id,
            'nombre': self.product_name
        }

    def add_product(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def modify_item(self, product_category_id, brand_id, product_name, product_upc):
        self.product_category_id = product_category_id
        self.brand_id = brand_id
        self.product_name = product_name
        self.product_upc = product_upc
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_category(self, product_category_id):
        self.product_category_id = product_category_id
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_manufacturer(self, brand_id):
        self.brand_id = brand_id
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_name(self, product_name):
        self.product_name = product_name
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_barcode(self, product_upc):
        self.product_upc = product_upc
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}



def search_product(keywords):
    print('Original list: ', keywords)
    keywords = unidecode(keywords).lower()
    keyword_list = re.split("[^a-zA-Z0-9á-ú']+", keywords)

    keyword_list = collections.OrderedDict.fromkeys(keyword_list)
    keyword_list = [keyword for keyword in keyword_list if not (keyword is '' or len(keyword) <= 2)]

    print('Processed list: ', keyword_list)

    mfr_kw_filter = [Brand.brand_name.ilike("%" + kw + "%") for kw in keyword_list]
    mfrs = s.query(Brand.brand_id).filter(or_(*mfr_kw_filter)).all()

    print('Brand list ', [mfr.id_fabricante for mfr in mfrs])

    cat_kw_filter = [ProductCategory.product_category_name.ilike("%" + kw + "%") for kw in keyword_list]
    categories = s.query(ProductCategory.product_category_id).filter(or_(*cat_kw_filter)).all()
    print('Category list ', [cat.id_categoria for cat in categories])

    keyword_filter = [unaccent(Product.product_name).ilike("%" + keyword + "%") for keyword in keyword_list]
    keyword_filter.extend([Product.brand_id == kw for kw in mfrs])
    keyword_filter.extend([Product.product_category_id == kw for kw in categories])
    items = s.query(Product, func.concat(Brand.brand_name, ' ', Product.product_name, ' ', ProductCategory.product_category_name)).join(Brand).join(ProductCategory).filter(or_(*keyword_filter)).all()
    for item in items:
        print('Query:', item[1].lower())
        print('Keywords:', keywords.lower())
        item[0].search_similarity_index = difflib.SequenceMatcher(None, item[1].lower().split(), keywords.split()).quick_ratio()
    items.sort(key=lambda item1: item[0].search_similarity_index, reverse=True)
    return items


def get_product(item_id):
    if not item_id or '':
        raise InvalidArgument('El campo item_id no puede estar vacio')
    item = s.query(Product).filter(
        Product.product_id == item_id).first()
    return item


if __name__ == '__main__':
    pass