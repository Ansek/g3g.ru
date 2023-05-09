from flask import (
    Blueprint,
    render_template,
    flash,
    abort,
    request,
    jsonify,
    current_app
)
from sqlalchemy.exc import SQLAlchemyError

from .model import Product, db
from app.api_v1 import (
    convert_arg,
    log_error,
    API_V1,
    API_V1_ValidationException
)    

module = Blueprint('products', __name__,
    template_folder='templates', url_prefix='/products')


@module.route('/', methods=['GET'])
def index():
    products = None
    try:
        products = Product.query.all()
    except SQLAlchemyError as e:
        log_error(e, 'in product.all')
        abort(500)
    return render_template('products/index.html', products=products)
    

class Product_API_V1(API_V1):
    def __init__(self):
        super().__init__('products', Product)
        self.gets_param.extend([
            'geCost', 'leCost', 'category'
        ])
        
        @self.bp.route('/<int:id>/add_count/<int:n>', methods=['PUT'])
        def add_count(id, n):
            def query(id, data):
                data.count += n
                db.session.commit()
                res = { 'data': data }
                return res, 200 
            return self.query_id(id, query, 'PUT')

        @self.bp.route('/<int:id>/sub_count/<int:n>', methods=['PUT'])
        def sub_count(id, n):
            def query(id, data):
                data.count -= n
                if data.count < 0:
                    msg = 'Сount cannot be a negative number. '+\
                        f'count = {data.count}'
                    res = { 'message': msg }
                    db.session.rollback()
                    return jsonify(res), 400
                db.session.commit()
                res = { 'data': data }
                return res, 200 
            return self.query_id(id, query, 'PUT')

    def get(self, limit, offset):
        query = self.dbclass.query
        
        try:
            # Стоимость больше или равно чем
            geCost = convert_arg('geCost', int)
            if geCost:
                 query = query.filter(Product.cost >= geCost)
            # Стоимость меньше или равно чем
            leCost = convert_arg('leCost', int)
            if leCost:
                 query = query.filter(Product.cost <= leCost)
            # Из категории
            category = convert_arg('category', int)
            if category:
                 query = query.filter(Product.category_id == category)
        except API_V1_ValidationException as e:
            res = { 'message': str(e)}
            return jsonify(res), 400
            
        return super().get(limit, offset, query)


api_v1 = Product_API_V1()