from app.database import db
from dataclasses import dataclass

from app.api_v1 import API_V1_ValidationException, convert_arg

@dataclass
class Product(db.Model):
    id: int
    name: str
    cost: float
    img_path: str
    category_id: int

    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    cost = db.Column(db.Float, nullable=False)
    img_path = db.Column(db.String(256), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __str__(self):
        return self.name
        
    def validate_args():
        id = convert_arg('id', int, IsNotNone=True)
        name = convert_arg('name', str, 'str', IsNotNone=True)
        cost = convert_arg('cost', float, 'float', IsNotNone=True)
        img_path = convert_arg('img_path', str, 'str', IsNotNone=True)
        category_id = convert_arg('category_id', int, IsNotNone=True)
        
        if id < 0:
            msg = 'Id must be should be a positive number'
            raise API_V1_ValidationException(msg)
              
        if len(name.strip()) == 0:
            msg = 'Name must not be empty'
            raise API_V1_ValidationException(msg)
            
        if len(name) > 128:
            msg = f'Name must exceed 128 characters'
            raise API_V1_ValidationException(msg)
            
        if cost < 0:
            msg = 'Cost must be should be a positive number'
            raise API_V1_ValidationException(msg)
            
        if len(img_path.strip()) == 0:
            msg = 'Image path must not be empty'
            raise API_V1_ValidationException(msg)
            
        if len(img_path) > 256:
            msg = f'Image path must exceed 256 characters'
            raise API_V1_ValidationException(msg)
            
        if category_id < 0:
            msg = 'Category id must be should be a positive number'
            raise API_V1_ValidationException(msg)