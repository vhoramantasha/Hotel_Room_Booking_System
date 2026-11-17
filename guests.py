"""
guests.py - Guests module for the Hotel Room Booking System.

Functional Requirements:
• Register a new guest
• List all guests
• Edit/update guest details
"""

from typing import List, Dict, Any, Optional
import sqlite3
from database import get_connection


def register_guest(name: str, email: str = "", phone: str = "", db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Registers a new guest.
    Validates that the guest name is non-empty.
    """
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Guest name cannot be empty.")

    cleaned_email = email.strip() if email else ""
    cleaned_phone = phone.strip() if phone else ""

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO guests (name, email, phone) VALUES (?, ?, ?);",
                (cleaned_name, cleaned_email, cleaned_phone)
            )
            guest_id = cursor.lastrowid

        return {
            "guest_id": guest_id,
            "name": cleaned_name,
            "email": cleaned_email,
            "phone": cleaned_phone
        }
    finally:
        conn.close()


def list_guests(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lists all registered guests.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT guest_id, name, email, phone FROM guests ORDER BY guest_id ASC;")
        rows = cursor.fetchall()
        return [
            {
                "guest_id": row["guest_id"],
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"]
            }
            for row in rows
        ]
    finally:
        conn.close()


def get_guest(guest_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetches details of a single guest by guest_id.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT guest_id, name, email, phone FROM guests WHERE guest_id = ?;", (guest_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "guest_id": row["guest_id"],
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"]
        }
    finally:
        conn.close()


def update_guest(
    guest_id: int, 
    name: Optional[str] = None, 
    email: Optional[str] = None, 
    phone: Optional[str] = None, 
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Edits/updates guest details.
    """
    existing = get_guest(guest_id, db_path=db_path)
    if not existing:
        raise ValueError(f"Guest with ID {guest_id} does not exist.")

    updated_name = existing["name"]
    if name is not None:
        c_name = name.strip()
        if not c_name:
            raise ValueError("Guest name cannot be empty.")
        updated_name = c_name

    updated_email = existing["email"] if email is None else email.strip()
    updated_phone = existing["phone"] if phone is None else phone.strip()

    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "UPDATE guests SET name = ?, email = ?, phone = ? WHERE guest_id = ?;",
                (updated_name, updated_email, updated_phone, guest_id)
            )

        return {
            "guest_id": guest_id,
            "name": updated_name,
            "email": updated_email,
            "phone": updated_phone
        }
    finally:
        conn.close()
