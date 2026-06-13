"""
认证蓝图（Blueprint）—— 用户注册 & 登录。

本文件负责：
  - POST /api/auth/register  注册新用户
  - POST /api/auth/login     用户登录（返回 user_id 供前端后续请求使用）

⚠️ 注意事项：
  - 登录成功后 **必须** 返回 user_id，前端才能知道当前是哪个用户。
  - 前端会把这个 user_id 传给菜谱搜索、盲盒抽取、私房菜谱上传等接口，
    用于数据隔离（每个用户只能看到自己的私房菜谱和餐馆）。
  - token 目前是 mock 值，后续可改为 JWT 实现真正的会话管理。
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User

# ── 创建蓝图，所有路由以 /api/auth 开头 ────────────────────────────
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册。

    接收前端发来的用户名和密码，校验通过后在 user 表中创建一条记录。

    Request JSON
    ------------
    username : str   — 用户名（全局唯一）
    password : str   — 明文密码（后端用 werkzeug 哈希后存储）

    Returns
    -------
    JSON
        成功: {"code": 200, "message": "注册成功"}
        失败: {"code": 400, "message": "用户名已存在"}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    # 检查用户名是否已被占用
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    # 创建新用户：密码用 werkzeug 内置哈希，不存明文
    user = User(username=username)
    user.password_hash = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '注册成功',
        'user_id': user.id,
        'username': user.username,
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录。

    验证用户名和密码。登录成功后会返回 user_id，这是整个系统的关键字段：
      - 前端把 user_id 存下来
      - 后续所有个性化请求（菜谱搜索、盲盒抽取、私房菜谱上传）
        都带上这个 user_id，后端根据它来做数据隔离

    Request JSON
    ------------
    username : str
    password : str

    Returns
    -------
    JSON
        成功: {
          "code": 200,
          "message": "登录成功",
          "token": "mock-token-123456",
          "user_id": <int>,      ← 🔑 关键：前端依赖这个值做后续请求
          "username": "<str>"    ← 用于前端展示
        }
        失败: {"code": 400, "message": "用户名或密码错误"}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    # 根据用户名查找用户
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'code': 400, 'message': '用户名或密码错误'}), 400

    # ── 🔑 登录成功：返回 user_id 和 username ─────────────────
    # 前端收到后会存到 loggedInUserId / loggedInUser 变量中，
    # 后续所有需要用户身份的请求都从这里取值，不再硬编码 1。
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'token': 'mock-token-123456',   # TODO: 后续改为真实 JWT
        'user_id': user.id,             # 数据库自增主键，前端每次请求都要带
        'username': user.username,      # 用于前端界面展示"已登录：张三"
    }), 200
