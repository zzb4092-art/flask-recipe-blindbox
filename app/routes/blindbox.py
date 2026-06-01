"""Blind-box restaurant picker blueprint."""
import re
from flask import Blueprint, request, jsonify

from app import db
from app.models import Restaurant
from app.utils.blindbox_weight import calculate_restaurant_weight

blindbox_bp = Blueprint('blindbox', __name__, url_prefix='/api/restaurants')


def _extract_max_price(price_range: str) -> int | None:
    """Parse the upper bound of a price_range string like '人均120-180'.

    Returns the max price as int, or None if unparseable.
    """
    if not price_range:
        return None
    numbers = re.findall(r'\d+', price_range)
    if not numbers:
        return None
    return max(int(n) for n in numbers)


def _filter_by_budget(candidates: list, budget: str) -> list:
    """Filter restaurants by budget bracket.

    Parameters
    ----------
    candidates : list of Restaurant
    budget : str
        One of ``'low'`` (≤30), ``'mid'`` (30–80), ``'high'`` (≥80).

    Returns
    -------
    list of Restaurant
    """
    filtered = []
    for r in candidates:
        max_price = _extract_max_price(r.price_range)
        if max_price is None:
            # Unparseable price → keep it (don't accidentally exclude)
            filtered.append(r)
            continue
        if budget == 'low' and max_price <= 30:
            filtered.append(r)
        elif budget == 'mid' and 30 < max_price <= 80:
            filtered.append(r)
        elif budget == 'high' and max_price > 80:
            filtered.append(r)
        elif budget not in ('low', 'mid', 'high'):
            filtered.append(r)  # unknown value → no filter
    return filtered


@blindbox_bp.route('/blindbox', methods=['POST'])
def draw_restaurant():
    """Draw one restaurant using the smart weight algorithm.

    Request JSON
    ------------
    user_id : int
        ID of the current user.
    exclude_spicy : bool
        Whether to filter out spicy restaurants.
    user_weather : str or null
        Weather label, e.g. ``"雨天"``, ``"寒冷"``, ``null``.

    Returns
    -------
    JSON
        On success:
        {
          "code": 200,
          "data": {
            "id": 3,
            "name": "xx大排档",
            "tags": "中餐,宵夜,高性价比",
            "is_spicy": false,
            "price_range": "人均50-80",
            "weight": 30,
            "boosts": ["夜间推荐：宵夜"]
          }
        }

        When all restaurants are filtered out:
        {"code": 200, "data": null, "message": "没有符合条件的餐馆"}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求体不能为空'}), 400

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'code': 400, 'message': '请提供 user_id'}), 400

    exclude_spicy = bool(data.get('exclude_spicy', False))
    user_weather = data.get('user_weather')  # str or None
    budget = data.get('budget')  # 'low' | 'mid' | 'high' | None

    # ── Query user's restaurants ─────────────────────────────────
    candidates = (
        db.session.query(Restaurant)
        .filter_by(user_id=user_id)
        .all()
    )

    # ── Budget filter (before weight algorithm) ──────────────────
    if budget:
        candidates = _filter_by_budget(candidates, budget)

    if not candidates:
        return jsonify({
            'code': 200,
            'data': None,
            'message': '该用户还没有添加餐馆',
        }), 200

    # ── Run the weight algorithm ─────────────────────────────────
    result = calculate_restaurant_weight(
        restaurants=candidates,
        exclude_spicy=exclude_spicy,
        current_weather=user_weather,
    )

    if result is None:
        return jsonify({
            'code': 200,
            'data': None,
            'message': '没有符合条件的餐馆',
        }), 200

    r = result.restaurant

    return jsonify({
        'code': 200,
        'data': {
            'id': r.id,
            'name': r.name,
            'tags': r.tags,
            'is_spicy': r.is_spicy,
            'price_range': r.price_range,
            'weight': result.weight,
            'boosts': result.boosts,
        },
    }), 200
