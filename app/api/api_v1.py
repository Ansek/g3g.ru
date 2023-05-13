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
from marshmallow import Schema, fields
import json

from app.database import db


def get_args():
    args = None
    if request.form:
        args = request.form
    elif request.json:
        args = request.json       
    return args


def convert_arg(args, arg_name, arg_type, IsNotNone=False):
    arg = args.get(arg_name)
    res = None
    str_type = arg_type.__name__
    msg = f'{arg_name} should be of type {str_type}'
    if arg:
        arg = args.get(arg_name, type=arg_type)
        if arg is not None:
            res = arg
        else:
            raise API_V1_ValidationException(msg)
    elif IsNotNone:
        raise API_V1_ValidationException(msg)
    return res


def check_unumber(n, name):
    if n and n < 0:
        msg = f'{name} must be should be a positive number'
        raise API_V1_ValidationException(msg)


def check_string(s, size, name):
    if s:  
        if len(s.strip()) == 0:
            msg = f'{name} must not be empty'
            raise API_V1_ValidationException(msg)
            
        if len(s) > size:
            msg = f'{name} must exceed {size} characters'
            raise API_V1_ValidationException(msg)


def check_arg_list(args, arg_list):
    for key in args.keys():
        if key not in arg_list:
            msg = f'The method has no argument named `{key}`'
            raise API_V1_ValidationException(msg)


def log_error(msg, e):
    print(f'\n{msg}\n{e}\n')

class Error400Schema(Schema):
    message = fields.String(description="Сообщение об ошибке", required=True, example='Id must be should be a positive number')


class Error404Schema(Schema):
    message = fields.String(description="Сообщение об ошибке", required=True, example='Resource table.id = id was not found in the database')


class ListError404Schema(Schema):
    message = fields.String(description="Сообщение об ошибке", required=True, example='Nothing found for this query in table')


class Error500Schema(Schema):
    message = fields.String(description="Сообщение об ошибке", required=True, example='Error while querying the database')

api_docs = {
    'dictSchema': {
        'Error400Schema': Error400Schema,
        'Error404Schema': Error404Schema,
        'ListError404Schema': ListError404Schema,
        'Error500Schema': Error500Schema
    }
}    
    
class API_V1:
    def __init__(self, name, dbclass, api_docs):
        self.bp = Blueprint(name, __name__, url_prefix=name)
        self.dbclass = dbclass
        self.name = name                        # Имя ресурса (мн. числе)
        self.tname = dbclass.__tablename__      # Имя таблицы (ед. числе)
        self.gets_param = ['limit', 'offset']   # Параметры метода GET
        
        @self.bp.route('/', methods=['GET'])
        def get():
            limit = current_app.config['REST_API_LIMIT']
            res, code = self.get(limit, 0)
            return jsonify(res), code
         
        @self.bp.route('/<int:id>', methods=['GET'])
        def get_id(id):
            res, code = self.get_by_id(id)       
            return jsonify(res), code
            
        @self.bp.route('/', methods=['POST'])
        def post():
            res, code = self.post()
            return jsonify(res), code

        @self.bp.route('/<int:id>', methods=['PUT'])
        def put(id):
            res, code = self.put(id)
            return jsonify(res), code
            
        @self.bp.route('/<int:id>', methods=['PATCH'])
        def patch(id):
            res, code = self.patch(id)
            return jsonify(res), code
            
        @self.bp.route('/<int:id>', methods=['DELETE'])
        def delete(id):
            res, code = self.delete(id)
            return jsonify(res), code
            
        
        error_404 =  f"""
        '400':
          description: {api_docs['errors']['404']}
          content:
            application/json:
              schema: Error404Schema   
    """
        error_400_500 = f"""
        '400':
          description: {api_docs['errors']['400']}
          content:
            application/json:
              schema: Error400Schema
        '500':
          description: {api_docs['errors']['500']}
          content:
            application/json:
              schema: Error500Schema
      tags:
        - {api_docs['tags']['name']}   
    """     
        get.__doc__ = f"""
    ---
    get:
      summary: {api_docs['get']['summary']}
      parameters:
        - in: query
          schema: {api_docs['schema']['get']}
      responses:
        '200':
          description: {api_docs['get']['200']}
          content:
            application/json:
              schema: {api_docs['schema']['table']}
        '404':
          description: {api_docs['get']['404']}
          content:
            application/json:
              schema: ListError404Schema""" + error_400_500
        get_id.__doc__ = f"""
    ---
    get:
      summary: {api_docs['get_id']['summary']}
      parameters:
        - in: query
          schema: {api_docs['schema']['id']}
      responses:
        '200':
          description: {api_docs['get_id']['200']}
          content:
            application/json:
              schema: {api_docs['schema']['table']}""" + error_404 + error_400_500
        post.__doc__ = f"""
    ---
    post:
      summary: {api_docs['post']['summary']}
      parameters:
        - in: query
          schema: {api_docs['schema']['id']}
      responses:
        '201':
          description: {api_docs['post']['201']}
          content:
            application/json:
              schema: {api_docs['schema']['table']}""" + error_404 + error_400_500
        put.__doc__ = f"""
    ---
    put:
      summary: {api_docs['put']['summary']}
      parameters:
        - in: query
          schema: {api_docs['schema']['id']}
      responses:
        '200':
          description: {api_docs['put']['200']}
          content:
            application/json:
              schema: {api_docs['schema']['table']}""" + error_404 + error_400_500
        patch.__doc__ = f"""
    ---
    patch:
      summary: {api_docs['patch']['summary']}
      parameters:
        - in: query
          schema: {api_docs['schema']['id']}
      responses:
        '200':
          description: {api_docs['patch']['200']}
          content:
            application/json:
              schema: {api_docs['schema']['table']}""" + error_404 + error_400_500
        delete.__doc__ = f"""
    ---
    delete:
      summary: {api_docs['delete']['summary']}
      parameters:
        - in: query
          schema: {api_docs['schema']['id']}
      responses:
        '204':
          description: {api_docs['delete']['204']}
          content:
            application/json:
              schema: {api_docs['schema']['table']}""" + error_404 + error_400_500

    def count(self):
        try:
            count = self.dbclass.query.count()
        except SQLAlchemyError as e:
            abort(500)
        return count
        
    def query_id(self, id, query, method):
        try:
            if id is None:
                res, code = query()
            else:
                data = self.dbclass.query.get(id)
                if data is None:
                    res = { 'message':
                        f'Resource {self.tname}.id = {id}' +\
                        ' was not found in the database'}
                    code = 404
                else:
                    res, code = query(id, data)            
        except SQLAlchemyError as e:
            msg = 'Error while querying the database' +\
                f'(in {self.tname}.{method})'
            res = { 'message': msg }
            code = 500
            log_error(msg, e)
            db.session.rollback()
        except API_V1_ValidationException as e:
            res = { 'message': str(e)}
            code = 400  
        return res, code      
            
    def get(self, limit, offset, query=None):
        code = 200
        try:
            args = request.args
            # Проверка на соотвествие аргументам
            check_arg_list(args, self.gets_param)
            # Если заданы пользовательские значения
            arg = convert_arg(args, 'limit', int)
            if arg is not None:
                 limit = arg
            arg = convert_arg(args, 'offset', int)
            if arg is not None:
                 offset = arg
            # Выполнение запроса 
            if query is None:
                query = self.dbclass.query
            total = query.count()
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
        return res, code
        
    def get_by_id(self, id, query=None):
        def query(id, data):
            res = { 'data': data }
            return res, 200
        return self.query_id(id, query, 'GET')
    
    def post(self):
        def query():
            args = get_args()
            self.dbclass.validate_args(args)
            data = self.dbclass(**args)
            db.session.add(data)
            db.session.flush()
            db.session.commit()
            res = { 'data': data }
            return res, 201        
        return self.query_id(None, query, 'POST')
        
    def put(self, id):
        def query(id, data):
            args = get_args()
            self.dbclass.validate_args(args)
            for key in args:
                setattr(data, key, args[key])
            db.session.commit()
            res = { 'data': data }
            return res, 200        
        return self.query_id(id, query, 'PUT')
        
    def patch(self, id):
        def query(id, data):
            args = get_args()
            self.dbclass.validate_args(args, False)
            is_changed = False
            # Сравнение с приведением к одному типу
            for key in args:
                val = args[key]
                t = type(getattr(data, key))
                if getattr(data, key) != t(val):
                    setattr(data, key, val)
                    is_changed = True
            # Если изменений не было
            if not is_changed:
                return '', 304
            # Иначе фиксируем данные
            db.session.commit()
            res = { 'data': data }
            return res, 200 
        return self.query_id(id, query, 'PATCH')

    def delete(self, id):
        def query(id, data):
            db.session.delete(data)
            db.session.commit()
            return '', 204
        return self.query_id(id, query, 'DELETE')

        
class API_V1_ValidationException(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg