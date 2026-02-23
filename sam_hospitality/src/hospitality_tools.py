from __future__ import annotations

import json
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

    if "list" in q or "lista" in q or "hoteles" in q:
        subset = _find_hotels_by_city_or_country(hotels, q)
        selected = subset if subset else hotels
        lines = ["### Hoteles encontrados", ""]
        lines.extend(_format_hotel_row(h) for h in selected)
        return "\n".join(lines)

    if "meal" in q or "comida" in q or "plan" in q:
        lines = ["### Planes de comida por hotel", ""]
        for hotel in hotels:
            name = _get_name(hotel)
            meal_plans = _get_meal_plans(hotel)
            meal_text = ", ".join(meal_plans) if meal_plans else "N/A"
            lines.append(f"- **{name}**: {meal_text}")
        return "\n".join(lines)

    if "address" in q or "dirección" in q or "direccion" in q:
        lines = ["### Direcciones", ""]
        for hotel in hotels:
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
