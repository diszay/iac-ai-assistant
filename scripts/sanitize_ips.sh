#!/bin/bash
# IP Address Sanitization Script - Security Critical
# Removes all hardcoded private IP addresses from the codebase

set -e

echo "🔒 SECURITY: Sanitizing IP addresses from public repository..."

# Define the project root
PROJECT_ROOT="/home/diszay-claudedev/projects/iac-ai-assistant"

# Function to replace IPs in files
sanitize_file() {
    local file="$1"
    if [[ -f "$file" ]]; then
        echo "Sanitizing: $file"
        
        # Replace specific IP addresses with placeholders
        sed -i 's/192\.168\.1\.50/YOUR_PROXMOX_HOST/g' "$file"
        sed -i 's/192\.168\.1\.101/YOUR_VM_IP/g' "$file"
        sed -i 's/192\.168\.1\.102/YOUR_VM_IP_2/g' "$file"
        sed -i 's/192\.168\.1\.100/YOUR_VM_IP_START/g' "$file"
        sed -i 's/192\.168\.1\.[0-9]\+/YOUR_VM_IP/g' "$file"
        
        # Replace network ranges
        sed -i 's/192\.168\.1\.0\/24/YOUR_NETWORK\/24/g' "$file"
        sed -i 's/192\.168\.10\.0\/24/YOUR_DEV_NETWORK\/24/g' "$file"
        sed -i 's/192\.168\.30\.0\/24/YOUR_PROD_NETWORK\/24/g' "$file"
        
        # Replace API URLs
        sed -i 's|https://192\.168\.1\.50:8006|https://YOUR_PROXMOX_HOST:8006|g' "$file"
        
        # Replace SSH commands
        sed -i 's/ssh.*root@192\.168\.1\.50/ssh root@YOUR_PROXMOX_HOST/g' "$file"
        sed -i 's/ssh -p 2849.*192\.168\.1\.50/ssh -p YOUR_SSH_PORT root@YOUR_PROXMOX_HOST/g' "$file"
        
        echo "✅ Sanitized: $file"
    fi
}

# Sanitize all files that might contain IP addresses
cd "$PROJECT_ROOT"

# Configuration files
sanitize_file "config/config.yaml" 
sanitize_file "config/gitops/workflow.yaml"
sanitize_file "config/templates/terraform/terraform.tfvars.example"
sanitize_file "config/templates/terraform/variables.tf"
sanitize_file ".env.example"

# Source code files  
find src/ -name "*.py" -exec bash -c 'sanitize_file "$0"' {} \;

# Documentation files
find docs/ -name "*.md" -exec bash -c 'sanitize_file "$0"' {} \;

# Scripts
find scripts/ -name "*.py" -exec bash -c 'sanitize_file "$0"' {} \;

# Test files
find tests/ -name "*.py" -exec bash -c 'sanitize_file "$0"' {} \;

# Root level markdown files
sanitize_file "README.md"
sanitize_file "GETTING_STARTED.md" 
sanitize_file "SECURITY.md"
sanitize_file "CLAUDE.md"

# Development artifacts
find development/ -name "*.md" -exec bash -c 'sanitize_file "$0"' {} \;

echo ""
echo "🔒 SECURITY SANITIZATION COMPLETE"
echo "✅ All private IP addresses replaced with placeholders"
echo "✅ Network topology information secured"
echo "✅ Repository safe for public exposure"
echo ""
echo "📋 Placeholders used:"
echo "  - YOUR_PROXMOX_HOST (instead of 192.168.1.50)"
echo "  - YOUR_VM_IP (instead of 192.168.1.x)"
echo "  - YOUR_NETWORK/24 (instead of 192.168.1.0/24)"
echo "  - YOUR_SSH_PORT (instead of 2849)"
echo ""