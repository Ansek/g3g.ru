from app.database import db
from dataclasses import dataclass
from flask_login import UserMixin

from app.api.api_v1 import (
    check_arg_list,
    check_unumber,
    check_string,
    convert_arg
)


@dataclass
class User(db.Model, UserMixin):
    id: int
    login: str
    password: str
    telephone: str
    email: str
    is_admin: bool

    _tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    telephone = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean(), nullable=False, default=False)

    def check_password(self,  password):
        return self.password == password

    def __str__(self):
        return self.login
        
    def validate_args(args, IsNotNone=True):
        # Проверка на соотвествие аргументам
        arg_list = ['login', 'password', 'telephone', 'email', 'is_admin']
        check_arg_list(args, arg_list)

        # Проверки на тип
        id = convert_arg(args, 'id', int)
        login = convert_arg(args, 'login', str, IsNotNone)
        password = convert_arg(args, 'password', str, IsNotNone)
        telephone = convert_arg(args, 'telephone', str, IsNotNone)
        email = convert_arg(args, 'email', str)
        _ = convert_arg(args, 'is_admin', bool)

        # Проверки на значения
        check_unumber(id, 'id')
        check_string(login, 128, 'login')
        check_string(password, 64, 'password')
        check_string(telephone, 10, 'telephone')
        check_string(email, 128, 'email')