"""
菜谱相关模型 —— Recipe（菜谱）、Ingredient（食材字典）、RecipeIngredientMapping（关联表）

══════════════════════════════════════════════════════════════════════
表关系说明：

  recipe ──┬── recipe_ingredient_mapping ──┬── ingredient
           │  (junction 关联表)              │   (食材字典)
           │                                │
           │  recipe_id  → recipe.id        │
           │  ingredient_id → ingredient.id  │
           │  amount (用量)                  │
           │                                │
           └── user (author)                │
              user_id → user.id             │

  - 一道菜（recipe）可以有多个食材（ingredient）
  - 一个食材（ingredient）可以属于多道菜（recipe）
  - 多对多关系通过 recipe_ingredient_mapping（junction 表）实现
  - junction 表额外存储 amount（用量），如 "500g"、"2个"

  - 私房菜谱（is_custom=True）绑定到一个用户（user_id）
  - 系统菜谱（is_custom=False）的 user_id 为 NULL
══════════════════════════════════════════════════════════════════════
"""
from app import db


class Recipe(db.Model):
    """菜谱表 —— 存储每道菜的基本信息。

    Attributes
    ----------
    id : int              自增主键
    title : str           菜名，如 "西红柿炒鸡蛋"
    steps : str           烹饪步骤说明（长文本）
    is_custom : bool      False=系统菜谱, True=用户上传的私房菜谱
    user_id : int | None  私房菜谱的归属用户 ID（系统菜谱为 NULL）
    """

    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment='菜名标题')
    steps = db.Column(db.Text, nullable=False, comment='做菜步骤说明')
    is_custom = db.Column(db.Boolean, default=False, comment='0:系统自带, 1:用户自定义')
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),  # 用户被删时级联删除其菜谱
        nullable=True,
        comment='自定义菜谱绑定的用户ID（系统菜谱为 NULL）'
    )

    # ── 关系映射 ──────────────────────────────────────────────
    # author：通过 user_id 关联到 User 表
    author = db.relationship(
        'User',
        back_populates='recipes',
        foreign_keys=[user_id]
    )
    # ingredient_mappings：关联到 junction 表，可访问 amount 字段
    ingredient_mappings = db.relationship(
        'RecipeIngredientMapping',
        back_populates='recipe',
        lazy='select',
        cascade='all, delete-orphan'  # 删除菜谱时级联删除所有食材映射
    )
    # ingredients：快捷方式，跳过 junction 表直接拿食材列表（只读）
    ingredients = db.relationship(
        'Ingredient',
        secondary='recipe_ingredient_mapping',
        back_populates='recipes',
        viewonly=True,
        lazy='select'
    )

    def __repr__(self) -> str:
        return f'<Recipe {self.title!r}>'


class Ingredient(db.Model):
    """食材字典表 —— 所有食材的标准名称和别名。

    Attributes
    ----------
    id : int         自增主键
    name : str       标准食材名（唯一），如 "土豆"、"牛肉"
    aliases : str    别名列表，逗号分隔，如 "马铃薯,洋芋"
                     用于搜索时的模糊匹配
    """

    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='标准食材名（唯一）')
    aliases = db.Column(db.String(255), nullable=True, comment='别名，用逗号分隔，如 马铃薯,洋芋')

    # ── 关系映射 ──────────────────────────────────────────────
    recipe_mappings = db.relationship(
        'RecipeIngredientMapping',
        back_populates='ingredient',
        lazy='select',
        cascade='all, delete-orphan'
    )
    recipes = db.relationship(
        'Recipe',
        secondary='recipe_ingredient_mapping',
        back_populates='ingredients',
        viewonly=True,
        lazy='select'
    )

    def __repr__(self) -> str:
        return f'<Ingredient {self.name!r}>'


class RecipeIngredientMapping(db.Model):
    """菜谱-食材关联表（Junction Table）—— 多对多关系的桥梁。

    除了关联 recipe 和 ingredient，还额外存储 amount（食材用量）。

    Attributes
    ----------
    id : int              自增主键
    recipe_id : int       外键 → recipe.id
    ingredient_id : int   外键 → ingredient.id
    amount : str | None   食材用量，如 "500g"、"2个"、"适量"
    """

    __tablename__ = 'recipe_ingredient_mapping'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipe.id', ondelete='CASCADE'),  # 菜谱删了，这条关联也删
        nullable=False
    )
    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey('ingredient.id', ondelete='CASCADE'),  # 食材删了，这条关联也删
        nullable=False
    )
    amount = db.Column(db.String(50), nullable=True, comment='食材用量，例如：2个、500g、适量')

    # ── 关系映射 ──────────────────────────────────────────────
    recipe = db.relationship('Recipe', back_populates='ingredient_mappings')
    ingredient = db.relationship('Ingredient', back_populates='recipe_mappings')

    def __repr__(self) -> str:
        return (
            f'<RecipeIngredientMapping '
            f'recipe={self.recipe_id} ingredient={self.ingredient_id} '
            f'amount={self.amount!r}>'
        )
