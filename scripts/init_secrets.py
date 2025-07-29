#!/usr/bin/env python3
"""
Initialize secure credential storage for Proxmox AI Assistant.

This script securely stores the root password and other initial credentials
using encrypted storage.
"""

import sys
import os
from pathlib import Path

# Add src to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from proxmox_ai.core.secrets import get_secret_manager, ProxmoxSecrets
import structlog

logger = structlog.get_logger(__name__)


def main():
    """Initialize secrets with secure storage."""
    
    # Initialize secret manager
    secrets_dir = Path(__file__).parent.parent / "config" / "secrets"
    secret_manager = get_secret_manager(secrets_dir)
    proxmox_secrets = ProxmoxSecrets(secret_manager)
    
    # Store Proxmox root credentials
    print("Initializing Proxmox AI Assistant secure credential storage...")
    
    # Store the root password as specified in the requirements
    root_password = "Cl@uD3D3V"
    proxmox_secrets.set_proxmox_credentials(
        username="root@pam",
        password=root_password,
        host="192.168.1.50"
    )
    
    print("✓ Proxmox root credentials stored securely")
    
    # Create SSH key placeholder (will be generated later)
    # For now, create placeholder entries
    print("Creating SSH key placeholders...")
    
    # These will be replaced with actual generated keys
    ssh_placeholder = {
        "private_key": "# SSH private key will be generated",
        "public_key": "# SSH public key will be generated"
    }
    
    secret_manager.set_secret("ssh_keys_placeholder", ssh_placeholder)
    
    print("✓ SSH key placeholders created")
    
    # Create API key placeholder for Anthropic
    print("Creating API key placeholders...")
    
    # This will be set from environment variable later
    secret_manager.set_secret("anthropic_api_key_placeholder", "# Set from ANTHROPIC_API_KEY environment variable")
    
    print("✓ API key placeholders created")
    
    # Show stored secrets (keys only, not values)
    stored_secrets = secret_manager.list_secrets()
    print(f"\nSecurely stored secrets: {stored_secrets}")
    
    # Set proper file permissions
    secrets_file = secrets_dir / "credentials.enc"
    key_file = secrets_dir / ".master.key"
    
    if secrets_file.exists():
        os.chmod(secrets_file, 0o600)
    if key_file.exists():
        os.chmod(key_file, 0o600)
    
    print("\n✓ Secret storage initialized successfully")
    print(f"Secrets stored in: {secrets_dir}")
    print("All secrets are encrypted at rest with AES-256")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())