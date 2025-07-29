# Security Incident Response Runbook

## Overview

This runbook provides step-by-step procedures for responding to security incidents in the Proxmox AI Infrastructure Assistant environment. All procedures follow enterprise security standards and include escalation paths.

## Incident Classification

### Severity Levels

#### Critical (P0) - Immediate Response Required
- **Definition**: Active security breach, data exfiltration, or system compromise
- **Response Time**: Immediate (within 15 minutes)
- **Examples**: 
  - Unauthorized access to Proxmox host (192.168.1.50)
  - Root credential compromise
  - Data encryption/ransomware detected
  - VM escape or hypervisor compromise

#### High (P1) - Urgent Response Required
- **Definition**: Significant security vulnerability or attempted breach
- **Response Time**: Within 1 hour
- **Examples**:
  - Failed authentication attempts exceeding threshold
  - Suspicious network traffic patterns
  - Security tool alerts indicating potential compromise
  - Unauthorized configuration changes

#### Medium (P2) - Prompt Response Required
- **Definition**: Security policy violation or potential vulnerability
- **Response Time**: Within 4 hours
- **Examples**:
  - Policy violations in VM configurations
  - Outdated security patches detected
  - Non-compliant security configurations
  - Suspicious user behavior patterns

#### Low (P3) - Standard Response
- **Definition**: Minor security concerns or informational alerts
- **Response Time**: Within 24 hours
- **Examples**:
  - Security tool maintenance alerts
  - Routine security scan findings
  - Documentation discrepancies

## Immediate Response Procedures

### Step 1: Detection and Initial Assessment (0-15 minutes)

#### 1.1 Incident Detection
- **Automated Alerts**: Monitor security tool alerts and automated detection systems
- **Manual Detection**: User reports, system anomalies, performance issues
- **Documentation**: Record detection time, source, and initial observations

#### 1.2 Initial Triage
```bash
# Quick system status check
ssh -i ~/.ssh/proxmox_key -p 2849 root@192.168.1.50 "systemctl status proxmox-ve"

# Check for active connections
netstat -tulpn | grep :8006
ss -tulpn | grep :22

# Review recent authentication logs
journalctl -u ssh -n 50 --no-pager
tail -f /var/log/auth.log
```

#### 1.3 Severity Assessment
- Evaluate potential impact on confidentiality, integrity, and availability
- Determine if incident involves credential compromise
- Assess network exposure and potential lateral movement
- Document initial severity classification

### Step 2: Containment (15-30 minutes)

#### 2.1 Network Isolation (If Required)
```bash
# Emergency network isolation - Proxmox host
iptables -A INPUT -j DROP
iptables -A OUTPUT -j DROP
iptables -A FORWARD -j DROP

# Allow only SSH for emergency access
iptables -I INPUT -p tcp --dport 2849 -j ACCEPT
iptables -I OUTPUT -p tcp --sport 2849 -j ACCEPT
```

#### 2.2 VM Isolation Procedures
```bash
# Stop specific VM if compromised
qm stop <vmid>

# Isolate VM network interface
qm set <vmid> -net0 model=virtio,bridge=vmbr_isolated

# Take VM snapshot for forensics before any changes
qm snapshot <vmid> incident_$(date +%Y%m%d_%H%M%S)
```

#### 2.3 Access Control Lockdown
```bash
# Disable suspect user accounts (if applicable)
usermod -L suspicious_user

# Force SSH key regeneration if compromise suspected
rm /root/.ssh/authorized_keys.backup
cp /root/.ssh/authorized_keys /root/.ssh/authorized_keys.backup
> /root/.ssh/authorized_keys

# Restart SSH service with new configuration
systemctl restart ssh
```

### Step 3: Evidence Preservation (30-60 minutes)

#### 3.1 System State Capture
```bash
# Capture system state
ps aux > /tmp/incident_processes_$(date +%Y%m%d_%H%M%S).txt
netstat -tulpn > /tmp/incident_network_$(date +%Y%m%d_%H%M%S).txt
lsof > /tmp/incident_files_$(date +%Y%m%d_%H%M%S).txt

# Memory dump (if system compromise suspected)
dd if=/dev/mem of=/tmp/memory_dump_$(date +%Y%m%d_%H%M%S).img bs=1M

# Disk forensic image
dd if=/dev/sda of=/external/disk_image_$(date +%Y%m%d_%H%M%S).img bs=4M status=progress
```

#### 3.2 Log Collection
```bash
# Collect security-relevant logs
journalctl --since "2 hours ago" > /tmp/system_logs_$(date +%Y%m%d_%H%M%S).log
grep -i "authentication\|security\|error\|fail" /var/log/* > /tmp/security_events_$(date +%Y%m%d_%H%M%S).log

# Proxmox-specific logs
cp /var/log/pve/* /tmp/proxmox_logs_$(date +%Y%m%d_%H%M%S)/
```

#### 3.3 Configuration Backup
```bash
# Backup current configurations
cp -r /etc/ /tmp/etc_backup_$(date +%Y%m%d_%H%M%S)/
vzdump --all --compress gzip --storage backup-storage

# Export VM configurations
qm config <vmid> > /tmp/vm_config_$(date +%Y%m%d_%H%M%S).conf
```

## Investigation Procedures

### Forensic Analysis Checklist

#### Network Analysis
- [ ] Review firewall logs for unauthorized access attempts
- [ ] Analyze network traffic patterns and anomalies
- [ ] Check for data exfiltration indicators
- [ ] Verify network segmentation integrity

#### System Analysis
- [ ] Review authentication logs and failed login attempts
- [ ] Check for unauthorized processes or services
- [ ] Analyze file system changes and modifications
- [ ] Verify system integrity and patch levels

#### Application Analysis
- [ ] Review Proxmox web interface access logs
- [ ] Check API usage patterns and authentication
- [ ] Analyze VM creation, modification, and deletion logs
- [ ] Verify configuration management integrity

## Recovery Procedures

### System Recovery Steps

#### 1. Threat Elimination
```bash
# Remove malicious processes (if identified)
kill -9 <malicious_pid>

# Remove unauthorized files
rm -rf /path/to/malicious/files

# Update and patch systems
apt update && apt upgrade -y
```

#### 2. System Restoration
```bash
# Restore from clean backup (if compromise confirmed)
qmrestore /backup/clean_backup.vma.gz <vmid>

# Restore configuration files
cp /backup/etc_clean/* /etc/

# Regenerate SSH keys
ssh-keygen -f /etc/ssh/ssh_host_rsa_key -N '' -t rsa
ssh-keygen -f /etc/ssh/ssh_host_ecdsa_key -N '' -t ecdsa
ssh-keygen -f /etc/ssh/ssh_host_ed25519_key -N '' -t ed25519
```

#### 3. Security Hardening
```bash
# Update all passwords and keys
passwd root

# Implement additional security measures
fail2ban-client restart
ufw enable

# Update security configurations
systemctl restart ssh
systemctl restart pve-proxy
```

## Communication Procedures

### Internal Communication

#### Immediate Notification (P0/P1 Incidents)
- **Security Team**: Immediate notification via secure channel
- **Management**: Within 30 minutes for P0, 2 hours for P1
- **Development Team**: As required for technical response

#### Status Updates
- **Frequency**: Every 30 minutes for P0, hourly for P1, daily for P2/P3
- **Format**: Structured status report including timeline, actions taken, next steps
- **Distribution**: Security team, affected stakeholders, management

### External Communication

#### Regulatory Requirements
- **Data Breach**: Follow applicable data protection regulations
- **Timeline**: Report within required timeframes (typically 72 hours)
- **Content**: Include nature of incident, data affected, remediation steps

#### Customer/User Communication
- **Timing**: After initial containment and impact assessment
- **Content**: Transparent communication about impact and remediation
- **Channel**: Official communication channels with security team approval

## Post-Incident Activities

### Documentation Requirements
- [ ] Complete incident timeline with all actions taken
- [ ] Root cause analysis with contributing factors
- [ ] Impact assessment including affected systems and data
- [ ] Lessons learned and improvement recommendations

### Follow-up Actions
- [ ] Implement security improvements identified during investigation
- [ ] Update security policies and procedures based on lessons learned
- [ ] Conduct post-incident security assessment
- [ ] Schedule follow-up security training if required

### Metrics and Reporting
- [ ] Document response times and effectiveness metrics
- [ ] Update incident response procedures based on experience
- [ ] Report to management with recommendations for security investment
- [ ] Schedule review of incident response capabilities

## Emergency Contacts

### Primary Response Team
- **Incident Commander**: [Primary Contact]
- **Security Lead**: [Security Contact]
- **Technical Lead**: [Technical Contact]
- **Management Escalation**: [Management Contact]

### External Resources
- **Legal Counsel**: [Legal Contact]
- **Regulatory Authority**: [Regulatory Contact]
- **Forensic Services**: [Forensic Contact]
- **Public Relations**: [PR Contact]

## Tools and Resources

### Security Tools
- **SIEM System**: Centralized log analysis and correlation
- **Forensic Tools**: Digital forensics and incident analysis
- **Network Monitoring**: Traffic analysis and intrusion detection
- **Vulnerability Scanner**: Security assessment and compliance checking

### Documentation Resources
- Incident Response Plan (this document)
- Security Policies and Procedures
- Network Architecture Diagrams
- System Configuration Documentation
- Business Continuity Plan

---

**Classification**: Confidential - Security Sensitive
**Last Updated**: 2025-07-29
**Review Schedule**: Quarterly
**Approved By**: Security Team Lead
**Document Version**: 1.0