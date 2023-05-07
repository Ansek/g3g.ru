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
    Product,
    PhoneString,
    EmailString,
    AddressInt,
    Order,
    Order_Product,
    db
)

module = Blueprint('basket', __name__,
    template_folder='templates', url_prefix='/basket')

@module.route('/', methods=['GET'])
def index():
    return render_template('basket/index.html')


class OrderService(ServiceBase):
    @rpc(PhoneString, EmailString, AddressInt, Array(Product),
        _returns=Unicode)
    def CreateOrder(ctx, phone, email, address_id, products):
        with ctx.udc.context:
            try:
                order = Order(
                    phone=phone,
                    email=email,
                    address_id=address_id,
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
                return str(e)
        return 'Order successfully created'


class UserDefinedContext(object):
    def __init__(self, app):
        self.context = app.app_context()


def create_soap(app):
    application = Application(
        [OrderService],
        tns='bascket',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11(),
    )
    
    def _flask_context(ctx):
        ctx.udc = UserDefinedContext(app)
    application.event_manager.add_listener('method_call', _flask_context)
    
    return application