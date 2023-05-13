from flask import (
    Blueprint,
    render_template
)

from app.api.categories.model import Category

module = Blueprint('shop', __name__, url_prefix='/shop',
    template_folder='templates', static_folder='static')


@module.route('/category/<int:id>', methods=['GET'])
def index(id):
    category = Category.query.get_or_404(id)
    return render_template('shop/index.html', category=category)