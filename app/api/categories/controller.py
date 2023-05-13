from flask import request
from marshmallow import Schema, fields, validate

from .model import Category, db
from app.api.api_v1 import (
    convert_arg,
    API_V1,
    API_V1_ValidationException
)    


class CategoryGETSchema(Schema):
    limit = fields.Int(description="Ограничие на количество в списке категорий", required=False, example=10, validate=validate.Range(min=0))
    offset = fields.Int(description="Смещение в списке категорий", required=False, example=5, validate=validate.Range(min=0))


class CategoryTableSchema(Schema):
    name = fields.Str(description="Название категории (unique)", required=True, example='Смартфоны', validate=validate.Length(max=64))


class CategoryIdSchema(Schema):
    id = fields.Int(description="Идентификатор категории", required=True, example=5)


api_docs = {
    'tags': {
        'name': 'Category',
        'description': 'Информация о категории товаров'
    },
    'get': {
        'summary': 'Возвращает список категорий',
        '200': 'Выводится список категорий',
        '404': 'По данному запросу список категорий пуст'
    }, 
    'get_id': {
        'summary': 'Возвращает категорию по идентификатору',
        '200': 'Выводится информация о категории'
    }, 
    'post': {
        'summary': 'Добавляет информацию о категории',
        '201': 'Выводится информация о категории с новым идентификатом'
    },
    'put': {
        'summary': 'Изменяет информацию о категории целиком',
        '200': 'Выводится информация о категории с новыми данными'
    },
    'patch': {
        'summary': 'Изменяет информацию о категории по указанным полям',
        '200': 'Выводится информация о категории с новыми данными'
    },
    'delete': {
        'summary': 'Удаляет информацию о категории',
        '204': 'Ничего не возращает'
    },
    'errors': {
        '404': 'По данному идентификатору категория не найдена',
        '400': 'Неправильно заданы параметры',
        '500': 'Произошла пробелема при выполнении запроса к БД'
    },
    'schema': {
        'get': 'CategoryGETSchema',
        'id': 'CategoryIdSchema',
        'table': 'CategoryTableSchema'
    },  
    'dictSchema': {
        'CategoryGETSchema': CategoryGETSchema,
        'CategoryIdSchema': CategoryIdSchema,
        'CategoryTableSchema': CategoryTableSchema
    }         
}


class Category_API_V1(API_V1):
    def __init__(self):
        super().__init__('categories', Category, api_docs)
        
    def get(self, limit, offset):      
        res, code = super().get(limit, offset)
        for c in res['data']:
            c.CategoryCount = len(c.products)
        return res, code
        
api_v1 = Category_API_V1()