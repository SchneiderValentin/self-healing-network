# Main Logic

This directory contains the core scripts for the automated experiment execution and closed-loop. It includes the master script, a webhook listener for Prometheus and convergence timestamps, and a packet sniffer designed to detect the first data packet arriving via the healthy alternative link.

## Directory Structure

```text
.
├── master.py                # Master script for closed-loop and automated experiment execution
├── push_timestamp_icmp.sh   # Packet sniffer logic
├── thesis_utils.py          # Helper functions for the master script (e.g., subprocess calls for Ansible playbook execution)
└── unified_webhook.py       # Webhook for receiving Prometheus FIRING alerts and packet sniffer timestamps