# GitHub Actions Workflow Setup

## Overview

This repository includes comprehensive GitHub Actions workflows for automated testing, security scanning, and GitOps deployment. Due to GitHub's security restrictions, workflows require specific Personal Access Token (PAT) permissions.

## Current Status

✅ **Active Workflows:**
- `local-ai-ci.yml` - Local AI testing and security pipeline

⏳ **Pending Workflows** (require PAT with `workflow` scope):
- `drift-monitoring.yml` - Infrastructure drift detection
- `gitops-deployment.yml` - Automated deployment pipeline

## Setup Instructions

### 1. Update Personal Access Token

To enable all workflows, update your PAT with the following scopes:

**Required Scopes:**
- `repo` - Full repository access
- `workflow` - Workflow management
- `read:org` - Organization access (if applicable)

**Steps:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Edit your existing token or create a new one
3. Select the `workflow` scope in addition to existing permissions
4. Update the token in your repository secrets

### 2. Add Remaining Workflows

Once your PAT has the `workflow` scope:

```bash
# Copy workflows from the workflows_to_add directory
cp workflows_to_add/*.yml .github/workflows/

# Commit and push
git add .github/workflows/
git commit -m "Add remaining GitOps workflows"
git push origin main
```

### 3. Verify Workflow Execution

After adding workflows, verify they run correctly:

1. Check the Actions tab in your GitHub repository
2. Monitor workflow runs for any failures
3. Review security scan results and test coverage

## Workflow Details

### Local AI CI Pipeline (`local-ai-ci.yml`)

**Features:**
- Security compliance scanning with Bandit and Safety
- Local AI functionality testing with Ollama
- Hardware detection and model optimization tests
- Package building and deployment readiness checks
- Comprehensive test coverage reporting

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual dispatch

### Drift Monitoring (`drift-monitoring.yml`)

**Features:**
- Continuous monitoring of infrastructure configuration
- Automated drift detection and alerting
- Configuration compliance validation
- Remediation workflow triggers

### GitOps Deployment (`gitops-deployment.yml`)

**Features:**
- Multi-environment deployment pipeline
- Infrastructure as Code validation
- Security-first deployment practices
- Rollback capabilities

## Security Considerations

### Token Security
- Never expose PAT tokens in commits or workflows
- Use GitHub repository secrets for sensitive data
- Regularly rotate access tokens
- Monitor token usage and access logs

### Workflow Security
- All workflows follow security-first principles
- Secrets are properly masked in logs
- Limited scope permissions where possible
- Regular security scanning enabled

## Troubleshooting

### Common Issues

**Workflow Creation Failed:**
```
refusing to allow a Personal Access Token to create or update workflow
```
**Solution:** Update PAT with `workflow` scope

**Ollama Tests Failing:**
```
Connection refused to localhost:11434
```
**Solution:** Workflows automatically handle Ollama installation and startup

**Security Scan Warnings:**
Review the security reports and address any findings before deployment

## Manual Workflow Execution

You can manually trigger workflows using:

```bash
# Trigger deployment workflow
gh workflow run gitops-deployment.yml --ref main

# Trigger CI pipeline
gh workflow run local-ai-ci.yml --ref main
```

## Contributing

When adding new workflows:

1. Follow security-first principles
2. Include comprehensive testing
3. Document any new requirements
4. Test in development branches first

## Support

For workflow-related issues:

1. Check the Actions tab for detailed logs
2. Review this setup guide
3. Verify PAT permissions
4. Check repository settings

---

**Note:** This system maintains a security-first approach with local AI processing and comprehensive audit trails for all operations.