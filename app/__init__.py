import os
from flask import Flask, Blueprint
from spyne.server.wsgi import WsgiApplication
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from .database import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    if app.debug == True:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)
        except:
            pass

    import app.api.addresses.controller as addresses
    import app.api.categories.controller as categories
    import app.api.products.controller as products
    import app.basket.controller as basket
    import app.controller as general
    import app.soap.orders.controller as orders

    app.register_blueprint(basket.module)
    app.register_blueprint(general.module)
    
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
    api_v1.register_blueprint(addresses.api_v1.bp)
    api_v1.register_blueprint(categories.api_v1.bp)
    api_v1.register_blueprint(products.api_v1.bp)
    app.register_blueprint(api_v1)
    
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/soap/orders': WsgiApplication(orders.create_soap(app))
    })
    
    return app