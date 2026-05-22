# Testbed Base Configurations

This directory contains basic configuration files used for the Proxmox Host and VMs.

## Directory Structure

Configurations are separated by their system utilities or services.

```text
.
├── netplan/
│   ├── probing.yaml              # Network interfaces configuration for Probing Node
│   ├── source.yaml               # Network interfaces configuration for Source Node
│   └── ...                       # Other node network interfaces configurations
├── ssh/
│   └── ssh_config_template       # Template for easy SSH connection
└── README.md                     # Configurations documentation (You are here)