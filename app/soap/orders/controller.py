from spyne import (
    Unicode,
    UnsignedShort,
    Array,
    Boolean,
    Application,
    ServiceBase,
    rpc
)
from sqlalchemy.exc import SQLAlchemyError
from spyne.protocol.soap import Soap11
from datetime import datetime

from .model import (
    get_full_status,
    get_reduced_status,
    Product as SOAP_Product,
    ProductInfo,
    PhoneString,
    EmailString,
    ReasonString,
    IdInt,
    StatusEnum,
    OrderItem,
    OrderList,
    OrderInfo,
    Order,
    Order_Product,
    ReturnedProduct,
    db
)
from .faults import  (
    SoapDBError,
    SoapOrderNotFound,
    SoapProductNotFound,
    SoapStatusAssignmentError,
    SoapStatusAlreadySetError,
    SoapNotEnoughProducts
)
from app.api.addresses.model import Address
from app.api.products.model import Product

class OrderService(ServiceBase):
    @rpc(PhoneString, EmailString, IdInt, Array(SOAP_Product),
        _returns=OrderItem)
    def CreateOrder(ctx, phone, email, address_id, products):
        with ctx.udc.context:
            try:
                order = Order(
                    phone=phone,
                    email=email,
                    address_id=address_id,
                    status=get_reduced_status('Created'),
                    date_order = datetime.now()
                )
                db.session.add(order)
                db.session.flush()
                for p in products:
                    # Изменение количества товара
                    dbp = Product.query.get(p.id)
                    if dbp is None:
                        db.session.rollback()
                        raise SoapProductNotFound(p.id)
                    new_count = dbp.count - p.count
                    if new_count < 0:
                        db.session.rollback()
                        raise SoapNotEnoughProducts(
                            dbp.id,
                            dbp.name,
                            p.count,
                            dbp.count
                        )
                    dbp.count = new_count
                    # Добавление торара к заказу
                    op = Order_Product(
                        order_id = order.id,
                        product_id = p.id,
                        cost = p.cost,
                        count = p.count
                    )
                    db.session.add(op) 
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                raise SoapDBError(e)
            status = get_full_status(order.status)
            return OrderItem(id=order.id, status=status)
        
    @rpc(IdInt, StatusEnum, _returns=OrderItem)
    def ChangeOrderStatus(ctx, id, status):
        status = get_full_status(status)
        with ctx.udc.context:
            try:
                order = Order.query.get(id)
                if order is None:
                    raise SoapOrderNotFound(id)
                if get_full_status(order.status) == status:
                    raise SoapStatusAlreadySetError(status)
                if status == 'Assembled':
                    if get_full_status(order.status) != 'Created':
                        raise SoapStatusAssignmentError(status, 'Created')
                    order.date_assembly = datetime.now()
                elif status == 'Dispatched':
                    if get_full_status(order.status) != 'Assembled':
                        raise SoapStatusAssignmentError(status, 'Assembled')
                    order.date_dispatch = datetime.now()
                elif status == 'Received':
                    order.date_receive = datetime.now()
                else:
                    if get_full_status(status) == 'Canceled':
                        # Получение информации о товарах заказа
                        op = Order_Product.query.\
                            filter(Order_Product.order_id==id)
                        # Возврат количества товаров
                        for p in op:
                            dbp = Product.query.get(p.product_id)
                            dbp.count += p.count                            
                    order.date_complete = datetime.now()
                order.status = get_reduced_status(status)
                db.session.commit()                                    
            except SQLAlchemyError as e:
                raise SoapDBError(e)
            return OrderItem(id=order.id, status=status)

    @rpc(UnsignedShort, UnsignedShort, Boolean, _returns=OrderList)
    def GetOrderList(ctx, limit, offset, not_completed):
        res = []
        with ctx.udc.context:
            try:
                if limit is None:
                    limit = ctx.udc.config['SOAP_LIMIT']
                if offset is None:
                    offset = 0
                query = Order.query
                if not_completed == True:
                    query = query.filter(Order.date_complete.is_(None))
                total = query.count()
                orders = query.limit(limit).offset(offset).all()
                for order in orders:
                    oi = OrderItem(
                        id=order.id,
                        status=get_full_status(order.status)
                    )
                    res.append(oi)
            except SQLAlchemyError as e:
                raise SoapDBError(e)
            return OrderList(
                list=res,
                limit=limit,
                offset=offset,
                total=total
            )

    @rpc(IdInt, _returns=OrderInfo)
    def GetOrderById(ctx, id):
        with ctx.udc.context:
            try:
                order = Order.query.get(id)
                if order is None:
                    raise SoapOrderNotFound(id)
                products = []
                for p in order.products:
                    dbp = Product.query.get(p.product_id)
                    products.append(ProductInfo(
                            id=p.product_id,
                            cost=p.cost,
                            count=p.count,
                            name=dbp.name
                        )
                    )
                addr = Address.query.get(order.address_id)
            except SQLAlchemyError as e:
                raise SoapDBError(e)
            return OrderInfo(
                id=order.id,
                phone=order.phone,
                email=order.email,
                status=get_full_status(order.status),
                receipt=order.receipt,
                date_order=order.date_order,
                date_assembly=order.date_assembly,
                date_dispatch=order.date_dispatch,
                date_receive=order.date_receive,
                date_complete=order.date_complete,
                address_id=order.address_id,
                city=addr.city,
                address=addr.address,
                products=products
            )
            
    @rpc(IdInt, IdInt, IdInt, ReasonString, _returns=OrderItem)
    def ReturnProduct(ctx, id, product_id, count, reason):
        with ctx.udc.context:
            try:
                order = Order.query.get(id)
                if order is None:
                    raise SoapOrderNotFound(id)
                # Получение информации о товаре
                op = Order_Product.query.filter(
                        Order_Product.order_id==id,
                        Order_Product.product_id==product_id
                    ).first()
                dbp = Product.query.get(product_id)
                if op is None or dbp is None:
                    db.session.rollback()
                    raise SoapProductNotFound(product_id, id)
                new_count = op.count - count 
                if new_count < 0:
                    db.session.rollback()
                    raise SoapNotEnoughProducts(
                        dbp.id,
                        dbp.name,
                        count,
                        op.count
                    )
                # Перенос товара в другую таблицу
                rp = ReturnedProduct(
                    order_id=order.id,
                    product_id=op.product_id,
                    cost=op.cost,
                    count=count,
                    date_return=datetime.now(),
                    reason=reason
                )
                db.session.add(rp)
                # Проверка был ли полностью возращен товар
                if new_count == 0:
                    db.session.delete(op)
                else:
                    op.count = new_count
                # Проверка был ли полностью возращен заказ 
                lst = Order_Product.query.\
                    filter(Order_Product.order_id==order.id).count()
                if lst == 0:
                    order.status = get_reduced_status('Returned')
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                raise SoapDBError(e)
            status=get_full_status(order.status)
            return OrderItem(id=order.id, status=status)


class UserDefinedContext(object):
    def __init__(self, app):
        self.context = app.app_context()
        self.config = app.config


def create_soap(app):
    application = Application(
        [OrderService],
        tns='orders',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )
    
    def _flask_context(ctx):
        ctx.udc = UserDefinedContext(app)
    application.event_manager.add_listener('method_call', _flask_context)
    
    return application