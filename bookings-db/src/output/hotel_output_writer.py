"""Module for writing hotel data to output files in various formats (JSON, Excel, CSV, MD)."""

import json
from io import TextIOWrapper
from typing import cast, Dict, List, Any

import pandas as pd

def generate_file_json_for_hotels(hotels: List[Dict[str, Any]], output_path: str) -> None:
    """Generate a JSON file containing hotel data.

    Args:
        hotels: List of hotel dictionaries
        output_path: Directory path where the file will be saved
    """
    filename = f"{output_path}hotels.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump({"Hotels": hotels}, cast(TextIOWrapper, file), indent=4, ensure_ascii=False)

def generate_file_excel_for_hotels(hotels: List[Dict[str, Any]], output_path: str) -> None:
    """Generate an Excel file containing hotel data.

    Args:
        hotels: List of hotel dictionaries
        output_path: Directory path where the file will be saved
    """
    df = pd.DataFrame(hotels)
    filename = f"{output_path}hotels.xlsx"
    df.to_excel(filename, index=False)

def generate_file_csv_for_hotels(hotels: List[Dict[str, Any]], output_path: str) -> None:
    """Generate a CSV file containing hotel data.

    Args:
        hotels: List of hotel dictionaries
        output_path: Directory path where the file will be saved
    """
    df = pd.DataFrame(hotels)
    filename = f"{output_path}hotels.csv"
    df.to_csv(filename, index=False, encoding='utf-8')

def generate_file_csv_for_all_hotels(hotels: List[Dict[str, Any]], output_path: str) -> None:
    """Generate a CSV file containing all hotel data.

    Args:
        hotels: List of hotel dictionaries
        output_path: Directory path where the file will be saved
    """
    df = pd.DataFrame(hotels)
    filename = f"{output_path}all_hotels.csv"
    df.to_csv(filename, index=False, encoding='utf-8')

def generate_file_md_hotel_details(hotels: List[Dict[str, Any]], output_path: str) -> None:
    """Generate a Markdown file containing hotel details.

    Args:
        hotels: List of hotel dictionaries
        output_path: Directory path where the file will be saved
    """
    filename = f"{output_path}hotel_details.md"
    with open(filename, "w", encoding="utf-8") as file:
        for hotel in hotels:
            addr = hotel.get('Address', {})
            city = addr.get('City', 'Unknown')
            country = addr.get('Country', 'Unknown')
            file.write(f"# {hotel['Name']} ({city}, {country})\n\n")
            file.write(f"**Hotel Key:** {hotel['hotelkey']}\n\n")
            file.write(f"**Location:** {country}, {city}\n\n")
            file.write(f"**Address:** {addr.get('Address', '')}\n\n")
            file.write(f"**Zip Code:** {addr.get('ZipCode', '')}\n\n")
            file.write("## Rooms\n\n")
            for room in hotel['Rooms']:
                file.write(f"### Room {room['RoomId']}\n\n")
                file.write(f"- **Floor:** {room['Floor']}\n")
                file.write(f"- **Category:** {room['Category']}\n")
                file.write(f"- **Type:** {room['Type']}\n")
                file.write(f"- **Guests:** {room['Guests']}\n")
                file.write(f"- **Price (Off Season):** {room['PriceOffSeason']}\n")
                file.write(f"- **Price (Peak Season):** {room['PricePeakSeason']}\n\n")
            file.write("---\n\n")

def generate_file_md_hotel_rooms(hotels: List[Dict[str, Any]], output_path: str) -> None:
    """Generate a Markdown file containing hotel room details.

    Args:
        hotels: List of hotel dictionaries
        output_path: Directory path where the file will be saved
    """
    filename = f"{output_path}hotel_rooms.md"
    with open(filename, "w", encoding="utf-8") as file:
        for hotel in hotels:
            addr = hotel.get('Address', {})
            city = addr.get('City', 'Unknown')
            country = addr.get('Country', 'Unknown')
            file.write(f"# {hotel['Name']} ({city}, {country})\n\n")
            file.write(f"- City: {city}\n")
            file.write(f"- Country: {country}\n\n")
            for room in hotel['Rooms']:
                file.write(f"## Room {room['RoomId']} - {room['Category']} {room['Type']} ({city}, {country})\n")
                file.write(f"- Hotel: {hotel['Name']}\n")
                file.write(f"- City: {city}\n")
                file.write(f"- Country: {country}\n")
                file.write(f"- Category: {room['Category']}\n")
                file.write(f"- Type: {room['Type']}\n")
                file.write(f"- Guests: {room['Guests']}\n")
                file.write(f"- Price Off Season: {room['PriceOffSeason']}\n")
                file.write(f"- Price Peak Season: {room['PricePeakSeason']}\n\n")
            file.write("---\n\n")

def generate_file_md_hotel_meal_plans(hotels: List[Dict[str, Any]], output_path: str) -> None:
    """Generate a Markdown file containing meal plan details per hotel.

    Args:
        hotels: List of hotel dictionaries
        output_path: Directory path where the file will be saved
    """
    filename = f"{output_path}hotel_meal_plans.md"
    with open(filename, "w", encoding="utf-8") as file:
        file.write("# Hotel Meal Plans Reference\n\n")
        for hotel in hotels:
            params = hotel.get('SyntheticParams', {})
            weights = params.get('MealPlanWeights', {})
            prices = params.get('MealPlanPrices', {})
            addr = hotel.get('Address', {})
            city = addr.get('City', 'Unknown')
            country = addr.get('Country', 'Unknown')
            file.write(f"## {hotel['Name']} ({city}, {country})\n")
            file.write(f"- Country: {country}\n")
            file.write(f"- City: {city}\n")
            file.write(f"- Stars: {hotel.get('Stars', 'N/A')}\n\n")
            file.write("### Meal Plans Available\n")
            for info in weights.values():
                plan_name = info['name']
                available = 'Yes' if info['weight'] > 0 else 'No'
                price_mult = prices.get(plan_name, 1.0)
                file.write(
                    f"- **{plan_name}**: Available={available},"
                    f" Price multiplier={price_mult}x\n"
                )
            file.write("\n")
