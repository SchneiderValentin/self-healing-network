import os
import time
import socket
import subprocess
import re
import glob
import math
from datetime import datetime

# Dropfiles #

PROMETHEUS_FILE = "/tmp/prometheus_alert_timestamp.txt"
SNIFFER_FILE ="/tmp/sniffer_trigger_timestamp.txt"

# Methods #

def run_playbook(command, description): # Use this to run playbooks as subprocess.
    # Executing Playbook
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] RUNNING PLAYBOOK '{description}'...")

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] ERROR running playbook '{description}'")
        print(result.stderr)
        return False

    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] SUCCESS running playbook '{description}'")
    return True

def clear_old_alerts():
    # Cleanup previous run records
    if os.path.exists(PROMETHEUS_FILE):
        os.remove(PROMETHEUS_FILE)
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] ERASE Removed previous Prometheus logfile")

    if os.path.exists(SNIFFER_FILE):
        os.remove(SNIFFER_FILE)
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] ERASE Removed previous Packet Sniffer logfile")


def check_webhook_running(port=5000):
    # Verify Webhook for Prometheus and Packet Sniffer is online
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] VERIFY Looking for Webhook at {port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        try:
            s.connect(("127.0.0.1", port))
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] SUCCESS Webhook live")
            return True
        except (ConnectionRefusedError, socket.timeout):
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] ERROR Webhook offline")
            print(f"Make sure Webhook is running at port {port}")
            return False

def wait_for_sniffer(timeout_seconds=60):
    # Wait for Packet Sniffer to deliver t1 (First packet via alternative transit)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] WAIT Expecting timestamp from Packet Sniffer (Timeout in {timeout_seconds}s)")
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if os.path.exists(SNIFFER_FILE):
            with open(SNIFFER_FILE, 'r') as f:
                ts = f.read().strip()
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] SUCCESS Received Timestamp: {ts})")
            return ts
        time.sleep(0.5)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] TIMEOUT No signal from Packet Sniffer")
    print(f"Please verify Packet Sniffer and traffic status")
    return None

def wait_for_prometheus(timeout_seconds=60):
    # Wait for Prometheus FIRING
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] WAIT Expecting Prometheus 'FIRING' (Timeout: {timeout_seconds}s)...")

    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if os.path.exists(PROMETHEUS_FILE):

            with open(PROMETHEUS_FILE, 'r') as f:
                ts = f.read().strip()

            if not ts:
                # File exists but has no content yet (Edge case, happened rarely)
                time.sleep(0.01)
                continue

            clean_ts = format_timestamp(ts)
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] SUCCESS Gray Failure has been detected at {clean_ts}")
            return ts

        time.sleep(0.01)

    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] TIMEOUT No signal from Prometheus")
    return None

def ospf_cooldown(cooldown_seconds=120):

    # Waiting for OSPF to recover
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] WAIT Initiating OSPF convergence cooldown ({cooldown_seconds}s)...")
    start_time = time.time()

    while time.time() - start_time < cooldown_seconds:
        remaining = int(cooldown_seconds - (time.time() - start_time))

        if remaining > 0 and remaining % 10 == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] INFO OSPF cooldown running... {remaining}s remaining")
            time.sleep(1) 
        time.sleep(0.1)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-2]}] SUCCESS OSPF cooldown complete. Network should be reconverged.")

def format_timestamp(timestamp):

    prom_clean = timestamp.replace("Z", "+00:00")
    dt_prom = datetime.fromisoformat(prom_clean)
    ts_prom = dt_prom.timestamp()
    return ts_prom

def analyze_icmp_window(t_prom, t_sniff, log_dir="/home/user/logs", ping_interval=0.05):

    # Calculate cumulative packet loss #

    # 1. Find newest log
    list_of_files = glob.glob(f"{log_dir}/cpl_*.log")
    if not list_of_files:
        print("No log found")
        return 0, 0, 0, 0.0
    latest_log = max(list_of_files, key=os.path.getctime)

    # 2. Variables for seq window
    seq_before = None
    seq_after = None
    seq_in_window = []

    # Create pattern, compile once
    pattern = re.compile(r"\[(\d+\.\d+)\] .* icmp_seq=(\d+)")

    # 3. Parse log
    with open(latest_log, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                ts = float(match.group(1))
                seq = int(match.group(2))

                if ts < t_prom:
                    seq_before = seq  # Last packet before t0
                elif t_prom <= ts <= t_sniff:
                    seq_in_window.append(seq)
                elif ts > t_sniff:
                    if seq_after is None:
                        seq_after = seq  # First packet after t1
                        break # Reached edge, stop parsing

    # 4. Maths
    received_packets = len(seq_in_window)
    
    # Prefered calculation
    if seq_before is not None and seq_after is not None:
        expected_packets = seq_after - seq_before - 1
        
    # Fallback for bad logs - this is not an exact measurement for high frequency ping! 
    else:
        print("[WARNING] Boundary packets missing! Using time-based estimation for expected packets at ping -i 0.05! Please check ICMP-Stream")
        window_duration = t_sniff - t_prom
        if window_duration > 0:
            expected_packets = math.ceil(window_duration / ping_interval)
        else:
            expected_packets = 0

    # 5. Finalize
    lost_packets = max(0, expected_packets - received_packets)
    loss_rate = (lost_packets / expected_packets * 100.0) if expected_packets > 0 else 0.0
    return expected_packets, received_packets, lost_packets, loss_rate