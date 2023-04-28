from flask import (
    Blueprint,
    render_template,
    flash,
    abort,
    current_app
)
from sqlalchemy.exc import SQLAlchemyError

from .model import Section, db
from app.api_v1 import API_V1

module = Blueprint('sections', __name__,
    template_folder='templates', url_prefix='/sections')


def log_error(e, cond):
    msg = f'Error while querying the database ({cond})'
    current_app.logger.error(msg, exc_info=e)
    flash(msg, 'danger')


@module.route('/', methods=['GET'])
def index():
    sections = None
    try:
        sections = Section.query.all()
    except SQLAlchemyError as e:
        log_error(e, 'in section.all')
        abort(500)
    return render_template('sections/index.html', sections=sections)
    

api_v1 = API_V1('sections', Section)