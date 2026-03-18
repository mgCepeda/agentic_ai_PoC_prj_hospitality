from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _hotel_paths() -> Dict[str, Path]:
    root = _workspace_root()
    return {
        "hotels_json": root / "bookings-db" / "output_files" / "hotels" / "hotels.json",
        "hotel_details_md": root / "bookings-db" / "output_files" / "hotels" / "hotel_details.md",
        "hotel_rooms_md": root / "bookings-db" / "output_files" / "hotels" / "hotel_rooms.md",
    }


def _load_hotels() -> List[Dict[str, Any]]:
    paths = _hotel_paths()
    hotels_json = paths["hotels_json"]
    if not hotels_json.exists():
        return []

    with hotels_json.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    hotels = payload.get("hotels")
    if not isinstance(hotels, list):
        hotels = payload.get("Hotels")
    if isinstance(hotels, list):
        return hotels

    if isinstance(payload, list):
        return payload

    return []


def _get_name(hotel: Dict[str, Any]) -> str:
    return str(hotel.get("name") or hotel.get("Name") or "N/A")


def _get_country_city_address(hotel: Dict[str, Any]) -> tuple[str, str, str]:
    address_obj = hotel.get("Address") if isinstance(hotel.get("Address"), dict) else {}
    country = str(
        hotel.get("country")
        or address_obj.get("Country")
        or "N/A"
    )
    city = str(
        hotel.get("city")
        or address_obj.get("City")
        or "N/A"
    )
    address = str(
        hotel.get("address")
        or address_obj.get("Address")
        or "N/A"
    )
    return country, city, address


def _get_meal_plans(hotel: Dict[str, Any]) -> List[str]:
    meal_plans = hotel.get("meal_plans")
    if isinstance(meal_plans, list) and meal_plans:
        return [str(item) for item in meal_plans]

    synthetic_params = hotel.get("SyntheticParams")
    if isinstance(synthetic_params, dict):
        meal_plan_prices = synthetic_params.get("MealPlanPrices")
        if isinstance(meal_plan_prices, dict):
            return [str(key) for key in meal_plan_prices.keys()]

    return []


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _iter_rooms(hotel: Dict[str, Any]) -> List[Dict[str, Any]]:
    rooms = hotel.get("Rooms")
    if isinstance(rooms, list):
        return rooms
    return []


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_meal_multiplier(hotel: Dict[str, Any], meal_name: str) -> float | None:
    synthetic_params = hotel.get("SyntheticParams")
    if not isinstance(synthetic_params, dict):
        return None
    meal_plan_prices = synthetic_params.get("MealPlanPrices")
    if not isinstance(meal_plan_prices, dict):
        return None
    multiplier = meal_plan_prices.get(meal_name)
    return _safe_float(multiplier)


def _room_price_stats(
    hotel: Dict[str, Any],
    room_type: str | None = None,
    category: str | None = None,
) -> Dict[str, float] | None:
    off_prices: List[float] = []
    peak_prices: List[float] = []

    for room in _iter_rooms(hotel):
        room_type_value = str(room.get("Type", "")).lower()
        category_value = str(room.get("Category", "")).lower()

        if room_type and room_type_value != room_type.lower():
            continue
        if category and category_value != category.lower():
            continue

        off = _safe_float(room.get("PriceOffSeason"))
        peak = _safe_float(room.get("PricePeakSeason"))
        if off is not None:
            off_prices.append(off)
        if peak is not None:
            peak_prices.append(peak)

    if not off_prices and not peak_prices:
        return None

    stats: Dict[str, float] = {}
    if off_prices:
        stats["off_min"] = min(off_prices)
        stats["off_avg"] = sum(off_prices) / len(off_prices)
    if peak_prices:
        stats["peak_min"] = min(peak_prices)
        stats["peak_avg"] = sum(peak_prices) / len(peak_prices)
    return stats


def _format_eur(value: float) -> str:
    return f"€{value:.2f}"


def _format_hotel_row(hotel: Dict[str, Any]) -> str:
    name = _get_name(hotel)
    country, city, address = _get_country_city_address(hotel)
    return f"- **{name}** · {city}, {country} · {address}"


def _find_hotels_by_city_or_country(hotels: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    query_norm = _normalize(query)
    matches: List[Dict[str, Any]] = []
    for hotel in hotels:
        country_raw, city_raw, _ = _get_country_city_address(hotel)
        city = _normalize(city_raw)
        country = _normalize(country_raw)
        name = _normalize(_get_name(hotel))
        if city in query_norm or country in query_norm or name in query_norm:
            matches.append(hotel)
    return matches


def _extract_location_hint(query: str) -> str | None:
    query_norm = _normalize(query)
    patterns = [
        r"\bfor hotels in\s+([a-záéíóúñ]+)\b",
        r"\bin\s+([a-záéíóúñ]+)\b",
        r"\ben\s+([a-záéíóúñ]+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, query_norm)
        if match:
            token = match.group(1).strip()
            if token and token not in {"the", "a", "an"}:
                return token
    return None


def _select_hotels_for_query(hotels: List[Dict[str, Any]], query: str) -> tuple[List[Dict[str, Any]], str | None]:
    subset = _find_hotels_by_city_or_country(hotels, query)
    if subset:
        return subset, None

    location_hint = _extract_location_hint(query)
    if location_hint:
        return [], location_hint

    return hotels, None


def query_hospitality_data(question: str) -> str:
    """
    Tool para Solace Agent Mesh.
    Realiza consultas básicas sobre hoteles usando datos sintéticos del workshop.
    """
    hotels = _load_hotels()
    if not hotels:
        paths = _hotel_paths()
        return (
            "No se encontró data de hoteles. Genera primero los datos sintéticos con:\n"
            "`cd bookings-db && python src/gen_synthetic_hotels.py`\n"
            f"Ruta esperada: {paths['hotels_json']}"
        )

    q = _normalize(question)

    has_price_word = ("price" in q) or ("precio" in q)
    has_lowest_word = (
        ("lowest" in q)
        or ("minimum" in q)
        or ("cheapest" in q)
        or ("minimo" in q)
        or ("mínimo" in q)
        or ("mas barato" in q)
        or ("más barato" in q)
    )
    has_single_word = ("single" in q) or ("individual" in q)
    has_standard_word = ("standard" in q) or ("estandar" in q) or ("estándar" in q)
    has_no_meal_word = (
        ("no meal plan" in q)
        or ("room only" in q)
        or ("sin plan" in q)
        or ("sin comida" in q)
        or ("solo habitacion" in q)
        or ("solo habitación" in q)
    )
    has_room_count_intent = (
        ("amount of rooms per type" in q)
        or ("rooms per type" in q)
        or ("room count by type" in q)
        or (("count by type" in q) and ("room" in q))
        or (("how many" in q) and ("room" in q) and ("type" in q))
        or (("cuantas" in q or "cuántas" in q) and ("habitacion" in q or "habitación" in q) and ("tipo" in q))
    )

    # 1) Triple premium prices in a location (off+peak)
    if "price" in q and "triple" in q and "premium" in q and ("paris" in q or "nice" in q or "cannes" in q or "france" in q):
        selected, location_hint = _select_hotels_for_query(hotels, q)
        if not selected and location_hint:
            return f"I couldn't find hotels for location '{location_hint.title()}'."
        lines = ["### Triple Premium Room Prices", ""]
        for hotel in selected:
            stats = _room_price_stats(hotel, room_type="triple", category="premium")
            if not stats:
                continue
            lines.append(f"- **{_get_name(hotel)}**")
            if "off_avg" in stats:
                lines.append(f"  - Off Season: {_format_eur(stats['off_avg'])}")
            if "peak_avg" in stats:
                lines.append(f"  - Peak Season: {_format_eur(stats['peak_avg'])}")
        if len(lines) == 2:
            return "No encontré habitaciones premium triple para esa ubicación."
        return "\n".join(lines)

    # 2) Compare triple off-season + room and breakfast
    if "compare" in q and "triple" in q and "off season" in q and ("room and breakfast" in q or "breakfast" in q):
        selected, location_hint = _select_hotels_for_query(hotels, q)
        if not selected and location_hint:
            return f"I couldn't find hotels for location '{location_hint.title()}'."
        lines = ["### Triple Room Comparison (Off Season + Room and Breakfast)", ""]
        for hotel in selected:
            stats = _room_price_stats(hotel, room_type="triple")
            if not stats or "off_avg" not in stats:
                continue
            multiplier = _get_meal_multiplier(hotel, "Room and Breakfast")
            off_price = stats["off_avg"]
            total = off_price * multiplier if multiplier is not None else None
            lines.append(f"- **{_get_name(hotel)}**")
            lines.append(f"  - Off Season (room): {_format_eur(off_price)}")
            if total is not None:
                lines.append(f"  - Off Season + Room and Breakfast: {_format_eur(total)}")
        if len(lines) == 2:
            return "No encontré datos suficientes para comparar esa consulta."
        return "\n".join(lines)

    # 3) Lowest standard single in location with no meal plan
    if has_price_word and has_single_word and has_no_meal_word and (has_lowest_word or has_standard_word):
        selected, location_hint = _select_hotels_for_query(hotels, q)
        if not selected and location_hint:
            return f"I couldn't find hotels for location '{location_hint.title()}'."
        candidates: List[tuple[str, float]] = []
        for hotel in selected:
            # Prefer standard single, fallback to single if standard rooms are not explicitly requested
            stats = _room_price_stats(hotel, room_type="single", category="standard")
            if (not stats) and (not has_standard_word):
                stats = _room_price_stats(hotel, room_type="single", category=None)
            if not stats or "off_min" not in stats:
                continue
            multiplier = _get_meal_multiplier(hotel, "Room Only")
            effective = stats["off_min"] * (multiplier if multiplier is not None else 1.0)
            candidates.append((_get_name(hotel), effective))

        if not candidates:
            return "No encontré habitaciones standard single para esa ubicación."

        candidates.sort(key=lambda item: item[1])
        lines = ["### Lowest Price: Standard Single (No Meal Plan)", ""]
        for name, price in candidates:
            lines.append(f"- **{name}**: {_format_eur(price)}")
        lines.append("")
        lines.append(f"**Lowest**: {candidates[0][0]} with {_format_eur(candidates[0][1])}")
        return "\n".join(lines)

    # 4) Meal charge for half board in location
    if "meal charge" in q and "half board" in q:
        selected, location_hint = _select_hotels_for_query(hotels, q)
        if not selected and location_hint:
            return f"I couldn't find hotels for location '{location_hint.title()}'."
        lines = ["### Meal Charge for Half Board", ""]
        for hotel in selected:
            multiplier = _get_meal_multiplier(hotel, "Half Board")
            if multiplier is None:
                continue
            uplift_pct = (multiplier - 1.0) * 100
            lines.append(
                f"- **{_get_name(hotel)}**: x{multiplier:.2f} over Room Only ({uplift_pct:.1f}% extra)"
            )
        if len(lines) == 2:
            return "No encontré cargos de Half Board para esa ubicación."
        return "\n".join(lines)

    # 5) Amount of rooms per type in location
    if has_room_count_intent:
        selected, location_hint = _select_hotels_for_query(hotels, q)
        if not selected and location_hint:
            return f"I couldn't find hotels for location '{location_hint.title()}'."
        lines = ["### Room Count by Type", ""]
        for hotel in selected:
            counts = Counter(str(room.get("Type", "Unknown")) for room in _iter_rooms(hotel))
            if not counts:
                continue
            lines.append(f"- **{_get_name(hotel)}**")
            for room_type, count in sorted(counts.items()):
                lines.append(f"  - {room_type}: {count}")
        if len(lines) == 2:
            return "No encontré habitaciones para esa ubicación."
        return "\n".join(lines)

    if "list" in q or "lista" in q or "hoteles" in q:
        selected, location_hint = _select_hotels_for_query(hotels, q)
        if not selected and location_hint:
            return f"I couldn't find hotels for location '{location_hint.title()}'."
        lines = ["### Hoteles encontrados", ""]
        lines.extend(_format_hotel_row(h) for h in selected)
        return "\n".join(lines)

    if "meal" in q or "comida" in q or "plan" in q:
        selected, location_hint = _select_hotels_for_query(hotels, q)
        if not selected and location_hint:
            return f"I couldn't find hotels for location '{location_hint.title()}'."
        lines = ["### Planes de comida por hotel", ""]
        for hotel in selected:
            name = _get_name(hotel)
            meal_plans = _get_meal_plans(hotel)
            meal_text = ", ".join(meal_plans) if meal_plans else "N/A"
            lines.append(f"- **{name}**: {meal_text}")
        return "\n".join(lines)

    if "address" in q or "dirección" in q or "direccion" in q:
        selected, location_hint = _select_hotels_for_query(hotels, q)
        if not selected and location_hint:
            return f"I couldn't find hotels for location '{location_hint.title()}'."
        lines = ["### Direcciones", ""]
        for hotel in selected:
            _, _, address = _get_country_city_address(hotel)
            lines.append(f"- **{_get_name(hotel)}**: {address}")
        return "\n".join(lines)

    sample = hotels[:5]
    lines = [
        "No detecté un patrón específico. Resumen rápido de hoteles:",
        "",
    ]
    lines.extend(_format_hotel_row(h) for h in sample)
    lines.append("")
    lines.append("Sugerencia: prueba preguntas como 'list hotels in France' o 'meal plans in Paris'.")
    return "\n".join(lines)
