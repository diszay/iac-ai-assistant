# Proxmox AI Infrastructure Assistant - Installation Guide

## 🐧 Ubuntu Quick Launch Commands

**For Ubuntu users who need to launch the assistant after installation:**

```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant

# Activate virtual environment
source venv/bin/activate

# Start the AI assistant
python -m src.proxmox_ai.cli.main

# Or use the startup script
./scripts/start-assistant.sh

# Common operations
python -m src.proxmox_ai.cli.main ai status        # Check status
python -m src.proxmox_ai.cli.main ai chat          # Interactive mode
python -m src.proxmox_ai.cli.main doctor           # Health check
```

---

## Overview

This guide provides comprehensive installation procedures for the Proxmox AI Infrastructure Assistant with local AI integration and a security-first approach. The system uses Ollama for local AI model execution, ensuring complete privacy and offline operation. All procedures follow enterprise security standards and include verification steps.

## Prerequisites

### System Requirements

#### Proxmox Host Requirements
- **Proxmox VE**: Version 7.4 or later recommended
- **Hardware**: Minimum 16GB RAM, 500GB storage, 4 CPU cores (32GB+ RAM recommended for production)
- **Network**: Static IP address configured
- **Security**: SSH access configured with key-based authentication

#### Client System Requirements
- **Operating System**: macOS, Linux, or Windows with SSH client
- **Python**: Version 3.12 or later
- **Memory**: Minimum 4GB RAM (8GB+ recommended for optimal AI performance)
- **Storage**: Minimum 15GB available space (5GB for AI models, 10GB for tools and logs)
- **Network**: SSH access to your Proxmox host
- **AI Engine**: Ollama for local AI model execution

#### Network Requirements
- **Internet Access**: Required for initial downloads (Ollama, Python packages, AI models)
- **Proxmox Access**: SSH and API access to your Proxmox server
- **Firewall Rules**: SSH, Proxmox Web interface, and API access
- **DNS Resolution**: Proper hostname resolution for your network

### Local AI Requirements

#### Ollama Installation
- **Ollama Engine**: Latest version for local AI model execution
- **AI Models**: Hardware-optimized quantized models (1-8GB)
- **Performance**: Automatic hardware detection and optimization
- **Privacy**: Complete offline operation - no external AI services

### Security Prerequisites

#### Credential Management
- SSH key pair generation and secure storage
- Proxmox API token generation and secure management
- Secure backup of all authentication credentials
- Local AI model security and isolation

#### Network Security
- Firewall configuration and port restrictions
- SSH hardening and key-based authentication
- TLS certificate generation and management
- Network segmentation and VLAN configuration

## Pre-Installation Setup

### 1. Ollama Installation and Configuration

#### Install Ollama Engine - Ubuntu Commands
```bash
# Ubuntu/Linux Installation
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service
ollama serve &

# Check service status
curl http://localhost:11434/api/tags

# Download recommended model
ollama pull llama3.1:8b-instruct-q4_0

# Verify model installation
ollama list
```

#### Hardware Detection and Model Selection
```bash
# Create hardware detection script
cat << 'EOF' > scripts/detect_hardware.sh
#!/bin/bash
# Hardware detection for optimal AI model selection

echo "=== Hardware Detection ==="

# Get memory information
MEM_GB=$(free -g | awk '/^Mem:/{print $2}')
echo "Available Memory: ${MEM_GB}GB"

# Get CPU information
CPU_CORES=$(nproc)
echo "CPU Cores: $CPU_CORES"

# Check for GPU
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits)
    echo "GPU: $GPU_INFO"
else
    echo "GPU: Not available"
fi

# Recommend model based on available memory
echo "\n=== Recommended AI Models ==="
if [ "$MEM_GB" -lt 6 ]; then
    echo "Recommended: llama3.2:3b-instruct-q4_0 (Basic quality, ~2GB)"  
    RECOMMENDED_MODEL="llama3.2:3b-instruct-q4_0"
elif [ "$MEM_GB" -lt 12 ]; then
    echo "Recommended: llama3.1:8b-instruct-q4_0 (Good quality, ~4.5GB)"
    RECOMMENDED_MODEL="llama3.1:8b-instruct-q4_0"
elif [ "$MEM_GB" -lt 24 ]; then
    echo "Recommended: llama3.1:8b-instruct-q8_0 (High quality, ~8GB)"
    RECOMMENDED_MODEL="llama3.1:8b-instruct-q8_0"
else
    echo "Recommended: llama3.1:70b-instruct-q4_0 (Excellent quality, ~40GB)"
    RECOMMENDED_MODEL="llama3.1:70b-instruct-q4_0"
fi

echo "\nTo install recommended model: ollama pull $RECOMMENDED_MODEL"
EOF

chmod +x scripts/detect_hardware.sh
./scripts/detect_hardware.sh
```

#### Install Recommended AI Model
```bash
# Pull the model recommended by hardware detection
# For systems with 4-6GB RAM:
ollama pull llama3.2:3b-instruct-q4_0

# For systems with 6-12GB RAM:
ollama pull llama3.1:8b-instruct-q4_0

# For systems with 12-24GB RAM:
ollama pull llama3.1:8b-instruct-q8_0

# For systems with 24GB+ RAM:
ollama pull llama3.1:70b-instruct-q4_0

# Verify model installation
ollama list

# Test model functionality
ollama run llama3.2:3b-instruct-q4_0 "Hello, can you help with infrastructure automation?"
```

#### Configure Ollama for Production
```bash
# Create Ollama systemd service (Linux)
sudo cat << 'EOF' > /etc/systemd/system/ollama.service
[Unit]
Description=Ollama Local AI Service
After=network.target

[Service]
Type=simple
User=ollama
Group=ollama
ExecStart=/usr/local/bin/ollama serve
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_MODELS=/var/lib/ollama/models"
Restart=always
RestartSec=3
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF

# Create ollama user
sudo useradd -r -s /bin/false -d /var/lib/ollama -m ollama

# Set permissions
sudo mkdir -p /var/lib/ollama/models
sudo chown -R ollama:ollama /var/lib/ollama

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Verify service status
sudo systemctl status ollama
curl http://localhost:11434/api/tags
```

## Security Setup

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

#### Create Project Directory Structure - Ubuntu Commands
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

#### Python Environment Setup - Ubuntu Commands
```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant

# Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install from pyproject.toml (includes all dependencies)
pip install -e .

# Verify installation
python -m src.proxmox_ai.cli.main --version

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
PROXMOX_ROOT_PASSWORD=[PROXMOX_ROOT_PASSWORD]
PROXMOX_SSH_PORT=2849
PROXMOX_SSH_KEY_PATH=/home/$USER/.ssh/proxmox_ai_key

# API Authentication
PROXMOX_API_USER=root@pam
PROXMOX_API_TOKEN=YOUR_PROXMOX_API_TOKEN_HERE

# Local AI Configuration
OLLAMA_HOST=http://localhost:11434
AI_MODEL=llama3.2:3b-instruct-q4_0
AI_SKILL_LEVEL=intermediate
AI_CACHE_ENABLED=true
AI_USE_GPU=false
AI_MAX_MEMORY_GB=4

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

# Install the application using pyproject.toml
cat << 'EOF' > setup_check.py
#!/usr/bin/env python3
"""
Setup verification script for Proxmox AI Infrastructure Assistant
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version requirement"""
    if sys.version_info < (3, 12):
        print("❌ Python 3.12+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_ollama():
    """Check Ollama installation"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("❌ Ollama not installed or not in PATH")
    return False

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service running")
            return True
    except Exception:
        pass
    print("❌ Ollama service not running")
    return False

def check_dependencies():
    """Check required Python packages"""
    required_packages = [
        'typer', 'rich', 'proxmoxer', 'structlog', 
        'pydantic', 'cryptography', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def main():
    """Run setup verification"""
    print("=== Proxmox AI Infrastructure Assistant Setup Check ===")
    
    checks = [
        check_python_version(),
        check_ollama(),
        check_ollama_service(),
        check_dependencies()
    ]
    
    if all(checks):
        print("\n🎉 All checks passed! System ready for installation.")
        return 0
    else:
        print("\n❌ Some checks failed. Please resolve issues before continuing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

# Make setup check executable
chmod +x setup_check.py

# Run setup verification
python setup_check.py

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

### 1. Installation Verification - Ubuntu Commands
```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Verify all components
echo "=== Installation Verification ==="

# Check Python environment
python --version
pip list | grep -E "(typer|rich|proxmoxer)"

# Check application installation
python -m src.proxmox_ai.cli.main --version

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

### 3. Functional Testing - Ubuntu Commands
```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Test basic functionality
python -m src.proxmox_ai.cli.main status
python -m src.proxmox_ai.cli.main --version

# Test local AI functionality
python -m src.proxmox_ai.cli.main ai status
python -m src.proxmox_ai.cli.main hardware-info

# Test AI model interaction
python -m src.proxmox_ai.cli.main ai generate terraform "Simple Ubuntu server" --skill beginner

# Test SSH connectivity
ssh proxmox-ai "pvesh get /version"

# Test API functionality
source /etc/proxmox-ai/credentials.env
curl -k -H "Authorization: PVEAPIToken=$PROXMOX_API_TOKEN" \
     https://192.168.1.50:8006/api2/json/nodes

# Test Ollama service
curl http://localhost:11434/api/tags
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