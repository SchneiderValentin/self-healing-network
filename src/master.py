import argparse
import os
import csv
import time
from datetime import datetime
from thesis_utils import *

# --- CONFIG --- #
ANSIBLE_INVENTORY = "inventories/inventory.yaml"        # Adjust this path for your directory structure #
WEBHOOK_PORT = 5000

# --- CONSOLE OUTPUT COLORS --- #
GREEN = '\033[92m'
RESET = '\033[0m'

# --- MAIN --- #
def main():

    # Initialize arg parser #
    parser = argparse.ArgumentParser(description="Master Script")
    parser.add_argument(
        "-i", "--iterations",
        type=int,
        default=1,
        help="Number of runs (default: 1)"
    )
    args = parser.parse_args()
    total_iterations = args.iterations

    # Validate that .csv exists #
    csv_filename = "rm1_results.csv"                    # Change this for alternative mechanism #
    if not os.path.exists(csv_filename):
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Iteration", 
                "Prometheus_Time", 
                "Sniffer_Time", 
                "Time_To_Mitigate_Seconds",
                "Expected_ICMP_Packets", 
                "Received_ICMP_Packets", 
                "Lost_ICMP_Packets", 
                "ICMP_Loss_Rate_Percent"
            ])

    
    # Start execution loop #
    # Add or remove Playbooks as required #
    # Built Ansible subprocesses like this: cmd_start_icmp = ["ansible-playbook", "-i", ANSIBLE_INVENTORY, "start_packet_loss_measurement.yaml"] #

    print("\n" + "=" * 90)
    print(f"AUTOMATED EXPERIMENT EXECUTION - RUNNING {total_iterations} ITERATIONS")
    print("=" * 90)

    for current_iter in range(1, total_iterations + 1):

        print("\n" + "=" * 90)
        print(f"STARTING ITERATION {current_iter} OF {total_iterations}")
        print("=" * 90 + "\n")

        print("-" * 90)

        # Clear previous dropfiles
        clear_old_alerts()

        print("-" * 90)

        # Verify webhook is live
        if not check_webhook_running(WEBHOOK_PORT):
            print("Webhook not running. Exit.")
            exit(1)

        print("-" * 90)

        # Activate ICMP Stream                          # Expected ping -i : 0.05 otherwise check thesis_utils.py#
        cmd_start_icmp = ["ansible-playbook", "-i", ANSIBLE_INVENTORY, "start_packet_loss_measurement.yaml"]
        if not run_playbook(cmd_start_icmp, "Activate ICMP Stream"):
            exit(1)

        print("-" * 90)

        # Activate Packet Sniffer
        cmd_sniffer = ["ansible-playbook", "-i", ANSIBLE_INVENTORY, "start_infra_sniffer.yaml"]
        if not run_playbook(cmd_sniffer, "Activate Packet Sniffer"):
            exit(1)

        print("-" * 90)

        # Inject Gray Failure
        cmd_inject = ["ansible-playbook", "-i", ANSIBLE_INVENTORY, "inject_infra_failure.yaml"]
        if not run_playbook(cmd_inject, "Injecting Gray Failure"):
            exit(1)

        print("-" * 90)

        # Wait for Prometheus FIRING
        prometheus_ts_str = wait_for_prometheus(timeout_seconds=60)
        if not prometheus_ts_str:
            print("FAILED: Prometheus Alert not received!")
            exit(1)

        print("-" * 90)

        # Take Remediation Action 
        cmd_remediate = [
            "ansible-playbook", 
            "-i", "inventories/inventory.yaml", #  
            "clean_isolate.yaml"                        # Change this for alternative mechanism #
        ]
        if not run_playbook(cmd_remediate, "Take action"):
            exit(1)

        print("-" * 90)

        # Wait for Time To Mitigate
        sniffer_ts_str = wait_for_sniffer(timeout_seconds=60)
        if not sniffer_ts_str:
            print("Iteration cancelled: No reaction from sniffer received.")
            run_playbook(["ansible-playbook", "-i", ANSIBLE_INVENTORY, "heal_failure.yaml"], "Safety heal")
            exit(1)

        print("-" * 90)

        # Buffer measurement
        time.sleep(5)

        # Stop ICMP Stream
        cmd_stop_icmp = ["ansible-playbook", "-i", ANSIBLE_INVENTORY, "stop_packet_loss_measurement.yaml"]
        if not run_playbook(cmd_stop_icmp, "Parse ICMP stream"):
            exit(1)

        print("-" * 90)

        cmd_kill_icmp = ["ansible-playbook", "-i", ANSIBLE_INVENTORY, "killping.yaml"]
        if not run_playbook(cmd_kill_icmp, "Stop ICMP stream"):
            exit(1)

        print("-" * 90)

        # Heal Gray Failure
        cmd_heal = ["ansible-playbook", "-i", ANSIBLE_INVENTORY, "heal_failure.yaml"]
        if not run_playbook(cmd_heal, "Healing Gray Failure"):
            exit(1)

        print("-" * 90)

        # Resetting Network Configuration
        cmd_reset = [
            "ansible-playbook", 
            "-i", "inventories/inventory.yaml", 
            "heal_clean_isolate.yaml",                  # Change this for alternative mechanism #
        ]
        if not run_playbook(cmd_reset, "Reset network configuration"):
            exit(1)
        print("-" * 90)

        # Write TTM & Analyze ICMP        
        try:
            # 1. Parse t0 
            clean_prom_str = prometheus_ts_str.replace("Z", "+00:00")
            prom_dt = datetime.fromisoformat(clean_prom_str)
            t_prom = prom_dt.timestamp()

            # 2. Fetch t1
            t_sniff = float(sniffer_ts_str)

            # 3. Calculate TTM
            ttm_seconds = t_sniff - t_prom

            # 4. Create readable Strings for .csv
            prom_readable = prom_dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            sniff_readable = datetime.fromtimestamp(t_sniff).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            # 5. Analyze cumulative packet loss
            exp_pkts, recv_pkts, lost_pkts, loss_rate = analyze_icmp_window(
                t_prom, 
                t_sniff, 
                log_dir="/home/user/logs"
            )

            # 6. Write into .csv
            with open(csv_filename, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    current_iter,     
                    prom_readable,    
                    sniff_readable,   
                    round(ttm_seconds, 4),
                    exp_pkts,
                    recv_pkts,
                    lost_pkts,
                    round(loss_rate, 2)                 # Add more optional timestamps here #
                ])

            # 7. Show results on console
            print("\n")
            print(f"{GREEN}>>> TTM = {ttm_seconds:.4f}s | ICMP Loss: {lost_pkts}/{exp_pkts} Packets ({loss_rate:.2f}%) <<<{RESET}")
            print("\n" + "=" * 90)

        except Exception as e:
            print(f"Error in analysis: {e}")

        # Initiate cooldown phase before next iteration
        if current_iter < total_iterations:
            ospf_cooldown(30)                           # Change this param to adjust cooldown#

        print(f"Iteration {current_iter} executed successfully.")
        print("=" * 90)

    print("\nALL ITERATIONS COMPLETED")

if __name__ == "__main__":
    main()