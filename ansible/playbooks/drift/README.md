# Drift Detection

This directory contains files used to check for configuration drift in `frr.conf` via Ansible. It verifies that the manually configured router VMs remain consistent with the desired state defined in the Ansible configuration.

## Contents
- **`drift.yaml`**: The Ansible playbook executing the check
- **`templates/frr.conf.j2`**: The master blueprint for the FRR configuration
- **`host_vars/`**: Variables for each router VM

## Usage
To check for drift on all routers run:

```bash
ansible-playbook -i inventory.yaml drift.yaml --diff