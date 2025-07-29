# GitOps Setup and Configuration Guide

## Overview

This document provides complete setup instructions for the Proxmox Infrastructure GitOps system, including version control, configuration management, and automated deployment workflows.

## Prerequisites

- Python 3.8+
- Git configured with your credentials
- Proxmox VE access (192.168.1.50)
- GitHub account and repository access

## Quick Setup

Run the automated setup script:

```bash
python3 scripts/setup_gitops.py
```

## Manual Setup Steps

### 1. Configure Git

```bash
git config --global user.name "diszay"
git config --global user.email "disisaiah@gmail.com"
```

### 2. Initialize Credentials

```python
from config.gitops.credentials import GitOpsCredentialManager

# Initialize with master password
cred_manager = GitOpsCredentialManager('your_master_password')

# Store credentials
cred_manager.initialize_credentials(
    proxmox_root_password='[PROXMOX_ROOT_PASSWORD]',
    github_token='your_github_token'
)
```

### 3. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `iac-ai-assistant`
3. Description: "Proxmox Infrastructure as Code AI Assistant with GitOps workflow"
4. Set visibility (public/private)
5. Create repository

### 4. Push Code to GitHub

```bash
git remote add origin https://github.com/diszay/iac-ai-assistant.git
git push -u origin main
```

### 5. Configure GitHub Secrets

In your repository settings, add these secrets:

- `PROXMOX_PASSWORD`: Your Proxmox root password
- `MASTER_PASSWORD`: Master password for credential encryption
- `SLACK_WEBHOOK_URL`: (Optional) For drift notifications

## GitOps Workflow Components

### 1. Credential Management (`config/gitops/credentials.py`)

Secure, encrypted storage for sensitive credentials:

- Proxmox root password
- GitHub tokens
- SSH keys
- PBKDF2 key derivation with 100,000 iterations
- AES-256 encryption using Fernet

### 2. Configuration Drift Detection (`src/proxmox_ai/gitops/drift_detector.py`)

Monitors infrastructure for unauthorized changes:

- VM configuration monitoring
- Network settings validation
- Storage configuration checks
- User permission auditing
- Automatic baseline creation
- Severity-based alerting

### 3. Workflow Orchestrator (`src/proxmox_ai/gitops/workflow_orchestrator.py`)

Manages deployment workflows:

- Multi-environment deployments (dev/staging/prod)
- Validation and testing pipelines
- Backup creation before changes
- Post-deployment verification
- Rollback capabilities

### 4. GitHub Actions Workflows

#### Deployment Pipeline (`.github/workflows/gitops-deployment.yml`)

- Triggered on push to main branches
- Validation and security scanning
- Environment-specific deployments
- Manual approval for production
- Post-deployment verification

#### Drift Monitoring (`.github/workflows/drift-monitoring.yml`)

- Runs every 15 minutes
- Detects configuration drift
- Creates issues for critical drift
- Auto-remediation for low-severity issues
- Monitoring dashboard updates

## Usage Examples

### Deploy to Development

```bash
# Automatic deployment on push to develop branch
git checkout develop
git push origin develop
```

### Manual Deployment

```bash
python -m src.proxmox_ai.gitops.workflow_orchestrator \
  --action deploy \
  --environment production \
  --branch main \
  --config config/config.yaml
```

### Drift Detection

```bash
# One-time drift check
python -m src.proxmox_ai.gitops.drift_detector --action detect

# Create baseline
python -m src.proxmox_ai.gitops.drift_detector --action baseline

# Continuous monitoring
python -m src.proxmox_ai.gitops.drift_detector --action monitor
```

### Credential Management

```python
from config.gitops.credentials import GitOpsCredentialManager

# Initialize with master password
cred_manager = GitOpsCredentialManager('master_password')

# Store new credential
cred_manager.store_credential('api_key', 'secret_value')

# Retrieve credential
api_key = cred_manager.retrieve_credential('api_key')

# List all credentials
credentials = cred_manager.list_credentials()
```

## Security Features

### Encryption
- All credentials encrypted with AES-256
- Key derivation using PBKDF2 with salt
- Secure file permissions (600)

### Access Control
- Master password required for credential access
- Environment-specific deployment controls
- Manual approval for production deployments

### Audit Trail
- All changes tracked in Git
- Deployment logs and artifacts
- Configuration drift reports
- Security scan results

## Monitoring and Alerting

### Configuration Drift
- Real-time drift detection
- Severity-based classification
- Automatic GitHub issue creation
- Slack notifications (configurable)

### Deployment Monitoring
- Health checks post-deployment
- Performance validation
- Security scanning
- Rollback triggers

## Directory Structure

```
iac-ai-assistant/
├── config/
│   ├── gitops/
│   │   ├── credentials.py          # Encrypted credential management
│   │   └── workflow.yaml           # GitOps workflow configuration
│   ├── secrets/                    # Encrypted credential storage
│   └── baselines/                  # Configuration baselines
├── src/proxmox_ai/gitops/
│   ├── __init__.py
│   ├── drift_detector.py           # Configuration drift detection
│   └── workflow_orchestrator.py    # Deployment orchestration
├── .github/workflows/
│   ├── gitops-deployment.yml       # Deployment pipeline
│   └── drift-monitoring.yml        # Continuous monitoring
├── scripts/
│   └── setup_gitops.py            # Automated setup script
├── logs/                          # Drift reports and logs
└── backups/                       # Infrastructure state backups
```

## Troubleshooting

### Common Issues

1. **Credential Access Errors**
   ```
   Error: Failed to retrieve credential
   ```
   - Verify master password is correct
   - Check credential file permissions (should be 600)
   - Ensure credential was stored properly

2. **Proxmox Connection Issues**
   ```
   Error: Unable to connect to Proxmox cluster
   ```
   - Verify Proxmox host IP (192.168.1.50)
   - Check network connectivity
   - Validate SSL certificate settings

3. **GitHub Actions Failures**
   ```
   Error: Bad credentials
   ```
   - Check GitHub token validity
   - Verify repository secrets configuration
   - Ensure proper permissions on token

4. **Drift Detection Issues**
   ```
   Error: No baseline configuration found
   ```
   - Create initial baseline: `--action baseline`
   - Check baseline file permissions
   - Verify Proxmox connectivity

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support

- Check logs in `logs/` directory
- Review GitHub Actions workflow runs
- Verify configuration in `config/config.yaml`
- Test credential access with debug script

## Best Practices

### Security
- Rotate credentials regularly (90 days)
- Use strong master passwords (16+ characters)
- Review access logs periodically
- Keep GitOps workflows updated

### Operations
- Test deployments in development first
- Create baselines after major changes
- Monitor drift detection alerts
- Backup before production deployments

### Maintenance
- Update Python dependencies regularly
- Review and update security policies
- Clean up old backup files
- Audit user permissions quarterly

## Version Information

- GitOps Workflow Version: 1.0.0
- Python Version: 3.11+
- Proxmox API Version: 2.0
- GitHub Actions Version: 4.0