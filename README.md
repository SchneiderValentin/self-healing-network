# Self-Healing Network Architecture for Gray Failures

[![Proxmox VE](https://img.shields.io/badge/Proxmox-VE-E57000?style=for-the-badge&logo=proxmox&logoColor=white)](#)
[![Ansible](https://img.shields.io/badge/Ansible-Automation-EE0000?style=for-the-badge&logo=ansible&logoColor=white)](#)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](#)
[![Grafana](https://img.shields.io/badge/Grafana-Observability-F46800?style=for-the-badge&logo=grafana&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-Logic-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)

**Automated Network Reconfiguration via Ansible & Prometheus in Proxmox VE.**

## Problem & Solution
* **Problem:** Gray failures (like creeping packet loss) evade traditional routing protocol detection, leading to silent degradation and poor network health without triggering standard failover mechanisms.
* **Solution:** A reactive Automation approach. By integrating Prometheus observability with Ansible-driven Network-reconfigurations, this architecture detects degradation in real-time and dynamically applies remediation-strategies to restore network integrity.

---

## Closed-Control-Loop

The system relies on a continuous closed-control-loop:

![Architecture Closed-Control-Loop](./docs/architecture_loop.svg)

1. **Monitor:** ICMP Probing utilizing `Blackbox Exporter` to check for Packet Loss on Links.
2. **Analyze:** `Prometheus` analysis of Packet Loss occurrence to ensure Gray-Failure existence.
3. **Plan:** Prometheus `Alertmanager` and a `Python Webhook` receive Prometheus FIRING alerts and choose the remediation-mechanic.
4. **Execute:** Execution of `Ansible` playbook containing the chosen remediation-mechanic is triggered.
---



## Repository Structure (Upcoming)

```text
.
├── ansible/             # Ansible playbooks
├── architecture/        # Architecture diagrams
├── docs/                # Other documentation
├── src/                 # Webhook logic
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation (You are here)
