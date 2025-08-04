# 🔧 Troubleshooting Guide - Common Issues & Solutions

## 🎯 Quick Problem Solver

**🚨 Having issues?** Choose your situation:

- [🚫 Can't connect to Proxmox](#connection-issues) - Network, SSH, or API problems
- [🤖 AI not responding](#ai-issues) - Ollama or model problems  
- [🐍 Python errors](#python-issues) - Installation or dependency problems
- [🔐 Authentication failed](#authentication-issues) - Login or permission problems
- [💾 Out of space](#storage-issues) - Disk space or storage problems
- [🐌 Running slowly](#performance-issues) - Speed or resource problems
- [❓ Something else](#other-issues) - General problems and solutions

---

## 🔍 Quick Diagnosis

Run this first to identify your issue:

```bash
# Comprehensive system check
proxmox-ai doctor

# This checks:
# ✅ Python environment
# ✅ Ollama AI service  
# ✅ Proxmox connectivity
# ✅ Configuration validity
# ✅ Available resources
# ✅ Security settings
```

---

## 🚫 Connection Issues

### Problem: Can't Connect to Proxmox

#### 🔍 Quick Check
```bash
# Test basic connectivity
ping -c 3 YOUR_PROXMOX_HOST

# Test SSH connection
ssh root@YOUR_PROXMOX_HOST

# Test Proxmox web interface
curl -k https://YOUR_PROXMOX_HOST:8006/api2/json/version
```

#### ✅ Solution Steps

**Step 1: Verify Network Connectivity**
```bash
# Check if Proxmox host is reachable
ping -c 5 192.168.1.50

# If ping fails, check:
# - Is Proxmox host powered on?
# - Is the IP address correct?
# - Are you on the same network?
```

**Step 2: Test SSH Access**
```bash
# Test SSH with verbose output
ssh -v root@192.168.1.50

# Common fixes:
# - Check if SSH service is running: systemctl status ssh
# - Verify SSH port (default 22): ssh -p 2849 root@192.168.1.50
# - Check firewall rules: sudo ufw status
```

**Step 3: Test API Access**
```bash
# Test Proxmox API
curl -k https://192.168.1.50:8006/api2/json/version

# If this fails:
# - Check if Proxmox web interface is accessible
# - Verify port 8006 is open
# - Check SSL certificate issues
```

**Step 4: Fix Configuration**
```bash
# Update Proxmox host settings
proxmox-ai config set proxmox.host "192.168.1.50"
proxmox-ai config set proxmox.port "8006"

# Test the connection
proxmox-ai vm list
```

---

## 🤖 AI Issues

### Problem: AI Not Responding or Slow

#### 🔍 Quick Check
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Check available models
ollama list

# Test AI response
proxmox-ai ask "hello"
```

#### ✅ Solution Steps

**Step 1: Start Ollama Service**
```bash
# Start Ollama (if not running)
ollama serve &

# Check if it's running
ps aux | grep ollama
curl http://localhost:11434/api/tags
```

**Step 2: Download AI Model**
```bash
# Check what models you have
ollama list

# If no models, download one based on your RAM:
# 4-6GB RAM:
ollama pull llama3.2:3b-instruct-q4_0

# 6-12GB RAM:
ollama pull llama3.1:8b-instruct-q4_0

# 12GB+ RAM:
ollama pull llama3.1:8b-instruct-q8_0
```

**Step 3: Configure AI Model**
```bash
# Set the model in configuration
proxmox-ai config set ai.model "llama3.1:8b-instruct-q4_0"

# Test AI functionality
proxmox-ai ai-status
proxmox-ai ask "test response"
```

**Step 4: Memory Issues**
```bash
# Check available memory
free -h

# Switch to smaller model if needed
proxmox-ai ai switch-model llama3.2:3b-instruct-q4_0

# Or reduce memory usage
proxmox-ai config set ai.max_memory_gb 4
```

---

## 🐍 Python Issues

### Problem: Python Installation or Import Errors

#### 🔍 Quick Check
```bash
# Check Python version
python3.12 --version || python3 --version

# Check if proxmox-ai is installed
proxmox-ai --version

# Check for import errors
python3 -c "import typer, rich, proxmoxer"
```

#### ✅ Solution Steps

**Step 1: Install Python 3.12+**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-pip

# macOS
brew install python@3.12

# Windows
winget install Python.Python.3.12

# Verify installation
python3.12 --version
```

**Step 2: Create Virtual Environment**
```bash
# Create clean virtual environment
python3.12 -m venv proxmox-ai-env

# Activate it
source proxmox-ai-env/bin/activate  # Linux/macOS
# proxmox-ai-env\Scripts\activate   # Windows

# Verify activation
which python  # Should point to venv
```

**Step 3: Install Dependencies**
```bash
# Ensure you're in the project directory
cd ~/projects/iac-ai-assistant

# Install with pip
pip install --upgrade pip
pip install -e .

# Or install specific dependencies
pip install -r requirements.txt

# Verify installation
proxmox-ai --version
```

**Step 4: Fix Import Errors**
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reinstall problematic packages
pip install --force-reinstall typer rich proxmoxer

# Test imports
python3 -c "import src.proxmox_ai.cli.main"
```

---

## 🔐 Authentication Issues

### Problem: Can't Login to Proxmox

#### 🔍 Quick Check
```bash
# Test SSH authentication
ssh root@YOUR_PROXMOX_HOST

# Test API authentication
proxmox-ai vm list

# Check stored credentials
proxmox-ai config get proxmox.user
proxmox-ai config get proxmox.host
```

#### ✅ Solution Steps

**Step 1: Fix SSH Authentication**
```bash
# Generate new SSH key if needed
ssh-keygen -t ed25519 -f ~/.ssh/proxmox_ai_key

# Copy key to Proxmox host
ssh-copy-id -i ~/.ssh/proxmox_ai_key.pub root@192.168.1.50

# Test SSH key authentication
ssh -i ~/.ssh/proxmox_ai_key root@192.168.1.50

# Update configuration
proxmox-ai config set proxmox.ssh_key ~/.ssh/proxmox_ai_key
```

**Step 2: Fix API Authentication**
```bash
# Method 1: Use API Token (Recommended)
# Create token in Proxmox web interface:
# Datacenter → API Tokens → Add

# Set token in configuration
proxmox-ai config set proxmox.api_token "PVEAPIToken=root@pam!tokenname=your-token-uuid"

# Method 2: Use Password (Less Secure)
proxmox-ai config set proxmox.password "your-proxmox-password"
```

**Step 3: Test Authentication**
```bash
# Test connection
proxmox-ai vm list

# If still failing, check logs
proxmox-ai logs --error

# Reset authentication
proxmox-ai config init --reset-auth
```

---

## 💾 Storage Issues

### Problem: Out of Disk Space

#### 🔍 Quick Check
```bash
# Check disk space
df -h

# Check AI model sizes
ollama list

# Check application cache
du -sh ~/.cache/proxmox-ai/
```

#### ✅ Solution Steps

**Step 1: Free Up Space**
```bash
# Remove unused AI models
ollama list
ollama rm unused-model-name

# Clear application cache
rm -rf ~/.cache/proxmox-ai/

# Clear system logs
sudo journalctl --vacuum-time=7d
```

**Step 2: Use Smaller AI Model**
```bash
# Switch to smaller model
ollama pull llama3.2:3b-instruct-q4_0
proxmox-ai ai switch-model llama3.2:3b-instruct-q4_0

# Remove larger models
ollama rm llama3.1:70b-instruct-q4_0
```

**Step 3: Clean Up System**
```bash
# Remove old packages (Ubuntu/Debian)
sudo apt autoremove
sudo apt autoclean

# Clear temporary files
sudo rm -rf /tmp/*
rm -rf ~/.cache/*

# Check space again
df -h
```

---

## 🐌 Performance Issues

### Problem: System Running Slowly

#### 🔍 Quick Check
```bash
# Check system resources
htop  # or top
free -h
iostat -x 1 5

# Check AI model performance
proxmox-ai ai stats
```

#### ✅ Solution Steps

**Step 1: Optimize AI Model**
```bash
# Check hardware recommendations
proxmox-ai hardware-info

# Use optimal model for your hardware
proxmox-ai ai optimize

# Enable caching
proxmox-ai config set ai.cache_enabled true
```

**Step 2: Reduce Memory Usage**
```bash
# Switch to smaller model
proxmox-ai ai switch-model llama3.2:3b-instruct-q4_0

# Limit memory usage
proxmox-ai config set ai.max_memory_gb 4

# Close other applications
# Stop unnecessary services
```

**Step 3: Optimize Network**
```bash
# Check network latency
ping -c 10 YOUR_PROXMOX_HOST

# Use local network addresses
proxmox-ai config set proxmox.host "192.168.1.50"  # Not public IP

# Optimize SSH settings
echo "ServerAliveInterval 60" >> ~/.ssh/config
```

---

## ❓ Other Issues

### Problem: Command Not Found

#### 🔍 Quick Check
```bash
# Check if proxmox-ai is installed
which proxmox-ai
proxmox-ai --version

# Check if in correct directory
pwd
ls -la
```

#### ✅ Solution
```bash
# If not installed, install it
cd ~/projects/iac-ai-assistant
pip install -e .

# Or add to PATH
export PATH=$PATH:$PWD/src/proxmox_ai/cli
echo 'export PATH=$PATH:~/projects/iac-ai-assistant/src/proxmox_ai/cli' >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

### Problem: Configuration Not Saved

#### 🔍 Quick Check
```bash
# Check configuration
proxmox-ai config list

# Check config file location
ls -la ~/.config/proxmox-ai/
```

#### ✅ Solution
```bash
# Create config directory
mkdir -p ~/.config/proxmox-ai/

# Initialize configuration
proxmox-ai config init

# Set permissions
chmod 700 ~/.config/proxmox-ai/
chmod 600 ~/.config/proxmox-ai/config.yaml
```

### Problem: Terraform/Ansible Not Working

#### 🔍 Quick Check
```bash
# Check if tools are installed
terraform --version
ansible --version

# Test generated code
proxmox-ai generate terraform "test vm" --output test.tf
terraform validate test.tf
```

#### ✅ Solution
```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Ansible
pip install ansible

# Verify installation
terraform --version
ansible --version
```

---

## 🆘 Emergency Recovery

### Complete System Reset

If everything is broken, start fresh:

```bash
# 1. Backup important configurations
cp ~/.config/proxmox-ai/config.yaml ~/config-backup.yaml

# 2. Remove everything
rm -rf ~/projects/iac-ai-assistant
rm -rf ~/.config/proxmox-ai/
rm -rf ~/.cache/proxmox-ai/

# 3. Kill Ollama processes
pkill ollama

# 4. Fresh installation
curl -fsSL https://raw.githubusercontent.com/diszay/iac-ai-assistant/main/scripts/express-install.sh | bash

# 5. Restore configuration
cp ~/config-backup.yaml ~/.config/proxmox-ai/config.yaml
```

### Get Help from AI

When stuck, ask the AI for help:

```bash
# Start interactive troubleshooting
proxmox-ai chat

# Then describe your problem:
"I'm having trouble with [describe your issue]. Can you help me troubleshoot?"
"My AI is not responding, what should I check?"
"I can't connect to Proxmox, what are the common causes?"
```

---

## 💡 Prevention Tips

### Regular Maintenance

```bash
# Weekly system check
proxmox-ai doctor

# Monthly updates
proxmox-ai update
ollama list  # Check for model updates

# Quarterly cleanup
proxmox-ai cleanup
ollama rm unused-models
```

### Monitoring Setup

```bash
# Set up health monitoring
echo "0 */6 * * * /usr/local/bin/proxmox-ai status >> /var/log/proxmox-ai-health.log 2>&1" | crontab -

# Monitor disk space
echo "0 0 * * * df -h | mail -s 'Disk Space Report' your-email@domain.com" | crontab -

# Monitor AI performance
proxmox-ai config set ai.performance_monitoring true
```

### Backup Strategy

```bash
# Backup configuration
mkdir -p ~/backups/proxmox-ai/
cp -r ~/.config/proxmox-ai/ ~/backups/proxmox-ai/config-$(date +%Y%m%d)/

# Backup generated configurations
tar -czf ~/backups/proxmox-ai/generated-configs-$(date +%Y%m%d).tar.gz ~/projects/iac-ai-assistant/generated/

# Backup AI models (optional - they can be re-downloaded)
# ollama list > ~/backups/proxmox-ai/models-list-$(date +%Y%m%d).txt
```

---

## 🔗 Getting More Help

### Built-in Help System

```bash
# General help
proxmox-ai --help

# Command-specific help
proxmox-ai generate --help
proxmox-ai vm --help
proxmox-ai config --help

# Interactive help
proxmox-ai chat
# Ask: "Help me troubleshoot [your issue]"
```

### Documentation Resources

- **Requirements**: `/requirements.md` - System requirements and setup
- **Getting Started**: `/GETTING_STARTED.md` - Step-by-step setup guide
- **Quick Reference**: `/docs/QUICK_REFERENCE.md` - Common commands and patterns
- **Command Cheatsheet**: `/docs/COMMAND_CHEATSHEET.md` - All available commands
- **User Guides**: `/docs/user-guides/` - Skill-level specific guides
- **Architecture**: `/docs/architecture/` - Technical documentation

### Community Support

```bash
# Check for known issues
proxmox-ai ask "Is there a known issue with [your problem]?"

# Report bugs (include this information)
proxmox-ai doctor > bug-report.txt
proxmox-ai config list >> bug-report.txt
proxmox-ai --version >> bug-report.txt
uname -a >> bug-report.txt
```

### Emergency Contacts

- **Critical Issues**: Use `proxmox-ai doctor` to generate diagnostic report
- **Security Issues**: Follow `/SECURITY.md` reporting procedures  
- **Documentation Issues**: Suggest improvements via GitHub issues

---

## 📊 Common Error Messages

### "Connection refused"
- **Cause**: Proxmox host not reachable or service not running
- **Fix**: Check network, verify Proxmox is running, test with `ping` and `curl`

### "Authentication failed"  
- **Cause**: Wrong credentials or expired tokens
- **Fix**: Verify credentials, regenerate API tokens, test SSH keys

### "Model not found"
- **Cause**: AI model not downloaded or wrong model name
- **Fix**: `ollama list`, `ollama pull model-name`, update config

### "Permission denied"
- **Cause**: File permissions or user access issues
- **Fix**: Check file permissions, verify user has proper access

### "Out of memory"
- **Cause**: AI model too large for available RAM
- **Fix**: Switch to smaller model, close other applications

### "Module not found"
- **Cause**: Python dependency missing or virtual environment not activated
- **Fix**: Activate venv, `pip install -e .`, check requirements

---

**🎯 Remember**: When in doubt, run `proxmox-ai doctor` first and ask the AI for help with `proxmox-ai chat`!

**Document Version**: 1.0  
**Last Updated**: 2025-07-30  
**Troubleshooting Guide for**: Proxmox AI Infrastructure Assistant

#### Symptoms
- Connection refused when attempting SSH to Proxmox host
- Permission denied despite correct credentials
- Timeout errors during SSH connection attempts

#### Root Causes
- Incorrect SSH key permissions
- SSH key not properly deployed to Proxmox host
- SSH service configuration issues
- Network connectivity problems

#### Solution Steps

##### 1. Verify SSH Key Permissions
```bash
# Check SSH key file permissions
ls -la ~/.ssh/proxmox_ai_key*

# Expected output:
# -rw------- 1 user user 411 Jul 29 10:00 /home/user/.ssh/proxmox_ai_key
# -rw-r--r-- 1 user user  99 Jul 29 10:00 /home/user/.ssh/proxmox_ai_key.pub

# Fix permissions if incorrect
chmod 600 ~/.ssh/proxmox_ai_key
chmod 644 ~/.ssh/proxmox_ai_key.pub
```

##### 2. Verify SSH Key Deployment
```bash
# Test SSH connectivity with verbose output
ssh -v -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50

# Check if public key exists on Proxmox host (using password authentication)
ssh -o PreferredAuthentications=password -p 2849 root@192.168.1.50 "cat ~/.ssh/authorized_keys"

# Redeploy SSH key if missing
ssh-copy-id -i ~/.ssh/proxmox_ai_key.pub -p 2849 root@192.168.1.50
```

##### 3. Verify SSH Service Configuration
```bash
# Connect to Proxmox host and check SSH configuration
ssh -p 2849 root@192.168.1.50

# Check SSH daemon status
systemctl status ssh

# Verify SSH configuration
grep -E "^(Port|PermitRootLogin|PubkeyAuthentication|PasswordAuthentication)" /etc/ssh/sshd_config

# Expected configuration:
# Port 2849
# PermitRootLogin yes
# PubkeyAuthentication yes
# PasswordAuthentication no
```

##### 4. Network Connectivity Verification
```bash
# Test network connectivity
ping -c 4 192.168.1.50

# Test port accessibility
telnet 192.168.1.50 2849
# Or using nc
nc -zv 192.168.1.50 2849

# Check local firewall rules
sudo iptables -L -n | grep 2849
```

#### Prevention
- Implement automated SSH key rotation procedures
- Monitor SSH service health with automated alerts
- Regular connectivity testing through health checks
- Backup SSH keys in secure encrypted storage

---

### Issue: Proxmox API Authentication Failures

#### Symptoms
- HTTP 401 Unauthorized errors when making API calls
- Invalid token or expired token messages
- Permission denied for specific API operations

#### Root Causes
- Expired or invalid API tokens
- Incorrect token format or encoding
- Insufficient permissions for API operations
- Network connectivity to API endpoint

#### Solution Steps

##### 1. Verify API Token Format
```bash
# Check current token configuration
source /etc/proxmox-ai/credentials.env
echo "API Token: $PROXMOX_API_TOKEN"

# Token should be in format: PVEAPIToken=root@pam!token-name=uuid
# Example: PVEAPIToken=root@pam!proxmox-ai=12345678-1234-1234-1234-123456789abc
```

##### 2. Test API Connectivity
```bash
# Test basic API connectivity
curl -k -s -H "Authorization: $PROXMOX_API_TOKEN" \
     https://192.168.1.50:8006/api2/json/version

# Expected response should include version information
# If error, check token validity and permissions
```

##### 3. Regenerate API Token
```bash
# Connect to Proxmox host
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50

# Delete existing token
pveum user token delete root@pam proxmox-ai-assistant

# Create new token
pveum user token add root@pam proxmox-ai-assistant --privsep=0

# Update credentials file with new token
sudo nano /etc/proxmox-ai/credentials.env
```

##### 4. Verify API Permissions
```bash
# Check user permissions
pveum user list
pveum user permissions root@pam

# Check token permissions
pveum user token permissions root@pam proxmox-ai-assistant

# Grant additional permissions if needed
pveum aclmod / -user root@pam -role Administrator
```

#### Prevention
- Implement API token rotation schedule (every 180 days)
- Monitor API call success rates and error patterns
- Automated token validation in health checks
- Backup and secure storage of API tokens

---

## Network and Connectivity Issues

### Issue: Network Timeouts and Connection Drops

#### Symptoms
- Intermittent connection failures to Proxmox host
- Slow API response times
- SSH sessions dropping unexpectedly
- VNC console connectivity issues

#### Root Causes
- Network infrastructure problems
- Firewall blocking connections
- DNS resolution issues
- Bandwidth limitations or congestion

#### Solution Steps

##### 1. Network Diagnostics
```bash
# Test basic connectivity
ping -c 10 192.168.1.50

# Check packet loss and latency
mtr --report --report-cycles 10 192.168.1.50

# Test specific ports
nmap -p 22,2849,8006,5900-5999 192.168.1.50

# DNS resolution test
nslookup 192.168.1.50
dig -x 192.168.1.50
```

##### 2. Firewall Analysis
```bash
# Check local firewall rules
sudo iptables -L -n -v
sudo ufw status verbose

# Test from Proxmox host perspective
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50
iptables -L -n -v
fail2ban-client status

# Check for blocked IPs
fail2ban-client status sshd
```

##### 3. Performance Optimization
```bash
# Optimize SSH keep-alive settings
cat >> ~/.ssh/config << 'EOF'
Host proxmox-ai
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
EOF

# Test connection stability
while true; do ssh proxmox-ai "date" || break; sleep 30; done
```

##### 4. Router/Network Infrastructure Check
```bash
# Check router configuration and logs
# Access router admin interface and verify:
# - Port forwarding rules for SSH (2849) and Proxmox Web (8006)
# - Firewall rules allowing traffic
# - DHCP reservation for Proxmox host (192.168.1.50)
# - QoS settings that might affect performance
```

#### Prevention
- Implement network monitoring and alerting
- Regular network infrastructure health checks
- Bandwidth monitoring and capacity planning
- Redundant network paths where possible

---

## Storage and Backup Issues

### Issue: Disk Space and Storage Problems

#### Symptoms
- VM creation failures due to insufficient space
- Backup failures with space-related errors
- Performance degradation due to full disks
- LUKS encryption issues with storage

#### Root Causes
- Insufficient disk space on Proxmox host
- Full backup storage locations
- Corrupted storage pools or filesystems
- Failed disk drives or storage hardware

#### Solution Steps

##### 1. Check Disk Space
```bash
# Connect to Proxmox host
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50

# Check overall disk usage
df -h

# Check Proxmox storage status
pvesm status

# Check specific storage pools
zpool status  # For ZFS
lvs           # For LVM
```

##### 2. Clean Up Storage
```bash
# Remove old backups
find /var/lib/vz/dump -name "*.vma.gz" -mtime +30 -delete

# Clean up old ISO files
ls -la /var/lib/vz/template/iso/
rm /var/lib/vz/template/iso/old-image.iso

# Remove unused VM disks
pvesm list local --content images
# Identify and remove unused disk images

# Clean system logs
journalctl --vacuum-time=7d
```

##### 3. Expand Storage
```bash
# Check available space for expansion
fdisk -l
parted -l

# Extend LVM volume (example)
lvextend -l +100%FREE /dev/pve/data
resize2fs /dev/pve/data

# Add new storage device
fdisk /dev/sdb  # Create partitions
pvcreate /dev/sdb1
vgextend pve /dev/sdb1
```

##### 4. Backup Storage Maintenance
```bash
# Check backup storage
ls -la /backup/
df -h /backup/

# Test backup creation
vzdump --all --compress gzip --storage backup-storage

# Verify backup integrity
zcat /backup/dump.vma.gz | vma verify -
```

#### Prevention
- Implement automated disk space monitoring with alerts
- Regular cleanup schedules for old backups and logs
- Capacity planning and growth monitoring
- RAID configuration for redundancy and performance

---

## Application and Service Issues

### Issue: Proxmox AI Application Errors

#### Symptoms
- Command execution failures
- Import or module errors in Python
- Configuration loading problems
- Unexpected application crashes

#### Root Causes
- Missing Python dependencies
- Configuration file corruption
- Environment variable issues
- Application code bugs or logic errors

#### Solution Steps

##### 1. Environment Verification
```bash
# Check Python environment
python --version
which python

# Activate virtual environment
source ~/projects/iac-ai-assistant/venv/bin/activate

# Verify dependencies
pip list
pip check

# Test import of key modules
python -c "import typer, rich, proxmoxer; print('All imports successful')"
```

##### 2. Configuration Diagnosis
```bash
# Check credentials file
ls -la /etc/proxmox-ai/credentials.env
sudo cat /etc/proxmox-ai/credentials.env

# Verify environment loading
source /etc/proxmox-ai/credentials.env
env | grep PROXMOX

# Test configuration loading in Python
python -c "
import os
from pathlib import Path
creds_file = Path('/etc/proxmox-ai/credentials.env')
print(f'Credentials file exists: {creds_file.exists()}')
print(f'Permissions: {oct(creds_file.stat().st_mode)[-3:]}')
"
```

##### 3. Application Testing
```bash
# Test basic application functionality
proxmox-ai --help
proxmox-ai version
proxmox-ai status

# Run with debug output
python -v ~/projects/iac-ai-assistant/src/cli/main.py status

# Check application logs
tail -f /var/log/proxmox-ai/application.log
journalctl -f -u proxmox-ai
```

##### 4. Dependency Resolution
```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt

# Install missing system dependencies
sudo apt update
sudo apt install python3-dev build-essential libssl-dev

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

#### Prevention
- Pin dependency versions in requirements.txt
- Implement application health monitoring
- Regular testing of application functionality
- Automated dependency vulnerability scanning

---

## VM Management Issues

### Issue: VM Creation and Management Failures

#### Symptoms
- VM creation timeouts or failures
- Unable to start or stop VMs
- Network connectivity issues with VMs
- VM console access problems

#### Root Causes
- Insufficient resources on Proxmox host
- Network configuration problems
- Storage allocation issues
- VM configuration errors

#### Solution Steps

##### 1. Resource Verification
```bash
# Check host resources
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50

# Check CPU and memory usage
htop
free -h

# Check running VMs
qm list
pct list

# Check resource allocation
pvesh get /nodes/$(hostname)/resources
```

##### 2. VM Diagnostics
```bash
# Check specific VM status
qm status <vmid>
qm config <vmid>

# Check VM logs
tail -f /var/log/pve/tasks/active

# Test VM operations
qm start <vmid>
qm stop <vmid>
qm reset <vmid>
```

##### 3. Network Troubleshooting
```bash
# Check network bridges
ip link show
brctl show

# Check VM network configuration
qm config <vmid> | grep net

# Test network connectivity
ping <vm_ip>
ssh <vm_ip>

# Check firewall rules
pve-firewall status
iptables -L -v -n
```

##### 4. Storage Investigation
```bash
# Check VM disk allocation
qm config <vmid> | grep -E "(ide|scsi|virtio)"

# Check disk usage
pvesm status
du -sh /var/lib/vz/images/<vmid>/

# Test disk operations
qm resize <vmid> scsi0 +10G
```

#### Prevention
- Implement resource monitoring and alerting
- Regular VM health checks and maintenance
- Automated backup and snapshot procedures
- Documentation of VM configurations and procedures

---

## Security and Compliance Issues

### Issue: Security Policy Violations

#### Symptoms
- Failed security scans or audits
- Non-compliant configurations detected
- Unauthorized access attempts
- Certificate expiration warnings

#### Root Causes
- Outdated security configurations
- Missing security patches
- Weak authentication configurations
- Expired certificates or keys

#### Solution Steps

##### 1. Security Assessment
```bash
# Run security scan
nmap -sS -O 192.168.1.50
nmap --script vuln 192.168.1.50

# Check for security updates
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50
apt update
apt list --upgradable
```

##### 2. Configuration Hardening
```bash
# Review SSH configuration
grep -E "^(PermitRootLogin|PasswordAuthentication|Protocol)" /etc/ssh/sshd_config

# Check firewall status
ufw status verbose
iptables -L -n

# Review user accounts and permissions
cat /etc/passwd
last -n 20
```

##### 3. Certificate Management
```bash
# Check certificate expiration
openssl x509 -in /etc/ssl/certs/proxmox-ai.crt -noout -dates

# Verify certificate chain
openssl verify /etc/ssl/certs/proxmox-ai.crt

# Generate new certificate if needed
openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/proxmox-ai.key \
            -out /etc/ssl/certs/proxmox-ai.crt -days 365 -nodes
```

##### 4. Compliance Validation
```bash
# Run compliance checks
# Check CIS benchmarks
cis-cat --report --format txt

# Verify security policies
./tests/security/security_test.sh

# Generate compliance report
./scripts/generate_compliance_report.sh
```

#### Prevention
- Automated security scanning and patch management
- Regular compliance audits and assessments
- Security configuration management with version control
- Continuous monitoring of security events and alerts

---

## Performance and Optimization Issues

### Issue: Slow Performance and Response Times

#### Symptoms
- Slow API response times
- VM operations taking longer than expected
- High resource utilization on Proxmox host
- Network latency issues

#### Root Causes
- Resource contention and overallocation
- Inefficient storage configuration
- Network bottlenecks
- Suboptimal VM configurations

#### Solution Steps

##### 1. Performance Analysis
```bash
# System performance monitoring
htop
iotop
iftop

# Check system load
uptime
vmstat 5 5

# Analyze disk I/O
iostat -x 5 5
```

##### 2. Resource Optimization
```bash
# Check VM resource allocation
for vmid in $(qm list | grep running | awk '{print $1}'); do
    echo "VM $vmid:"
    qm config $vmid | grep -E "(memory|cores|sockets)"
done

# Optimize storage
# Enable compression for ZFS
zfs set compression=lz4 rpool

# Adjust VM settings
qm set <vmid> --balloon 1024
qm set <vmid> --cpu cputype=host
```

##### 3. Network Optimization
```bash
# Check network utilization
iftop -i vmbr0

# Optimize network settings
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
sysctl -p

# Test network performance
iperf3 -s  # On one system
iperf3 -c 192.168.1.50  # On another system
```

##### 4. Application Optimization
```bash
# Profile application performance
python -m cProfile src/cli/main.py status

# Optimize API calls
# Implement connection pooling and caching
# Use asynchronous operations where possible

# Monitor application metrics
ps aux | grep python
netstat -tulpn | grep python
```

#### Prevention
- Regular performance monitoring and capacity planning
- Automated performance testing and benchmarking
- Resource usage trending and alerting
- Performance optimization as part of regular maintenance

---

## Emergency Recovery Procedures

### Issue: System Compromise or Security Incident

#### Immediate Actions
1. **Isolate the system** - Disconnect from network if necessary
2. **Preserve evidence** - Take snapshots and memory dumps
3. **Activate incident response team** - Follow escalation procedures
4. **Document everything** - Maintain detailed incident log

#### Recovery Steps
```bash
# Emergency system isolation
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP

# Preserve system state
ps aux > /tmp/processes_$(date +%Y%m%d_%H%M%S).txt
netstat -tulpn > /tmp/network_$(date +%Y%m%d_%H%M%S).txt

# Create forensic images
dd if=/dev/sda of=/external/forensic_image_$(date +%Y%m%d_%H%M%S).img

# Follow incident response procedures in:
# /docs/security/runbooks/incident-response.md
```

### Issue: Complete System Failure

#### Recovery from Backup
```bash
# Boot from rescue media
# Mount backup storage
mount /dev/backup_device /mnt/backup

# Restore system from backup
tar -xzf /mnt/backup/system_backup.tar.gz -C /

# Restore VM data
qmrestore /mnt/backup/vm_backup.vma.gz <vmid>

# Verify system integrity
fsck /dev/sda1
qm config <vmid>
```

---

## Support and Escalation

### Internal Support Contacts
- **Technical Issues**: Documentation Lead & Knowledge Manager
- **Security Issues**: Security Team Lead
- **Infrastructure Issues**: System Administrator
- **Emergency**: Follow incident response procedures

### External Resources
- **Proxmox VE Documentation**: https://pve.proxmox.com/wiki/
- **Community Forums**: https://forum.proxmox.com/
- **Professional Support**: Proxmox Server Solutions GmbH

### Documentation Resources
- **Architecture Guide**: `/docs/architecture/overview.md`
- **Security Runbooks**: `/docs/security/runbooks/`
- **Installation Guide**: `/docs/operations/installation.md`
- **API Documentation**: `/docs/api/`

---

**Classification**: Internal Use - Troubleshooting Sensitive
**Last Updated**: 2025-07-29
**Review Schedule**: Monthly
**Approved By**: Technical Team Lead
**Document Version**: 1.0