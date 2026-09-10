#!/usr/bin/env python3
"""
Local PIN Validation Service
A simple Flask service that validates 4-digit PINs for brute force testing.
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os

app = Flask(__name__)

# Configuration
CORRECT_PIN = "1234"  # Default PIN - change as needed
MAX_ATTEMPTS = 10  # Max attempts before lockout
LOCKOUT_DURATION = 60  # Lockout duration in seconds
LOG_FILE = "service_logs.json"

# In-memory tracking of failed attempts
attempt_tracker = defaultdict(lambda: {"count": 0, "last_attempt": None, "locked_until": None})

def log_attempt(ip, pin, success):
    """Log authentication attempts to file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "ip_address": ip,
        "pin_attempted": pin,
        "success": success,
        "attempt_number": attempt_tracker[ip]["count"]
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def is_locked_out(ip):
    """Check if an IP is currently locked out."""
    tracker = attempt_tracker[ip]
    if tracker["locked_until"] and datetime.now() < tracker["locked_until"]:
        return True
    return False

def reset_lockout(ip):
    """Reset lockout if duration has expired."""
    tracker = attempt_tracker[ip]
    if tracker["locked_until"] and datetime.now() >= tracker["locked_until"]:
        tracker["locked_until"] = None
        tracker["count"] = 0

@app.route("/", methods=["GET"])
def status():
    """Health check endpoint."""
    return jsonify({
        "status": "online",
        "service": "PIN Validation Service",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route("/validate", methods=["POST"])
def validate_pin():
    """Validate a 4-digit PIN."""
    ip = request.remote_addr
    data = request.get_json()
    
    if not data or "pin" not in data:
        return jsonify({"error": "Missing 'pin' parameter"}), 400
    
    pin = data.get("pin", "").strip()
    
    # Validate PIN format
    if not pin.isdigit() or len(pin) != 4:
        return jsonify({"error": "PIN must be exactly 4 digits"}), 400
    
    # Check if IP is locked out
    reset_lockout(ip)
    if is_locked_out(ip):
        locked_time = attempt_tracker[ip]["locked_until"]
        return jsonify({
            "error": "Too many attempts. Account locked.",
            "locked_until": locked_time.isoformat(),
            "ip": ip
        }), 429
    
    # Increment attempt counter
    attempt_tracker[ip]["count"] += 1
    attempt_tracker[ip]["last_attempt"] = datetime.now()
    
    # Check if PIN is correct
    success = (pin == CORRECT_PIN)
    log_attempt(ip, pin, success)
    
    if success:
        # Reset tracker on success
        attempt_tracker[ip] = {"count": 0, "last_attempt": None, "locked_until": None}
        return jsonify({
            "success": True,
            "message": "PIN is correct!",
            "attempts": attempt_tracker[ip]["count"]
        }), 200
    else:
        # Increment failed attempts
        remaining = MAX_ATTEMPTS - attempt_tracker[ip]["count"]
        
        if remaining <= 0:
            # Lock out the IP
            attempt_tracker[ip]["locked_until"] = datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
            return jsonify({
                "success": False,
                "message": "Maximum attempts exceeded. Account locked.",
                "attempts_used": attempt_tracker[ip]["count"],
                "locked_until": attempt_tracker[ip]["locked_until"].isoformat()
            }), 429
        else:
            return jsonify({
                "success": False,
                "message": f"PIN is incorrect. {remaining} attempts remaining.",
                "attempts_used": attempt_tracker[ip]["count"],
                "attempts_remaining": remaining
            }), 401

@app.route("/stats", methods=["GET"])
def get_stats():
    """Get current tracking statistics."""
    stats = {}
    for ip, tracker in attempt_tracker.items():
        reset_lockout(ip)
        stats[ip] = {
            "total_attempts": tracker["count"],
            "last_attempt": tracker["last_attempt"].isoformat() if tracker["last_attempt"] else None,
            "locked_out": is_locked_out(ip)
        }
    return jsonify(stats), 200

@app.route("/reset", methods=["POST"])
def reset_stats():
    """Reset all tracking data (admin endpoint)."""
    global attempt_tracker
    attempt_tracker = defaultdict(lambda: {"count": 0, "last_attempt": None, "locked_until": None})
    return jsonify({"message": "All statistics reset."}), 200

if __name__ == "__main__":
    # Initialize log file
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    
    print("\n🔐 PIN Validation Service")
    print(f"Correct PIN: {CORRECT_PIN}")
    print(f"Max attempts: {MAX_ATTEMPTS}")
    print(f"Lockout duration: {LOCKOUT_DURATION}s")
    print("\nEndpoints:")
    print("  GET  /              - Health check")
    print("  POST /validate      - Validate a PIN")
    print("  GET  /stats         - View attempt statistics")
    print("  POST /reset         - Reset all statistics\n")
    
    app.run(host="localhost", port=5000, debug=False)
