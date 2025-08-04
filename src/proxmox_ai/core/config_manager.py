#!/usr/bin/env python3
"""
Secure Configuration Manager for Proxmox Infrastructure
Handles encrypted configuration storage and credential management
"""

import os
import yaml
import json
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dataclasses import dataclass, asdict
import hashlib
import datetime

@dataclass
class ProxmoxCredentials:
    """Proxmox API credentials"""
    host: str
    user: str
    password: str
    token_id: Optional[str] = None
    token_secret: Optional[str] = None
    verify_ssl: bool = True

@dataclass
class ConfigurationChange:
    """Configuration change audit record"""
    timestamp: str
    user: str
    component: str
    action: str
    old_value_hash: str
    new_value_hash: str
    description: str

class SecureConfigManager:
    """Secure configuration management with encryption and audit trails"""
    
    def __init__(self, config_dir: str = "/config"):
        self.config_dir = Path(config_dir)
        self.secrets_dir = self.config_dir / "secrets"
        self.audit_log = self.config_dir / "audit.log"
        self.master_config_file = self.config_dir / "config.yaml"
        
        # Ensure directories exist
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.audit_log),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption system"""
        key_file = self.secrets_dir / "master.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            # Generate new encryption key
            self.encryption_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.encryption_key)
            # Restrict permissions
            os.chmod(key_file, 0o600)
        
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return base64.b64encode(
            self.cipher.encrypt(data.encode())
        ).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(
            base64.b64decode(encrypted_data.encode())
        ).decode()
    
    def load_config(self) -> Dict[str, Any]:
        """Load main configuration file"""
        if not self.master_config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.master_config_file}")
        
        with open(self.master_config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def save_config(self, config: Dict[str, Any], user: str = "system"):
        """Save configuration with audit trail"""
        # Create backup of existing config
        if self.master_config_file.exists():
            backup_file = self.master_config_file.with_suffix(
                f".backup.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            self.master_config_file.rename(backup_file)
        
        # Save new configuration
        with open(self.master_config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        # Log configuration change
        self._audit_log(
            user=user,
            component="main_config",
            action="update",
            description="Configuration file updated"
        )
    
    def store_credentials(self, credentials: ProxmoxCredentials, environment: str = "production"):
        """Store encrypted credentials"""
        creds_file = self.secrets_dir / f"{environment}_credentials.enc"
        
        # Encrypt credentials
        creds_data = asdict(credentials)
        encrypted_creds = self.encrypt_data(json.dumps(creds_data))
        
        with open(creds_file, 'w') as f:
            f.write(encrypted_creds)
        
        # Restrict permissions
        os.chmod(creds_file, 0o600)
        
        self._audit_log(
            user="system",
            component="credentials",
            action="store",
            description=f"Credentials stored for environment: {environment}"
        )
    
    def load_credentials(self, environment: str = "production") -> ProxmoxCredentials:
        """Load and decrypt credentials"""
        creds_file = self.secrets_dir / f"{environment}_credentials.enc"
        
        if not creds_file.exists():
            raise FileNotFoundError(f"Credentials file not found: {creds_file}")
        
        with open(creds_file, 'r') as f:
            encrypted_creds = f.read()
        
        # Decrypt credentials
        creds_data = json.loads(self.decrypt_data(encrypted_creds))
        return ProxmoxCredentials(**creds_data)
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for specific environment"""
        env_config_file = self.config_dir / "environments" / environment / "config.yaml"
        
        if env_config_file.exists():
            with open(env_config_file, 'r') as f:
                env_config = yaml.safe_load(f)
        else:
            env_config = {}
        
        # Merge with base configuration
        base_config = self.load_config()
        
        # Deep merge configurations
        return self._deep_merge(base_config, env_config)
    
    def _deep_merge(self, base: Dict, overlay: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _audit_log(self, user: str, component: str, action: str, 
                   description: str, old_value: str = "", new_value: str = ""):
        """Log configuration changes for audit trail"""
        change = ConfigurationChange(
            timestamp=datetime.datetime.now().isoformat(),
            user=user,
            component=component,
            action=action,
            old_value_hash=hashlib.sha256(old_value.encode()).hexdigest() if old_value else "",
            new_value_hash=hashlib.sha256(new_value.encode()).hexdigest() if new_value else "",
            description=description
        )
        
        self.logger.info(
            f"AUDIT: {change.timestamp} | {user} | {component} | {action} | {description}"
        )
        
        # Store detailed audit record
        audit_file = self.secrets_dir / "audit_trail.json"
        audit_records = []
        
        if audit_file.exists():
            with open(audit_file, 'r') as f:
                audit_records = json.load(f)
        
        audit_records.append(asdict(change))
        
        with open(audit_file, 'w') as f:
            json.dump(audit_records, f, indent=2)
        
        # Restrict permissions
        os.chmod(audit_file, 0o600)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration integrity"""
        validation_results = {
            "status": "success",
            "errors": [],
            "warnings": [],
            "config_hash": "",
            "last_validated": datetime.datetime.now().isoformat()
        }
        
        try:
            # Load and validate main config
            config = self.load_config()
            
            # Required sections validation
            required_sections = [
                "proxmox", "vm_templates", "backup",
                "cloud_init", "network", "security"
            ]
            
            for section in required_sections:
                if section not in config:
                    validation_results["errors"].append(
                        f"Missing required configuration section: {section}"
                    )
            
            # Validate Proxmox connection settings
            if "proxmox" in config:
                proxmox_config = config["proxmox"]
                if "host" not in proxmox_config:
                    validation_results["errors"].append(
                        "Proxmox host not configured"
                    )
            
            # Calculate configuration hash
            config_str = yaml.dump(config, sort_keys=True)
            validation_results["config_hash"] = hashlib.sha256(
                config_str.encode()
            ).hexdigest()
            
            if validation_results["errors"]:
                validation_results["status"] = "error"
            elif validation_results["warnings"]:
                validation_results["status"] = "warning"
            
        except Exception as e:
            validation_results["status"] = "error"
            validation_results["errors"].append(f"Configuration validation failed: {str(e)}")
        
        return validation_results
    
    def rotate_encryption_key(self, user: str = "system"):
        """Rotate encryption key and re-encrypt all secrets"""
        self.logger.info("Starting encryption key rotation")
        
        # Generate new key
        new_key = Fernet.generate_key()
        new_cipher = Fernet(new_key)
        
        # Re-encrypt all secret files
        for secret_file in self.secrets_dir.glob("*.enc"):
            try:
                # Decrypt with old key
                with open(secret_file, 'r') as f:
                    old_encrypted = f.read()
                decrypted_data = self.decrypt_data(old_encrypted)
                
                # Encrypt with new key
                new_encrypted = base64.b64encode(
                    new_cipher.encrypt(decrypted_data.encode())
                ).decode()
                
                # Write back
                with open(secret_file, 'w') as f:
                    f.write(new_encrypted)
                
                self.logger.info(f"Re-encrypted: {secret_file.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to re-encrypt {secret_file.name}: {str(e)}")
                raise
        
        # Update master key
        key_file = self.secrets_dir / "master.key"
        with open(key_file, 'wb') as f:
            f.write(new_key)
        
        # Update cipher
        self.encryption_key = new_key
        self.cipher = new_cipher
        
        self._audit_log(
            user=user,
            component="encryption",
            action="key_rotation",
            description="Encryption key rotated successfully"
        )
        
        self.logger.info("Encryption key rotation completed successfully")

def main():
    """Example usage of SecureConfigManager"""
    config_manager = SecureConfigManager("/home/diszay-claudedev/projects/iac-ai-assistant/config")
    
    # Example: Store Proxmox credentials
    credentials = ProxmoxCredentials(
        host="192.168.1.50",
        user="root@pam",
        password="[PROXMOX_ROOT_PASSWORD]",  # This should come from environment variable
        verify_ssl=True
    )
    
    config_manager.store_credentials(credentials, "production")
    
    # Validate configuration
    validation = config_manager.validate_configuration()
    print(f"Configuration validation: {validation['status']}")
    
    if validation["errors"]:
        for error in validation["errors"]:
            print(f"ERROR: {error}")

if __name__ == "__main__":
    main()