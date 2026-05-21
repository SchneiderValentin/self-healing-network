# Ansible Automation & Infrastructure

This directory contains all Infrastructure as Code and automation playbooks that were used in the testbed.

## Prerequisites

To run these playbooks, the management node requires:
* Ansible (`apt install ansible`).
* SSH key-based authentication configured for all testbed nodes.
* The `ansible_user` defined in `inventories/inventory.yaml` having `sudo` privileges without entering a password.

## Usage

To execute a playbook manually (like verify_time.yaml for verifying the NTP time synchronization across the testbed), run the following command from the ansible directory:

```bash
ansible-playbook -i inventories/inventory.yaml playbooks/setup/verify_time.yaml
```

## Directory Structure

To ensure separation of concerns, the playbooks will be divided into folders named by the function they provide interacting with the testbed.

```text
.
├── inventories/
│   └── inventory.yaml            # Inventory containing all testbed VM's except the management node itself
└── playbooks/
    └── setup/                    # Playbooks to prepare and patch the testbed
        ├── check_updates.yaml    # Verifies the last package update timestamp
        ├── set_hostnames.yaml    # Edits system hostnames at /etc/hosts to match inventory hostnames
        ├── update_nodes.yaml     # Performs safe apt-get upgrade
        └── verify_time.yaml      # Verifies NTP time synchronization across the testbed 
```
