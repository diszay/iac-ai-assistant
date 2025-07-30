# Proxmox AI Infrastructure Assistant - CLI Reference

Complete command-line interface reference for the Proxmox AI Infrastructure Assistant with local AI integration.

## 📋 Table of Contents

- [System Management Commands](#system-management-commands)
- [AI and Hardware Commands](#ai-and-hardware-commands)
- [Code Generation Commands](#code-generation-commands)
- [Analysis and Optimization Commands](#analysis-and-optimization-commands)
- [Interactive and Learning Commands](#interactive-and-learning-commands)
- [Configuration Management](#configuration-management)
- [Global Options](#global-options)
- [Examples by Skill Level](#examples-by-skill-level)

## 🖥️ System Management Commands

### `proxmox-ai status`

Check overall system health and connectivity.

**Usage:**
```bash
proxmox-ai status [OPTIONS]
```

**Options:**
- `--detailed`: Show detailed system information
- `--json`: Output in JSON format
- `--check-all`: Perform comprehensive health checks

**Examples:**
```bash
# Basic status check
proxmox-ai status

# Detailed status with all checks
proxmox-ai status --detailed --check-all

# JSON output for scripting
proxmox-ai status --json
```

**Sample Output:**
```
🤖 Proxmox AI Infrastructure Assistant Status

✅ System Health:       Operational
✅ Local AI:           Available (llama3.1:8b-q4_0)
✅ Proxmox Connection: Connected (192.168.1.50)
✅ SSH Access:         Authenticated
✅ API Access:         Authorized
✅ Hardware:           Optimized (8GB RAM, 4 cores)

Performance Stats:
- AI Response Time:    2.3s average
- Cache Hit Rate:      67%
- Memory Usage:        5.2GB / 8GB
- Model Quality:       Good
```

### `proxmox-ai version`

Display version information and build details.

**Usage:**
```bash
proxmox-ai version [OPTIONS]
```

**Options:**
- `--full`: Show detailed version information
- `--check-updates`: Check for available updates

**Examples:**
```bash
# Basic version info
proxmox-ai version

# Full version details
proxmox-ai version --full

# Check for updates
proxmox-ai version --check-updates
```

### `proxmox-ai setup`

Initial system configuration and optimization.

**Usage:**
```bash
proxmox-ai setup [OPTIONS]
```

**Options:**
- `--optimize-hardware`: Run automatic hardware optimization
- `--interactive`: Interactive setup wizard
- `--skip-ai-setup`: Skip AI model configuration
- `--force`: Force reconfiguration

**Examples:**
```bash
# Interactive setup wizard
proxmox-ai setup --interactive

# Automated setup with hardware optimization
proxmox-ai setup --optimize-hardware

# Quick setup skipping AI configuration
proxmox-ai setup --skip-ai-setup
```

## 🤖 AI and Hardware Commands

### `proxmox-ai ai-status`

Check local AI service status and performance.

**Usage:**
```bash
proxmox-ai ai-status [OPTIONS]
```

**Options:**
- `--performance`: Show performance metrics
- `--models`: List available models
- `--health-check`: Perform AI health check

**Examples:**
```bash
# Basic AI status
proxmox-ai ai-status

# Performance metrics
proxmox-ai ai-status --performance

# List all available models
proxmox-ai ai-status --models
```

### `proxmox-ai hardware-info`

Display detailed hardware analysis and recommendations.

**Usage:**
```bash
proxmox-ai hardware-info [OPTIONS]
```

**Options:**
- `--benchmark`: Run hardware benchmarks
- `--recommendations`: Show optimization recommendations
- `--compare-models`: Compare model performance on current hardware

**Examples:**
```bash
# Basic hardware info
proxmox-ai hardware-info

# Full hardware analysis with recommendations
proxmox-ai hardware-info --recommendations --benchmark

# Compare AI model performance
proxmox-ai hardware-info --compare-models
```

### `proxmox-ai optimize-hardware`

Optimize AI configuration for current hardware.

**Usage:**
```bash
proxmox-ai optimize-hardware [OPTIONS]
```

**Options:**
- `--auto`: Automatically apply optimizations
- `--profile PROFILE`: Use specific optimization profile
- `--gpu`: Enable GPU optimizations
- `--memory-limit GB`: Set memory usage limit

**Examples:**
```bash
# Interactive optimization
proxmox-ai optimize-hardware

# Automatic optimization
proxmox-ai optimize-hardware --auto

# Optimize with GPU acceleration
proxmox-ai optimize-hardware --auto --gpu

# Optimize with memory limit
proxmox-ai optimize-hardware --auto --memory-limit 6
```

### `proxmox-ai performance-stats`

Show real-time performance metrics.

**Usage:**
```bash
proxmox-ai performance-stats [OPTIONS]
```

**Options:**
- `--live`: Show live updating metrics
- `--duration SECONDS`: Monitor for specified duration
- `--export FILE`: Export metrics to file

**Examples:**
```bash
# Current performance stats
proxmox-ai performance-stats

# Live monitoring for 60 seconds
proxmox-ai performance-stats --live --duration 60

# Export metrics to file
proxmox-ai performance-stats --export metrics.json
```

### `proxmox-ai benchmark-models`

Benchmark AI models on current hardware.

**Usage:**
```bash
proxmox-ai benchmark-models [OPTIONS]
```

**Options:**
- `--models MODEL1,MODEL2`: Specific models to benchmark
- `--duration SECONDS`: Benchmark duration per model
- `--workload TYPE`: Workload type (infrastructure, code-generation, analysis)
- `--output FORMAT`: Output format (table, json, csv)

**Examples:**
```bash
# Benchmark all available models
proxmox-ai benchmark-models

# Benchmark specific models
proxmox-ai benchmark-models --models "llama3.1:8b-q4_0,llama3.2:3b-q4_0"

# Infrastructure-specific benchmark
proxmox-ai benchmark-models --workload infrastructure --duration 30
```

## 🚀 Code Generation Commands

### `proxmox-ai generate terraform`

Generate Terraform configurations for infrastructure.

**Usage:**
```bash
proxmox-ai generate terraform [OPTIONS] DESCRIPTION
```

**Options:**
- `--skill-level LEVEL`: Target skill level (beginner, intermediate, expert)
- `--format FORMAT`: Output format (hcl, json)
- `--output-file FILE`: Save to specific file
- `--provider PROVIDER`: Cloud provider (proxmox, aws, azure, gcp)
- `--template TEMPLATE`: Use specific template
- `--variables FILE`: Variable definitions file

**Examples:**
```bash
# Basic VM configuration for beginners
proxmox-ai generate terraform --skill-level beginner \
  "Simple Ubuntu web server with 2GB RAM"

# Advanced multi-tier application
proxmox-ai generate terraform --skill-level expert \
  "High-availability web application with load balancer and database cluster" \
  --output-file ha-webapp.tf

# Using custom variables
proxmox-ai generate terraform \
  "Development environment" \
  --variables dev-vars.tfvars \
  --skill-level intermediate
```

### `proxmox-ai generate ansible`

Generate Ansible playbooks for configuration management.

**Usage:**
```bash
proxmox-ai generate ansible [OPTIONS] DESCRIPTION
```

**Options:**
- `--skill-level LEVEL`: Target skill level
- `--inventory FILE`: Ansible inventory file
- `--vault-file FILE`: Ansible vault file
- `--roles`: Generate with role structure
- `--tags TAGS`: Specify playbook tags

**Examples:**
```bash
# Basic web server configuration
proxmox-ai generate ansible --skill-level beginner \
  "Install and configure NGINX with basic security"

# Advanced security hardening
proxmox-ai generate ansible --skill-level expert \
  "CIS benchmark compliance automation with monitoring" \
  --roles --output-file security-hardening.yml

# Configuration with custom inventory
proxmox-ai generate ansible \
  "Database cluster setup with replication" \
  --inventory production-inventory.ini \
  --skill-level intermediate
```

### `proxmox-ai generate vm`

Generate VM configurations with specific requirements.

**Usage:**
```bash
proxmox-ai generate vm [OPTIONS] DESCRIPTION
```

**Options:**
- `--skill-level LEVEL`: Target skill level
- `--count NUMBER`: Number of VMs
- `--template TEMPLATE`: Base template to use
- `--network NETWORK`: Network configuration
- `--storage STORAGE`: Storage configuration

**Examples:**
```bash
# Single development VM
proxmox-ai generate vm --skill-level beginner \
  "Ubuntu development server with Docker"

# Multiple web servers for load balancing
proxmox-ai generate vm --skill-level intermediate \
  "Load-balanced web servers" \
  --count 3 --network "vmbr1" --template "ubuntu-22.04"

# High-performance computing cluster
proxmox-ai generate vm --skill-level expert \
  "HPC cluster nodes with RDMA networking" \
  --count 8 --network "high-performance"
```

### `proxmox-ai generate docker`

Generate Docker and Docker Compose configurations.

**Usage:**
```bash
proxmox-ai generate docker [OPTIONS] DESCRIPTION
```

**Options:**
- `--skill-level LEVEL`: Target skill level
- `--format FORMAT`: docker or compose
- `--multi-stage`: Use multi-stage builds
- `--security`: Include security best practices

**Examples:**
```bash
# Basic web application container
proxmox-ai generate docker --skill-level beginner \
  "Node.js web application with PostgreSQL database"

# Production-ready microservices
proxmox-ai generate docker --skill-level expert \
  "Microservices architecture with monitoring and logging" \
  --format compose --security --multi-stage
```

### `proxmox-ai generate kubernetes`

Generate Kubernetes manifests and configurations.

**Usage:**
```bash
proxmox-ai generate kubernetes [OPTIONS] DESCRIPTION
```

**Options:**
- `--skill-level LEVEL`: Target skill level
- `--namespace NAMESPACE`: Target Kubernetes namespace
- `--helm`: Generate Helm charts
- `--operators`: Include custom operators

**Examples:**
```bash
# Basic application deployment
proxmox-ai generate kubernetes --skill-level intermediate \
  "Web application with database and ingress"

# Complex microservices platform
proxmox-ai generate kubernetes --skill-level expert \
  "Event-driven microservices with service mesh" \
  --helm --operators --namespace production
```

## 🔍 Analysis and Optimization Commands

### `proxmox-ai explain`

Explain existing configurations in detail.

**Usage:**
```bash
proxmox-ai explain [OPTIONS] FILE
```

**Options:**
- `--skill-level LEVEL`: Explanation detail level
- `--section SECTION`: Explain specific section
- `--format FORMAT`: Output format (text, markdown, html)
- `--interactive`: Interactive explanation mode

**Examples:**
```bash
# Explain Terraform configuration for beginners
proxmox-ai explain --skill-level beginner terraform/main.tf

# Interactive explanation
proxmox-ai explain --interactive --skill-level intermediate config.yml

# Explain specific section
proxmox-ai explain terraform/network.tf --section "security_groups"
```

### `proxmox-ai optimize`

Optimize existing configurations for better performance or security.

**Usage:**
```bash
proxmox-ai optimize [OPTIONS] FILE
```

**Options:**
- `--skill-level LEVEL`: Optimization complexity
- `--focus AREA`: Focus area (performance, security, cost, reliability)
- `--backup`: Create backup before optimization
- `--apply`: Apply optimizations automatically

**Examples:**
```bash
# Optimize for performance
proxmox-ai optimize --focus performance \
  --skill-level intermediate infrastructure.tf

# Security-focused optimization
proxmox-ai optimize --focus security \
  --backup --skill-level expert production-config.yml

# Cost optimization
proxmox-ai optimize --focus cost \
  --apply infrastructure/
```

### `proxmox-ai validate`

Validate configurations for syntax and best practices.

**Usage:**
```bash
proxmox-ai validate [OPTIONS] FILE_OR_DIRECTORY
```

**Options:**
- `--strict`: Strict validation mode
- `--format FORMAT`: Output format (text, json, junit)
- `--fix`: Automatically fix issues where possible
- `--rules FILE`: Custom validation rules

**Examples:**
```bash
# Basic validation
proxmox-ai validate terraform/

# Strict validation with fixes
proxmox-ai validate --strict --fix ansible-playbooks/

# Custom validation rules
proxmox-ai validate --rules custom-rules.yaml infrastructure/
```

### `proxmox-ai security-review`

Perform security analysis of configurations.

**Usage:**
```bash
proxmox-ai security-review [OPTIONS] FILE_OR_DIRECTORY
```

**Options:**
- `--compliance STANDARD`: Compliance standard (cis, nist, soc2, gdpr)
- `--severity LEVEL`: Minimum severity to report
- `--output FILE`: Save report to file
- `--remediation`: Include remediation suggestions

**Examples:**
```bash
# Basic security review
proxmox-ai security-review infrastructure/

# CIS compliance check
proxmox-ai security-review --compliance cis \
  --remediation terraform/

# High-severity issues only
proxmox-ai security-review --severity high \
  --output security-report.json production/
```

## 💬 Interactive and Learning Commands

### `proxmox-ai chat`

Start interactive AI assistant session.

**Usage:**
```bash
proxmox-ai chat [OPTIONS]
```

**Options:**
- `--skill-level LEVEL`: Set conversation complexity
- `--context FILE`: Provide context files
- `--mode MODE`: Chat mode (general, troubleshooting, learning)
- `--save-session FILE`: Save chat session

**Examples:**
```bash
# General interactive session
proxmox-ai chat --skill-level intermediate

# Troubleshooting mode
proxmox-ai chat --mode troubleshooting --context logs.txt

# Learning session with saved history
proxmox-ai chat --mode learning --save-session learning-session.json
```

### `proxmox-ai ask`

Ask specific questions to the AI assistant.

**Usage:**
```bash
proxmox-ai ask [OPTIONS] "QUESTION"
```

**Options:**
- `--skill-level LEVEL`: Response complexity
- `--context FILE`: Provide context files
- `--format FORMAT`: Response format

**Examples:**
```bash
# Basic infrastructure question
proxmox-ai ask "How do I set up load balancing in Proxmox?"

# Complex architectural question
proxmox-ai ask --skill-level expert \
  "Design a disaster recovery strategy for multi-region deployment"

# Question with context
proxmox-ai ask --context current-config.tf \
  "How can I improve the security of this configuration?"
```

### `proxmox-ai learn`

Start interactive learning sessions on specific topics.

**Usage:**
```bash
proxmox-ai learn [OPTIONS] TOPIC
```

**Options:**
- `--skill-level LEVEL`: Learning level
- `--interactive`: Interactive learning mode
- `--duration MINUTES`: Session duration
- `--progress-tracking`: Track learning progress

**Examples:**
```bash
# Basic Terraform learning
proxmox-ai learn terraform-basics --skill-level beginner

# Interactive Kubernetes session
proxmox-ai learn kubernetes --interactive --skill-level intermediate

# Advanced security topics
proxmox-ai learn zero-trust-architecture --skill-level expert
```

### `proxmox-ai workshop`

Start skill-level appropriate workshops.

**Usage:**
```bash
proxmox-ai workshop [OPTIONS] SKILL_LEVEL
```

**Options:**
- `--topic TOPIC`: Specific workshop topic
- `--duration MINUTES`: Workshop duration
- `--hands-on`: Include hands-on exercises

**Examples:**
```bash
# Beginner workshop
proxmox-ai workshop beginner --hands-on

# Intermediate infrastructure workshop
proxmox-ai workshop intermediate --topic "multi-tier-applications"

# Expert workshop on advanced topics
proxmox-ai workshop expert --topic "chaos-engineering"
```

### `proxmox-ai tutorial`

Access step-by-step tutorials.

**Usage:**
```bash
proxmox-ai tutorial [OPTIONS] TUTORIAL_NAME
```

**Options:**
- `--list`: List available tutorials
- `--skill-level LEVEL`: Filter by skill level
- `--interactive`: Interactive tutorial mode

**Examples:**
```bash
# List all tutorials
proxmox-ai tutorial --list

# Beginner VM creation tutorial
proxmox-ai tutorial creating-your-first-vm --skill-level beginner

# Interactive security tutorial
proxmox-ai tutorial security-hardening --interactive
```

## 🔧 Configuration Management

### `proxmox-ai config`

Manage application configuration.

**Usage:**
```bash
proxmox-ai config [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**
- `init`: Initialize configuration
- `get KEY`: Get configuration value
- `set KEY VALUE`: Set configuration value
- `list`: List all configuration
- `reset`: Reset to defaults
- `export FILE`: Export configuration
- `import FILE`: Import configuration

**Examples:**
```bash
# Initialize configuration
proxmox-ai config init

# Set Proxmox connection details
proxmox-ai config set proxmox.host "192.168.1.50"
proxmox-ai config set proxmox.api_token "your-token-here"

# Configure AI settings
proxmox-ai config set ai.model "llama3.1:8b-q4_0"
proxmox-ai config set ai.skill_level "intermediate"
proxmox-ai config set ai.cache_enabled true

# Get current configuration
proxmox-ai config get ai.model
proxmox-ai config list

# Export/import configuration
proxmox-ai config export my-config.yaml
proxmox-ai config import my-config.yaml
```

## 🌐 Global Options

These options can be used with most commands:

### Skill Level Control
- `--skill-level {beginner|intermediate|expert}`: Adapt response complexity
- `--auto-skill`: Auto-detect optimal skill level based on context

### Output Control
- `--format {text|json|yaml|markdown}`: Output format
- `--output-file FILE`: Save output to file
- `--quiet`: Suppress non-essential output
- `--verbose`: Increase output verbosity
- `--color {auto|always|never}`: Control colored output

### AI Model Control
- `--model MODEL_NAME`: Use specific AI model
- `--temperature FLOAT`: Control response creativity (0.0-1.0)
- `--max-tokens INTEGER`: Limit response length
- `--no-cache`: Disable response caching
- `--no-stream`: Disable streaming responses

### Performance Options
- `--profile`: Enable performance profiling
- `--timeout SECONDS`: Set operation timeout
- `--parallel`: Enable parallel processing where applicable

### Security Options
- `--secure-mode`: Enable maximum security mode
- `--no-audit-log`: Disable audit logging (not recommended)
- `--offline`: Ensure complete offline operation

## 📝 Examples by Skill Level

### Beginner Examples

```bash
# Generate your first VM
proxmox-ai generate terraform --skill-level beginner \
  "Simple Ubuntu server for learning web development"

# Understand existing configuration
proxmox-ai explain --skill-level beginner terraform/main.tf

# Ask basic questions
proxmox-ai ask --skill-level beginner \
  "What is the difference between CPU cores and memory in a VM?"

# Start learning session
proxmox-ai learn terraform-basics --skill-level beginner
```

### Intermediate Examples

```bash
# Generate multi-tier application
proxmox-ai generate terraform --skill-level intermediate \
  "Web application with load balancer, app servers, and database"

# Optimize existing infrastructure
proxmox-ai optimize --focus performance \
  --skill-level intermediate infrastructure.tf

# Security review
proxmox-ai security-review --compliance cis \
  --skill-level intermediate production/

# Generate Ansible automation
proxmox-ai generate ansible --skill-level intermediate \
  "Automated deployment with monitoring and backup"
```

### Expert Examples

```bash
# Generate enterprise architecture
proxmox-ai generate terraform --skill-level expert \
  "Multi-region, highly available, auto-scaling platform with disaster recovery"

# Advanced optimization
proxmox-ai optimize --focus "performance,security,cost" \
  --skill-level expert --apply enterprise-infrastructure/

# Complex troubleshooting
proxmox-ai troubleshoot --skill-level expert \
  --context "metrics.json,logs.txt" \
  "Intermittent performance issues in distributed application"

# Architecture consultation
proxmox-ai ask --skill-level expert \
  "Design zero-trust security architecture for financial services platform"
```

## 🆘 Help and Documentation

### Getting Help

```bash
# General help
proxmox-ai --help

# Command-specific help
proxmox-ai generate --help
proxmox-ai config --help

# Show examples for a command
proxmox-ai generate terraform --examples

# Interactive help
proxmox-ai help --interactive
```

### Built-in Documentation

```bash
# Show available documentation
proxmox-ai docs --list

# Open specific documentation
proxmox-ai docs installation
proxmox-ai docs troubleshooting

# Search documentation
proxmox-ai docs --search "networking"
```

## 🔍 Troubleshooting Commands

```bash
# System diagnostics
proxmox-ai diagnose

# AI service troubleshooting
proxmox-ai troubleshoot-ai

# Connection testing
proxmox-ai test-connection --all

# Performance debugging
proxmox-ai debug-performance --duration 60

# Log analysis
proxmox-ai analyze-logs --file application.log
```

## 📊 Monitoring and Metrics Commands

```bash
# System metrics
proxmox-ai metrics --live

# AI performance metrics
proxmox-ai ai-metrics --export metrics.json

# Usage statistics
proxmox-ai usage-stats --timeframe "last-week"

# Resource utilization
proxmox-ai resource-usage --detailed
```

---

**Note:** This CLI reference covers the complete command set. Commands are designed to be intuitive and self-documenting. Use `--help` with any command to get detailed usage information and examples.

For more detailed guides, see:
- [Beginner Guide](user-guides/beginner.md)
- [Intermediate Guide](user-guides/intermediate.md)
- [Expert Guide](user-guides/expert.md)
- [Installation Guide](operations/installation.md)