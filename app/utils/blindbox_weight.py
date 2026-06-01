"""Blind-box restaurant weight calculator.

Pure-Python algorithm — no database dependency, designed for unit-testability.
"""
import random
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class WeightResult:
    """Outcome of a single blind-box draw."""

    restaurant: object          # Restaurant ORM instance
    weight: int                 # Final computed weight
    boosts: list[str] = field(default_factory=list)  # Human-readable boost reasons


# ── keyword constants ───────────────────────────────────────────────
NIGHT_TAGS = {'宵夜', '烧烤'}
WEATHER_TAGS = {'砂锅粥', '火锅', '养生'}
NIGHT_START = 22    # 22:00
NIGHT_END = 4       # 04:00
BASE_WEIGHT = 10
NIGHT_WEIGHT = 30          # replaces base (3×)
WEATHER_BONUS = 10          # additive on top


def _is_night() -> bool:
    """Check whether current system time falls in the night window (22:00–04:00)."""
    hour = datetime.now().hour
    return hour >= NIGHT_START or hour < NIGHT_END


def _parse_tags(tags_str: str) -> set[str]:
    """Split a comma-separated tag string into a set of stripped tokens."""
    if not tags_str:
        return set()
    return {t.strip() for t in tags_str.split(',') if t.strip()}


def calculate_restaurant_weight(
    restaurants: list,
    exclude_spicy: bool = False,
    current_weather: str | None = None,
) -> WeightResult | None:
    """Weighted random draw — pick ONE lucky restaurant.

    Parameters
    ----------
    restaurants : list
        List of Restaurant ORM objects (must have .is_spicy, .tags attributes).
    exclude_spicy : bool
        If True, remove all ``is_spicy == True`` restaurants before drawing.
    current_weather : str | None
        Weather label from frontend, e.g. ``"雨天"``, ``"寒冷"``.

    Returns
    -------
    WeightResult | None
        The winning restaurant and its weight metadata, or **None** if
        every candidate was filtered out.

    Algorithm
    ---------
    1. **Hard filter** — exclude spicy restaurants when requested.
    2. **Base weight** — every restaurant starts at 10.
    3. **Night boost** — between 22:00–04:00, restaurants tagged
       ``宵夜`` or ``烧烤`` get their weight set to 30 (3×).
    4. **Weather boost** — when ``current_weather`` is ``"雨天"`` or
       ``"寒冷"``, restaurants tagged ``砂锅粥`` / ``火锅`` / ``养生``
       receive an extra +10.
    5. **Draw** — ``random.choices(…, weights=…)`` picks the winner.
    """
    candidates = list(restaurants)

    # ── 1. Hard filter: exclude spicy ───────────────────────────
    if exclude_spicy:
        candidates = [r for r in candidates if not r.is_spicy]

    if not candidates:
        return None

    # ── 2. Determine active boosts ──────────────────────────────
    night = _is_night()
    bad_weather = current_weather in ('雨天', '寒冷')

    # ── 3. Calculate per-restaurant weights ─────────────────────
    scores: list[int] = []
    boosts_per: list[list[str]] = []

    for r in candidates:
        weight = BASE_WEIGHT
        reasons: list[str] = []
        tags = _parse_tags(r.tags)

        # Night boost (replaces base when triggered)
        if night and (tags & NIGHT_TAGS):
            weight = NIGHT_WEIGHT
            matched_night = tags & NIGHT_TAGS
            reasons.append(f'夜间推荐：{"、".join(matched_night)}')

        # Weather boost (additive)
        if bad_weather and (tags & WEATHER_TAGS):
            weight += WEATHER_BONUS
            matched_w = tags & WEATHER_TAGS
            reasons.append(f'天气推荐：{"、".join(matched_w)}')

        scores.append(weight)
        boosts_per.append(reasons)

    # ── 4. Weighted random draw ─────────────────────────────────
    winner = random.choices(candidates, weights=scores, k=1)[0]
    idx = candidates.index(winner)

    return WeightResult(
        restaurant=winner,
        weight=scores[idx],
        boosts=boosts_per[idx],
    )
