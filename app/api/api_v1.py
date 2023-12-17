from flask import (
    Blueprint,
    jsonify,
    abort,
    request,
    url_for,
    current_app
)
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from psycopg2.errors import UniqueViolation
from marshmallow import Schema, fields

from app.database import db


def get_args():
    args = None
    if request.form:
        args = request.form.to_dict()
        for k, v in args.items():
            if v.lower() == 'true':
                args[k] = True
            if v.lower() == 'false':
                args[k] = False
    elif request.json:
        args = request.json       
    return args


def convert_arg(args, arg_name, arg_type, IsNotNone=False):
    arg = args.get(arg_name)
    res = None
    str_type = arg_type.__name__
    msg = f'{arg_name} should be of type {str_type}'
    if arg is not None:
        arg = arg_type(args.get(arg_name))
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
    if len(arg_list) > 0 and args is None:
        msg = 'There are no arguments here'
        raise API_V1_ValidationException(msg) 
    for key in args.keys():
        if key not in arg_list:
            msg = f'The method has no argument named `{key}`'
            raise API_V1_ValidationException(msg)


def check_authorization(only_admin):
    if not current_user.is_authenticated:
        raise API_V1_UnauthorizedException()
    if only_admin and not current_user.is_admin:
        raise API_V1_ForbiddenException()


def log_error(msg, e):
    print(f'\n{msg}\n{e}\n')


def try_query_func(func, resource, method):
        try:
            res, code = func()
        except SQLAlchemyError as e:
            if isinstance(e.orig, UniqueViolation):
                msg = str(e.orig)
                msg = msg[msg.index('Key'):-2]
            else:
                msg = 'Error while querying the database ' +\
                    f'(in {resource}.{method})'
            res = { 'message': msg }
            code = 500
            log_error(msg, e)
            db.session.rollback()
        except API_V1_ValidationException as e:
            res = { 'message': str(e)}
            code = 400
        except API_V1_UnauthorizedException as e:
            res = { 'message': str(e)}
            code = 401
        except API_V1_ForbiddenException as e:
            res = { 'message': str(e)}
            code = 403
        return res, code


class Error400Schema(Schema):
    message = fields.String(
        description="Сообщение об ошибке",
        required=True,
        example='Id must be should be a positive number')


class Error401Schema(Schema):
    message = fields.String(
        description="Сообщение об ошибке",
        required=True,
        example='Unauthorized access. Make a request for /api/v1/session/login/')
    

class Error403Schema(Schema):
    message = fields.String(
        description="Сообщение об ошибке",
        required=True,
        example='Access is denied. Administrator rights are required')


class Error404Schema(Schema):
    message = fields.String(
        description="Сообщение об ошибке",
        required=True,
        example='Resource table.id = id was not found in the database')


class ListError404Schema(Schema):
    message = fields.String(
        description="Сообщение об ошибке",
        required=True,
        example='Nothing found for this query in table')


class Error500Schema(Schema):
    message = fields.String(description="Сообщение об ошибке", required=True, example='Error while querying the database')

api_docs = {
    'dictSchema': {
        'Error400Schema': Error400Schema,
        'Error401Schema': Error401Schema,
        'Error403Schema': Error403Schema,
        'Error404Schema': Error404Schema,
        'ListError404Schema': ListError404Schema,
        'Error500Schema': Error500Schema
    }
}    
    
class API_V1:
    def __init__(self, name, dbclass, api_docs, allow_post=False, only_admin=True):
        self.bp = Blueprint(name, __name__, url_prefix=name)
        self.dbclass = dbclass
        self.name = name                        # Имя ресурса (мн. числе)
        self.tname = dbclass.__tablename__      # Имя таблицы (ед. числе)
        self.gets_param = ['limit', 'offset']   # Параметры метода GET
        self.allow_post = allow_post            # Разрешить POST без авторизации
        self.only_admin = only_admin            # Выполнение только с правом администратора
        
        @self.bp.route('/', methods=['GET'])
        def get():
            limit = current_app.config['REST_API_LIMIT']
            res, code = self.get(limit, 0)
            response = jsonify(res)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, code
         
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
            
        # Формирование текста для перечисления схем ошибок + тег    
        def errors(codes):
            s = str(codes[0])
            err = f"""
        '{s}':
          description: {api_docs['errors'][s]}
          content:
            application/json:
              schema: Error{s}Schema
        """
            if len(codes) > 1:
                return err + errors(codes[1:])
            else:
                return err + f"""
      tags:
        - {api_docs['tags']['name']}   
        """
            
        add_codes = [400, 500]
        edit_codes = [400, 404, 500]
        del_codes = [404, 500]
        if only_admin:
            add_codes.insert(1, 403)
            edit_codes.insert(1, 403)
            del_codes.insert(0, 403)
        if not allow_post:
            add_codes.insert(1, 401)

        # Установка документации к методам
        get.__doc__ = f"""
    ---
    get:
      summary: {api_docs['get']['summary']}
      parameters:
        - in: query
          schema: {api_docs['get']['inputSchema']}
      responses:
        '200':
          description: {api_docs['get']['200']}
          content:
            application/json:
              schema: {api_docs['get']['ouputSchema']}
        '404':
          description: {api_docs['get']['404']}
          content:
            application/json:
              schema: ListError404Schema""" +\
              errors([400, 404, 500])
        get_id.__doc__ = f"""
    ---
    get:
      summary: {api_docs['get_id']['summary']}
      parameters:
        - in: query
          schema: {api_docs['get_id']['inputSchema']}
      responses:
        '200':
          description: {api_docs['get_id']['200']}
          content:
            application/json:
              schema: {api_docs['get_id']['ouputSchema']}""" +\
              errors([400, 404, 500])
        post.__doc__ = f"""
    ---
    post:
      summary: {api_docs['post']['summary']}
      parameters:
        - in: query
          schema: {api_docs['post']['inputSchema']}
      responses:
        '201':
          description: {api_docs['post']['201']}
          content:
            application/json:
              schema: {api_docs['post']['ouputSchema']}""" +\
              errors(add_codes)
        put.__doc__ = f"""
    ---
    put:
      summary: {api_docs['put']['summary']}
      parameters:
        - in: query
          schema: {api_docs['put']['inputSchema']}
      responses:
        '200':
          description: {api_docs['put']['200']}
          content:
            application/json:
              schema: {api_docs['put']['ouputSchema']}""" +\
              errors(edit_codes)
        patch.__doc__ = f"""
    ---
    patch:
      summary: {api_docs['patch']['summary']}
      parameters:
        - in: query
          schema: {api_docs['patch']['inputSchema']}
      responses:
        '200':
          description: {api_docs['patch']['200']}
          content:
            application/json:
              schema: {api_docs['patch']['ouputSchema']}""" +\
              errors(edit_codes)
        delete.__doc__ = f"""
    ---
    delete:
      summary: {api_docs['delete']['summary']}
      parameters:
        - in: query
          schema: {api_docs['delete']['inputSchema']}
      responses:
        '204':
          description: {api_docs['delete']['204']}""" +\
          errors(del_codes)
          
        self.errors = errors

    def count(self):
        try:
            count = self.dbclass.query.count()
        except SQLAlchemyError as e:
            abort(500)
        return count


    def query_id(self, id, query, method):
        def func():
            data = self.dbclass.query.get(id)
            if data is None:
                res = { 'message':
                    f'Resource {self.tname}.id = {id}' +\
                    ' was not found in the database'}
                code = 404
            else:
                res, code = query(data)
            return res, code
        return try_query_func(func, self.tname, method)
         
            
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
        def query(data):
            res = { 'data': data }
            return res, 200
        return self.query_id(id, query, 'GET')
    
    def post(self):
        def query():
            if not self.allow_post:
                check_authorization(self.only_admin)
            args = get_args()
            self.dbclass.validate_args(args)
            data = self.dbclass(**args)
            db.session.add(data)
            db.session.flush()
            db.session.commit()
            res = { 'data': data }
            return res, 201        
        return try_query_func(query, self.tname, 'POST')
        
    def put(self, id):
        def query(data):
            check_authorization(self.only_admin)
            args = get_args()
            self.dbclass.validate_args(args)
            for key in args:
                setattr(data, key, args[key])
            db.session.commit()
            res = { 'data': data }
            return res, 200        
        return self.query_id(id, query, 'PUT')
        
    def patch(self, id):
        def query(data):
            check_authorization(self.only_admin)
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
        def query(data):
            check_authorization(self.only_admin)
            db.session.delete(data)
            db.session.commit()
            return '', 204
        return self.query_id(id, query, 'DELETE')

        
class API_V1_ValidationException(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg
    
class API_V1_UnauthorizedException(Exception): 
    def __init__(self):
        self.msg = 'Unauthorized access. Make a request for ' + url_for('api_v1.session.login')
        
    def __str__(self):
        return self.msg

class API_V1_ForbiddenException(Exception):
    def __init__(self):
        self.msg = 'Access is denied. Administrator rights are required'
        
    def __str__(self):
        return self.msg