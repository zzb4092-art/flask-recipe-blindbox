"""
Flask 应用工厂（Application Factory）。

本文件是整个后端项目的入口，负责：
  - 创建 Flask 实例
  - 加载配置（数据库连接、密钥等）
  - 初始化扩展（SQLAlchemy、CORS）
  - 注册所有蓝图（auth、recipe、blindbox）

使用方式：
  >>> from app import create_app
  >>> app = create_app()           # 开发环境
  >>> app = create_app('production')  # 生产环境
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

# ── 全局数据库实例（所有模型和路由都 import 这个 db） ───────────────
db = SQLAlchemy()


def create_app(config_name: str | None = None) -> Flask:
    """创建并配置 Flask 应用。

    Parameters
    ----------
    config_name : str | None
        'development' / 'production' / None（默认使用 'default'）
        对应 config.py 中的 DevelopmentConfig / ProductionConfig

    Returns
    -------
    Flask
        配置完成的 Flask 应用实例，可直接 run()
    """
    flask_app = Flask(__name__)

    # ── ① 加载配置 ────────────────────────────────────────────────
    # 从 config.py 读取数据库连接串、SECRET_KEY 等
    config_name = config_name or 'default'
    flask_app.config.from_object(config[config_name])

    # ── ② 初始化扩展 ────────────────────────────────────────────
    # SQLAlchemy：ORM 框架，操作 MySQL 数据库
    db.init_app(flask_app)

    # CORS：用正则匹配任意 localhost 端口，Vite 换端口也不怕
    # ^http://(localhost|127\.0\.0\.1):\d+$  ← 匹配 5173 / 5174 / 5175 / …
    CORS(flask_app, origins=r'^http://(localhost|127\.0\.0\.1):\d+$')

    # ── ③ 注册模型（让 SQLAlchemy 知道有哪些表） ─────────────────
    # 必须在 app_context 中 import，因为模型需要访问 db 实例
    with flask_app.app_context():
        import app.models  # noqa: F401  （导入副作用：注册 User, Recipe, Restaurant 等模型）

    # ── ④ 注册蓝图（API 路由） ───────────────────────────────────
    # 三个蓝图分别对应：认证、菜谱、盲盒餐馆
    # 蓝图前缀：
    #   /api/auth        → 登录注册
    #   /api/recipes     → 菜谱搜索、上传、我的菜谱
    #   /api/restaurants → 盲盒抽餐馆
    from app.routes.auth import auth_bp
    from app.routes.recipe_search import recipe_bp
    from app.routes.blindbox import blindbox_bp
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(recipe_bp)
    flask_app.register_blueprint(blindbox_bp)

    return flask_app
