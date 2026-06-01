"""Authentication blueprint – register & login."""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration.

    Request JSON
    ------------
    username : str
    password : str

    Returns
    -------
    JSON
        {"code": 200, "message": "注册成功"}
        {"code": 400, "message": "用户名已存在"}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    # Create new user
    user = User(username=username)
    user.password_hash = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'code': 200, 'message': '注册成功'}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login.

    Request JSON
    ------------
    username : str
    password : str

    Returns
    -------
    JSON
        {"code": 200, "message": "登录成功", "token": "mock-token-123456"}
        {"code": 400, "message": "用户名或密码错误"}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    # Find user by username
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'code': 400, 'message': '用户名或密码错误'}), 400

    return jsonify({
        'code': 200,
        'message': '登录成功',
        'token': 'mock-token-123456',
    }), 200
