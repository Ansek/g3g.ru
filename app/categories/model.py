from app.database import db
from dataclasses import dataclass

from app.api_v1 import (
    API_V1_ValidationException, 
    check_arg_list,
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
        if IsNotNone:
            arg_list += ['id']
        check_arg_list(arg_list)
        
        # Проверки на тип
        id = convert_arg('id', int, IsNotNone)
        name = convert_arg('name', str, IsNotNone)
        section_id = convert_arg('section_id', int, IsNotNone)

        # Проверки на значения
        if id and id < 0:
            msg = 'Id must be should be a positive number'
            raise API_V1_ValidationException(msg)
        
        if name:  
            if len(name.strip()) == 0:
                msg = 'Name must not be empty'
                raise API_V1_ValidationException(msg)
                
            if len(name) > 64:
                msg = f'Name must exceed 64 characters'
                raise API_V1_ValidationException(msg)
            
        if section_id and section_id < 0:
            msg = 'Section id must be should be a positive number'
            raise API_V1_ValidationException(msg)