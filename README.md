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

![Architecture Closed-Control-Loop](./architecture/mape.svg)

1. **Monitor:** ICMP Probing utilizing `Blackbox Exporter` to check for Packet Loss on Links.
2. **Analyze:** `Prometheus` analysis of Packet Loss occurrence to ensure Gray-Failure existence.
3. **Plan:** Prometheus `Alertmanager` and a `Python Webhook` receive Prometheus FIRING alerts and choose the remediation-mechanic.
4. **Execute:** Execution of `Ansible` playbook containing the chosen remediation-mechanic is triggered.
---

## Evaluation

The thesis evaluated the MAPE-K **Execute** phase in isolation. Three remediation mechanisms (RM1–RM3) were compared against Time-to-Mitigate (TTM), cumulative packet loss, and established resilience design principles.

The plot below compares TTM across 100 consecutive trials per mechanism, measured from the Prometheus `FIRING` event to the first packet received via a healthy link.

![TTM Comparison](./docs/ttm_comparison.svg)

Executed within the closed-loop, Administrative Shutdown (RM1) and OSPF Metric Overwrite (RM2) achieve average sub-second mitigation. In contrast, an unoptimized Cold Backup (RM3) takes approximately 18.5 seconds on average, illustrating the inherent trade-off between remediation speed and the resource efficiency of a passive cold standby.

## Repository Structure (Upcoming)

```text
.
├── ansible/             # Ansible playbooks
├── architecture/        # Architecture diagrams
├── configs/             # Configuration files
├── docs/                # Other documentation
├── src/                 # Webhook logic
├── .gitignore           # Git ignore rules for clean commits
└── README.md            # Project documentation (You are here)