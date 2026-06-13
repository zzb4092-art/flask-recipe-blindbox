"""
餐馆模型 —— Restaurant 表。

每家餐馆归属于一个用户，用户只能在自己的餐馆库中盲盒抽取。
标签（tags）用于权重加成判定（宵夜、火锅、养生等）。
"""
from app import db


class Restaurant(db.Model):
    """餐馆表 —— 用户收藏的常去餐馆。

    Attributes
    ----------
    id : int              自增主键
    user_id : int         归属用户 ID（外键 → user.id）
    name : str            餐馆名称，如 "xx大排档"
    tags : str            标签列表，逗号分隔，如 "中餐,宵夜,高性价比"
                          用于盲盒权重算法的加成判定
    is_spicy : bool       是否辣（True=辣, False=不辣）
                          用于 "今天不吃辣" 硬过滤
    price_range : str     价格区间，如 "人均50-80"
                          用于预算过滤（low/mid/high）
    """

    __tablename__ = 'restaurant'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),  # 用户被删时级联删除其所有餐馆
        nullable=False,
        comment='归属用户ID'
    )
    name = db.Column(db.String(100), nullable=False, comment='餐馆名称')
    tags = db.Column(db.String(255), nullable=False, comment='标签列表，逗号分隔，例如：中餐,高性价比,宵夜')
    is_spicy = db.Column(db.Boolean, default=False, comment='是否辣: 0=不辣, 1=辣')
    price_range = db.Column(db.String(50), nullable=True, comment='价格区间，如 人均50-80')

    # ── 关系映射 ──────────────────────────────────────────────
    owner = db.relationship(
        'User',
        back_populates='restaurants',
        foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        return f'<Restaurant {self.name!r}>'
