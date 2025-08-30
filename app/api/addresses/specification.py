import copy
from marshmallow import Schema, fields, validate


_limit = fields.Int(
    description="Ограничие на количество в списке адресов",
    required=False,
    example=10,
    validate=validate.Range(min=0))
    
_offset = fields.Int(
    description="Смещение в списке адресов",
    required=False,
    example=5,
    validate=validate.Range(min=0))

_id = fields.Int(
    description="Идентификатор адреса",
    required=True,
    example=5)

_address = fields.Str(
    description="Адрес (unique)",
    required=True,
    example='ул. Котова, д. 5',
    validate=validate.Length(max=128))

_city = fields.Str(
    description="Город",
    required=True,
    example='Санкт-Петербург',
    validate=validate.Length(max=128))

_img_path = fields.Str(
    description="Карта (unique)",
    required=True,
    example='img/map/addr1.png',
    validate=validate.Length(max=256))

_total = fields.Int(
    description="Количество адресов, для которых выполняются условия",
    required=False,
    example=5,
    validate=validate.Range(min=0))


class GET_AddressSchema(Schema):
    limit = _limit
    offset = _offset 


class ID_AddressSchema(Schema):
    id = _id


class POST_AddressSchema(Schema):
    address = _address
    city = _city
    img_path = _img_path


class Data_AddressSchema(Schema):
    id = _id
    address = _address
    city = _city
    img_path = _img_path


class Table_AddressSchema(Schema):
    data = fields.Nested(Data_AddressSchema())
    total = _total


class PATCH_AddressSchema(Schema):
    id = _id
    address = copy.deepcopy(_address)
    city = copy.deepcopy(_city)
    img_path = copy.deepcopy(_img_path)
    address.required = False
    city.required = False
    img_path.required = False
    

class LIST_AddressSchema(Schema):
    data = fields.List(fields.Nested(Data_AddressSchema()))
    limit = _limit
    offset = _offset
    total = _total
    
    
api_docs = {
    'tags': {
        'name': 'Address',
        'description': 'Информация об адресах салона связи'
    },
    'get': {
        'summary': 'Возвращает список адресов',
        '200': 'Выводится список адресов',
        '404': 'По данному запросу список адресов пуст',
        'inputSchema': 'GET_AddressSchema',
        'ouputSchema': 'LIST_AddressSchema'
    }, 
    'get_id': {
        'summary': 'Возвращает адрес по идентификатору',
        '200': 'Выводится информация об адресе',
        'inputSchema': 'ID_AddressSchema',
        'ouputSchema': 'Table_AddressSchema'
    }, 
    'post': {
        'summary': 'Добавляет информацию об адресе',
        '201': 'Выводится информация об адресе с новым идентификатом',
        'inputSchema': 'POST_AddressSchema',
        'ouputSchema': 'Table_AddressSchema'
    },
    'put': {
        'summary': 'Изменяет информацию об адресе целиком',
        '200': 'Выводится информация об адресе с новыми данными',
        'inputSchema': 'Data_AddressSchema',
        'ouputSchema': 'Table_AddressSchema'
    },
    'patch': {
        'summary': 'Изменяет информацию об адресе по указанным полям',
        '200': 'Выводится информация об адресе с новыми данными',
        'inputSchema': 'PATCH_AddressSchema',
        'ouputSchema': 'Table_AddressSchema'
    },
    'delete': {
        'summary': 'Удаляет информацию об адресе',
        '200': 'Количество оставшихся данных',
        'inputSchema': 'ID_AddressSchema'
    },
    'errors': {
        '400': 'Неправильно заданы параметры',
        '401': 'Для доступа к адресам требуется авторизация',
        '403': 'Для доступа к адресам требуются права администратора',
        '404': 'По данному идентификатору адрес не найден',
        '500': 'Произошла пробелема при выполнении запроса к БД'
    },
    'dictSchema': {
        'GET_AddressSchema': GET_AddressSchema,
        'ID_AddressSchema': ID_AddressSchema,
        'POST_AddressSchema': POST_AddressSchema,
        'Data_AddressSchema': Data_AddressSchema,
        'Table_AddressSchema': Table_AddressSchema,
        'PATCH_AddressSchema': PATCH_AddressSchema,
        'LIST_AddressSchema': LIST_AddressSchema
    }         
}