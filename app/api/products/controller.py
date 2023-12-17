from flask import request, jsonify

from .model import Product, db
from app.api.api_v1 import (
    convert_arg,
    get_args,
    API_V1,
    API_V1_ValidationException
)
from .specification import api_docs

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
            def query(data):
                data.count += _get_count()
                db.session.commit()
                res = { 'data': data }
                return res, 200 
            return self.query_id(id, query, 'PATCH')

        @self.bp.route('/<int:id>/sub', methods=['PATCH'])
        def sub_count(id):
            def query(data):
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
        
        error_400 = f"""
        '400':
          description: Количество должны быть положительным значением
          content:
            application/json:
              schema: CountError400Schema
        """        
        add_count.__doc__ = f"""
    ---
    patch:
      summary: Суммирование текущего количество товара к общему
      parameters:
        - in: query
          schema: Cost_ProductSchema
      responses:
        '200':
          description: {api_docs['put']['200']}
          content:
            application/json:
              schema: Table_ProductSchema""" +\
              error_400 + self.errors([401, 403, 404, 500])
        sub_count.__doc__ = f"""
    ---
    patch:
      summary: Вычитание текущего количества товара из общемего
      parameters:
        - in: query
          schema: Cost_ProductSchema
      responses:
        '200':
          description: {api_docs['put']['200']}
          content:
            application/json:
              schema: Table_ProductSchema""" +\
              error_400 + self.errors([401, 403, 404, 500])


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