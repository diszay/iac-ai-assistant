# 📋 System Requirements - Proxmox AI Infrastructure Assistant

## 🐧 Ubuntu Terminal Launch Commands

**For Ubuntu users - Copy these commands to start the assistant:**

```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant

# Activate virtual environment
source venv/bin/activate

# Launch the AI assistant
python -m src.proxmox_ai.cli.main

# Or use the convenient startup script
./scripts/start-assistant.sh

# Quick status check
python -m src.proxmox_ai.cli.main status
```

---

## 🎯 Quick Compatibility Check

**Can you run this application?**
- ✅ **Operating System**: Linux, macOS, or Windows 10/11
- ✅ **Memory**: 4GB+ RAM (8GB+ recommended)
- ✅ **Python**: Version 3.12 or newer
- ✅ **Network**: Internet access for initial setup and model downloads
- ✅ **Storage**: 10GB+ free space

**→ If you meet these requirements, you're ready to install! Skip to [Quick Install](#-quick-install)**

---

## 🖥️ System Requirements

### **Minimum Requirements (Basic Functionality)**
| Component | Requirement | Notes |
|-----------|-------------|-------|
| **OS** | Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10/11 | WSL2 required for Windows |
| **CPU** | 2+ cores, x86_64 or ARM64 | Intel, AMD, or Apple Silicon |
| **RAM** | 4GB total system memory | 3GB available for AI models |
| **Storage** | 10GB free space | SSD recommended for better performance |
| **Network** | Broadband internet connection | For initial setup and model downloads |
| **Python** | Python 3.12+ | Other versions not supported |

### **Recommended Configuration (Optimal Performance)**
| Component | Recommendation | Benefits |
|-----------|----------------|----------|
| **OS** | Linux (Ubuntu 22.04 LTS) | Best performance and compatibility |
| **CPU** | 4+ cores, 3.0GHz+ | Faster AI inference and processing |
| **RAM** | 8GB-16GB | Larger AI models, better multitasking |
| **Storage** | 20GB+ SSD | Faster model loading and caching |
| **Network** | Stable broadband | Reliable model downloads |
| **GPU** | Integrated or discrete GPU | Potential AI acceleration (optional) |

### **High-Performance Setup (Professional Use)**
| Component | Specification | Use Case |
|-----------|---------------|----------|
| **OS** | Linux (Ubuntu 22.04 LTS) | Enterprise deployment |
| **CPU** | 8+ cores, 3.5GHz+ | Heavy infrastructure generation |
| **RAM** | 16GB-32GB | Large language models (13B+ parameters) |
| **Storage** | 50GB+ NVMe SSD | Multiple models and extensive caching |
| **Network** | High-speed internet | Fast model updates and downloads |
| **GPU** | 8GB+ VRAM GPU | Hardware-accelerated AI inference |

---

## 🐍 Python Requirements

### **Python Version Compatibility**
- ✅ **Required**: Python 3.12.0 or newer
- ✅ **Recommended**: Python 3.12.4+ (latest stable)
- ❌ **Not Supported**: Python 3.11 or older

### **Installation by Platform**

#### **Ubuntu/Debian - Copy-Paste Commands**
```bash
# Check current version
python3 --version

# Install Python 3.12+ if needed
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-pip

# Verify installation
python3.12 --version

# After installation, navigate to project
cd ~/projects/iac-ai-assistant
source venv/bin/activate
python -m src.proxmox_ai.cli.main --version
```

#### **macOS**
```bash
# Using Homebrew (recommended)
brew install python@3.12

# Using official installer
# Download from https://python.org/downloads/

# Verify installation
python3.12 --version
```

#### **Windows**
```powershell
# Option 1: Microsoft Store (easiest)
# Search "Python 3.12" in Microsoft Store and install

# Option 2: Official installer
# Download from https://python.org/downloads/

# Option 3: Windows Subsystem for Linux (WSL2)
wsl --install
# Then follow Ubuntu instructions above

# Verify installation
python --version
```

#### **Package Dependencies**
All Python dependencies are automatically installed via `requirements.txt`:
```
typer>=0.9.0          # CLI framework
rich>=13.7.0          # Terminal formatting
proxmoxer>=2.0.1      # Proxmox API client
requests>=2.31.0      # HTTP requests
pydantic>=2.5.0       # Configuration validation
structlog>=23.2.0     # Structured logging
keyring>=24.3.0       # Credential storage
cryptography>=41.0.0  # Encryption
jinja2>=3.1.0         # Template engine
pyyaml>=6.0.0         # YAML parsing
ollama>=0.2.0         # Local AI integration
```

---

## 🧠 AI Model Requirements

### **Local AI Engine: Ollama**
The application uses Ollama for local AI processing (no cloud dependencies).

#### **Ollama Installation - Ubuntu Commands**
```bash
# Ubuntu/Linux installation
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Verify installation and service
ollama --version
curl http://localhost:11434/api/tags

# Download recommended model for your hardware
# For 4-6GB RAM:
ollama pull llama3.2:3b-instruct-q4_0

# For 8GB+ RAM:
ollama pull llama3.1:8b-instruct-q4_0
```

### **AI Model Storage Requirements**

| Model Size | RAM Usage | Disk Space | Quality | Response Time |
|------------|-----------|------------|---------|---------------|
| **3B parameters** | 2-4GB | 2GB | Good | 2-5 seconds |
| **7B parameters** | 4-6GB | 4GB | Better | 3-8 seconds |
| **8B parameters** | 6-8GB | 5GB | Excellent | 4-10 seconds |
| **13B parameters** | 8-12GB | 8GB | Superior | 6-15 seconds |
| **70B parameters** | 40-50GB | 40GB | Outstanding | 15-30 seconds |

#### **Automatic Model Selection - Ubuntu Commands**
The application automatically selects the best model for your hardware:
```bash
# Navigate to project directory
cd ~/projects/iac-ai-assistant

# Hardware detection happens automatically
./scripts/start-assistant.sh

# Or run manually
source venv/bin/activate
python -m src.proxmox_ai.cli.main ai optimize

# Manual model selection if needed
ollama pull llama3.1:8b-instruct-q4_0  # Recommended for 8GB+ RAM
ollama pull llama3.2:3b-instruct-q4_0  # For 4-6GB RAM systems
```

---

## 🌐 Network Requirements

### **Required Network Access**
| Service | Purpose | During | Required |
|---------|---------|--------|----------|
| **GitHub** | Code repository access | Installation | ✅ Yes |
| **Ollama.ai** | AI model downloads | Setup | ✅ Yes |
| **PyPI** | Python package installation | Setup | ✅ Yes |
| **Your Proxmox Server** | Infrastructure management | Operation | ✅ Yes |

### **Proxmox Network Requirements**
| Component | Requirement | Default | Notes |
|-----------|-------------|---------|-------|
| **Host Access** | HTTPS (port 8006) | ✅ Standard | Proxmox web interface port |
| **SSH Access** | SSH (port 22) | ⚠️ Optional | For advanced operations |
| **Custom SSH Port** | User-defined | ⚠️ Optional | Enhanced security |
| **VPN Access** | Site-to-site or client VPN | ⚠️ Optional | For remote access |

#### **Firewall Configuration**
```bash
# Allow outbound HTTPS for Proxmox API
# Allow outbound HTTPS for model downloads
# Allow inbound if running web interface (optional)

# Example UFW rules
sudo ufw allow out 443    # HTTPS outbound
sudo ufw allow out 8006   # Proxmox API
```

---

## 💾 Storage Requirements

### **Disk Space Breakdown**
| Component | Minimum | Recommended | Purpose |
|-----------|---------|-------------|---------|
| **Application** | 500MB | 1GB | Source code and dependencies |
| **AI Models** | 2GB | 8GB | Local language models |
| **Cache** | 100MB | 1GB | Response and template caching |
| **Logs** | 50MB | 200MB | Application and security logs |
| **Generated Files** | 100MB | 500MB | Terraform/Ansible outputs |
| **Backups** | 100MB | 1GB | Configuration backups |
| **Total** | **3GB** | **12GB** | Complete installation |

### **Performance Considerations**
| Storage Type | Impact | Recommendation |
|--------------|--------|----------------|
| **HDD** | Slower model loading | Acceptable for basic use |
| **SSD** | 2-3x faster performance | Recommended for regular use |
| **NVMe SSD** | 4-5x faster performance | Best for professional use |

---

## 🔧 Development Tools (Optional)

### **For Contributing or Customization**
```bash
# Git (version control)
git --version

# Code editor (choose one)
code .          # Visual Studio Code
vim main.py     # Vim
nano main.py    # Nano

# Development dependencies (optional)
pip install pytest black flake8
```

---

## 🚀 Quick Install

**Ready to install? Choose your preferred method:**

### **Method 1: One-Command Install (Fastest)**
```bash
curl -fsSL https://raw.githubusercontent.com/diszay/iac-ai-assistant/main/scripts/quick-install.sh | bash
```

### **Method 2: Manual Install (Learning) - Ubuntu Commands**
```bash
# 1. Create projects directory and clone
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/diszay/iac-ai-assistant.git
cd iac-ai-assistant

# 2. Set up virtual environment
python3.12 -m venv venv
source venv/bin/activate

# 3. Install and run
pip install -e .
./scripts/start-assistant.sh
```

### **Method 3: Step-by-Step (Complete Control)**
See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions.

---

## 🔍 Compatibility Testing

### **Test Your System**
Run this quick compatibility check:
```bash
# Download and run compatibility test
curl -fsSL https://raw.githubusercontent.com/diszay/iac-ai-assistant/main/scripts/compatibility-check.sh | bash
```

### **Manual Testing - Ubuntu Commands**
```bash
# Check Python version
python3 --version  # Should be 3.12+

# Check memory
free -h

# Check disk space
df -h

# Test network connectivity
ping -c 3 github.com
curl -I https://ollama.ai

# Test project setup
cd ~/projects/iac-ai-assistant
source venv/bin/activate
python -m src.proxmox_ai.cli.main --version
```

---

## ⚠️ Troubleshooting Requirements

### **Common Issues**

#### **"Python 3.12 not found"**
```bash
# Ubuntu/Debian
sudo apt install python3.12

# macOS
brew install python@3.12

# Windows
# Download from python.org
```

#### **"Insufficient memory for AI model"**
```bash
# Check available memory
free -h

# Use smaller model
export AI_MODEL="llama3.2:3b-instruct-q4_0"

# Or increase swap space
sudo swapon --show
```

#### **"Cannot connect to Proxmox"**
```bash
# Test network connection
ping YOUR_PROXMOX_HOST

# Test HTTPS access
curl -k https://YOUR_PROXMOX_HOST:8006/api2/json/version

# Check firewall settings
sudo ufw status
```

#### **"Ollama installation failed"**
```bash
# Manual installation
# Visit https://ollama.ai/download
# Download appropriate installer for your OS

# Verify installation
ollama --version
ollama serve  # Start service
```

---

## 📞 Getting Help

### **Before Installation**
- 📧 **System Requirements Questions**: Check [compatibility-check.sh](scripts/compatibility-check.sh)
- 🖥️ **Hardware Recommendations**: Run `./scripts/hardware-check.sh`
- 🔗 **Network Issues**: See [Network Troubleshooting](docs/troubleshooting/network.md)

### **During Installation**
- 🛠️ **Installation Problems**: See [Installation Troubleshooting](docs/troubleshooting/installation.md)
- 📋 **Dependency Issues**: Run `./scripts/doctor.sh`
- 🔧 **Configuration Help**: Use `proxmox-ai config --help`

### **After Installation**
- 💬 **Interactive Help**: Run `proxmox-ai chat` and ask questions
- 📖 **Documentation**: Browse [docs/](docs/) directory
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/diszay/iac-ai-assistant/issues)

---

## ✅ Ready to Install?

**If your system meets these requirements, you're ready to get started!**

👉 **Next Step**: Choose your installation method in [GETTING_STARTED.md](GETTING_STARTED.md)

---

*This requirements guide ensures optimal performance and security for the Proxmox AI Infrastructure Assistant while providing comprehensive support for different system configurations and use cases.*