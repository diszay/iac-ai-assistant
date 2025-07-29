"""
Secure credential management system for Proxmox AI Assistant.

Provides encrypted storage and retrieval of sensitive configuration data
including passwords, API keys, and certificates using industry-standard
encryption practices.
"""

import os
import json
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import structlog

logger = structlog.get_logger(__name__)


class SecretManager:
    """
    Secure credential management with encrypted storage.
    
    Uses Fernet (AES 128 in CBC mode) with PBKDF2 key derivation for
    encrypting sensitive configuration data.
    """
    
    def __init__(self, secrets_dir: Path, master_key: Optional[str] = None):
        """
        Initialize SecretManager.
        
        Args:
            secrets_dir: Directory to store encrypted secrets
            master_key: Master key for encryption (if None, generates new key)
        """
        self.secrets_dir = Path(secrets_dir)
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        
        self.key_file = self.secrets_dir / ".master.key"
        self.secrets_file = self.secrets_dir / "credentials.enc"
        
        # Initialize encryption key
        if master_key:
            self._key = self._derive_key(master_key.encode())
        else:
            self._key = self._load_or_generate_key()
        
        self._cipher = Fernet(self._key)
        
        logger.info("SecretManager initialized", secrets_dir=str(self.secrets_dir))
    
    def _derive_key(self, password: bytes, salt: bytes = None) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generates if None)
        
        Returns:
            Derived encryption key
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _load_or_generate_key(self) -> bytes:
        """
        Load existing encryption key or generate new one.
        
        Returns:
            Encryption key
        """
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                logger.debug("Loaded existing encryption key")
                return key
            except Exception as e:
                logger.error("Failed to load encryption key", error=str(e))
                raise
        else:
            # Generate new key
            key = Fernet.generate_key()
            try:
                # Write key with restricted permissions
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                os.chmod(self.key_file, 0o600)  # Owner read/write only
                logger.info("Generated new encryption key")
                return key
            except Exception as e:
                logger.error("Failed to save encryption key", error=str(e))
                raise
    
    def _load_secrets(self) -> Dict[str, Any]:
        """
        Load and decrypt secrets from storage.
        
        Returns:
            Dictionary of decrypted secrets
        """
        if not self.secrets_file.exists():
            return {}
        
        try:
            with open(self.secrets_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self._cipher.decrypt(encrypted_data)
            secrets_dict = json.loads(decrypted_data.decode())
            
            logger.debug("Loaded secrets from storage", count=len(secrets_dict))
            return secrets_dict
        
        except Exception as e:
            logger.error("Failed to load secrets", error=str(e))
            raise
    
    def _save_secrets(self, secrets_dict: Dict[str, Any]) -> None:
        """
        Encrypt and save secrets to storage.
        
        Args:
            secrets_dict: Dictionary of secrets to encrypt and save
        """
        try:
            json_data = json.dumps(secrets_dict, indent=2)
            encrypted_data = self._cipher.encrypt(json_data.encode())
            
            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted_data)
            
            os.chmod(self.secrets_file, 0o600)  # Owner read/write only
            
            logger.debug("Saved secrets to storage", count=len(secrets_dict))
        
        except Exception as e:
            logger.error("Failed to save secrets", error=str(e))
            raise
    
    def set_secret(self, key: str, value: Union[str, Dict, Any]) -> None:
        """
        Store encrypted secret.
        
        Args:
            key: Secret identifier
            value: Secret value to encrypt and store
        """
        secrets_dict = self._load_secrets()
        secrets_dict[key] = value
        self._save_secrets(secrets_dict)
        
        logger.info("Secret stored", key=key)
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """
        Retrieve and decrypt secret.
        
        Args:
            key: Secret identifier
            default: Default value if secret not found
        
        Returns:
            Decrypted secret value or default
        """
        secrets_dict = self._load_secrets()
        value = secrets_dict.get(key, default)
        
        if value is not None:
            logger.debug("Secret retrieved", key=key)
        else:
            logger.debug("Secret not found", key=key)
        
        return value
    
    def delete_secret(self, key: str) -> bool:
        """
        Delete secret from storage.
        
        Args:
            key: Secret identifier
        
        Returns:
            True if secret was deleted, False if not found
        """
        secrets_dict = self._load_secrets()
        
        if key in secrets_dict:
            del secrets_dict[key]
            self._save_secrets(secrets_dict)
            logger.info("Secret deleted", key=key)
            return True
        else:
            logger.debug("Secret not found for deletion", key=key)
            return False
    
    def list_secrets(self) -> list:
        """
        List all secret keys (not values).
        
        Returns:
            List of secret keys
        """
        secrets_dict = self._load_secrets()
        keys = list(secrets_dict.keys())
        
        logger.debug("Listed secret keys", count=len(keys))
        return keys
    
    def secret_exists(self, key: str) -> bool:
        """
        Check if secret exists.
        
        Args:
            key: Secret identifier
        
        Returns:
            True if secret exists, False otherwise
        """
        secrets_dict = self._load_secrets()
        exists = key in secrets_dict
        
        logger.debug("Secret existence check", key=key, exists=exists)
        return exists
    
    def rotate_key(self, new_master_key: str) -> None:
        """
        Rotate encryption key and re-encrypt all secrets.
        
        Args:
            new_master_key: New master key for encryption
        """
        # Load current secrets
        old_secrets = self._load_secrets()
        
        # Generate new key
        new_key = self._derive_key(new_master_key.encode())
        new_cipher = Fernet(new_key)
        
        # Re-encrypt all secrets with new key
        json_data = json.dumps(old_secrets, indent=2)
        encrypted_data = new_cipher.encrypt(json_data.encode())
        
        # Save new key and re-encrypted secrets
        with open(self.key_file, 'wb') as f:
            f.write(new_key)
        os.chmod(self.key_file, 0o600)
        
        with open(self.secrets_file, 'wb') as f:
            f.write(encrypted_data)
        os.chmod(self.secrets_file, 0o600)
        
        # Update instance variables
        self._key = new_key
        self._cipher = new_cipher
        
        logger.info("Encryption key rotated successfully")
    
    def export_secrets(self, export_path: Path, include_key: bool = False) -> None:
        """
        Export encrypted secrets for backup.
        
        Args:
            export_path: Path to export secrets
            include_key: Whether to include encryption key (DANGEROUS)
        """
        export_path = Path(export_path)
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Export encrypted secrets
        if self.secrets_file.exists():
            import shutil
            shutil.copy2(self.secrets_file, export_path / "credentials.enc")
        
        # Export key if requested (NOT recommended for production)
        if include_key and self.key_file.exists():
            shutil.copy2(self.key_file, export_path / ".master.key")
            logger.warning("Encryption key exported - SECURITY RISK")
        
        logger.info("Secrets exported", export_path=str(export_path), include_key=include_key)


class ProxmoxSecrets:
    """
    Proxmox-specific secret management wrapper.
    
    Provides convenience methods for managing Proxmox credentials
    and other infrastructure secrets.
    """
    
    def __init__(self, secret_manager: SecretManager):
        """
        Initialize ProxmoxSecrets.
        
        Args:
            secret_manager: SecretManager instance
        """
        self.secret_manager = secret_manager
        logger.debug("ProxmoxSecrets initialized")
    
    def set_proxmox_credentials(self, username: str, password: str, host: str = None) -> None:
        """
        Store Proxmox credentials securely.
        
        Args:
            username: Proxmox username
            password: Proxmox password
            host: Proxmox host (optional)
        """
        credentials = {
            "username": username,
            "password": password
        }
        
        if host:
            credentials["host"] = host
        
        self.secret_manager.set_secret("proxmox_credentials", credentials)
        logger.info("Proxmox credentials stored securely")
    
    def get_proxmox_credentials(self) -> Optional[Dict[str, str]]:
        """
        Retrieve Proxmox credentials.
        
        Returns:
            Dictionary with username/password or None if not found
        """
        return self.secret_manager.get_secret("proxmox_credentials")
    
    def set_anthropic_api_key(self, api_key: str) -> None:
        """
        Store Anthropic API key securely.
        
        Args:
            api_key: Anthropic API key
        """
        self.secret_manager.set_secret("anthropic_api_key", api_key)
        logger.info("Anthropic API key stored securely")
    
    def get_anthropic_api_key(self) -> Optional[str]:
        """
        Retrieve Anthropic API key.
        
        Returns:
            API key or None if not found
        """
        return self.secret_manager.get_secret("anthropic_api_key")
    
    def set_ssh_keys(self, private_key: str, public_key: str) -> None:
        """
        Store SSH key pair securely.
        
        Args:
            private_key: SSH private key
            public_key: SSH public key
        """
        self.secret_manager.set_secret("ssh_private_key", private_key)
        self.secret_manager.set_secret("ssh_public_key", public_key)
        logger.info("SSH keys stored securely")
    
    def get_ssh_keys(self) -> Optional[Dict[str, str]]:
        """
        Retrieve SSH key pair.
        
        Returns:
            Dictionary with private/public keys or None if not found
        """
        private_key = self.secret_manager.get_secret("ssh_private_key")
        public_key = self.secret_manager.get_secret("ssh_public_key")
        
        if private_key and public_key:
            return {
                "private_key": private_key,
                "public_key": public_key
            }
        return None


def get_secret_manager(secrets_dir: Path = None, master_key: str = None) -> SecretManager:
    """
    Get SecretManager instance.
    
    Args:
        secrets_dir: Directory for secrets storage
        master_key: Master encryption key
    
    Returns:
        SecretManager instance
    """
    if secrets_dir is None:
        from .config import get_settings
        settings = get_settings()
        secrets_dir = settings.config_dir / "secrets"
    
    return SecretManager(secrets_dir, master_key)


def get_proxmox_secrets(secret_manager: SecretManager = None) -> ProxmoxSecrets:
    """
    Get ProxmoxSecrets instance.
    
    Args:
        secret_manager: SecretManager instance (creates new if None)
    
    Returns:
        ProxmoxSecrets instance
    """
    if secret_manager is None:
        secret_manager = get_secret_manager()
    
    return ProxmoxSecrets(secret_manager)