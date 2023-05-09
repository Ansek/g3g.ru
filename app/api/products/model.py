from app.database import db
from dataclasses import dataclass

from app.api.api_v1 import (
    API_V1_ValidationException, 
    check_arg_list,
    check_unumber,
    check_string,
    convert_arg
)


@dataclass
class Product(db.Model):
    id: int
    name: str
    cost: float
    count: int
    img_path: str
    category_id: int

    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    cost = db.Column(db.Float, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    img_path = db.Column(db.String(256), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __str__(self):
        return self.name
        
    def validate_args(IsNotNone=True):
        # Проверка на соотвествие аргументам
        arg_list = ['name', 'cost', 'count', 'img_path', 'category_id']
        check_arg_list(arg_list)
        
        # Проверки на тип
        id = convert_arg('id', int)
        name = convert_arg('name', str, IsNotNone)
        cost = convert_arg('cost', float, IsNotNone)
        count = convert_arg('count', int, IsNotNone)
        img_path = convert_arg('img_path', str, IsNotNone)
        category_id = convert_arg('category_id', int, IsNotNone)
        
        # Проверки на значения
        check_unumber(id, 'id')
        check_string(name, 128, 'name')
        check_unumber(cost, 'cost')
        check_unumber(count, 'count')
        check_string(img_path, 256, 'img_path')
        check_unumber(category_id, 'category_id')