#!/usr/bin/env python3
"""
Secure Credential Management System for GitOps
Encrypts and manages sensitive credentials for Proxmox infrastructure
"""

import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SecureCredentialManager:
    """Manages encrypted credentials for GitOps operations"""
    
    def __init__(self, master_password: str = None, storage_path: str = None):
        """
        Initialize credential manager with master password
        
        Args:
            master_password: Master password for encryption key derivation
            storage_path: Path to store encrypted credentials
        """
        self.storage_path = Path(storage_path or "config/secrets/credentials.enc")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        if master_password:
            self.key = self._derive_key(master_password.encode())
            self.cipher = Fernet(self.key)
        
    def _derive_key(self, password: bytes) -> bytes:
        """Derive encryption key from master password using PBKDF2"""
        salt = b'proxmox_gitops_salt_2024'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def store_credential(self, name: str, value: str) -> bool:
        """
        Store encrypted credential
        
        Args:
            name: Credential identifier
            value: Credential value to encrypt
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing credentials or create new dict
            credentials = self.load_all_credentials() or {}
            
            # Encrypt and store new credential
            encrypted_value = self.cipher.encrypt(value.encode())
            credentials[name] = base64.urlsafe_b64encode(encrypted_value).decode()
            
            # Write encrypted credentials to file
            encrypted_data = self.cipher.encrypt(json.dumps(credentials).encode())
            
            with open(self.storage_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Set secure file permissions
            os.chmod(self.storage_path, 0o600)
            
            logger.info(f"Credential '{name}' stored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store credential '{name}': {e}")
            return False
    
    def retrieve_credential(self, name: str) -> str:
        """
        Retrieve and decrypt credential
        
        Args:
            name: Credential identifier
            
        Returns:
            Decrypted credential value or None if not found
        """
        try:
            credentials = self.load_all_credentials()
            if not credentials or name not in credentials:
                logger.warning(f"Credential '{name}' not found")
                return None
            
            encrypted_value = base64.urlsafe_b64decode(credentials[name])
            decrypted_value = self.cipher.decrypt(encrypted_value)
            
            return decrypted_value.decode()
            
        except Exception as e:
            logger.error(f"Failed to retrieve credential '{name}': {e}")
            return None
    
    def load_all_credentials(self) -> dict:
        """Load all encrypted credentials from storage"""
        try:
            if not self.storage_path.exists():
                return {}
            
            with open(self.storage_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return {}
    
    def list_credentials(self) -> list:
        """List all stored credential names"""
        credentials = self.load_all_credentials()
        return list(credentials.keys()) if credentials else []
    
    def delete_credential(self, name: str) -> bool:
        """Delete a stored credential"""
        try:
            credentials = self.load_all_credentials()
            if not credentials or name not in credentials:
                logger.warning(f"Credential '{name}' not found")
                return False
            
            del credentials[name]
            
            # Write updated credentials back
            encrypted_data = self.cipher.encrypt(json.dumps(credentials).encode())
            with open(self.storage_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"Credential '{name}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete credential '{name}': {e}")
            return False


class GitOpsCredentialManager(SecureCredentialManager):
    """Specialized credential manager for GitOps operations"""
    
    def __init__(self, master_password: str = None):
        super().__init__(master_password, "config/secrets/gitops_credentials.enc")
    
    def store_proxmox_root_password(self, password: str) -> bool:
        """Store Proxmox root password securely"""
        return self.store_credential("proxmox_root_password", password)
    
    def get_proxmox_root_password(self) -> str:
        """Retrieve Proxmox root password"""
        return self.retrieve_credential("proxmox_root_password")
    
    def store_github_token(self, token: str) -> bool:
        """Store GitHub personal access token"""
        return self.store_credential("github_token", token)
    
    def get_github_token(self) -> str:
        """Retrieve GitHub personal access token"""
        return self.retrieve_credential("github_token")
    
    def store_ssh_private_key(self, key_content: str) -> bool:
        """Store SSH private key for Git operations"""
        return self.store_credential("ssh_private_key", key_content)
    
    def get_ssh_private_key(self) -> str:
        """Retrieve SSH private key"""
        return self.retrieve_credential("ssh_private_key")
    
    def initialize_credentials(self, proxmox_root_password: str, github_token: str = None) -> bool:
        """Initialize all required credentials"""
        success = True
        
        # Store Proxmox root password
        if not self.store_proxmox_root_password(proxmox_root_password):
            success = False
        
        # Store GitHub token if provided
        if github_token and not self.store_github_token(github_token):
            success = False
        
        return success


def setup_gitops_credentials():
    """Interactive setup for GitOps credentials"""
    print("GitOps Credential Setup")
    print("=" * 30)
    
    # Get master password
    master_password = input("Enter master password for credential encryption: ")
    
    # Initialize credential manager
    cred_manager = GitOpsCredentialManager(master_password)
    
    # Store Proxmox root password
    proxmox_password = os.getenv("PROXMOX_ROOT_PASSWORD", "")  # Load from environment
    if cred_manager.store_proxmox_root_password(proxmox_password):
        print("✓ Proxmox root password stored securely")
    else:
        print("✗ Failed to store Proxmox root password")
    
    # Optionally store GitHub token
    github_token = input("Enter GitHub token (optional, press Enter to skip): ").strip()
    if github_token:
        if cred_manager.store_github_token(github_token):
            print("✓ GitHub token stored securely")
        else:
            print("✗ Failed to store GitHub token")
    
    print("\nCredential setup complete!")
    print(f"Stored credentials: {', '.join(cred_manager.list_credentials())}")


if __name__ == "__main__":
    setup_gitops_credentials()