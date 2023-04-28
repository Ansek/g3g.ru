from flask import (
    Blueprint,
    jsonify,
    abort,
    request,
    redirect,
    url_for,
    current_app
)
from sqlalchemy.exc import SQLAlchemyError

from app.database import db


def convert_arg(arg_name, arg_type=int, str_type='int', IsNotNone=False):
    arg = request.args.get(arg_name)
    res = None
    msg = f'{arg_name} should be of type {str_type}'
    if arg and arg != '':
        arg = request.args.get(arg_name, type=arg_type)
        if arg is not None:
            res = arg
        else:
            raise API_V1_ValidationException(msg)
    elif IsNotNone:
        raise API_V1_ValidationException(msg)
    return res

def log_error(msg, e):
    print(f'\n{msg}\n{e}\n')

class API_V1:
    def __init__(self, name, dbclass):
        self.bp = Blueprint(name, __name__, url_prefix=name)
        self.dbclass = dbclass
        self.name = name                        # Имя ресурса (мн. числе)
        self.tname = dbclass.__tablename__      # Имя таблицы (мн. числе)
        self.gets_param = ['limit', 'offset']   # Параметры метода Get
        
        @self.bp.route('/', methods=['GET'])
        def get():
            total = self._count()
            limit = current_app.config['REST_API_LIMIT']
            return self._get(limit, 0, total)
            
        @self.bp.route('/<int:id>', methods=['GET'])
        def get_id(id): 
            return self._get_by_id(id)
            
        @self.bp.route('/', methods=['POST'])
        def post(): 
            return self._post()

    def _count(self):
        try:
            count = self.dbclass.query.count()
        except SQLAlchemyError as e:
            abort(500)
        return count
            
    def _get(self, limit, offset, total, query=None):
        code = 200
        # Проверка соотвествия аргументам
        for key in request.args.keys():
            if key not in self.gets_param:
                return jsonify({'message':
                    f'The method has no argument named `{key}`'}), 400
        try:
            # Если заданы пользовательские значения
            arg = self._convert_arg('limit', int)
            if arg:
                 limit = arg
            arg = self._convert_arg('offset', int)
            if arg:
                 offset = arg
            # Выполнение запроса 
            if query is None:
                query = self.dbclass.query
            data = query.limit(limit).offset(offset).all()
            # Проверка на отсутствие данных
            if len(data) == 0:
                res = { 'message':
                    f'Nothing found for this query in {self.name}', 
                    'limit':limit, 'offset':offset, 'total':total}
                code = 404
            else:
                res = {'data':data, 'limit':limit, 'offset':offset, 'total':total}
        except SQLAlchemyError as e:
            res = { 'message':
                f'Error while querying the database (in {self.tname}.GET)'}
            code = 500
        except API_V1_ValidationException as e:
            res = { 'message': str(e)}
            code = 400
        return jsonify(res), code
        
    def _get_by_id(self, id, query=None):
        code = 200
        # Выполнение запроса
        try:
            if query is None:
                query = self.dbclass.query
            data = query.get(id)
        except SQLAlchemyError as e:
            res = { 'message':
                f'Error while querying the database (in {self.tname}.GET)'}
            code = 500
        # Проверка на отсутствие данных
        if data is None:
            res = { 'message':
                f'Resource {self.tname}.id = {id} was not found in the database'}
            code = 404
        else:
            res = { 'data': data }
        return jsonify(res), code 
        
    def _post(self):
        code = 201
        # Выполнение запроса
        try:
            self.dbclass.validate_args()
            dbclass = self.dbclass(**request.args)
            db.session.add(dbclass)
            db.session.flush()
            id = dbclass.id
            db.session.commit()
            res = { 'data': dbclass }
        except SQLAlchemyError as e:
            msg = f'Error while querying the database (in {self.tname}.GET)\n'
            res = { 'message': msg }
            log_error(msg, e)
            code = 500
            db.session.rollback()
        except API_V1_ValidationException as e:
            res = { 'message': str(e)}
            code = 400
            db.session.rollback()
        return jsonify(res), code    

    def _convert_arg(self, *args):
        return convert_arg(*args)
        
class API_V1_ValidationException(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg