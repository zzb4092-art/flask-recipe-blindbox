"""Restaurant model."""
from app import db


class Restaurant(db.Model):
    """Restaurant table model."""
    __tablename__ = 'restaurant'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        comment='归属用户'
    )
    name = db.Column(db.String(100), nullable=False, comment='餐馆名称')
    tags = db.Column(db.String(255), nullable=False, comment='标签列表，逗号分隔，例如：中餐,高性价比,夜宵')
    is_spicy = db.Column(db.Boolean, default=False, comment='是否辣: 0不辣, 1辣')
    price_range = db.Column(db.String(50), nullable=True, comment='价格区间')

    # ── relationships ──────────────────────────────────────────────
    owner = db.relationship(
        'User',
        back_populates='restaurants',
        foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        return f'<Restaurant {self.name!r}>'
