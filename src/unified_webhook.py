from flask import Flask, request
import logging
from datetime import datetime

app = Flask(__name__)

log = logging.getLogger('skip')
log.setLevel(logging.ERROR)

PROMETHEUS_FILE = "/tmp/prometheus_alert_timestamp.txt"
SNIFFER_FILE = "/tmp/sniffer_trigger_timestamp.txt"

# Helper for logging
def log_event(source, message):
    time_str = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{time_str}] [{source}] {message}")

# ==========================================
# ENDPOINT 1: Prometheus Alerts
# ==========================================
@app.route('/alert', methods=['POST'])
def prometheus_webhook():
    data = request.json
    alerts = data.get('alerts', [])

    for a in alerts:
        status = a.get('status')
        alertname = a.get('labels', {}).get('alertname', 'Unknown Alert')

        if status == 'firing':
            timestamp = a.get('startsAt', datetime.now().isoformat())
            
            # 2. Drop-File for master
            with open(PROMETHEUS_FILE, 'w') as f:
                f.write(timestamp)
                
            log_event("PROMETHEUS", f"ALARM FIRING ({alertname}). Drop-File created.")
            break # Only first alert

        elif status == 'resolved':
            log_event("PROMETHEUS", f"ALARM RESOLVED ({alertname}). Network reconverged")

    return "OK", 200

# ==========================================
# ENDPOINT 2: Packet Sniffer
# ==========================================
@app.route('/webhook/sniffer', methods=['POST'])
def sniffer_webhook():
    data = request.json
    
    # Security check
    if not data or 'node' not in data or 'timestamp' not in data:
        log_event("SNIFFER", "Received invalid payload.")
        return "Invalid payload", 400

    # Drop-File for master
    with open(SNIFFER_FILE, 'w') as f:
        f.write(data['timestamp'])

    log_event("SNIFFER", f"TRIGGER received by {data['node']}! Timestamp: {data['timestamp']}")
    return "OK", 200

# ==========================================
# MAIN RUNNER
# ==========================================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("Unified Event-Webhook live")
    print("="*70)
    print(" - Listening at port 5000")
    print(" - API:")
    print("   -> /alert")
    print("   -> /webhook/sniffer")
    print(" - STRG+C to cancel\n")
    
    app.run(host='0.0.0.0', port=5000)
