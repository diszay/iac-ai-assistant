# Credential Management Security Runbook

## Overview

This runbook provides comprehensive procedures for secure credential management in the Proxmox AI Infrastructure Assistant environment. All procedures follow zero-trust security principles and enterprise-grade credential protection standards.

## Critical Security Note

**Root Password**: `[PROXMOX_ROOT_PASSWORD]` (192.168.1.50)
- **Security Status**: HIGH RISK - Requires immediate secure handling
- **Access Control**: Restricted to authorized personnel only
- **Rotation Schedule**: Every 90 days or immediately upon suspected compromise
- **Documentation**: All usage must be logged and audited

## Credential Classification

### Tier 1 - Critical Credentials
- **Root Access**: Proxmox host root password and SSH keys
- **API Keys**: Proxmox API tokens and Claude AI API keys
- **Encryption Keys**: LUKS disk encryption keys and TLS certificates
- **Protection Level**: Hardware security modules or encrypted storage required

### Tier 2 - Administrative Credentials
- **Service Accounts**: Application service account credentials
- **Database Access**: VM database authentication credentials
- **Backup Systems**: Backup storage and recovery credentials
- **Protection Level**: Encrypted storage with access logging required

### Tier 3 - Standard Credentials
- **User Accounts**: Standard user authentication credentials
- **Monitoring**: System monitoring and alerting credentials
- **Development**: Non-production development environment credentials
- **Protection Level**: Standard encrypted storage acceptable

## Secure Credential Storage

### Environment Variables Method
```bash
# Create secure environment file
sudo mkdir -p /etc/proxmox-ai/
sudo touch /etc/proxmox-ai/credentials.env
sudo chmod 600 /etc/proxmox-ai/credentials.env
sudo chown root:root /etc/proxmox-ai/credentials.env

# Example credential storage format
cat << 'EOF' | sudo tee /etc/proxmox-ai/credentials.env
# Proxmox AI Infrastructure Assistant - Secure Credentials
# WARNING: This file contains sensitive credentials - Handle with extreme care

# Proxmox Host Access
PROXMOX_HOST=192.168.1.50
PROXMOX_ROOT_PASSWORD=[PROXMOX_ROOT_PASSWORD]
PROXMOX_SSH_PORT=2849

# API Authentication
PROXMOX_API_USER=root@pam
PROXMOX_API_TOKEN=your_api_token_here
CLAUDE_API_KEY=your_claude_api_key_here

# Encryption and Security
LUKS_PASSPHRASE=your_luks_passphrase_here
TLS_CERT_PATH=/etc/ssl/certs/proxmox-ai.crt
TLS_KEY_PATH=/etc/ssl/private/proxmox-ai.key

# Backup and Recovery
BACKUP_ENCRYPTION_KEY=your_backup_encryption_key_here
RECOVERY_PASSPHRASE=your_recovery_passphrase_here
EOF
```

### SSH Key Management
```bash
# Generate dedicated SSH key for Proxmox access
ssh-keygen -t ed25519 -f ~/.ssh/proxmox_ai_key -C "proxmox-ai-assistant"
chmod 600 ~/.ssh/proxmox_ai_key
chmod 644 ~/.ssh/proxmox_ai_key.pub

# Copy public key to Proxmox host
ssh-copy-id -i ~/.ssh/proxmox_ai_key.pub -p 2849 root@192.168.1.50

# Test SSH key authentication
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50 "echo 'SSH key authentication successful'"
```

### Secure Configuration Loading
```python
# Python example for secure credential loading
import os
from pathlib import Path
from cryptography.fernet import Fernet
import json

class SecureCredentialManager:
    def __init__(self, credentials_file="/etc/proxmox-ai/credentials.env"):
        self.credentials_file = Path(credentials_file)
        self.credentials = {}
        self.load_credentials()
    
    def load_credentials(self):
        """Load credentials from secure environment file"""
        if not self.credentials_file.exists():
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
        
        # Verify file permissions
        stat_info = self.credentials_file.stat()
        if stat_info.st_mode & 0o077:
            raise PermissionError("Credentials file has insecure permissions")
        
        # Load environment variables
        with open(self.credentials_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    self.credentials[key] = value
    
    def get_credential(self, key):
        """Retrieve credential with audit logging"""
        if key not in self.credentials:
            raise KeyError(f"Credential not found: {key}")
        
        # Log credential access (without exposing value)
        self.log_access(key)
        return self.credentials[key]
    
    def log_access(self, credential_key):
        """Log credential access for security auditing"""
        import logging
        logging.info(f"Credential accessed: {credential_key} by {os.getuser()}")
```

## SSH Key Rotation Procedures

### Monthly SSH Key Rotation
```bash
#!/bin/bash
# SSH Key Rotation Script

set -euo pipefail

# Configuration
PROXMOX_HOST="192.168.1.50"
PROXMOX_PORT="2849"
OLD_KEY="$HOME/.ssh/proxmox_ai_key"
NEW_KEY="$HOME/.ssh/proxmox_ai_key_new"
BACKUP_DIR="$HOME/.ssh/backup/$(date +%Y%m%d_%H%M%S)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting SSH key rotation procedure..."

# Step 1: Backup current keys
cp "$OLD_KEY" "$BACKUP_DIR/"
cp "$OLD_KEY.pub" "$BACKUP_DIR/"
echo "Current keys backed up to: $BACKUP_DIR"

# Step 2: Generate new SSH key pair
ssh-keygen -t ed25519 -f "$NEW_KEY" -C "proxmox-ai-$(date +%Y%m%d)" -N ""
echo "New SSH key pair generated"

# Step 3: Add new public key to Proxmox host
ssh -i "$OLD_KEY" -p "$PROXMOX_PORT" root@"$PROXMOX_HOST" \
    "echo '$(cat $NEW_KEY.pub)' >> ~/.ssh/authorized_keys"
echo "New public key added to Proxmox host"

# Step 4: Test new key authentication
if ssh -i "$NEW_KEY" -p "$PROXMOX_PORT" root@"$PROXMOX_HOST" "echo 'New key test successful'"; then
    echo "New key authentication verified"
else
    echo "ERROR: New key authentication failed"
    exit 1
fi

# Step 5: Remove old key from authorized_keys
ssh -i "$NEW_KEY" -p "$PROXMOX_PORT" root@"$PROXMOX_HOST" \
    "grep -v '$(cat $OLD_KEY.pub | cut -d' ' -f2)' ~/.ssh/authorized_keys > ~/.ssh/authorized_keys.tmp && mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys"
echo "Old public key removed from Proxmox host"

# Step 6: Replace old key with new key
mv "$NEW_KEY" "$OLD_KEY"
mv "$NEW_KEY.pub" "$OLD_KEY.pub"
chmod 600 "$OLD_KEY"
chmod 644 "$OLD_KEY.pub"
echo "SSH key rotation completed successfully"

# Step 7: Update application configurations
echo "Remember to update application configurations with new key path"
echo "Backup location: $BACKUP_DIR"
```

## Password Management Procedures

### Root Password Rotation
```bash
#!/bin/bash
# Root Password Rotation Script

set -euo pipefail

# Generate new secure password
NEW_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
echo "Generated new secure password"

# Connect to Proxmox host and change password
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50 << EOF
echo "root:$NEW_PASSWORD" | chpasswd
echo "Root password updated successfully"
EOF

# Update credentials file
sudo sed -i "s/PROXMOX_ROOT_PASSWORD=.*/PROXMOX_ROOT_PASSWORD=$NEW_PASSWORD/" /etc/proxmox-ai/credentials.env
echo "Credentials file updated"

# Log password change
logger "Proxmox root password rotated - $(date)"

echo "Password rotation completed successfully"
echo "New password: $NEW_PASSWORD"
echo "IMPORTANT: Update all systems that use this credential"
```

### API Token Management  
```bash
# Generate new Proxmox API token
pveum user token add root@pam proxmox-ai-$(date +%Y%m%d) --privsep=0

# Update application configuration
sudo sed -i "s/PROXMOX_API_TOKEN=.*/PROXMOX_API_TOKEN=$NEW_TOKEN/" /etc/proxmox-ai/credentials.env

# Test API token functionality
curl -k -H "Authorization: PVEAPIToken=root@pam!proxmox-ai-$(date +%Y%m%d)=$NEW_TOKEN" \
     https://192.168.1.50:8006/api2/json/version
```

## Encryption Key Management

### LUKS Disk Encryption
```bash
# Generate new LUKS passphrase
NEW_LUKS_PASSPHRASE=$(openssl rand -base64 32)

# Add new passphrase to LUKS header
echo -n "$NEW_LUKS_PASSPHRASE" | cryptsetup luksAddKey /dev/vda3 --key-file=-

# Test new passphrase
echo -n "$NEW_LUKS_PASSPHRASE" | cryptsetup luksOpen --test-passphrase /dev/vda3 --key-file=-

# Remove old passphrase (after confirming new one works)
echo -n "$OLD_LUKS_PASSPHRASE" | cryptsetup luksRemoveKey /dev/vda3 --key-file=-

# Update credentials file
sudo sed -i "s/LUKS_PASSPHRASE=.*/LUKS_PASSPHRASE=$NEW_LUKS_PASSPHRASE/" /etc/proxmox-ai/credentials.env
```

### TLS Certificate Management
```bash
# Generate new TLS certificate and key
openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/proxmox-ai-new.key \
            -out /etc/ssl/certs/proxmox-ai-new.crt -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=proxmox-ai"

# Update certificate permissions
chmod 600 /etc/ssl/private/proxmox-ai-new.key
chmod 644 /etc/ssl/certs/proxmox-ai-new.crt

# Test certificate validity
openssl x509 -in /etc/ssl/certs/proxmox-ai-new.crt -text -noout

# Replace old certificates
mv /etc/ssl/private/proxmox-ai.key /etc/ssl/private/proxmox-ai.key.old
mv /etc/ssl/certs/proxmox-ai.crt /etc/ssl/certs/proxmox-ai.crt.old
mv /etc/ssl/private/proxmox-ai-new.key /etc/ssl/private/proxmox-ai.key
mv /etc/ssl/certs/proxmox-ai-new.crt /etc/ssl/certs/proxmox-ai.crt

# Restart services to use new certificates
systemctl restart nginx
systemctl restart pve-proxy
```

## Audit and Monitoring

### Credential Access Logging
```bash
# Setup credential access monitoring
cat << 'EOF' > /etc/rsyslog.d/50-credential-access.conf
# Log credential access attempts
:msg, contains, "Credential accessed" /var/log/credential-access.log
& stop
EOF

systemctl restart rsyslog
```

### Access Monitoring Script
```bash
#!/bin/bash
# Monitor credential file access

inotifywait -m /etc/proxmox-ai/credentials.env -e access,modify,open | while read path action file; do
    echo "$(date): Credential file accessed - Action: $action by $(who)" >> /var/log/credential-access.log
    logger "SECURITY: Credential file accessed - $action"
done
```

### Regular Security Audits
```bash
#!/bin/bash
# Credential Security Audit Script

echo "=== Proxmox AI Credential Security Audit ==="
echo "Date: $(date)"
echo

# Check file permissions
echo "1. Checking credential file permissions..."
ls -la /etc/proxmox-ai/credentials.env
if [ "$(stat -c %a /etc/proxmox-ai/credentials.env)" != "600" ]; then
    echo "WARNING: Insecure file permissions detected"
fi

# Check SSH key permissions
echo "2. Checking SSH key permissions..."
ls -la ~/.ssh/proxmox_ai_key*
if [ "$(stat -c %a ~/.ssh/proxmox_ai_key)" != "600" ]; then
    echo "WARNING: Insecure SSH key permissions detected"
fi

# Check for password age
echo "3. Checking password age..."
LAST_CHANGE=$(stat -c %Y /etc/proxmox-ai/credentials.env)
CURRENT_TIME=$(date +%s)
AGE_DAYS=$(( (CURRENT_TIME - LAST_CHANGE) / 86400 ))
echo "Credentials last updated: $AGE_DAYS days ago"
if [ $AGE_DAYS -gt 90 ]; then
    echo "WARNING: Credentials older than 90 days - rotation recommended"
fi

# Check for unauthorized access attempts
echo "4. Checking for unauthorized access attempts..."
grep "authentication failure" /var/log/auth.log | tail -5

echo "=== Audit Complete ==="
```

## Emergency Procedures

### Credential Compromise Response
```bash
#!/bin/bash
# Emergency credential compromise response

echo "EMERGENCY: Credential compromise detected"
echo "Initiating immediate security lockdown..."

# 1. Change root password immediately
NEW_EMERGENCY_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50 "echo 'root:$NEW_EMERGENCY_PASSWORD' | chpasswd"

# 2. Disable compromised SSH keys
ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@192.168.1.50 "mv ~/.ssh/authorized_keys ~/.ssh/authorized_keys.disabled"

# 3. Generate new SSH keys
ssh-keygen -t ed25519 -f ~/.ssh/proxmox_ai_emergency_key -N ""

# 4. Add emergency key via password authentication
ssh-copy-id -o PreferredAuthentications=password -p 2849 root@192.168.1.50

# 5. Regenerate API tokens
pveum user token delete root@pam proxmox-ai
NEW_TOKEN=$(pveum user token add root@pam proxmox-ai-emergency --privsep=0)

# 6. Update credentials file
sudo sed -i "s/PROXMOX_ROOT_PASSWORD=.*/PROXMOX_ROOT_PASSWORD=$NEW_EMERGENCY_PASSWORD/" /etc/proxmox-ai/credentials.env
sudo sed -i "s/PROXMOX_API_TOKEN=.*/PROXMOX_API_TOKEN=$NEW_TOKEN/" /etc/proxmox-ai/credentials.env

# 7. Log incident
logger "SECURITY INCIDENT: Emergency credential rotation completed - $(date)"

echo "Emergency credential rotation completed"
echo "New root password: $NEW_EMERGENCY_PASSWORD"
echo "IMPORTANT: Follow full incident response procedures"
```

## Compliance and Documentation

### Credential Inventory
- [ ] Root passwords - Last rotated: ___________
- [ ] SSH keys - Last rotated: ___________
- [ ] API tokens - Last rotated: ___________
- [ ] Encryption keys - Last rotated: ___________
- [ ] TLS certificates - Expiration: ___________

### Access Logging Requirements
- All credential access must be logged with timestamp and user
- Failed authentication attempts must trigger alerts
- Credential file modifications must be monitored and logged
- Regular audit reports must be generated and reviewed

### Rotation Schedule
- **Root passwords**: Every 90 days or upon suspected compromise
- **SSH keys**: Every 30 days for production systems
- **API tokens**: Every 180 days or upon policy change
- **Encryption keys**: Annually or upon security incident
- **TLS certificates**: Before expiration (typically annually)

---

**Classification**: Confidential - Security Critical
**Last Updated**: 2025-07-29
**Review Schedule**: Monthly
**Approved By**: Security Team Lead
**Document Version**: 1.0

**SECURITY WARNING**: This document contains sensitive security procedures. Access is restricted to authorized personnel only. Unauthorized disclosure may result in security vulnerabilities.