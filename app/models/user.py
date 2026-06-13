"""
用户模型 —— User 表。

每个注册用户对应一条记录，拥有：
  - 自己的私房菜谱（Recipe，is_custom=True）
  - 自己的餐馆列表（Restaurant）

密码安全：
  - 使用 werkzeug.security.generate_password_hash 哈希存储
  - 使用 check_password_hash 验证
  - 数据库中只存哈希值，不存明文
"""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    """用户表 —— 存储所有注册用户。

    Attributes
    ----------
    id : int              自增主键（🔑 这个值会被传给前端，用于数据隔离）
    username : str        用户名（全局唯一）
    password_hash : str   密码的哈希值（不存明文）
    created_at : datetime 注册时间
    """

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名（全局唯一）')
    password_hash = db.Column(db.String(255), nullable=False, comment='哈希加密后的密码')
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        comment='账户创建时间'
    )

    # ── 关系映射 ──────────────────────────────────────────────
    # recipes：该用户的所有私房菜谱（一对多）
    # lazy='dynamic' 适合可能有大量菜谱的场景，返回 Query 对象
    recipes = db.relationship(
        'Recipe',
        back_populates='author',
        lazy='dynamic',
        foreign_keys='Recipe.user_id'
    )
    # restaurants：该用户收藏的所有餐馆（一对多）
    restaurants = db.relationship(
        'Restaurant',
        back_populates='owner',
        lazy='dynamic'
    )

    # ── 密码工具方法 ─────────────────────────────────────────
    def set_password(self, password: str) -> None:
        """将明文密码哈希后存储（注册时调用）。"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """验证明文密码是否与存储的哈希匹配（登录时调用）。"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username!r}>'
