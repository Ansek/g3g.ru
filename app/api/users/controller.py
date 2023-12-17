from .model import User
from app.api.api_v1 import API_V1
from .specification import api_docs


api_v1 = API_V1('users', User, api_docs,
    allow_post=True, only_admin=False)