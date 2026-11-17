"""
test_system.py - Comprehensive Unit Test Suite for Hotel Room Booking System.
Verifies all functional requirements across Rooms, Guests, Services, Bookings, and Dashboard.
"""

import unittest
import os
import tempfile
from datetime import date, timedelta
from hotel_system import HotelBookingSystem


class TestHotelBookingSystem(unittest.TestCase):

    def setUp(self):
        # Create a temporary database file for each test
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.system = HotelBookingSystem(db_path=self.db_path)
        self.today = date.today()

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    # =========================================================================
    # 1. ROOMS MODULE TESTS
    # =========================================================================
    def test_add_room_success(self):
        room = self.system.add_room("101", "Single", 120.0)
        self.assertEqual(room["room_number"], "101")
        self.assertEqual(room["room_type"], "Single")
        self.assertEqual(room["price_per_night"], 120.0)

    def test_add_room_validation_errors(self):
        # Invalid type
        with self.assertRaises(ValueError):
            self.system.add_room("102", "Penthouse", 200.0)

        # Invalid price (<= 0)
        with self.assertRaises(ValueError):
            self.system.add_room("103", "Double", 0)
        with self.assertRaises(ValueError):
            self.system.add_room("104", "Suite", -50)

        # Duplicate room
        self.system.add_room("105", "Double", 150.0)
        with self.assertRaises(ValueError):
            self.system.add_room("105", "Double", 160.0)

    def test_list_rooms_with_availability(self):
        self.system.add_room("101", "Single", 100.0)
        self.system.add_room("102", "Double", 150.0)
        guest = self.system.register_guest("John Doe")

        # Initially both are available
        rooms = self.system.list_rooms(target_date=self.today)
        self.assertEqual(len(rooms), 2)
        self.assertEqual(rooms[0]["availability_status"], "Available")
        self.assertEqual(rooms[1]["availability_status"], "Available")

        # Book room 101 spanning today
        self.system.book_room(
            room_number="101",
            guest_id=guest["guest_id"],
            check_in_date=(self.today - timedelta(days=1)).isoformat(),
            check_out_date=(self.today + timedelta(days=2)).isoformat(),
            status="Booked"
        )

        rooms_after = self.system.list_rooms(target_date=self.today)
        r101 = next(r for r in rooms_after if r["room_number"] == "101")
        r102 = next(r for r in rooms_after if r["room_number"] == "102")
        self.assertEqual(r101["availability_status"], "Occupied")
        self.assertEqual(r102["availability_status"], "Available")

    def test_update_room_details(self):
        self.system.add_room("201", "Single", 100.0)
        updated = self.system.update_room("201", new_type="Suite", new_price=300.0)
        self.assertEqual(updated["room_type"], "Suite")
        self.assertEqual(updated["price_per_night"], 300.0)

    def test_delete_room_prevention_on_active_or_upcoming_booking(self):
        self.system.add_room("202", "Double", 150.0)
        guest = self.system.register_guest("Jane Smith")

        # Add upcoming booking
        self.system.book_room(
            room_number="202",
            guest_id=guest["guest_id"],
            check_in_date=(self.today + timedelta(days=3)).isoformat(),
            check_out_date=(self.today + timedelta(days=6)).isoformat(),
            status="Booked"
        )

        # Deletion must fail
        with self.assertRaises(ValueError) as ctx:
            self.system.delete_room("202", target_date=self.today)
        self.assertIn("active/upcoming", str(ctx.exception))

    def test_delete_room_success_when_no_active_bookings(self):
        self.system.add_room("203", "Single", 100.0)
        success = self.system.delete_room("203", target_date=self.today)
        self.assertTrue(success)
        self.assertIsNone(self.system.get_room("203"))

    # =========================================================================
    # 2. GUESTS MODULE TESTS
    # =========================================================================
    def test_register_and_list_guests(self):
        g1 = self.system.register_guest("Alice Walker", "alice@test.com", "1234567890")
        self.assertEqual(g1["name"], "Alice Walker")
        self.assertIsNotNone(g1["guest_id"])

        g_list = self.system.list_guests()
        self.assertEqual(len(g_list), 1)
        self.assertEqual(g_list[0]["name"], "Alice Walker")

    def test_register_guest_empty_name(self):
        with self.assertRaises(ValueError):
            self.system.register_guest("   ")

    def test_update_guest_details(self):
        g = self.system.register_guest("Bob", "bob@old.com", "111")
        updated = self.system.update_guest(g["guest_id"], name="Robert", email="robert@new.com", phone="999")
        self.assertEqual(updated["name"], "Robert")
        self.assertEqual(updated["email"], "robert@new.com")
        self.assertEqual(updated["phone"], "999")

    # =========================================================================
    # 3. SERVICES MODULE TESTS
    # =========================================================================
    def test_add_and_list_services(self):
        s1 = self.system.add_service("Breakfast", "Fresh buffet", 25.0)
        s2 = self.system.add_service("Spa", "Massage", 80.0)
        self.assertEqual(s1["name"], "Breakfast")
        self.assertEqual(s2["price"], 80.0)

        services = self.system.list_services()
        self.assertEqual(len(services), 2)

    def test_add_service_validation(self):
        with self.assertRaises(ValueError):
            self.system.add_service("", "No name", 20.0)
        with self.assertRaises(ValueError):
            self.system.add_service("Gym", "Pass", -10.0)

        # Duplicate
        self.system.add_service("Airport Pickup", "Car transfer", 50.0)
        with self.assertRaises(ValueError):
            self.system.add_service("Airport Pickup", "Duplicate", 60.0)

    def test_update_service_details(self):
        s = self.system.add_service("Laundry", "Wash and iron", 15.0)
        updated = self.system.update_service(s["service_id"], price=20.0, description="Express wash")
        self.assertEqual(updated["price"], 20.0)
        self.assertEqual(updated["description"], "Express wash")

    # =========================================================================
    # 4. BOOKINGS MODULE TESTS
    # =========================================================================
    def test_book_room_and_total_amount(self):
        self.system.add_room("101", "Single", 100.0)
        g = self.system.register_guest("Alice")
        s1 = self.system.add_service("Breakfast", "Morning meal", 20.0)

        # 3 nights stay
        in_d = (self.today + timedelta(days=1)).isoformat()
        out_d = (self.today + timedelta(days=4)).isoformat()

        booking = self.system.book_room(
            room_number="101",
            guest_id=g["guest_id"],
            check_in_date=in_d,
            check_out_date=out_d,
            service_ids=[s1["service_id"]]
        )

        self.assertEqual(booking["nights"], 3)
        self.assertEqual(booking["room_cost"], 300.0)
        self.assertEqual(booking["services_cost"], 20.0)
        self.assertEqual(booking["total_amount"], 320.0)
        self.assertEqual(booking["guest_name"], "Alice")
        self.assertEqual(booking["room_number"], "101")

    def test_overlapping_booking_prevention(self):
        self.system.add_room("101", "Single", 100.0)
        g1 = self.system.register_guest("Alice")
        g2 = self.system.register_guest("Bob")

        base_in = self.today + timedelta(days=10)
        base_out = self.today + timedelta(days=15)

        # First booking: Days 10 to 15
        self.system.book_room(
            room_number="101",
            guest_id=g1["guest_id"],
            check_in_date=base_in.isoformat(),
            check_out_date=base_out.isoformat()
        )

        # Overlap 1: Exact same dates
        with self.assertRaises(ValueError):
            self.system.book_room("101", g2["guest_id"], base_in.isoformat(), base_out.isoformat())

        # Overlap 2: Inside the dates (Days 11 to 13)
        with self.assertRaises(ValueError):
            self.system.book_room("101", g2["guest_id"], (base_in + timedelta(days=1)).isoformat(), (base_out - timedelta(days=1)).isoformat())

        # Overlap 3: Starts before and overlaps into booking (Days 8 to 12)
        with self.assertRaises(ValueError):
            self.system.book_room("101", g2["guest_id"], (base_in - timedelta(days=2)).isoformat(), (base_in + timedelta(days=2)).isoformat())

        # Overlap 4: Starts inside and extends past (Days 13 to 17)
        with self.assertRaises(ValueError):
            self.system.book_room("101", g2["guest_id"], (base_in + timedelta(days=3)).isoformat(), (base_out + timedelta(days=2)).isoformat())

        # Adjacent non-overlapping 1: Ends on Day 10 (Checkout same day as checkin) -> Allowed!
        b_adj1 = self.system.book_room("101", g2["guest_id"], (base_in - timedelta(days=4)).isoformat(), base_in.isoformat())
        self.assertIsNotNone(b_adj1["booking_id"])

        # Adjacent non-overlapping 2: Starts on Day 15 (Checkin same day as checkout) -> Allowed!
        b_adj2 = self.system.book_room("101", g2["guest_id"], base_out.isoformat(), (base_out + timedelta(days=3)).isoformat())
        self.assertIsNotNone(b_adj2["booking_id"])

    def test_add_services_to_existing_booking(self):
        self.system.add_room("101", "Single", 100.0)
        g = self.system.register_guest("Alice")
        s1 = self.system.add_service("Spa", "Massage", 50.0)
        s2 = self.system.add_service("Airport", "Shuttle", 30.0)

        in_d = (self.today + timedelta(days=1)).isoformat()
        out_d = (self.today + timedelta(days=3)).isoformat()

        b = self.system.book_room("101", g["guest_id"], in_d, out_d)
        self.assertEqual(b["total_amount"], 200.0)
        self.assertEqual(len(b["services"]), 0)

        # Add both services
        updated = self.system.add_services_to_booking(b["booking_id"], [s1["service_id"], s2["service_id"]])
        self.assertEqual(len(updated["services"]), 2)
        self.assertEqual(updated["services_cost"], 80.0)
        self.assertEqual(updated["total_amount"], 280.0)

    def test_cancel_and_update_booking_status(self):
        self.system.add_room("101", "Single", 100.0)
        g = self.system.register_guest("Alice")
        b = self.system.book_room("101", g["guest_id"], (self.today + timedelta(days=1)).isoformat(), (self.today + timedelta(days=3)).isoformat())

        # Update to Checked In
        b_checked_in = self.system.update_booking_status(b["booking_id"], "Checked In")
        self.assertEqual(b_checked_in["status"], "Checked In")

        # Cancel booking
        b_cancelled = self.system.cancel_booking(b["booking_id"])
        self.assertEqual(b_cancelled["status"], "Cancelled")

        # Cancelled booking no longer blocks dates!
        g2 = self.system.register_guest("Bob")
        b2 = self.system.book_room("101", g2["guest_id"], (self.today + timedelta(days=1)).isoformat(), (self.today + timedelta(days=3)).isoformat())
        self.assertEqual(b2["status"], "Booked")

    def test_filter_bookings(self):
        self.system.add_room("101", "Single", 100.0)
        self.system.add_room("102", "Double", 200.0)
        g1 = self.system.register_guest("Charlie Brown")
        g2 = self.system.register_guest("Lucy Van Pelt")

        d1 = (self.today + timedelta(days=1)).isoformat()
        d2 = (self.today + timedelta(days=2)).isoformat()
        d3 = (self.today + timedelta(days=4)).isoformat()

        self.system.book_room("101", g1["guest_id"], d1, d2)
        self.system.book_room("102", g2["guest_id"], d2, d3)

        # Filter by guest name
        f_guest = self.system.filter_bookings(guest_query="Charlie")
        self.assertEqual(len(f_guest), 1)
        self.assertEqual(f_guest[0]["guest_name"], "Charlie Brown")

        # Filter by room
        f_room = self.system.filter_bookings(room_number="102")
        self.assertEqual(len(f_room), 1)
        self.assertEqual(f_room[0]["room_number"], "102")

        # Filter by check-in date
        f_date = self.system.filter_bookings(check_in_date=d1)
        self.assertEqual(len(f_date), 1)
        self.assertEqual(f_date[0]["check_in_date"], d1)

    def test_flag_active_bookings(self):
        self.system.add_room("101", "Single", 100.0)
        self.system.add_room("102", "Double", 200.0)
        g = self.system.register_guest("Active Guest")

        # Booking active today
        b_active = self.system.book_room(
            "101", g["guest_id"],
            (self.today - timedelta(days=1)).isoformat(),
            (self.today + timedelta(days=2)).isoformat(),
            status="Checked In"
        )

        # Booking future (not active today)
        b_future = self.system.book_room(
            "102", g["guest_id"],
            (self.today + timedelta(days=5)).isoformat(),
            (self.today + timedelta(days=7)).isoformat(),
            status="Booked"
        )

        # Check active flags
        b_active_details = self.system.get_booking(b_active["booking_id"], target_date=self.today)
        b_future_details = self.system.get_booking(b_future["booking_id"], target_date=self.today)
        self.assertTrue(b_active_details["is_active"])
        self.assertFalse(b_future_details["is_active"])

        # Filter only active
        active_list = self.system.filter_bookings(only_active=True, target_date=self.today)
        self.assertEqual(len(active_list), 1)
        self.assertEqual(active_list[0]["booking_id"], b_active["booking_id"])

    # =========================================================================
    # 5. DASHBOARD TESTS
    # =========================================================================
    def test_dashboard_metrics(self):
        self.system.add_room("101", "Single", 100.0)
        self.system.add_room("102", "Double", 150.0)
        self.system.add_room("103", "Suite", 250.0)
        g1 = self.system.register_guest("Guest One")
        g2 = self.system.register_guest("Guest Two")
        g3 = self.system.register_guest("Guest Three")

        # 1. Booking checking in today
        self.system.book_room(
            "101", g1["guest_id"],
            self.today.isoformat(),
            (self.today + timedelta(days=2)).isoformat()
        )

        # 2. Booking checking out today
        self.system.book_room(
            "102", g2["guest_id"],
            (self.today - timedelta(days=2)).isoformat(),
            self.today.isoformat(),
            status="Checked In"
        )

        dash = self.system.get_dashboard(target_date=self.today)
        self.assertEqual(dash["total_rooms"], 3)
        self.assertEqual(dash["total_guests"], 3)
        self.assertEqual(dash["todays_check_ins_count"], 1)
        self.assertEqual(dash["todays_check_outs_count"], 1)
        self.assertGreaterEqual(dash["occupied_rooms_today"], 1)
        # Verify detailed lists
        self.assertEqual(len(dash["all_rooms"]), 3)
        self.assertEqual(len(dash["all_guests"]), 3)
        self.assertEqual(len(dash["occupied_rooms"]), 2)
        occupied_numbers = [r["room_number"] for r in dash["occupied_rooms"]]
        self.assertIn("101", occupied_numbers)
        self.assertIn("102", occupied_numbers)


if __name__ == "__main__":
    unittest.main()
