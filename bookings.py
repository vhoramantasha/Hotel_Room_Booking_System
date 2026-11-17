"""
bookings.py - Bookings module for the Hotel Room Booking System.

Functional Requirements:
• Book a room for a guest (choose room, guest, check-in date, check-out date) should check
  the room isn't already booked for overlapping dates
• Add one or more services to an existing booking
• Cancel/update a booking status
• List all bookings with guest name, room number, and total amount (room cost + services)
• Filter bookings by guest, room, or by check-in date
• Flag currently active bookings (checked in, not yet checked out)
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional, Union
import sqlite3
from database import get_connection

VALID_BOOKING_STATUSES = ("Booked", "Checked In", "Checked Out", "Cancelled")


def _parse_date(d: Union[str, date]) -> date:
    """Helper to convert string or date into a date object."""
    if isinstance(d, date):
        return d
    try:
        return datetime.strptime(d.strip(), "%Y-%m-%d").date()
    except Exception:
        raise ValueError(f"Invalid date format '{d}'. Expected YYYY-MM-DD.")


def is_active_booking(booking: Dict[str, Any], target_date: Optional[date] = None) -> bool:
    """
    Checks if a booking is currently active (checked in, not yet checked out).
    A booking is active if:
      - Status is 'Checked In' (and not 'Checked Out' or 'Cancelled')
      - OR Status is 'Booked' and check_in_date <= today < check_out_date
    """
    status = booking.get("status")
    if status == "Cancelled" or status == "Checked Out":
        return False

    today = target_date or date.today()
    in_date = _parse_date(booking["check_in_date"])
    out_date = _parse_date(booking["check_out_date"])

    if status == "Checked In":
        # Guest has checked in and has not yet checked out
        return True

    if status == "Booked" and in_date <= today < out_date:
        return True

    return False


def check_room_overlap(
    room_number: str, 
    check_in_date: Union[str, date], 
    check_out_date: Union[str, date], 
    exclude_booking_id: Optional[int] = None, 
    db_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Checks if the given room has an overlapping booking for the requested date interval.
    Two bookings overlap if: check_in < existing_check_out AND check_out > existing_check_in.
    Cancelled bookings are ignored.
    Returns the overlapping booking dict if found, else None.
    """
    in_d = _parse_date(check_in_date)
    out_d = _parse_date(check_out_date)

    if in_d >= out_d:
        raise ValueError("Check-out date must be strictly after check-in date (at least 1 night).")

    in_str = in_d.isoformat()
    out_str = out_d.isoformat()

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        query = """
        SELECT booking_id, room_number, guest_id, check_in_date, check_out_date, status
        FROM bookings
        WHERE room_number = ?
          AND status != 'Cancelled'
          AND check_in_date < ?
          AND check_out_date > ?
        """
        params: List[Any] = [room_number, out_str, in_str]
        if exclude_booking_id is not None:
            query += " AND booking_id != ?"
            params.append(exclude_booking_id)

        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def book_room(
    room_number: str,
    guest_id: int,
    check_in_date: Union[str, date],
    check_out_date: Union[str, date],
    status: str = "Booked",
    service_ids: Optional[List[int]] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Books a room for a guest:
    - Validates guest and room exist
    - Verifies check-in and check-out dates
    - Checks the room isn't already booked for overlapping dates
    - Optionally adds initial services
    """
    room_number = str(room_number).strip()
    norm_status = status.strip().title()
    if norm_status not in VALID_BOOKING_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Allowed: {', '.join(VALID_BOOKING_STATUSES)}")

    in_d = _parse_date(check_in_date)
    out_d = _parse_date(check_out_date)
    if in_d >= out_d:
        raise ValueError("Check-out date must be after check-in date.")

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()

        # Check room exists
        cursor.execute("SELECT room_number, room_type, price_per_night FROM rooms WHERE room_number = ?;", (room_number,))
        room = cursor.fetchone()
        if not room:
            raise ValueError(f"Room '{room_number}' does not exist.")

        # Check guest exists
        cursor.execute("SELECT guest_id, name FROM guests WHERE guest_id = ?;", (guest_id,))
        guest = cursor.fetchone()
        if not guest:
            raise ValueError(f"Guest with ID {guest_id} does not exist.")

        # Check overlap
        overlap = check_room_overlap(room_number, in_d, out_d, db_path=db_path)
        if overlap:
            raise ValueError(
                f"Room '{room_number}' is already booked from {overlap['check_in_date']} "
                f"to {overlap['check_out_date']} (Booking #{overlap['booking_id']}, status: {overlap['status']})."
            )

        with conn:
            cursor.execute(
                """
                INSERT INTO bookings (room_number, guest_id, check_in_date, check_out_date, status)
                VALUES (?, ?, ?, ?, ?);
                """,
                (room_number, guest_id, in_d.isoformat(), out_d.isoformat(), norm_status)
            )
            booking_id = cursor.lastrowid

        # Attach services if provided
        if service_ids:
            add_services_to_booking(booking_id, service_ids, db_path=db_path)

        return get_booking_details(booking_id, db_path=db_path)
    finally:
        conn.close()


def add_services_to_booking(
    booking_id: int, 
    service_ids: List[int], 
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Adds one or more services to an existing booking.
    Calculates prices at current service rates.
    """
    if not service_ids:
        raise ValueError("No services selected to add.")

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT booking_id, status FROM bookings WHERE booking_id = ?;", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            raise ValueError(f"Booking #{booking_id} does not exist.")

        if booking["status"] == "Cancelled":
            raise ValueError(f"Cannot add services to cancelled booking #{booking_id}.")

        with conn:
            for s_id in service_ids:
                cursor.execute("SELECT service_id, name, price FROM services WHERE service_id = ?;", (s_id,))
                srv = cursor.fetchone()
                if not srv:
                    raise ValueError(f"Service with ID {s_id} does not exist.")
                cursor.execute(
                    """
                    INSERT INTO booking_services (booking_id, service_id, service_name, service_price)
                    VALUES (?, ?, ?, ?);
                    """,
                    (booking_id, srv["service_id"], srv["name"], srv["price"])
                )

        return get_booking_details(booking_id, db_path=db_path)
    finally:
        conn.close()


def update_booking_status(
    booking_id: int, 
    new_status: str, 
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cancels or updates the status of a booking ('Booked', 'Checked In', 'Checked Out', 'Cancelled').
    """
    norm_status = new_status.strip().title()
    if norm_status not in VALID_BOOKING_STATUSES:
        raise ValueError(f"Invalid booking status '{new_status}'. Allowed: {', '.join(VALID_BOOKING_STATUSES)}")

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT booking_id FROM bookings WHERE booking_id = ?;", (booking_id,))
        if not cursor.fetchone():
            raise ValueError(f"Booking #{booking_id} does not exist.")

        with conn:
            cursor.execute("UPDATE bookings SET status = ? WHERE booking_id = ?;", (norm_status, booking_id))

        return get_booking_details(booking_id, db_path=db_path)
    finally:
        conn.close()


def cancel_booking(booking_id: int, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience helper to cancel a booking."""
    return update_booking_status(booking_id, "Cancelled", db_path=db_path)


def get_booking_details(
    booking_id: int, 
    target_date: Optional[date] = None, 
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetches full booking details including guest name, room number, nights,
    services breakdown, and total amount (room cost + services).
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            b.booking_id,
            b.room_number,
            r.room_type,
            r.price_per_night,
            b.guest_id,
            g.name AS guest_name,
            g.phone AS guest_phone,
            g.email AS guest_email,
            b.check_in_date,
            b.check_out_date,
            b.status
        FROM bookings b
        JOIN rooms r ON b.room_number = r.room_number
        JOIN guests g ON b.guest_id = g.guest_id
        WHERE b.booking_id = ?;
        """
        cursor.execute(query, (booking_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Booking #{booking_id} not found.")

        # Fetch services
        cursor.execute(
            "SELECT id, service_id, service_name, service_price FROM booking_services WHERE booking_id = ? ORDER BY id ASC;",
            (booking_id,)
        )
        services_rows = cursor.fetchall()
        services = [
            {
                "id": s["id"],
                "service_id": s["service_id"],
                "name": s["service_name"],
                "price": s["service_price"]
            }
            for s in services_rows
        ]

        in_d = _parse_date(row["check_in_date"])
        out_d = _parse_date(row["check_out_date"])
        nights = max(1, (out_d - in_d).days)
        room_cost = nights * row["price_per_night"]
        services_cost = sum(s["price"] for s in services)
        total_amount = room_cost + services_cost

        booking_data = {
            "booking_id": row["booking_id"],
            "room_number": row["room_number"],
            "room_type": row["room_type"],
            "price_per_night": row["price_per_night"],
            "guest_id": row["guest_id"],
            "guest_name": row["guest_name"],
            "guest_phone": row["guest_phone"],
            "guest_email": row["guest_email"],
            "check_in_date": row["check_in_date"],
            "check_out_date": row["check_out_date"],
            "nights": nights,
            "room_cost": room_cost,
            "services": services,
            "services_cost": services_cost,
            "total_amount": total_amount,
            "status": row["status"]
        }
        booking_data["is_active"] = is_active_booking(booking_data, target_date=target_date)
        return booking_data
    finally:
        conn.close()


def list_bookings(
    target_date: Optional[date] = None, 
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Lists all bookings with guest name, room number, total amount (room cost + services),
    and active status flag.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT booking_id FROM bookings ORDER BY booking_id DESC;")
        ids = [r["booking_id"] for r in cursor.fetchall()]
        return [get_booking_details(b_id, target_date=target_date, db_path=db_path) for b_id in ids]
    finally:
        conn.close()


def filter_bookings(
    guest_query: Optional[Union[str, int]] = None,
    room_number: Optional[str] = None,
    check_in_date: Optional[Union[str, date]] = None,
    only_active: bool = False,
    target_date: Optional[date] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filters bookings by:
    - Guest (by guest name substring or guest ID)
    - Room (by room number)
    - Check-in date (by specific date YYYY-MM-DD)
    - Optional active filter
    """
    all_b = list_bookings(target_date=target_date, db_path=db_path)
    filtered = []

    for b in all_b:
        # Filter by guest
        if guest_query is not None and str(guest_query).strip():
            g_q = str(guest_query).strip().lower()
            guest_match = (
                str(b["guest_id"]) == g_q or
                g_q in b["guest_name"].lower()
            )
            if not guest_match:
                continue

        # Filter by room
        if room_number is not None and str(room_number).strip():
            if b["room_number"].strip().lower() != str(room_number).strip().lower():
                continue

        # Filter by check-in date
        if check_in_date is not None and str(check_in_date).strip():
            target_in_str = _parse_date(check_in_date).isoformat()
            if b["check_in_date"] != target_in_str:
                continue

        # Filter by active
        if only_active and not b["is_active"]:
            continue

        filtered.append(b)

    return filtered
