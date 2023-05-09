from spyne import (
    Unicode,
    Integer,
    Float,
    DateTime,
    Array,
    ComplexModel
)
    
from app.database import db

NAMESPACE = 'orders'


class Product(ComplexModel):
    __namespace__ = NAMESPACE
    id = Integer(nullable=False, min_occurs=1, ge=1)
    cost = Float(nullable=False, min_occurs=1, ge=0)
    count = Integer(nullable=False, min_occurs=1, ge=0)


class ProductInfo(Product):
    __nameclass__ = 'Product'
    name = Unicode()


class OrderItem(ComplexModel):
    __namespace__ = NAMESPACE
    id = Integer()
    status = Unicode()


class OrderList(ComplexModel):
    __namespace__ = NAMESPACE
    list = Array(OrderItem)
    limit = Integer()
    offset = Integer()
    total = Integer()


class OrderInfo(ComplexModel):
    __namespace__ = NAMESPACE
    id = Integer()
    phone = Unicode()
    email = Unicode()
    status = Unicode()
    receipt = Unicode()
    date_order = DateTime()
    date_assembly = DateTime()
    date_dispatch = DateTime()
    date_receive = DateTime()
    date_complete = DateTime()
    address_id = Integer()
    city = Unicode()
    address = Unicode()
    products = Array(ProductInfo)


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


IdInt = Integer(nullable=False, min_occurs=1, ge=1)


ReasonString = Unicode(256,
        type_name='ReasonString',
        nullable=False,
        min_occurs=1,
        min_len=1,
        max_len=256
    )


status = {
    'CR': 'Created',     # Заказ создан
    'RT': 'Returned',    # Заказ возвращён
    'CA': 'Canceled',    # Заказ отменён
    'AS': 'Assembled',   # Заказ собран 
    'DI': 'Dispatched',  # Заказ отправлен в салон связи
    'RC': 'Received',    # Заказ прибыл в салон связи
    'CO': 'Completed'    # Заказ завершён   
}
l = [[k, v] for k, v in status.items()] 
enums = [a for b in l for a in b]   # Список чередует key и value
StatusEnum = Unicode(values=enums[4:], type_name="SomeEnum")


def get_full_status(key):
    if len(key) > 2:
        return key
    return status[key]


def get_reduced_status(value):
    for k, v in status.items():
        if v == value:
            return k
    return value


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(2), nullable=True)
    receipt = db.Column(db.String(256), nullable=True)
    date_order = db.Column(db.DateTime, nullable=False)
    date_assembly = db.Column(db.DateTime, nullable=True)
    date_dispatch = db.Column(db.DateTime, nullable=True)
    date_receive = db.Column(db.DateTime, nullable=True)
    date_complete = db.Column(db.DateTime, nullable=True)
    
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

    
class ReturnedProduct(db.Model):
    __tablename__ = 'returnedproduct'
    
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'),
        primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),
        primary_key=True)
    date_return = db.Column(db.DateTime, primary_key=True)
    cost = db.Column(db.Float(), nullable=False)
    count = db.Column(db.Integer(), nullable=False)    
    reason = db.Column(db.String(256), nullable=False)