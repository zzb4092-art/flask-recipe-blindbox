"""User model."""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    """User table model."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='哈希加密后的密码')
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        comment='创建时间'
    )

    # ── relationships ──────────────────────────────────────────────
    recipes = db.relationship(
        'Recipe',
        back_populates='author',
        lazy='dynamic',
        foreign_keys='Recipe.user_id'
    )
    restaurants = db.relationship(
        'Restaurant',
        back_populates='owner',
        lazy='dynamic'
    )

    # ── password helpers ───────────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Hash and store the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username!r}>'
