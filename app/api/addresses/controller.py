from marshmallow import Schema, fields, validate

from .model import Address, db
from app.api.api_v1 import API_V1


class AddressGETSchema(Schema):
    limit = fields.Int(description="Ограничие на количество в списке адресов", required=False, example=10, validate=validate.Range(min=0))
    offset = fields.Int(description="Смещение в списке адресов", required=False, example=5, validate=validate.Range(min=0))

class AddressTableSchema(Schema):
    address = fields.Str(description="Адрес (unique)", required=True, example='ул. Котова, д. 5', validate=validate.Length(max=128))
    city = fields.Str(description="Город", required=True, example='Санкт-Петербург', validate=validate.Length(max=128))
    img_path = fields.Str(description="Карта (unique)", required=True, example='img/map/addr1.png', validate=validate.Length(max=256))
    
    
class AddressIdSchema(Schema):
    id = fields.Int(description="Идентификатор адреса", required=True, example=5)
    
    
api_docs = {
    'tags': {
        'name': 'Address',
        'description': 'Информация об адресах салона связи'
    },
    'get': {
        'summary': 'Возвращает список адресов',
        '200': 'Выводится список адресов',
        '404': 'По данному запросу список адресов пуст'
    }, 
    'get_id': {
        'summary': 'Возвращает адрес по идентификатору',
        '200': 'Выводится информация об адресе'
    }, 
    'post': {
        'summary': 'Добавляет информацию об адресе',
        '201': 'Выводится информация об адресе с новым идентификатом'
    },
    'put': {
        'summary': 'Изменяет информацию об адресе целиком',
        '200': 'Выводится информация об адресе с новыми данными'
    },
    'patch': {
        'summary': 'Изменяет информацию об адресе по указанным полям',
        '200': 'Выводится информация об адресе с новыми данными'
    },
    'delete': {
        'summary': 'Удаляет информацию об адресе',
        '204': 'Ничего не возращает'
    },
    'errors': {
        '404': 'По данному идентификатору адрес не найден',
        '400': 'Неправильно заданы параметры',
        '500': 'Произошла пробелема при выполнении запроса к БД'
    },
    'schema': {
        'get': 'AddressGETSchema',
        'id': 'AddressIdSchema',
        'table': 'AddressTableSchema'
    },  
    'dictSchema': {
        'AddressGETSchema': AddressGETSchema,
        'AddressIdSchema': AddressIdSchema,
        'AddressTableSchema': AddressTableSchema
    }         
}


api_v1 = API_V1('addresses', Address, api_docs)