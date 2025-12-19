"""
Booking Analytics Module

This module provides advanced analytics calculations for hotel bookings,
including occupancy rate, RevPAR (Revenue Per Available Room), and other
hospitality metrics.
"""

from typing import Dict, Optional
from datetime import datetime, date
from decimal import Decimal
import psycopg2

from util.logger_config import logger


# Cache for hotel room counts
_hotel_rooms_cache: Optional[Dict[str, int]] = None

# Database connection string
DB_CONNECTION_STRING = "postgresql://postgres:postgres@localhost:5432/bookings_db"


def load_hotel_room_counts() -> Dict[str, int]:
    """
    Load the total number of rooms per hotel from the database.
    Queries the bookings table to count distinct room_ids per hotel.
    
    Returns:
        Dict mapping hotel names to room counts
    """
    global _hotel_rooms_cache
    
    if _hotel_rooms_cache is not None:
        return _hotel_rooms_cache
    
    try:
        # Connect to database
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Query distinct room counts per hotel
        cursor.execute("""
            SELECT hotel_name, COUNT(DISTINCT room_id) as total_rooms
            FROM bookings
            GROUP BY hotel_name
            ORDER BY hotel_name;
        """)
        
        results = cursor.fetchall()
        room_counts = {hotel_name: int(count) for hotel_name, count in results}
        
        cursor.close()
        conn.close()
        
        _hotel_rooms_cache = room_counts
        logger.info(f"Loaded room counts from database for {len(room_counts)} hotels")
        return room_counts
        
    except Exception as e:
        logger.error(f"Error loading hotel room counts from database: {e}")
        # Return empty dict if database not available
        return {}


def calculate_occupancy_rate(
    bookings_count: int,
    total_rooms: int,
    period_days: int,
    hotel_name: Optional[str] = None
) -> float:
    """
    Calculate occupancy rate for a hotel or all hotels.
    
    Occupancy Rate = (Number of Room-Nights Sold / Total Available Room-Nights) * 100
    
    Args:
        bookings_count: Number of bookings in the period
        total_rooms: Total number of rooms available
        period_days: Number of days in the period
        hotel_name: Optional hotel name for logging
        
    Returns:
        Occupancy rate as percentage (0-100)
    """
    try:
        available_room_nights = total_rooms * period_days
        
        if available_room_nights == 0:
            logger.warning("Cannot calculate occupancy: zero available room-nights")
            return 0.0
        
        occupancy = (bookings_count / available_room_nights) * 100
        
        log_prefix = f"[{hotel_name}] " if hotel_name else ""
        logger.info(
            f"{log_prefix}Occupancy: {bookings_count} bookings / "
            f"{available_room_nights} room-nights = {occupancy:.2f}%"
        )
        
        return round(occupancy, 2)
        
    except Exception as e:
        logger.error(f"Error calculating occupancy rate: {e}")
        return 0.0


def calculate_revpar(
    total_revenue: float,
    total_rooms: int,
    period_days: int,
    hotel_name: Optional[str] = None
) -> float:
    """
    Calculate RevPAR (Revenue Per Available Room).
    
    RevPAR = Total Room Revenue / Total Available Room-Nights
    
    Args:
        total_revenue: Total revenue in the period
        total_rooms: Total number of rooms available
        period_days: Number of days in the period
        hotel_name: Optional hotel name for logging
        
    Returns:
        RevPAR in EUR
    """
    try:
        available_room_nights = total_rooms * period_days
        
        if available_room_nights == 0:
            logger.warning("Cannot calculate RevPAR: zero available room-nights")
            return 0.0
        
        revpar = total_revenue / available_room_nights
        
        log_prefix = f"[{hotel_name}] " if hotel_name else ""
        logger.info(
            f"{log_prefix}RevPAR: €{total_revenue:.2f} / "
            f"{available_room_nights} room-nights = €{revpar:.2f}"
        )
        
        return round(revpar, 2)
        
    except Exception as e:
        logger.error(f"Error calculating RevPAR: {e}")
        return 0.0


def calculate_adr(
    total_revenue: float,
    bookings_count: int,
    hotel_name: Optional[str] = None
) -> float:
    """
    Calculate ADR (Average Daily Rate).
    
    ADR = Total Room Revenue / Number of Rooms Sold
    
    Args:
        total_revenue: Total revenue in the period
        bookings_count: Number of bookings in the period
        hotel_name: Optional hotel name for logging
        
    Returns:
        ADR in EUR
    """
    try:
        if bookings_count == 0:
            logger.warning("Cannot calculate ADR: zero bookings")
            return 0.0
        
        adr = total_revenue / bookings_count
        
        log_prefix = f"[{hotel_name}] " if hotel_name else ""
        logger.info(
            f"{log_prefix}ADR: €{total_revenue:.2f} / "
            f"{bookings_count} bookings = €{adr:.2f}"
        )
        
        return round(adr, 2)
        
    except Exception as e:
        logger.error(f"Error calculating ADR: {e}")
        return 0.0


def format_analytics_response(
    metric_name: str,
    value: float,
    unit: str = "",
    context: Optional[Dict] = None
) -> str:
    """
    Format an analytics response in a user-friendly way.
    
    Args:
        metric_name: Name of the metric (e.g., "Occupancy Rate", "RevPAR")
        value: The calculated value
        unit: Unit of measurement (e.g., "%", "EUR")
        context: Optional context information (hotel name, period, etc.)
        
    Returns:
        Formatted response string
    """
    response = f"**{metric_name}**: {value:,.2f}{unit}"
    
    if context:
        response += "\n\n**Details:**"
        for key, val in context.items():
            response += f"\n- {key}: {val}"
    
    return response


def get_days_in_period(start_date: Optional[date] = None, end_date: Optional[date] = None, year: Optional[int] = None, month: Optional[int] = None) -> int:
    """
    Calculate the number of days in a period.
    
    Args:
        start_date: Start date of period (optional)
        end_date: End date of period (optional)
        year: Year (if calculating for a full year or specific month)
        month: Month (if calculating for a specific month)
        
    Returns:
        Number of days in the period
    """
    try:
        if start_date and end_date:
            return (end_date - start_date).days + 1
        elif year and month:
            # Days in specific month
            if month == 2:
                # Check for leap year
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    return 29
                return 28
            elif month in [4, 6, 9, 11]:
                return 30
            else:
                return 31
        elif year:
            # Days in year
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return 366
            return 365
        else:
            logger.warning("No valid period specified, defaulting to 30 days")
            return 30
    except Exception as e:
        logger.error(f"Error calculating days in period: {e}")
        return 30
