from flask import request

from .model import Category, db
from app.api.api_v1 import (
    convert_arg,
    API_V1,
    API_V1_ValidationException
)    


class Category_API_V1(API_V1):
    def __init__(self):
        super().__init__('categories', Category)
        
    def get(self, limit, offset):      
        res, code = super().get(limit, offset)
        for c in res['data']:
            c.productCount = len(c.products)
        return res, code
        
api_v1 = Category_API_V1()