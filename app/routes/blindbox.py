"""
盲盒选餐馆蓝图（Blueprint）—— 加权随机抽取餐馆。

本文件提供：
  - POST /api/restaurants/blindbox  根据用户条件和场景权重抽取一家餐馆

══════════════════════════════════════════════════════════════════════
核心算法（见 app/utils/blindbox_weight.py）：
  1. 硬过滤：排除辣味餐馆（可选）
  2. 基础权重：每家餐馆起步 10 分
  3. 夜间加成（22:00–04:00）：宵夜/烧烤标签 → 30 分
  4. 天气加成（雨天/寒冷）：砂锅粥/火锅/养生标签 → +10 分
  5. 加权随机：用 random.choices(weights=...) 抽取赢家

餐馆数据归属：
  - 每家餐馆绑定到一个 user_id
  - 用户只能从自己的餐馆库中抽取
  - 用户 ID 由前端从登录接口获取并传递
══════════════════════════════════════════════════════════════════════
"""
import re
from flask import Blueprint, request, jsonify

from app import db
from app.models import Restaurant, User
from app.utils.blindbox_weight import calculate_restaurant_weight

# ── 创建蓝图，所有路由以 /api/restaurants 开头 ─────────────────────
blindbox_bp = Blueprint('blindbox', __name__, url_prefix='/api/restaurants')


# ── 辅助函数 ────────────────────────────────────────────────────────

def _extract_max_price(price_range: str) -> int | None:
    """从价格区间字符串中提取上限值。

    例如：
      "人均120-180" → 180
      "人均50-80"   → 80
      "人均30以下"  → 30

    Parameters
    ----------
    price_range : str  价格区间字符串

    Returns
    -------
    int | None  上限值，无法解析时返回 None
    """
    if not price_range:
        return None
    # 提取所有连续数字
    numbers = re.findall(r'\d+', price_range)
    if not numbers:
        return None
    return max(int(n) for n in numbers)  # 取最大值作为上限


def _filter_by_budget(candidates: list, budget: str) -> list:
    """按预算档位过滤餐馆。

    Parameters
    ----------
    candidates : list of Restaurant
        待过滤的餐馆列表
    budget : str
        'low'   → 人均 ≤30
        'mid'   → 人均 30–80
        'high'  → 人均 ≥80

    Returns
    -------
    list of Restaurant
        过滤后的餐馆列表
    """
    filtered = []
    for r in candidates:
        max_price = _extract_max_price(r.price_range)
        if max_price is None:
            # 无法解析价格 → 保留（不误杀）
            filtered.append(r)
            continue
        if budget == 'low' and max_price <= 30:
            filtered.append(r)
        elif budget == 'mid' and 30 < max_price <= 80:
            filtered.append(r)
        elif budget == 'high' and max_price > 80:
            filtered.append(r)
        elif budget not in ('low', 'mid', 'high'):
            filtered.append(r)  # 未知档位 → 不过滤
    return filtered


# ── API 路由 ────────────────────────────────────────────────────────

@blindbox_bp.route('/blindbox', methods=['POST'])
def draw_restaurant():
    """🎰 盲盒抽餐馆 —— 使用智能权重算法抽取一家餐馆。

    完整流程：
      ① 校验请求参数
      ② 从数据库查出当前用户的所有餐馆
      ③ 按预算档位过滤（可选）
      ④ 调用权重算法计算每家餐馆的中奖概率
      ⑤ 返回中奖餐馆及其权重元数据

    Request JSON
    ------------
    user_id : int
        当前用户的数据库 ID（🔑 决定从谁的餐馆库中抽）
    exclude_spicy : bool
        是否排除辣味餐馆（如用户选了"今天不吃辣"）
    user_weather : str or null
        天气标签："雨天" / "寒冷" / null
        影响砂锅粥、火锅、养生类餐馆的权重
    budget : str or null
        预算档位："low" | "mid" | "high" | null（不限）

    Returns
    -------
    JSON
        成功抽到:
        {
          "code": 200,
          "data": {
            "id": 3,
            "name": "xx大排档",
            "tags": "中餐,宵夜,高性价比",
            "is_spicy": false,
            "price_range": "人均50-80",
            "weight": 30,                           ← 最终权重值
            "boosts": ["夜间推荐：宵夜"]              ← 加成原因
          }
        }

        没有符合条件的餐馆:
        {"code": 200, "data": null, "message": "没有符合条件的餐馆"}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    # ── ① 提取并校验参数 ─────────────────────────────────────────
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'code': 400, 'message': '请提供 user_id'}), 400

    exclude_spicy = bool(data.get('exclude_spicy', False))
    user_weather = data.get('user_weather')  # str or None
    budget = data.get('budget')              # 'low' | 'mid' | 'high' | None
    preferred_tags = data.get('preferred_tags')  # list[str] or None

    # ── ② 查询当前用户的餐馆库 ──────────────────────────────────
    # 🔑 关键：只查当前用户的餐馆，不查别人的
    candidates = (
        db.session.query(Restaurant)
        .filter_by(user_id=user_id)
        .all()
    )

    # ── ③ 预算过滤（在权重算法之前，直接缩小候选池） ────────────
    if budget:
        candidates = _filter_by_budget(candidates, budget)

    if not candidates:
        return jsonify({
            'code': 200,
            'data': None,
            'message': '该用户还没有添加餐馆',
        }), 200

    # ── ④ 运行权重算法 ─────────────────────────────────────────
    # calculate_restaurant_weight 是纯 Python 函数，不依赖数据库，
    # 方便单元测试。它会根据时间、天气等条件给每家餐馆打分。
    result = calculate_restaurant_weight(
        restaurants=candidates,
        exclude_spicy=exclude_spicy,
        current_weather=user_weather,
        preferred_tags=preferred_tags,
    )

    if result is None:
        return jsonify({
            'code': 200,
            'data': None,
            'message': '没有符合条件的餐馆',
        }), 200

    # ── ⑤ 组装返回数据 ─────────────────────────────────────────
    r = result.restaurant

    return jsonify({
        'code': 200,
        'data': {
            'id': r.id,
            'name': r.name,              # 餐馆名称
            'tags': r.tags,              # 标签（逗号分隔）
            'is_spicy': r.is_spicy,      # 是否辣
            'price_range': r.price_range,  # 价格区间
            'weight': result.weight,     # 最终权重
            'boosts': result.boosts,     # 加成原因（如 "夜间推荐：宵夜"）
        },
    }), 200


# ══════════════════════════════════════════════════════════════════════
#  餐馆管理 —— 增·删·查（接入盲盒页面）
# ══════════════════════════════════════════════════════════════════════

@blindbox_bp.route('', methods=['GET'])
def list_restaurants():
    """获取当前用户的所有餐馆。

    Query Parameters
    ----------------
    user_id : int  — 登录用户的 ID

    Returns
    -------
    JSON
        {"code": 200, "data": [{id, name, tags, is_spicy, price_range}, ...]}
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '请提供 user_id'}), 400

    restaurants = (
        db.session.query(Restaurant)
        .filter_by(user_id=user_id)
        .order_by(Restaurant.id.desc())
        .all()
    )

    return jsonify({
        'code': 200,
        'data': [{
            'id': r.id,
            'name': r.name,
            'tags': r.tags,
            'is_spicy': r.is_spicy,
            'price_range': r.price_range or '',
        } for r in restaurants],
    }), 200


@blindbox_bp.route('', methods=['POST'])
def add_restaurant():
    """新增一家餐馆到当前用户的餐馆库。

    Request JSON
    ------------
    user_id : int        — 归属用户 ID
    name : str           — 餐馆名称（必填）
    tags : str           — 标签，逗号分隔（必填）
    is_spicy : bool      — 是否辣（默认 false）
    price_range : str    — 价格区间，如 "人均50-80"

    Returns
    -------
    JSON
        {"code": 201, "data": {id, name, ...}}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    user_id = data.get('user_id')
    name = (data.get('name') or '').strip()
    tags = (data.get('tags') or '').strip()

    # 校验
    if not user_id:
        return jsonify({'code': 400, 'message': '请提供 user_id'}), 400
    if db.session.get(User, user_id) is None:
        return jsonify({'code': 400, 'message': '用户不存在'}), 400
    if not name:
        return jsonify({'code': 400, 'message': '餐馆名称不能为空'}), 400
    if not tags:
        return jsonify({'code': 400, 'message': '标签不能为空'}), 400

    restaurant = Restaurant(
        user_id=user_id,
        name=name,
        tags=tags,
        is_spicy=bool(data.get('is_spicy', False)),
        price_range=(data.get('price_range') or '').strip() or None,
    )
    db.session.add(restaurant)
    db.session.commit()

    return jsonify({
        'code': 201,
        'message': '添加成功',
        'data': {
            'id': restaurant.id,
            'name': restaurant.name,
            'tags': restaurant.tags,
            'is_spicy': restaurant.is_spicy,
            'price_range': restaurant.price_range or '',
        },
    }), 201


@blindbox_bp.route('/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id: int):
    """删除一家餐馆（仅 owner 可删）。

    通过查询参数传入 user_id 验证所有权。

    Query Parameters
    ----------------
    user_id : int  — 当前登录用户 ID

    Returns
    -------
    JSON
        {"code": 200, "message": "已删除"}
        {"code": 404, "message": "餐馆不存在"}
        {"code": 403, "message": "无权操作"}
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': '请提供 user_id'}), 400

    restaurant = db.session.get(Restaurant, restaurant_id)
    if restaurant is None:
        return jsonify({'code': 404, 'message': '餐馆不存在'}), 404

    if restaurant.user_id != user_id:
        return jsonify({'code': 403, 'message': '无权操作'}), 403

    db.session.delete(restaurant)
    db.session.commit()
    return jsonify({'code': 200, 'message': '已删除'}), 200
