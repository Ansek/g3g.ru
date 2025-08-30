import copy
from marshmallow import Schema, fields, validate


_limit = fields.Int(
    description="Ограничие на количество в списке товаров",
    required=False,
    example=10,
    validate=validate.Range(min=0))
    
_offset = fields.Int(
    description="Смещение в списке товаров",
    required=False,
    example=5,
    validate=validate.Range(min=0))
    
_geCost = fields.Int(
    description="Стоимость товара больше или равно чем geCost",
    required=False,
    example=10000)
    
_leCost = fields.Int(
    description="Стоимость товара меньше или равно чем leCost",
    required=False,
    example=20000)
    
_category = fields.Int(
    description="Идентификатор категории",
    required=False,
    example=1)
    
_id = fields.Int(
    description="Идентификатор товара",
    required=True,
    example=1)
    
_name = fields.Str(
    description="Название товара (unique)",
    required=True,
    example='Lenovo K900',
    validate=validate.Length(max=128))
    
_cost = fields.Float(
    description="Стоимость товара",
    required=True,
    example=16000.0,
    validate=validate.Range(min=0))
    
_count = fields.Int(
    description="Количество в наличии",
    required=True,
    example=20,
    validate=validate.Range(min=0))
    
_img_path = fields.Str(
    description="Изображение товара",
    required=True,
    example='img/smartphone/sm1-1.png',
    validate=validate.Length(max=256))
    
_category_id = fields.Int(
    description="Идентификатор категории",
    required=True,
    example=1,
    validate=validate.Range(min=1))
    
_total = fields.Int(
    description="Количество товаров, для которых выполняются условия",
    required=False,
    example=5,
    validate=validate.Range(min=0))
    
    
class GET_ProductSchema(Schema):
    limit = _limit
    offset = _offset
    geCost = _geCost
    leCost = _leCost
    category = _category

   
class ID_ProductSchema(Schema):
    id = _id


class POST_ProductSchema(Schema):
    name = _name
    cost = _cost
    count = _count
    img_path = _img_path
    category_id = _category_id


class Data_ProductSchema(Schema):
    id = _id
    name = _name
    cost = _cost
    count = _count
    img_path = _img_path
    category_id = _category_id


class Table_ProductSchema(Schema):
    data = fields.Nested(Data_ProductSchema())
    total = _total


class PATCH_ProductSchema(Schema):
    id = _id
    name = copy.deepcopy(_name)
    cost = copy.deepcopy(_cost)
    count = copy.deepcopy(_count)
    img_path = copy.deepcopy(_img_path)
    category_id = copy.deepcopy(_category_id)
    name.required = False
    cost.required = False
    count.required = False
    img_path.required = False
    category_id.required = False


class LIST_ProductSchema(Schema):
    data = fields.List(fields.Nested(Data_ProductSchema()))
    limit = _limit
    offset = _offset
    total = _total

class Cost_ProductSchema(Schema):
    count = copy.deepcopy(_count)
    count.example=3
    count.required = True


class CountError400Schema(Schema):
     message = fields.String(
         description="Сообщение об ошибке",
         required=True,
         example='Сount cannot be a negative number. count = -1')
    
api_docs = {
    'tags': {
        'name': 'Product',
        'description': 'Информация о товарах'
    },
    'get': {
        'summary': 'Возвращает список товаров',
        '200': 'Выводится список товаров',
        '404': 'По данному запросу список товаров пуст',
        'inputSchema': 'GET_ProductSchema',
        'ouputSchema': 'LIST_ProductSchema'
    }, 
    'get_id': {
        'summary': 'Возвращает товар по идентификатору',
        '200': 'Выводится информация о товаре',
        'inputSchema': 'ID_ProductSchema',
        'ouputSchema': 'Table_ProductSchema'
    }, 
    'post': {
        'summary': 'Добавляет информацию о товаре',
        '201': 'Выводится информация о товаре с новым идентификатом',
        'inputSchema': 'POST_ProductSchema',
        'ouputSchema': 'Table_ProductSchema'
    },
    'put': {
        'summary': 'Изменяет информацию о товаре целиком',
        '200': 'Выводится информация о товаре с новыми данными',
        'inputSchema': 'Data_ProductSchema',
        'ouputSchema': 'Table_ProductSchema'
    },
    'patch': {
        'summary': 'Изменяет информацию о товаре по указанным полям',
        '200': 'Выводится информация о товаре с новыми данными',
        'inputSchema': 'PATCH_ProductSchema',
        'ouputSchema': 'Table_ProductSchema'
    },
    'delete': {
        'summary': 'Удаляет информацию о товаре',
        '200': 'Количество оставшихся данных',
        'inputSchema': 'ID_ProductSchema'
    },
    'errors': {
        '400': 'Неправильно заданы параметры',
        '401': 'Для доступа к товарам требуется авторизация',
        '403': 'Для доступа к товарам требуются права администратора',
        '404': 'По данному идентификатору товар не найден',
        '500': 'Произошла пробелема при выполнении запроса к БД'
    },  
    'dictSchema': {
        'GET_ProductSchema': GET_ProductSchema,
        'ID_ProductSchema': ID_ProductSchema,
        'POST_ProductSchema': POST_ProductSchema,
        'Data_ProductSchema': Data_ProductSchema,
        'Table_ProductSchema': Table_ProductSchema,
        'PATCH_ProductSchema': PATCH_ProductSchema,
        'LIST_ProductSchema': LIST_ProductSchema,
        'Cost_ProductSchema': Cost_ProductSchema
    }         
}