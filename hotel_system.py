"""
hotel_system.py - Unified controller facade for the Hotel Room Booking System.
Binds Rooms, Guests, Services, Bookings, and Dashboard modules.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import date
import database
import rooms
import guests
import services
import bookings
import dashboard


class HotelBookingSystem:
    """Unified manager for the boutique hotel booking system."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        database.init_db(self.db_path)

    # ==================== ROOMS MODULE ====================
    def add_room(self, room_number: str, room_type: str, price_per_night: float) -> Dict[str, Any]:
        """Add a new room (room number, type: Single/Double/Suite, price per night)."""
        return rooms.add_room(room_number, room_type, price_per_night, db_path=self.db_path)

    def list_rooms(self, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """List all rooms with current availability status."""
        return rooms.list_rooms(target_date=target_date, db_path=self.db_path)

    def get_room(self, room_number: str) -> Optional[Dict[str, Any]]:
        """Fetch details of a single room."""
        return rooms.get_room(room_number, db_path=self.db_path)

    def update_room(self, room_number: str, new_type: Optional[str] = None, new_price: Optional[float] = None) -> Dict[str, Any]:
        """Edit/update room details."""
        return rooms.update_room(room_number, new_type=new_type, new_price=new_price, db_path=self.db_path)

    def delete_room(self, room_number: str, target_date: Optional[date] = None) -> bool:
        """Delete a room (only if it has no active/upcoming bookings)."""
        return rooms.delete_room(room_number, target_date=target_date, db_path=self.db_path)

    # ==================== GUESTS MODULE ====================
    def register_guest(self, name: str, email: str = "", phone: str = "") -> Dict[str, Any]:
        """Register a new guest."""
        return guests.register_guest(name, email=email, phone=phone, db_path=self.db_path)

    def list_guests(self) -> List[Dict[str, Any]]:
        """List all guests."""
        return guests.list_guests(db_path=self.db_path)

    def get_guest(self, guest_id: int) -> Optional[Dict[str, Any]]:
        """Get guest details by ID."""
        return guests.get_guest(guest_id, db_path=self.db_path)

    def update_guest(self, guest_id: int, name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        """Edit/update guest details."""
        return guests.update_guest(guest_id, name=name, email=email, phone=phone, db_path=self.db_path)

    # ==================== SERVICES MODULE ====================
    def add_service(self, name: str, description: str, price: float) -> Dict[str, Any]:
        """Add a new service (name, description, price)."""
        return services.add_service(name, description, price, db_path=self.db_path)

    def list_services(self) -> List[Dict[str, Any]]:
        """List all services."""
        return services.list_services(db_path=self.db_path)

    def get_service(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Get service details by ID."""
        return services.get_service(service_id, db_path=self.db_path)

    def update_service(self, service_id: int, name: Optional[str] = None, description: Optional[str] = None, price: Optional[float] = None) -> Dict[str, Any]:
        """Edit/update service details."""
        return services.update_service(service_id, name=name, description=description, price=price, db_path=self.db_path)

    # ==================== BOOKINGS MODULE ====================
    def book_room(
        self,
        room_number: str,
        guest_id: int,
        check_in_date: Union[str, date],
        check_out_date: Union[str, date],
        status: str = "Booked",
        service_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Book a room for a guest (choose room, guest, check-in date, check-out date).
        Checks the room isn't already booked for overlapping dates.
        """
        return bookings.book_room(
            room_number=room_number,
            guest_id=guest_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status=status,
            service_ids=service_ids,
            db_path=self.db_path
        )

    def add_services_to_booking(self, booking_id: int, service_ids: List[int]) -> Dict[str, Any]:
        """Add one or more services to an existing booking."""
        return bookings.add_services_to_booking(booking_id, service_ids, db_path=self.db_path)

    def update_booking_status(self, booking_id: int, new_status: str) -> Dict[str, Any]:
        """Cancel/update a booking status."""
        return bookings.update_booking_status(booking_id, new_status, db_path=self.db_path)

    def cancel_booking(self, booking_id: int) -> Dict[str, Any]:
        """Cancel a booking."""
        return bookings.cancel_booking(booking_id, db_path=self.db_path)

    def get_booking(self, booking_id: int, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Fetch booking details with guest name, room number, total amount, and active flag."""
        return bookings.get_booking_details(booking_id, target_date=target_date, db_path=self.db_path)

    def list_bookings(self, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """List all bookings with guest name, room number, total amount (room cost + services), and active flag."""
        return bookings.list_bookings(target_date=target_date, db_path=self.db_path)

    def filter_bookings(
        self,
        guest_query: Optional[Union[str, int]] = None,
        room_number: Optional[str] = None,
        check_in_date: Optional[Union[str, date]] = None,
        only_active: bool = False,
        target_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Filter bookings by guest, room, or by check-in date, or active status."""
        return bookings.filter_bookings(
            guest_query=guest_query,
            room_number=room_number,
            check_in_date=check_in_date,
            only_active=only_active,
            target_date=target_date,
            db_path=self.db_path
        )

    # ==================== DASHBOARD MODULE ====================
    def get_dashboard(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Dashboard showing: total rooms, occupied rooms today, total guests, today's check-ins and check-outs.
        """
        return dashboard.get_dashboard_summary(target_date=target_date, db_path=self.db_path)
