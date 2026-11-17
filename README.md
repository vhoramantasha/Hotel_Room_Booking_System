# Hotel Room Booking System

A Python-based management system for a boutique hotel to manage rooms, guests, bookings, and add-on services (breakfast, spa, airport pickup, etc.).

---

## 📋 Functional Requirements Implemented

Strictly following the project specification with **no extra, unrequested functionality**:

### 1. Rooms Module (`rooms.py`)
- **Add a new room**: Accepts `room_number`, `room_type` (`Single`, `Double`, or `Suite`), and `price_per_night` (> 0).
- **List all rooms with current availability status**: Dynamically calculates whether each room is currently `Available` or `Occupied` based on active bookings.
- **Edit/update room details**: Update room type and nightly rate.
- **Delete a room**: Guarded deletion that **only succeeds if the room has no active or upcoming bookings**; blocks deletion with a detailed error message if active/upcoming reservations exist.

### 2. Guests Module (`guests.py`)
- **Register a new guest**: Registers guest details (`name`, `email`, `phone`).
- **List all guests**: Displays all registered guests.
- **Edit/update guest details**: Update guest information.

### 3. Services Module (`services.py`)
- **Add a new service**: Create add-on services (`name`, `description`, `price`), such as Breakfast, Spa, Airport Pickup.
- **List all services**: Displays all available hotel services and prices.
- **Edit/update service details**: Update service name, description, and price.

### 4. Bookings Module (`bookings.py`)
- **Book a room for a guest**:
  - Select room, guest, check-in date (`YYYY-MM-DD`), and check-out date (`YYYY-MM-DD`).
  - **Overlapping Dates Check**: Rigorously verifies that the room is not already booked for overlapping dates (`new_check_in < existing_check_out` and `new_check_out > existing_check_in` for active bookings). Adjacent bookings (same-day checkout and checkin) are permitted.
- **Add one or more services to an existing booking**: Attach services to a booking at any time.
- **Cancel/update a booking status**: Update status between `Booked`, `Checked In`, `Checked Out`, and `Cancelled`.
- **List all bookings with guest name, room number, and total amount**:
  - Automatically calculates total amount: $\text{Total Amount} = \text{Room Cost} (\text{nights} \times \text{rate}) + \text{Services Cost}$.
- **Filter bookings**: Filter by guest (name or ID), by room number, or by check-in date.
- **Flag currently active bookings**: Identifies guests who are currently checked in (not yet checked out) and flags them with an `[ACTIVE]` indicator.

### 5. Dashboard (`dashboard.py`)
Provides real-time operational metrics and comprehensive activity overviews:
- **Total Rooms**: Count of all rooms in the hotel with a quick link to **View All Rooms** (displays room number, room type, nightly price, and current availability status).
- **Occupied Rooms Today**: Distinct count of rooms currently occupied today with a quick link to **View Occupied Details** (displays occupied room number, type, nightly rate, guest name, contact phone, check-in, check-out, and status).
- **Total Guests**: Count of all registered guests with a quick link to **View All Guests** (displays guest ID, name, email, and phone).
- **Today's Check-Ins**: Number and details of bookings checking in today.
- **Today's Check-Outs**: Number and details of bookings checking out today.

### 6. Currency Option (USD - INR)
- Switch dynamically between **USD ($)** and **INR (₹)** at 1 USD = ₹83.00.
- All room rates, add-on service prices, booking totals, and dashboard summaries instantly convert and re-render across the entire interface.
- Supported in both the **Web Interface** (top navigation bar toggle) and the **CLI Application** (interactive option 6).

---

## 🗂️ Project Structure

```
LLM_Project_2/
├── database.py       # SQLite connection and table schema initialization
├── rooms.py          # Rooms module (Add, List with availability, Edit, Delete check)
├── guests.py         # Guests module (Register, List, Edit)
├── services.py       # Services module (Add, List, Edit)
├── bookings.py       # Bookings module (Booking, Overlap check, Services, Filter, Active flag)
├── dashboard.py      # Dashboard module (Summary metrics & today's activity)
├── hotel_system.py   # Unified facade controller linking all modules
├── seed_data.py      # Initial boutique hotel sample data for demonstration
├── main.py           # Interactive Command-Line Interface (CLI)
├── app.py            # Modern Web Application (Zero-dependency using standard library)
├── test_system.py    # Automated test suite (19 unit tests covering all requirements)
└── README.md         # Documentation
```

---

## 🚀 How to Run the System

### 1. Interactive Command-Line Interface (CLI)
Run the interactive menu in your terminal:
```bash
python main.py
```
This launches a formatted console menu allowing you to operate all 5 modules directly:
```
=================================================================
============== BOUTIQUE HOTEL ROOM BOOKING SYSTEM ===============
=================================================================
1. Dashboard (Overview & Today's Activity)
2. Rooms Module
3. Guests Module
4. Services Module
5. Bookings Module
0. Exit
```

### 2. Automated Test Suite
Run the comprehensive test suite verifying all functional requirements and edge cases:
```bash
python test_system.py
```
Expected output:
```
...................
----------------------------------------------------------------------
Ran 19 tests in 1.026s

OK
```

### 3. Web Interface (Optional)
Run the zero-dependency web server:
```bash
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```
This presents a clean dashboard with Font Awesome icons, room/guest/service management tables, booking modal, filtering, and live metrics.

---

## 💾 Database Schema

The system uses an embedded SQLite database (`hotel.db`) with Foreign Keys enabled:
- **`rooms`**: `room_number` (PK), `room_type` (`Single`, `Double`, `Suite`), `price_per_night`
- **`guests`**: `guest_id` (PK), `name`, `email`, `phone`
- **`services`**: `service_id` (PK), `name` (UNIQUE), `description`, `price`
- **`bookings`**: `booking_id` (PK), `room_number` (FK), `guest_id` (FK), `check_in_date`, `check_out_date`, `status`
- **`booking_services`**: `id` (PK), `booking_id` (FK), `service_id` (FK), `service_name`, `service_price`
