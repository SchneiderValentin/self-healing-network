# Ansible Playbooks

This directory contains the playbooks used for testbed setup und updating.

### Quick Functionality Overview

* **`check_updates.yaml`**: # Verifies the last package update timestamp
* **`set_hostnames.yaml`**: # Edits system hostnames at /etc/hosts to match inventory hostnames
* **`shutdown_vms`**: Shutdowns all VMs (not LXC's), excluding provided node ID
* **`start_vms`**: Starts all VMs (not LXC's)
* **`update_nodes`**: # Performs safe apt-get upgrade
* **`verify_time.yaml`**: Verifies NTP time synchronization across the testbed (for setup purposes only)