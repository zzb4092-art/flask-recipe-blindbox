"""Recipe, Ingredient and RecipeIngredientMapping models."""
from app import db


class Recipe(db.Model):
    """Recipe table model."""
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, comment='标题')
    steps = db.Column(db.Text, nullable=False, comment='做菜步骤说明')
    is_custom = db.Column(db.Boolean, default=False, comment='0:系统自带, 1:用户自定义')
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=True,
        comment='自定义菜谱绑定的用户ID'
    )

    # ── relationships ──────────────────────────────────────────────
    author = db.relationship(
        'User',
        back_populates='recipes',
        foreign_keys=[user_id]
    )
    # Association object – gives access to the `amount` column on the junction table
    ingredient_mappings = db.relationship(
        'RecipeIngredientMapping',
        back_populates='recipe',
        lazy='select',
        cascade='all, delete-orphan'
    )
    # Convenience: traverse directly to ingredients (read-only through the junction)
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
    """Ingredient table model (standard ingredient dictionary)."""
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='标准食材名')
    aliases = db.Column(db.String(255), nullable=True, comment='别名，用逗号分隔')

    # ── relationships ──────────────────────────────────────────────
    recipe_mappings = db.relationship(
        'RecipeIngredientMapping',
        back_populates='ingredient',
        lazy='select',
        cascade='all, delete-orphan'
    )
    # Convenience: traverse directly to recipes (read-only through the junction)
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
    """Junction table – maps recipes to ingredients with the quantity used."""
    __tablename__ = 'recipe_ingredient_mapping'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipe.id', ondelete='CASCADE'),
        nullable=False
    )
    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey('ingredient.id', ondelete='CASCADE'),
        nullable=False
    )
    amount = db.Column(db.String(50), nullable=True, comment='食材用量，例如：2个、500g')

    # ── relationships ──────────────────────────────────────────────
    recipe = db.relationship('Recipe', back_populates='ingredient_mappings')
    ingredient = db.relationship('Ingredient', back_populates='recipe_mappings')

    def __repr__(self) -> str:
        return (
            f'<RecipeIngredientMapping '
            f'recipe={self.recipe_id} ingredient={self.ingredient_id} '
            f'amount={self.amount!r}>'
        )
