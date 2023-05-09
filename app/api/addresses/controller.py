from .model import Address, db
from app.api.api_v1 import API_V1

api_v1 = API_V1('addresses', Address)