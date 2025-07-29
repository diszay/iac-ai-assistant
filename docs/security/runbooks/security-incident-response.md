# Security Incident Response Procedures - Proxmox AI Infrastructure

**Document Classification:** CONFIDENTIAL - SECURITY PROCEDURES  
**Last Updated:** 2025-07-29  
**Security Authority:** QA Engineer & Security Specialist  
**Approval Status:** APPROVED FOR IMMEDIATE IMPLEMENTATION

---

## 🚨 EMERGENCY CONTACT INFORMATION

### **Critical Security Contacts**
- **Security Incident Commander:** QA Engineer & Security Specialist
- **Primary Response Team:** All Development Agents
- **Infrastructure Manager:** Project Manager & Infrastructure Orchestrator
- **Technical Lead:** Software Engineer & Automation Developer

### **Emergency Response Numbers**
- **Security Hotline:** [To be configured]
- **Infrastructure Emergency:** [To be configured]
- **Management Escalation:** [To be configured]

---

## 🎯 INCIDENT CLASSIFICATION MATRIX

### **Severity Level 1 - CRITICAL**
**Response Time:** Immediate (< 15 minutes)
- Active security breach or system compromise
- Unauthorized access to critical systems
- Data exfiltration in progress
- Complete system outage affecting security controls
- Ransomware or malware infection

### **Severity Level 2 - HIGH**
**Response Time:** 1 Hour
- Suspected unauthorized access
- Security control failures
- Vulnerability exploitation attempts
- Significant configuration drift
- Failed backup or recovery systems

### **Severity Level 3 - MEDIUM**
**Response Time:** 4 Hours
- Policy violations
- Suspicious network activity
- Authentication anomalies
- Non-critical security tool failures
- Compliance violations

### **Severity Level 4 - LOW**
**Response Time:** 24 Hours
- Security awareness issues
- Minor policy violations
- Information requests
- Documentation updates needed

---

## 🚀 IMMEDIATE RESPONSE PROCEDURES (CRITICAL INCIDENTS)

### **Step 1: Initial Response (0-15 minutes)**

#### **IMMEDIATE ACTIONS - DO NOT DELAY**
1. **ALERT THE SECURITY TEAM**
   ```bash
   # Send immediate alert
   echo "SECURITY INCIDENT: [Brief Description]" | mail -s "CRITICAL SECURITY INCIDENT" security-team@organization.com
   ```

2. **ASSESS THE SITUATION**
   - Determine if incident is ongoing
   - Identify affected systems
   - Assess potential data exposure
   - Document initial observations

3. **CONTAIN THE THREAT**
   ```bash
   # If system compromise suspected - ISOLATE IMMEDIATELY
   # Block suspicious IP addresses
   sudo ufw deny from [SUSPICIOUS_IP]
   
   # Disable compromised user accounts
   sudo usermod -L [COMPROMISED_USER]
   
   # Stop suspicious processes if safe to do so
   sudo pkill -f [SUSPICIOUS_PROCESS]
   ```

4. **PRESERVE EVIDENCE**
   ```bash
   # Create forensic snapshot
   sudo dd if=/dev/[DEVICE] of=/forensics/$(date +%Y%m%d_%H%M%S)_incident_image.dd bs=4M
   
   # Capture system state
   sudo netstat -tulpn > /forensics/netstat_$(date +%Y%m%d_%H%M%S).log
   sudo ps aux > /forensics/processes_$(date +%Y%m%d_%H%M%S).log
   sudo ss -tulpn > /forensics/sockets_$(date +%Y%m%d_%H%M%S).log
   ```

### **Step 2: Extended Response (15-60 minutes)**

#### **DETAILED ANALYSIS**
1. **SYSTEM ANALYSIS**
   ```bash
   # Check for rootkits and malware
   sudo rkhunter --check --report-warnings-only
   sudo chkrootkit
   
   # Analyze authentication logs
   sudo grep -i "failed\|error\|invalid" /var/log/auth.log | tail -50
   
   # Check for suspicious network connections
   sudo netstat -antup | grep ESTABLISHED
   ```

2. **PROXMOX-SPECIFIC CHECKS**
   ```bash
   # Check Proxmox logs for suspicious activity
   sudo grep -i "error\|fail\|unauthorized" /var/log/pve-* | tail -50
   
   # Verify VM integrity
   sudo pvesh get /nodes/$(hostname)/qemu --output-format json
   
   # Check cluster status
   sudo pvecm status
   ```

3. **EVIDENCE COLLECTION**
   ```bash
   # Collect comprehensive logs
   sudo tar -czf /forensics/incident_logs_$(date +%Y%m%d_%H%M%S).tar.gz \
     /var/log/auth.log \
     /var/log/syslog \
     /var/log/pve-* \
     /var/log/daemon.log
   
   # Memory dump (if system stable)
   sudo dd if=/proc/kcore of=/forensics/memory_$(date +%Y%m%d_%H%M%S).dump bs=1M count=1024
   ```

### **Step 3: Communication (Within 1 hour)**

#### **INTERNAL COMMUNICATION**
1. **Team Notification**
   - Notify all development agents
   - Brief project manager
   - Update security incident channel

2. **Documentation**
   - Create incident ticket
   - Document timeline of events
   - Record all actions taken

#### **EXTERNAL COMMUNICATION (If Required)**
1. **Management Notification**
   - Brief executive summary
   - Impact assessment
   - Immediate actions taken

2. **Customer/User Notification (If Applicable)**
   - Service impact notice
   - Security advisory
   - Remediation timeline

---

## 🔍 DETAILED INVESTIGATION PROCEDURES

### **Forensic Analysis Workflow**

#### **1. System State Analysis**
```bash
#!/bin/bash
# Comprehensive system analysis script

INCIDENT_DIR="/forensics/incident_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$INCIDENT_DIR"

echo "Starting forensic analysis at $(date)" > "$INCIDENT_DIR/analysis.log"

# System information
uname -a > "$INCIDENT_DIR/system_info.txt"
cat /proc/version >> "$INCIDENT_DIR/system_info.txt"
uptime >> "$INCIDENT_DIR/system_info.txt"

# Network analysis
netstat -antup > "$INCIDENT_DIR/network_connections.txt"
ss -tulpn > "$INCIDENT_DIR/socket_statistics.txt"
iptables -L -n -v > "$INCIDENT_DIR/firewall_rules.txt"

# Process analysis
ps auxf > "$INCIDENT_DIR/process_tree.txt"
lsof > "$INCIDENT_DIR/open_files.txt"

# File system analysis
find /tmp -type f -mtime -1 -ls > "$INCIDENT_DIR/recent_temp_files.txt"
find /var/tmp -type f -mtime -1 -ls >> "$INCIDENT_DIR/recent_temp_files.txt"
find /home -name ".*" -type f -mtime -1 -ls > "$INCIDENT_DIR/recent_hidden_files.txt"

# Authentication analysis
grep -i "fail\|error\|invalid\|denied" /var/log/auth.log > "$INCIDENT_DIR/auth_failures.txt"
last -n 50 > "$INCIDENT_DIR/recent_logins.txt"
who > "$INCIDENT_DIR/current_users.txt"

echo "Forensic analysis completed at $(date)" >> "$INCIDENT_DIR/analysis.log"
```

#### **2. Proxmox-Specific Investigation**
```bash
#!/bin/bash
# Proxmox security investigation script

PROXMOX_INCIDENT_DIR="/forensics/proxmox_incident_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$PROXMOX_INCIDENT_DIR"

# Proxmox cluster analysis
pvecm status > "$PROXMOX_INCIDENT_DIR/cluster_status.txt"
pvecm nodes > "$PROXMOX_INCIDENT_DIR/cluster_nodes.txt"

# VM analysis
pvesh get /nodes/$(hostname)/qemu --output-format json > "$PROXMOX_INCIDENT_DIR/vm_list.json"
pvesh get /nodes/$(hostname)/storage --output-format json > "$PROXMOX_INCIDENT_DIR/storage_list.json"

# Log analysis
grep -i "error\|fail\|unauthorized\|denied" /var/log/pve-* > "$PROXMOX_INCIDENT_DIR/pve_errors.txt"
grep -i "login\|auth" /var/log/pve-* > "$PROXMOX_INCIDENT_DIR/pve_auth.txt"

# Configuration backup
cp -r /etc/pve "$PROXMOX_INCIDENT_DIR/pve_config_backup"

# API access logs
grep -i "api" /var/log/daemon.log > "$PROXMOX_INCIDENT_DIR/api_access.txt"
```

### **Malware and Rootkit Detection**
```bash
#!/bin/bash
# Comprehensive malware detection

MALWARE_SCAN_DIR="/forensics/malware_scan_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$MALWARE_SCAN_DIR"

# Rootkit detection
rkhunter --check --report-warnings-only --logfile "$MALWARE_SCAN_DIR/rkhunter.log"
chkrootkit > "$MALWARE_SCAN_DIR/chkrootkit.log" 2>&1

# File integrity checking
aide --check > "$MALWARE_SCAN_DIR/aide_check.log" 2>&1

# Suspicious process detection
ps aux | grep -E "(nc|netcat|ncat|socat|perl|python|ruby|bash|sh).*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" > "$MALWARE_SCAN_DIR/suspicious_processes.txt"

# Suspicious network connections
netstat -antup | grep -E ":[1-9][0-9]{3,4}\s" > "$MALWARE_SCAN_DIR/suspicious_connections.txt"

# Check for backdoors
find /usr/bin /usr/sbin /bin /sbin -type f -perm -4000 -ls > "$MALWARE_SCAN_DIR/suid_files.txt"
find /tmp /var/tmp -name ".*" -type f -ls > "$MALWARE_SCAN_DIR/hidden_temp_files.txt"
```

---

## 🛡️ CONTAINMENT AND ERADICATION

### **Network Isolation Procedures**

#### **Immediate Network Isolation**
```bash
# Complete network isolation (EMERGENCY ONLY)
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT DROP

# Allow only essential local communication
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT

# Allow emergency SSH (modify as needed)
sudo iptables -A INPUT -p tcp --dport 22 -s [ADMIN_IP] -j ACCEPT
sudo iptables -A OUTPUT -p tcp --sport 22 -d [ADMIN_IP] -j ACCEPT
```

#### **Selective Network Controls**
```bash
# Block specific suspicious IPs
SUSPICIOUS_IPS=("IP1" "IP2" "IP3")
for ip in "${SUSPICIOUS_IPS[@]}"; do
    sudo iptables -A INPUT -s "$ip" -j DROP
    sudo iptables -A OUTPUT -d "$ip" -j DROP
done

# Block suspicious ports
SUSPICIOUS_PORTS=("6667" "1337" "31337")
for port in "${SUSPICIOUS_PORTS[@]}"; do
    sudo iptables -A INPUT -p tcp --dport "$port" -j DROP
    sudo iptables -A OUTPUT -p tcp --sport "$port" -j DROP
done
```

### **System Isolation Procedures**

#### **VM Isolation (Proxmox)**
```bash
# Stop suspicious VMs
SUSPICIOUS_VMIDS=("101" "102")
for vmid in "${SUSPICIOUS_VMIDS[@]}"; do
    pvesh create /nodes/$(hostname)/qemu/$vmid/status/stop
done

# Isolate VM networks
pvesh set /nodes/$(hostname)/qemu/$vmid/config -net0 model=virtio,bridge=vmbr999

# Create isolated VLAN for investigation
pvesh create /nodes/$(hostname)/network -iface vmbr999 -type bridge -comments "Isolated bridge for security investigation"
```

#### **User Account Controls**
```bash
# Disable suspicious user accounts
SUSPICIOUS_USERS=("user1" "user2")
for user in "${SUSPICIOUS_USERS[@]}"; do
    sudo usermod -L "$user"
    sudo usermod -s /bin/false "$user"
done

# Force logout of active sessions
sudo pkill -u [SUSPICIOUS_USER]

# Disable sudo access temporarily
sudo usermod -G "" [SUSPICIOUS_USER]
```

### **Eradication Procedures**

#### **Malware Removal**
```bash
# Remove identified malware files
MALWARE_FILES=("/tmp/suspicious_file" "/var/tmp/backdoor")
for file in "${MALWARE_FILES[@]}"; do
    if [ -f "$file" ]; then
        sudo rm -f "$file"
        echo "Removed malware file: $file"
    fi
done

# Clean suspicious processes
MALWARE_PROCESSES=("suspicious_process" "backdoor_daemon")
for process in "${MALWARE_PROCESSES[@]}"; do
    sudo pkill -f "$process"
done

# Remove malicious cron jobs
sudo crontab -l | grep -v "suspicious_command" | sudo crontab -
```

#### **Configuration Restoration**
```bash
# Restore from known good configuration
sudo cp /backup/config/sshd_config.backup /etc/ssh/sshd_config
sudo systemctl restart sshd

# Restore firewall rules
sudo iptables-restore < /backup/config/iptables.backup

# Reset file permissions
sudo chmod 644 /etc/passwd
sudo chmod 640 /etc/shadow
sudo chmod 644 /etc/group
```

---

## 🔄 RECOVERY PROCEDURES

### **System Recovery Checklist**

#### **Pre-Recovery Validation**
- [ ] Threat completely eradicated
- [ ] System integrity verified
- [ ] Forensic evidence preserved
- [ ] Root cause identified
- [ ] Patches/fixes applied
- [ ] Monitoring enhanced

#### **Proxmox System Recovery**
```bash
# Verify Proxmox cluster health
pvecm status
pvecm nodes

# Check storage integrity
pvesm status

# Verify VM configurations
for vmid in $(pvesh get /nodes/$(hostname)/qemu --output-format json | jq -r '.[].vmid'); do
    pvesh get /nodes/$(hostname)/qemu/$vmid/config
done

# Test backup integrity
pvesh get /nodes/$(hostname)/storage/[STORAGE]/content --content backup
```

#### **Service Restoration**
```bash
# Restart essential services
sudo systemctl restart sshd
sudo systemctl restart pveproxy
sudo systemctl restart pvedaemon

# Verify service health
sudo systemctl status pveproxy
sudo systemctl status pvedaemon
sudo systemctl status pvestatd

# Test API functionality
curl -k https://localhost:8006/api2/json/version
```

### **Network Recovery**
```bash
# Gradually restore network access
sudo iptables -F
sudo iptables -X
sudo iptables -Z

# Restore normal firewall rules
sudo iptables-restore < /etc/iptables/rules.v4

# Test network connectivity
ping -c 3 8.8.8.8
curl -I https://www.google.com
```

---

## 📊 POST-INCIDENT ACTIVITIES

### **Damage Assessment**

#### **Data Integrity Check**
```bash
# VM data integrity
for vmid in $(pvesh get /nodes/$(hostname)/qemu --output-format json | jq -r '.[].vmid'); do
    echo "Checking VM $vmid"
    pvesh get /nodes/$(hostname)/qemu/$vmid/status/current
done

# Storage integrity
zpool status
lvs
```

#### **Security Control Validation**
```bash
# Verify security configurations
sudo sshd -t
sudo nginx -t
sudo ufw status verbose

# Check file integrity
sudo aide --check
```

### **Root Cause Analysis**

#### **Investigation Questions**
1. **How did the incident occur?**
   - Initial attack vector
   - Exploitation method
   - Timeline of compromise

2. **What vulnerabilities were exploited?**
   - Technical vulnerabilities
   - Process weaknesses
   - Human factors

3. **What was the impact?**
   - Systems affected
   - Data compromised
   - Service disruption

4. **What controls failed?**
   - Detection failures
   - Prevention failures
   - Response delays

#### **Documentation Requirements**
- Detailed incident timeline
- Technical analysis report
- Lessons learned document
- Improvement recommendations
- Updated procedures

### **Improvement Implementation**

#### **Immediate Improvements**
- Patch identified vulnerabilities
- Update security configurations
- Enhance monitoring rules
- Improve access controls

#### **Long-term Improvements**
- Security architecture changes
- Process improvements
- Training updates
- Technology upgrades

---

## 🔄 LESSONS LEARNED PROCESS

### **Post-Incident Review Meeting**
**Attendees:** All incident response team members
**Timeline:** Within 72 hours of incident closure

#### **Meeting Agenda**
1. Incident timeline review
2. Response effectiveness analysis
3. What went well
4. What could be improved
5. Action items assignment
6. Process updates needed

### **Improvement Tracking**
```bash
# Create improvement tracking
cat > /security/improvements/incident_$(date +%Y%m%d)_improvements.md << EOF
# Incident Improvement Tracking

## Incident ID: INC-$(date +%Y%m%d)-001
## Date: $(date)

### Immediate Actions
- [ ] Action 1 (Owner: X, Due: Date)
- [ ] Action 2 (Owner: Y, Due: Date)

### Medium-term Actions
- [ ] Action 3 (Owner: Z, Due: Date)
- [ ] Action 4 (Owner: A, Due: Date)

### Long-term Actions
- [ ] Action 5 (Owner: B, Due: Date)
- [ ] Action 6 (Owner: C, Due: Date)
EOF
```

---

## 📱 COMMUNICATION TEMPLATES

### **Critical Incident Alert Template**
```
SUBJECT: CRITICAL SECURITY INCIDENT - Immediate Response Required

INCIDENT DETAILS:
- Incident ID: INC-YYYYMMDD-XXX
- Classification: [CRITICAL/HIGH/MEDIUM/LOW]
- Discovery Time: [TIME]
- Affected Systems: [SYSTEMS]
- Initial Assessment: [BRIEF DESCRIPTION]

IMMEDIATE ACTIONS TAKEN:
- [ACTION 1]
- [ACTION 2]
- [ACTION 3]

NEXT STEPS:
- [NEXT ACTION 1]
- [NEXT ACTION 2]

RESPONSE TEAM:
- Incident Commander: [NAME]
- Technical Lead: [NAME]
- Communications: [NAME]

Contact the incident commander immediately for coordination.
```

### **Executive Summary Template**
```
SUBJECT: Security Incident Executive Summary - [INCIDENT ID]

EXECUTIVE SUMMARY:
A security incident was detected at [TIME] affecting [SYSTEMS/SERVICES]. 
The incident has been [CONTAINED/RESOLVED] and normal operations [RESTORED/IN PROGRESS].

IMPACT:
- Service Impact: [DESCRIPTION]
- Data Impact: [DESCRIPTION]  
- Customer Impact: [DESCRIPTION]

RESPONSE:
- Detection Time: [TIME]
- Response Time: [TIME]
- Resolution Time: [TIME]

ROOT CAUSE:
[BRIEF DESCRIPTION OF ROOT CAUSE]

REMEDIATION:
[DESCRIPTION OF FIXES APPLIED]

NEXT STEPS:
[IMPROVEMENT ACTIONS]

This incident is now [RESOLVED/UNDER INVESTIGATION].
```

---

## 🧪 TESTING AND VALIDATION

### **Incident Response Testing**

#### **Tabletop Exercises**
- Monthly scenario discussions
- Quarterly comprehensive exercises
- Annual red team exercises

#### **Technical Testing**
```bash
# Test incident response scripts
./scripts/incident_response_test.sh

# Validate forensic procedures
./scripts/forensic_test.sh

# Test communication procedures
./scripts/communication_test.sh
```

### **Procedure Validation**
- Regular procedure walkthroughs
- Response time measurements
- Tool functionality verification
- Team readiness assessment

---

**APPROVAL STATUS:** This incident response procedure is approved for immediate implementation and regular testing.

**NEXT REVIEW:** Monthly review of procedures, quarterly comprehensive update.

**CONTACT:** For questions or updates to this procedure, contact the QA Engineer & Security Specialist.

---

*This document contains sensitive security procedures. Distribution is limited to authorized personnel only. Unauthorized disclosure is prohibited.*