from app.database import db
from dataclasses import dataclass

from app.api_v1 import (
    API_V1_ValidationException, 
    check_arg_list,
    convert_arg
)


@dataclass
class Section(db.Model):
    id: int
    name: str

    __tablename__ = 'section'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)

    categories = db.relationship('Category', backref='section')

    def __str__(self):
        return self.name
        
    def validate_args(IsNotNone=True):
        # Проверка на соотвествие аргументам
        arg_list = ['name']
        if IsNotNone:
            arg_list += ['id']
        check_arg_list(arg_list)
        
        # Проверки на тип
        id = convert_arg('id', int, IsNotNone)
        name = convert_arg('name', str, IsNotNone)

        # Проверки на значения
        if id and id < 0:
            msg = 'Id must be should be a positive number'
            raise API_V1_ValidationException(msg)
                
        if name:      
            if len(name.strip()) == 0:
                msg = 'Name must not be empty'
                raise API_V1_ValidationException(msg)
                
            if len(name) > 32:
                msg = f'Name must exceed 32 characters'
                raise API_V1_ValidationException(msg)