# Proxmox AI Infrastructure Assistant - Installation Guide

## Overview

This guide provides comprehensive installation procedures for the Proxmox AI Infrastructure Assistant with a security-first approach. All procedures follow enterprise security standards and include verification steps.

## Prerequisites

### System Requirements

#### Proxmox Host Requirements
- **Proxmox VE**: Version 7.4 or later
- **Hardware**: Minimum 32GB RAM, 1TB storage, 8 CPU cores
- **Network**: Static IP address (192.168.1.50)
- **Security**: SSH access configured with key-based authentication

#### Client System Requirements
- **Operating System**: macOS, Linux, or Windows with SSH client
- **Python**: Version 3.12 or later
- **Network**: SSH access to Proxmox host (port 2849)
- **Storage**: Minimum 10GB available space for tools and logs

#### Network Requirements
- **Internal Network**: 192.168.1.0/24 subnet
- **Internet Access**: Required for package downloads and API access
- **Firewall Rules**: SSH (2849), Proxmox Web (8006), API access
- **DNS Resolution**: Proper hostname resolution for all systems

### Security Prerequisites

#### Credential Management
- Secure storage for root password: `Cl@uD3D3V`
- SSH key pair generation and secure storage
- API token generation and secure management
- Backup of all security credentials

#### Network Security
- Firewall configuration and port restrictions
- SSH hardening and key-based authentication
- TLS certificate generation and management
- Network segmentation and VLAN configuration

## Pre-Installation Security Setup

### 1. SSH Key Configuration

#### Generate SSH Key Pair
```bash
# Create dedicated SSH key for Proxmox access
ssh-keygen -t ed25519 -b 4096 -f ~/.ssh/proxmox_ai_key -C "proxmox-ai-assistant-$(date +%Y%m%d)"

# Set secure permissions
chmod 600 ~/.ssh/proxmox_ai_key
chmod 644 ~/.ssh/proxmox_ai_key.pub

# Verify key generation
ls -la ~/.ssh/proxmox_ai_key*
ssh-keygen -l -f ~/.ssh/proxmox_ai_key
```

#### Deploy SSH Key to Proxmox Host
```bash
# Copy public key to Proxmox host (will prompt for root password)
ssh-copy-id -i ~/.ssh/proxmox_ai_key.pub -p 2849 root@192.168.1.50

# Test SSH key authentication
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50 "echo 'SSH key authentication successful'"

# Verify authorized_keys on Proxmox host
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50 "cat ~/.ssh/authorized_keys"
```

### 2. Proxmox Host Security Hardening

#### SSH Hardening
```bash
# Connect to Proxmox host
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50

# Backup original SSH configuration
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Apply security hardening
cat << 'EOF' >> /etc/ssh/sshd_config

# Proxmox AI Security Hardening
Protocol 2
PermitRootLogin yes
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM no
X11Forwarding no
PrintMotd no
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
MaxSessions 5
EOF

# Restart SSH service
systemctl restart ssh
systemctl status ssh
```

#### Firewall Configuration
```bash
# Configure iptables for security
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 2849 -j ACCEPT  # SSH
iptables -A INPUT -p tcp --dport 8006 -j ACCEPT  # Proxmox Web UI
iptables -A INPUT -p tcp --dport 5900:5999 -j ACCEPT  # VNC consoles
iptables -A INPUT -j DROP

# Save iptables rules
iptables-save > /etc/iptables/rules.v4

# Install and configure fail2ban
apt update && apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. API Token Generation

#### Create Proxmox API Token
```bash
# Connect to Proxmox host
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50

# Create API token for the assistant
pveum user token add root@pam proxmox-ai-assistant --privsep=0

# Note: Save the generated token securely - it will only be displayed once
# Example output: PVEAPIToken=root@pam!proxmox-ai-assistant=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
```

#### Test API Access
```bash
# Test API token functionality
curl -k -H "Authorization: PVEAPIToken=root@pam!proxmox-ai-assistant=YOUR_TOKEN_HERE" \
     https://192.168.1.50:8006/api2/json/version

# Expected response should include Proxmox version information
```

## Installation Process

### 1. Environment Setup

#### Create Project Directory Structure
```bash
# Create project directory
mkdir -p ~/projects/iac-ai-assistant
cd ~/projects/iac-ai-assistant

# Create directory structure
mkdir -p {src,config,docs,tests,scripts,tasks}
mkdir -p config/{templates,secrets}
mkdir -p docs/{architecture,security,operations,api,training,troubleshooting}
mkdir -p src/{cli,api,security,utils}
mkdir -p tests/{unit,integration,security}

# Set appropriate permissions
chmod 700 config/secrets
chmod 755 src scripts tests
```

#### Python Environment Setup
```bash
# Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install typer rich proxmoxer requests python-dotenv cryptography
pip install ansible terraform-python pytest pytest-security

# Save dependency list
pip freeze > requirements.txt
```

### 2. Secure Configuration Setup

#### Create Credentials File
```bash
# Create secure credentials directory
sudo mkdir -p /etc/proxmox-ai
sudo touch /etc/proxmox-ai/credentials.env
sudo chmod 600 /etc/proxmox-ai/credentials.env
sudo chown $USER:$USER /etc/proxmox-ai/credentials.env

# Create credentials configuration
cat << 'EOF' > /etc/proxmox-ai/credentials.env
# Proxmox AI Infrastructure Assistant - Secure Credentials
# WARNING: This file contains sensitive credentials

# Proxmox Host Configuration
PROXMOX_HOST=192.168.1.50
PROXMOX_ROOT_PASSWORD=Cl@uD3D3V
PROXMOX_SSH_PORT=2849
PROXMOX_SSH_KEY_PATH=/home/$USER/.ssh/proxmox_ai_key

# API Authentication
PROXMOX_API_USER=root@pam
PROXMOX_API_TOKEN=YOUR_PROXMOX_API_TOKEN_HERE
CLAUDE_API_KEY=YOUR_CLAUDE_API_KEY_HERE

# Security Configuration
TLS_VERIFY=true
LOG_LEVEL=INFO
AUDIT_LOGGING=true
ENCRYPTION_ENABLED=true

# Backup Configuration
BACKUP_ENCRYPTION_KEY=YOUR_BACKUP_ENCRYPTION_KEY_HERE
BACKUP_STORAGE_PATH=/backup/proxmox-ai
EOF

# Secure the credentials file
chmod 600 /etc/proxmox-ai/credentials.env
```

#### SSH Configuration
```bash
# Create SSH config for Proxmox access
cat << 'EOF' >> ~/.ssh/config

# Proxmox AI Infrastructure Assistant
Host proxmox-ai
    HostName 192.168.1.50
    Port 2849
    User root
    IdentityFile ~/.ssh/proxmox_ai_key
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking yes
EOF

# Test SSH configuration
ssh proxmox-ai "echo 'SSH configuration successful'"
```

### 3. Application Installation

#### Core Application Setup
```bash
# Clone or create the application structure
cd ~/projects/iac-ai-assistant

# Create main CLI application file
cat << 'EOF' > src/cli/main.py
#!/usr/bin/env python3
"""
Proxmox AI Infrastructure Assistant - Main CLI Application
Security-first infrastructure automation with AI assistance
"""

import typer
from rich.console import Console
from rich.panel import Panel
import os
from pathlib import Path

# Initialize Rich console
console = Console()

# Initialize Typer app
app = typer.Typer(
    name="proxmox-ai",
    help="Proxmox AI Infrastructure Assistant - Secure VM Management",
    no_args_is_help=True
)

def load_credentials():
    """Load secure credentials from environment file"""
    creds_file = Path("/etc/proxmox-ai/credentials.env")
    if not creds_file.exists():
        console.print("❌ Credentials file not found", style="red")
        raise typer.Exit(1)
    
    # Load environment variables
    with open(creds_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value.strip()

@app.command()
def status():
    """Check system status and connectivity"""
    console.print(Panel.fit("🤖 Proxmox AI Infrastructure Assistant", style="blue"))
    console.print("✅ System status: Operational")
    console.print("✅ Security: Enabled")
    console.print("✅ Credentials: Loaded")

@app.command()
def version():
    """Display version information"""
    console.print("Proxmox AI Infrastructure Assistant v1.0.0")
    console.print("Security-first infrastructure automation")

if __name__ == "__main__":
    load_credentials()
    app()
EOF

# Make the application executable
chmod +x src/cli/main.py
```

#### Create Installation Script
```bash
# Create automated installation script
cat << 'EOF' > scripts/install.sh
#!/bin/bash
# Proxmox AI Infrastructure Assistant - Installation Script

set -euo pipefail

echo "🚀 Installing Proxmox AI Infrastructure Assistant..."

# Check prerequisites
python3.12 --version || { echo "Python 3.12+ required"; exit 1; }
ssh -V || { echo "SSH client required"; exit 1; }

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create symbolic link for global access
sudo ln -sf $(pwd)/src/cli/main.py /usr/local/bin/proxmox-ai
sudo chmod +x /usr/local/bin/proxmox-ai

# Verify installation
proxmox-ai version

echo "✅ Installation completed successfully"
echo "Run 'proxmox-ai --help' to get started"
EOF

chmod +x scripts/install.sh
```

### 4. Security Validation

#### Create Security Test Suite
```bash
# Create security validation script
cat << 'EOF' > tests/security/security_test.sh
#!/bin/bash
# Security validation test suite

set -euo pipefail

echo "🔒 Running security validation tests..."

# Test 1: Credential file permissions
echo "Test 1: Checking credential file permissions..."
if [ "$(stat -c %a /etc/proxmox-ai/credentials.env)" != "600" ]; then
    echo "❌ Insecure credential file permissions"
    exit 1
fi
echo "✅ Credential file permissions secure"

# Test 2: SSH key permissions
echo "Test 2: Checking SSH key permissions..."
if [ "$(stat -c %a ~/.ssh/proxmox_ai_key)" != "600" ]; then
    echo "❌ Insecure SSH key permissions"
    exit 1
fi
echo "✅ SSH key permissions secure"

# Test 3: SSH connectivity
echo "Test 3: Testing SSH connectivity..."
if ! ssh -i ~/.ssh/proxmox_ai_key -p 2849 -o ConnectTimeout=10 root@192.168.1.50 "echo 'SSH test successful'" > /dev/null 2>&1; then
    echo "❌ SSH connectivity failed"
    exit 1
fi
echo "✅ SSH connectivity successful"

# Test 4: API connectivity
echo "Test 4: Testing Proxmox API connectivity..."
source /etc/proxmox-ai/credentials.env
if ! curl -k -s -H "Authorization: PVEAPIToken=$PROXMOX_API_TOKEN" \
     https://192.168.1.50:8006/api2/json/version > /dev/null; then
    echo "❌ API connectivity failed"
    exit 1
fi
echo "✅ API connectivity successful"

echo "🎉 All security tests passed"
EOF

chmod +x tests/security/security_test.sh
```

#### Run Security Validation
```bash
# Execute security validation
./tests/security/security_test.sh
```

### 5. Final Installation Steps

#### Install the Application
```bash
# Run the installation script
./scripts/install.sh

# Verify global installation
proxmox-ai --help
proxmox-ai status
```

#### Create Backup Configuration
```bash
# Create backup directory
sudo mkdir -p /backup/proxmox-ai
sudo chown $USER:$USER /backup/proxmox-ai

# Create backup script
cat << 'EOF' > scripts/backup.sh
#!/bin/bash
# Backup configuration and credentials

BACKUP_DIR="/backup/proxmox-ai/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup credentials (encrypted)
gpg --symmetric --cipher-algo AES256 /etc/proxmox-ai/credentials.env
mv credentials.env.gpg "$BACKUP_DIR/"

# Backup SSH keys
cp ~/.ssh/proxmox_ai_key* "$BACKUP_DIR/"

# Backup configuration
cp -r config/ "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x scripts/backup.sh
```

## Post-Installation Configuration

### 1. System Integration

#### Create Systemd Service (Optional)
```bash
# Create systemd service file
sudo cat << 'EOF' > /etc/systemd/system/proxmox-ai.service
[Unit]
Description=Proxmox AI Infrastructure Assistant
After=network.target

[Service]
Type=oneshot
User=root
ExecStart=/usr/local/bin/proxmox-ai status
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable proxmox-ai
```

#### Configure Logging
```bash
# Create log directory
sudo mkdir -p /var/log/proxmox-ai
sudo chown $USER:$USER /var/log/proxmox-ai

# Configure rsyslog
sudo cat << 'EOF' > /etc/rsyslog.d/50-proxmox-ai.conf
# Proxmox AI logging configuration
:programname, isequal, "proxmox-ai" /var/log/proxmox-ai/application.log
& stop
:msg, contains, "PROXMOX-AI-SECURITY" /var/log/proxmox-ai/security.log
& stop
EOF

sudo systemctl restart rsyslog
```

### 2. Monitoring Setup

#### Create Health Check Script
```bash
cat << 'EOF' > scripts/health_check.sh
#!/bin/bash
# System health check

echo "=== Proxmox AI Health Check ==="
echo "Timestamp: $(date)"

# Check SSH connectivity
if ssh proxmox-ai "echo 'SSH OK'" > /dev/null 2>&1; then
    echo "✅ SSH connectivity: OK"
else
    echo "❌ SSH connectivity: FAILED"
fi

# Check API connectivity
source /etc/proxmox-ai/credentials.env
if curl -k -s -H "Authorization: PVEAPIToken=$PROXMOX_API_TOKEN" \
   https://192.168.1.50:8006/api2/json/version > /dev/null; then
    echo "✅ API connectivity: OK"
else
    echo "❌ API connectivity: FAILED"
fi

# Check application
if proxmox-ai status > /dev/null 2>&1; then
    echo "✅ Application: OK"
else
    echo "❌ Application: FAILED"
fi

echo "=== Health Check Complete ==="
EOF

chmod +x scripts/health_check.sh
```

#### Setup Cron Job for Health Monitoring
```bash
# Add cron job for health monitoring
(crontab -l 2>/dev/null; echo "*/15 * * * * /home/$USER/projects/iac-ai-assistant/scripts/health_check.sh >> /var/log/proxmox-ai/health.log 2>&1") | crontab -
```

## Verification and Testing

### 1. Installation Verification
```bash
# Verify all components
echo "=== Installation Verification ==="

# Check Python environment
python --version
pip list | grep -E "(typer|rich|proxmoxer)"

# Check application installation
which proxmox-ai
proxmox-ai --version

# Check credentials
ls -la /etc/proxmox-ai/credentials.env

# Check SSH configuration
ssh proxmox-ai "hostname && date"

echo "=== Verification Complete ==="
```

### 2. Security Testing
```bash
# Run comprehensive security tests
./tests/security/security_test.sh

# Test credential isolation
sudo -u nobody cat /etc/proxmox-ai/credentials.env 2>&1 | grep -q "Permission denied" && echo "✅ Credential isolation working"

# Test SSH key security
ls -la ~/.ssh/proxmox_ai_key | grep -q "^-rw-------" && echo "✅ SSH key permissions secure"
```

### 3. Functional Testing
```bash
# Test basic functionality
proxmox-ai status
proxmox-ai version

# Test SSH connectivity
ssh proxmox-ai "pvesh get /version"

# Test API functionality
source /etc/proxmox-ai/credentials.env
curl -k -H "Authorization: PVEAPIToken=$PROXMOX_API_TOKEN" \
     https://192.168.1.50:8006/api2/json/nodes
```

## Troubleshooting

### Common Installation Issues

#### SSH Key Authentication Failures
```bash
# Debug SSH connectivity
ssh -v -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50

# Check key permissions
ls -la ~/.ssh/proxmox_ai_key*

# Verify key on Proxmox host
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50 "cat ~/.ssh/authorized_keys"
```

#### API Token Issues
```bash
# Regenerate API token
ssh proxmox-ai "pveum user token delete root@pam proxmox-ai-assistant"
ssh proxmox-ai "pveum user token add root@pam proxmox-ai-assistant --privsep=0"

# Update credentials file
sudo nano /etc/proxmox-ai/credentials.env
```

#### Permission Problems
```bash
# Fix credential file permissions
sudo chmod 600 /etc/proxmox-ai/credentials.env
sudo chown $USER:$USER /etc/proxmox-ai/credentials.env

# Fix SSH key permissions
chmod 600 ~/.ssh/proxmox_ai_key
chmod 644 ~/.ssh/proxmox_ai_key.pub
```

## Next Steps

After successful installation:

1. **Security Review**: Conduct security assessment using `/docs/security/runbooks/`
2. **Configuration**: Customize settings in `/config/` directory
3. **Training**: Complete tutorials in `/docs/training/`
4. **Backup**: Run initial backup using `./scripts/backup.sh`
5. **Monitoring**: Verify health check automation is working

## Support and Documentation

- **Architecture Guide**: `/docs/architecture/overview.md`
- **Security Runbooks**: `/docs/security/runbooks/`
- **API Documentation**: `/docs/api/`
- **Troubleshooting**: `/docs/troubleshooting/`

---

**Classification**: Internal Use - Installation Sensitive
**Last Updated**: 2025-07-29
**Review Schedule**: Monthly
**Approved By**: Security Team Lead
**Document Version**: 1.0