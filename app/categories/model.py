from app.database import db
from dataclasses import dataclass

from app.api_v1 import (
    API_V1_ValidationException, 
    check_arg_list,
    check_unumber,
    check_string,
    convert_arg
)


@dataclass
class Category(db.Model):
    id: int
    name: str
    section_id: int

    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    products = db.relationship('Product', backref='category')

    def __str__(self):
        return self.name
        
    def validate_args(IsNotNone=True):
        # Проверка на соотвествие аргументам
        arg_list = ['name', 'section_id']
        check_arg_list(arg_list)
        
        # Проверки на тип
        id = convert_arg('id', int)
        name = convert_arg('name', str, IsNotNone)
        section_id = convert_arg('section_id', int, IsNotNone)

        # Проверки на значения
        check_unumber(id, 'id')
        check_string(name, 64, 'name')
        check_unumber(section_id, 'section_id')