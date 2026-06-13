"""
菜谱搜索蓝图（Blueprint）—— 食材反查 & 私房菜谱管理。

本文件提供以下 API：
  - GET  /api/recipes/search           按食材搜索菜谱（清空冰箱计划）
  - GET  /api/recipes/<id>/detail      菜谱详情
  - GET  /api/recipes/mine             我的私房菜谱列表（个人中心用）
  - POST /api/recipes/custom           上传私房菜谱

══════════════════════════════════════════════════════════════════════
核心设计：可见性过滤（visibility filter）
──────────────────────────────────────────────────────────────────────
系统里有两类菜谱：
  1. 系统菜谱（is_custom=False）：所有用户都能看到
  2. 私房菜谱（is_custom=True, user_id=<某人>）：只有上传者自己能看到

在搜索时：
  - 如果传了 user_id → 返回「系统菜谱」+「该用户的私房菜谱」
  - 如果不传 user_id → 返回全部（游客模式，方便未登录浏览）

⚠️ 这意味着：如果前端传错 user_id，用户就看不到自己的私房菜谱！  ← 本次 bug 的根因
══════════════════════════════════════════════════════════════════════
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import func, or_

from app import db
from app.models import Recipe, Ingredient, RecipeIngredientMapping, User

# ── 创建蓝图，所有路由以 /api/recipes 开头 ──────────────────────────
recipe_bp = Blueprint('recipe', __name__, url_prefix='/api/recipes')


# ══════════════════════════════════════════════════════════════════════
#  搜索 —— 食材反查菜谱（清空冰箱计划核心功能）
# ══════════════════════════════════════════════════════════════════════

@recipe_bp.route('/search', methods=['GET'])
def search_recipes():
    """根据食材搜索菜谱，支持别名匹配和用户私房菜谱。

    搜索流程（5 步）：
      ① 解析用户输入的食材（逗号分隔）
      ② 在 ingredient 表中匹配（精确名称 OR 别名模糊匹配）
      ③ 根据 user_id 决定可见范围（本 bug 的关键所在 ← 见上方文档）
      ④ 按匹配度排序（私房菜谱优先、匹配食材数越多越靠前）
      ⑤ 组装返回数据

    Query Parameters
    ----------------
    ingredients : str
        逗号分隔的食材名称/别名，例如 "西红柿,鸡蛋"
        前端从冰箱标签列表中 join(',') 生成
    user_id : int, optional
        登录用户的数据库 ID。
        - 传入时：只显示系统菜谱 + 该用户的私房菜谱
        - 不传时：显示全部菜谱（游客模式）

    Returns
    -------
    JSON
        成功: {"code": 200, "data": [{...}]}
        失败: {"code": 400, "message": "请提供食材参数"}
    """
    # ── ① 获取并清洗前端参数 ──────────────────────────────────────
    ingredients_str = request.args.get('ingredients', '').strip()
    user_id = request.args.get('user_id', type=int)  # 可选，未登录时为 None

    if not ingredients_str:
        return jsonify({'code': 400, 'message': '请提供食材参数'}), 400

    terms = [t.strip() for t in ingredients_str.split(',') if t.strip()]
    if not terms:
        return jsonify({'code': 400, 'message': '请提供食材参数'}), 400

    # ── ② 食材名称 → ingredient 表 ID（精确 + 别名模糊） ──────────
    # 例：用户输入 "土豆" 可以匹配到 name="土豆" 或 aliases 包含 "马铃薯,土豆" 的记录
    conditions = []
    for term in terms:
        conditions.append(Ingredient.name == term)            # 精确匹配
        conditions.append(Ingredient.aliases.like(f'%{term}%'))  # 别名模糊匹配

    matched_rows = (
        db.session.query(Ingredient.id)
        .filter(or_(*conditions))  # 所有条件之间是 OR 关系
        .all()
    )
    matched_ids = [row[0] for row in matched_rows]

    # 没有任何食材匹配 → 直接返回空列表
    if not matched_ids:
        return jsonify({'code': 200, 'data': []}), 200

    # ── ③ 🔑 可见性过滤（本次 bug 的核心修复点） ─────────────────
    # 这里决定用户能看到哪些菜谱。规则：
    #   - 系统菜谱（is_custom=False）：所有人可见
    #   - 私房菜谱（is_custom=True） ：只有上传者（recipe.user_id == user_id）可见
    #
    # ⚠️ 如果前端传错 user_id（比如硬编码成 1），就会出现：
    #   用户上传菜谱时 user_id=1，搜索时 user_id=2 → 搜不到！
    #   现在前端已修复为：登录时从后端获取真实 user_id，不再硬编码。
    if user_id is not None:
        visibility = [
            (Recipe.is_custom == False)                               # 系统菜谱
            | ((Recipe.is_custom == True) & (Recipe.user_id == user_id))  # 我的私房菜谱
        ]
    else:
        # 未登录（游客模式）：不做过滤，展示所有菜谱
        visibility = []

    # ── ④ 联表查询：recipe → junction → ingredient，按匹配度排序 ──
    # match_count = 该菜谱中有多少个食材命中了用户输入
    match_count = func.count(RecipeIngredientMapping.id).label('match_count')

    query = (
        db.session.query(Recipe, match_count)
        .join(
            RecipeIngredientMapping,
            Recipe.id == RecipeIngredientMapping.recipe_id,
        )
        .filter(RecipeIngredientMapping.ingredient_id.in_(matched_ids))
    )
    # 应用可见性过滤
    if visibility:
        query = query.filter(or_(*visibility))

    rows = (
        query
        .group_by(Recipe.id)
        .order_by(
            Recipe.is_custom.desc(),   # 🔑 私房菜谱置顶：自定义菜谱永远排在最前面
            match_count.desc(),        # 匹配食材数越多越靠前
        )
        .all()
    )

    # ── ⑤ 组装响应数据 ──────────────────────────────────────────
    recipes_data = []
    for recipe, mc in rows:
        # 查询该菜谱的所有食材名称
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
            'title': recipe.title,             # 菜名
            'steps': recipe.steps,             # 烹饪步骤
            'is_custom': recipe.is_custom,     # 是否私房菜谱
            'user_id': recipe.user_id,         # 上传者 ID
            'match_count': mc,                 # 命中了几个食材
            'total_ingredients': len(ingredient_names),  # 这道菜一共需要几种食材
            'ingredients': ingredient_names,   # 食材名称列表
        })

    return jsonify({'code': 200, 'data': recipes_data}), 200


# ══════════════════════════════════════════════════════════════════════
#  详情 —— 单个菜谱的完整信息（含食材用量）
# ══════════════════════════════════════════════════════════════════════

@recipe_bp.route('/<int:recipe_id>/detail', methods=['GET'])
def recipe_detail(recipe_id: int):
    """获取单个菜谱的详细信息，包括每个食材的用量。

    Path Parameters
    ---------------
    recipe_id : int  — 菜谱 ID（URL 路径参数）

    Returns
    -------
    JSON
        成功: {"code": 200, "data": {"id": 3, "title": "...", "ingredients": [...]}}
        失败: {"code": 404, "message": "菜谱不存在"}
    """
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return jsonify({'code': 404, 'message': '菜谱不存在'}), 404

    # 联表查询：获取食材名称 + 用量
    mappings = (
        db.session.query(
            Ingredient.name,                    # 食材名称
            RecipeIngredientMapping.amount,     # 用量（如 "500g"、"2个"）
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
#  我的菜谱 —— 获取当前用户的所有私房菜谱（个人中心用）
#  🆕 本次新增端点，专门替代之前用 /search?ingredients='' 的 hack
# ══════════════════════════════════════════════════════════════════════

@recipe_bp.route('/mine', methods=['GET'])
def my_recipes():
    """返回当前用户上传的所有私房菜谱。

    为什么需要一个独立的端点？
    ─────────────────────────
    之前前端 loadUserData() 调用 /api/recipes/search?ingredients=&user_id=1
    这种 hack 有两个问题：
      1. ingredients 为空 → 后端返回 400 → 前端 .catch() 吞掉错误 → 永远空列表
      2. user_id 硬编码为 1 → 多用户场景下拿不到正确数据

    现在用专门的 /api/recipes/mine 端点，只根据 user_id 查私房菜谱，
    不依赖食材参数，语义清晰且不会出错。

    Query Parameters
    ----------------
    user_id : int  — 当前登录用户的 ID

    Returns
    -------
    JSON
        成功: {"code": 200, "data": [{"id": ..., "title": ..., "ingredients": [...]}]}
        失败: {"code": 400, "message": "请提供 user_id"}
    """
    # ── 获取并校验参数 ──────────────────────────────────────────
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '请提供 user_id'}), 400

    # ── 只查该用户的私房菜谱，按 ID 倒序（最新上传的排前面） ──
    recipes_list = (
        db.session.query(Recipe)
        .filter(Recipe.is_custom == True, Recipe.user_id == user_id)
        .order_by(Recipe.id.desc())
        .all()
    )

    # ── 为每个菜谱查出食材列表 ─────────────────────────────────
    result = []
    for recipe in recipes_list:
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

        result.append({
            'id': recipe.id,
            'title': recipe.title,
            'steps': recipe.steps,
            'is_custom': recipe.is_custom,
            'user_id': recipe.user_id,
            'total_ingredients': len(ingredient_names),
            'ingredients': ingredient_names,
        })

    return jsonify({'code': 200, 'data': result}), 200


# ══════════════════════════════════════════════════════════════════════
#  上传 —— 用户上传私房菜谱
# ══════════════════════════════════════════════════════════════════════

@recipe_bp.route('/custom', methods=['POST'])
def create_custom_recipe():
    """上传一条用户自定义的私房菜谱。

    业务流程：
      ① 校验必填字段（user_id、标题、食材、步骤）
      ② 验证 user_id 对应的用户是否存在（DB 外键约束）
      ③ 在 recipe 表创建记录（is_custom=True）
      ④ 逐个食材做「匹配已有 OR 新建」，然后建 junction 映射
      ⑤ 提交事务，返回新菜谱数据

    Request JSON
    ------------
    user_id : int      — 🔑 菜谱归属的用户 ID（前端从登录接口获取）
    title : str        — 菜名，如 "奶奶的红烧肉"
    ingredients : str  — 逗号分隔的食材，如 "五花肉,冰糖,酱油"
    steps : str        — 烹饪步骤说明

    Returns
    -------
    JSON
        成功: {"code": 201, "message": "创建成功", "data": {...}}
        失败: {"code": 400, "message": "具体错误原因"}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    # ── ① 提取并清洗字段 ────────────────────────────────────────
    user_id = data.get('user_id')
    title = (data.get('title') or '').strip()
    ingredients_str = (data.get('ingredients') or '').strip()
    steps = (data.get('steps') or '').strip()

    # ── ② 校验 ─────────────────────────────────────────────────
    if not user_id:
        return jsonify({'code': 400, 'message': '请提供 user_id'}), 400
    # 验证用户是否存在（外键约束需要有效的 user_id）
    if db.session.get(User, user_id) is None:
        return jsonify({'code': 400, 'message': '用户不存在'}), 400
    if not title:
        return jsonify({'code': 400, 'message': '菜名不能为空'}), 400
    if not ingredients_str:
        return jsonify({'code': 400, 'message': '食材不能为空'}), 400
    if not steps:
        return jsonify({'code': 400, 'message': '步骤不能为空'}), 400

    # 把逗号分隔的食材字符串拆成列表
    ingredient_names = [
        name.strip() for name in ingredients_str.split(',') if name.strip()
    ]
    if not ingredient_names:
        return jsonify({'code': 400, 'message': '食材不能为空'}), 400

    # ── ③ 创建菜谱记录 ─────────────────────────────────────────
    recipe = Recipe(
        title=title,
        steps=steps,
        is_custom=True,    # 标记为私房菜谱
        user_id=user_id,   # 归属用户
    )
    db.session.add(recipe)
    db.session.flush()  # 先 flush 拿到 recipe.id，下面建 junction 要用

    # ── ④ 匹配或创建食材，并建立 recipe ↔ ingredient 的映射 ────
    # 对每个食材名称，先去 ingredient 表里找有没有同名的：
    #   - 有 → 直接用已有记录（避免重复）
    #   - 没有 → 新建一条 ingredient 记录
    # 然后在 junction 表插入一行，把 recipe 和 ingredient 关联起来。
    for ing_name in ingredient_names:
        # 查找已有食材（DB 排序规则是 utf8mb4_0900_ai_ci，天然支持大小写不敏感）
        ingredient = Ingredient.query.filter_by(name=ing_name).first()
        if ingredient is None:
            # 食材字典里还没有这个食材 → 新建
            ingredient = Ingredient(name=ing_name)
            db.session.add(ingredient)
            db.session.flush()  # flush 以获取 ingredient.id

        # 建立 recipe ↔ ingredient 的映射（junction 表）
        mapping = RecipeIngredientMapping(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            amount=None,  # 用户上传时不带用量信息，后续可扩展
        )
        db.session.add(mapping)

    # ── ⑤ 提交事务 ─────────────────────────────────────────────
    db.session.commit()

    # ── ⑥ 返回新创建的菜谱数据 ──────────────────────────────────
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
