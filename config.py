import os


class Config(object):
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REST_API_LIMIT = 5 # Ограничение списка в методе GET для RestAPI  
    SOAP_LIMIT = 10    # Ограничение списка для SOAP

class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True