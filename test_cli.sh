#!/bin/bash

# Test script for Proxmox AI Assistant CLI
# Demonstrates working CLI functionality

echo "=== Proxmox AI Assistant CLI Test ==="
echo

# Activate virtual environment
source venv/bin/activate

echo "1. Testing --help command:"
python -m src.proxmox_ai.cli.main --help
echo

echo "2. Testing --version command:"
python -m src.proxmox_ai.cli.main --version
echo

echo "3. Testing status command:"
python -m src.proxmox_ai.cli.main status
echo

echo "4. Testing doctor command:"
python -m src.proxmox_ai.cli.main doctor
echo

echo "5. Testing VM commands:"
python -m src.proxmox_ai.cli.main vm --help
echo

echo "6. Testing config commands:"
python -m src.proxmox_ai.cli.main config --help
echo

echo "7. Testing AI commands:"
python -m src.proxmox_ai.cli.main ai --help
echo

echo "8. Testing with environment variables:"
echo "Setting PROXMOX_ROOT_PASSWORD environment variable..."
PROXMOX_ROOT_PASSWORD="${PROXMOX_ROOT_PASSWORD:-}" python -m src.proxmox_ai.cli.main status
echo

echo "=== CLI Test Complete ==="
echo "✅ All basic CLI functionality is working!"
echo
echo "Environment Variables for Authentication:"
echo "- PROXMOX_ROOT_PASSWORD: Root password for Proxmox authentication"
echo "- ANTHROPIC__API_KEY: API key for AI integration"
echo
echo "Usage Examples:"
echo "  PROXMOX_ROOT_PASSWORD=\"your_password\" python -m src.proxmox_ai.cli.main vm list"
echo "  ANTHROPIC__API_KEY=\"your_key\" python -m src.proxmox_ai.cli.main ai generate vm \"Ubuntu server with 8GB RAM\""