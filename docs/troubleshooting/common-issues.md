# Proxmox AI Infrastructure Assistant - Common Issues & Solutions

## Overview

This document provides solutions to frequently encountered issues in the Proxmox AI Infrastructure Assistant environment. All solutions include security considerations and verification steps.

## Authentication and Access Issues

### Issue: SSH Key Authentication Failures

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