"""
main.py - Interactive Command-Line Interface (CLI) for the Hotel Room Booking System.
Strictly implements the functional requirements for Rooms, Guests, Services, Bookings, and Dashboard.
"""

import sys
from datetime import date
from typing import Optional
from hotel_system import HotelBookingSystem
from seed_data import seed_database


def print_header(title: str) -> None:
    print("\n" + "=" * 65)
    print(f" {title.upper()} ".center(65, "="))
    print("=" * 65)


def prompt_input(prompt: str, default: Optional[str] = None) -> str:
    if default:
        res = input(f"{prompt} [{default}]: ").strip()
        return res if res else default
    return input(f"{prompt}: ").strip()


class HotelCLI:
    def __init__(self):
        self.system = HotelBookingSystem()
        self.currency = "USD"
        self.usd_to_inr = 83.0

    def format_price(self, usd_amount: float) -> str:
        if self.currency == "INR":
            return f"₹{usd_amount * self.usd_to_inr:,.2f}"
        return f"${usd_amount:,.2f}"

    def get_currency_symbol(self) -> str:
        return "₹" if self.currency == "INR" else "$"

    def toggle_currency(self):
        self.currency = "INR" if self.currency == "USD" else "USD"
        print(f"\n[✓] Currency switched to: {self.currency} ({self.get_currency_symbol()}) [Rate: 1 USD = ₹{self.usd_to_inr:.2f}]")

    def run(self):
        # Auto-seed initial data if brand new database
        if not self.system.list_rooms():
            seed_database()

        while True:
            print_header("Boutique Hotel Room Booking System")
            print(f"Currency: {self.currency} ({self.get_currency_symbol()})")
            print("1. Dashboard (Overview & Detailed Activity)")
            print("2. Rooms Module")
            print("3. Guests Module")
            print("4. Services Module")
            print("5. Bookings Module")
            print(f"6. Price Option (USD / INR) [Current: {self.currency}]")
            print("0. Exit")
            choice = input("\nEnter choice (0-6): ").strip()

            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.menu_rooms()
            elif choice == "3":
                self.menu_guests()
            elif choice == "4":
                self.menu_services()
            elif choice == "5":
                self.menu_bookings()
            elif choice == "6":
                self.toggle_currency()
            elif choice == "0":
                print("\nThank you for using the Hotel Room Booking System. Goodbye!\n")
                sys.exit(0)
            else:
                print("\n[!] Invalid choice. Please enter a number between 0 and 6.")

    # =========================================================================
    # DASHBOARD
    # =========================================================================
    def show_dashboard(self):
        while True:
            print_header("Hotel Dashboard")
            data = self.system.get_dashboard()
            print(f"Report Date           : {data['date']}")
            print(f"Active Currency       : {self.currency} ({self.get_currency_symbol()})")
            print(f"Total Rooms           : {data['total_rooms']}")
            print(f"Occupied Rooms Today  : {data['occupied_rooms_today']}")
            print(f"Total Guests          : {data['total_guests']}")
            print(f"Today's Check-ins     : {data['todays_check_ins_count']}")
            print(f"Today's Check-outs    : {data['todays_check_outs_count']}")

            print("\n--- DASHBOARD DETAILS & ACTIONS ---")
            print("1. View Occupied Rooms Details (Today)")
            print("2. View All Rooms Details & Availability Status")
            print("3. View All Registered Guests Details")
            print("4. View Today's Check-ins & Check-outs")
            print("0. Back to Main Menu")
            d_choice = input("\nEnter choice (0-4): ").strip()

            if d_choice == "1":
                self.show_occupied_rooms_details(data.get("occupied_rooms", []))
            elif d_choice == "2":
                self.action_list_rooms()
            elif d_choice == "3":
                self.action_list_guests()
            elif d_choice == "4":
                self.show_checkins_checkouts(data)
            elif d_choice == "0":
                break
            else:
                print("\n[!] Invalid choice. Please choose 0-4.")

    def show_occupied_rooms_details(self, occupied_rooms: list):
        print("\n[Occupied Rooms Today - Full Details]")
        if not occupied_rooms:
            print("No rooms are currently occupied today.")
            return

        print(f"{'Room':<8} {'Type':<10} {'Price/Night':<14} {'Current Guest':<20} {'Phone':<16} {'Stay Dates':<25} {'Status':<12}")
        print("-" * 105)
        for o in occupied_rooms:
            dates = f"{o['check_in_date']} to {o['check_out_date']}"
            phone = o.get('guest_phone') or '-'
            price_str = self.format_price(o['price_per_night'])
            print(f"{o['room_number']:<8} {o['room_type']:<10} {price_str:<14} {o['guest_name']:<20} {phone:<16} {dates:<25} {o['status']:<12}")

    def show_checkins_checkouts(self, data: dict):
        print("\n--- TODAY'S CHECK-INS ---")
        if data["todays_check_ins"]:
            for b in data["todays_check_ins"]:
                print(f"• Booking #{b['booking_id']} | Guest: {b['guest_name']} | Room: {b['room_number']} ({b['room_type']}) | Status: {b['status']} | Total: {self.format_price(b['total_amount'])}")
        else:
            print("  No check-ins scheduled for today.")

        print("\n--- TODAY'S CHECK-OUTS ---")
        if data["todays_check_outs"]:
            for b in data["todays_check_outs"]:
                print(f"• Booking #{b['booking_id']} | Guest: {b['guest_name']} | Room: {b['room_number']} ({b['room_type']}) | Status: {b['status']} | Total: {self.format_price(b['total_amount'])}")
        else:
            print("  No check-outs scheduled for today.")

    # =========================================================================
    # ROOMS MODULE
    # =========================================================================
    def menu_rooms(self):
        while True:
            print_header("Rooms Module")
            print("1. Add a new room")
            print("2. List all rooms with current availability status")
            print("3. Edit/update room details")
            print("4. Delete a room (only if no active/upcoming bookings)")
            print("0. Back to Main Menu")
            choice = input("\nEnter choice (0-4): ").strip()

            if choice == "1":
                self.action_add_room()
            elif choice == "2":
                self.action_list_rooms()
            elif choice == "3":
                self.action_edit_room()
            elif choice == "4":
                self.action_delete_room()
            elif choice == "0":
                break
            else:
                print("\n[!] Invalid choice. Please choose 0-4.")

    def action_add_room(self):
        print("\n[Add New Room]")
        r_num = prompt_input("Room Number (e.g. 105)")
        print("Room Types: Single, Double, Suite")
        r_type = prompt_input("Room Type")
        price = prompt_input(f"Price per Night ({self.get_currency_symbol()})")
        try:
            val = float(price)
            val_usd = val / self.usd_to_inr if self.currency == "INR" else val
            room = self.system.add_room(r_num, r_type, val_usd)
            print(f"\n[✓] Room {room['room_number']} ({room['room_type']}) added successfully at {self.format_price(room['price_per_night'])}/night.")
        except Exception as e:
            print(f"\n[Error] {e}")

    def action_list_rooms(self):
        print("\n[List All Rooms with Availability Status]")
        rooms_list = self.system.list_rooms()
        if not rooms_list:
            print("No rooms found in the system.")
            return

        print(f"{'Room':<10} {'Type':<12} {'Price/Night':<16} {'Availability Status':<20}")
        print("-" * 62)
        for r in rooms_list:
            status_tag = f"[{r['availability_status'].upper()}]"
            print(f"{r['room_number']:<10} {r['room_type']:<12} {self.format_price(r['price_per_night']):<16} {status_tag:<20}")

    def action_edit_room(self):
        print("\n[Edit Room Details]")
        r_num = prompt_input("Enter room number to edit")
        room = self.system.get_room(r_num)
        if not room:
            print(f"[Error] Room '{r_num}' not found.")
            return

        cur_price_disp = room['price_per_night'] * self.usd_to_inr if self.currency == "INR" else room['price_per_night']
        print(f"Current Details: Type = {room['room_type']}, Price = {self.format_price(room['price_per_night'])}")
        new_type = prompt_input(f"New Room Type (Single/Double/Suite)", default=room['room_type'])
        new_price = prompt_input(f"New Price per Night ({self.get_currency_symbol()})", default=f"{cur_price_disp:.2f}")

        try:
            val = float(new_price)
            val_usd = val / self.usd_to_inr if self.currency == "INR" else val
            updated = self.system.update_room(r_num, new_type=new_type, new_price=val_usd)
            print(f"\n[✓] Room {updated['room_number']} updated: Type={updated['room_type']}, Price={self.format_price(updated['price_per_night'])}")
        except Exception as e:
            print(f"\n[Error] {e}")

    def action_delete_room(self):
        print("\n[Delete Room]")
        r_num = prompt_input("Enter room number to delete")
        try:
            self.system.delete_room(r_num)
            print(f"\n[✓] Room '{r_num}' deleted successfully.")
        except Exception as e:
            print(f"\n[Error] {e}")

    # =========================================================================
    # GUESTS MODULE
    # =========================================================================
    def menu_guests(self):
        while True:
            print_header("Guests Module")
            print("1. Register a new guest")
            print("2. List all guests")
            print("3. Edit/update guest details")
            print("0. Back to Main Menu")
            choice = input("\nEnter choice (0-3): ").strip()

            if choice == "1":
                self.action_register_guest()
            elif choice == "2":
                self.action_list_guests()
            elif choice == "3":
                self.action_edit_guest()
            elif choice == "0":
                break
            else:
                print("\n[!] Invalid choice. Please choose 0-3.")

    def action_register_guest(self):
        print("\n[Register New Guest]")
        name = prompt_input("Full Name")
        email = prompt_input("Email (optional)")
        phone = prompt_input("Phone Number (optional)")
        try:
            guest = self.system.register_guest(name, email, phone)
            print(f"\n[✓] Guest registered successfully with ID: #{guest['guest_id']} ({guest['name']})")
        except Exception as e:
            print(f"\n[Error] {e}")

    def action_list_guests(self):
        print("\n[List All Guests]")
        guests_list = self.system.list_guests()
        if not guests_list:
            print("No guests found in the system.")
            return

        print(f"{'ID':<6} {'Name':<24} {'Email':<28} {'Phone':<18}")
        print("-" * 76)
        for g in guests_list:
            print(f"#{g['guest_id']:<5} {g['name']:<24} {g['email']:<28} {g['phone']:<18}")

    def action_edit_guest(self):
        print("\n[Edit Guest Details]")
        g_id_str = prompt_input("Enter Guest ID to edit")
        try:
            g_id = int(g_id_str)
        except ValueError:
            print("[Error] Invalid Guest ID.")
            return

        guest = self.system.get_guest(g_id)
        if not guest:
            print(f"[Error] Guest with ID #{g_id} not found.")
            return

        print(f"Current Details: Name: {guest['name']}, Email: {guest['email']}, Phone: {guest['phone']}")
        new_name = prompt_input("New Name", default=guest["name"])
        new_email = prompt_input("New Email", default=guest["email"])
        new_phone = prompt_input("New Phone", default=guest["phone"])

        try:
            updated = self.system.update_guest(g_id, name=new_name, email=new_email, phone=new_phone)
            print(f"\n[✓] Guest #{g_id} updated successfully.")
        except Exception as e:
            print(f"\n[Error] {e}")

    # =========================================================================
    # SERVICES MODULE
    # =========================================================================
    def menu_services(self):
        while True:
            print_header("Services Module")
            print("1. Add a new service")
            print("2. List all services")
            print("3. Edit/update service details")
            print("0. Back to Main Menu")
            choice = input("\nEnter choice (0-3): ").strip()

            if choice == "1":
                self.action_add_service()
            elif choice == "2":
                self.action_list_services()
            elif choice == "3":
                self.action_edit_service()
            elif choice == "0":
                break
            else:
                print("\n[!] Invalid choice. Please choose 0-3.")

    def action_add_service(self):
        print("\n[Add New Service]")
        name = prompt_input("Service Name (e.g. Airport Pickup, Spa, Breakfast)")
        desc = prompt_input("Description")
        price = prompt_input(f"Price ({self.get_currency_symbol()})")
        try:
            val = float(price)
            val_usd = val / self.usd_to_inr if self.currency == "INR" else val
            srv = self.system.add_service(name, desc, val_usd)
            print(f"\n[✓] Service '{srv['name']}' added successfully with ID #{srv['service_id']} at {self.format_price(srv['price'])}")
        except Exception as e:
            print(f"\n[Error] {e}")

    def action_list_services(self):
        print("\n[List All Services]")
        services_list = self.system.list_services()
        if not services_list:
            print("No services found in the system.")
            return

        print(f"{'ID':<6} {'Name':<22} {'Price':<14} {'Description':<35}")
        print("-" * 77)
        for s in services_list:
            print(f"#{s['service_id']:<5} {s['name']:<22} {self.format_price(s['price']):<14} {s['description']:<35}")

    def action_edit_service(self):
        print("\n[Edit Service Details]")
        s_id_str = prompt_input("Enter Service ID to edit")
        try:
            s_id = int(s_id_str)
        except ValueError:
            print("[Error] Invalid Service ID.")
            return

        srv = self.system.get_service(s_id)
        if not srv:
            print(f"[Error] Service #{s_id} not found.")
            return

        cur_price_disp = srv['price'] * self.usd_to_inr if self.currency == "INR" else srv['price']
        print(f"Current Details: Name: {srv['name']}, Price: {self.format_price(srv['price'])}, Description: {srv['description']}")
        new_name = prompt_input("New Name", default=srv["name"])
        new_desc = prompt_input("New Description", default=srv["description"])
        new_price = prompt_input(f"New Price ({self.get_currency_symbol()})", default=f"{cur_price_disp:.2f}")

        try:
            val = float(new_price)
            val_usd = val / self.usd_to_inr if self.currency == "INR" else val
            updated = self.system.update_service(s_id, name=new_name, description=new_desc, price=val_usd)
            print(f"\n[✓] Service #{s_id} updated successfully: Price = {self.format_price(updated['price'])}.")
        except Exception as e:
            print(f"\n[Error] {e}")

    # =========================================================================
    # BOOKINGS MODULE
    # =========================================================================
    def menu_bookings(self):
        while True:
            print_header("Bookings Module")
            print("1. Book a room for a guest (checks overlapping dates)")
            print("2. Add one or more services to an existing booking")
            print("3. Cancel / update a booking status")
            print("4. List all bookings (guest name, room number, total amount)")
            print("5. Filter bookings by guest, room, or check-in date")
            print("6. Flag & list currently active bookings")
            print("0. Back to Main Menu")
            choice = input("\nEnter choice (0-6): ").strip()

            if choice == "1":
                self.action_book_room()
            elif choice == "2":
                self.action_add_services_to_booking()
            elif choice == "3":
                self.action_update_booking_status()
            elif choice == "4":
                self.action_list_bookings()
            elif choice == "5":
                self.action_filter_bookings()
            elif choice == "6":
                self.action_list_active_bookings()
            elif choice == "0":
                break
            else:
                print("\n[!] Invalid choice. Please choose 0-6.")

    def action_book_room(self):
        print("\n[Book a Room for a Guest]")
        r_num = prompt_input("Room Number")
        g_id_str = prompt_input("Guest ID")
        try:
            g_id = int(g_id_str)
        except ValueError:
            print("[Error] Guest ID must be an integer.")
            return

        check_in = prompt_input("Check-In Date (YYYY-MM-DD)")
        check_out = prompt_input("Check-Out Date (YYYY-MM-DD)")

        # Optional initial services
        print("\nAvailable Services:")
        all_services = self.system.list_services()
        for s in all_services:
            print(f"  #{s['service_id']}: {s['name']} ({self.format_price(s['price'])})")
        service_input = prompt_input("Enter Service IDs to add (comma separated, or press Enter for none)")

        service_ids = []
        if service_input:
            try:
                service_ids = [int(x.strip()) for x in service_input.split(",") if x.strip()]
            except ValueError:
                print("[Error] Service IDs must be integers.")
                return

        try:
            booking = self.system.book_room(
                room_number=r_num,
                guest_id=g_id,
                check_in_date=check_in,
                check_out_date=check_out,
                service_ids=service_ids
            )
            print(f"\n[✓] Booking #{booking['booking_id']} created successfully!")
            print(f"    Guest        : {booking['guest_name']}")
            print(f"    Room         : {booking['room_number']} ({booking['room_type']})")
            print(f"    Dates        : {booking['check_in_date']} to {booking['check_out_date']} ({booking['nights']} night(s))")
            print(f"    Room Cost    : {self.format_price(booking['room_cost'])}")
            if booking["services"]:
                srv_str = ", ".join(f"{s['name']} ({self.format_price(s['price'])})" for s in booking["services"])
                print(f"    Services     : {srv_str} (Subtotal: {self.format_price(booking['services_cost'])})")
            print(f"    Total Amount : {self.format_price(booking['total_amount'])}")
            print(f"    Status       : {booking['status']}")
        except Exception as e:
            print(f"\n[Booking Failed] {e}")

    def action_add_services_to_booking(self):
        print("\n[Add Services to an Existing Booking]")
        b_id_str = prompt_input("Enter Booking ID")
        try:
            b_id = int(b_id_str)
        except ValueError:
            print("[Error] Booking ID must be an integer.")
            return

        try:
            booking = self.system.get_booking(b_id)
        except Exception as e:
            print(f"[Error] {e}")
            return

        print(f"\nBooking #{b_id} for {booking['guest_name']} (Room {booking['room_number']})")
        if booking["services"]:
            print("Current Services:")
            for s in booking["services"]:
                print(f"  - {s['name']} ({self.format_price(s['price'])})")

        print("\nAvailable Services:")
        all_services = self.system.list_services()
        for s in all_services:
            print(f"  #{s['service_id']}: {s['name']} ({self.format_price(s['price'])})")

        service_input = prompt_input("Enter Service IDs to add (comma separated)")
        try:
            service_ids = [int(x.strip()) for x in service_input.split(",") if x.strip()]
            updated = self.system.add_services_to_booking(b_id, service_ids)
            print(f"\n[✓] Services added to Booking #{b_id}!")
            print(f"    Updated Services Cost : {self.format_price(updated['services_cost'])}")
            print(f"    New Total Amount      : {self.format_price(updated['total_amount'])}")
        except Exception as e:
            print(f"\n[Error] {e}")

    def action_update_booking_status(self):
        print("\n[Cancel / Update Booking Status]")
        b_id_str = prompt_input("Enter Booking ID")
        try:
            b_id = int(b_id_str)
        except ValueError:
            print("[Error] Booking ID must be an integer.")
            return

        try:
            booking = self.system.get_booking(b_id)
            print(f"Current status for Booking #{b_id}: {booking['status']}")
            print("Options: Booked | Checked In | Checked Out | Cancelled")
            new_status = prompt_input("New Status")
            updated = self.system.update_booking_status(b_id, new_status)
            print(f"\n[✓] Booking #{b_id} status updated to '{updated['status']}'.")
        except Exception as e:
            print(f"\n[Error] {e}")

    def action_list_bookings(self, bookings_list: Optional[list] = None):
        if bookings_list is None:
            print("\n[All Bookings]")
            bookings_list = self.system.list_bookings()

        if not bookings_list:
            print("No bookings found.")
            return

        print(f"{'ID':<5} {'Guest Name':<18} {'Room':<6} {'Check-In':<11} {'Check-Out':<11} {'Status':<12} {'Total':<14} {'Active?':<8}")
        print("-" * 88)
        for b in bookings_list:
            active_badge = "[ACTIVE]" if b["is_active"] else ""
            print(
                f"#{b['booking_id']:<4} {b['guest_name']:<18} {b['room_number']:<6} "
                f"{b['check_in_date']:<11} {b['check_out_date']:<11} {b['status']:<12} "
                f"{self.format_price(b['total_amount']):<14} {active_badge:<8}"
            )

    def action_filter_bookings(self):
        print("\n[Filter Bookings]")
        print("Leave blank any filter you wish to skip.")
        g_q = prompt_input("Filter by Guest (Name or Guest ID)")
        r_num = prompt_input("Filter by Room Number")
        in_date = prompt_input("Filter by Check-In Date (YYYY-MM-DD)")

        try:
            filtered = self.system.filter_bookings(
                guest_query=g_q if g_q else None,
                room_number=r_num if r_num else None,
                check_in_date=in_date if in_date else None
            )
            print(f"\n[Filtered Results: {len(filtered)} booking(s) matched]")
            self.action_list_bookings(filtered)
        except Exception as e:
            print(f"\n[Error] {e}")

    def action_list_active_bookings(self):
        print("\n[Currently Active Bookings (Checked In, Not Yet Checked Out)]")
        active = self.system.filter_bookings(only_active=True)
        if not active:
            print("No currently active bookings.")
            return
        self.action_list_bookings(active)


if __name__ == "__main__":
    cli = HotelCLI()
    cli.run()
