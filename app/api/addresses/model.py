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
class Address(db.Model):
    id: int
    address: str
    city: str
    img_path: str

    __tablename__ = 'address'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(128), nullable=False, unique=True)
    city =  db.Column(db.String(64), nullable=False)
    img_path = db.Column(db.String(256), nullable=False, unique=True) 

    def __str__(self):
        return self.address
        
    def validate_args(IsNotNone=True):
        # Проверка на соотвествие аргументам
        arg_list = ['address', 'city', 'img_path']
        check_arg_list(arg_list)
        
        # Проверки на тип
        id = convert_arg('id', int)
        address = convert_arg('address', str, IsNotNone)
        city = convert_arg('address', str, IsNotNone)
        img_path = convert_arg('img_path', str, IsNotNone)

        # Проверки на значения
        check_unumber(id, 'id')
        check_string(address, 128, 'address')
        check_string(city, 64, 'city')
        check_string(img_path, 256, 'img_path')