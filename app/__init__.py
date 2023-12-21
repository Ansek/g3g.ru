import os
from flask import Flask, Blueprint, json
from spyne.server.wsgi import WsgiApplication
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from .login import login_manager
from .database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

    login_manager.init_app(app)
    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    if app.debug == True:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)
        except:
            pass

    import app.api.session.controller as session
    import app.api.addresses.controller as addresses
    import app.api.categories.controller as categories
    import app.api.products.controller as products
    import app.api.users.controller as users
    import app.account.controller as account
    import app.basket.controller as basket
    import app.general.controller as general
    import app.shop.controller as shop
    import app.soap.orders.controller as orders

    app.register_blueprint(account.module)
    app.register_blueprint(basket.module)
    app.register_blueprint(general.module)
    app.register_blueprint(shop.module)
        
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
    api_v1.register_blueprint(session.bp)
    api_v1.register_blueprint(addresses.api_v1.bp)
    api_v1.register_blueprint(categories.api_v1.bp)
    api_v1.register_blueprint(products.api_v1.bp)
    api_v1.register_blueprint(users.api_v1.bp)
    app.register_blueprint(api_v1)
    
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/soap/orders': WsgiApplication(orders.create_soap(app))
    })
    
    from app.docs.api_spec import get_apispec
    from app.docs.swagger import swagger_ui_blueprint, SWAGGER_URL
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    @app.route('/swagger')
    def create_swagger_spec():
        return json.dumps(get_apispec(app).to_dict())

    return app