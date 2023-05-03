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
from app.api_v1 import API_V1, API_V1_ValidationException

module = Blueprint('products', __name__,
    template_folder='templates', url_prefix='/products')


def log_error(e, cond):
    msg = f'Error while querying the database ({cond})'
    current_app.logger.error(msg, exc_info=e)
    flash(msg, 'danger')


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

    def get(self, limit, offset, total):
        query = self.dbclass.query
        
        try:
            # Стоимость больше или равно чем
            geCost = self._convert_arg('geCost', int)
            if geCost:
                 query = query.filter(Product.cost >= geCost)
            # Стоимость меньше или равно чем
            leCost = self._convert_arg('leCost', int)
            if leCost:
                 query = query.filter(Product.cost <= leCost)
            # Из категории
            category = self._convert_arg('category', int)
            if category:
                 query = query.filter(Product.category_id == category)
        except API_V1_ValidationException as e:
            res = { 'message': str(e)}
            return jsonify(res), 400
            
        return super().get(limit, offset, total, query)

api_v1 = Product_API_V1()