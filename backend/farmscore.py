"""
farmscore.py
Core scoring logic for the Farm Score Project.
"""

WEIGHTS = {
    "soil_health": 0.30,
    "water_efficiency": 0.25,
    "biodiversity": 0.20,
    "practices": 0.25,
}

MAX_INPUT = 10.0  # Input scores should be between 0 and 10


def calculate_score(data: dict) -> dict:
    """
    Calculate a farm's sustainability score.

    Expected input:
        farm_name (str)
        soil_health (0-10)
        water_usage_efficiency (0-10)
        biodiversity_score (0-10)
        irrigation_type ('drip', 'sprinkler', 'flood', 'rainfed')
        crop_type (str)

    Returns:
        dict containing:
            farm_name
            total_score
            grade
            breakdown
            recommendations
    """

    soil = _clamp(data.get("soil_health", 0))
    water = _clamp(data.get("water_usage_efficiency", 0))
    biodiversity = _clamp(data.get("biodiversity_score", 0))
    practices = _practices_score(data)

    breakdown = {
        "soil_health": round(soil * WEIGHTS["soil_health"] * 10, 2),
        "water_efficiency": round(water * WEIGHTS["water_efficiency"] * 10, 2),
        "biodiversity": round(biodiversity * WEIGHTS["biodiversity"] * 10, 2),
        "practices": round(practices * WEIGHTS["practices"] * 10, 2),
    }

    total_score = round(sum(breakdown.values()), 2)

    return {
        "farm_name": data.get("farm_name", "Unknown Farm"),
        "total_score": total_score,
        "grade": _grade(total_score),
        "breakdown": breakdown,
        "recommendations": _recommendations(data, breakdown),
    }


# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------

def _clamp(value, lo=0.0, hi=MAX_INPUT):
    """Ensure a numeric value stays within range."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return lo

    return max(lo, min(value, hi))


def _practices_score(data: dict) -> float:
    """Calculate farming practices score (0-10)."""

    score = 5.0

    irrigation_bonus = {
        "drip": 3.0,
        "sprinkler": 1.5,
        "rainfed": 2.0,
        "flood": -1.0,
    }

    irrigation = str(data.get("irrigation_type", "")).strip().lower()
    score += irrigation_bonus.get(irrigation, 0)

    crop = str(data.get("crop_type", "")).strip()

    # Bonus for descriptive crop information
    if len(crop) > 5:
        score += 0.5

    return _clamp(score)


def _grade(score: float) -> str:
    """Convert numeric score into grade."""

    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def _recommendations(data: dict, breakdown: dict) -> list:
    """Generate improvement recommendations."""

    recommendations = []

    if breakdown["soil_health"] < 20:
        recommendations.append(
            "Improve soil health using compost, cover crops, or crop rotation."
        )

    if breakdown["water_efficiency"] < 15:
        recommendations.append(
            "Adopt drip irrigation to improve water-use efficiency."
        )

    if breakdown["biodiversity"] < 12:
        recommendations.append(
            "Increase biodiversity by planting hedgerows or wildflower strips."
        )

    if breakdown["practices"] < 15:
        irrigation = str(data.get("irrigation_type", "")).strip().lower()

        if irrigation == "flood":
            recommendations.append(
                "Replace flood irrigation with drip or sprinkler irrigation."
            )
        else:
            recommendations.append(
                "Adopt additional sustainable farming practices."
            )

    if not recommendations:
        recommendations.append(
            "Excellent sustainability performance. Continue current practices."
        )

    return recommendations
