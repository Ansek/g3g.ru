import copy
from marshmallow import Schema, fields, validate


_limit = fields.Int(
    description="Ограничие на количество в списке пользователей",
    required=False,
    example=10,
    validate=validate.Range(min=0))
    
_offset = fields.Int(
    description="Смещение в списке пользователей",
    required=False,
    example=5,
    validate=validate.Range(min=0))

_id = fields.Int(
    description="Идентификатор пользователя",
    required=True,
    example=1)

_login = fields.Str(
    description="Логин (unique)",
    required=True,
    example='admin',
    validate=validate.Length(max=128))

_password = fields.Str(
    description="Пароль",
    required=True,
    example='5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
    validate=validate.Length(max=64))

_telephone = fields.Str(
    description="Телефон (unique)",
    required=True,
    example='9211234567',
    validate=validate.Length(max=10))

_email = fields.Str(
    description="Электронный адрес",
    required=False,
    example='admin@mail.ru',
    validate=validate.Length(max=128))

_is_admin = fields.Bool(
    description="Флаг, имеет ли пользователь доступ администратора",
    required=False,
    example='true')

_total = fields.Int(
    description="Количество категорий, для которых выполняются условия",
    required=False,
    example=5,
    validate=validate.Range(min=0))

class GET_UserSchema(Schema):
    limit = _limit
    offset = _offset 


class ID_UserSchema(Schema):
    id = _id


class POST_UserSchema(Schema):
    login = _login
    password = _password
    telephone = _telephone
    email = _email
    is_admin = _is_admin


class Table_UserSchema(Schema):
    id = _id
    login = _login
    password = _password
    telephone = _telephone
    email = _email
    is_admin = _is_admin


class PATCH_UserSchema(Schema):
    id = _id
    login = copy.deepcopy(_login)
    password = copy.deepcopy(_password)
    telephone = copy.deepcopy(_telephone)
    email = copy.deepcopy(_email)
    is_admin = copy.deepcopy(_is_admin)
    login.required = False
    password.required = False
    telephone.required = False
    email.required = False
    is_admin.required = False
    

class LIST_UserSchema(Schema):
    data = fields.List(fields.Nested(Table_UserSchema()))
    limit = _limit
    offset = _offset
    total = _total
    
    
api_docs = {
    'tags': {
        'name': 'Users',
        'description': 'Информация о пользователях сайта'
    },
    'get': {
        'summary': 'Возвращает список пользователей',
        '200': 'Выводится список пользователей',
        '404': 'По данному запросу список пользователей пуст',
        'inputSchema': 'GET_UserSchema',
        'ouputSchema': 'LIST_UserSchema'
    }, 
    'get_id': {
        'summary': 'Возвращает пользователя по идентификатору',
        '200': 'Выводится информация о пользователе',
        'inputSchema': 'ID_UserSchema',
        'ouputSchema': 'Table_UserSchema'
    }, 
    'post': {
        'summary': 'Добавляет информацию о пользователе',
        '201': 'Выводится информация о пользователе с новым идентификатом',
        'inputSchema': 'POST_UserSchema',
        'ouputSchema': 'Table_UserSchema'
    },
    'put': {
        'summary': 'Изменяет информацию о пользователе целиком',
        '200': 'Выводится информация о пользователе с новыми данными',
        'inputSchema': 'Table_UserSchema',
        'ouputSchema': 'Table_UserSchema'
    },
    'patch': {
        'summary': 'Изменяет информацию о пользователе по указанным полям',
        '200': 'Выводится информация о пользователе с новыми данными',
        'inputSchema': 'PATCH_UserSchema',
        'ouputSchema': 'Table_UserSchema'
    },
    'delete': {
        'summary': 'Удаляет информацию о пользователе',
        '204': 'Ничего не возращает',
        'inputSchema': 'ID_UserSchema'
    },
    'errors': {
        '400': 'Неправильно заданы параметры',
        '404': 'По данному идентификатору пользователь не найден',
        '500': 'Произошла пробелема при выполнении запроса к БД'
    },
    'dictSchema': {
        'GET_UserSchema': GET_UserSchema,
        'ID_UserSchema': ID_UserSchema,
        'POST_UserSchema': POST_UserSchema,
        'Table_UserSchema': Table_UserSchema,
        'PATCH_UserSchema': PATCH_UserSchema,
        'LIST_UserSchema': LIST_UserSchema
    }         
}