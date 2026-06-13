"""
盲盒餐馆权重计算器（纯 Python 算法，不依赖数据库）。

══════════════════════════════════════════════════════════════════════
设计原则：
  - 纯函数：输入餐馆列表 + 场景参数 → 输出中奖结果
  - 无数据库依赖：方便单元测试
  - 可扩展：新增加成规则只需修改常量和循环逻辑

算法流程：
  ① 硬过滤：排除辣味餐馆（如果用户选了"不吃辣"）
  ② 基础权重：每家餐馆起步 10 分
  ③ 夜间加成（22:00–04:00）：宵夜/烧烤标签 → 权重设为 30（3 倍）
  ④ 天气加成（雨天/寒冷）：砂锅粥/火锅/养生标签 → +10 分
  ⑤ 加权随机抽取：random.choices(..., weights=...) 选出一家

使用方式：
  from app.utils.blindbox_weight import calculate_restaurant_weight
  result = calculate_restaurant_weight(restaurants, exclude_spicy, weather)
  if result:
      print(result.restaurant.name, result.weight, result.boosts)
══════════════════════════════════════════════════════════════════════
"""
import random
from datetime import datetime
from dataclasses import dataclass, field


# ── 数据结构 ────────────────────────────────────────────────────────

@dataclass
class WeightResult:
    """单次盲盒抽取的结果。

    Attributes
    ----------
    restaurant : object
        中奖的 Restaurant ORM 实例
    weight : int
        该餐馆的最终权重值
    boosts : list[str]
        权重加成原因（人类可读），如 ["夜间推荐：宵夜"]、["天气推荐：火锅"]
    """

    restaurant: object
    weight: int
    boosts: list[str] = field(default_factory=list)


# ── 算法常量（可根据业务需求调整） ──────────────────────────────────

NIGHT_TAGS = {'宵夜', '烧烤'}          # 夜间推荐标签
WEATHER_TAGS = {'砂锅粥', '火锅', '养生'}  # 坏天气推荐标签
NIGHT_START = 22    # 夜间开始时间（22:00）
NIGHT_END = 4       # 夜间结束时间（04:00）
BASE_WEIGHT = 10    # 基础权重
NIGHT_WEIGHT = 30   # 夜间加成权重（替换基础值，即 3×）
WEATHER_BONUS = 10  # 天气加成（叠加值）


# ── 辅助函数 ────────────────────────────────────────────────────────

def _is_night() -> bool:
    """判断当前系统时间是否处于夜间窗口（22:00–04:00）。

    系统时间从 datetime.now() 获取，不需要外部传参。
    """
    hour = datetime.now().hour
    return hour >= NIGHT_START or hour < NIGHT_END


def _parse_tags(tags_str: str) -> set[str]:
    """将数据库中的逗号分隔标签字符串拆成集合。

    例："中餐,宵夜,高性价比" → {"中餐", "宵夜", "高性价比"}

    使用 set 是为了高效做交集运算（判断餐馆是否包含特定标签）。
    """
    if not tags_str:
        return set()
    return {t.strip() for t in tags_str.split(',') if t.strip()}


# ── 核心算法 ────────────────────────────────────────────────────────

def calculate_restaurant_weight(
    restaurants: list,
    exclude_spicy: bool = False,
    current_weather: str | None = None,
    preferred_tags: list[str] | None = None,
) -> WeightResult | None:
    """加权随机抽取 —— 从候选餐馆中选出一家幸运儿。

    Parameters
    ----------
    restaurants : list
        Restaurant ORM 对象列表（必须有 .is_spicy 和 .tags 属性）
    exclude_spicy : bool
        是否排除辣味餐馆（用户选了"今天不吃辣"时为 True）
    current_weather : str | None
        天气标签："雨天" / "寒冷" / None
    preferred_tags : list[str] | None
        用户选中的口味偏好标签，每个匹配 +5 分

    Returns
    -------
    WeightResult | None
        中奖结果，包含餐馆、权重和加成原因。

    算法详解
    --------
    ① 硬过滤（exclude_spicy）
    ② 基础权重（BASE_WEIGHT=10）
    ③ 口味标签匹配加成（+5/匹配标签）
    ④ 夜间加成（NIGHT_WEIGHT=30）
    ⑤ 天气加成（WEATHER_BONUS=+10）
    ⑥ 加权随机抽取
    """
    candidates = list(restaurants)

    # ── ① 硬过滤：排除辣味餐馆 ──────────────────────────────────
    if exclude_spicy:
        candidates = [r for r in candidates if not r.is_spicy]

    if not candidates:
        return None

    # ── ② 确定当前生效的加成条件 ────────────────────────────────
    night = _is_night()                              # 现在是夜间吗？
    bad_weather = current_weather in ('雨天', '寒冷')  # 天气不好吗？

    # ── ③ 逐餐馆计算权重 ────────────────────────────────────────
    scores: list[int] = []
    boosts_per: list[list[str]] = []

    for r in candidates:
        weight = BASE_WEIGHT
        reasons: list[str] = []
        tags = _parse_tags(r.tags)

        # 夜间加成（替换基础值）
        if night and (tags & NIGHT_TAGS):
            weight = NIGHT_WEIGHT
            matched_night = tags & NIGHT_TAGS
            reasons.append(f'夜间推荐：{"、".join(matched_night)}')

        # 天气加成（叠加值）
        if bad_weather and (tags & WEATHER_TAGS):
            weight += WEATHER_BONUS
            matched_w = tags & WEATHER_TAGS
            reasons.append(f'天气推荐：{"、".join(matched_w)}')

        # 口味标签匹配加成（叠加值，每个匹配标签 +5 分）
        if preferred_tags:
            matched_pref = tags & set(preferred_tags)
            if matched_pref:
                bonus = len(matched_pref) * 5
                weight += bonus
                reasons.append(f'口味偏好：{"、".join(sorted(matched_pref))}')

        scores.append(weight)
        boosts_per.append(reasons)

    # ── ④ 加权随机抽取 ─────────────────────────────────────────
    # random.choices 返回的是列表，k=1 表示只抽一个
    winner = random.choices(candidates, weights=scores, k=1)[0]
    idx = candidates.index(winner)

    return WeightResult(
        restaurant=winner,
        weight=scores[idx],
        boosts=boosts_per[idx],
    )
