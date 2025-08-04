# 🚀 Getting Started with Proxmox AI Infrastructure Assistant

## 🐧 Ubuntu Terminal Commands - Copy & Paste Ready

**For Ubuntu users who need easy copy-paste commands:**

```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant

# Activate virtual environment
source venv/bin/activate

# Start the AI assistant
python -m src.proxmox_ai.cli.main

# Or use the start script
./scripts/start-assistant.sh

# Quick status check
python -m src.proxmox_ai.cli.main ai status

# Interactive AI chat mode
python -m src.proxmox_ai.cli.main ai chat

# Generate your first infrastructure
python -m src.proxmox_ai.cli.main ai generate terraform "Ubuntu web server with 2GB RAM"
```

---

Welcome to the **Proxmox AI Infrastructure Assistant** - your complete solution for local AI-powered infrastructure automation with complete privacy and security. This guide provides multiple paths to get you started quickly based on your experience level and needs.

## 🎯 Choose Your Path

**🚀 I want to start immediately (2 minutes)**  
👉 [Express Setup](#express-setup) - One command to get running

**📚 I want to understand what I'm installing (10 minutes)**  
👉 [Guided Setup](#guided-setup) - Step-by-step with explanations

**🔧 I want full control over the installation (30 minutes)**  
👉 [Advanced Setup](#advanced-setup) - Complete customization

**🆘 I'm having problems**  
👉 [Troubleshooting](#troubleshooting) - Solutions to common issues

---

## 🚀 Express Setup (2 Minutes)

**Perfect for:** Experienced users who want to start immediately

### Quick Requirements Check ✅
- [ ] **Python 3.12+** installed (`python3.12 --version`)
- [ ] **4GB+ RAM** available  
- [ ] **15GB+ disk space** free
- [ ] **Proxmox server** accessible on your network

### One-Command Installation
```bash
# Download and run the express installer
curl -fsSL https://raw.githubusercontent.com/diszay/iac-ai-assistant/main/scripts/express-install.sh | bash

# That's it! The script will:
# ✅ Install Ollama (local AI engine)
# ✅ Download optimal AI model for your hardware
# ✅ Install Proxmox AI Assistant
# ✅ Guide you through basic configuration
# ✅ Test everything is working
```

### Ubuntu Terminal Commands After Installation
```bash
# Navigate to the installed directory
cd ~/projects/iac-ai-assistant

# Activate the virtual environment
source venv/bin/activate

# Start the assistant
python -m src.proxmox_ai.cli.main

# Or use the convenient script
./scripts/start-assistant.sh
```

### Express Configuration
```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Configure your Proxmox connection (when prompted)
Enter Proxmox host (e.g., 192.168.1.50): YOUR_HOST
Enter SSH port (default 22): 22
Choose authentication method: [1] API Token [2] Password
Enter API token or password: YOUR_CREDENTIALS

# Test your setup
python -m src.proxmox_ai.cli.main status  # Should show all green checkmarks
```

### Start Using Immediately
```bash
# Ubuntu Terminal Commands:
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Start interactive AI chat
python -m src.proxmox_ai.cli.main ai chat

# Or generate your first infrastructure
python -m src.proxmox_ai.cli.main ai generate terraform "Ubuntu web server with 2GB RAM"

# Or use the convenient script
./scripts/start-assistant.sh
```

**✅ Done!** Skip to [Basic Usage](#basic-usage) to start automating your infrastructure.

---

## 📚 Guided Setup (10 Minutes)

**Perfect for:** New users who want to understand each step

### Table of Contents
1. [Requirements Check](#requirements-check)
2. [Local AI Setup](#local-ai-setup)
3. [Application Installation](#application-installation)
4. [Configuration](#configuration)
5. [First Test](#first-test)

### 1. Requirements Check

Let's make sure your system is ready:

#### ✅ System Check - Ubuntu Terminal Commands
```bash
# Check Python version (need 3.12+)
python3.12 --version || python3 --version

# Check available memory (need 4GB+)
free -h | grep "Mem:"

# Check disk space (need 15GB+)  
df -h | head -2

# Check network connectivity to your Proxmox
ping -c 3 YOUR_PROXMOX_HOST  # Replace with your Proxmox IP
```

#### 🔧 Install Missing Requirements

**Python 3.12 (if needed):**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3.12 python3.12-venv python3.12-pip

# macOS  
brew install python@3.12

# Windows (via winget)
winget install Python.Python.3.12
```

**Git (if needed):**
```bash
# Ubuntu/Debian
sudo apt install git

# macOS (usually pre-installed)
git --version

# Windows  
winget install Git.Git
```

### 2. Local AI Setup

We use Ollama for local AI processing - no cloud dependencies!

#### Install Ollama
```bash
# Linux/macOS - one command
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - download installer from ollama.ai
# Or use: winget install Ollama.Ollama

# Verify installation
ollama --version
```

#### Start Ollama Service
```bash
# Start the service
ollama serve &

# Verify it's running (should return JSON)
curl http://localhost:11434/api/tags
```

#### Choose Your AI Model
We'll automatically detect the best model for your hardware:

```bash
# Check your system specs
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "CPU cores: $(nproc)"

# We'll recommend:
# 4-6GB RAM: llama3.2:3b-instruct-q4_0 (2GB model)
# 6-12GB RAM: llama3.1:8b-instruct-q4_0 (4.5GB model)  
# 12GB+ RAM: llama3.1:8b-instruct-q8_0 (8GB model)
```

### 3. Application Installation

#### Clone and Install - Ubuntu Terminal Commands
```bash
# Navigate to projects directory
mkdir -p ~/projects
cd ~/projects

# Clone the repository
git clone https://github.com/diszay/iac-ai-assistant.git
cd iac-ai-assistant

# Create virtual environment (keeps everything isolated)
python3.12 -m venv venv

# Activate it
source venv/bin/activate

# Install the application
pip install -e .

# Verify installation
python -m src.proxmox_ai.cli.main --version
```

### 4. Configuration

#### Basic Configuration - Ubuntu Terminal Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Initialize configuration (creates secure config files)
python -m src.proxmox_ai.cli.main config init

# Configure your Proxmox connection
python -m src.proxmox_ai.cli.main config set proxmox.host "YOUR_PROXMOX_IP"
python -m src.proxmox_ai.cli.main config set proxmox.port "8006"  
python -m src.proxmox_ai.cli.main config set proxmox.user "root@pam"

# Choose authentication method:
# Option A: API Token (recommended for security)
python -m src.proxmox_ai.cli.main config set proxmox.api_token "YOUR_API_TOKEN"

# Option B: Password (less secure but easier)
python -m src.proxmox_ai.cli.main config set proxmox.password "YOUR_PASSWORD"
```

#### AI Configuration (Auto-detected) - Ubuntu Terminal Commands
```bash
# Navigate to project and activate environment
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# The application will automatically:
# ✅ Detect your hardware capabilities
# ✅ Download the optimal AI model
# ✅ Configure memory settings
# ✅ Set appropriate skill level

# Or manually configure:
python -m src.proxmox_ai.cli.main config set ai.model "llama3.1:8b-instruct-q4_0"
python -m src.proxmox_ai.cli.main config set ai.skill_level "intermediate"
```

### 5. First Test

Let's make sure everything works:

```bash
# Ubuntu Terminal Commands:
cd ~/projects/iac-ai-assistant
source venv/bin/activate

# Run comprehensive diagnostics
python -m src.proxmox_ai.cli.main doctor

# Expected output:
# ✅ Python environment: OK
# ✅ Ollama service: Running  
# ✅ AI model: Available
# ✅ Proxmox connection: Connected
# ✅ Configuration: Valid
# ✅ Security: Configured

# Test AI functionality
python -m src.proxmox_ai.cli.main ask "Hello, can you help me with infrastructure?"

# Test Proxmox connectivity
python -m src.proxmox_ai.cli.main vm list
```

**🎉 Success!** Continue to [Basic Usage](#basic-usage)

---

## 🔧 Advanced Setup (30 Minutes)

**Perfect for:** Users who want complete control and customization

### Table of Contents  
1. [Custom Python Environment](#custom-python-environment)
2. [Advanced AI Configuration](#advanced-ai-configuration)
3. [Security Hardening](#security-hardening) 
4. [Performance Optimization](#performance-optimization)
5. [Enterprise Features](#enterprise-features)

### Custom Python Environment

For advanced users who want complete control:

```bash
# Use pyenv for multiple Python versions
curl https://pyenv.run | bash
pyenv install 3.12.3
pyenv local 3.12.3

# Create custom virtual environment
python -m venv --copies --clear proxmox-ai-env
source proxmox-ai-env/bin/activate

# Install with specific versions
pip install -r requirements-locked.txt
```

---

## 🛠️ Basic Usage

Now that you have the system installed, let's learn how to use it effectively!

### 💬 Interactive AI Chat (Easiest Way)

The chat mode is perfect for beginners and natural conversation:

```bash
# Start interactive chat
proxmox-ai chat

# Now you can ask natural questions like:
"Create a simple web server for my blog"
"I need 3 Ubuntu VMs for a development cluster"  
"How do I add more memory to an existing VM?"
"What's the best way to backup my VMs?"
"Explain this Terraform configuration to me"
```

### 🚀 Quick Commands for Common Tasks

#### Generate Infrastructure Code
```bash
# Generate different types of infrastructure

# Simple web server
proxmox-ai generate terraform "Ubuntu web server with nginx, 2GB RAM"

# Development environment  
proxmox-ai generate terraform "Development cluster with 3 VMs and shared storage"

# Database server
proxmox-ai generate terraform "PostgreSQL database server with backup storage"

# Multi-tier application
proxmox-ai generate terraform "Web app with load balancer, app servers, and database"
```

#### Generate Automation Scripts
```bash
# Ansible playbooks for configuration

# Server hardening
proxmox-ai generate ansible "Harden Ubuntu servers with firewall and security updates"

# Software installation
proxmox-ai generate ansible "Install Docker and configure container environment"

# Monitoring setup
proxmox-ai generate ansible "Install and configure Prometheus monitoring"
```

#### Analyze and Improve Existing Code
```bash
# Get help with existing configurations

# Explain what a configuration does
proxmox-ai explain my-terraform-config.tf

# Get optimization suggestions  
proxmox-ai optimize my-infrastructure.tf

# Security review
proxmox-ai security-review my-vm-config.tf

# Fix common issues
proxmox-ai fix problematic-config.tf
```

### 🎯 Skill Level Adaptation

The AI adapts its responses based on your skill level:

#### Beginner Level
```bash
# Set beginner mode for detailed explanations
proxmox-ai config set ai.skill_level beginner

# Example response includes:
# ✅ Step-by-step explanations
# ✅ What each setting means
# ✅ Why certain choices are made
# ✅ Safety warnings and best practices
# ✅ Links to learn more
```

#### Intermediate Level (Default)
```bash
# Set intermediate mode for practical focus
proxmox-ai config set ai.skill_level intermediate

# Example response includes:
# ✅ Production-ready configurations
# ✅ Best practices integrated
# ✅ Reasonable automation
# ✅ Performance considerations
```

#### Expert Level
```bash
# Set expert mode for advanced features
proxmox-ai config set ai.skill_level expert

# Example response includes:
# ✅ Advanced optimization options
# ✅ Enterprise patterns
# ✅ Performance tuning
# ✅ Complex scenarios
```

### 📊 System Management Commands

#### Check System Status
```bash
# Quick health check
proxmox-ai status

# Comprehensive diagnostics
proxmox-ai doctor

# View configuration
proxmox-ai config list

# Hardware analysis
proxmox-ai hardware-info
```

#### AI Model Management  
```bash
# Check AI status
proxmox-ai ai-status

# See available models
proxmox-ai ai models

# Switch to different model
proxmox-ai ai switch-model llama3.1:8b-instruct-q8_0

# Optimize for your hardware
proxmox-ai ai optimize
```

#### VM Operations
```bash
# List all VMs
proxmox-ai vm list

# Get VM details
proxmox-ai vm info 101

# Start/stop VMs
proxmox-ai vm start 101
proxmox-ai vm stop 101

# Create VM from generated config
proxmox-ai vm create my-server-config.tf
```

### 🔍 Getting Help and Learning

#### Interactive Help
```bash
# Start a learning conversation
proxmox-ai chat
# Then ask: "I'm new to this, teach me about virtual machines"

# Get help with specific topics
proxmox-ai ask "How do I set up VM networking?"
proxmox-ai ask "What's the difference between containers and VMs?"
proxmox-ai ask "How do I backup my infrastructure?"
```

#### Command Help
```bash
# Get help for any command
proxmox-ai --help
proxmox-ai generate --help
proxmox-ai vm --help

# Examples and tutorials
proxmox-ai examples terraform
proxmox-ai tutorial "first-vm"
```

### 🔧 Common Workflows

#### Workflow 1: Create Your First VM
```bash
# Step 1: Generate the configuration
proxmox-ai generate terraform "Simple Ubuntu server for learning" --output vm-config.tf

# Step 2: Review and understand
proxmox-ai explain vm-config.tf

# Step 3: Test the configuration  
proxmox-ai validate vm-config.tf

# Step 4: Deploy (when ready)
proxmox-ai vm create vm-config.tf
```

#### Workflow 2: Learn and Experiment
```bash
# Start interactive learning
proxmox-ai chat

# Ask questions like:
"What happens if I increase the RAM in my VM?"
"How do I add a second network interface?"
"Show me examples of different VM configurations"
"What are the security best practices?"
```

#### Workflow 3: Optimize Existing Infrastructure
```bash
# Analyze current setup
proxmox-ai analyze my-infrastructure/

# Get optimization recommendations
proxmox-ai optimize my-infrastructure/

# Review security
proxmox-ai security-review my-infrastructure/

# Generate improvements
proxmox-ai improve my-infrastructure/ --focus performance
```

### 💡 Pro Tips for Success

#### Start Simple
```bash
# Begin with basic VMs
proxmox-ai generate terraform "Single Ubuntu VM" --skill beginner

# Gradually increase complexity
proxmox-ai generate terraform "Ubuntu VM with custom networking" --skill intermediate

# Eventually tackle complex scenarios  
proxmox-ai generate terraform "High-availability web cluster" --skill expert
```

#### Use the Chat Mode
```bash
# Chat is perfect for learning
proxmox-ai chat

# Ask follow-up questions
"Can you explain that in simpler terms?"
"What would happen if I changed this setting?"
"Show me a different way to do this"
```

#### Save and Reuse
```bash
# Save configurations for reuse
proxmox-ai generate terraform "Web server template" --output templates/web-server.tf

# Create variations
proxmox-ai modify templates/web-server.tf "Add 4GB RAM and SSD storage"

# Build libraries
mkdir templates/
proxmox-ai generate terraform "Database server" --output templates/database.tf
proxmox-ai generate terraform "Load balancer" --output templates/lb.tf
```

---

## 🎓 Skill Level Progression Guide

### 🌱 Beginner (Week 1-2)
**Goal**: Understand basics and create simple VMs

```bash
# Start here
proxmox-ai config set ai.skill_level beginner

# Learn fundamentals
proxmox-ai chat
# Ask: "Explain virtual machines in simple terms"
# Ask: "What is Infrastructure as Code?"

# First tasks
proxmox-ai generate terraform "Simple test VM"
proxmox-ai explain my-first-vm.tf
```

**Checklist for Beginners:**
- [ ] Successfully created first VM configuration
- [ ] Understand what each section does  
- [ ] Can explain memory, CPU, and storage settings
- [ ] Know how to ask for help

### 🌿 Intermediate (Week 3-4)
**Goal**: Create production-ready multi-VM setups

```bash
# Progress to intermediate
proxmox-ai config set ai.skill_level intermediate

# More complex scenarios
proxmox-ai generate terraform "Web application with database backend"
proxmox-ai generate ansible "Automate server configuration"

# Learn best practices
proxmox-ai security-review my-infrastructure.tf
proxmox-ai optimize my-infrastructure.tf
```

**Checklist for Intermediate:**
- [ ] Can create multi-VM configurations
- [ ] Understand networking and security basics
- [ ] Use Ansible for automation
- [ ] Follow security best practices

### 🌳 Expert (Week 5+)
**Goal**: Enterprise-grade infrastructure automation

```bash
# Advance to expert level
proxmox-ai config set ai.skill_level expert

# Complex scenarios
proxmox-ai generate terraform "HA Kubernetes cluster with persistent storage"
proxmox-ai generate terraform "Multi-tier application with monitoring"

# Advanced operations
proxmox-ai analyze production-infrastructure/
proxmox-ai optimize --focus performance production-infrastructure/
```

**Checklist for Expert:**
- [ ] Design complex, scalable architectures
- [ ] Implement high availability and disaster recovery
- [ ] Optimize for performance and cost
- [ ] Integrate with existing enterprise systems

---

## 🆘 Troubleshooting
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