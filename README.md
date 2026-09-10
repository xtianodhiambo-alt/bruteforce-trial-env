# Brute Force Trial Environment

A controlled testing environment for demonstrating and analyzing brute force attacks against a 4-digit PIN service.

## Overview

This project includes:
- **PIN Validation Service**: A local Flask-based service that validates 4-digit PINs
- **Brute Force Attack Script**: Systematically attempts PIN combinations
- **Security Mechanisms**: Rate limiting, attempt tracking, and account lockout
- **Logging & Monitoring**: Detailed logs of all attempts and results

## Security Features

- ✅ **Rate Limiting**: Maximum 10 attempts per IP address
- ✅ **Account Lockout**: 60-second lockout after exceeding max attempts
- ✅ **Attempt Tracking**: Real-time monitoring of attack attempts
- ✅ **Comprehensive Logging**: JSON logs of all validation attempts
- ✅ **Statistics Endpoint**: View current attempt statistics

## Setup

### Prerequisites
- Python 3.7+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/xtianodhiambo-alt/bruteforce-trial-env.git
cd bruteforce-trial-env

# Install dependencies
pip install -r requirements.txt
```

## Usage

### 1. Start the PIN Service

```bash
python pin_service.py
```

Output:
```
🔐 PIN Validation Service
Correct PIN: 1234
Max attempts: 10
Lockout duration: 60s

Endpoints:
  GET  /              - Health check
  POST /validate      - Validate a PIN
  GET  /stats         - View attempt statistics
  POST /reset         - Reset all statistics

 * Running on http://localhost:5000
```

### 2. Run the Brute Force Attack (in another terminal)

```bash
python brute_force_attack.py
```

Example output:
```
🚀 Starting brute force attack...
   Target: http://localhost:5000
   PIN range: 0000 - 9999
   Delay between attempts: 0s

⏳ Attempt #100: 0100 - Incorrect
⏳ Attempt #200: 0200 - Incorrect
...
✅ SUCCESS! PIN found: 1234 (Attempt #1235)

==================================================
📊 BRUTE FORCE ATTACK SUMMARY
==================================================
Total attempts:     1235
Duration:           2.45 seconds
Attempts/second:    503.06

✅ PIN FOUND: 1234
==================================================

💾 Results saved to attack_results.json
```

### 3. View Attack Statistics

```bash
# While attack is running, check stats
curl http://localhost:5000/stats | python -m json.tool
```

## Command Line Options

### Brute Force Attack Script

```
Usage: python brute_force_attack.py [options]

Options:
  --start <pin>   Start PIN (default: 0000)
  --end <pin>     End PIN (default: 9999)
  --delay <sec>   Delay between attempts in seconds (default: 0)
  --quiet         Suppress verbose output
  --help          Show this help message
```

### Examples

```bash
# Attack with a delay between attempts
python brute_force_attack.py --delay 0.5

# Attack a specific range of PINs
python brute_force_attack.py --start 1000 --end 2000

# Quiet mode (minimal output)
python brute_force_attack.py --quiet
```

## Configuration

### PIN Service (`pin_service.py`)

Edit these variables to customize behavior:

```python
CORRECT_PIN = "1234"           # The PIN to find
MAX_ATTEMPTS = 10              # Attempts before lockout
LOCKOUT_DURATION = 60          # Lockout duration (seconds)
```

### Attack Script (`brute_force_attack.py`)

Edit these variables:

```python
DELAY_BETWEEN_ATTEMPTS = 0     # Delay in seconds
VERBOSE = True                 # Detailed output
MAX_PINS = 10000               # Maximum attempts
```

## API Endpoints

### Health Check
```
GET /

Response: 200 OK
{
  "status": "online",
  "service": "PIN Validation Service",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### Validate PIN
```
POST /validate
Content-Type: application/json

{
  "pin": "1234"
}

Response (Success): 200 OK
{
  "success": true,
  "message": "PIN is correct!",
  "attempts": 0
}

Response (Incorrect): 401 Unauthorized
{
  "success": false,
  "message": "PIN is incorrect. 9 attempts remaining.",
  "attempts_used": 1,
  "attempts_remaining": 9
}

Response (Locked): 429 Too Many Requests
{
  "error": "Too many attempts. Account locked.",
  "locked_until": "2024-01-15T10:31:00.000000",
  "ip": "127.0.0.1"
}
```

### View Statistics
```
GET /stats

Response: 200 OK
{
  "127.0.0.1": {
    "total_attempts": 25,
    "last_attempt": "2024-01-15T10:30:00.000000",
    "locked_out": false
  }
}
```

### Reset Statistics
```
POST /reset

Response: 200 OK
{
  "message": "All statistics reset."
}
```

## Output Files

### service_logs.json
Detailed logs of every validation attempt:

```json
{"timestamp": "2024-01-15T10:30:01.234567", "ip_address": "127.0.0.1", "pin_attempted": "0000", "success": false, "attempt_number": 1}
{"timestamp": "2024-01-15T10:30:01.345678", "ip_address": "127.0.0.1", "pin_attempted": "0001", "success": false, "attempt_number": 2}
...
```

### attack_results.json
Summary and detailed results of the brute force attack:

```json
{
  "summary": {
    "total_attempts": 1235,
    "successful_pin": "1234",
    "start_time": "2024-01-15T10:30:00.000000",
    "end_time": "2024-01-15T10:30:02.450000",
    "duration_seconds": 2.45
  },
  "results": [
    {
      "attempt": 1,
      "pin": "0000",
      "status_code": 401,
      "response": {...},
      "timestamp": "2024-01-15T10:30:01.234567"
    }
  ]
}
```

## Learning Objectives

This project demonstrates:

1. **Brute Force Attack Mechanics**: How systematic PIN guessing works
2. **Rate Limiting**: Defense against repeated authentication attempts
3. **Account Lockout**: Temporal restrictions on failed attempts
4. **Attack Analysis**: Measuring attack speed and effectiveness
5. **Logging & Monitoring**: Detecting and tracking attack attempts

## Important Notes

⚠️ **Legal & Ethical Warning**
- This is for **educational purposes only**
- Only test on systems you own or have explicit permission to test
- Unauthorized brute force attacks are illegal in most jurisdictions
- Use this to understand security mechanisms, not to compromise systems

## Troubleshooting

### Service won't start
```
# Check if port 5000 is already in use
lsof -i :5000

# Kill the process
kill -9 <PID>
```

### Connection errors during attack
```
# Ensure service is running in another terminal
python pin_service.py

# Check if service is responsive
curl http://localhost:5000/
```

### Locked out during testing
```
# Reset all statistics
curl -X POST http://localhost:5000/reset
```

## Future Enhancements

- [ ] Database persistence for logs
- [ ] Web dashboard for monitoring
- [ ] Multiple PIN service instances
- [ ] Distributed attack simulation
- [ ] Advanced defense mechanisms (exponential backoff, CAPTCHA)
- [ ] Machine learning anomaly detection

## License

MIT
