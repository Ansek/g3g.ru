from flask import (
    Blueprint,
    render_template,
    flash,
    abort,
    current_app
)
from sqlalchemy.exc import SQLAlchemyError
from .model import Category, db

module = Blueprint('categories', __name__,
    template_folder='templates', url_prefix='/categories')

def log_error(e, cond):
    msg = f'Error while querying the database ({cond})'
    current_app.logger.error(msg, exc_info=e)
    flash(msg, 'danger')


@module.route('/', methods=['GET'])
def index():
    categories = None
    try:
        categories = Category.query.all()
    except SQLAlchemyError as e:
        log_error(e, 'in category.all')
        abort(500)
    return render_template('categories/index.html', categories=categories)