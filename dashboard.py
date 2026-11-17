"""
dashboard.py - Dashboard module for the Hotel Room Booking System.

Functional Requirements:
• A dashboard showing: total rooms, occupied rooms today, total guests, today's check-ins and check-outs
"""

from datetime import date
from typing import Dict, Any, Optional
from database import get_connection
from bookings import get_booking_details
import rooms
import guests


def get_dashboard_summary(target_date: Optional[date] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns dashboard metrics for the hotel:
    - total_rooms: Total count of rooms
    - occupied_rooms_today: Count of rooms occupied today
    - total_guests: Total registered guests
    - todays_check_ins_count: Count of bookings checking in today
    - todays_check_outs_count: Count of bookings checking out today
    - todays_check_ins: Detailed list of today's check-in bookings
    - todays_check_outs: Detailed list of today's check-out bookings
    - occupied_rooms: Detailed list of rooms currently occupied with booking & guest details
    - all_rooms: Complete list of all rooms with availability status
    - all_guests: Complete list of all registered guests
    """
    today_obj = target_date or date.today()
    today_str = today_obj.isoformat()

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()

        # 1. Total rooms
        cursor.execute("SELECT COUNT(*) AS total FROM rooms;")
        total_rooms = cursor.fetchone()["total"]

        # 2. Total guests
        cursor.execute("SELECT COUNT(*) AS total FROM guests;")
        total_guests = cursor.fetchone()["total"]

        # 3. Occupied rooms today
        # Distinct rooms with active booking today
        cursor.execute(
            """
            SELECT COUNT(DISTINCT room_number) AS occupied
            FROM bookings
            WHERE status != 'Cancelled'
              AND (
                  status = 'Checked In' 
                  OR (status = 'Booked' AND check_in_date <= ? AND check_out_date > ?)
              );
            """,
            (today_str, today_str)
        )
        occupied_rooms_today = cursor.fetchone()["occupied"]

        # Detailed occupied rooms with guest and booking information
        cursor.execute(
            """
            SELECT 
                r.room_number,
                r.room_type,
                r.price_per_night,
                b.booking_id,
                b.guest_id,
                g.name AS guest_name,
                g.phone AS guest_phone,
                b.check_in_date,
                b.check_out_date,
                b.status
            FROM rooms r
            JOIN bookings b ON r.room_number = b.room_number
            JOIN guests g ON b.guest_id = g.guest_id
            WHERE b.status != 'Cancelled'
              AND (
                  b.status = 'Checked In'
                  OR (b.status = 'Booked' AND b.check_in_date <= ? AND b.check_out_date > ?)
              )
            ORDER BY r.room_number ASC;
            """,
            (today_str, today_str)
        )
        occupied_rooms = [dict(row) for row in cursor.fetchall()]

        # 4. Today's check-ins
        cursor.execute(
            """
            SELECT booking_id
            FROM bookings
            WHERE check_in_date = ?
              AND status != 'Cancelled'
            ORDER BY booking_id ASC;
            """,
            (today_str,)
        )
        check_in_ids = [r["booking_id"] for r in cursor.fetchall()]

        # 5. Today's check-outs
        cursor.execute(
            """
            SELECT booking_id
            FROM bookings
            WHERE check_out_date = ?
              AND status != 'Cancelled'
            ORDER BY booking_id ASC;
            """,
            (today_str,)
        )
        check_out_ids = [r["booking_id"] for r in cursor.fetchall()]

    finally:
        conn.close()

    todays_check_ins = [get_booking_details(b_id, target_date=today_obj, db_path=db_path) for b_id in check_in_ids]
    todays_check_outs = [get_booking_details(b_id, target_date=today_obj, db_path=db_path) for b_id in check_out_ids]
    all_rooms_list = rooms.list_rooms(target_date=today_obj, db_path=db_path)
    all_guests_list = guests.list_guests(db_path=db_path)

    return {
        "date": today_str,
        "total_rooms": total_rooms,
        "occupied_rooms_today": occupied_rooms_today,
        "total_guests": total_guests,
        "todays_check_ins_count": len(todays_check_ins),
        "todays_check_outs_count": len(todays_check_outs),
        "todays_check_ins": todays_check_ins,
        "todays_check_outs": todays_check_outs,
        "occupied_rooms": occupied_rooms,
        "all_rooms": all_rooms_list,
        "all_guests": all_guests_list
    }
