# 🚀 Getting Started with Proxmox AI Infrastructure Assistant

Welcome to the **Proxmox AI Infrastructure Assistant** - your complete solution for local AI-powered infrastructure automation. This guide will walk you through everything you need to get started, from installation to your first infrastructure deployment.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Basic Usage](#basic-usage)
6. [Skill Level Guide](#skill-level-guide)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

## 🎯 Prerequisites

### System Requirements

**Minimum Requirements:**
- **OS**: Linux, macOS, or Windows
- **RAM**: 4GB (8GB recommended)
- **Storage**: 10GB free space
- **CPU**: 2+ cores (4+ cores recommended)

**Recommended for Optimal Performance:**
- **RAM**: 8GB+ (for better AI model performance)
- **CPU**: 4+ cores with good single-thread performance
- **Storage**: SSD with 20GB+ free space
- **Network**: Stable connection for initial model downloads

### Software Dependencies

1. **Python 3.12+**
   ```bash
   # Check your Python version
   python3 --version
   
   # If you need to install Python 3.12+
   # Ubuntu/Debian:
   sudo apt update && sudo apt install python3.12 python3.12-venv
   
   # macOS (with Homebrew):
   brew install python@3.12
   
   # Windows: Download from python.org
   ```

2. **Git** (for cloning the repository)
   ```bash
   # Ubuntu/Debian:
   sudo apt install git
   
   # macOS:
   git --version  # Usually pre-installed
   
   # Windows: Download from git-scm.com
   ```

3. **Ollama** (Local AI Model Server)
   ```bash
   # Linux/macOS:
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows: Download from ollama.ai
   ```

### Proxmox Environment

You'll need access to a **Proxmox VE** server:
- Proxmox VE 7.0+ installed and running
- Administrative access (root or equivalent)
- Network connectivity to the Proxmox host
- HTTPS/SSL enabled (recommended)

## 🔧 Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/diszay/iac-ai-assistant.git
cd iac-ai-assistant

# Verify you're in the right directory
ls -la
# You should see: README.md, src/, docs/, requirements.txt, etc.
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
# venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
which python  # Should point to venv/bin/python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(typer|rich|proxmoxer)"
```

### Step 4: Set Up Ollama and AI Models

```bash
# Start Ollama service
ollama serve

# In a new terminal, download recommended AI model
ollama pull codellama:7b-instruct-q4_0

# Verify model installation
ollama list
```

## ⚙️ Configuration

### Step 1: Environment Variables

Create your environment configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the configuration file
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```bash
# Proxmox Configuration
PROXMOX__HOST=your-proxmox-ip-or-hostname
PROXMOX__PORT=8006
PROXMOX__USER=root@pam
PROXMOX__VERIFY_SSL=true
PROXMOX_ROOT_PASSWORD=your_proxmox_password

# Local AI Configuration
LOCAL_AI__MODEL_NAME=codellama:7b-instruct-q4_0
LOCAL_AI__OLLAMA_HOST=http://localhost:11434
LOCAL_AI__SKILL_LEVEL=intermediate

# Security
MASTER_PASSWORD=your_secure_master_password_for_encryption
```

### Step 2: Verify Configuration

```bash
# Test your configuration
python -m src.proxmox_ai.cli.main doctor

# Check AI model availability
python -m src.proxmox_ai.cli.main ai status
```

### Step 3: Hardware Optimization

Run the hardware detection to optimize for your system:

```bash
# Detect and optimize for your hardware
python -m src.proxmox_ai.cli.main ai optimize-models

# View hardware recommendations
python -m src.proxmox_ai.cli.main ai benchmark
```

## 🎮 First Run

### Step 1: Verify Installation

```bash
# Check if everything is working
python -m src.proxmox_ai.cli.main --help

# Expected output: CLI help with all available commands
```

### Step 2: System Status Check

```bash
# Check system status
python -m src.proxmox_ai.cli.main status

# You should see:
# ✓ Application: Running
# ✓ Configuration: Loaded
# ✓ Proxmox VE: Connected (if configured)
# ✓ AI Integration: Available
# ✓ Credentials: Secure
```

### Step 3: Test AI Generation

```bash
# Generate your first infrastructure code
python -m src.proxmox_ai.cli.main ai generate terraform \
  "Simple web server with Ubuntu 22.04" \
  --skill beginner

# This should generate Terraform configuration for a basic VM
```

## 🛠️ Basic Usage

### Common Commands

```bash
# System Information
python -m src.proxmox_ai.cli.main info          # Detailed system info
python -m src.proxmox_ai.cli.main status        # Quick status check
python -m src.proxmox_ai.cli.main doctor        # Health diagnostics

# AI Code Generation
python -m src.proxmox_ai.cli.main ai generate terraform "description" --skill level
python -m src.proxmox_ai.cli.main ai generate ansible "description" --skill level
python -m src.proxmox_ai.cli.main ai optimize "existing-config.tf"

# VM Management (when Proxmox is configured)
python -m src.proxmox_ai.cli.main vm list       # List all VMs
python -m src.proxmox_ai.cli.main vm status 100 # Check VM 100 status
python -m src.proxmox_ai.cli.main vm create "config.json"

# Configuration Management
python -m src.proxmox_ai.cli.main config show   # Show current config
python -m src.proxmox_ai.cli.main config test   # Test connections
```

### Example Workflows

**1. Generate a Simple Web Server:**
```bash
python -m src.proxmox_ai.cli.main ai generate terraform \
  "Ubuntu 22.04 web server with nginx, 2GB RAM, 20GB disk" \
  --skill beginner
```

**2. Create an Ansible Playbook:**
```bash
python -m src.proxmox_ai.cli.main ai generate ansible \
  "Install Docker and configure firewall" \
  --skill intermediate
```

**3. Optimize Existing Configuration:**
```bash
python -m src.proxmox_ai.cli.main ai optimize ./my-terraform-config.tf
```

## 🎓 Skill Level Guide

### Beginner Level
- **Focus**: Learning and safety
- **Features**: Simple configurations, detailed explanations, guided workflows
- **Best For**: New to IaC, learning Proxmox, first-time users

```bash
# Beginner examples
python -m src.proxmox_ai.cli.main ai generate terraform \
  "Basic Ubuntu server" --skill beginner

# Generates: Simple configuration with comments explaining each part
```

### Intermediate Level  
- **Focus**: Production-ready configurations
- **Features**: Best practices, moderate complexity, reusable templates
- **Best For**: Some IaC experience, building production systems

```bash
# Intermediate examples
python -m src.proxmox_ai.cli.main ai generate terraform \
  "Load-balanced web cluster with database backend" --skill intermediate

# Generates: Multi-VM setup with networking and security configurations
```

### Expert Level
- **Focus**: Advanced architectures and optimization
- **Features**: Complex scenarios, performance tuning, enterprise patterns
- **Best For**: Experienced with IaC, complex infrastructure needs

```bash
# Expert examples
python -m src.proxmox_ai.cli.main ai generate terraform \
  "High-availability Kubernetes cluster with external storage" --skill expert

# Generates: Advanced multi-node setup with HA, monitoring, and security
```

## 🔧 Troubleshooting

### Common Issues

**1. "Ollama not available" Error**
```bash
# Check if Ollama is running
ollama list

# If not running, start it:
ollama serve

# In another terminal, test:
curl http://localhost:11434/api/tags
```

**2. "Model not found" Error**
```bash
# List available models
ollama list

# Download the recommended model
ollama pull codellama:7b-instruct-q4_0

# Verify download
ollama list
```

**3. "Proxmox connection failed" Error**
```bash
# Test network connectivity
ping your-proxmox-host

# Test HTTPS connection
curl -k https://your-proxmox-host:8006/api2/json/version

# Check your credentials in .env file
```

**4. Memory Issues**
```bash
# Check available memory
free -h

# Use a smaller model if needed
ollama pull codellama:7b-instruct-q4_0  # Smaller quantized version

# Or use TinyLlama for very limited memory
ollama pull tinyllama:1.1b
```

### Performance Optimization

**For Low-Memory Systems (4-6GB):**
```bash
# Use lightweight model
export LOCAL_AI__MODEL_NAME=tinyllama:1.1b

# Reduce context window
export LOCAL_AI__MAX_TOKENS=512
```

**For High-Performance Systems (16GB+):**
```bash
# Use full model
export LOCAL_AI__MODEL_NAME=codellama:13b-instruct

# Increase context window
export LOCAL_AI__MAX_TOKENS=4096
```

### Getting Help

1. **Check Documentation**: See `docs/` directory for detailed guides
2. **Run Diagnostics**: Use `python -m src.proxmox_ai.cli.main doctor`
3. **View Logs**: Check application logs for detailed error information
4. **Community Support**: Check GitHub issues and discussions

## 🚀 Next Steps

### After Basic Setup

1. **Explore User Guides**:
   - `docs/user-guides/beginner.md`: First steps and simple examples
   - `docs/user-guides/intermediate.md`: Production workflows
   - `docs/user-guides/expert.md`: Advanced configurations

2. **Learn More Features**:
   - Read `docs/cli-reference.md` for all available commands
   - Check `docs/troubleshooting/` for common solutions
   - Review `docs/security/` for security best practices

3. **Build Your First Project**:
   - Start with a simple VM deployment
   - Progress to multi-VM applications
   - Explore advanced networking and security

### Advanced Topics

- **Custom Templates**: Create reusable infrastructure templates
- **GitOps Integration**: Set up automated deployments
- **Security Hardening**: Implement enterprise security practices
- **Performance Monitoring**: Monitor and optimize your infrastructure

## 📚 Additional Resources

- **Documentation**: `docs/` directory contains comprehensive guides
- **Examples**: `examples/` directory (coming soon) with sample configurations
- **GitHub Repository**: https://github.com/diszay/iac-ai-assistant
- **Issue Tracking**: Report bugs and request features on GitHub

---

## 🎉 Congratulations!

You're now ready to use the Proxmox AI Infrastructure Assistant! Start with simple commands and gradually work your way up to more complex infrastructure deployments.

**Happy automating!** 🤖🚀

---

*This guide follows security best practices and ensures your infrastructure remains secure and private with local AI processing.*