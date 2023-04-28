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
        self.name = name
        self.tname = dbclass.__tablename__
        
        @self.bp.route('/', methods=['GET'])
        def get():
            total = self._count()
            limit = current_app.config['REST_API_LIMIT']
            return self._get(limit, 0, total)
            
        @self.bp.route('/<int:id>', methods=['GET'])
        def get_id(id): 
            return self._get_by_id(id)

    def _count(self):
        try:
            count = self.dbclass.query.count()
        except SQLAlchemyError as e:
            abort(500)
        return count
            
    def _get(self, limit, offset, total, query=None):
        code = 200
        try:
            limit = request.args.get('limit', default=limit, type=int)
            offset = request.args.get('offset', default=offset, type=int)
            if query is None:
                query = self.dbclass.query
            data = query.limit(limit).offset(offset).all()
        except SQLAlchemyError as e:
            res = { 'message' :
                f'Error while querying the database (in {self.tname}.GET)'}
            code = 500
        if len(data) == 0:
            res = { 'message' :
                f'Nothing found for this query in {self.name}', 
                'limit':limit, 'offset':offset, 'total':total}
            code = 404
        else:
            res = {'data':data, 'limit':limit, 'offset':offset, 'total':total}
        return jsonify(res), code
        
    def _get_by_id(self, id, query=None):
        code = 200
        try:
            if query is None:
                query = self.dbclass.query
            data = query.get(id)
        except SQLAlchemyError as e:
            res = { 'message' :
                f'Error while querying the database (in {self.tname}.GET)'}
            code = 500
        if data is None:
            res = { 'message' :
                f'Resource {self.tname}.id = {id} was not found in the database'}
            code = 404
        else:
            res = { 'data': data }
        return jsonify(res), code 