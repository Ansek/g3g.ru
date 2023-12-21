import copy
from marshmallow import Schema, fields, validate


_limit = fields.Int(
    description="Ограничие на количество в списке категорий",
    required=False,
    example=10,
    validate=validate.Range(min=0))
    
_offset = fields.Int(
    description="Смещение в списке категорий",
    required=False,
    example=5,
    validate=validate.Range(min=0))

_id = fields.Int(
    description="Идентификатор категории",
    required=True,
    example=5)
    
_name = fields.Str(
    description="Название категории (unique)",
    required=True,
    example='Смартфоны',
    validate=validate.Length(max=64))
    
_productCount = fields.Int(
    description="Количество товаров в данной категории",
    required=True,
    example=20,
    validate=validate.Range(min=0))
    
_total = fields.Int(
    description="Количество категорий, для которых выполняются условия",
    required=False,
    example=5,
    validate=validate.Range(min=0))


class GET_CategorySchema(Schema):
    limit = _limit
    offset = _offset


class ID_CategorySchema(Schema):
    id = _id


class POST_CategorySchema(Schema):
    name = _name


class Data_CategorySchema(Schema):
    id = _id
    name = _name


class Table_CategorySchema(Schema):
    data = fields.Nested(Data_CategorySchema())
    total = _total


class PATCH_CategorySchema(Schema):
    id = _id
    name = copy.deepcopy(_name)
    name.required = False

        
class GET_Table_CategorySchema(Schema):
    id = _id
    name = _name
    productCount = _productCount
 

class LIST_CategorySchema(Schema):
    data = fields.List(fields.Nested(Data_CategorySchema()))
    limit = _limit
    offset = _offset
    total = _total
    

api_docs = {
    'tags': {
        'name': 'Category',
        'description': 'Информация о категории товаров'
    },
    'get': {
        'summary': 'Возвращает список категорий',
        '200': 'Выводится список категорий',
        '404': 'По данному запросу список категорий пуст',
        'inputSchema': 'GET_CategorySchema',
        'ouputSchema': 'LIST_CategorySchema'
    }, 
    'get_id': {
        'summary': 'Возвращает категорию по идентификатору',
        '200': 'Выводится информация о категории',
        'inputSchema': 'ID_CategorySchema',
        'ouputSchema': 'Table_CategorySchema'
    }, 
    'post': {
        'summary': 'Добавляет информацию о категории',
        '201': 'Выводится информация о категории с новым идентификатом',
        'inputSchema': 'POST_CategorySchema',
        'ouputSchema': 'Table_CategorySchema'
    },
    'put': {
        'summary': 'Изменяет информацию о категории целиком',
        '200': 'Выводится информация о категории с новыми данными',
        'inputSchema': 'Data_CategorySchema',
        'ouputSchema': 'Table_CategorySchema'
    },
    'patch': {
        'summary': 'Изменяет информацию о категории по указанным полям',
        '200': 'Выводится информация о категории с новыми данными',
        'inputSchema': 'PATCH_CategorySchema',
        'ouputSchema': 'Table_CategorySchema'
    },
    'delete': {
        'summary': 'Удаляет информацию о категории',
        '200': 'Количество оставшихся данных',
        'inputSchema': 'ID_CategorySchema'
    },
    'errors': {
        '400': 'Неправильно заданы параметры',
        '401': 'Для доступа к категориям требуется авторизация',
        '403': 'Для доступа к категориям требуются права администратора',
        '404': 'По данному идентификатору категория не найдена',
        '500': 'Произошла пробелема при выполнении запроса к БД'
    },
    'dictSchema': {
        'GET_CategorySchema': GET_CategorySchema,
        'ID_CategorySchema': ID_CategorySchema,
        'POST_CategorySchema': POST_CategorySchema,
        'Data_CategorySchema': Data_CategorySchema,
        'Table_CategorySchema': Table_CategorySchema,
        'PATCH_CategorySchema': PATCH_CategorySchema,
        'LIST_CategorySchema': LIST_CategorySchema
    }        
}