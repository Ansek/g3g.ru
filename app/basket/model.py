from spyne import (
    Unicode,
    Integer,
    Float,
    ComplexModel
)
    
from app.database import db


class Product(ComplexModel):
    __namespace__ = 'bascket'
    id = Integer(nullable=False, min_occurs=1, ge=1)
    cost = Float(nullable=False, min_occurs=1, ge=0)
    count = Integer(nullable=False, min_occurs=1, ge=0)
    
    
PhoneString = Unicode(10,
        pattern='\d{10}',
        type_name='PhoneString',
        nullable=False,
        min_occurs=1,
        max_len=10
    )
    
EmailString = Unicode(256,
        pattern='[^@]+@[^@]+',
        type_name='EmailString',
        nullable=False,
        min_occurs=1,
        min_len=5,
        max_len=256
    )
    
    
AddressInt = Integer(nullable=False, min_occurs=1, ge=1)


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(256), nullable=True)
    date_order = db.Column(db.DateTime, nullable=False)
    date_build = db.Column(db.DateTime, nullable=True)
    date_dispatch = db.Column(db.DateTime, nullable=True)
    date_receipt = db.Column(db.DateTime, nullable=True)
    date_payment = db.Column(db.DateTime, nullable=True)
    date_complet = db.Column(db.DateTime, nullable=True)
    
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    products = db.relationship('Order_Product', backref='order') 


class Order_Product(db.Model):
    __tablename__ = 'order_product'
    
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'),
        primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),
        primary_key=True)
    cost = db.Column(db.Float(), nullable=False)
    count = db.Column(db.Integer(), nullable=False)