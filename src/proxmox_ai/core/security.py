"""
Secure credential management and encryption utilities.

This module provides secure storage and retrieval of sensitive credentials
using industry-standard encryption and system keyring integration.
"""

import base64
import getpass
import os
import secrets
from pathlib import Path
from typing import Dict, Optional, Any

import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel, Field, SecretStr
import structlog

logger = structlog.get_logger(__name__)


class CredentialError(Exception):
    """Raised when credential operations fail."""
    pass


class SecureCredentials(BaseModel):
    """Secure credential storage model."""
    
    service_name: str = Field(..., description="Service identifier")
    username: str = Field(..., description="Username")
    password: SecretStr = Field(..., description="Encrypted password")
    host: Optional[str] = Field(None, description="Host address")
    port: Optional[int] = Field(None, description="Port number")
    additional_data: Dict[str, Any] = Field(default_factory=dict)


class CredentialManager:
    """
    Secure credential management with encryption and keyring integration.
    
    Provides methods to securely store, retrieve, and manage credentials
    using system keyring and Fernet encryption for additional security.
    """
    
    def __init__(self, app_name: str = "proxmox-ai-assistant"):
        self.app_name = app_name
        self._encryption_key: Optional[bytes] = None
        self._setup_encryption()
        
        logger.info("Credential manager initialized", app_name=app_name)
    
    def _setup_encryption(self) -> None:
        """Initialize encryption key from keyring or create new one."""
        try:
            # Try to get existing encryption key from keyring
            key_b64 = keyring.get_password(self.app_name, "encryption_key")
            
            if key_b64:
                self._encryption_key = base64.urlsafe_b64decode(key_b64)
                logger.debug("Retrieved existing encryption key from keyring")
            else:
                # Generate new encryption key
                self._encryption_key = Fernet.generate_key()
                key_b64 = base64.urlsafe_b64encode(self._encryption_key).decode()
                
                # Store in keyring
                keyring.set_password(self.app_name, "encryption_key", key_b64)
                logger.info("Generated and stored new encryption key")
                
        except Exception as e:
            logger.error("Failed to setup encryption", error=str(e))
            raise CredentialError(f"Failed to initialize encryption: {e}")
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption/decryption."""
        if not self._encryption_key:
            raise CredentialError("Encryption not initialized")
        return Fernet(self._encryption_key)
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def store_credentials(
        self,
        service_name: str,
        username: str,
        password: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Securely store credentials with encryption.
        
        Args:
            service_name: Unique identifier for the service
            username: Username for authentication
            password: Password (will be encrypted)
            host: Optional host address
            port: Optional port number
            additional_data: Optional additional secure data
            
        Returns:
            bool: True if credentials stored successfully
            
        Raises:
            CredentialError: If storage fails
        """
        try:
            fernet = self._get_fernet()
            
            # Encrypt password
            encrypted_password = fernet.encrypt(password.encode())
            encrypted_password_b64 = base64.urlsafe_b64encode(encrypted_password).decode()
            
            # Create credential object
            credentials = SecureCredentials(
                service_name=service_name,
                username=username,
                password=SecretStr(encrypted_password_b64),
                host=host,
                port=port,
                additional_data=additional_data or {}
            )
            
            # Store in keyring as JSON
            credential_data = credentials.model_dump(mode='json')
            # Remove password from JSON, store separately
            credential_data.pop('password', None)
            
            # Store metadata in keyring
            keyring.set_password(
                self.app_name,
                f"{service_name}_metadata",
                str(credential_data)
            )
            
            # Store encrypted password separately
            keyring.set_password(
                self.app_name,
                f"{service_name}_password",
                encrypted_password_b64
            )
            
            logger.info(
                "Credentials stored successfully",
                service_name=service_name,
                username=username,
                has_host=bool(host)
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to store credentials",
                service_name=service_name,
                error=str(e)
            )
            raise CredentialError(f"Failed to store credentials: {e}")
    
    def get_credentials(self, service_name: str) -> Optional[SecureCredentials]:
        """
        Retrieve and decrypt stored credentials.
        
        Args:
            service_name: Service identifier
            
        Returns:
            SecureCredentials: Decrypted credentials or None if not found
            
        Raises:
            CredentialError: If retrieval or decryption fails
        """
        try:
            # Get metadata
            metadata_str = keyring.get_password(self.app_name, f"{service_name}_metadata")
            if not metadata_str:
                logger.debug("No credentials found", service_name=service_name)
                return None
            
            # Get encrypted password
            encrypted_password_b64 = keyring.get_password(
                self.app_name,
                f"{service_name}_password"
            )
            if not encrypted_password_b64:
                logger.error("Password not found for service", service_name=service_name)
                return None
            
            # Parse metadata
            import ast
            metadata = ast.literal_eval(metadata_str)
            
            # Decrypt password
            fernet = self._get_fernet()
            encrypted_password = base64.urlsafe_b64decode(encrypted_password_b64)
            decrypted_password = fernet.decrypt(encrypted_password).decode()
            
            # Reconstruct credentials
            credentials = SecureCredentials(
                service_name=metadata['service_name'],
                username=metadata['username'],
                password=SecretStr(decrypted_password),
                host=metadata.get('host'),
                port=metadata.get('port'),
                additional_data=metadata.get('additional_data', {})
            )
            
            logger.debug(
                "Credentials retrieved successfully",
                service_name=service_name,
                username=credentials.username
            )
            return credentials
            
        except Exception as e:
            logger.error(
                "Failed to retrieve credentials",
                service_name=service_name,
                error=str(e)
            )
            raise CredentialError(f"Failed to retrieve credentials: {e}")
    
    def delete_credentials(self, service_name: str) -> bool:
        """
        Delete stored credentials.
        
        Args:
            service_name: Service identifier
            
        Returns:
            bool: True if deletion successful
        """
        try:
            # Delete metadata
            keyring.delete_password(self.app_name, f"{service_name}_metadata")
            
            # Delete password
            keyring.delete_password(self.app_name, f"{service_name}_password")
            
            logger.info("Credentials deleted successfully", service_name=service_name)
            return True
            
        except keyring.errors.PasswordDeleteError:
            logger.warning("Credentials not found for deletion", service_name=service_name)
            return False
        except Exception as e:
            logger.error(
                "Failed to delete credentials",
                service_name=service_name,
                error=str(e)
            )
            return False
    
    def list_services(self) -> list[str]:
        """
        List all stored service names.
        
        Returns:
            list[str]: List of service names
        """
        # Note: keyring doesn't provide a direct way to list all keys
        # This is a simplified implementation
        # In production, you might want to maintain a separate index
        services = []
        
        # This is a placeholder - actual implementation would depend on
        # keyring backend and might require additional metadata storage
        logger.info("Listed credential services", count=len(services))
        return services
    
    def prompt_for_credentials(
        self,
        service_name: str,
        username_prompt: str = "Username",
        password_prompt: str = "Password",
        host_prompt: Optional[str] = None,
        port_prompt: Optional[str] = None
    ) -> SecureCredentials:
        """
        Interactively prompt user for credentials and store them.
        
        Args:
            service_name: Service identifier
            username_prompt: Prompt text for username
            password_prompt: Prompt text for password  
            host_prompt: Optional prompt text for host
            port_prompt: Optional prompt text for port
            
        Returns:
            SecureCredentials: The entered credentials
        """
        try:
            print(f"\n🔐 Enter credentials for {service_name}")
            
            username = input(f"{username_prompt}: ").strip()
            if not username:
                raise CredentialError("Username cannot be empty")
            
            password = getpass.getpass(f"{password_prompt}: ")
            if not password:
                raise CredentialError("Password cannot be empty")
            
            host = None
            port = None
            
            if host_prompt:
                host_input = input(f"{host_prompt} (optional): ").strip()
                host = host_input if host_input else None
            
            if port_prompt:
                port_input = input(f"{port_prompt} (optional): ").strip()
                try:
                    port = int(port_input) if port_input else None
                except ValueError:
                    raise CredentialError("Port must be a number")
            
            # Store credentials
            self.store_credentials(
                service_name=service_name,
                username=username,
                password=password,
                host=host,
                port=port
            )
            
            # Return credentials (password will be decrypted)
            return self.get_credentials(service_name)
            
        except KeyboardInterrupt:
            logger.info("Credential input cancelled by user")
            raise CredentialError("Credential input cancelled")
        except Exception as e:
            logger.error("Failed to prompt for credentials", error=str(e))
            raise CredentialError(f"Failed to get credentials: {e}")


def get_or_prompt_credentials(
    service_name: str,
    force_prompt: bool = False,
    **prompt_kwargs
) -> SecureCredentials:
    """
    Get credentials from storage or prompt user if not found.
    
    Args:
        service_name: Service identifier
        force_prompt: Force prompting even if credentials exist
        **prompt_kwargs: Arguments passed to prompt_for_credentials
        
    Returns:
        SecureCredentials: Retrieved or entered credentials
    """
    credential_manager = CredentialManager()
    
    if not force_prompt:
        credentials = credential_manager.get_credentials(service_name)
        if credentials:
            logger.debug("Using stored credentials", service_name=service_name)
            return credentials
    
    logger.info("Prompting for new credentials", service_name=service_name)
    return credential_manager.prompt_for_credentials(service_name, **prompt_kwargs)