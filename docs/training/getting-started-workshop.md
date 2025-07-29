# Getting Started Workshop: Proxmox AI Infrastructure Assistant

## Workshop Overview

**Duration:** 4 hours  
**Format:** Hands-on workshop with guided exercises  
**Prerequisites:** Basic knowledge of virtualization concepts and command-line interface  
**Target Audience:** System administrators, DevOps engineers, infrastructure operators

## Learning Objectives

By the end of this workshop, participants will be able to:
- Install and configure the Proxmox AI Infrastructure Assistant
- Create and manage virtual machines using CLI commands
- Implement security best practices for VM deployments
- Use AI-assisted infrastructure operations
- Monitor and troubleshoot common issues
- Integrate the system into existing workflows

## Workshop Prerequisites

### System Requirements
- **Local Machine:** macOS, Linux, or Windows with SSH client
- **Network Access:** SSH connectivity to Proxmox host (port 2849)
- **Credentials:** Provided during workshop registration
- **Software:** Terminal/command prompt, text editor

### Pre-Workshop Setup
Participants should complete these steps before the workshop:

1. **Verify SSH Connectivity**
   ```bash
   ssh -p 2849 workshop-user@training.proxmox-ai.internal
   ```

2. **Download Workshop Materials**
   ```bash
   git clone https://github.com/proxmox-ai/workshop-materials.git
   cd workshop-materials
   ```

3. **Install Required Tools**
   ```bash
   # Install workshop CLI tools
   curl -sSL https://get.proxmox-ai.com/workshop-install.sh | bash
   ```

## Module 1: Introduction and Setup (30 minutes)

### 1.1 Welcome and Overview (10 minutes)

**Workshop Introduction**
- Welcome and introductions
- Workshop agenda and objectives
- Lab environment overview
- Safety guidelines for infrastructure operations

**Architecture Overview**
- Proxmox AI Infrastructure Assistant components
- Security-first design principles
- AI integration benefits
- Use cases and real-world applications

### 1.2 Environment Setup (20 minutes)

**Lab Environment Access**

Each participant receives:
- **SSH Credentials:** username/password for lab access
- **Workshop VM:** Dedicated VM for hands-on exercises
- **API Token:** Pre-configured for workshop activities
- **Lab Guide:** Reference materials and exercise solutions

**Initial Connection Test**
```bash
# Connect to workshop environment
ssh -p 2849 workshop-user-01@training.proxmox-ai.internal

# Verify system status
proxmox-ai status

# Check available resources
proxmox-ai system resources
```

**Expected Output:**
```
🤖 Proxmox AI Infrastructure Assistant v1.0.0
✅ System Status: Operational
✅ Security: Enabled
✅ API Connectivity: Connected
✅ AI Service: Available

Workshop Environment: Ready
Assigned VM Range: 200-210
Available Resources: 8 CPU cores, 32GB RAM, 500GB storage
```

### 1.3 CLI Basics (15 minutes)

**Command Structure**
```bash
# Basic command syntax
proxmox-ai <resource> <action> [options]

# Get help for any command
proxmox-ai --help
proxmox-ai vm --help
proxmox-ai vm create --help
```

**Essential Commands**
```bash
# System information
proxmox-ai info
proxmox-ai version

# Authentication status
proxmox-ai auth status

# Resource overview
proxmox-ai resources
```

**Exercise 1.1: CLI Exploration**
```bash
# Task: Use help commands to discover available operations
# Time: 5 minutes

# 1. List all available resource types
proxmox-ai --help

# 2. Explore VM operations
proxmox-ai vm --help

# 3. Check network commands
proxmox-ai network --help

# 4. Review security operations
proxmox-ai security --help
```

## Module 2: Virtual Machine Management (60 minutes)

### 2.1 VM Creation Fundamentals (20 minutes)

**VM Templates Overview**
```bash
# List available templates
proxmox-ai template list

# Template details
proxmox-ai template show ubuntu-22.04-secure
```

**Basic VM Creation**
```bash
# Create a simple VM
proxmox-ai vm create \
  --name "workshop-vm-01" \
  --template "ubuntu-22.04-secure" \
  --cpu-cores 2 \
  --memory 4096 \
  --storage 50 \
  --description "My first workshop VM"
```

**Exercise 2.1: Create Your First VM**
```bash
# Task: Create a VM with specific configuration
# Time: 10 minutes

# Create VM with your assigned number (replace XX with your number)
proxmox-ai vm create \
  --name "workshop-vm-XX" \
  --template "ubuntu-22.04-secure" \
  --cpu-cores 2 \
  --memory 4096 \
  --storage 50 \
  --network-vlan 200 \
  --description "Created by [Your Name]"

# Monitor creation progress
proxmox-ai job status <job-id>

# Verify VM status
proxmox-ai vm show workshop-vm-XX
```

### 2.2 VM Configuration and Management (25 minutes)

**VM Operations**
```bash
# List VMs
proxmox-ai vm list

# Start VM
proxmox-ai vm start workshop-vm-XX

# Check VM status
proxmox-ai vm status workshop-vm-XX

# Stop VM
proxmox-ai vm stop workshop-vm-XX

# VM details
proxmox-ai vm show workshop-vm-XX --detailed
```

**VM Modification**
```bash
# Increase memory
proxmox-ai vm update workshop-vm-XX --memory 8192

# Add CPU cores
proxmox-ai vm update workshop-vm-XX --cpu-cores 4

# Update description
proxmox-ai vm update workshop-vm-XX --description "Updated in workshop"
```

**Exercise 2.2: VM Management Operations**
```bash
# Task: Practice VM lifecycle management
# Time: 15 minutes

# 1. Start your VM
proxmox-ai vm start workshop-vm-XX

# 2. Monitor startup process
proxmox-ai vm status workshop-vm-XX --watch

# 3. Connect to VM console (when available)
proxmox-ai vm console workshop-vm-XX

# 4. Update VM configuration
proxmox-ai vm update workshop-vm-XX --memory 6144

# 5. Create a snapshot
proxmox-ai vm snapshot create workshop-vm-XX \
  --name "workshop-checkpoint" \
  --description "Checkpoint during workshop"

# 6. List snapshots
proxmox-ai vm snapshot list workshop-vm-XX
```

### 2.3 Advanced VM Features (15 minutes)

**Network Configuration**
```bash
# Configure static IP
proxmox-ai vm network set workshop-vm-XX \
  --interface eth0 \
  --ip 192.168.200.10 \
  --netmask 255.255.255.0 \
  --gateway 192.168.200.1

# Add secondary network interface
proxmox-ai vm network add workshop-vm-XX \
  --interface eth1 \
  --vlan 201
```

**Storage Management**
```bash
# Add additional disk
proxmox-ai vm disk add workshop-vm-XX \
  --size 20 \
  --type ssd \
  --mount-point /data

# Resize existing disk
proxmox-ai vm disk resize workshop-vm-XX \
  --disk 0 \
  --size 60
```

**Exercise 2.3: Advanced Configuration**
```bash
# Task: Configure advanced VM features
# Time: 10 minutes

# 1. Configure VM network
proxmox-ai vm network set workshop-vm-XX \
  --interface eth0 \
  --ip 192.168.200.XX \
  --netmask 255.255.255.0 \
  --gateway 192.168.200.1

# 2. Add data disk
proxmox-ai vm disk add workshop-vm-XX \
  --size 10 \
  --type ssd \
  --name "data-disk"

# 3. Apply tags
proxmox-ai vm tag add workshop-vm-XX \
  --tags "workshop,training,ubuntu"

# 4. View complete configuration
proxmox-ai vm show workshop-vm-XX --config-only
```

## Module 3: Security Implementation (45 minutes)

### 3.1 Security Fundamentals (15 minutes)

**Security Best Practices Overview**
- Encryption at rest (LUKS)
- Network segmentation
- SSH key authentication
- Firewall configuration
- Regular security updates

**Security Assessment**
```bash
# Run security scan on VM
proxmox-ai security scan workshop-vm-XX

# Check compliance status
proxmox-ai security compliance workshop-vm-XX --standard cis

# View security recommendations
proxmox-ai security recommendations workshop-vm-XX
```

### 3.2 Implementing Security Controls (20 minutes)

**Disk Encryption**
```bash
# Enable disk encryption (on new VM)
proxmox-ai vm create \
  --name "secure-vm-XX" \
  --template "ubuntu-22.04-secure" \
  --cpu-cores 2 \
  --memory 4096 \
  --storage 50 \
  --encrypt-disk \
  --description "Encrypted VM for security demo"
```

**SSH Key Management**
```bash
# Generate SSH key pair for VM access
ssh-keygen -t ed25519 -f ~/.ssh/workshop_key -C "workshop-$(date +%s)"

# Add SSH key to VM
proxmox-ai vm ssh-key add workshop-vm-XX \
  --key-file ~/.ssh/workshop_key.pub \
  --user ubuntu
```

**Firewall Configuration**
```bash
# Enable VM firewall
proxmox-ai vm firewall enable workshop-vm-XX

# Add firewall rules
proxmox-ai vm firewall rule add workshop-vm-XX \
  --action accept \
  --protocol tcp \
  --port 22 \
  --source 192.168.200.0/24 \
  --description "SSH access from workshop network"

# Add HTTP rule
proxmox-ai vm firewall rule add workshop-vm-XX \
  --action accept \
  --protocol tcp \
  --port 80 \
  --source any \
  --description "HTTP access"
```

**Exercise 3.1: Security Hardening**
```bash
# Task: Implement security controls on your VM
# Time: 15 minutes

# 1. Run initial security scan
proxmox-ai security scan workshop-vm-XX

# 2. Enable firewall
proxmox-ai vm firewall enable workshop-vm-XX

# 3. Configure SSH access
ssh-keygen -t ed25519 -f ~/.ssh/workshop_vm_XX -C "workshop-vm-XX"
proxmox-ai vm ssh-key add workshop-vm-XX \
  --key-file ~/.ssh/workshop_vm_XX.pub

# 4. Add firewall rules
proxmox-ai vm firewall rule add workshop-vm-XX \
  --action accept \
  --protocol tcp \
  --port 22 \
  --source 192.168.200.0/24

# 5. Run post-hardening scan
proxmox-ai security scan workshop-vm-XX --compare-baseline
```

### 3.3 Security Monitoring (10 minutes)

**Security Monitoring Commands**
```bash
# Monitor security events
proxmox-ai security events --vm workshop-vm-XX --last-hour

# Check for vulnerabilities
proxmox-ai security vulnerabilities workshop-vm-XX

# View security metrics
proxmox-ai security metrics workshop-vm-XX
```

**Exercise 3.2: Security Monitoring**
```bash
# Task: Set up security monitoring
# Time: 5 minutes

# 1. Enable security monitoring
proxmox-ai vm monitoring enable workshop-vm-XX \
  --security-events \
  --intrusion-detection

# 2. View current security status
proxmox-ai security status workshop-vm-XX

# 3. Set up alerts
proxmox-ai security alert create \
  --vm workshop-vm-XX \
  --type security-violation \
  --notification email
```

## Module 4: AI-Assisted Operations (45 minutes)

### 4.1 AI Integration Overview (10 minutes)

**AI Capabilities**
- Natural language infrastructure requests
- Automated code generation
- Intelligent troubleshooting
- Security best practice recommendations
- Performance optimization suggestions

**AI Safety Features**
- Request validation and sanitization
- Generated code security scanning
- Human approval for high-risk operations
- Comprehensive audit logging

### 4.2 Using AI for Infrastructure Tasks (25 minutes)

**Natural Language VM Creation**
```bash
# Create VM using natural language
proxmox-ai ai create "Create a secure web server VM with 4GB RAM, enable HTTPS, and configure firewall for port 80 and 443"

# AI-generated network configuration
proxmox-ai ai configure "Set up a development network with DHCP and isolated from production"

# AI security hardening
proxmox-ai ai secure "Apply CIS benchmarks to workshop-vm-XX and enable monitoring"
```

**Exercise 4.1: AI-Assisted VM Creation**
```bash
# Task: Use AI to create and configure a VM
# Time: 15 minutes

# 1. Create VM with AI assistance
proxmox-ai ai create "Create a database server VM named db-vm-XX with 8GB RAM, 100GB storage, encrypted disk, and MySQL optimization"

# 2. Review generated configuration
proxmox-ai job show <job-id> --show-generated-code

# 3. Apply AI security recommendations
proxmox-ai ai secure "Harden db-vm-XX for production database workload with CIS compliance"

# 4. Validate AI-generated configuration
proxmox-ai vm validate db-vm-XX --security-check
```

### 4.3 AI Troubleshooting and Optimization (10 minutes)

**AI-Powered Troubleshooting**
```bash
# Diagnose VM issues
proxmox-ai ai diagnose workshop-vm-XX "VM is running slowly and has high CPU usage"

# Performance optimization
proxmox-ai ai optimize workshop-vm-XX --workload web-server

# Security analysis
proxmox-ai ai analyze-security workshop-vm-XX --generate-report
```

**Exercise 4.2: AI Troubleshooting**
```bash
# Task: Use AI for problem diagnosis and optimization
# Time: 8 minutes

# 1. Simulate performance issue
proxmox-ai vm stress-test workshop-vm-XX --cpu-load 80

# 2. Use AI to diagnose issue
proxmox-ai ai diagnose workshop-vm-XX "High CPU usage affecting performance"

# 3. Apply AI recommendations
proxmox-ai ai optimize workshop-vm-XX --apply-recommendations

# 4. Verify improvements
proxmox-ai vm metrics workshop-vm-XX --compare-before-after
```

## Module 5: Monitoring and Operations (30 minutes)

### 5.1 System Monitoring (15 minutes)

**Monitoring Commands**
```bash
# System overview
proxmox-ai monitor dashboard

# VM performance metrics
proxmox-ai monitor vm workshop-vm-XX --metrics cpu,memory,disk,network

# Real-time monitoring
proxmox-ai monitor vm workshop-vm-XX --real-time --duration 5m
```

**Setting Up Alerts**
```bash
# Create performance alert
proxmox-ai alert create \
  --vm workshop-vm-XX \
  --metric cpu_usage \
  --threshold 80 \
  --duration 5m \
  --action email

# Create disk space alert
proxmox-ai alert create \
  --vm workshop-vm-XX \
  --metric disk_usage \
  --threshold 85 \
  --action notification
```

### 5.2 Backup and Recovery (15 minutes)

**Backup Operations**
```bash
# Create manual backup
proxmox-ai backup create workshop-vm-XX \
  --type full \
  --compression gzip \
  --description "Workshop checkpoint backup"

# List backups
proxmox-ai backup list --vm workshop-vm-XX

# Schedule automated backups
proxmox-ai backup schedule workshop-vm-XX \
  --frequency daily \
  --time "02:00" \
  --retention 7 \
  --type incremental
```

**Exercise 5.1: Backup and Monitoring Setup**
```bash
# Task: Configure monitoring and backup
# Time: 10 minutes

# 1. Create baseline backup
proxmox-ai backup create workshop-vm-XX \
  --type full \
  --encrypt \
  --description "Pre-workshop backup"

# 2. Set up monitoring dashboard
proxmox-ai monitor setup workshop-vm-XX \
  --metrics cpu,memory,disk,network \
  --refresh-interval 30s

# 3. Configure alerts
proxmox-ai alert create \
  --vm workshop-vm-XX \
  --metric cpu_usage \
  --threshold 75 \
  --notification email

# 4. Schedule regular backups
proxmox-ai backup schedule workshop-vm-XX \
  --frequency daily \
  --time "01:00" \
  --retention 14
```

## Module 6: Integration and Best Practices (30 minutes)

### 6.1 API Integration (15 minutes)

**API Basics**
```bash
# Generate API token
proxmox-ai auth token create \
  --name "workshop-integration" \
  --permissions "vm:read,vm:write" \
  --expires-in 3600

# Test API connectivity
curl -H "Authorization: Bearer <token>" \
  https://api.proxmox-ai.internal/v1/vms
```

**Python Integration Example**
```python
#!/usr/bin/env python3
# Workshop API integration example

import requests
import json
import os

# API configuration
API_BASE = "https://api.proxmox-ai.internal/v1"
API_TOKEN = os.getenv('PROXMOX_AI_TOKEN')

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

def list_vms():
    """List all VMs"""
    response = requests.get(f"{API_BASE}/vms", headers=headers)
    return response.json()

def create_vm(config):
    """Create a new VM"""
    response = requests.post(f"{API_BASE}/vms", headers=headers, json=config)
    return response.json()

# Example usage
if __name__ == "__main__":
    # List existing VMs
    vms = list_vms()
    print(f"Found {len(vms['data']['vms'])} VMs")
    
    # Create new VM
    vm_config = {
        "name": "api-created-vm",
        "template": "ubuntu-22.04-secure",
        "cpu_cores": 2,
        "memory_mb": 4096,
        "storage_gb": 50
    }
    
    result = create_vm(vm_config)
    print(f"VM creation job: {result['data']['vm']['creation_job_id']}")
```

### 6.2 CI/CD Integration (15 minutes)

**GitHub Actions Example**
```yaml
# .github/workflows/infrastructure.yml
name: Deploy Infrastructure

on:
  push:
    branches: [main]
    paths: ['infrastructure/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Proxmox AI CLI
        run: |
          curl -sSL https://get.proxmox-ai.com/install.sh | bash
          echo "${{ secrets.PROXMOX_AI_TOKEN }}" > ~/.proxmox-ai/token
      
      - name: Validate Infrastructure
        run: |
          proxmox-ai validate infrastructure/vm-config.yaml
      
      - name: Deploy VMs
        run: |
          proxmox-ai deploy infrastructure/vm-config.yaml
      
      - name: Run Security Scan
        run: |
          proxmox-ai security scan --all --format json > security-report.json
      
      - name: Upload Security Report
        uses: actions/upload-artifact@v2
        with:
          name: security-report
          path: security-report.json
```

**Exercise 6.1: Automation Setup**
```bash
# Task: Create automation scripts
# Time: 10 minutes

# 1. Create VM deployment script
cat << 'EOF' > deploy_vm.sh
#!/bin/bash
set -e

VM_NAME="$1"
TEMPLATE="$2"
CPU_CORES="${3:-2}"
MEMORY="${4:-4096}"

echo "Deploying VM: $VM_NAME"

# Create VM
JOB_ID=$(proxmox-ai vm create \
  --name "$VM_NAME" \
  --template "$TEMPLATE" \
  --cpu-cores "$CPU_CORES" \
  --memory "$MEMORY" \
  --format json | jq -r '.data.vm.creation_job_id')

echo "Job ID: $JOB_ID"

# Wait for completion
proxmox-ai job wait "$JOB_ID"

# Verify deployment
proxmox-ai vm show "$VM_NAME"

echo "Deployment completed successfully"
EOF

chmod +x deploy_vm.sh

# 2. Test deployment script
./deploy_vm.sh "scripted-vm-XX" "ubuntu-22.04-secure" 2 4096

# 3. Create monitoring script
cat << 'EOF' > monitor_vms.sh
#!/bin/bash

# Get all VMs and their status
proxmox-ai vm list --format json | \
  jq -r '.data.vms[] | "\(.name): \(.status) - CPU: \(.cpu_usage)% Memory: \(.memory_usage)%"'
EOF

chmod +x monitor_vms.sh

# 4. Run monitoring script
./monitor_vms.sh
```

## Module 7: Troubleshooting and Best Practices (20 minutes)

### 7.1 Common Issues and Solutions (10 minutes)

**Troubleshooting Checklist**
```bash
# System health check
proxmox-ai health check

# Connectivity test
proxmox-ai connectivity test

# Resource availability
proxmox-ai resources check

# Permission verification
proxmox-ai auth verify
```

**Common Issues:**

1. **VM Creation Failures**
   ```bash
   # Check resource availability
   proxmox-ai resources check
   
   # Verify template exists
   proxmox-ai template list
   
   # Check job logs
   proxmox-ai job logs <job-id>
   ```

2. **Network Connectivity Issues**
   ```bash
   # Test network configuration
   proxmox-ai network test workshop-vm-XX
   
   # Check firewall rules
   proxmox-ai vm firewall list workshop-vm-XX
   
   # Verify VLAN configuration
   proxmox-ai network show vlan-200
   ```

3. **Performance Problems**
   ```bash
   # Check resource usage
   proxmox-ai vm metrics workshop-vm-XX
   
   # Run performance analysis
   proxmox-ai vm analyze workshop-vm-XX --performance
   
   # Apply optimization recommendations
   proxmox-ai vm optimize workshop-vm-XX
   ```

### 7.2 Best Practices Review (10 minutes)

**Security Best Practices**
- Always enable disk encryption for sensitive workloads
- Use SSH keys instead of passwords
- Implement proper firewall rules
- Regular security scans and updates
- Monitor security events

**Operational Best Practices**
- Use descriptive names and tags
- Implement backup strategies
- Monitor resource usage
- Document configurations
- Test disaster recovery procedures

**Development Best Practices**
- Use infrastructure as code
- Implement CI/CD pipelines
- Version control configurations
- Automated testing
- Proper error handling

## Workshop Wrap-up and Next Steps (15 minutes)

### 7.3 Workshop Review

**Key Concepts Learned**
- Proxmox AI Infrastructure Assistant installation and configuration
- VM lifecycle management
- Security implementation and monitoring
- AI-assisted operations
- Monitoring and alerting
- API and CI/CD integration

**Hands-on Skills Developed**
- CLI command proficiency
- Security hardening techniques
- AI-powered troubleshooting
- Automation script creation
- Best practices implementation

### 7.4 Next Steps and Resources

**Continuing Education**
- Advanced security workshop
- API development training
- DevOps integration course
- AI automation masterclass

**Resources for Further Learning**
- **Documentation**: https://docs.proxmox-ai.internal/
- **Community Forum**: https://community.proxmox-ai.internal/
- **GitHub Examples**: https://github.com/proxmox-ai/examples
- **Video Tutorials**: https://training.proxmox-ai.internal/videos

**Certification Path**
- Proxmox AI Certified Operator (PACO)
- Proxmox AI Security Specialist (PASS)
- Proxmox AI Solutions Architect (PASA)

### 7.5 Workshop Cleanup

**Clean Up Resources**
```bash
# Stop and remove workshop VMs
proxmox-ai vm stop workshop-vm-XX
proxmox-ai vm delete workshop-vm-XX --confirm

# Remove created backups (optional)
proxmox-ai backup list --vm workshop-vm-XX
proxmox-ai backup delete <backup-id> --confirm

# Revoke workshop API tokens
proxmox-ai auth token list
proxmox-ai auth token revoke <token-id>
```

## Workshop Evaluation

**Feedback Form**
Please complete the workshop evaluation form:
- Content relevance and quality
- Instructor effectiveness
- Hands-on exercise difficulty
- Workshop pace and timing
- Overall satisfaction
- Suggestions for improvement

**Contact Information**
- **Workshop Instructor**: instructor@proxmox-ai.internal
- **Technical Support**: workshop-support@proxmox-ai.internal
- **Training Team**: training@proxmox-ai.internal

## Appendix: Quick Reference

### Essential Commands Cheat Sheet

```bash
# System Status
proxmox-ai status
proxmox-ai health check
proxmox-ai resources

# VM Management
proxmox-ai vm list
proxmox-ai vm create --name <name> --template <template>
proxmox-ai vm start <vm-name>
proxmox-ai vm stop <vm-name>
proxmox-ai vm show <vm-name>

# Security
proxmox-ai security scan <vm-name>
proxmox-ai vm firewall enable <vm-name>
proxmox-ai vm ssh-key add <vm-name> --key-file <key>

# Monitoring
proxmox-ai monitor vm <vm-name>
proxmox-ai backup create <vm-name>
proxmox-ai alert create --vm <vm-name>

# AI Operations
proxmox-ai ai create "<natural language request>"
proxmox-ai ai diagnose <vm-name> "<issue description>"
proxmox-ai ai optimize <vm-name>

# Jobs and Status
proxmox-ai job list
proxmox-ai job status <job-id>
proxmox-ai job wait <job-id>
```

### Configuration Files

**VM Configuration Template**
```yaml
# vm-config.yaml
name: example-vm
template: ubuntu-22.04-secure
configuration:
  cpu_cores: 4
  memory_mb: 8192
  storage_gb: 100
security:
  encrypt_disk: true
  enable_firewall: true
  ssh_keys:
    - ~/.ssh/id_ed25519.pub
network:
  vlan_id: 100
  static_ip: 192.168.1.100
backup:
  enabled: true
  schedule: daily
  retention_days: 30
tags:
  - production
  - web-server
```

---

**Workshop Materials**
- **Duration**: 4 hours
- **Format**: Interactive hands-on training
- **Materials**: Provided lab environment, documentation, examples
- **Certificate**: Completion certificate available

**Classification**: Training Materials - Internal Use
**Last Updated**: 2025-07-29
**Review Schedule**: Quarterly
**Approved By**: Training Team Lead
**Document Version**: 1.0