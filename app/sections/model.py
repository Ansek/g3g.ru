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
        check_arg_list(arg_list)
        
        # Проверки на тип
        id = convert_arg('id', int)
        name = convert_arg('name', str, IsNotNone)

        # Проверки на значения
        check_unumber(id, 'id')
        check_string(name, 32, 'name')