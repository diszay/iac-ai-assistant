# 🚀 Quick Start Guide - Proxmox AI Infrastructure Assistant

**Get your local AI-powered infrastructure automation running in minutes!**

This guide will help you start the Proxmox AI Assistant and begin automating your infrastructure with intelligent recommendations and Terraform/Ansible generation.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Proxmox VE Server** running and accessible (IP: YOUR_PROXMOX_HOST or your IP)
- [ ] **Python 3.12+** installed on your system
- [ ] **Ollama** installed for local AI models
- [ ] **4GB+ RAM** available for AI model operation
- [ ] **Network access** to your Proxmox server
- [ ] **SSH access** configured for Proxmox

## ⚡ One-Command Quick Start

```bash
# Clone, setup, and start the assistant in one command
curl -fsSL https://raw.githubusercontent.com/your-repo/proxmox-ai-assistant/main/scripts/quick-start.sh | bash
```

## 🔧 Manual Setup (Recommended for Learning)

### Step 1: Install Ollama (Local AI Engine)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### Step 2: Download Optimal AI Model

The assistant will automatically detect your hardware and download the best model:

```bash
# Let the assistant choose the optimal model for your hardware
# This happens automatically on first run, or manually:
python -c "
from src.proxmox_ai.core.hardware_detector import hardware_detector
rec = hardware_detector.get_model_recommendation()
print(f'Recommended model: {rec.model_name}')
print(f'Download command: ollama pull {rec.model_name}')
"

# Alternative: Download a specific model based on your RAM
# For 4-8GB RAM (Basic):
ollama pull llama3.2:3b-instruct-q4_0

# For 8-16GB RAM (Good):
ollama pull llama3.1:8b-instruct-q4_0

# For 16GB+ RAM (Best):
ollama pull llama3.1:8b-instruct-q8_0
```

### Step 3: Install the Proxmox AI Assistant

```bash
# Clone the repository
git clone https://github.com/your-username/proxmox-ai-assistant.git
cd proxmox-ai-assistant

# Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the application
pip install -e .

# Verify installation
proxmox-ai --version
```

### Step 4: Configure the Assistant

```bash
# Initialize configuration
proxmox-ai config init

# Configure Proxmox connection
proxmox-ai config set proxmox.host "YOUR_PROXMOX_HOST"
proxmox-ai config set proxmox.user "root@pam"
proxmox-ai config set proxmox.port "8006"

# Configure authentication (choose one method):

# Method A: API Token (Recommended)
proxmox-ai config set proxmox.api_token_id "root@pam!terraform"
proxmox-ai config set proxmox.api_token_secret "your-api-token-here"

# Method B: Password (Less secure)
proxmox-ai config set proxmox.password "your-password-here"

# Configure AI settings (optional - auto-detected)
proxmox-ai config set ai.model "llama3.1:8b-instruct-q4_0"
proxmox-ai config set ai.skill_level "intermediate"
```

### Step 5: Test the Setup

```bash
# Run health check
proxmox-ai doctor

# Test AI integration
proxmox-ai ai-status

# Test Proxmox connection
proxmox-ai vm list

# Start interactive mode
proxmox-ai chat
```

## 🎯 First Use Examples

### Example 1: Generate a Simple Web Server

```bash
# Interactive conversation
proxmox-ai chat

# Then type any of these phrases:
"Create a Ubuntu web server with 2GB RAM and nginx"
"I need a simple web server for development"
"Deploy a LAMP stack with basic security"
"Set up a WordPress hosting environment"
```

### Example 2: Generate Terraform Infrastructure

```bash
# Command-line generation
proxmox-ai generate terraform "Create 3 Ubuntu servers for a development cluster with load balancer"

# Or interactively
proxmox-ai chat
# Then: "Generate terraform code for a Kubernetes cluster with 3 nodes"
```

### Example 3: Get Infrastructure Recommendations

```bash
# Ask for best practices
proxmox-ai chat
# Then: "What are the security best practices for production VMs?"
# Or: "How should I configure networking for a multi-tier application?"
# Or: "Optimize my existing terraform configuration for better performance"
```

## 🤖 Understanding the AI Conversation System

The assistant understands natural language and adapts to your skill level:

### Beginner Phrases:
- "I'm new to this, help me create a simple server"
- "What is the best way to set up a VM?"
- "Can you explain how to deploy infrastructure step by step?"

### Intermediate Phrases:
- "Generate terraform for a scalable web application"
- "Create an Ansible playbook for server hardening"
- "Set up monitoring for my infrastructure"

### Expert Phrases:
- "Deploy a highly available Kubernetes cluster with persistent storage"
- "Implement zero-downtime rolling updates with service mesh"
- "Configure advanced network policies and security groups"

## 🛠️ Key Commands Reference

### System Management
```bash
proxmox-ai status          # Overall system health
proxmox-ai doctor          # Comprehensive diagnostics
proxmox-ai config list     # Show all configuration
proxmox-ai hardware-info   # Hardware analysis and recommendations
```

### AI Interaction
```bash
proxmox-ai chat                    # Interactive conversation mode
proxmox-ai ask "your question"     # Quick question
proxmox-ai generate terraform "description"  # Generate Terraform
proxmox-ai generate ansible "description"    # Generate Ansible
```

### Infrastructure Operations
```bash
proxmox-ai vm list                 # List VMs
proxmox-ai vm create --help        # VM creation options
proxmox-ai templates list          # Available templates
proxmox-ai security-scan           # Security assessment
```

## 🔧 Troubleshooting Common Issues

### Issue: "Local AI model not available"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve &

# Check if model is downloaded
ollama list

# Download model if missing
ollama pull llama3.1:8b-instruct-q4_0
```

### Issue: "Cannot connect to Proxmox"
```bash
# Test connection manually
curl -k https://YOUR_PROXMOX_HOST:8006/api2/json/version

# Check configuration
proxmox-ai config get proxmox.host
proxmox-ai config get proxmox.user

# Test with verbose output
proxmox-ai vm list --debug
```

### Issue: "Memory issues with AI model"
```bash
# Check hardware recommendations
proxmox-ai hardware-info

# Switch to smaller model
proxmox-ai config set ai.model "llama3.2:3b-instruct-q4_0"

# Monitor resource usage
proxmox-ai performance-stats
```

### Issue: "Permission denied"
```bash
# Check API token permissions in Proxmox web interface
# Token needs: VM.Allocate, VM.Config, VM.Monitor, Datastore.Allocate

# Or use password authentication temporarily
proxmox-ai config set proxmox.password "your-password"
```

## 🎓 Learning Path

### Week 1: Basics
1. Set up the environment following this guide
2. Practice basic VM operations with the assistant
3. Learn infrastructure concepts through conversations
4. Generate simple Terraform configurations

### Week 2: Intermediate
1. Create multi-VM environments
2. Implement basic security hardening
3. Use Ansible for configuration management
4. Set up monitoring and logging

### Week 3: Advanced
1. Deploy production-ready clusters
2. Implement CI/CD pipelines
3. Advanced networking and security
4. Performance optimization and scaling

## 🔗 Next Steps

- **Read the Full Documentation**: [docs/README.md](docs/README.md)
- **Explore Templates**: [config/templates/](config/templates/)
- **Join the Community**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Contribute**: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🆘 Getting Help

### Interactive Help
```bash
proxmox-ai chat
# Then ask: "How do I [your question]?"
```

### Documentation
```bash
proxmox-ai --help
proxmox-ai vm --help
proxmox-ai generate --help
```

### Community Support
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and community support
- Documentation: Comprehensive guides and tutorials

---

**🎉 You're ready to start automating your infrastructure with AI!**

Begin with: `proxmox-ai chat` and tell the assistant what you want to build.