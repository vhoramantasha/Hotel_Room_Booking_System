"""
app.py - Zero-dependency Web Interface for the Hotel Room Booking System.
Uses Python's built-in http.server to provide a modern, responsive web dashboard and management portal.
All actions interact with the same underlying SQLite database and modules.
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import date
from typing import Dict, Any
from hotel_system import HotelBookingSystem
from seed_data import seed_database

PORT = 5000
system = HotelBookingSystem()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Boutique Hotel Booking System</title>
  <!-- Font Awesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    :root {
      --primary: #1e3a8a;
      --primary-light: #3b82f6;
      --accent: #d97706;
      --bg: #f8fafc;
      --surface: #ffffff;
      --text: #1e293b;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --success: #15803d;
      --success-bg: #dcfce7;
      --warning: #b45309;
      --warning-bg: #fef3c7;
      --danger: #b91c1c;
      --danger-bg: #fee2e2;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: var(--bg); color: var(--text); display: flex; min-height: 100vh; }
    
    /* Sidebar */
    .sidebar { width: 260px; background: #0f172a; color: white; display: flex; flex-direction: column; flex-shrink: 0; }
    .brand { padding: 24px 20px; border-bottom: 1px solid #1e293b; font-size: 1.15rem; font-weight: 700; letter-spacing: 0.5px; color: #f1f5f9; display: flex; align-items: center; gap: 10px; }
    .brand span { color: #f59e0b; }
    .brand i { color: #f59e0b; font-size: 1.25rem; }
    .nav { list-style: none; padding: 16px 0; flex-grow: 1; }
    .nav li { margin-bottom: 4px; }
    .nav-btn { width: 100%; border: none; background: transparent; color: #94a3b8; padding: 12px 24px; text-align: left; font-size: 0.95rem; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
    .nav-btn i { width: 18px; text-align: center; }
    .nav-btn:hover { color: white; background: #1e293b; }
    .nav-btn.active { color: white; background: var(--primary); font-weight: 600; border-left: 4px solid #f59e0b; }
    
    /* Main Content */
    .main { flex-grow: 1; overflow-y: auto; padding: 32px 40px; }
    .header { margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }
    .header h1 { font-size: 1.75rem; color: #0f172a; }
    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeIn 0.2s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    /* Cards & Stats */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 18px; margin-bottom: 28px; }
    .stat-card { background: var(--surface); padding: 20px; border-radius: 10px; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .stat-label { font-size: 0.825rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); display: flex; align-items: center; gap: 8px; }
    .stat-value { font-size: 2rem; font-weight: 700; color: #0f172a; margin-top: 6px; }

    /* Tables */
    .card { background: var(--surface); border-radius: 10px; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 24px; margin-bottom: 24px; }
    .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 16px; color: #0f172a; display: flex; justify-content: space-between; align-items: center; }
    .card-title-text { display: flex; align-items: center; gap: 8px; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 0.92rem; }
    th { text-align: left; padding: 12px 14px; background: #f8fafc; color: #475569; font-weight: 600; border-bottom: 1px solid var(--border); }
    td { padding: 12px 14px; border-bottom: 1px solid var(--border); color: #334155; }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background-color: #f8fafc; }

    /* Badges */
    .badge { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-available { background: var(--success-bg); color: var(--success); }
    .badge-occupied { background: var(--warning-bg); color: var(--warning); }
    .badge-active { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; font-weight: 700; }
    .badge-cancelled { background: var(--danger-bg); color: var(--danger); }
    .badge-booked { background: #f1f5f9; color: #475569; }

    /* Buttons & Forms */
    .btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 16px; font-size: 0.875rem; font-weight: 500; border-radius: 6px; border: none; cursor: pointer; transition: all 0.15s; }
    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: #1d4ed8; }
    .btn-danger { background: #fee2e2; color: #b91c1c; }
    .btn-danger:hover { background: #fecaca; }
    .btn-outline { background: transparent; border: 1px solid var(--border); color: #334155; }
    .btn-outline:hover { background: #f1f5f9; }
    
    .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
    .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
    label { font-size: 0.85rem; font-weight: 600; color: #475569; }
    input, select, textarea { padding: 9px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 0.9rem; outline: none; background: #fff; }
    input:focus, select:focus, textarea:focus { border-color: var(--primary-light); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15); }
    
    /* Alerts */
    .alert { padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; font-size: 0.9rem; display: none; }
    .alert-success { background: var(--success-bg); color: var(--success); border: 1px solid #bbf7d0; }
    .alert-error { background: var(--danger-bg); color: var(--danger); border: 1px solid #fecaca; }

    /* Currency Switcher & Top Bar */
    .top-nav-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
    .currency-bar { display: inline-flex; align-items: center; gap: 10px; background: var(--surface); padding: 6px 14px; border-radius: 8px; border: 1px solid var(--border); box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
    .currency-label { font-size: 0.825rem; font-weight: 600; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }
    .currency-switch { display: inline-flex; background: #f1f5f9; border-radius: 6px; padding: 2px; }
    .curr-btn { border: none; background: transparent; padding: 4px 10px; border-radius: 5px; font-size: 0.8rem; font-weight: 700; cursor: pointer; color: #64748b; transition: all 0.15s; }
    .curr-btn.active { background: var(--primary); color: white; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    .rate-badge { font-size: 0.75rem; color: var(--text-muted); background: #f8fafc; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border); }

    /* Stat Card Links & Details */
    .stat-card { display: flex; flex-direction: column; justify-content: space-between; }
    .stat-actions { margin-top: 12px; padding-top: 10px; border-top: 1px dashed var(--border); }
    .stat-link { color: var(--primary-light); font-size: 0.8rem; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; cursor: pointer; transition: color 0.15s; }
    .stat-link:hover { color: var(--primary); text-decoration: underline; }

    /* Modal */
    .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: none; align-items: center; justify-content: center; z-index: 1000; }
    .modal { background: white; border-radius: 10px; width: 90%; max-width: 520px; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .modal-header h3 { font-size: 1.2rem; }
    .close-btn { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #64748b; }
    .close-btn:hover { color: #0f172a; }
  </style>
</head>
<body>

  <!-- Navigation Sidebar -->
  <div class="sidebar">
    <div class="brand">
      <i class="fa-solid fa-hotel"></i> Boutique <span>Hotel</span>
    </div>
    <ul class="nav">
      <li><button class="nav-btn active" onclick="switchTab('dashboard')"><i class="fa-solid fa-chart-pie"></i> Dashboard</button></li>
      <li><button class="nav-btn" onclick="switchTab('rooms')"><i class="fa-solid fa-bed"></i> Rooms Module</button></li>
      <li><button class="nav-btn" onclick="switchTab('guests')"><i class="fa-solid fa-users"></i> Guests Module</button></li>
      <li><button class="nav-btn" onclick="switchTab('services')"><i class="fa-solid fa-bell-concierge"></i> Services Module</button></li>
      <li><button class="nav-btn" onclick="switchTab('bookings')"><i class="fa-solid fa-calendar-check"></i> Bookings Module</button></li>
    </ul>
  </div>

  <!-- Main Container -->
  <div class="main">
    <!-- Top Global Bar with Price Currency Option (USD - INR) -->
    <div class="top-nav-bar">
      <div style="font-size: 0.95rem; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 8px;">
        <i class="fa-solid fa-hotel" style="color: var(--primary-light);"></i> Boutique Hotel Management
      </div>
      <div class="currency-bar">
        <span class="currency-label"><i class="fa-solid fa-coins"></i> Currency:</span>
        <div class="currency-switch">
          <button id="btnUSD" class="curr-btn active" onclick="setCurrency('USD')">$ USD</button>
          <button id="btnINR" class="curr-btn" onclick="setCurrency('INR')">₹ INR</button>
        </div>
        <span class="rate-badge">1 USD = ₹83.00</span>
      </div>
    </div>

    <div id="alertBox" class="alert"></div>

    <!-- 1. DASHBOARD TAB -->
    <div id="tab-dashboard" class="tab-content active">
      <div class="header">
        <h1>Dashboard</h1>
        <span id="dashDate" style="color: var(--text-muted); font-size: 0.95rem; font-weight: 500;"></span>
      </div>

      <!-- Stat Cards with Links to Detailed Views -->
      <div class="stats-grid">
        <div class="stat-card">
          <div>
            <div class="stat-label"><i class="fa-solid fa-bed"></i> Total Rooms</div>
            <div class="stat-value" id="statTotalRooms">0</div>
          </div>
          <div class="stat-actions">
            <a href="javascript:void(0)" onclick="scrollToDashCard('dashAllRoomsCard')" class="stat-link">
              <i class="fa-solid fa-table-cells"></i> View All Rooms &rarr;
            </a>
          </div>
        </div>

        <div class="stat-card">
          <div>
            <div class="stat-label"><i class="fa-solid fa-door-closed"></i> Occupied Rooms Today</div>
            <div class="stat-value" id="statOccupiedRooms" style="color: var(--accent);">0</div>
          </div>
          <div class="stat-actions">
            <a href="javascript:void(0)" onclick="scrollToDashCard('dashOccupiedCard')" class="stat-link">
              <i class="fa-solid fa-list-check"></i> View Occupied Details &rarr;
            </a>
          </div>
        </div>

        <div class="stat-card">
          <div>
            <div class="stat-label"><i class="fa-solid fa-users"></i> Total Guests</div>
            <div class="stat-value" id="statTotalGuests">0</div>
          </div>
          <div class="stat-actions">
            <a href="javascript:void(0)" onclick="scrollToDashCard('dashGuestsCard')" class="stat-link">
              <i class="fa-solid fa-address-book"></i> View All Guests &rarr;
            </a>
          </div>
        </div>

        <div class="stat-card">
          <div>
            <div class="stat-label"><i class="fa-solid fa-arrow-right-to-bracket"></i> Today's Check-Ins</div>
            <div class="stat-value" id="statCheckIns" style="color: var(--success);">0</div>
          </div>
          <div class="stat-actions">
            <a href="javascript:void(0)" onclick="scrollToDashCard('dashCheckInsCard')" class="stat-link">
              <i class="fa-solid fa-eye"></i> View Check-Ins &rarr;
            </a>
          </div>
        </div>

        <div class="stat-card">
          <div>
            <div class="stat-label"><i class="fa-solid fa-arrow-right-from-bracket"></i> Today's Check-Outs</div>
            <div class="stat-value" id="statCheckOuts" style="color: #6366f1;">0</div>
          </div>
          <div class="stat-actions">
            <a href="javascript:void(0)" onclick="scrollToDashCard('dashCheckOutsCard')" class="stat-link">
              <i class="fa-solid fa-eye"></i> View Check-Outs &rarr;
            </a>
          </div>
        </div>
      </div>

      <!-- Occupied Rooms Today (Detailed Section) -->
      <div class="card" id="dashOccupiedCard">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-door-closed" style="color: var(--accent);"></i> Occupied Rooms Today (Detailed)</span>
          <span>
            <button class="btn btn-outline" style="font-size:0.75rem;padding:4px 8px;" onclick="switchTab('rooms')"><i class="fa-solid fa-bed"></i> Rooms Module</button>
            <button class="btn btn-outline" style="font-size:0.75rem;padding:4px 8px;" onclick="switchTab('bookings')"><i class="fa-solid fa-calendar-check"></i> Bookings Module</button>
          </span>
        </div>
        <table id="tableOccupiedRooms">
          <thead>
            <tr>
              <th>Room #</th>
              <th>Type</th>
              <th>Price/Night</th>
              <th>Current Guest</th>
              <th>Contact Phone</th>
              <th>Check-In</th>
              <th>Check-Out</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>

      <!-- All Rooms (Detailed Section on Dashboard) -->
      <div class="card" id="dashAllRoomsCard">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-bed" style="color: var(--primary-light);"></i> All Rooms & Availability Overview</span>
          <button class="btn btn-outline" style="font-size:0.75rem;padding:4px 8px;" onclick="switchTab('rooms')"><i class="fa-solid fa-arrow-up-right-from-square"></i> Open Rooms Module</button>
        </div>
        <table id="tableAllRoomsDash">
          <thead>
            <tr>
              <th>Room #</th>
              <th>Room Type</th>
              <th>Price/Night</th>
              <th>Current Availability</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>

      <!-- All Guests (Detailed Section on Dashboard) -->
      <div class="card" id="dashGuestsCard">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-users" style="color: var(--primary-light);"></i> All Registered Guests Overview</span>
          <button class="btn btn-outline" style="font-size:0.75rem;padding:4px 8px;" onclick="switchTab('guests')"><i class="fa-solid fa-arrow-up-right-from-square"></i> Open Guests Module</button>
        </div>
        <table id="tableGuestsDash">
          <thead>
            <tr>
              <th>Guest ID</th>
              <th>Full Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>

      <!-- Today's Check-Ins Table -->
      <div class="card" id="dashCheckInsCard">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-arrow-right-to-bracket" style="color: var(--success);"></i> Today's Check-Ins</span>
          <button class="btn btn-outline" style="font-size:0.75rem;padding:4px 8px;" onclick="switchTab('bookings')"><i class="fa-solid fa-arrow-up-right-from-square"></i> Bookings Module</button>
        </div>
        <table id="tableCheckIns">
          <thead><tr><th>Booking #</th><th>Guest</th><th>Room</th><th>Status</th><th>Total Amount</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>

      <!-- Today's Check-Outs Table -->
      <div class="card" id="dashCheckOutsCard">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-arrow-right-from-bracket" style="color: #6366f1;"></i> Today's Check-Outs</span>
          <button class="btn btn-outline" style="font-size:0.75rem;padding:4px 8px;" onclick="switchTab('bookings')"><i class="fa-solid fa-arrow-up-right-from-square"></i> Bookings Module</button>
        </div>
        <table id="tableCheckOuts">
          <thead><tr><th>Booking #</th><th>Guest</th><th>Room</th><th>Status</th><th>Total Amount</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- 2. ROOMS MODULE TAB -->
    <div id="tab-rooms" class="tab-content">
      <div class="header">
        <h1>Rooms Module</h1>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-square-plus" style="color: var(--primary-light);"></i> Add a New Room</span>
        </div>
        <form id="formAddRoom" onsubmit="handleAddRoom(event)">
          <div class="form-grid">
            <div class="form-group">
              <label>Room Number</label>
              <input type="text" id="addRoomNum" placeholder="e.g. 101" required>
            </div>
            <div class="form-group">
              <label>Room Type</label>
              <select id="addRoomType" required>
                <option value="Single">Single</option>
                <option value="Double">Double</option>
                <option value="Suite">Suite</option>
              </select>
            </div>
            <div class="form-group">
              <label>Price per Night (<span class="curr-sym">$</span>)</label>
              <input type="number" step="0.01" min="1" id="addRoomPrice" placeholder="120.00" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top: 8px;"><i class="fa-solid fa-plus"></i> Add Room</button>
        </form>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-list-check" style="color: var(--primary-light);"></i> All Rooms & Availability Status</span>
        </div>
        <table id="tableRooms">
          <thead><tr><th>Room #</th><th>Type</th><th>Price/Night</th><th>Current Availability</th><th>Actions</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- 3. GUESTS MODULE TAB -->
    <div id="tab-guests" class="tab-content">
      <div class="header">
        <h1>Guests Module</h1>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-user-plus" style="color: var(--primary-light);"></i> Register a New Guest</span>
        </div>
        <form id="formAddGuest" onsubmit="handleAddGuest(event)">
          <div class="form-grid">
            <div class="form-group">
              <label>Full Name</label>
              <input type="text" id="addGuestName" placeholder="e.g. Eleanor Vance" required>
            </div>
            <div class="form-group">
              <label>Email Address</label>
              <input type="email" id="addGuestEmail" placeholder="eleanor@example.com">
            </div>
            <div class="form-group">
              <label>Phone Number</label>
              <input type="tel" id="addGuestPhone" placeholder="+1-555-0199">
            </div>
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top: 8px;"><i class="fa-solid fa-user-check"></i> Register Guest</button>
        </form>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-address-book" style="color: var(--primary-light);"></i> All Registered Guests</span>
        </div>
        <table id="tableGuests">
          <thead><tr><th>Guest ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Actions</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- 4. SERVICES MODULE TAB -->
    <div id="tab-services" class="tab-content">
      <div class="header">
        <h1>Services Module</h1>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-circle-plus" style="color: var(--primary-light);"></i> Add a New Service</span>
        </div>
        <form id="formAddService" onsubmit="handleAddService(event)">
          <div class="form-grid">
            <div class="form-group">
              <label>Service Name</label>
              <input type="text" id="addServiceName" placeholder="e.g. Airport Pickup, Spa" required>
            </div>
            <div class="form-group">
              <label>Price (<span class="curr-sym">$</span>)</label>
              <input type="number" step="0.01" min="0" id="addServicePrice" placeholder="50.00" required>
            </div>
            <div class="form-group" style="grid-column: 1 / -1;">
              <label>Description</label>
              <input type="text" id="addServiceDesc" placeholder="e.g. Luxury sedan transfer from airport">
            </div>
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top: 8px;"><i class="fa-solid fa-plus"></i> Add Service</button>
        </form>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-bell-concierge" style="color: var(--primary-light);"></i> All Services</span>
        </div>
        <table id="tableServices">
          <thead><tr><th>Service ID</th><th>Name</th><th>Price</th><th>Description</th><th>Actions</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- 5. BOOKINGS MODULE TAB -->
    <div id="tab-bookings" class="tab-content">
      <div class="header">
        <h1>Bookings Module</h1>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-calendar-plus" style="color: var(--primary-light);"></i> Book a Room for a Guest</span>
        </div>
        <form id="formBookRoom" onsubmit="handleBookRoom(event)">
          <div class="form-grid">
            <div class="form-group">
              <label>Select Room</label>
              <select id="bookRoomSelect" required></select>
            </div>
            <div class="form-group">
              <label>Select Guest</label>
              <select id="bookGuestSelect" required></select>
            </div>
            <div class="form-group">
              <label>Check-In Date</label>
              <input type="date" id="bookCheckIn" required>
            </div>
            <div class="form-group">
              <label>Check-Out Date</label>
              <input type="date" id="bookCheckOut" required>
            </div>
            <div class="form-group" style="grid-column: 1 / -1;">
              <label>Add Services (Hold Ctrl/Cmd to select multiple)</label>
              <select id="bookServicesSelect" multiple size="3" style="height: auto;"></select>
            </div>
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top: 8px;"><i class="fa-solid fa-check"></i> Book Room</button>
        </form>
      </div>

      <!-- Bookings Filtering -->
      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-filter" style="color: var(--primary-light);"></i> Filter Bookings</span>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label>Filter by Guest</label>
            <input type="text" id="filterGuest" placeholder="Guest name or ID" oninput="applyBookingFilters()">
          </div>
          <div class="form-group">
            <label>Filter by Room</label>
            <input type="text" id="filterRoom" placeholder="Room number" oninput="applyBookingFilters()">
          </div>
          <div class="form-group">
            <label>Filter by Check-In Date</label>
            <input type="date" id="filterCheckIn" oninput="applyBookingFilters()">
          </div>
          <div class="form-group" style="justify-content: flex-end;">
            <button type="button" class="btn btn-outline" onclick="clearBookingFilters()"><i class="fa-solid fa-rotate-left"></i> Reset Filters</button>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span class="card-title-text"><i class="fa-solid fa-clipboard-list" style="color: var(--primary-light);"></i> All Bookings</span>
          <span style="font-size: 0.85rem; font-weight: normal; color: var(--text-muted);">(Total Amount = Room Cost + Services)</span>
        </div>
        <table id="tableBookings">
          <thead>
            <tr>
              <th>ID</th>
              <th>Guest Name</th>
              <th>Room #</th>
              <th>Check-In</th>
              <th>Check-Out</th>
              <th>Status</th>
              <th>Services</th>
              <th>Total Amount</th>
              <th>Active?</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Generic Edit Modal -->
  <div id="editModal" class="modal-overlay">
    <div class="modal">
      <div class="modal-header">
        <h3 id="modalTitle">Edit</h3>
        <button class="close-btn" onclick="closeModal()"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div id="modalBody"></div>
    </div>
  </div>

  <script>
    // Global State & Currency Configuration (USD / INR)
    let currentCurrency = localStorage.getItem('hotel_currency') || 'USD';
    const USD_TO_INR = 83.0;

    let allRooms = [];
    let allGuests = [];
    let allServices = [];
    let allBookings = [];

    function formatPrice(usdAmount) {
      const val = parseFloat(usdAmount) || 0;
      if (currentCurrency === 'INR') {
        const inr = val * USD_TO_INR;
        return '₹' + inr.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      }
      return '$' + val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function getCurrencySymbol() {
      return currentCurrency === 'INR' ? '₹' : '$';
    }

    function setCurrency(curr) {
      currentCurrency = curr;
      localStorage.setItem('hotel_currency', curr);
      updateCurrencyUI();
      refreshAll();
    }

    function updateCurrencyUI() {
      const bUsd = document.getElementById('btnUSD');
      const bInr = document.getElementById('btnINR');
      if (bUsd) bUsd.classList.toggle('active', currentCurrency === 'USD');
      if (bInr) bInr.classList.toggle('active', currentCurrency === 'INR');
      document.querySelectorAll('.curr-sym').forEach(el => {
        el.textContent = getCurrencySymbol();
      });
    }

    function scrollToDashCard(cardId) {
      const el = document.getElementById(cardId);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        el.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
        el.style.borderColor = 'var(--primary-light)';
        el.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.25)';
        setTimeout(() => {
          el.style.borderColor = 'var(--border)';
          el.style.boxShadow = '0 1px 3px rgba(0,0,0,0.05)';
        }, 2000);
      }
    }

    function showAlert(msg, isError = false) {
      const box = document.getElementById("alertBox");
      box.textContent = msg;
      box.className = "alert " + (isError ? "alert-error" : "alert-success");
      box.style.display = "block";
      setTimeout(() => { box.style.display = "none"; }, 5000);
    }

    function switchTab(tabId) {
      document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
      document.querySelectorAll(".nav-btn").forEach(el => el.classList.remove("active"));
      document.getElementById("tab-" + tabId).classList.add("active");
      const btn = Array.from(document.querySelectorAll(".nav-btn")).find(b => b.getAttribute("onclick").includes(tabId));
      if (btn) btn.classList.add("active");
      refreshAll();
    }

    function closeModal() {
      document.getElementById("editModal").style.display = "none";
    }

    async function api(path, options = {}) {
      try {
        const res = await fetch(path, {
          headers: { "Content-Type": "application/json" },
          ...options
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "An error occurred");
        }
        return data;
      } catch (err) {
        showAlert(err.message, true);
        throw err;
      }
    }

    async function refreshAll() {
      updateCurrencyUI();
      await loadDashboard();
      await loadRooms();
      await loadGuests();
      await loadServices();
      await loadBookings();
    }

    // 1. Dashboard
    async function loadDashboard() {
      try {
        const d = await api("/api/dashboard");
        document.getElementById("dashDate").textContent = "Date: " + d.date;
        document.getElementById("statTotalRooms").textContent = d.total_rooms;
        document.getElementById("statOccupiedRooms").textContent = d.occupied_rooms_today;
        document.getElementById("statTotalGuests").textContent = d.total_guests;
        document.getElementById("statCheckIns").textContent = d.todays_check_ins_count;
        document.getElementById("statCheckOuts").textContent = d.todays_check_outs_count;

        // Table CheckIns
        const tbodyIn = document.querySelector("#tableCheckIns tbody");
        tbodyIn.innerHTML = d.todays_check_ins.length ? d.todays_check_ins.map(b => `
          <tr>
            <td>#${b.booking_id}</td>
            <td><strong>${b.guest_name}</strong></td>
            <td>Room ${b.room_number} (${b.room_type})</td>
            <td><span class="badge badge-booked">${b.status}</span></td>
            <td><strong>${formatPrice(b.total_amount)}</strong></td>
          </tr>
        `).join("") : '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:14px;">No check-ins today</td></tr>';

        // Table CheckOuts
        const tbodyOut = document.querySelector("#tableCheckOuts tbody");
        tbodyOut.innerHTML = d.todays_check_outs.length ? d.todays_check_outs.map(b => `
          <tr>
            <td>#${b.booking_id}</td>
            <td><strong>${b.guest_name}</strong></td>
            <td>Room ${b.room_number} (${b.room_type})</td>
            <td><span class="badge badge-booked">${b.status}</span></td>
            <td><strong>${formatPrice(b.total_amount)}</strong></td>
          </tr>
        `).join("") : '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:14px;">No check-outs today</td></tr>';

        // Table Occupied Rooms Today (Detailed)
        const tbodyOcc = document.querySelector("#tableOccupiedRooms tbody");
        tbodyOcc.innerHTML = d.occupied_rooms && d.occupied_rooms.length ? d.occupied_rooms.map(o => `
          <tr>
            <td><strong>Room ${o.room_number}</strong></td>
            <td>${o.room_type}</td>
            <td>${formatPrice(o.price_per_night)}</td>
            <td><strong>${o.guest_name}</strong></td>
            <td>${o.guest_phone || '-'}</td>
            <td>${o.check_in_date}</td>
            <td>${o.check_out_date}</td>
            <td><span class="badge badge-occupied"><i class="fa-solid fa-door-closed"></i> ${o.status}</span></td>
          </tr>
        `).join("") : '<tr><td colspan="8" style="text-align:center;color:var(--text-muted);padding:16px;">No rooms occupied today.</td></tr>';

        // Table All Rooms Overview on Dashboard
        const tbodyAllRooms = document.querySelector("#tableAllRoomsDash tbody");
        tbodyAllRooms.innerHTML = d.all_rooms && d.all_rooms.length ? d.all_rooms.map(r => `
          <tr>
            <td><strong>Room ${r.room_number}</strong></td>
            <td>${r.room_type}</td>
            <td>${formatPrice(r.price_per_night)}</td>
            <td>
              <span class="badge ${r.availability_status === 'Available' ? 'badge-available' : 'badge-occupied'}">
                <i class="fa-solid ${r.availability_status === 'Available' ? 'fa-circle-check' : 'fa-circle-xmark'}"></i>
                ${r.availability_status}
              </span>
            </td>
            <td>
              <button class="btn btn-outline" style="padding:3px 8px;font-size:0.75rem;" onclick="openEditRoom('${r.room_number}')"><i class="fa-solid fa-pen-to-square"></i> Edit</button>
            </td>
          </tr>
        `).join("") : '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">No rooms found.</td></tr>';

        // Table All Guests Overview on Dashboard
        const tbodyAllGuests = document.querySelector("#tableGuestsDash tbody");
        tbodyAllGuests.innerHTML = d.all_guests && d.all_guests.length ? d.all_guests.map(g => `
          <tr>
            <td><strong>#${g.guest_id}</strong></td>
            <td><strong>${g.name}</strong></td>
            <td>${g.email || '-'}</td>
            <td>${g.phone || '-'}</td>
            <td>
              <button class="btn btn-outline" style="padding:3px 8px;font-size:0.75rem;" onclick="openEditGuest(${g.guest_id})"><i class="fa-solid fa-pen-to-square"></i> Edit</button>
            </td>
          </tr>
        `).join("") : '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">No guests registered.</td></tr>';

      } catch (e) {}
    }

    // 2. Rooms Module
    async function loadRooms() {
      allRooms = await api("/api/rooms");
      const tbody = document.querySelector("#tableRooms tbody");
      tbody.innerHTML = allRooms.map(r => `
        <tr>
          <td><strong>${r.room_number}</strong></td>
          <td>${r.room_type}</td>
          <td>${formatPrice(r.price_per_night)}</td>
          <td>
            <span class="badge ${r.availability_status === 'Available' ? 'badge-available' : 'badge-occupied'}">
              <i class="fa-solid ${r.availability_status === 'Available' ? 'fa-circle-check' : 'fa-circle-xmark'}"></i>
              ${r.availability_status}
            </span>
          </td>
          <td>
            <button class="btn btn-outline" onclick="openEditRoom('${r.room_number}')"><i class="fa-solid fa-pen-to-square"></i> Edit</button>
            <button class="btn btn-danger" onclick="deleteRoom('${r.room_number}')"><i class="fa-solid fa-trash-can"></i> Delete</button>
          </td>
        </tr>
      `).join("");

      // Update room select in booking form
      const select = document.getElementById("bookRoomSelect");
      select.innerHTML = allRooms.map(r => `<option value="${r.room_number}">Room ${r.room_number} (${r.room_type} - ${formatPrice(r.price_per_night)}/nt)</option>`).join("");
    }

    async function handleAddRoom(e) {
      e.preventDefault();
      const rawPrice = parseFloat(document.getElementById("addRoomPrice").value);
      const priceInUSD = currentCurrency === 'INR' ? rawPrice / USD_TO_INR : rawPrice;
      try {
        await api("/api/rooms", {
          method: "POST",
          body: JSON.stringify({
            room_number: document.getElementById("addRoomNum").value,
            room_type: document.getElementById("addRoomType").value,
            price_per_night: priceInUSD
          })
        });
        showAlert("Room added successfully!");
        document.getElementById("formAddRoom").reset();
        refreshAll();
      } catch (err) {}
    }

    function openEditRoom(roomNum) {
      const r = allRooms.find(x => x.room_number === roomNum);
      if (!r) return;
      const displayPrice = currentCurrency === 'INR' ? (r.price_per_night * USD_TO_INR).toFixed(2) : r.price_per_night.toFixed(2);
      document.getElementById("modalTitle").innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Room ' + r.room_number;
      document.getElementById("modalBody").innerHTML = `
        <form onsubmit="saveEditRoom(event, '${r.room_number}')">
          <div class="form-group">
            <label>Room Type</label>
            <select id="editRoomType">
              <option value="Single" ${r.room_type === 'Single' ? 'selected' : ''}>Single</option>
              <option value="Double" ${r.room_type === 'Double' ? 'selected' : ''}>Double</option>
              <option value="Suite" ${r.room_type === 'Suite' ? 'selected' : ''}>Suite</option>
            </select>
          </div>
          <div class="form-group">
            <label>Price per Night (<span class="curr-sym">${getCurrencySymbol()}</span>)</label>
            <input type="number" step="0.01" min="1" id="editRoomPrice" value="${displayPrice}" required>
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top:12px;"><i class="fa-solid fa-floppy-disk"></i> Save Changes</button>
        </form>
      `;
      document.getElementById("editModal").style.display = "flex";
    }

    async function saveEditRoom(e, roomNum) {
      e.preventDefault();
      const val = parseFloat(document.getElementById("editRoomPrice").value);
      const priceInUSD = currentCurrency === 'INR' ? val / USD_TO_INR : val;
      try {
        await api("/api/rooms/" + roomNum, {
          method: "PUT",
          body: JSON.stringify({
            room_type: document.getElementById("editRoomType").value,
            price_per_night: priceInUSD
          })
        });
        closeModal();
        showAlert("Room updated successfully!");
        refreshAll();
      } catch (err) {}
    }

    async function deleteRoom(roomNum) {
      if (!confirm(`Are you sure you want to delete Room ${roomNum}? (Allowed only if no active/upcoming bookings exist)`)) return;
      try {
        await api("/api/rooms/" + roomNum, { method: "DELETE" });
        showAlert("Room deleted successfully!");
        refreshAll();
      } catch (err) {}
    }

    // 3. Guests Module
    async function loadGuests() {
      allGuests = await api("/api/guests");
      const tbody = document.querySelector("#tableGuests tbody");
      tbody.innerHTML = allGuests.map(g => `
        <tr>
          <td>#${g.guest_id}</td>
          <td><strong>${g.name}</strong></td>
          <td>${g.email || '-'}</td>
          <td>${g.phone || '-'}</td>
          <td>
            <button class="btn btn-outline" onclick="openEditGuest(${g.guest_id})"><i class="fa-solid fa-pen-to-square"></i> Edit</button>
          </td>
        </tr>
      `).join("");

      const select = document.getElementById("bookGuestSelect");
      select.innerHTML = allGuests.map(g => `<option value="${g.guest_id}">${g.name} (#${g.guest_id})</option>`).join("");
    }

    async function handleAddGuest(e) {
      e.preventDefault();
      try {
        await api("/api/guests", {
          method: "POST",
          body: JSON.stringify({
            name: document.getElementById("addGuestName").value,
            email: document.getElementById("addGuestEmail").value,
            phone: document.getElementById("addGuestPhone").value
          })
        });
        showAlert("Guest registered successfully!");
        document.getElementById("formAddGuest").reset();
        refreshAll();
      } catch (err) {}
    }

    function openEditGuest(guestId) {
      const g = allGuests.find(x => x.guest_id === guestId);
      if (!g) return;
      document.getElementById("modalTitle").innerHTML = '<i class="fa-solid fa-user-pen"></i> Edit Guest #' + g.guest_id;
      document.getElementById("modalBody").innerHTML = `
        <form onsubmit="saveEditGuest(event, ${g.guest_id})">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" id="editGuestName" value="${g.name}" required>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" id="editGuestEmail" value="${g.email || ''}">
          </div>
          <div class="form-group">
            <label>Phone</label>
            <input type="tel" id="editGuestPhone" value="${g.phone || ''}">
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top:12px;"><i class="fa-solid fa-floppy-disk"></i> Save Changes</button>
        </form>
      `;
      document.getElementById("editModal").style.display = "flex";
    }

    async function saveEditGuest(e, guestId) {
      e.preventDefault();
      try {
        await api("/api/guests/" + guestId, {
          method: "PUT",
          body: JSON.stringify({
            name: document.getElementById("editGuestName").value,
            email: document.getElementById("editGuestEmail").value,
            phone: document.getElementById("editGuestPhone").value
          })
        });
        closeModal();
        showAlert("Guest updated successfully!");
        refreshAll();
      } catch (err) {}
    }

    // 4. Services Module
    async function loadServices() {
      allServices = await api("/api/services");
      const tbody = document.querySelector("#tableServices tbody");
      tbody.innerHTML = allServices.map(s => `
        <tr>
          <td>#${s.service_id}</td>
          <td><strong>${s.name}</strong></td>
          <td>${formatPrice(s.price)}</td>
          <td>${s.description || '-'}</td>
          <td>
            <button class="btn btn-outline" onclick="openEditService(${s.service_id})"><i class="fa-solid fa-pen-to-square"></i> Edit</button>
          </td>
        </tr>
      `).join("");

      const sSelect = document.getElementById("bookServicesSelect");
      sSelect.innerHTML = allServices.map(s => `<option value="${s.service_id}">${s.name} (+${formatPrice(s.price)})</option>`).join("");
    }

    async function handleAddService(e) {
      e.preventDefault();
      const rawPrice = parseFloat(document.getElementById("addServicePrice").value);
      const priceInUSD = currentCurrency === 'INR' ? rawPrice / USD_TO_INR : rawPrice;
      try {
        await api("/api/services", {
          method: "POST",
          body: JSON.stringify({
            name: document.getElementById("addServiceName").value,
            description: document.getElementById("addServiceDesc").value,
            price: priceInUSD
          })
        });
        showAlert("Service added successfully!");
        document.getElementById("formAddService").reset();
        refreshAll();
      } catch (err) {}
    }

    function openEditService(serviceId) {
      const s = allServices.find(x => x.service_id === serviceId);
      if (!s) return;
      const displayPrice = currentCurrency === 'INR' ? (s.price * USD_TO_INR).toFixed(2) : s.price.toFixed(2);
      document.getElementById("modalTitle").innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Service #' + s.service_id;
      document.getElementById("modalBody").innerHTML = `
        <form onsubmit="saveEditService(event, ${s.service_id})">
          <div class="form-group">
            <label>Service Name</label>
            <input type="text" id="editServiceName" value="${s.name}" required>
          </div>
          <div class="form-group">
            <label>Price (<span class="curr-sym">${getCurrencySymbol()}</span>)</label>
            <input type="number" step="0.01" min="0" id="editServicePrice" value="${displayPrice}" required>
          </div>
          <div class="form-group">
            <label>Description</label>
            <input type="text" id="editServiceDesc" value="${s.description || ''}">
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top:12px;"><i class="fa-solid fa-floppy-disk"></i> Save Changes</button>
        </form>
      `;
      document.getElementById("editModal").style.display = "flex";
    }

    async function saveEditService(e, serviceId) {
      e.preventDefault();
      const val = parseFloat(document.getElementById("editServicePrice").value);
      const priceInUSD = currentCurrency === 'INR' ? val / USD_TO_INR : val;
      try {
        await api("/api/services/" + serviceId, {
          method: "PUT",
          body: JSON.stringify({
            name: document.getElementById("editServiceName").value,
            description: document.getElementById("editServiceDesc").value,
            price: priceInUSD
          })
        });
        closeModal();
        showAlert("Service updated successfully!");
        refreshAll();
      } catch (err) {}
    }

    // 5. Bookings Module
    async function loadBookings() {
      allBookings = await api("/api/bookings");
      applyBookingFilters();
    }

    function renderBookings(list) {
      const tbody = document.querySelector("#tableBookings tbody");
      if (!list.length) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align:center;color:var(--text-muted);padding:24px;">No bookings match the criteria.</td></tr>';
        return;
      }
      tbody.innerHTML = list.map(b => {
        const srvNames = b.services.map(s => `${s.name} (${formatPrice(s.price)})`).join(", ") || "None";
        const activeBadge = b.is_active ? '<span class="badge badge-active"><i class="fa-solid fa-bolt"></i> Active</span>' : '-';
        return `
          <tr>
            <td>#${b.booking_id}</td>
            <td><strong>${b.guest_name}</strong></td>
            <td>Room ${b.room_number}</td>
            <td>${b.check_in_date}</td>
            <td>${b.check_out_date}</td>
            <td><span class="badge ${b.status === 'Cancelled' ? 'badge-cancelled' : 'badge-booked'}">${b.status}</span></td>
            <td><small>${srvNames}</small></td>
            <td><strong>${formatPrice(b.total_amount)}</strong></td>
            <td>${activeBadge}</td>
            <td>
              <button class="btn btn-outline" style="padding:4px 8px;font-size:0.75rem;" onclick="openAddServicesModal(${b.booking_id})"><i class="fa-solid fa-plus"></i> Service</button>
              <button class="btn btn-outline" style="padding:4px 8px;font-size:0.75rem;" onclick="openStatusModal(${b.booking_id}, '${b.status}')"><i class="fa-solid fa-sliders"></i> Status</button>
            </td>
          </tr>
        `;
      }).join("");
    }

    function applyBookingFilters() {
      const gFilter = document.getElementById("filterGuest").value.trim().toLowerCase();
      const rFilter = document.getElementById("filterRoom").value.trim().toLowerCase();
      const inFilter = document.getElementById("filterCheckIn").value;

      let filtered = allBookings.filter(b => {
        if (gFilter && !b.guest_name.toLowerCase().includes(gFilter) && b.guest_id.toString() !== gFilter) return false;
        if (rFilter && b.room_number.toLowerCase() !== rFilter) return false;
        if (inFilter && b.check_in_date !== inFilter) return false;
        return true;
      });

      renderBookings(filtered);
    }

    function clearBookingFilters() {
      document.getElementById("filterGuest").value = "";
      document.getElementById("filterRoom").value = "";
      document.getElementById("filterCheckIn").value = "";
      renderBookings(allBookings);
    }

    async function handleBookRoom(e) {
      e.preventDefault();
      const sOptions = document.getElementById("bookServicesSelect").selectedOptions;
      const sIds = Array.from(sOptions).map(o => parseInt(o.value));

      try {
        await api("/api/bookings", {
          method: "POST",
          body: JSON.stringify({
            room_number: document.getElementById("bookRoomSelect").value,
            guest_id: parseInt(document.getElementById("bookGuestSelect").value),
            check_in_date: document.getElementById("bookCheckIn").value,
            check_out_date: document.getElementById("bookCheckOut").value,
            service_ids: sIds
          })
        });
        showAlert("Booking created successfully!");
        document.getElementById("formBookRoom").reset();
        refreshAll();
      } catch (err) {}
    }

    function openAddServicesModal(bookingId) {
      document.getElementById("modalTitle").innerHTML = '<i class="fa-solid fa-bell-concierge"></i> Add Services to Booking #' + bookingId;
      document.getElementById("modalBody").innerHTML = `
        <form onsubmit="saveAddServices(event, ${bookingId})">
          <div class="form-group">
            <label>Select Services to Add</label>
            <select id="modalServicesSelect" multiple size="4" style="height:auto;" required>
              ${allServices.map(s => `<option value="${s.service_id}">${s.name} (+$${s.price.toFixed(2)})</option>`).join("")}
            </select>
            <small style="color:var(--text-muted);">Hold Ctrl/Cmd to select multiple</small>
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top:12px;"><i class="fa-solid fa-plus"></i> Add Selected Services</button>
        </form>
      `;
      document.getElementById("editModal").style.display = "flex";
    }

    async function saveAddServices(e, bookingId) {
      e.preventDefault();
      const sOptions = document.getElementById("modalServicesSelect").selectedOptions;
      const sIds = Array.from(sOptions).map(o => parseInt(o.value));
      try {
        await api("/api/bookings/" + bookingId + "/services", {
          method: "POST",
          body: JSON.stringify({ service_ids: sIds })
        });
        closeModal();
        showAlert("Services added to booking!");
        refreshAll();
      } catch (err) {}
    }

    function openStatusModal(bookingId, currentStatus) {
      document.getElementById("modalTitle").innerHTML = '<i class="fa-solid fa-sliders"></i> Update Booking #' + bookingId + " Status";
      document.getElementById("modalBody").innerHTML = `
        <form onsubmit="saveBookingStatus(event, ${bookingId})">
          <div class="form-group">
            <label>Booking Status</label>
            <select id="editBookingStatus">
              <option value="Booked" ${currentStatus === 'Booked' ? 'selected' : ''}>Booked</option>
              <option value="Checked In" ${currentStatus === 'Checked In' ? 'selected' : ''}>Checked In</option>
              <option value="Checked Out" ${currentStatus === 'Checked Out' ? 'selected' : ''}>Checked Out</option>
              <option value="Cancelled" ${currentStatus === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary" style="margin-top:12px;"><i class="fa-solid fa-check"></i> Update Status</button>
        </form>
      `;
      document.getElementById("editModal").style.display = "flex";
    }

    async function saveBookingStatus(e, bookingId) {
      e.preventDefault();
      try {
        await api("/api/bookings/" + bookingId + "/status", {
          method: "PUT",
          body: JSON.stringify({ status: document.getElementById("editBookingStatus").value })
        });
        closeModal();
        showAlert("Booking status updated!");
        refreshAll();
      } catch (err) {}
    }

    // Initial load
    refreshAll();
  </script>
</body>
</html>
"""


class HotelRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_error(self, message: str, status: int = 400):
        self._send_json({"error": str(message)}, status=status)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path.rstrip("/")

        if path == "" or path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        # API Routes
        try:
            if path == "/api/dashboard":
                summary = system.get_dashboard()
                self._send_json(summary)
            elif path == "/api/rooms":
                rooms_list = system.list_rooms()
                self._send_json(rooms_list)
            elif path == "/api/guests":
                guests_list = system.list_guests()
                self._send_json(guests_list)
            elif path == "/api/services":
                services_list = system.list_services()
                self._send_json(services_list)
            elif path == "/api/bookings":
                bookings_list = system.list_bookings()
                self._send_json(bookings_list)
            else:
                self._send_error("Endpoint not found", status=404)
        except Exception as e:
            self._send_error(str(e), status=500)

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path.rstrip("/")
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        try:
            if path == "/api/rooms":
                room = system.add_room(
                    room_number=body["room_number"],
                    room_type=body["room_type"],
                    price_per_night=float(body["price_per_night"])
                )
                self._send_json(room, status=201)

            elif path == "/api/guests":
                guest = system.register_guest(
                    name=body["name"],
                    email=body.get("email", ""),
                    phone=body.get("phone", "")
                )
                self._send_json(guest, status=201)

            elif path == "/api/services":
                service = system.add_service(
                    name=body["name"],
                    description=body.get("description", ""),
                    price=float(body["price"])
                )
                self._send_json(service, status=201)

            elif path == "/api/bookings":
                booking = system.book_room(
                    room_number=body["room_number"],
                    guest_id=int(body["guest_id"]),
                    check_in_date=body["check_in_date"],
                    check_out_date=body["check_out_date"],
                    service_ids=body.get("service_ids")
                )
                self._send_json(booking, status=201)

            elif path.startswith("/api/bookings/") and path.endswith("/services"):
                booking_id = int(path.split("/")[3])
                updated = system.add_services_to_booking(booking_id, body.get("service_ids", []))
                self._send_json(updated)

            else:
                self._send_error("Endpoint not found", status=404)
        except Exception as e:
            self._send_error(str(e), status=400)

    def do_PUT(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path.rstrip("/")
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        try:
            if path.startswith("/api/rooms/"):
                room_number = path.split("/")[3]
                updated = system.update_room(
                    room_number=room_number,
                    new_type=body.get("room_type"),
                    new_price=float(body["price_per_night"]) if "price_per_night" in body else None
                )
                self._send_json(updated)

            elif path.startswith("/api/guests/"):
                guest_id = int(path.split("/")[3])
                updated = system.update_guest(
                    guest_id=guest_id,
                    name=body.get("name"),
                    email=body.get("email"),
                    phone=body.get("phone")
                )
                self._send_json(updated)

            elif path.startswith("/api/services/"):
                service_id = int(path.split("/")[3])
                updated = system.update_service(
                    service_id=service_id,
                    name=body.get("name"),
                    description=body.get("description"),
                    price=float(body["price"]) if "price" in body else None
                )
                self._send_json(updated)

            elif path.startswith("/api/bookings/") and path.endswith("/status"):
                booking_id = int(path.split("/")[3])
                updated = system.update_booking_status(booking_id, body["status"])
                self._send_json(updated)

            else:
                self._send_error("Endpoint not found", status=404)
        except Exception as e:
            self._send_error(str(e), status=400)

    def do_DELETE(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path.rstrip("/")

        try:
            if path.startswith("/api/rooms/"):
                room_number = path.split("/")[3]
                system.delete_room(room_number)
                self._send_json({"success": True, "message": f"Room {room_number} deleted"})
            else:
                self._send_error("Endpoint not found", status=404)
        except Exception as e:
            self._send_error(str(e), status=400)


def start_server(port: int = PORT):
    # Ensure database is seeded if empty
    if not system.list_rooms():
        seed_database()

    server_address = ("", port)
    with socketserver.TCPServer(server_address, HotelRequestHandler) as httpd:
        print(f"Hotel Room Booking System Web App running at http://localhost:{port}")
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")


if __name__ == "__main__":
    start_server()
