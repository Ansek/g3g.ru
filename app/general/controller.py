import os
from flask import (
    Blueprint,
    render_template,
    url_for
)

module = Blueprint('general', __name__,
    template_folder='templates', static_folder='static', 
    static_url_path='/general/static')


@module.route('/', methods=['GET'])
def index():
    path = os.path.join(os.getcwd(),
        'app', 'general', 'static', 'img', 'slides')
    url = url_for('.static', filename='img/slides/')
    slides = [url + name for name in os.listdir(path)]
    return render_template('index.html', slides=slides)


@module.app_errorhandler(404)
def handle_404(err):
    return render_template('404.html'), 404


@module.app_errorhandler(500)
def handle_500(err):
    return render_template('500.html'), 500