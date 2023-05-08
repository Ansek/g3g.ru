from flask import (
    Blueprint,
    render_template,
    current_app
)
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
    IdInt,
    StatusEnum,
    OrderItem,
    OrderList,
    OrderInfo,
    Order,
    Order_Product,
    db
)
from .faults import  (
    SoapDBError,
    SoapOrderNotFound,
    SoapStatusAssignmentError,
    SoapNotEnoughProducts
)
from app.addresses.model import Address
from app.products.model import Product

module = Blueprint('basket', __name__,
    template_folder='templates', url_prefix='/basket')


@module.route('/', methods=['GET'])
def index():
    return render_template('basket/index.html')


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
                raise SoapDBError(e)
            status = get_full_status(order.status)
            return OrderItem(id=order.id, status=status)
        
    @rpc(IdInt, StatusEnum, _returns=Unicode)
    def ChangeOrderStatus(ctx, id, status):
        status = get_full_status(status)
        with ctx.udc.context:
            try:
                order = Order.query.get(id)
                if order is None:
                    raise SoapOrderNotFound(id)
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
            if limit is None:
                limit = current_app.config['SOAP_LIMIT']
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
            return OrderList(
                list=res,
                limit=limit,
                offset=offset,
                total=total
            )

    @rpc(IdInt, _returns=OrderInfo)
    def GetOrderById(ctx, id):
        with ctx.udc.context:
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
            
        

class UserDefinedContext(object):
    def __init__(self, app):
        self.context = app.app_context()


def create_soap(app):
    application = Application(
        [OrderService],
        tns='order',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11(),
    )
    
    def _flask_context(ctx):
        ctx.udc = UserDefinedContext(app)
    application.event_manager.add_listener('method_call', _flask_context)
    
    return application