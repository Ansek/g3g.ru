from flask import (
    Blueprint,
    jsonify,
    abort,
    request,
    current_app
)
from sqlalchemy.exc import SQLAlchemyError


class API_V1:
    def __init__(self, name, dbclass):
        self.bp = Blueprint(name, __name__, url_prefix=name)
        self.dbclass = dbclass
        
        @self.bp.route('/', methods=['GET'])
        def get():
            total = self.dbclass.query.count()
            limit = current_app.config['REST_API_LIMIT']
            args = self._get(limit, 0, total)
            return jsonify(args)
            
    def _get(self, limit, offset, total, query=None):
        try:
            limit = request.args.get('limit', default=limit, type=int)
            offset = request.args.get('offset', default=offset, type=int)
            if query is None:
                query = self.dbclass.query
            data = query.limit(limit).offset(offset).all()
        except SQLAlchemyError as e:
            abort(500)
        return { 'data':data, 'limit':limit, 'offset':offset, 'total':total }