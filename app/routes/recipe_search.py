"""Recipe search blueprint – ingredient-based reverse lookup & custom recipes."""
from flask import Blueprint, request, jsonify
from sqlalchemy import func, or_

from app import db
from app.models import Recipe, Ingredient, RecipeIngredientMapping, User

recipe_bp = Blueprint('recipe', __name__, url_prefix='/api/recipes')


# ══════════════════════════════════════════════════════════════════════
#  Search – ingredient-based reverse lookup
# ══════════════════════════════════════════════════════════════════════

@recipe_bp.route('/search', methods=['GET'])
def search_recipes():
    """Search recipes by ingredients, including the user's own custom recipes.

    Query Parameters
    ----------------
    ingredients : str
        Comma-separated ingredient names/aliases, e.g. ``"西红柿,鸡蛋"``.
    user_id : int, optional
        When provided, the search includes **system recipes** (is_custom=0)
        AND **this user's custom recipes** (is_custom=1, user_id=…).
        When omitted, only system recipes are returned.
        Recipes uploaded by *other* users are never visible.

    Returns
    -------
    JSON
        ``{"code": 200, "data": [{...}]}``
    """
    ingredients_str = request.args.get('ingredients', '').strip()
    user_id = request.args.get('user_id', type=int)

    if not ingredients_str:
        return jsonify({'code': 400, 'message': '请提供食材参数'}), 400

    # ── Step 1: parse input into individual terms ──────────────────
    terms = [t.strip() for t in ingredients_str.split(',') if t.strip()]
    if not terms:
        return jsonify({'code': 400, 'message': '请提供食材参数'}), 400

    # ── Step 2: resolve terms → ingredient IDs (exact name OR alias LIKE) ──
    conditions = []
    for term in terms:
        conditions.append(Ingredient.name == term)
        conditions.append(Ingredient.aliases.like(f'%{term}%'))

    matched_rows = (
        db.session.query(Ingredient.id)
        .filter(or_(*conditions))
        .all()
    )
    matched_ids = [row[0] for row in matched_rows]

    if not matched_ids:
        return jsonify({'code': 200, 'data': []}), 200

    # ── Step 3: visibility filter ──────────────────────────────────
    #   Without user_id: show ALL recipes (system + all custom).
    #   With user_id:    show system recipes + only THIS user's customs.
    if user_id is not None:
        visibility = [
            (Recipe.is_custom == False)
            | ((Recipe.is_custom == True) & (Recipe.user_id == user_id))
        ]
    else:
        visibility = []  # no filter — return everything

    # ── Step 4: find recipes containing any matched ingredient, ────
    #            ranked by match count & custom-first               ──
    match_count = func.count(RecipeIngredientMapping.id).label('match_count')

    query = (
        db.session.query(Recipe, match_count)
        .join(
            RecipeIngredientMapping,
            Recipe.id == RecipeIngredientMapping.recipe_id,
        )
        .filter(RecipeIngredientMapping.ingredient_id.in_(matched_ids))
    )
    if visibility:
        query = query.filter(or_(*visibility))

    rows = (
        query
        .group_by(Recipe.id)
        .order_by(
            Recipe.is_custom.desc(),   # 私有库提权：自定义菜谱永远排在最前面
            match_count.desc(),        # 匹配食材数越多越靠前
        )
        .all()
    )

    # ── Step 5: assemble response ──────────────────────────────────
    recipes_data = []
    for recipe, mc in rows:
        ingredient_rows = (
            db.session.query(Ingredient.name)
            .join(
                RecipeIngredientMapping,
                Ingredient.id == RecipeIngredientMapping.ingredient_id,
            )
            .filter(RecipeIngredientMapping.recipe_id == recipe.id)
            .all()
        )
        ingredient_names = [r[0] for r in ingredient_rows]

        recipes_data.append({
            'id': recipe.id,
            'title': recipe.title,
            'steps': recipe.steps,
            'is_custom': recipe.is_custom,
            'user_id': recipe.user_id,
            'match_count': mc,
            'total_ingredients': len(ingredient_names),
            'ingredients': ingredient_names,
        })

    return jsonify({'code': 200, 'data': recipes_data}), 200


# ══════════════════════════════════════════════════════════════════════
#  Detail – single recipe with full ingredient amounts
# ══════════════════════════════════════════════════════════════════════

@recipe_bp.route('/<int:recipe_id>/detail', methods=['GET'])
def recipe_detail(recipe_id: int):
    """Get full detail of a single recipe.

    Path Parameters
    ---------------
    recipe_id : int

    Returns
    -------
    JSON
    """
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return jsonify({'code': 404, 'message': '菜谱不存在'}), 404

    mappings = (
        db.session.query(
            Ingredient.name,
            RecipeIngredientMapping.amount,
        )
        .join(
            RecipeIngredientMapping,
            Ingredient.id == RecipeIngredientMapping.ingredient_id,
        )
        .filter(RecipeIngredientMapping.recipe_id == recipe_id)
        .all()
    )

    ingredients_data = [
        {'name': name, 'amount': amount}
        for name, amount in mappings
    ]

    return jsonify({
        'code': 200,
        'data': {
            'id': recipe.id,
            'title': recipe.title,
            'steps': recipe.steps,
            'is_custom': recipe.is_custom,
            'user_id': recipe.user_id,
            'ingredients': ingredients_data,
        },
    }), 200


# ══════════════════════════════════════════════════════════════════════
#  Custom – user-uploaded recipe
# ══════════════════════════════════════════════════════════════════════

@recipe_bp.route('/custom', methods=['POST'])
def create_custom_recipe():
    """Upload a user-defined custom recipe.

    Request JSON
    ------------
    user_id : int
        Owner of the recipe.
    title : str
        Recipe title.
    ingredients : str
        Comma-separated ingredient names, e.g. ``"西红柿,鸡蛋"``.
    steps : str
        Cooking instructions.

    Returns
    -------
    JSON
        ``{"code": 201, "message": "创建成功", "data": {...}}``
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    user_id = data.get('user_id')
    title = (data.get('title') or '').strip()
    ingredients_str = (data.get('ingredients') or '').strip()
    steps = (data.get('steps') or '').strip()

    # ── validation ────────────────────────────────────────────────
    if not user_id:
        return jsonify({'code': 400, 'message': '请提供 user_id'}), 400
    # Verify user exists (FK constraint requires a valid user)
    if db.session.get(User, user_id) is None:
        return jsonify({'code': 400, 'message': '用户不存在'}), 400
    if not title:
        return jsonify({'code': 400, 'message': '菜名不能为空'}), 400
    if not ingredients_str:
        return jsonify({'code': 400, 'message': '食材不能为空'}), 400
    if not steps:
        return jsonify({'code': 400, 'message': '步骤不能为空'}), 400

    ingredient_names = [
        name.strip() for name in ingredients_str.split(',') if name.strip()
    ]
    if not ingredient_names:
        return jsonify({'code': 400, 'message': '食材不能为空'}), 400

    # ── create recipe ─────────────────────────────────────────────
    recipe = Recipe(
        title=title,
        steps=steps,
        is_custom=True,
        user_id=user_id,
    )
    db.session.add(recipe)
    db.session.flush()  # get recipe.id before committing

    # ── match-or-create ingredients & build mapping rows ──────────
    for ing_name in ingredient_names:
        # Look up existing ingredient (case-insensitive would be ideal,
        # but the DB collation is utf8mb4_0900_ai_ci which is CI by default)
        ingredient = Ingredient.query.filter_by(name=ing_name).first()
        if ingredient is None:
            ingredient = Ingredient(name=ing_name)
            db.session.add(ingredient)
            db.session.flush()

        mapping = RecipeIngredientMapping(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            amount=None,  # user uploads don't carry amounts
        )
        db.session.add(mapping)

    db.session.commit()

    # ── build response ────────────────────────────────────────────
    return jsonify({
        'code': 201,
        'message': '创建成功',
        'data': {
            'id': recipe.id,
            'title': recipe.title,
            'steps': recipe.steps,
            'is_custom': recipe.is_custom,
            'user_id': recipe.user_id,
            'ingredients': ingredient_names,
        },
    }), 201
