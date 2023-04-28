from flask import (
    Blueprint,
    render_template,
    flash,
    abort,
    request,
    current_app
)
from sqlalchemy.exc import SQLAlchemyError

from .model import Product, db
from app.api_v1 import API_V1

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
    
    def _get(self, limit, offset, total):
        query = self.dbclass.query
        
        # Стоимость больше или равно чем
        geCost = request.args.get('geCost')
        if geCost and geCost != '':
            geCost = request.args.get('geCost', type=int)
            query = query.filter(Product.cost >= geCost)
        
        # Стоимость меньше или равно чем
        leCost = request.args.get('leCost')
        if leCost and leCost != '':
            leCost = request.args.get('leCost', type=int)
            query = query.filter(Product.cost <= leCost)
            
        # Из категории
        category = request.args.get('category')
        if category and category != '':
            category = request.args.get('category', type=int)
            query = query.filter(Product.category_id == category)
           
        return super()._get(limit, offset, total, query)
    
api_v1 = Product_API_V1()