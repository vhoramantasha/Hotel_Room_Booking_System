"""
services.py - Services module for the Hotel Room Booking System.

Functional Requirements:
• Add a new service (name, description, price)
• List all services
• Edit/update service details
"""

from typing import List, Dict, Any, Optional
import sqlite3
from database import get_connection


def add_service(name: str, description: str, price: float, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Adds a new service (e.g. Breakfast, Spa, Airport Pickup).
    Validates service name is non-empty and price is non-negative.
    """
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Service name cannot be empty.")

    try:
        val_price = float(price)
        if val_price < 0:
            raise ValueError("Service price cannot be negative.")
    except (ValueError, TypeError):
        raise ValueError("Service price must be a valid number.")

    cleaned_desc = description.strip() if description else ""

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO services (name, description, price) VALUES (?, ?, ?);",
                (cleaned_name, cleaned_desc, val_price)
            )
            service_id = cursor.lastrowid

        return {
            "service_id": service_id,
            "name": cleaned_name,
            "description": cleaned_desc,
            "price": val_price
        }
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e).upper():
            raise ValueError(f"Service '{cleaned_name}' already exists.")
        raise e
    finally:
        conn.close()


def list_services(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lists all available services.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT service_id, name, description, price FROM services ORDER BY service_id ASC;")
        rows = cursor.fetchall()
        return [
            {
                "service_id": row["service_id"],
                "name": row["name"],
                "description": row["description"],
                "price": row["price"]
            }
            for row in rows
        ]
    finally:
        conn.close()


def get_service(service_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetches details of a single service by service_id.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT service_id, name, description, price FROM services WHERE service_id = ?;", (service_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "service_id": row["service_id"],
            "name": row["name"],
            "description": row["description"],
            "price": row["price"]
        }
    finally:
        conn.close()


def update_service(
    service_id: int, 
    name: Optional[str] = None, 
    description: Optional[str] = None, 
    price: Optional[float] = None, 
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Edits/updates service details (name, description, price).
    """
    existing = get_service(service_id, db_path=db_path)
    if not existing:
        raise ValueError(f"Service with ID {service_id} does not exist.")

    updated_name = existing["name"]
    if name is not None:
        c_name = name.strip()
        if not c_name:
            raise ValueError("Service name cannot be empty.")
        updated_name = c_name

    updated_desc = existing["description"] if description is None else description.strip()

    updated_price = existing["price"]
    if price is not None:
        try:
            val_price = float(price)
            if val_price < 0:
                raise ValueError("Service price cannot be negative.")
            updated_price = val_price
        except (ValueError, TypeError):
            raise ValueError("Service price must be a valid number.")

    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "UPDATE services SET name = ?, description = ?, price = ? WHERE service_id = ?;",
                (updated_name, updated_desc, updated_price, service_id)
            )

        return {
            "service_id": service_id,
            "name": updated_name,
            "description": updated_desc,
            "price": updated_price
        }
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e).upper():
            raise ValueError(f"Service name '{updated_name}' already exists.")
        raise e
    finally:
        conn.close()
