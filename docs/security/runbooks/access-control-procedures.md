# Access Control Procedures Runbook

## Overview

This runbook establishes comprehensive access control procedures for the Proxmox AI Infrastructure Assistant environment, implementing Zero Trust principles with least privilege access, multi-factor authentication, and continuous monitoring.

## Access Control Framework

### 1. Access Control Principles

#### Zero Trust Model
- **Never Trust, Always Verify**: Every access request must be authenticated and authorized
- **Least Privilege**: Users receive minimum access required for their role
- **Continuous Verification**: Access rights are continuously validated
- **Dynamic Access Control**: Access decisions based on context and risk

#### Role-Based Access Control (RBAC)

```python
#!/usr/bin/env python3
# Role-Based Access Control Implementation
# File: /scripts/security/rbac_manager.py

import json
import sqlite3
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets

class AccessLevel(Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"

class ResourceType(Enum):
    VM = "vm"
    NETWORK = "network"
    STORAGE = "storage"
    BACKUP = "backup"
    SYSTEM = "system"
    SECURITY = "security"

@dataclass
class Permission:
    resource_type: ResourceType
    resource_id: Optional[str]  # None for all resources of type
    access_level: AccessLevel
    conditions: Dict[str, str]  # Additional conditions (time, location, etc.)

@dataclass
class Role:
    name: str
    description: str
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class User:
    username: str
    email: str
    full_name: str
    roles: List[str]
    mfa_enabled: bool = False
    is_active: bool = True
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AccessRequest:
    user_id: str
    resource_type: ResourceType
    resource_id: str
    access_level: AccessLevel
    request_context: Dict[str, str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class RBACManager:
    def __init__(self, db_path: str = "/var/lib/security/rbac.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._initialize_database()
        self._create_default_roles()
    
    def _initialize_database(self):
        """Initialize RBAC database schema"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT,
                mfa_enabled BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Roles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                name TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                permissions TEXT NOT NULL, -- JSON array of permissions
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User-Role assignments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_roles (
                username TEXT,
                role_name TEXT,
                assigned_by TEXT,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                PRIMARY KEY (username, role_name),
                FOREIGN KEY (username) REFERENCES users(username),
                FOREIGN KEY (role_name) REFERENCES roles(name)
            )
        """)
        
        # Access logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                resource_type TEXT,
                resource_id TEXT,
                access_level TEXT,
                action TEXT,
                result TEXT, -- 'granted', 'denied'
                reason TEXT,
                source_ip TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        # MFA tokens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mfa_tokens (
                username TEXT,
                token_type TEXT, -- 'totp', 'backup'
                token_value TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                PRIMARY KEY (username, token_type, token_value),
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        self.conn.commit()
    
    def _create_default_roles(self):
        """Create default system roles"""
        default_roles = [
            Role(
                name="system_admin",
                description="System Administrator - Full access to all resources",
                permissions=[
                    Permission(ResourceType.SYSTEM, None, AccessLevel.OWNER, {}),
                    Permission(ResourceType.VM, None, AccessLevel.ADMIN, {}),
                    Permission(ResourceType.NETWORK, None, AccessLevel.ADMIN, {}),
                    Permission(ResourceType.STORAGE, None, AccessLevel.ADMIN, {}),
                    Permission(ResourceType.BACKUP, None, AccessLevel.ADMIN, {}),
                    Permission(ResourceType.SECURITY, None, AccessLevel.ADMIN, {})
                ]
            ),
            Role(
                name="infrastructure_operator",
                description="Infrastructure Operator - VM and network management",
                permissions=[
                    Permission(ResourceType.VM, None, AccessLevel.WRITE, {}),
                    Permission(ResourceType.NETWORK, None, AccessLevel.WRITE, {}),
                    Permission(ResourceType.STORAGE, None, AccessLevel.READ, {}),
                    Permission(ResourceType.BACKUP, None, AccessLevel.READ, {})
                ]
            ),
            Role(
                name="security_auditor",
                description="Security Auditor - Read-only access for security monitoring",
                permissions=[
                    Permission(ResourceType.SECURITY, None, AccessLevel.READ, {}),
                    Permission(ResourceType.SYSTEM, None, AccessLevel.READ, {"audit_only": "true"}),
                    Permission(ResourceType.VM, None, AccessLevel.READ, {}),
                    Permission(ResourceType.NETWORK, None, AccessLevel.READ, {})
                ]
            ),
            Role(
                name="developer",
                description="Developer - Limited VM access for development",
                permissions=[
                    Permission(ResourceType.VM, None, AccessLevel.WRITE, {"environment": "development"}),
                    Permission(ResourceType.NETWORK, None, AccessLevel.READ, {}),
                    Permission(ResourceType.STORAGE, None, AccessLevel.READ, {})
                ]
            ),
            Role(
                name="readonly_user",
                description="Read-only User - View access only",
                permissions=[
                    Permission(ResourceType.VM, None, AccessLevel.READ, {}),
                    Permission(ResourceType.NETWORK, None, AccessLevel.READ, {}),
                    Permission(ResourceType.STORAGE, None, AccessLevel.READ, {})
                ]
            )
        ]
        
        for role in default_roles:
            self.create_role(role)
    
    def create_user(self, user: User, password: str = None) -> bool:
        """Create a new user with secure password handling"""
        cursor = self.conn.cursor()
        
        try:
            # Hash password if provided
            password_hash = None
            if password:
                salt = secrets.token_hex(32)
                password_hash = hashlib.pbkdf2_hmac('sha256', 
                                                  password.encode('utf-8'), 
                                                  salt.encode('utf-8'), 
                                                  100000)
                password_hash = salt + password_hash.hex()
            
            cursor.execute("""
                INSERT INTO users (username, email, full_name, password_hash, mfa_enabled, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user.username, user.email, user.full_name, password_hash, user.mfa_enabled, user.is_active))
            
            # Assign roles
            for role_name in user.roles:
                self.assign_role_to_user(user.username, role_name, "system")
            
            self.conn.commit()
            self._log_access("system", "user", user.username, "admin", "create_user", "granted", "User created successfully")
            return True
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            self._log_access("system", "user", user.username, "admin", "create_user", "denied", f"User creation failed: {e}")
            return False
    
    def create_role(self, role: Role) -> bool:
        """Create a new role"""
        cursor = self.conn.cursor()
        
        try:
            permissions_json = json.dumps([asdict(p) for p in role.permissions])
            
            cursor.execute("""
                INSERT OR REPLACE INTO roles (name, description, permissions, is_active)
                VALUES (?, ?, ?, ?)
            """, (role.name, role.description, permissions_json, role.is_active))
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error creating role {role.name}: {e}")
            return False
    
    def assign_role_to_user(self, username: str, role_name: str, assigned_by: str, expires_at: datetime = None) -> bool:
        """Assign a role to a user"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO user_roles (username, role_name, assigned_by, expires_at, is_active)
                VALUES (?, ?, ?, ?, TRUE)
            """, (username, role_name, assigned_by, expires_at))
            
            self.conn.commit()
            self._log_access(assigned_by, "role", role_name, "admin", "assign_role", "granted", f"Role assigned to {username}")
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            self._log_access(assigned_by, "role", role_name, "admin", "assign_role", "denied", f"Role assignment failed: {e}")
            return False
    
    def check_access(self, request: AccessRequest) -> bool:
        """Check if user has access to requested resource"""
        cursor = self.conn.cursor()
        
        # Get user's roles
        cursor.execute("""
            SELECT r.permissions 
            FROM users u
            JOIN user_roles ur ON u.username = ur.username
            JOIN roles r ON ur.role_name = r.name
            WHERE u.username = ? AND u.is_active = TRUE AND ur.is_active = TRUE 
            AND r.is_active = TRUE
            AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
        """, (request.user_id,))
        
        role_permissions = cursor.fetchall()
        
        # Check permissions
        access_granted = False
        for (permissions_json,) in role_permissions:
            permissions = json.loads(permissions_json)
            
            for perm_dict in permissions:
                perm = Permission(
                    resource_type=ResourceType(perm_dict['resource_type']),
                    resource_id=perm_dict.get('resource_id'),
                    access_level=AccessLevel(perm_dict['access_level']),
                    conditions=perm_dict.get('conditions', {})
                )
                
                if self._permission_matches_request(perm, request):
                    access_granted = True
                    break
            
            if access_granted:
                break
        
        # Log access attempt
        result = "granted" if access_granted else "denied"
        reason = "Permission found" if access_granted else "No matching permission"
        
        self._log_access(
            request.user_id, 
            request.resource_type.value, 
            request.resource_id,
            request.access_level.value,
            "access_check",
            result,
            reason
        )
        
        return access_granted
    
    def _permission_matches_request(self, permission: Permission, request: AccessRequest) -> bool:
        """Check if a permission matches an access request"""
        # Check resource type
        if permission.resource_type != request.resource_type:
            return False
        
        # Check resource ID (None means all resources of type)
        if permission.resource_id is not None and permission.resource_id != request.resource_id:
            return False
        
        # Check access level hierarchy
        access_hierarchy = {
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.OWNER: 4
        }
        
        if access_hierarchy[permission.access_level] < access_hierarchy[request.access_level]:
            return False
        
        # Check conditions
        for condition_key, condition_value in permission.conditions.items():
            if condition_key in request.request_context:
                if request.request_context[condition_key] != condition_value:
                    return False
        
        return True
    
    def _log_access(self, username: str, resource_type: str, resource_id: str, 
                   access_level: str, action: str, result: str, reason: str):
        """Log access attempt"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO access_logs (username, resource_type, resource_id, access_level, 
                                   action, result, reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (username, resource_type, resource_id, access_level, action, result, reason))
        
        self.conn.commit()
    
    def get_user_permissions(self, username: str) -> List[Permission]:
        """Get all permissions for a user"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT r.permissions 
            FROM users u
            JOIN user_roles ur ON u.username = ur.username
            JOIN roles r ON ur.role_name = r.name
            WHERE u.username = ? AND u.is_active = TRUE AND ur.is_active = TRUE 
            AND r.is_active = TRUE
            AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
        """, (username,))
        
        all_permissions = []
        for (permissions_json,) in cursor.fetchall():
            permissions = json.loads(permissions_json)
            for perm_dict in permissions:
                perm = Permission(
                    resource_type=ResourceType(perm_dict['resource_type']),
                    resource_id=perm_dict.get('resource_id'),
                    access_level=AccessLevel(perm_dict['access_level']),
                    conditions=perm_dict.get('conditions', {})
                )
                all_permissions.append(perm)
        
        return all_permissions
    
    def revoke_user_access(self, username: str, revoked_by: str, reason: str = "") -> bool:
        """Revoke all access for a user"""
        cursor = self.conn.cursor()
        
        try:
            # Deactivate user
            cursor.execute("""
                UPDATE users SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            """, (username,))
            
            # Deactivate role assignments
            cursor.execute("""
                UPDATE user_roles SET is_active = FALSE
                WHERE username = ?
            """, (username,))
            
            self.conn.commit()
            self._log_access(revoked_by, "user", username, "admin", "revoke_access", "granted", f"Access revoked: {reason}")
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            self._log_access(revoked_by, "user", username, "admin", "revoke_access", "denied", f"Revocation failed: {e}")
            return False
    
    def generate_access_report(self, days: int = 30) -> Dict[str, any]:
        """Generate access control report"""
        cursor = self.conn.cursor()
        start_date = datetime.now() - timedelta(days=days)
        
        # Access statistics
        cursor.execute("""
            SELECT result, COUNT(*) as count
            FROM access_logs 
            WHERE timestamp >= ?
            GROUP BY result
        """, (start_date,))
        
        access_stats = dict(cursor.fetchall())
        
        # Top users by access attempts
        cursor.execute("""
            SELECT username, COUNT(*) as attempts
            FROM access_logs 
            WHERE timestamp >= ?
            GROUP BY username
            ORDER BY attempts DESC
            LIMIT 10
        """, (start_date,))
        
        top_users = [{"username": row[0], "attempts": row[1]} for row in cursor.fetchall()]
        
        # Access denials by reason
        cursor.execute("""
            SELECT reason, COUNT(*) as count
            FROM access_logs 
            WHERE timestamp >= ? AND result = 'denied'
            GROUP BY reason
            ORDER BY count DESC
        """, (start_date,))
        
        denial_reasons = [{"reason": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Active users and roles
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
        active_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM roles WHERE is_active = TRUE")
        active_roles = cursor.fetchone()[0]
        
        return {
            "report_period_days": days,
            "access_statistics": access_stats,
            "top_users": top_users,
            "denial_reasons": denial_reasons,
            "active_users": active_users,
            "active_roles": active_roles,
            "generated_at": datetime.now().isoformat()
        }

def main():
    # Example usage
    rbac = RBACManager()
    
    # Create a test user
    test_user = User(
        username="test_operator",
        email="operator@example.com",
        full_name="Test Operator",
        roles=["infrastructure_operator"],
        mfa_enabled=True
    )
    
    if rbac.create_user(test_user, "secure_password123"):
        print("User created successfully")
    
    # Test access
    access_request = AccessRequest(
        user_id="test_operator",
        resource_type=ResourceType.VM,
        resource_id="vm-001",
        access_level=AccessLevel.WRITE,
        request_context={}
    )
    
    if rbac.check_access(access_request):
        print("Access granted")
    else:
        print("Access denied")
    
    # Generate report
    report = rbac.generate_access_report()
    print(f"Access report: {json.dumps(report, indent=2)}")

if __name__ == "__main__":
    main()
```

### 2. Multi-Factor Authentication (MFA)

#### MFA Implementation

```python
#!/usr/bin/env python3
# Multi-Factor Authentication System
# File: /scripts/security/mfa_manager.py

import pyotp
import qrcode
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@dataclass
class MFASetup:
    username: str
    secret_key: str
    qr_code_url: str
    backup_codes: List[str]
    setup_timestamp: datetime

class MFAManager:
    def __init__(self, db_path: str = "/var/lib/security/mfa.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize MFA database schema"""
        cursor = self.conn.cursor()
        
        # MFA configurations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mfa_configs (
                username TEXT PRIMARY KEY,
                secret_key TEXT NOT NULL,
                backup_codes TEXT, -- JSON array
                is_enabled BOOLEAN DEFAULT FALSE,
                setup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        # MFA attempts log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mfa_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                attempt_type TEXT, -- 'totp', 'backup_code', 'sms'
                result TEXT, -- 'success', 'failure'
                source_ip TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        self.conn.commit()
    
    def setup_totp_for_user(self, username: str, issuer: str = "Proxmox AI Assistant") -> MFASetup:
        """Setup TOTP MFA for a user"""
        # Generate secret key
        secret_key = pyotp.random_base32()
        
        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=username,
            issuer_name=issuer
        )
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        
        # Store in database
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO mfa_configs (username, secret_key, backup_codes, is_enabled)
            VALUES (?, ?, ?, FALSE)
        """, (username, secret_key, json.dumps(backup_codes)))
        
        self.conn.commit()
        
        return MFASetup(
            username=username,
            secret_key=secret_key,
            qr_code_url=totp_uri,
            backup_codes=backup_codes,
            setup_timestamp=datetime.now()
        )
    
    def verify_totp_token(self, username: str, token: str) -> bool:
        """Verify TOTP token for user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT secret_key FROM mfa_configs 
            WHERE username = ? AND is_enabled = TRUE
        """, (username,))
        
        result = cursor.fetchone()
        if not result:
            self._log_mfa_attempt(username, "totp", "failure", "MFA not enabled")
            return False
        
        secret_key = result[0]
        totp = pyotp.TOTP(secret_key)
        
        # Verify token (with 30-second window tolerance)
        is_valid = totp.verify(token, valid_window=1)
        
        if is_valid:
            # Update last used timestamp
            cursor.execute("""
                UPDATE mfa_configs SET last_used = CURRENT_TIMESTAMP
                WHERE username = ?
            """, (username,))
            self.conn.commit()
            
            self._log_mfa_attempt(username, "totp", "success", "Token verified")
        else:
            self._log_mfa_attempt(username, "totp", "failure", "Invalid token")
        
        return is_valid
    
    def verify_backup_code(self, username: str, backup_code: str) -> bool:
        """Verify backup code for user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT backup_codes FROM mfa_configs 
            WHERE username = ? AND is_enabled = TRUE
        """, (username,))
        
        result = cursor.fetchone()
        if not result:
            self._log_mfa_attempt(username, "backup_code", "failure", "MFA not enabled")
            return False
        
        backup_codes = json.loads(result[0])
        backup_code_upper = backup_code.upper().strip()
        
        if backup_code_upper in backup_codes:
            # Remove used backup code
            backup_codes.remove(backup_code_upper)
            
            cursor.execute("""
                UPDATE mfa_configs SET backup_codes = ?, last_used = CURRENT_TIMESTAMP
                WHERE username = ?
            """, (json.dumps(backup_codes), username))
            
            self.conn.commit()
            
            self._log_mfa_attempt(username, "backup_code", "success", "Backup code used")
            return True
        else:
            self._log_mfa_attempt(username, "backup_code", "failure", "Invalid backup code")
            return False
    
    def enable_mfa_for_user(self, username: str, verification_token: str) -> bool:
        """Enable MFA for user after verifying initial token"""
        if self.verify_totp_token(username, verification_token):
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE mfa_configs SET is_enabled = TRUE
                WHERE username = ?
            """, (username,))
            
            self.conn.commit()
            return True
        
        return False
    
    def disable_mfa_for_user(self, username: str, admin_user: str) -> bool:
        """Disable MFA for user (admin action)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mfa_configs SET is_enabled = FALSE
            WHERE username = ?
        """, (username,))
        
        self.conn.commit()
        
        self._log_mfa_attempt(admin_user, "admin_disable", "success", f"MFA disabled for {username}")
        return True
    
    def _log_mfa_attempt(self, username: str, attempt_type: str, result: str, details: str):
        """Log MFA attempt"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO mfa_attempts (username, attempt_type, result, source_ip, timestamp)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (username, attempt_type, result, "127.0.0.1"))  # TODO: Get real IP
        
        self.conn.commit()
    
    def generate_mfa_qr_image(self, totp_uri: str, output_path: str):
        """Generate QR code image for TOTP setup"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        
        return output_path
    
    def get_mfa_status(self, username: str) -> Optional[dict]:
        """Get MFA status for user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT is_enabled, setup_date, last_used, backup_codes
            FROM mfa_configs 
            WHERE username = ?
        """, (username,))
        
        result = cursor.fetchone()
        if not result:
            return None
        
        backup_codes = json.loads(result[3]) if result[3] else []
        
        return {
            "enabled": bool(result[0]),
            "setup_date": result[1],
            "last_used": result[2],
            "backup_codes_remaining": len(backup_codes)
        }
```

### 3. SSH Key Management

#### Automated SSH Key Rotation

```bash
#!/bin/bash
# SSH Key Rotation Script
# File: /scripts/security/ssh_key_rotation.sh

set -euo pipefail

# Configuration
KEY_DIR="/etc/ssh/keys"
BACKUP_DIR="/backup/ssh_keys"
PROXMOX_HOST="192.168.1.50"
ROTATION_LOG="/var/log/security/ssh_key_rotation.log"
KEY_SIZE=4096
KEY_TYPE="rsa"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$ROTATION_LOG"
}

create_key_directories() {
    log_message "Creating key directories..."
    mkdir -p "$KEY_DIR" "$BACKUP_DIR"
    chmod 700 "$KEY_DIR" "$BACKUP_DIR"
}

backup_existing_keys() {
    log_message "Backing up existing SSH keys..."
    
    backup_timestamp=$(date +%Y%m%d_%H%M%S)
    backup_path="$BACKUP_DIR/backup_$backup_timestamp"
    mkdir -p "$backup_path"
    
    # Backup client keys
    if [[ -f ~/.ssh/proxmox_ai_key ]]; then
        cp ~/.ssh/proxmox_ai_key* "$backup_path/"
        log_message "Client keys backed up to $backup_path"
    fi
    
    # Backup server keys
    ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@"$PROXMOX_HOST" "
        mkdir -p /backup/ssh_keys/backup_$backup_timestamp
        cp /etc/ssh/ssh_host_* /backup/ssh_keys/backup_$backup_timestamp/ 2>/dev/null || true
        cp /root/.ssh/authorized_keys /backup/ssh_keys/backup_$backup_timestamp/ 2>/dev/null || true
    " 2>&1 | tee -a "$ROTATION_LOG"
}

generate_new_client_key() {
    log_message "Generating new client SSH key..."
    
    new_key_path="$KEY_DIR/proxmox_ai_key_new"
    
    # Generate new key pair
    ssh-keygen -t "$KEY_TYPE" -b "$KEY_SIZE" -f "$new_key_path" -N "" \
        -C "proxmox-ai-assistant-$(date +%Y%m%d)"
    
    # Set proper permissions
    chmod 600 "$new_key_path"
    chmod 644 "$new_key_path.pub"
    
    log_message "New client key generated: $new_key_path"
}

deploy_new_client_key() {
    log_message "Deploying new client key to Proxmox host..."
    
    new_key_path="$KEY_DIR/proxmox_ai_key_new"
    
    # Add new public key to authorized_keys
    ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@"$PROXMOX_HOST" "
        # Backup current authorized_keys
        cp /root/.ssh/authorized_keys /root/.ssh/authorized_keys.backup
        
        # Add new key
        cat >> /root/.ssh/authorized_keys
    " < "$new_key_path.pub" 2>&1 | tee -a "$ROTATION_LOG"
    
    # Test new key
    if ssh -i "$new_key_path" -p 2849 -o ConnectTimeout=10 root@"$PROXMOX_HOST" "echo 'New key test successful'"; then
        log_message "✓ New client key deployed and tested successfully"
        return 0
    else
        log_message "✗ New client key test failed"
        return 1
    fi
}

rotate_server_host_keys() {
    log_message "Rotating server host keys..."
    
    ssh -i "$KEY_DIR/proxmox_ai_key_new" -p 2849 root@"$PROXMOX_HOST" "
        # Generate new host keys
        ssh-keygen -t rsa -b 4096 -f /etc/ssh/ssh_host_rsa_key_new -N ''
        ssh-keygen -t ecdsa -b 521 -f /etc/ssh/ssh_host_ecdsa_key_new -N ''
        ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key_new -N ''
        
        # Set proper permissions
        chmod 600 /etc/ssh/ssh_host_*_key_new
        chmod 644 /etc/ssh/ssh_host_*_key_new.pub
        
        # Replace old keys
        mv /etc/ssh/ssh_host_rsa_key /etc/ssh/ssh_host_rsa_key.old || true
        mv /etc/ssh/ssh_host_ecdsa_key /etc/ssh/ssh_host_ecdsa_key.old || true
        mv /etc/ssh/ssh_host_ed25519_key /etc/ssh/ssh_host_ed25519_key.old || true
        
        mv /etc/ssh/ssh_host_rsa_key_new /etc/ssh/ssh_host_rsa_key
        mv /etc/ssh/ssh_host_ecdsa_key_new /etc/ssh/ssh_host_ecdsa_key
        mv /etc/ssh/ssh_host_ed25519_key_new /etc/ssh/ssh_host_ed25519_key
        
        mv /etc/ssh/ssh_host_rsa_key_new.pub /etc/ssh/ssh_host_rsa_key.pub
        mv /etc/ssh/ssh_host_ecdsa_key_new.pub /etc/ssh/ssh_host_ecdsa_key.pub
        mv /etc/ssh/ssh_host_ed25519_key_new.pub /etc/ssh/ssh_host_ed25519_key.pub
        
        # Restart SSH service
        systemctl restart ssh
        
        echo 'Host keys rotated successfully'
    " 2>&1 | tee -a "$ROTATION_LOG"
}

activate_new_client_key() {
    log_message "Activating new client key..."
    
    # Move old key
    if [[ -f ~/.ssh/proxmox_ai_key ]]; then
        mv ~/.ssh/proxmox_ai_key ~/.ssh/proxmox_ai_key.old
        mv ~/.ssh/proxmox_ai_key.pub ~/.ssh/proxmox_ai_key.pub.old
    fi
    
    # Activate new key
    cp "$KEY_DIR/proxmox_ai_key_new" ~/.ssh/proxmox_ai_key
    cp "$KEY_DIR/proxmox_ai_key_new.pub" ~/.ssh/proxmox_ai_key.pub
    
    # Set proper permissions
    chmod 600 ~/.ssh/proxmox_ai_key
    chmod 644 ~/.ssh/proxmox_ai_key.pub
    
    log_message "New client key activated"
}

cleanup_old_keys() {
    log_message "Cleaning up old keys..."
    
    # Remove old public key from server
    ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@"$PROXMOX_HOST" "
        # Remove old key from authorized_keys
        if [[ -f /root/.ssh/authorized_keys.backup ]]; then
            # Get old key content
            if [[ -f ~/.ssh/proxmox_ai_key.pub.old ]]; then
                old_key_content=\$(cat ~/.ssh/proxmox_ai_key.pub.old 2>/dev/null || echo 'OLD_KEY_NOT_FOUND')
                
                # Remove old key from authorized_keys
                grep -v \"\$old_key_content\" /root/.ssh/authorized_keys > /root/.ssh/authorized_keys.tmp || true
                mv /root/.ssh/authorized_keys.tmp /root/.ssh/authorized_keys
            fi
        fi
        
        # Remove old host keys
        rm -f /etc/ssh/ssh_host_*_key.old /etc/ssh/ssh_host_*_key.old.pub
        
        echo 'Server cleanup completed'
    " 2>&1 | tee -a "$ROTATION_LOG"
    
    # Clean up local files
    rm -f ~/.ssh/proxmox_ai_key.old ~/.ssh/proxmox_ai_key.pub.old
    rm -f "$KEY_DIR/proxmox_ai_key_new" "$KEY_DIR/proxmox_ai_key_new.pub"
    
    log_message "Key cleanup completed"
}

verify_rotation() {
    log_message "Verifying key rotation..."
    
    # Test SSH connectivity
    if ssh -i ~/.ssh/proxmox_ai_key -p 2849 -o ConnectTimeout=10 root@"$PROXMOX_HOST" "echo 'SSH connectivity verified'"; then
        log_message "✓ SSH connectivity verified"
    else
        log_message "✗ SSH connectivity failed"
        return 1
    fi
    
    # Test Proxmox API access
    source /etc/proxmox-ai/credentials.env
    if curl -k -s -H "Authorization: PVEAPIToken=$PROXMOX_API_TOKEN" \
       https://192.168.1.50:8006/api2/json/version >/dev/null; then
        log_message "✓ Proxmox API access verified"
    else
        log_message "✗ Proxmox API access failed"
        return 1
    fi
    
    # Verify host key fingerprints
    ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@"$PROXMOX_HOST" "
        echo 'New host key fingerprints:'
        ssh-keygen -lf /etc/ssh/ssh_host_rsa_key.pub
        ssh-keygen -lf /etc/ssh/ssh_host_ecdsa_key.pub
        ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
    " 2>&1 | tee -a "$ROTATION_LOG"
    
    log_message "Key rotation verification completed successfully"
}

update_known_hosts() {
    log_message "Updating known_hosts with new host keys..."
    
    # Remove old host key entries
    ssh-keygen -R "$PROXMOX_HOST" 2>/dev/null || true
    ssh-keygen -R "[${PROXMOX_HOST}]:2849" 2>/dev/null || true
    
    # Add new host keys
    ssh-keyscan -p 2849 -H "$PROXMOX_HOST" >> ~/.ssh/known_hosts 2>/dev/null || true
    
    log_message "Known hosts updated"
}

send_rotation_notification() {
    log_message "Sending rotation notification..."
    
    # Create rotation report
    cat << EOF > /tmp/ssh_key_rotation_report.txt
SSH Key Rotation Report
Date: $(date)
System: Proxmox AI Infrastructure Assistant

=== Rotation Summary ===
- Client keys: Rotated successfully
- Server host keys: Rotated successfully
- SSH connectivity: Verified
- API access: Verified

=== New Key Fingerprints ===
$(ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@"$PROXMOX_HOST" "
    ssh-keygen -lf /etc/ssh/ssh_host_rsa_key.pub
    ssh-keygen -lf /etc/ssh/ssh_host_ecdsa_key.pub
    ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
" 2>/dev/null)

=== Security Notes ===
- Old keys have been backed up to: $BACKUP_DIR
- All connections should verify new host key fingerprints
- Monitor logs for any unauthorized access attempts

Report generated on: $(date)
EOF
    
    # Send email notification if configured
    if command -v mail >/dev/null 2>&1 && [[ -n "${ADMIN_EMAIL:-}" ]]; then
        mail -s "SSH Key Rotation Completed - $(date +%Y-%m-%d)" "$ADMIN_EMAIL" < /tmp/ssh_key_rotation_report.txt
        log_message "Rotation report sent to: $ADMIN_EMAIL"
    fi
    
    log_message "Rotation report generated: /tmp/ssh_key_rotation_report.txt"
}

rollback_rotation() {
    log_message "Rolling back SSH key rotation..."
    
    # Find most recent backup
    latest_backup=$(ls -1t "$BACKUP_DIR" | head -1)
    
    if [[ -n "$latest_backup" ]]; then
        backup_path="$BACKUP_DIR/$latest_backup"
        
        # Restore client keys
        if [[ -f "$backup_path/proxmox_ai_key" ]]; then
            cp "$backup_path/proxmox_ai_key"* ~/.ssh/
            chmod 600 ~/.ssh/proxmox_ai_key
            chmod 644 ~/.ssh/proxmox_ai_key.pub
            log_message "Client keys restored from $backup_path"
        fi
        
        # Restore server keys and authorized_keys
        ssh -i ~/.ssh/proxmox_ai_key -p 2849 root@"$PROXMOX_HOST" "
            if [[ -f /backup/ssh_keys/$latest_backup/ssh_host_rsa_key ]]; then
                cp /backup/ssh_keys/$latest_backup/ssh_host_* /etc/ssh/
                chmod 600 /etc/ssh/ssh_host_*_key
                chmod 644 /etc/ssh/ssh_host_*_key.pub
                systemctl restart ssh
                echo 'Server keys restored'
            fi
            
            if [[ -f /backup/ssh_keys/$latest_backup/authorized_keys ]]; then
                cp /backup/ssh_keys/$latest_backup/authorized_keys /root/.ssh/
                echo 'Authorized keys restored'
            fi
        " 2>&1 | tee -a "$ROTATION_LOG"
        
        log_message "Rollback completed"
    else
        log_message "No backup found for rollback"
        return 1
    fi
}

main() {
    log_message "Starting SSH key rotation process"
    
    # Create necessary directories
    create_key_directories
    
    # Backup existing keys
    backup_existing_keys
    
    # Generate and deploy new client key
    generate_new_client_key
    
    if deploy_new_client_key; then
        # Rotate server host keys
        rotate_server_host_keys
        
        # Activate new client key
        activate_new_client_key
        
        # Update known hosts
        update_known_hosts
        
        # Verify rotation
        if verify_rotation; then
            # Clean up old keys
            cleanup_old_keys
            
            # Send notification
            send_rotation_notification
            
            log_message "SSH key rotation completed successfully"
        else
            log_message "Rotation verification failed, initiating rollback"
            rollback_rotation
            exit 1
        fi
    else
        log_message "New key deployment failed, rotation aborted"
        exit 1
    fi
}

# Handle script interruption
trap 'log_message "SSH key rotation interrupted"; exit 1' INT TERM

# Execute main function
main "$@"
```

### 4. Access Review and Compliance

#### Quarterly Access Review Process

```python
#!/usr/bin/env python3
# Quarterly Access Review System
# File: /scripts/security/access_review.py

import sqlite3
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class AccessReviewItem:
    username: str
    full_name: str
    email: str
    roles: List[str]
    last_login: str
    permissions: List[str]
    risk_score: int
    review_status: str  # 'pending', 'approved', 'revoked', 'modified'
    reviewer: str
    review_date: str
    review_notes: str

class AccessReviewManager:
    def __init__(self, rbac_db_path: str = "/var/lib/security/rbac.db",
                 review_db_path: str = "/var/lib/security/access_reviews.db"):
        self.rbac_db = sqlite3.connect(rbac_db_path)
        self.review_db = sqlite3.connect(review_db_path)
        self._initialize_review_database()
    
    def _initialize_review_database(self):
        """Initialize access review database"""
        cursor = self.review_db.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_period TEXT NOT NULL,
                username TEXT NOT NULL,
                current_roles TEXT, -- JSON array
                current_permissions TEXT, -- JSON array
                last_login TIMESTAMP,
                risk_score INTEGER,
                review_status TEXT DEFAULT 'pending',
                reviewer TEXT,
                review_date TIMESTAMP,
                review_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_periods (
                period TEXT PRIMARY KEY,
                start_date DATE,
                end_date DATE,
                total_users INTEGER,
                reviewed_users INTEGER,
                revoked_users INTEGER,
                modified_users INTEGER,
                status TEXT DEFAULT 'active', -- 'active', 'completed'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.review_db.commit()
    
    def initiate_quarterly_review(self) -> str:
        """Initiate a new quarterly access review"""
        review_period = f"Q{((datetime.now().month - 1) // 3) + 1}_{datetime.now().year}"
        
        # Get all active users and their access
        rbac_cursor = self.rbac_db.cursor()
        rbac_cursor.execute("""
            SELECT u.username, u.full_name, u.email, u.last_login,
                   GROUP_CONCAT(ur.role_name) as roles
            FROM users u
            LEFT JOIN user_roles ur ON u.username = ur.username 
                AND ur.is_active = TRUE
                AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
            WHERE u.is_active = TRUE
            GROUP BY u.username, u.full_name, u.email, u.last_login
        """)
        
        users_data = rbac_cursor.fetchall()
        
        review_cursor = self.review_db.cursor()
        
        # Create review period record
        review_cursor.execute("""
            INSERT OR REPLACE INTO review_periods 
            (period, start_date, end_date, total_users, reviewed_users, revoked_users, modified_users)
            VALUES (?, ?, ?, ?, 0, 0, 0)
        """, (
            review_period,
            datetime.now().date(),
            (datetime.now() + timedelta(days=30)).date(),
            len(users_data)
        ))
        
        # Create review items for each user
        for username, full_name, email, last_login, roles in users_data:
            # Get user permissions
            permissions = self._get_user_permissions_summary(username)
            
            # Calculate risk score
            risk_score = self._calculate_user_risk_score(username, last_login, roles)
            
            review_cursor.execute("""
                INSERT INTO access_reviews 
                (review_period, username, current_roles, current_permissions, 
                 last_login, risk_score, review_status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """, (
                review_period,
                username,
                json.dumps(roles.split(',') if roles else []),
                json.dumps(permissions),
                last_login,
                risk_score
            ))
        
        self.review_db.commit()
        
        return review_period
    
    def _get_user_permissions_summary(self, username: str) -> List[str]:
        """Get summary of user permissions"""
        rbac_cursor = self.rbac_db.cursor()
        rbac_cursor.execute("""
            SELECT r.permissions 
            FROM users u
            JOIN user_roles ur ON u.username = ur.username
            JOIN roles r ON ur.role_name = r.name
            WHERE u.username = ? AND u.is_active = TRUE AND ur.is_active = TRUE 
            AND r.is_active = TRUE
            AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
        """, (username,))
        
        permissions_summary = set()
        for (permissions_json,) in rbac_cursor.fetchall():
            permissions = json.loads(permissions_json)
            for perm in permissions:
                resource_type = perm['resource_type']
                access_level = perm['access_level']
                permissions_summary.add(f"{resource_type}:{access_level}")
        
        return list(permissions_summary)
    
    def _calculate_user_risk_score(self, username: str, last_login: str, roles: str) -> int:
        """Calculate risk score for user"""
        risk_score = 0
        
        # Base score for active user
        risk_score += 1
        
        # Risk based on roles
        if roles:
            role_list = roles.split(',')
            if 'system_admin' in role_list:
                risk_score += 5
            elif 'infrastructure_operator' in role_list:
                risk_score += 3
            elif 'security_auditor' in role_list:
                risk_score += 2
        
        # Risk based on last login
        if last_login:
            last_login_date = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
            days_since_login = (datetime.now() - last_login_date.replace(tzinfo=None)).days
            
            if days_since_login > 90:
                risk_score += 4  # Inactive user
            elif days_since_login > 30:
                risk_score += 2  # Infrequent user
        else:
            risk_score += 5  # Never logged in
        
        # Check for suspicious activity
        rbac_cursor = self.rbac_db.cursor()
        rbac_cursor.execute("""
            SELECT COUNT(*) FROM access_logs 
            WHERE username = ? AND result = 'denied' 
            AND timestamp > datetime('now', '-30 days')
        """, (username,))
        
        denied_attempts = rbac_cursor.fetchone()[0]
        if denied_attempts > 10:
            risk_score += 3
        elif denied_attempts > 5:
            risk_score += 1
        
        return min(risk_score, 10)  # Cap at 10
    
    def generate_review_report(self, review_period: str) -> Dict[str, Any]:
        """Generate access review report"""
        cursor = self.review_db.cursor()
        
        # Get review period info
        cursor.execute("""
            SELECT * FROM review_periods WHERE period = ?
        """, (review_period,))
        
        period_info = cursor.fetchone()
        if not period_info:
            raise ValueError(f"Review period {review_period} not found")
        
        # Get review items
        cursor.execute("""
            SELECT * FROM access_reviews WHERE review_period = ?
            ORDER BY risk_score DESC, username
        """, (review_period,))
        
        review_items = []
        for row in cursor.fetchall():
            review_items.append({
                'username': row[2],
                'current_roles': json.loads(row[3]),
                'current_permissions': json.loads(row[4]),
                'last_login': row[5],
                'risk_score': row[6],
                'review_status': row[7],
                'reviewer': row[8],
                'review_date': row[9],
                'review_notes': row[10]
            })
        
        # Calculate statistics
        total_users = len(review_items)
        pending_reviews = sum(1 for item in review_items if item['review_status'] == 'pending')
        approved_reviews = sum(1 for item in review_items if item['review_status'] == 'approved')
        revoked_reviews = sum(1 for item in review_items if item['review_status'] == 'revoked')
        modified_reviews = sum(1 for item in review_items if item['review_status'] == 'modified')
        
        # High-risk users
        high_risk_users = [item for item in review_items if item['risk_score'] >= 7]
        
        return {
            'review_period': review_period,
            'period_start': period_info[2],
            'period_end': period_info[3],
            'statistics': {
                'total_users': total_users,
                'pending_reviews': pending_reviews,
                'approved_reviews': approved_reviews,
                'revoked_reviews': revoked_reviews,
                'modified_reviews': modified_reviews,
                'completion_percentage': round((total_users - pending_reviews) / total_users * 100, 2) if total_users > 0 else 0
            },
            'high_risk_users': high_risk_users,
            'review_items': review_items,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_review_worksheet(self, review_period: str, output_path: str) -> str:
        """Export review worksheet for managers"""
        report = self.generate_review_report(review_period)
        
        # Create CSV file for review
        csv_path = f"{output_path}/access_review_{review_period}.csv"
        
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = [
                'Username', 'Roles', 'Permissions', 'Last Login', 'Risk Score',
                'Review Status', 'Reviewer', 'Review Date', 'Review Notes'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in report['review_items']:
                writer.writerow({
                    'Username': item['username'],
                    'Roles': ', '.join(item['current_roles']),
                    'Permissions': ', '.join(item['current_permissions']),
                    'Last Login': item['last_login'] or 'Never',
                    'Risk Score': item['risk_score'],
                    'Review Status': item['review_status'],
                    'Reviewer': item['reviewer'] or '',
                    'Review Date': item['review_date'] or '',
                    'Review Notes': item['review_notes'] or ''
                })
        
        return csv_path
    
    def process_review_decisions(self, review_period: str, csv_file: str) -> Dict[str, int]:
        """Process review decisions from completed worksheet"""
        results = {'approved': 0, 'revoked': 0, 'modified': 0, 'errors': 0}
        
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            cursor = self.review_db.cursor()
            
            for row in reader:
                username = row['Username']
                review_status = row['Review Status'].lower()
                reviewer = row['Reviewer']
                review_notes = row['Review Notes']
                
                if review_status in ['approved', 'revoked', 'modified']:
                    # Update review record
                    cursor.execute("""
                        UPDATE access_reviews 
                        SET review_status = ?, reviewer = ?, review_date = CURRENT_TIMESTAMP,
                            review_notes = ?
                        WHERE review_period = ? AND username = ?
                    """, (review_status, reviewer, review_notes, review_period, username))
                    
                    # Process access changes
                    if review_status == 'revoked':
                        self._revoke_user_access(username, reviewer, review_notes)
                        results['revoked'] += 1
                    elif review_status == 'modified':
                        # Handle modifications based on notes
                        self._modify_user_access(username, reviewer, review_notes)
                        results['modified'] += 1
                    else:
                        results['approved'] += 1
                else:
                    results['errors'] += 1
            
            self.review_db.commit()
        
        # Update review period statistics
        cursor.execute("""
            UPDATE review_periods 
            SET reviewed_users = (
                SELECT COUNT(*) FROM access_reviews 
                WHERE review_period = ? AND review_status != 'pending'
            ),
            revoked_users = (
                SELECT COUNT(*) FROM access_reviews 
                WHERE review_period = ? AND review_status = 'revoked'
            ),
            modified_users = (
                SELECT COUNT(*) FROM access_reviews 
                WHERE review_period = ? AND review_status = 'modified'
            )
            WHERE period = ?
        """, (review_period, review_period, review_period, review_period))
        
        self.review_db.commit()
        
        return results
    
    def _revoke_user_access(self, username: str, revoked_by: str, reason: str):
        """Revoke all access for a user"""
        rbac_cursor = self.rbac_db.cursor()
        
        # Deactivate user
        rbac_cursor.execute("""
            UPDATE users SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        """, (username,))
        
        # Deactivate role assignments
        rbac_cursor.execute("""
            UPDATE user_roles SET is_active = FALSE
            WHERE username = ?
        """, (username,))
        
        self.rbac_db.commit()
        
        # Log the action
        rbac_cursor.execute("""
            INSERT INTO access_logs (username, resource_type, resource_id, access_level, 
                                   action, result, reason, timestamp)
            VALUES (?, 'user', ?, 'admin', 'revoke_access', 'granted', ?, CURRENT_TIMESTAMP)
        """, (revoked_by, username, f"Access revoked during review: {reason}"))
        
        self.rbac_db.commit()
    
    def _modify_user_access(self, username: str, modified_by: str, notes: str):
        """Modify user access based on review notes"""
        # This would implement specific modification logic based on notes
        # For now, just log the modification request
        rbac_cursor = self.rbac_db.cursor()
        
        rbac_cursor.execute("""
            INSERT INTO access_logs (username, resource_type, resource_id, access_level, 
                                   action, result, reason, timestamp)
            VALUES (?, 'user', ?, 'admin', 'modify_access', 'granted', ?, CURRENT_TIMESTAMP)
        """, (modified_by, username, f"Access modification requested: {notes}"))
        
        self.rbac_db.commit()
    
    def generate_compliance_summary(self, review_period: str) -> Dict[str, Any]:
        """Generate compliance summary for audit"""
        report = self.generate_review_report(review_period)
        
        cursor = self.review_db.cursor()
        cursor.execute("""
            SELECT period, start_date, end_date, total_users, reviewed_users, 
                   revoked_users, modified_users, status
            FROM review_periods 
            WHERE period = ?
        """, (review_period,))
        
        period_data = cursor.fetchone()
        
        compliance_summary = {
            'review_period': review_period,
            'review_dates': {
                'start_date': period_data[1],
                'end_date': period_data[2]
            },
            'compliance_metrics': {
                'total_users_reviewed': period_data[4],
                'total_users': period_data[3],
                'review_completion_rate': round(period_data[4] / period_data[3] * 100, 2) if period_data[3] > 0 else 0,
                'access_revocations': period_data[5],
                'access_modifications': period_data[6],
                'approval_rate': round((period_data[4] - period_data[5] - period_data[6]) / period_data[4] * 100, 2) if period_data[4] > 0 else 0
            },
            'risk_management': {
                'high_risk_users_identified': len([u for u in report['review_items'] if u['risk_score'] >= 7]),
                'inactive_users_found': len([u for u in report['review_items'] if not u['last_login']]),
                'excessive_privileges_found': len([u for u in report['review_items'] if 'system_admin' in u['current_roles']])
            },
            'recommendations': [],
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate recommendations
        if compliance_summary['compliance_metrics']['review_completion_rate'] < 100:
            compliance_summary['recommendations'].append("Complete pending access reviews")
        
        if compliance_summary['risk_management']['high_risk_users_identified'] > 0:
            compliance_summary['recommendations'].append("Review and mitigate high-risk user access")
        
        if compliance_summary['risk_management']['inactive_users_found'] > 0:
            compliance_summary['recommendations'].append("Disable or remove inactive user accounts")
        
        return compliance_summary

def main():
    review_manager = AccessReviewManager()
    
    # Initiate quarterly review
    review_period = review_manager.initiate_quarterly_review()
    print(f"Initiated access review for period: {review_period}")
    
    # Generate review report
    report = review_manager.generate_review_report(review_period)
    print(f"Review report generated - {report['statistics']['total_users']} users to review")
    
    # Export worksheet
    worksheet_path = review_manager.export_review_worksheet(review_period, "/tmp")
    print(f"Review worksheet exported: {worksheet_path}")
    
    # Generate compliance summary
    compliance = review_manager.generate_compliance_summary(review_period)
    print(f"Compliance summary generated - {compliance['compliance_metrics']['review_completion_rate']:.1f}% completion rate")

if __name__ == "__main__":
    main()
```

## Compliance and Audit Requirements

### 1. CIS Controls Implementation

**Control 5: Account Management**
- Inventory of all accounts
- Disable dormant accounts
- Regular access reviews
- Automated account lifecycle management

**Control 6: Access Control Management**
- Centralized access control policy
- Multi-factor authentication
- Regular access certification
- Privileged account management

### 2. Access Control Metrics

```python
# Key Performance Indicators for Access Control
ACCESS_CONTROL_METRICS = {
    "authentication_success_rate": "> 99.5%",
    "mfa_adoption_rate": "> 95%",
    "access_review_completion_rate": "100%",
    "privileged_account_monitoring": "100%",
    "average_access_request_time": "< 4 hours",
    "access_violation_incidents": "0 per month"
}
```

### 3. Audit Trail Requirements

- All authentication attempts logged
- All authorization decisions recorded
- All privilege escalations tracked
- All administrative actions audited
- Log integrity protection implemented
- Regular log review and analysis

---

**Classification**: Confidential - Access Control Procedures
**Last Updated**: 2025-07-29
**Review Schedule**: Quarterly
**Approved By**: Security Team Lead
**Document Version**: 1.0