from flask import request, jsonify
from marshmallow import Schema, fields, validate

from .model import Product, db
from app.api.api_v1 import (
    convert_arg,
    get_args,
    API_V1,
    API_V1_ValidationException
)    


class ProductGETSchema(Schema):
    limit = fields.Int(description="Ограничие на количество в списке товаров", required=False, example=10, validate=validate.Range(min=0))
    offset = fields.Int(description="Смещение в списке товаров", required=False, example=5, validate=validate.Range(min=0))
    geCost = fields.Int(description="Стоимость товара больше или равно чем geCost", required=False, example=10000)
    leCost = fields.Int(description="Стоимость товара меньше или равно чем leCost", required=False, example=20000)
    category = fields.Int(description="Идентификатор категории", required=False, example=1)


class ProductTableSchema(Schema):
    name = fields.Str(description="Название товара (unique)", required=True, example='Lenovo K900', validate=validate.Length(max=128))
    cost = fields.Float(description="Стоимость товара", required=True, example=16000.0, validate=validate.Range(min=0))
    count = fields.Int(description="Количество в наличии", required=True, example=20, validate=validate.Range(min=0))
    img_path = fields.Str(description="Изображение товара", required=True, example='img/smartphone/sm1-1.png', validate=validate.Length(max=256))
    category_id = fields.Int(description="Идентификатор категории", required=True, example=1, validate=validate.Range(min=1))


class ProductIdSchema(Schema):
    id = fields.Int(description="Идентификатор товара", required=True, example=5)


api_docs = {
    'tags': {
        'name': 'Product',
        'description': 'Информация о товарах'
    },
    'get': {
        'summary': 'Возвращает список товаров',
        '200': 'Выводится список товаров',
        '404': 'По данному запросу список товаров пуст'
    }, 
    'get_id': {
        'summary': 'Возвращает товар по идентификатору',
        '200': 'Выводится информация о товаре'
    }, 
    'post': {
        'summary': 'Добавляет информацию о товаре',
        '201': 'Выводится информация о товаре с новым идентификатом'
    },
    'put': {
        'summary': 'Изменяет информацию о товаре целиком',
        '200': 'Выводится информация о товаре с новыми данными'
    },
    'patch': {
        'summary': 'Изменяет информацию о товаре по указанным полям',
        '200': 'Выводится информация о товаре с новыми данными'
    },
    'delete': {
        'summary': 'Удаляет информацию о товаре',
        '204': 'Ничего не возращает'
    },
    'errors': {
        '404': 'По данному идентификатору товар не найден',
        '400': 'Неправильно заданы параметры',
        '500': 'Произошла пробелема при выполнении запроса к БД'
    },
    'schema': {
        'get': 'ProductGETSchema',
        'id': 'ProductIdSchema',
        'table': 'ProductTableSchema'
    },  
    'dictSchema': {
        'ProductGETSchema': ProductGETSchema,
        'ProductIdSchema': ProductIdSchema,
        'ProductTableSchema': ProductTableSchema
    }         
}

class Product_API_V1(API_V1):
    def __init__(self):
        super().__init__('products', Product, api_docs)
        self.gets_param.extend([
            'geCost', 'leCost', 'category'
        ])
        
        def _get_count():
            args = get_args()
            count = convert_arg(args, 'count', int)
            if count is None:
                raise API_V1_ValidationException('The `count` parameter must be set')
            if len(args) > 1:
                raise API_V1_ValidationException('The method accepts only the `count` parameter')
            return count
        
        @self.bp.route('/<int:id>/add', methods=['PATCH'])
        def add_count(id):
            def query(id, data):
                data.count += _get_count()
                db.session.commit()
                res = { 'data': data }
                return res, 200 
            return self.query_id(id, query, 'PATCH')

        @self.bp.route('/<int:id>/sub', methods=['PATCH'])
        def sub_count(id):
            def query(id, data):
                data.count -= _get_count()
                if data.count < 0:
                    msg = 'Сount cannot be a negative number. '+\
                        f'count = {data.count}'
                    res = { 'message': msg }
                    db.session.rollback()
                    return jsonify(res), 400
                db.session.commit()
                res = { 'data': data }
                return res, 200 
            return self.query_id(id, query, 'PATCH')

    def get(self, limit, offset):
        query = self.dbclass.query
        
        try:
            args = request.args
            # Стоимость больше или равно чем
            geCost = convert_arg(args, 'geCost', int)
            if geCost:
                 query = query.filter(Product.cost >= geCost)
            # Стоимость меньше или равно чем
            leCost = convert_arg(args, 'leCost', int)
            if leCost:
                 query = query.filter(Product.cost <= leCost)
            # Из категории
            category = convert_arg(args, 'category', int)
            if category:
                 query = query.filter(Product.category_id == category)
        except API_V1_ValidationException as e:
            res = { 'message': str(e)}
            return jsonify(res), 400
            
        return super().get(limit, offset, query)


api_v1 = Product_API_V1()