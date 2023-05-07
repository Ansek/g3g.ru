from app.database import db
from dataclasses import dataclass

from app.api_v1 import (
    API_V1_ValidationException, 
    check_arg_list,
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
        if IsNotNone:
            arg_list += ['id']
        check_arg_list(arg_list)
        
        # Проверки на тип
        id = convert_arg('id', int)
        address = convert_arg('address', str, IsNotNone)
        city = convert_arg('address', str, IsNotNone)
        img_path = convert_arg('img_path', str, IsNotNone)

        # Проверки на значения
        if id and id < 0:
            msg = 'Id must be should be a positive number'
            raise API_V1_ValidationException(msg)
        
        if address:  
            if len(address.strip()) == 0:
                msg = 'Address must not be empty'
                raise API_V1_ValidationException(msg)
                
            if len(address) > 128:
                msg = f'Address must exceed 128 characters'
                raise API_V1_ValidationException(msg)

        if city:  
            if len(city.strip()) == 0:
                msg = 'City must not be empty'
                raise API_V1_ValidationException(msg)
                
            if len(city) > 64:
                msg = f'City must exceed 64 characters'
                raise API_V1_ValidationException(msg)
                
        if img_path:  
            if len(img_path.strip()) == 0:
                msg = 'img_path must not be empty'
                raise API_V1_ValidationException(msg)
                
            if len(img_path) > 256:
                msg = f'img_path  must exceed 256 characters'
                raise API_V1_ValidationException(msg)