"""
Test script for booking analytics calculations (Phase 4).

This script tests:
- Occupancy rate calculations
- RevPAR calculations
- ADR calculations
- Edge case handling
"""

import asyncio
from agents.booking_analytics import (
    load_hotel_room_counts,
    calculate_occupancy_rate,
    calculate_revpar,
    calculate_adr,
    get_days_in_period
)


def test_room_counts():
    """Test loading hotel room counts."""
    print("\n" + "="*80)
    print("📊 TEST 1: Hotel Room Counts")
    print("="*80)
    
    room_counts = load_hotel_room_counts()
    print(f"\n✅ Loaded room counts for {len(room_counts)} hotels:")
    for hotel, count in room_counts.items():
        print(f"  - {hotel}: {count} rooms")
    
    total = sum(room_counts.values())
    print(f"\n  Total: {total} rooms across all hotels")


def test_occupancy_calculations():
    """Test occupancy rate calculations."""
    print("\n" + "="*80)
    print("📊 TEST 2: Occupancy Rate Calculations")
    print("="*80)
    
    # Test case 1: Obsidian Tower - January 2025 (31 days)
    # From our SQL query: 2011 bookings for Obsidian Tower in 2025
    # Let's assume roughly 1/12 for January: ~168 bookings
    print("\n--- Case 1: Obsidian Tower - January 2025 ---")
    occupancy1 = calculate_occupancy_rate(
        bookings_count=168,
        total_rooms=47,
        period_days=31,
        hotel_name="Obsidian Tower"
    )
    print(f"Result: {occupancy1}%")
    
    # Test case 2: Grand Victoria - Full year 2025
    print("\n--- Case 2: Grand Victoria - Full Year 2025 ---")
    occupancy2 = calculate_occupancy_rate(
        bookings_count=2500,
        total_rooms=78,
        period_days=365,
        hotel_name="Grand Victoria"
    )
    print(f"Result: {occupancy2}%")
    
    # Test case 3: Edge case - zero available rooms
    print("\n--- Case 3: Edge Case - Zero Available Room-Nights ---")
    occupancy3 = calculate_occupancy_rate(
        bookings_count=100,
        total_rooms=0,
        period_days=30
    )
    print(f"Result: {occupancy3}% (should be 0.0)")
    
    # Test case 4: Perfect occupancy (100%)
    print("\n--- Case 4: Perfect Occupancy (100%) ---")
    occupancy4 = calculate_occupancy_rate(
        bookings_count=1500,  # 50 rooms × 30 days
        total_rooms=50,
        period_days=30,
        hotel_name="Test Hotel"
    )
    print(f"Result: {occupancy4}% (should be 100.0)")


def test_revpar_calculations():
    """Test RevPAR calculations."""
    print("\n" + "="*80)
    print("📊 TEST 3: RevPAR Calculations")
    print("="*80)
    
    # Test case 1: Obsidian Tower - January
    print("\n--- Case 1: Obsidian Tower - January 2025 ---")
    revpar1 = calculate_revpar(
        total_revenue=45000.00,
        total_rooms=47,
        period_days=31,
        hotel_name="Obsidian Tower"
    )
    print(f"Result: €{revpar1}/room/night")
    
    # Test case 2: All hotels - Full year
    print("\n--- Case 2: All Hotels - Full Year 2025 ---")
    revpar2 = calculate_revpar(
        total_revenue=10810869.12,  # From our SQL query
        total_rooms=312,  # All hotels
        period_days=365,
        hotel_name="All Hotels"
    )
    print(f"Result: €{revpar2}/room/night")
    
    # Test case 3: Edge case - zero rooms
    print("\n--- Case 3: Edge Case - Zero Available Room-Nights ---")
    revpar3 = calculate_revpar(
        total_revenue=50000.00,
        total_rooms=0,
        period_days=30
    )
    print(f"Result: €{revpar3} (should be 0.0)")


def test_adr_calculations():
    """Test ADR calculations."""
    print("\n" + "="*80)
    print("📊 TEST 4: ADR (Average Daily Rate) Calculations")
    print("="*80)
    
    # Test case 1: Royal Sovereign
    print("\n--- Case 1: Royal Sovereign - 2025 ---")
    adr1 = calculate_adr(
        total_revenue=850000.00,
        bookings_count=2370,  # From our SQL query
        hotel_name="Royal Sovereign"
    )
    print(f"Result: €{adr1}/booking")
    
    # Test case 2: All hotels
    print("\n--- Case 2: All Hotels - 2025 ---")
    adr2 = calculate_adr(
        total_revenue=10810869.12,
        bookings_count=25522,  # From our SQL query
        hotel_name="All Hotels"
    )
    print(f"Result: €{adr2}/booking")
    
    # Test case 3: Edge case - zero bookings
    print("\n--- Case 3: Edge Case - Zero Bookings ---")
    adr3 = calculate_adr(
        total_revenue=100000.00,
        bookings_count=0
    )
    print(f"Result: €{adr3} (should be 0.0)")


def test_period_calculations():
    """Test period day calculations."""
    print("\n" + "="*80)
    print("📊 TEST 5: Period Day Calculations")
    print("="*80)
    
    from datetime import date
    
    # Test case 1: Specific date range
    print("\n--- Case 1: January 1-15, 2025 ---")
    days1 = get_days_in_period(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 15)
    )
    print(f"Result: {days1} days (should be 15)")
    
    # Test case 2: Full month - February (non-leap year)
    print("\n--- Case 2: February 2025 (non-leap) ---")
    days2 = get_days_in_period(year=2025, month=2)
    print(f"Result: {days2} days (should be 28)")
    
    # Test case 3: Full month - February (leap year)
    print("\n--- Case 3: February 2024 (leap year) ---")
    days3 = get_days_in_period(year=2024, month=2)
    print(f"Result: {days3} days (should be 29)")
    
    # Test case 4: Full year
    print("\n--- Case 4: Full Year 2025 ---")
    days4 = get_days_in_period(year=2025)
    print(f"Result: {days4} days (should be 365)")
    
    # Test case 5: Full year (leap)
    print("\n--- Case 5: Full Year 2024 (leap) ---")
    days5 = get_days_in_period(year=2024)
    print(f"Result: {days5} days (should be 366)")


def main():
    """Run all analytics tests."""
    print("\n" + "="*80)
    print("🧪 TESTING BOOKING ANALYTICS - Phase 4")
    print("="*80)
    
    test_room_counts()
    test_occupancy_calculations()
    test_revpar_calculations()
    test_adr_calculations()
    test_period_calculations()
    
    print("\n" + "="*80)
    print("✅ All analytics tests complete!")
    print("="*80)


if __name__ == "__main__":
    main()
