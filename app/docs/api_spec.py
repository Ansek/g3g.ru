from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


def get_apispec(app):
    spec = APISpec(
        title='REST API для работы с БД салона связи "Голубь 3G"',
        version='1.0.0',
        openapi_version='3.0.3',
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
    )
  
    from app.api.api_v1 import api_docs
    from app.api.addresses.specification import api_docs as api_docs_a
    from app.api.categories.specification import api_docs as api_docs_c
    from app.api.products.specification import api_docs as api_docs_p
    
    def add_docs(docs):
        for k, v in docs['dictSchema'].items():
            spec.components.schema(k, schema=v)
        if 'tags' in docs.keys():
            spec.tag(docs['tags'])
    
    add_docs(api_docs) 
    add_docs(api_docs_a)
    add_docs(api_docs_c)
    add_docs(api_docs_p)      
    
    with app.test_request_context():
        for fn_name in app.view_functions:
            if fn_name == 'static':
                continue
            view_fn = app.view_functions[fn_name]
            spec.path(view=view_fn)

    return spec