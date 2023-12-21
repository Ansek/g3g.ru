from app.database import db
from dataclasses import dataclass

from app.api.api_v1 import ( 
    check_arg_list,
    check_unumber,
    check_string,
    convert_arg
)


@dataclass
class Category(db.Model):
    id: int
    name: str
    productCount: int = 0
    
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    
    products = db.relationship('Product', backref='category', passive_deletes='all')

    def __str__(self):
        return self.name
        
    def validate_args(args, IsNotNone=True):
        # Проверка на соотвествие аргументам
        arg_list = ['name']
        check_arg_list(args, arg_list)
        
        # Проверки на тип
        id = convert_arg(args, 'id', int)
        name = convert_arg(args, 'name', str, IsNotNone)

        # Проверки на значения
        check_unumber(id, 'id')
        check_string(name, 64, 'name')