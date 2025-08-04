# 🚀 Proxmox AI Assistant - Quick Reference Guide

## 🐧 Ubuntu Copy-Paste Commands

**Most Common Commands for Ubuntu Users:**

```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant

# Activate virtual environment  
source venv/bin/activate

# Start the AI assistant
python -m src.proxmox_ai.cli.main

# Or use the script
./scripts/start-assistant.sh

# Quick start with specific commands
python -m src.proxmox_ai.cli.main ai chat          # Interactive chat
python -m src.proxmox_ai.cli.main ai status        # Check status
python -m src.proxmox_ai.cli.main vm list          # List VMs
```

## One-Minute Quick Start

```bash
# Install everything in one command
curl -fsSL https://raw.githubusercontent.com/diszay/iac-ai-assistant/main/scripts/express-install.sh | bash

# Start using immediately (Ubuntu)
cd ~/projects/iac-ai-assistant
source venv/bin/activate
python -m src.proxmox_ai.cli.main ai chat
```

## 📋 Essential Commands Cheat Sheet

### 🔍 System Status & Health - Ubuntu Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# System status commands
python -m src.proxmox_ai.cli.main status              # Quick health check
python -m src.proxmox_ai.cli.main doctor              # Comprehensive diagnostics  
python -m src.proxmox_ai.cli.main --version           # Show version info
python -m src.proxmox_ai.cli.main hardware-info       # Hardware analysis
python -m src.proxmox_ai.cli.main config list         # Show all configuration
```

### 🤖 AI Interaction - Ubuntu Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# AI interaction commands
python -m src.proxmox_ai.cli.main ai chat                                    # Interactive conversation
python -m src.proxmox_ai.cli.main ai ask "your question here"                # Quick question
python -m src.proxmox_ai.cli.main ai generate terraform "description"        # Generate Terraform
python -m src.proxmox_ai.cli.main ai generate ansible "description"          # Generate Ansible
python -m src.proxmox_ai.cli.main ai explain config-file.tf                 # Explain configuration
python -m src.proxmox_ai.cli.main ai optimize config-file.tf                # Optimize configuration
python -m src.proxmox_ai.cli.main ai security-review config-file.tf         # Security analysis
```

### 🖥️ VM Management - Ubuntu Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# VM management commands
python -m src.proxmox_ai.cli.main vm list                    # List all VMs
python -m src.proxmox_ai.cli.main vm info 101                # VM details
python -m src.proxmox_ai.cli.main vm start 101               # Start VM
python -m src.proxmox_ai.cli.main vm stop 101                # Stop VM
python -m src.proxmox_ai.cli.main vm create config.tf        # Create VM from config
```

### ⚙️ Configuration Management - Ubuntu Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Configuration commands
python -m src.proxmox_ai.cli.main config init                              # Initialize config
python -m src.proxmox_ai.cli.main config set proxmox.host "192.168.1.50"  # Set Proxmox host
python -m src.proxmox_ai.cli.main config set proxmox.user "root@pam"      # Set username
python -m src.proxmox_ai.cli.main config set ai.skill_level "intermediate" # Set skill level
python -m src.proxmox_ai.cli.main config get proxmox.host                 # Get setting value
```

### 🧠 AI Model Management - Ubuntu Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# AI model management
python -m src.proxmox_ai.cli.main ai status                   # Check AI service
python -m src.proxmox_ai.cli.main ai models                   # List available models
python -m src.proxmox_ai.cli.main ai optimize                 # Optimize for hardware
python -m src.proxmox_ai.cli.main ai switch-model MODEL_NAME  # Switch AI model
```

## 🎯 Common Usage Patterns

### Pattern 1: Generate Simple Infrastructure - Ubuntu Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Web server
python -m src.proxmox_ai.cli.main ai generate terraform "Ubuntu web server with nginx, 2GB RAM, 20GB disk"

# Database server  
python -m src.proxmox_ai.cli.main ai generate terraform "PostgreSQL server with 4GB RAM, 50GB disk, backup storage"

# Development environment
python -m src.proxmox_ai.cli.main ai generate terraform "3 Ubuntu VMs for development cluster with shared network"
```

### Pattern 2: Interactive Learning - Ubuntu Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Start chat and ask:
python -m src.proxmox_ai.cli.main ai chat

"I'm new to infrastructure automation, where should I start?"
"Create a simple web server and explain each part"
"What are the security best practices for VMs?"
"How do I set up automatic backups?"
```

### Pattern 3: Improve Existing Configuration - Ubuntu Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Analyze and improve
python -m src.proxmox_ai.cli.main ai explain existing-config.tf
python -m src.proxmox_ai.cli.main ai security-review existing-config.tf  
python -m src.proxmox_ai.cli.main ai optimize existing-config.tf
python -m src.proxmox_ai.cli.main ai fix existing-config.tf
```

## 🔧 Copy-Paste Configuration Examples

### Basic VM Configuration
```hcl
# Save as: basic-vm.tf
resource "proxmox_vm_qemu" "basic_vm" {
  name        = "ubuntu-basic"
  target_node = "pve"
  vmid        = 100
  
  memory = 2048
  cores  = 2
  
  clone      = "ubuntu-22.04-template" 
  full_clone = true
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
  
  disk {
    storage = "local-lvm"
    type    = "virtio" 
    size    = "20G"
  }
}
```

### Web Server with Nginx
```hcl
# Save as: web-server.tf
resource "proxmox_vm_qemu" "web_server" {
  name        = "web-server-01"
  target_node = "pve"
  vmid        = 101
  
  memory = 4096
  cores  = 2
  
  clone      = "ubuntu-22.04-template"
  full_clone = true
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
  
  disk {
    storage = "local-lvm"
    type    = "virtio"
    size    = "30G"
  }
  
  # Cloud-init configuration
  os_type    = "cloud-init"
  ciuser     = "ubuntu"
  cipassword = "secure-password"
  
  ipconfig0 = "ip=192.168.1.100/24,gw=192.168.1.1"
  
  provisioner "remote-exec" {
    inline = [
      "sudo apt update",
      "sudo apt install -y nginx",
      "sudo systemctl enable nginx",
      "sudo systemctl start nginx"
    ]
  }
}
```

### Development Cluster (3 VMs)
```hcl
# Save as: dev-cluster.tf
variable "vm_count" {
  default = 3
}

resource "proxmox_vm_qemu" "dev_cluster" {
  count = var.vm_count
  
  name        = "dev-node-${count.index + 1}"
  target_node = "pve"
  vmid        = 200 + count.index + 1
  
  memory = 4096
  cores  = 2
  
  clone      = "ubuntu-22.04-template"
  full_clone = true
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
  
  disk {
    storage = "local-lvm"
    type    = "virtio"
    size    = "40G"
  }
  
  # Sequential IP addressing
  ipconfig0 = "ip=192.168.1.${200 + count.index + 1}/24,gw=192.168.1.1"
}
```

## 🔒 Security Best Practices (Copy-Paste)

### Secure VM Template
```hcl
# Save as: secure-vm.tf
resource "proxmox_vm_qemu" "secure_vm" {
  name        = "secure-server"
  target_node = "pve"
  vmid        = 150
  
  memory = 4096
  cores  = 2
  
  clone      = "ubuntu-22.04-template"
  full_clone = true
  
  # Security-focused settings
  bios       = "ovmf"           # UEFI for better security
  boot       = "order=scsi0"    # Secure boot order
  scsihw     = "virtio-scsi-pci"
  
  network {
    model    = "virtio"
    bridge   = "vmbr0"
    firewall = true             # Enable VM firewall
  }
  
  disk {
    storage  = "local-lvm"
    type     = "virtio"
    size     = "30G"
    backup   = true             # Enable backups
    iothread = true             # Better I/O performance
  }
  
  # Cloud-init with security hardening
  os_type    = "cloud-init"
  ciuser     = "admin"
  cipassword = var.secure_password
  
  ipconfig0 = "ip=192.168.1.150/24,gw=192.168.1.1"
  
  # Post-deployment security hardening
  provisioner "remote-exec" {
    inline = [
      "sudo apt update && sudo apt upgrade -y",
      "sudo ufw enable",
      "sudo ufw default deny incoming",
      "sudo ufw allow ssh",
      "sudo fail2ban-client start",
      "sudo systemctl enable fail2ban"
    ]
  }
}
```

## 📦 Ansible Automation Examples

### Server Hardening Playbook
```yaml
# Save as: harden-servers.yml
---
- name: Harden Ubuntu Servers
  hosts: all
  become: yes
  tasks:
    - name: Update system packages
      apt:
        update_cache: yes
        upgrade: dist
        
    - name: Install security packages
      apt:
        name:
          - ufw
          - fail2ban
          - unattended-upgrades
        state: present
        
    - name: Configure firewall
      ufw:
        rule: "{{ item.rule }}"
        port: "{{ item.port }}"
      loop:
        - { rule: 'allow', port: 'ssh' }
        - { rule: 'allow', port: '80' }
        - { rule: 'allow', port: '443' }
        
    - name: Enable firewall
      ufw:
        state: enabled
        
    - name: Configure automatic updates
      lineinfile:
        path: /etc/apt/apt.conf.d/20auto-upgrades
        create: yes
        line: "{{ item }}"
      loop:
        - 'APT::Periodic::Update-Package-Lists "1";'
        - 'APT::Periodic::Unattended-Upgrade "1";'
```

### Docker Installation Playbook
```yaml
# Save as: install-docker.yml
---
- name: Install Docker on Ubuntu
  hosts: all
  become: yes
  tasks:
    - name: Install prerequisites
      apt:
        name:
          - apt-transport-https
          - ca-certificates
          - curl
          - gnupg
          - lsb-release
        update_cache: yes
        
    - name: Add Docker GPG key
      apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        state: present
        
    - name: Add Docker repository
      apt_repository:
        repo: "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
        state: present
        
    - name: Install Docker
      apt:
        name:
          - docker-ce
          - docker-ce-cli
          - containerd.io
          - docker-compose-plugin
        update_cache: yes
        
    - name: Start and enable Docker
      systemd:
        name: docker
        state: started
        enabled: yes
        
    - name: Add user to docker group
      user:
        name: "{{ ansible_user }}"
        groups: docker
        append: yes
```

## 🎯 Skill Level Quick Commands

### Beginner Commands - Ubuntu Terminal
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Set beginner mode
python -m src.proxmox_ai.cli.main config set ai.skill_level beginner

# Simple generations with explanations
python -m src.proxmox_ai.cli.main ai generate terraform "Basic Ubuntu VM" --skill beginner
python -m src.proxmox_ai.cli.main ai explain my-config.tf --skill beginner
python -m src.proxmox_ai.cli.main ai ask "What is a virtual machine?" --skill beginner
```

### Intermediate Commands - Ubuntu Terminal
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Set intermediate mode (default)
python -m src.proxmox_ai.cli.main config set ai.skill_level intermediate

# Production-ready configurations
python -m src.proxmox_ai.cli.main ai generate terraform "Web app with load balancer" --skill intermediate
python -m src.proxmox_ai.cli.main ai security-review my-infrastructure.tf --skill intermediate
python -m src.proxmox_ai.cli.main ai optimize my-config.tf --skill intermediate
```

### Expert Commands - Ubuntu Terminal
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Set expert mode
python -m src.proxmox_ai.cli.main config set ai.skill_level expert

# Advanced scenarios
python -m src.proxmox_ai.cli.main ai generate terraform "HA Kubernetes cluster" --skill expert
python -m src.proxmox_ai.cli.main ai generate terraform "Multi-tier app with monitoring" --skill expert
python -m src.proxmox_ai.cli.main ai analyze production-infrastructure/ --skill expert
```

## 🚨 Emergency Commands

### Quick Diagnostics
```bash
# Check everything quickly
proxmox-ai doctor

# Test connectivity
proxmox-ai vm list
curl -k https://YOUR_PROXMOX_HOST:8006/api2/json/version

# Check AI service
proxmox-ai ai-status
curl http://localhost:11434/api/tags
```

### Fix Common Issues
```bash
# Restart Ollama service
ollama serve &

# Reconnect to Proxmox
proxmox-ai config set proxmox.host "YOUR_HOST"
proxmox-ai config test

# Reset configuration
proxmox-ai config init --reset

# Clear cache and restart
rm -rf ~/.cache/proxmox-ai/
proxmox-ai status
```

## 📞 Getting Help

### Interactive Help
```bash
# Start learning conversation
proxmox-ai chat
# Then ask: "I need help with [your topic]"

# Command-specific help
proxmox-ai generate --help
proxmox-ai vm --help
proxmox-ai config --help
```

### Common Questions
```bash
# Ask the AI directly
proxmox-ai ask "How do I increase VM memory?"
proxmox-ai ask "What are the networking options?"
proxmox-ai ask "How do I backup my VMs?"
proxmox-ai ask "What's the difference between clone and template?"
```

## 🔄 Update Commands

### Keep System Updated
```bash
# Update application
cd ~/projects/iac-ai-assistant
git pull
pip install -e . --upgrade

# Update AI models
proxmox-ai ai models --update

# Update Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

## 💡 Pro Tips

### Performance Optimization
```bash
# Check hardware recommendations
proxmox-ai hardware-info

# Switch to optimal model
proxmox-ai ai optimize

# Enable caching
proxmox-ai config set ai.cache_enabled true
```

### Save Common Configurations
```bash
# Create template directory
mkdir -p ~/.proxmox-ai/templates

# Save frequently used configs
proxmox-ai generate terraform "Web server" --output ~/.proxmox-ai/templates/web.tf
proxmox-ai generate terraform "Database" --output ~/.proxmox-ai/templates/db.tf

# Reuse templates
proxmox-ai modify ~/.proxmox-ai/templates/web.tf "Add 4GB RAM"
```

### Batch Operations
```bash
# Generate multiple configurations
proxmox-ai generate terraform "Web tier" --output web.tf
proxmox-ai generate terraform "App tier" --output app.tf  
proxmox-ai generate terraform "DB tier" --output db.tf

# Validate all configs
for f in *.tf; do proxmox-ai validate "$f"; done

# Deploy all (be careful!)
for f in *.tf; do proxmox-ai vm create "$f"; done
```

---

**💡 Remember**: Always start with `proxmox-ai chat` for interactive help and learning!

**🔗 More Help**:
- Full documentation: [docs/](../docs/)
- Troubleshooting: [docs/troubleshooting/common-issues.md](troubleshooting/common-issues.md)
- Examples: [docs/user-guides/](user-guides/)

---

**Document Version**: 1.0  
**Last Updated**: 2025-07-30  
**Quick Reference for**: Proxmox AI Infrastructure Assistant