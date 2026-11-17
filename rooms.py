"""
rooms.py - Rooms module for the Hotel Room Booking System.

Functional Requirements:
• Add a new room (room number, type: Single/Double/Suite, price per night)
• List all rooms with current availability status
• Edit/update room details
• Delete a room (only if it has no active/upcoming bookings)
"""

from datetime import date
from typing import List, Dict, Any, Optional
import sqlite3
from database import get_connection

VALID_ROOM_TYPES = ("Single", "Double", "Suite")


def add_room(room_number: str, room_type: str, price_per_night: float, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Adds a new room to the system.
    Validates room number uniqueness, room type (Single/Double/Suite), and positive price.
    """
    room_number = str(room_number).strip()
    if not room_number:
        raise ValueError("Room number cannot be empty.")

    normalized_type = room_type.strip().title()
    if normalized_type not in VALID_ROOM_TYPES:
        raise ValueError(f"Invalid room type '{room_type}'. Allowed types: {', '.join(VALID_ROOM_TYPES)}")

    try:
        price = float(price_per_night)
        if price <= 0:
            raise ValueError("Price per night must be greater than 0.")
    except (ValueError, TypeError):
        raise ValueError("Price per night must be a valid positive number.")

    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "INSERT INTO rooms (room_number, room_type, price_per_night) VALUES (?, ?, ?);",
                (room_number, normalized_type, price)
            )
        return {
            "room_number": room_number,
            "room_type": normalized_type,
            "price_per_night": price
        }
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e).upper() or "PRIMARY KEY" in str(e).upper():
            raise ValueError(f"Room number '{room_number}' already exists.")
        raise e
    finally:
        conn.close()


def list_rooms(target_date: Optional[date] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lists all rooms with their current availability status for the target date (defaults to today).
    Availability is 'Occupied' if an active booking covers the date, else 'Available'.
    """
    check_date_str = (target_date or date.today()).isoformat()
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        # Query rooms and check if occupied today
        # A booking occupies a room if status is 'Checked In' or (status = 'Booked' and check_in <= today < check_out)
        query = """
        SELECT 
            r.room_number,
            r.room_type,
            r.price_per_night,
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM bookings b 
                    WHERE b.room_number = r.room_number 
                      AND b.status != 'Cancelled'
                      AND (
                          b.status = 'Checked In' 
                          OR (b.status = 'Booked' AND b.check_in_date <= ? AND b.check_out_date > ?)
                      )
                ) THEN 'Occupied'
                ELSE 'Available'
            END AS availability_status
        FROM rooms r
        ORDER BY r.room_number ASC;
        """
        cursor.execute(query, (check_date_str, check_date_str))
        rows = cursor.fetchall()
        return [
            {
                "room_number": row["room_number"],
                "room_type": row["room_type"],
                "price_per_night": row["price_per_night"],
                "availability_status": row["availability_status"]
            }
            for row in rows
        ]
    finally:
        conn.close()


def get_room(room_number: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetches details of a single room by its room number."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT room_number, room_type, price_per_night FROM rooms WHERE room_number = ?;", (room_number,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "room_number": row["room_number"],
            "room_type": row["room_type"],
            "price_per_night": row["price_per_night"]
        }
    finally:
        conn.close()


def update_room(
    room_number: str, 
    new_type: Optional[str] = None, 
    new_price: Optional[float] = None, 
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Edits/updates room details (type, price per night).
    """
    existing = get_room(room_number, db_path=db_path)
    if not existing:
        raise ValueError(f"Room '{room_number}' not found.")

    updated_type = existing["room_type"]
    if new_type is not None:
        norm_type = new_type.strip().title()
        if norm_type not in VALID_ROOM_TYPES:
            raise ValueError(f"Invalid room type '{new_type}'. Allowed types: {', '.join(VALID_ROOM_TYPES)}")
        updated_type = norm_type

    updated_price = existing["price_per_night"]
    if new_price is not None:
        try:
            val_price = float(new_price)
            if val_price <= 0:
                raise ValueError("Price per night must be greater than 0.")
            updated_price = val_price
        except (ValueError, TypeError):
            raise ValueError("Price per night must be a valid positive number.")

    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "UPDATE rooms SET room_type = ?, price_per_night = ? WHERE room_number = ?;",
                (updated_type, updated_price, room_number)
            )
        return {
            "room_number": room_number,
            "room_type": updated_type,
            "price_per_night": updated_price
        }
    finally:
        conn.close()


def delete_room(room_number: str, target_date: Optional[date] = None, db_path: Optional[str] = None) -> bool:
    """
    Deletes a room only if it has no active or upcoming bookings.
    Raises ValueError if active or upcoming bookings exist.
    """
    existing = get_room(room_number, db_path=db_path)
    if not existing:
        raise ValueError(f"Room '{room_number}' does not exist.")

    today_str = (target_date or date.today()).isoformat()
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        # Check active or upcoming bookings:
        # A booking is active if status is 'Checked In'.
        # A booking is upcoming if status != 'Cancelled' and check_out_date >= today.
        check_query = """
        SELECT booking_id, status, check_in_date, check_out_date
        FROM bookings
        WHERE room_number = ?
          AND status != 'Cancelled'
          AND (status = 'Checked In' OR check_out_date >= ?)
        ORDER BY check_in_date ASC;
        """
        cursor.execute(check_query, (room_number, today_str))
        active_or_upcoming = cursor.fetchall()

        if active_or_upcoming:
            details = ", ".join(
                f"[Booking #{b['booking_id']} ({b['status']}): {b['check_in_date']} to {b['check_out_date']}]"
                for b in active_or_upcoming
            )
            raise ValueError(
                f"Cannot delete room '{room_number}': room has {len(active_or_upcoming)} active/upcoming booking(s): {details}."
            )

        with conn:
            # Also clean up any historical cancelled or past bookings if any
            cursor.execute("DELETE FROM booking_services WHERE booking_id IN (SELECT booking_id FROM bookings WHERE room_number = ?);", (room_number,))
            cursor.execute("DELETE FROM bookings WHERE room_number = ?;", (room_number,))
            cursor.execute("DELETE FROM rooms WHERE room_number = ?;", (room_number,))

        return True
    finally:
        conn.close()
