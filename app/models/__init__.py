"""
数据模型包 —— 集中导出所有 SQLAlchemy 模型。

使用方式：
  from app.models import User, Recipe, Ingredient, Restaurant
"""
from app.models.user import User
from app.models.recipe import Recipe, Ingredient, RecipeIngredientMapping
from app.models.restaurant import Restaurant

__all__ = [
    'User',
    'Recipe',
    'Ingredient',
    'RecipeIngredientMapping',
    'Restaurant',
]
