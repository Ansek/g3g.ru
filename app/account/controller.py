from flask import (
    Blueprint,
    render_template
)
from flask_login import login_required

module = Blueprint('account', __name__, url_prefix='/account',
    template_folder='templates', static_folder='static')


@module.route('/', methods=['GET'])
@login_required
def index():
    return render_template('account/index.html')