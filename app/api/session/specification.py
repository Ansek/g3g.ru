from marshmallow import Schema, fields, validate


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

_remember = fields.Bool(
    description="Флаг, следует ли запоминать вход пользователя",
    required=False,
    example='true')


class Login_SessionSchema(Schema):
    login = _login
    password = _password
    remember = _remember


class ErrorLoginSchema(Schema):
    message = fields.String(
        description="Сообщение об ошибке",
        required=True,
        example='Invalid login or password')


api_docs = {
    'tags': {
        'name': 'Session',
        'description': 'Для работы с авторизацией пользователей'
    },
    'dictSchema': {
        'Login_SessionSchema': Login_SessionSchema,
        'ErrorLoginSchema': ErrorLoginSchema
    }         
}