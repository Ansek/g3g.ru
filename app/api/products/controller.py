from flask import request, jsonify

from .model import Product, db
from app.api.api_v1 import (
    convert_arg,
    log_error,
    get_args,
    API_V1,
    API_V1_ValidationException
)    


class Product_API_V1(API_V1):
    def __init__(self):
        super().__init__('products', Product)
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