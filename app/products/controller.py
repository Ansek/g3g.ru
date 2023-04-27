from flask import (
    Blueprint,
    render_template,
    flash,
    abort,
    current_app
)
from sqlalchemy.exc import SQLAlchemyError
from .model import Product, db

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
    
    