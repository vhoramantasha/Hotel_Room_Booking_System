"""
seed_data.py - Seeds sample boutique hotel data for demonstration and testing.
"""

from datetime import date, timedelta
from typing import Optional
from hotel_system import HotelBookingSystem


def seed_database(db_path: Optional[str] = None) -> None:
    """Populates the database with initial rooms, guests, services, and bookings."""
    system = HotelBookingSystem(db_path=db_path)
    today = date.today()

    # 1. Seed Rooms
    sample_rooms = [
        ("101", "Single", 100.0),
        ("102", "Single", 120.0),
        ("201", "Double", 180.0),
        ("202", "Double", 200.0),
        ("301", "Suite", 350.0),
    ]
    for r_num, r_type, price in sample_rooms:
        try:
            system.add_room(r_num, r_type, price)
        except ValueError:
            pass  # Already exists

    # 2. Seed Guests
    sample_guests = [
        ("Alice Smith", "alice@example.com", "+1-555-0101"),
        ("Bob Johnson", "bob@example.com", "+1-555-0102"),
        ("Clara Oswald", "clara@example.com", "+1-555-0103"),
        ("David Miller", "david@example.com", "+1-555-0104"),
    ]
    guest_ids = []
    for name, email, phone in sample_guests:
        existing = [g for g in system.list_guests() if g["name"] == name]
        if existing:
            guest_ids.append(existing[0]["guest_id"])
        else:
            g = system.register_guest(name, email, phone)
            guest_ids.append(g["guest_id"])

    # 3. Seed Services
    sample_services = [
        ("Breakfast", "Buffet breakfast with fresh bakery, juices, and coffee", 25.0),
        ("Spa Treatment", "60-minute relaxing aromatherapy massage and sauna access", 120.0),
        ("Airport Pickup", "Private luxury shuttle transfer from the airport to hotel", 50.0),
    ]
    service_ids = []
    for name, desc, price in sample_services:
        existing = [s for s in system.list_services() if s["name"] == name]
        if existing:
            service_ids.append(existing[0]["service_id"])
        else:
            s = system.add_service(name, desc, price)
            service_ids.append(s["service_id"])

    # 4. Seed Bookings if none exist
    current_bookings = system.list_bookings()
    if not current_bookings:
        # Booking 1: Checked In (Active today: today-1 to today+2)
        b1 = system.book_room(
            room_number="101",
            guest_id=guest_ids[0],
            check_in_date=(today - timedelta(days=1)).isoformat(),
            check_out_date=(today + timedelta(days=2)).isoformat(),
            status="Checked In",
            service_ids=[service_ids[0], service_ids[2]]  # Breakfast + Airport Pickup
        )

        # Booking 2: Checking in today (today to today+3)
        b2 = system.book_room(
            room_number="201",
            guest_id=guest_ids[1],
            check_in_date=today.isoformat(),
            check_out_date=(today + timedelta(days=3)).isoformat(),
            status="Booked",
            service_ids=[service_ids[0]]  # Breakfast
        )

        # Booking 3: Checking out today (today-2 to today)
        b3 = system.book_room(
            room_number="202",
            guest_id=guest_ids[2],
            check_in_date=(today - timedelta(days=2)).isoformat(),
            check_out_date=today.isoformat(),
            status="Checked In",
            service_ids=[service_ids[1]]  # Spa
        )

        # Booking 4: Upcoming booking next week (today+5 to today+8)
        b4 = system.book_room(
            room_number="301",
            guest_id=guest_ids[3],
            check_in_date=(today + timedelta(days=5)).isoformat(),
            check_out_date=(today + timedelta(days=8)).isoformat(),
            status="Booked",
            service_ids=[service_ids[0], service_ids[1], service_ids[2]]
        )

    print("Sample hotel data seeded successfully.")


if __name__ == "__main__":
    seed_database()
