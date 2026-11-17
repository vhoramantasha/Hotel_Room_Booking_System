"""
database.py - Database connection and schema initialization for the Hotel Room Booking System.
Uses SQLite for zero-dependency, reliable local persistence.
"""

import sqlite3
import os
from typing import Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotel.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database with row factory enabled."""
    path = db_path if db_path is not None else DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes tables for rooms, guests, services, bookings, and booking_services."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS rooms (
        room_number TEXT PRIMARY KEY,
        room_type TEXT NOT NULL CHECK(room_type IN ('Single', 'Double', 'Suite')),
        price_per_night REAL NOT NULL CHECK(price_per_night > 0)
    );

    CREATE TABLE IF NOT EXISTS guests (
        guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT
    );

    CREATE TABLE IF NOT EXISTS services (
        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        price REAL NOT NULL CHECK(price >= 0)
    );

    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT NOT NULL,
        guest_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,
        check_out_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Booked' CHECK(status IN ('Booked', 'Checked In', 'Checked Out', 'Cancelled')),
        FOREIGN KEY (room_number) REFERENCES rooms(room_number) ON UPDATE CASCADE,
        FOREIGN KEY (guest_id) REFERENCES guests(guest_id) ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS booking_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        service_name TEXT NOT NULL,
        service_price REAL NOT NULL,
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
        FOREIGN KEY (service_id) REFERENCES services(service_id) ON UPDATE CASCADE
    );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
