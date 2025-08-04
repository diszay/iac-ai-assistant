# 📋 Command Cheat Sheet - Proxmox AI Assistant

## 🐧 Ubuntu Copy-Paste Commands

**Most Used Commands for Ubuntu Users:**

```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant

# Activate virtual environment
source venv/bin/activate

# Start the AI assistant
python -m src.proxmox_ai.cli.main

# Common operations
python -m src.proxmox_ai.cli.main ai chat          # Interactive chat
python -m src.proxmox_ai.cli.main ai status        # Check status  
python -m src.proxmox_ai.cli.main vm list          # List VMs
python -m src.proxmox_ai.cli.main doctor           # Health check
```

## 🚀 One-Line Installers

```bash
# Complete setup in one command
curl -fsSL https://raw.githubusercontent.com/diszay/iac-ai-assistant/main/scripts/express-install.sh | bash

# Manual clone and install (Ubuntu)
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/diszay/iac-ai-assistant.git && cd iac-ai-assistant
python3.12 -m venv venv && source venv/bin/activate && pip install -e .
```

## 📊 System Status Commands

| Ubuntu Command | Description | Example Output |
|---------------|-------------|----------------|
| `cd ~/projects/iac-ai-assistant && source venv/bin/activate && python -m src.proxmox_ai.cli.main status` | Quick health check | ✅ All systems operational |
| `python -m src.proxmox_ai.cli.main doctor` | Comprehensive diagnostics | ✅ 8/8 checks passed |
| `python -m src.proxmox_ai.cli.main --version` | Show version info | v1.0.0 |
| `python -m src.proxmox_ai.cli.main hardware-info` | Hardware analysis | 16GB RAM, 8 cores detected |
| `python -m src.proxmox_ai.cli.main config list` | Show all settings | proxmox.host=192.168.1.50 |

## 🤖 AI Interaction Commands

### Basic AI Commands - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# AI interaction commands
python -m src.proxmox_ai.cli.main ai chat                                    # Interactive conversation
python -m src.proxmox_ai.cli.main ai ask "your question"                     # Quick question  
python -m src.proxmox_ai.cli.main ai ask "How do I create a web server?"     # Specific help
```

### Generate Infrastructure - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Infrastructure generation
python -m src.proxmox_ai.cli.main ai generate terraform "description"        # Generate Terraform
python -m src.proxmox_ai.cli.main ai generate ansible "description"          # Generate Ansible
python -m src.proxmox_ai.cli.main ai generate docker "description"           # Generate Docker Compose
```

### Code Analysis - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Code analysis commands
python -m src.proxmox_ai.cli.main ai explain config.tf                       # Explain configuration
python -m src.proxmox_ai.cli.main ai optimize config.tf                      # Optimize configuration
python -m src.proxmox_ai.cli.main ai security-review config.tf               # Security analysis
python -m src.proxmox_ai.cli.main ai validate config.tf                      # Validate syntax
python -m src.proxmox_ai.cli.main ai fix config.tf                          # Auto-fix issues
```

## 🖥️ VM Management Commands

### VM Information - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# VM information commands
python -m src.proxmox_ai.cli.main vm list                                 # List all VMs
python -m src.proxmox_ai.cli.main vm info 101                            # VM details
python -m src.proxmox_ai.cli.main vm status 101                          # VM status only
python -m src.proxmox_ai.cli.main vm config 101                          # VM configuration
```

### VM Control - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# VM control commands
python -m src.proxmox_ai.cli.main vm start 101                           # Start VM
python -m src.proxmox_ai.cli.main vm stop 101                            # Stop VM
python -m src.proxmox_ai.cli.main vm restart 101                         # Restart VM
python -m src.proxmox_ai.cli.main vm shutdown 101                        # Graceful shutdown
python -m src.proxmox_ai.cli.main vm reset 101                           # Hard reset
```

### VM Creation and Management
```bash
proxmox-ai vm create config.tf                    # Create from Terraform
proxmox-ai vm create config.json                  # Create from JSON
proxmox-ai vm clone 101 201                       # Clone VM 101 to 201
proxmox-ai vm template 101                        # Convert to template
proxmox-ai vm destroy 101                         # Delete VM (careful!)
```

## ⚙️ Configuration Commands

### Basic Configuration - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Configuration commands
python -m src.proxmox_ai.cli.main config init                            # Initialize config
python -m src.proxmox_ai.cli.main config show                            # Show current config
python -m src.proxmox_ai.cli.main config test                            # Test connections
python -m src.proxmox_ai.cli.main config reset                           # Reset to defaults
```

### Set Configuration Values - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Set configuration values
python -m src.proxmox_ai.cli.main config set proxmox.host "192.168.1.50"
python -m src.proxmox_ai.cli.main config set proxmox.port "8006"
python -m src.proxmox_ai.cli.main config set proxmox.user "root@pam"
python -m src.proxmox_ai.cli.main config set proxmox.password "your-password"
python -m src.proxmox_ai.cli.main config set proxmox.api_token "your-token"
python -m src.proxmox_ai.cli.main config set ai.skill_level "intermediate"
python -m src.proxmox_ai.cli.main config set ai.model "llama3.1:8b-instruct-q4_0"
```

### Get Configuration Values - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Get configuration values
python -m src.proxmox_ai.cli.main config get proxmox.host               # Get specific value
python -m src.proxmox_ai.cli.main config get ai.skill_level             # Get skill level
python -m src.proxmox_ai.cli.main config get ai.model                   # Get current model
```

## 🧠 AI Model Management

### Model Information
```bash
proxmox-ai ai-status                              # Check AI service
proxmox-ai ai models                              # List available models
proxmox-ai ai models --remote                     # List downloadable models
proxmox-ai ai benchmark                           # Performance test
```

### Model Operations
```bash
proxmox-ai ai optimize                            # Auto-optimize for hardware
proxmox-ai ai switch-model llama3.1:8b-q4_0     # Switch to specific model
proxmox-ai ai download llama3.2:3b-q4_0         # Download new model
proxmox-ai ai remove llama3.2:3b-q4_0           # Remove model
```

### Performance Commands
```bash
proxmox-ai ai stats                               # Performance statistics
proxmox-ai ai memory-usage                       # Memory consumption
proxmox-ai ai cache-stats                        # Cache performance
proxmox-ai ai warm-up                            # Pre-warm model
```

## 🔒 Security Commands

### Security Analysis
```bash
proxmox-ai security-scan                          # Scan infrastructure
proxmox-ai security-review config.tf             # Review configuration
proxmox-ai security-report                       # Generate security report
proxmox-ai security-audit                        # Full security audit
```

### Access Management  
```bash
proxmox-ai auth test                              # Test authentication
proxmox-ai auth tokens                            # List API tokens
proxmox-ai auth create-token "token-name"        # Create new token
proxmox-ai auth revoke-token "token-name"        # Revoke token
```

## 📝 Template and Example Commands

### Template Management
```bash
proxmox-ai templates list                         # List templates
proxmox-ai templates show web-server              # Show template
proxmox-ai templates create my-template config.tf # Create template
proxmox-ai templates delete my-template           # Delete template
```

### Examples and Learning
```bash
proxmox-ai examples list                          # List examples
proxmox-ai examples terraform                     # Terraform examples
proxmox-ai examples ansible                       # Ansible examples
proxmox-ai tutorial basic-vm                      # Run tutorial
proxmox-ai workshop beginner                      # Interactive workshop
```

## 📊 Monitoring and Logs

### System Monitoring
```bash
proxmox-ai monitor                                # Real-time monitoring
proxmox-ai metrics                                # System metrics
proxmox-ai performance                            # Performance stats
proxmox-ai resources                              # Resource usage
```

### Logging
```bash
proxmox-ai logs                                   # View recent logs
proxmox-ai logs --error                           # Error logs only
proxmox-ai logs --follow                          # Follow log output
proxmox-ai logs --clear                           # Clear logs
```

## 🔧 Maintenance Commands

### Updates and Maintenance
```bash
proxmox-ai update                                 # Update application
proxmox-ai update --check                         # Check for updates
proxmox-ai cleanup                                # Cleanup temporary files
proxmox-ai cache clear                            # Clear cache
proxmox-ai backup config                          # Backup configuration
proxmox-ai restore config backup.tar             # Restore configuration
```

### Diagnostics
```bash
proxmox-ai diagnose                               # Run diagnostics
proxmox-ai test-connection                        # Test Proxmox connection
proxmox-ai test-ai                                # Test AI functionality
proxmox-ai debug --verbose                        # Verbose debugging
```

## 🎯 Skill Level Commands

### Beginner Level - Ubuntu Terminal
```bash
# Navigate to project and activate environment first
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Beginner commands
python -m src.proxmox_ai.cli.main config set ai.skill_level beginner
python -m src.proxmox_ai.cli.main ai generate terraform "simple web server" --skill beginner
python -m src.proxmox_ai.cli.main ai explain config.tf --skill beginner --detailed
python -m src.proxmox_ai.cli.main ai ask "what is a virtual machine" --skill beginner
```

### Intermediate Level (Default)
```bash
proxmox-ai config set ai.skill_level intermediate
proxmox-ai generate terraform "web app with database" --skill intermediate
proxmox-ai optimize config.tf --skill intermediate
proxmox-ai security-review config.tf --skill intermediate
```

### Expert Level
```bash
proxmox-ai config set ai.skill_level expert
proxmox-ai generate terraform "HA kubernetes cluster" --skill expert
proxmox-ai analyze infrastructure/ --skill expert
proxmox-ai design-review architecture.tf --skill expert
```

## 🚀 Quick Generation Templates

### Web Servers
```bash
proxmox-ai generate terraform "nginx web server, 2GB RAM, ubuntu 22.04"
proxmox-ai generate terraform "apache web server with SSL, 4GB RAM"
proxmox-ai generate terraform "nodejs app server with load balancer"
```

### Database Servers
```bash
proxmox-ai generate terraform "postgresql database, 8GB RAM, 100GB storage"
proxmox-ai generate terraform "mysql cluster with replication"
proxmox-ai generate terraform "redis cache server, 4GB RAM"
```

### Development Environments
```bash
proxmox-ai generate terraform "development cluster, 3 nodes, docker"
proxmox-ai generate terraform "CI/CD environment with jenkins"
proxmox-ai generate terraform "testing environment with monitoring"
```

### Complex Infrastructures
```bash
proxmox-ai generate terraform "3-tier web application with load balancer"
proxmox-ai generate terraform "kubernetes cluster, 3 masters, 5 workers"
proxmox-ai generate terraform "monitoring stack with prometheus and grafana"
```

## 📱 Command Aliases and Shortcuts

### Useful Aliases
```bash
# Add to your .bashrc or .zshrc
alias pai='proxmox-ai'
alias pai-chat='proxmox-ai chat'
alias pai-status='proxmox-ai status'
alias pai-doctor='proxmox-ai doctor'
alias pai-gen='proxmox-ai generate terraform'
alias pai-vm='proxmox-ai vm list'
```

### Quick Status Check
```bash
# One-liner system check
proxmox-ai status && proxmox-ai ai-status && echo "All systems ready!"

# Quick VM overview
proxmox-ai vm list | head -10

# Fast generation
pai-gen "ubuntu server" && echo "Generated successfully!"
```

## 🔄 Pipeline and Automation Commands

### Batch Operations
```bash
# Generate multiple configurations
for app in web api db; do
  proxmox-ai generate terraform "$app server" --output "$app.tf"
done

# Validate all configurations
find . -name "*.tf" -exec proxmox-ai validate {} \;

# Apply multiple configurations (use with caution)
for config in *.tf; do
  proxmox-ai vm create "$config"
done
```

### CI/CD Integration
```bash
# Non-interactive mode for scripts
proxmox-ai generate terraform "web server" --output web.tf --no-interactive
proxmox-ai validate web.tf --format json
proxmox-ai security-review web.tf --format json --fail-on-critical
```

## 🚨 Emergency Commands

### Quick Diagnostics
```bash
# Emergency health check
proxmox-ai doctor --quick

# Test basic connectivity
proxmox-ai test-connection --timeout 10

# Check if AI is responding
proxmox-ai ask "test" --timeout 30
```

### Recovery Commands
```bash
# Reset everything
proxmox-ai config reset --force
proxmox-ai cache clear --all
proxmox-ai ai restart

# Backup before major changes
proxmox-ai backup config --timestamp
proxmox-ai backup templates --timestamp
```

## 💡 Pro Tips and Tricks

### Performance Optimization
```bash
# Enable caching for faster responses
proxmox-ai config set ai.cache_enabled true

# Use faster model for quick tasks
proxmox-ai ai switch-model llama3.2:3b-instruct-q4_0

# Pre-warm model for faster first response
proxmox-ai ai warm-up
```

### Workflow Optimization
```bash
# Save frequently used commands
echo "proxmox-ai generate terraform 'web server with 4GB RAM'" > ~/quick-web.sh
chmod +x ~/quick-web.sh

# Create configuration templates
mkdir ~/.proxmox-ai/templates
proxmox-ai generate terraform "base server" --output ~/.proxmox-ai/templates/base.tf
```

### Learning Shortcuts
```bash
# Quick learning session
proxmox-ai chat --topic "infrastructure basics"

# Get help for any concept
proxmox-ai ask "explain [concept] in simple terms"

# Practice with examples  
proxmox-ai examples terraform --interactive
```

---

## 📞 Help and Support

### Get Help for Any Command
```bash
proxmox-ai --help                    # General help
proxmox-ai generate --help           # Command-specific help
proxmox-ai vm --help                 # Subcommand help
```

### Interactive Help
```bash
proxmox-ai chat
# Then ask: "How do I [your question]?"
```

### Documentation Links
- Full Documentation: `docs/`
- Troubleshooting: `docs/troubleshooting/common-issues.md`
- User Guides: `docs/user-guides/`
- API Reference: `docs/api/`

---

**🎯 Remember**: When in doubt, use `proxmox-ai chat` for interactive help!

**Document Version**: 1.0  
**Last Updated**: 2025-07-30  
**Cheat Sheet for**: Proxmox AI Infrastructure Assistant