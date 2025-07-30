# Proxmox AI Infrastructure Assistant

A powerful, security-first Infrastructure as Code (IaC) automation tool that leverages local AI models to help manage Proxmox virtual environments. This assistant provides intelligent code generation, optimization recommendations, and interactive guidance for users of all skill levels.

**100% Local AI Processing** - No cloud dependencies, complete privacy, works offline

## Key Features

### 🤖 Local AI Integration
- **Complete Privacy**: 100% local processing - no data sent to external services
- **Hardware Optimized**: Automatic hardware detection and optimal model selection
- **Memory Efficient**: Quantized models requiring only 1-8GB RAM
- **Multi-Model Support**: Supports Llama 3.1/3.2 models with different quality levels
- **Intelligent Caching**: Smart response caching for faster repeated queries
- **Performance Monitoring**: Real-time hardware usage and optimization metrics

### 🛡️ Security-First Design
- **Enterprise Security**: Built with CIS benchmark compliance
- **Credential Management**: Secure handling of all authentication credentials
- **Network Isolation**: Comprehensive network security and firewall integration
- **Audit Logging**: Complete audit trail for all operations

### 🎯 Skill-Level Adaptation
- **Beginner**: Simple, guided explanations with step-by-step instructions
- **Intermediate**: Balanced detail with best practices and common patterns
- **Expert**: Advanced configurations, optimizations, and edge cases

### 🚀 Infrastructure Automation
- **Terraform Integration**: Generate and optimize Terraform configurations
- **Ansible Playbooks**: Create automated configuration management
- **VM Management**: Streamlined Proxmox virtual machine operations
- **Template Management**: Reusable infrastructure templates

## Quick Start

### Prerequisites

#### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.12 or later
- **Memory**: Minimum 4GB RAM (8GB+ recommended for better AI performance)
- **Storage**: 10GB free space for AI models and application data
- **Network**: SSH access to Proxmox host

#### Proxmox Requirements
- **Proxmox VE**: Version 7.4 or later
- **API Access**: Proxmox API token configured
- **SSH Access**: Key-based authentication configured

### Installation

#### 1. Install Ollama (Local AI Engine)

**Ollama Setup:**
```bash
# Linux/macOS installation
curl -fsSL https://ollama.ai/install.sh | sh

# Windows installation (via winget)
winget install Ollama.Ollama

# Start Ollama service
ollama serve

# Verify installation
ollama --version
curl http://localhost:11434/api/tags
```

**Automatic Hardware Detection and Model Selection:**
```bash
# The assistant will automatically detect your hardware and recommend the optimal model
# Run this after installing the main application to get personalized recommendations

proxmox-ai hardware-info
proxmox-ai optimize-hardware
```

**Manual Model Installation (if needed):**
```bash
# For systems with 4-6GB RAM (Basic quality, ~2-5 seconds response):
ollama pull llama3.2:3b-instruct-q4_0

# For systems with 6-12GB RAM (Good quality, ~3-8 seconds response):
ollama pull llama3.1:8b-instruct-q4_0

# For systems with 12-24GB RAM (High quality, ~4-10 seconds response):
ollama pull llama3.1:8b-instruct-q8_0

# For systems with 24GB+ RAM (Excellent quality, ~10-30 seconds response):
ollama pull llama3.1:70b-instruct-q4_0

# Verify model installation
ollama list
```

#### 2. Install Proxmox AI Assistant
```bash
# Clone the repository
git clone https://github.com/your-username/proxmox-ai-assistant.git
cd proxmox-ai-assistant

# Create virtual environment (Python 3.12+ required)
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the application with all dependencies
pip install -e .

# Run initial setup and hardware optimization
proxmox-ai setup --optimize-hardware

# Verify installation
proxmox-ai --version
proxmox-ai status
```

#### 3. Configure Credentials and AI Settings
```bash
# Initialize secure configuration
proxmox-ai config init

# Configure Proxmox connection
proxmox-ai config set proxmox.host "your-proxmox-ip"
proxmox-ai config set proxmox.api_token "your-api-token" 
proxmox-ai config set proxmox.ssh_key_path "~/.ssh/your-key"

# Configure local AI settings (optional - auto-detected by default)
proxmox-ai config set ai.model "llama3.1:8b-instruct-q4_0"
proxmox-ai config set ai.skill_level "intermediate"
proxmox-ai config set ai.cache_enabled true

# Test everything is working
proxmox-ai status
proxmox-ai ai-status
```

### Quick Start Examples

#### 🚀 Generate Infrastructure Code with AI
```bash
# Generate Terraform configuration (beginner-friendly)
proxmox-ai generate terraform --skill-level beginner \
  --description "Ubuntu web server with 2GB RAM and basic security"

# Generate Ansible playbook (intermediate)
proxmox-ai generate ansible --skill-level intermediate \
  --description "NGINX web server with SSL certificates and firewall"

# Generate VM configuration (expert level)
proxmox-ai generate vm --skill-level expert \
  --description "High-availability Kubernetes cluster with persistent storage"
```

#### 🔍 Analyze and Optimize Existing Code
```bash
# Explain existing configuration (great for learning)
proxmox-ai explain --file terraform-main.tf --skill-level beginner

# Optimize existing infrastructure code
proxmox-ai optimize --file ansible-playbook.yml --skill-level intermediate

# Security review of configurations
proxmox-ai security-review --file vm-config.tf --skill-level expert
```

#### 💬 Interactive AI Assistant
```bash
# Start interactive chat mode
proxmox-ai chat --skill-level intermediate

# Get help with specific IaC problems
proxmox-ai ask "How do I set up VM clustering in Proxmox?"

# Learn infrastructure concepts
proxmox-ai learn --topic "terraform-basics" --skill-level beginner
```

#### 📊 Hardware and Performance Monitoring
```bash
# Check your hardware capabilities
proxmox-ai hardware-info

# Monitor AI performance and optimize
proxmox-ai performance-stats

# Benchmark different models on your hardware
proxmox-ai benchmark-models
```

## Hardware Optimization

The assistant automatically detects your hardware and optimizes AI model selection for optimal performance and memory usage.

### 🔧 Automatic Hardware Detection
```bash
# Get detailed hardware analysis and recommendations
proxmox-ai hardware-info

# Run automatic optimization for your system
proxmox-ai optimize-hardware

# Monitor real-time performance and resource usage
proxmox-ai performance-stats

# Test different models on your hardware
proxmox-ai benchmark-models --duration 60
```

### 💻 Hardware Compatibility Matrix

| System RAM | CPU Cores | Recommended Model | Model Size | Quality | Response Time | Memory Usage |
|------------|-----------|-------------------|------------|---------|---------------|--------------|
| 4-6GB      | 2-4       | llama3.2:3b-q4_0 | ~2GB       | Basic   | 2-5 seconds   | 3-4GB        |
| 6-12GB     | 4-8       | llama3.1:8b-q4_0 | ~4.5GB     | Good    | 3-8 seconds   | 5-7GB        |
| 12-24GB    | 8-16      | llama3.1:8b-q8_0 | ~8GB       | High    | 4-10 seconds  | 9-12GB       |
| 24GB+      | 16+       | llama3.1:70b-q4_0| ~40GB      | Excellent| 10-30 seconds | 42-50GB      |

### ⚡ Performance Optimization Features

**GPU Acceleration (if available):**
```bash
# Auto-detect and enable GPU support
proxmox-ai config set ai.use_gpu auto

# Force GPU usage (if supported)
proxmox-ai config set ai.use_gpu true

# Monitor GPU usage
proxmox-ai gpu-stats
```

**Memory Management:**
```bash
# Set maximum memory usage (in GB)
proxmox-ai config set ai.max_memory_gb 8

# Enable memory mapping for faster model loading
proxmox-ai config set ai.use_mmap true

# Enable smart memory locking
proxmox-ai config set ai.use_mlock true
```

**Response Optimization:**
```bash
# Enable intelligent response caching
proxmox-ai config set ai.cache_enabled true

# Configure response streaming for faster perceived performance
proxmox-ai config set ai.stream_response true

# Adjust CPU thread usage for your system
proxmox-ai config set ai.cpu_threads auto
```

**Model Warming:**
```bash
# Pre-warm the model for faster first responses
proxmox-ai warmup-model

# Schedule automatic model warming
proxmox-ai config set ai.auto_warmup true
```

## Skill Level Configuration

### Beginner Mode
- **Focus**: Learning and understanding
- **Output**: Step-by-step instructions with explanations
- **Examples**: Simple, single-VM configurations
- **Safety**: Extra validation and confirmation prompts

```bash
proxmox-ai config set user.skill_level beginner
proxmox-ai generate vm --description "My first web server"
```

### Intermediate Mode
- **Focus**: Practical implementation
- **Output**: Best practices with common patterns
- **Examples**: Multi-VM setups with networking
- **Features**: Automation and configuration management

```bash
proxmox-ai config set user.skill_level intermediate
proxmox-ai generate infrastructure --description "Development environment"
```

### Expert Mode
- **Focus**: Advanced optimization
- **Output**: Enterprise patterns and edge cases
- **Examples**: HA clusters, disaster recovery
- **Features**: Advanced networking and security

```bash
proxmox-ai config set user.skill_level expert
proxmox-ai generate cluster --description "Production Kubernetes cluster"
```

## CLI Reference

### 🖥️ System Management Commands
```bash
# System status and health
proxmox-ai status                    # Overall system health check
proxmox-ai version                   # Display version information
proxmox-ai setup                     # Initial system configuration

# Configuration management
proxmox-ai config init               # Initialize configuration
proxmox-ai config set <key> <value>  # Set configuration value
proxmox-ai config get <key>          # Get configuration value
proxmox-ai config list               # List all configuration
```

### 🤖 AI and Hardware Commands
```bash
# AI model management
proxmox-ai ai-status                 # Check AI service status
proxmox-ai hardware-info             # Detailed hardware analysis
proxmox-ai optimize-hardware         # Optimize for current hardware
proxmox-ai performance-stats         # Real-time performance metrics

# Model operations
proxmox-ai list-models               # List available AI models
proxmox-ai switch-model <model>      # Switch to different model
proxmox-ai warmup-model              # Pre-warm model for faster responses
proxmox-ai benchmark-models          # Performance test all models
```

### 🚀 Code Generation Commands
```bash
# Infrastructure as Code generation
proxmox-ai generate terraform <description>    # Generate Terraform configuration
proxmox-ai generate ansible <description>      # Generate Ansible playbook
proxmox-ai generate vm <description>           # Generate VM configuration
proxmox-ai generate docker <description>       # Generate Docker compose
proxmox-ai generate kubernetes <description>   # Generate Kubernetes manifests

# Template-based generation
proxmox-ai generate from-template <template>   # Use predefined template
proxmox-ai templates list                      # List available templates
proxmox-ai templates create <name>             # Create custom template
```

### 🔍 Analysis and Optimization Commands
```bash
# Code analysis and explanation
proxmox-ai explain <file>            # Explain existing configuration
proxmox-ai security-review <file>    # Security analysis of code
proxmox-ai best-practices <file>     # Best practices review

# Code optimization
proxmox-ai optimize <file>           # Optimize existing configuration
proxmox-ai validate <file>           # Validate configuration syntax
proxmox-ai fix <file>                # Auto-fix common issues
```

### 💬 Interactive and Learning Commands
```bash
# Interactive AI assistant
proxmox-ai chat                      # Start interactive chat session
proxmox-ai ask "<question>"          # Ask specific question
proxmox-ai learn <topic>             # Interactive learning session

# Educational features
proxmox-ai workshop <level>          # Start skill-level workshop
proxmox-ai tutorial <topic>          # Step-by-step tutorials
proxmox-ai examples <technology>     # Show example configurations
```

### 🔧 Advanced Command Options

**Skill Level Control:**
```bash
--skill-level {beginner|intermediate|expert}  # Adapt response complexity
--auto-skill                                  # Auto-detect optimal skill level
```

**Output Formatting:**
```bash
--format {hcl|yaml|json|toml}        # Output format
--output-file <filename>             # Save to file
--pretty                             # Pretty-print output
--no-comments                        # Remove explanatory comments
```

**AI Model Control:**
```bash
--model <model-name>                 # Use specific model
--temperature <0.0-1.0>              # Control response creativity
--max-tokens <number>                # Limit response length
--use-cache                          # Enable response caching
--no-stream                          # Disable streaming responses
```

**Hardware and Performance:**
```bash
--optimize-for-hardware              # Auto-optimize for current hardware
--use-gpu                           # Force GPU usage
--max-memory <gb>                   # Set memory limit
--cpu-threads <number>              # Set CPU thread count
--profile                           # Enable performance profiling
```

**Security and Privacy:**
```bash
--audit-log                         # Enable detailed audit logging
--no-cache                          # Disable all caching
--secure-mode                       # Enable maximum security mode
--offline                           # Ensure complete offline operation
```

## Project Structure

```
proxmox-ai-assistant/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── CONTRIBUTING.md             # Contribution guidelines
├── SECURITY.md                 # Security policy
├── pyproject.toml              # Python project configuration
├── requirements.txt            # Python dependencies
├── src/
│   └── proxmox_ai/
│       ├── cli/                # Command-line interface
│       ├── ai/                 # Local AI integration
│       ├── core/               # Core functionality
│       ├── api/                # Proxmox API client
│       └── services/           # Business logic
├── docs/                       # Comprehensive documentation
│   ├── installation.md         # Detailed installation guide
│   ├── user-guides/           # User documentation by skill level
│   ├── api/                   # API documentation
│   ├── architecture/          # System architecture
│   ├── security/              # Security documentation
│   └── troubleshooting/       # Common issues and solutions
├── config/                     # Configuration templates
├── tests/                      # Test suites
└── scripts/                   # Utility scripts
```

## 📚 Documentation

### 🚀 **START HERE**
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - **Complete setup guide with step-by-step instructions**
- **[Documentation Index](docs/INDEX.md)** - Navigate all documentation easily

### 🎓 User Guides by Skill Level
- **[Beginner Guide](docs/user-guides/beginner.md)**: Your first steps with local AI and IaC
- **[Intermediate Guide](docs/user-guides/intermediate.md)**: Advanced automation workflows  
- **[Expert Guide](docs/user-guides/expert.md)**: Enterprise patterns and optimization

### 🔧 Essential References
- **[CLI Reference](docs/cli-reference.md)**: Complete command documentation
- **[Troubleshooting](docs/troubleshooting/common-issues.md)**: Solutions to common issues
- **[Security Guide](SECURITY.md)**: Security policies and best practices

- **[Examples Gallery](docs/examples/)**: Real-world configuration examples

### 🏗️ Technical Documentation
- **[Architecture Overview](docs/architecture/overview.md)**: System design and local AI integration
- **[API Documentation](docs/api/)**: Integration and development guides
- **[Security Guide](docs/security/)**: Privacy, security, and compliance
- **[Performance Guide](docs/performance.md)**: Optimization and benchmarking

### 🔍 Troubleshooting and Support
- **[Common Issues](docs/troubleshooting/common-issues.md)**: Frequent problems and solutions
- **[Hardware Compatibility](docs/troubleshooting/hardware.md)**: Hardware-specific guidance
- **[AI Model Issues](docs/troubleshooting/ai-models.md)**: Local AI troubleshooting
- **[Performance Troubleshooting](docs/troubleshooting/performance.md)**: Speed and memory optimization

## 🔒 Security and Privacy

This project prioritizes security and privacy with a local-first approach:

### 🏠 Complete Local Processing
- **Zero External Data Transfer**: All AI processing happens locally on your machine
- **No Cloud Dependencies**: Works completely offline once installed
- **Data Sovereignty**: Your infrastructure data never leaves your control
- **Network Isolation**: Optional air-gapped operation for maximum security

### 🛡️ Enterprise Security Features
- **Encrypted Credential Storage**: AES-256 encryption for all sensitive data
- **Secure Key Management**: Hardware security module (HSM) support
- **Role-Based Access Control**: Fine-grained permissions and audit trails
- **CIS Benchmark Compliance**: Meets enterprise security standards
- **Comprehensive Audit Logging**: Complete forensic trail of all operations

### 🔐 Privacy Guarantees
- **No Telemetry**: Zero usage data collection or transmission
- **Local Model Storage**: AI models stored locally on your system
- **Encrypted Communications**: TLS 1.3 for all Proxmox API communications
- **Memory Protection**: Secure memory handling for sensitive operations
- **Cache Encryption**: Optional encryption of local AI response cache

### 🚨 Security Reporting
- **Vulnerability Disclosure**: [SECURITY.md](SECURITY.md) for reporting procedures
- **Security Updates**: Automated security patch notifications
- **Threat Monitoring**: Built-in security monitoring and alerting

## Contributing

We welcome contributions from the community! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Setting up the development environment
- Code style and testing requirements
- Submitting pull requests
- Reporting issues and feature requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Discussions**: General questions and community support
- **Documentation**: Comprehensive guides and tutorials

### Enterprise Support
For enterprise deployments and commercial support, please contact the development team.

## 🙏 Acknowledgments

- **[Ollama Team](https://ollama.ai/)**: For the exceptional local AI model infrastructure
- **[Proxmox Team](https://www.proxmox.com/)**: For the robust and reliable virtualization platform
- **[Meta AI](https://ai.meta.com/)**: For the powerful Llama models that power our local AI
- **Open Source Community**: For the incredible tools, libraries, and contributions

## 📊 Performance Benchmarks

Typical performance metrics on different hardware configurations:

| Hardware Profile | Model Used | Config Generation | Code Explanation | Optimization Review |
|------------------|------------|-------------------|------------------|-------------------|
| Budget (4GB RAM) | llama3.2:3b | 5-8 seconds | 3-5 seconds | 8-12 seconds |
| Standard (8GB RAM) | llama3.1:8b-q4 | 3-6 seconds | 2-4 seconds | 6-10 seconds |
| High-End (16GB+ RAM) | llama3.1:8b-q8 | 2-4 seconds | 1-3 seconds | 4-8 seconds |
| Workstation (32GB+ RAM) | llama3.1:70b-q4 | 10-20 seconds | 5-15 seconds | 15-30 seconds |

*Performance varies based on specific hardware, complexity of requests, and system load*

---

**🚀 Built with passion for the Infrastructure as Code community**  
**🔒 Privacy-first • 🏠 Local-first • 🛡️ Security-first**