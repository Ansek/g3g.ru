from flask import (
    Blueprint,
    render_template,
    current_app
)

module = Blueprint('basket', __name__,
    template_folder='templates', url_prefix='/basket')


@module.route('/', methods=['GET'])
def index():
    return render_template('basket/index.html')