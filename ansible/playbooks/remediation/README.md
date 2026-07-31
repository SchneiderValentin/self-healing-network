# Ansible Playbooks

This directory contains the playbooks used to automate and execute experiments to evaluate remediation mechanisms.

### Quick Functionality Overview

* **`clean_isolate.yaml`**: Administratively shuts down Edge interfaces to a transit link, effectively isolating the link
* **`heal_clean_isolate.yaml`**: Inverse playbook to `clean_isolate.yaml`
* **`heal_failure.yaml`**: Removes `tc netem` rules on degraded transit
* **`infra_backup.yaml`**: Starts LXC as cold backup and verifies running state
* **`infra_reset.yaml`**: Inverse playbook to `infra_backup.yaml`
* **`inject_infra_failure.yaml`**: Places 30% packet loss on Transit -> Target link
* **`killping.yaml`**: Hard cuts all ping processes on Source
* **`proof_problem.yaml`**: Proves differential observability in the testbed
* **`start_infra_sniffer.yaml`**: Activates Packet Sniffer on Target Edge
* **`start_metric.yaml`**: Isolates transit link by increasing its OSPF metrics
* **`start_packet_loss_measurement.yaml`**: Starts datastream for measurements
* **`stop_metric.yaml`**: Inverse playbook to `start_metric.yaml`
* **`stop_packet_loss_measurement.yaml`**: Stops datastream for measurements and fetches results to management