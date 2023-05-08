from flask import (
    Blueprint,
    render_template,
    current_app
)
from spyne import (
    Unicode,
    Array,
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
    Product,
    PhoneString,
    EmailString,
    IdInt,
    StatusEnum,
    Order,
    Order_Product,
    db
)
from .faults import  (
    SoapDBError,
    SoapOrderNotFound,
    SoapStatusAssignmentError
)

module = Blueprint('basket', __name__,
    template_folder='templates', url_prefix='/basket')


@module.route('/', methods=['GET'])
def index():
    return render_template('basket/index.html')


class OrderService(ServiceBase):
    @rpc(PhoneString, EmailString, IdInt, Array(Product),
        _returns=Unicode)
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
            return f'Order #{order.id} successfully created'
        
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
        return f'Order status #{id} successfully changed to ' +\
            get_full_status(status)


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