"""
Test RAG Bot Queries
Executes test queries and validates responses against actual data
"""

import asyncio
import json
from pathlib import Path
from agents.hotel_rag_agent import answer_hotel_question_rag

# Load actual hotel data for validation
hotels_path = Path(__file__).parent.parent / "bookings-db" / "output_files" / "hotels" / "hotels.json"
with open(hotels_path, 'r', encoding='utf-8') as f:
    hotels_data = json.load(f)['Hotels']

# Create hotel lookup
hotels_by_name = {h['Name']: h for h in hotels_data}
hotels_by_city = {}
for h in hotels_data:
    city = h['Address']['City']
    if city not in hotels_by_city:
        hotels_by_city[city] = []
    hotels_by_city[city].append(h)

print("=" * 80)
print("TESTING RAG BOT QUERIES")
print("=" * 80)
print(f"\nLoaded {len(hotels_data)} hotels for validation\n")

async def test_query(query_num, query, expected_info):
    """Test a single query and validate response"""
    print(f"\n{'='*80}")
    print(f"Query {query_num}: {query}")
    print(f"{'-'*80}")
    
    try:
        response = await answer_hotel_question_rag(query)
        print(f"Response:\n{response}")
        print(f"\n{'~'*80}")
        print(f"Expected: {expected_info}")
        print(f"{'='*80}\n")
        return response
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

async def run_tests():
    """Run all test queries"""
    
    # Test 1: Full address of Obsidian Tower
    obsidian = hotels_by_name.get('Obsidian Tower')
    expected = f"{obsidian['Address']['Address']}, {obsidian['Address']['City']}, {obsidian['Address']['ZipCode']}, {obsidian['Address']['Country']}"
    await test_query(1, "What is the full address of Obsidian Tower?", expected)
    
    # Test 2: Meal charges for Half Board in Royal Sovereign
    royal = hotels_by_name.get('Royal Sovereign')
    hb_multiplier = royal['SyntheticParams']['MealPlanPrices']['Half Board']
    await test_query(2, "What are the meal charges for Half Board in Royal Sovereign?", f"Half Board: {hb_multiplier}x multiplier")
    
    # Test 3: List hotels in Paris
    paris_hotels = [h['Name'] for h in hotels_by_city.get('Paris', [])]
    await test_query(3, "List all hotels in Paris", f"Hotels in Paris: {', '.join(paris_hotels)}")
    
    # Test 4: Extra bed charge in Grand Victoria
    victoria = hotels_by_name.get('Grand Victoria')
    extra_bed = victoria['SyntheticParams']['ExtraBedChargePercentage']
    await test_query(4, "What is the discount for extra bed in Grand Victoria?", f"Extra Bed Charge: {extra_bed}% (NOTE: It's a CHARGE, not discount)")
    
    # Test 5: Meal charges for Room and Breakfast in Nice
    nice_hotels = hotels_by_city.get('Nice', [])
    await test_query(5, "What are the meal charges for Room and Breakfast in hotels in Nice?", f"{len(nice_hotels)} hotels in Nice")
    
    # Test 6: Full address of Imperial Crown
    imperial = hotels_by_name.get('Imperial Crown')
    expected = f"{imperial['Address']['Address']}, {imperial['Address']['City']}, {imperial['Address']['ZipCode']}, {imperial['Address']['Country']}"
    await test_query(6, "What is the full address of Imperial Crown?", expected)
    
    # Test 7: Double room cost peak season in Obsidian Tower
    double_rooms = [r for r in obsidian['Rooms'] if r['Type'] == 'Double']
    if double_rooms:
        prices = [f"€{r['PricePeakSeason']}" for r in double_rooms[:3]]
        await test_query(7, "How much does a double room cost during peak season in Obsidian Tower?", f"Sample prices: {', '.join(prices)}")
    
    # Test 8: How many hotels in France
    france_hotels = [h for h in hotels_data if h['Address']['Country'] == 'France']
    await test_query(19, "How many hotels are there in France?", f"{len(france_hotels)} hotels")
    
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_tests())
