from flask import jsonify, Blueprint
from flask_login import login_user, logout_user
 
from app.login import login_manager
from app.api.users.model import User
from app.api.api_v1 import (
    get_args,
    try_query_func,
    check_arg_list,
    check_string,
    convert_arg
)


bp = Blueprint('session', __name__, url_prefix='session')


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@bp.route('/login/', methods=['POST'])
def login():
    def func():
        res = ''
        code = 204
        args = get_args()
        # Проверки полей
        check_arg_list(args, ['login', 'password', 'remember'])
        login = convert_arg(args, 'login', str, IsNotNone=True)
        password = convert_arg(args, 'password', str, IsNotNone=True)
        remember = convert_arg(args, 'remember', bool)
        check_string(login, 128, 'login')
        check_string(password, 64, 'password')
        # Проверка пароля
        user = User.query.filter(User.login == login).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
        else:
            res = { 'message': 'Invalid login or password'}
            code = 401
        return res, code
    res, code = try_query_func(func, 'session', 'login')
    if code != 204:
        res = jsonify(res)
    return res, code


@bp.route('/logout/', methods=['POST'])
def logout():
    logout_user()
    return '', 204


login.__doc__ = f"""
    ---
    post:
      summary: Авторизация пользователя в систему
      parameters:
        - in: query
          schema: Login_SessionSchema
      responses:
        '204':
          description: Пользователь успешно вошел в систему
        '401':
          description: Неверный пароль или логин
          content:
            application/json:
              schema: ErrorLoginSchema
        '500':
          description: Произошла проблема при выполнении запроса к БД
          content:
            application/json:
              schema: Error500Schema
      tags:
        - Session
"""

logout.__doc__ = f"""
    ---
    post:
      summary: Удалить информацию о входе пользователя в систему
      responses:
        '204':
          description: Пользователь успешно вышел из системы
        '500':
          description: Произошла проблема при выполнении запроса к БД
          content:
            application/json:
              schema: Error500Schema
      tags:
        - Session
"""