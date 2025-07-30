# AI Models Troubleshooting Guide

This guide helps you diagnose and resolve issues with local AI models, hardware compatibility, and performance optimization.

## 🔍 Quick Diagnosis

### Check System Status

```bash
# Overall system health
proxmox-ai status --detailed

# AI-specific status
proxmox-ai ai-status --health-check

# Hardware analysis
proxmox-ai hardware-info --recommendations
```

## 🤖 Ollama Service Issues

### Ollama Not Running

**Symptoms:**
- "Local AI model not available" errors
- Connection refused to localhost:11434
- AI commands timeout

**Diagnosis:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check system processes
ps aux | grep ollama

# Check service status (Linux with systemd)
systemctl status ollama
```

**Solutions:**

1. **Start Ollama manually:**
```bash
# Start Ollama in background
ollama serve &

# Or start as systemd service
systemctl start ollama
systemctl enable ollama
```

2. **Fix port conflicts:**
```bash
# Check what's using port 11434
netstat -tulpn | grep 11434

# Use alternative port
OLLAMA_HOST=0.0.0.0:11435 ollama serve

# Update configuration
proxmox-ai config set ai.ollama_host "http://localhost:11435"
```

3. **Permission issues:**
```bash
# Fix permissions for Ollama user
sudo chown -R ollama:ollama /var/lib/ollama

# Or run as current user
OLLAMA_MODELS=$HOME/.ollama/models ollama serve
```

### Ollama Installation Problems

**macOS Installation Issues:**
```bash
# Manual installation
curl -fsSL https://ollama.ai/install.sh | sh

# Or using Homebrew
brew install ollama

# Verify installation
ollama --version
```

**Linux Installation Issues:**
```bash
# Check installation
which ollama

# Manual download and install
curl -L https://ollama.ai/download/ollama-linux-amd64 -o ollama
chmod +x ollama
sudo mv ollama /usr/local/bin/

# Add to systemd
sudo curl -L https://raw.githubusercontent.com/ollama/ollama/main/ollama.service -o /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
```

**Windows Installation Issues:**
```bash
# Using winget
winget install Ollama.Ollama

# Manual installation from ollama.ai
# Download and run the installer
```

## 🧠 AI Model Issues

### Model Not Found

**Symptoms:**
- "Model not available" errors
- Empty model list
- Failed to load model

**Diagnosis:**
```bash
# List available models
ollama list

# Check model status
ollama show llama3.1:8b-instruct-q4_0

# Check disk space
df -h ~/.ollama/models
```

**Solutions:**

1. **Download missing models:**
```bash
# Download recommended model
proxmox-ai optimize-hardware --auto

# Manual model download
ollama pull llama3.1:8b-instruct-q4_0

# List available models for download
ollama list --available
```

2. **Fix corrupted models:**
```bash
# Remove corrupted model
ollama rm llama3.1:8b-instruct-q4_0

# Re-download
ollama pull llama3.1:8b-instruct-q4_0

# Verify model integrity
ollama run llama3.1:8b-instruct-q4_0 "Hello, test message"
```

3. **Storage space issues:**
```bash
# Check available space
df -h ~/.ollama/

# Clean up old models
ollama rm unused-model-name

# Move models to larger drive
export OLLAMA_MODELS=/path/to/larger/drive/models
```

### Model Loading Slowly

**Symptoms:**
- Long delays before first response
- Timeout errors on first request
- High memory usage during loading

**Solutions:**

1. **Optimize model selection:**
```bash
# Use hardware-appropriate model
proxmox-ai hardware-info --compare-models

# Switch to smaller model for limited hardware
proxmox-ai config set ai.model "llama3.2:3b-instruct-q4_0"
```

2. **Enable model warming:**
```bash
# Pre-warm model at startup
proxmox-ai warmup-model

# Enable automatic warming
proxmox-ai config set ai.auto_warmup true
```

3. **Memory optimization:**
```bash
# Enable memory mapping
proxmox-ai config set ai.use_mmap true

# Enable memory locking
proxmox-ai config set ai.use_mlock true

# Adjust memory limit
proxmox-ai config set ai.max_memory_gb 6
```

## 💻 Hardware Compatibility Issues

### Insufficient Memory

**Symptoms:**
- Out of memory errors
- System becomes unresponsive
- Model fails to load

**Diagnosis:**
```bash
# Check memory usage
free -h

# Monitor memory during model loading
proxmox-ai performance-stats --live --duration 60

# Get memory recommendations
proxmox-ai hardware-info --recommendations
```

**Solutions:**

1. **Use smaller models:**
```bash
# For 4-6GB systems
ollama pull llama3.2:3b-instruct-q4_0
proxmox-ai config set ai.model "llama3.2:3b-instruct-q4_0"

# For 6-8GB systems
ollama pull llama3.1:8b-instruct-q4_0
proxmox-ai config set ai.model "llama3.1:8b-instruct-q4_0"
```

2. **Configure swap (temporary solution):**
```bash
# Add swap space (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

3. **Optimize system memory usage:**
```bash
# Close unnecessary applications
# Configure memory limits
proxmox-ai config set ai.max_memory_gb 4

# Enable memory optimization
proxmox-ai config set ai.memory_optimize true
```

### CPU Performance Issues

**Symptoms:**
- Very slow response times
- High CPU usage
- System becomes unresponsive

**Solutions:**

1. **Optimize CPU usage:**
```bash
# Auto-detect optimal CPU threads
proxmox-ai optimize-hardware --auto

# Manual thread configuration
proxmox-ai config set ai.cpu_threads 4

# Enable CPU optimization
proxmox-ai config set ai.cpu_optimize true
```

2. **Process priority adjustment:**
```bash
# Run with higher priority (be careful)
sudo nice -n -10 ollama serve

# Or adjust existing process
sudo renice -10 $(pgrep ollama)
```

### GPU Issues

**Symptoms:**
- GPU not detected
- CUDA errors
- Slower than expected performance

**Diagnosis:**
```bash
# Check GPU availability
nvidia-smi

# Check CUDA installation
nvcc --version

# Test GPU with Ollama
OLLAMA_GPU=1 ollama run llama3.1:8b-instruct-q4_0 "Test GPU"
```

**Solutions:**

1. **Enable GPU acceleration:**
```bash
# Auto-detect and enable GPU
proxmox-ai config set ai.use_gpu auto

# Force GPU usage
proxmox-ai config set ai.use_gpu true

# Check GPU status
proxmox-ai gpu-stats
```

2. **Fix CUDA installation:**
```bash
# Install CUDA drivers (Ubuntu)
sudo apt update
sudo apt install nvidia-driver-470 nvidia-cuda-toolkit

# Verify installation
nvidia-smi
nvcc --version
```

3. **GPU memory issues:**
```bash
# Limit GPU memory usage
proxmox-ai config set ai.gpu_memory_limit 6

# Enable GPU memory optimization
proxmox-ai config set ai.gpu_optimize true
```

## 🚀 Performance Optimization

### Slow Response Times

**Symptoms:**
- Responses take longer than expected
- Timeouts on complex requests
- Poor user experience

**Solutions:**

1. **Enable response caching:**
```bash
# Enable intelligent caching
proxmox-ai config set ai.cache_enabled true

# Check cache performance
proxmox-ai performance-stats --cache-stats

# Clear cache if needed
proxmox-ai clear-cache
```

2. **Optimize request parameters:**
```bash
# Reduce token limit for faster responses
proxmox-ai config set ai.max_tokens 512

# Adjust temperature for consistency
proxmox-ai config set ai.temperature 0.1

# Enable streaming responses
proxmox-ai config set ai.stream_response true
```

3. **Hardware optimization:**
```bash
# Run full hardware optimization
proxmox-ai optimize-hardware --auto

# Benchmark different models
proxmox-ai benchmark-models --duration 30

# Monitor performance metrics
proxmox-ai performance-stats --export metrics.json
```

### High Resource Usage

**Symptoms:**
- High CPU/memory usage
- System slowdown
- Other applications affected

**Solutions:**

1. **Resource limiting:**
```bash
# Set CPU thread limit
proxmox-ai config set ai.cpu_threads 2

# Set memory limit
proxmox-ai config set ai.max_memory_gb 4

# Enable resource monitoring
proxmox-ai config set performance.resource_monitoring true
```

2. **Process scheduling:**
```bash
# Use cgroups to limit resources (Linux)
sudo cgcreate -g cpu,memory:/proxmox-ai
sudo cgset -r cpu.cfs_quota_us=50000 /proxmox-ai
sudo cgset -r memory.limit_in_bytes=4G /proxmox-ai

# Run with resource limits
sudo cgexec -g cpu,memory:/proxmox-ai ollama serve
```

## 🔧 Configuration Issues

### Invalid Configuration

**Symptoms:**
- Configuration errors on startup
- Invalid parameter warnings
- Unexpected behavior

**Solutions:**

1. **Reset configuration:**
```bash
# Reset to defaults
proxmox-ai config reset

# Backup current config
proxmox-ai config export backup-config.yaml

# Import known good config
proxmox-ai config import good-config.yaml
```

2. **Validate configuration:**
```bash
# Check configuration validity
proxmox-ai config validate

# List current configuration
proxmox-ai config list

# Check specific settings
proxmox-ai config get ai.model
```

### Network Configuration Issues

**Symptoms:**
- Cannot connect to Ollama
- Network timeouts
- Firewall blocking connections

**Solutions:**

1. **Check network connectivity:**
```bash
# Test local connection
curl http://localhost:11434/api/tags

# Test with different host/port
curl http://127.0.0.1:11434/api/tags

# Check firewall rules
sudo ufw status
```

2. **Configure network settings:**
```bash
# Set custom Ollama host
proxmox-ai config set ai.ollama_host "http://127.0.0.1:11434"

# Increase timeout
proxmox-ai config set ai.timeout 60

# Enable connection retry
proxmox-ai config set ai.retry_enabled true
```

## 🛠️ Advanced Troubleshooting

### Debug Mode

**Enable detailed logging:**
```bash
# Enable debug logging
proxmox-ai config set logging.level DEBUG

# Run with verbose output
proxmox-ai --verbose generate terraform "test configuration"

# Check log files
tail -f ~/.proxmox-ai/logs/application.log
```

### Model Debugging

**Test model functionality:**
```bash
# Direct model testing
ollama run llama3.1:8b-instruct-q4_0 "Simple test question"

# Test through application
proxmox-ai ask "Simple test question" --debug

# Benchmark model performance
proxmox-ai benchmark-models --models "llama3.1:8b-instruct-q4_0" --duration 10
```

### System Resource Analysis

**Monitor system performance:**
```bash
# System resource monitoring
htop

# Memory usage analysis
smem -r

# Disk I/O monitoring
iotop

# Network monitoring
netstat -tulpn | grep 11434
```

## 📊 Performance Benchmarking

### Model Performance Testing

```bash
# Comprehensive model benchmarking
proxmox-ai benchmark-models --all --output benchmark-results.json

# Compare models on your hardware
proxmox-ai hardware-info --compare-models --detailed

# Performance regression testing
proxmox-ai benchmark-models --baseline baseline-results.json
```

### Hardware Performance Analysis

```bash
# CPU performance test
proxmox-ai benchmark --test cpu --duration 60

# Memory performance test
proxmox-ai benchmark --test memory --duration 30

# Storage performance test
proxmox-ai benchmark --test storage --target ~/.ollama/models
```

## 🚨 Emergency Procedures

### Complete System Reset

**When everything fails:**
```bash
# Stop all services
sudo systemctl stop ollama
pkill -f "proxmox-ai"

# Backup important data
cp -r ~/.proxmox-ai/config ~/.proxmox-ai/config.backup

# Reset application
proxmox-ai config reset --all
proxmox-ai setup --force

# Reinstall models
ollama pull llama3.1:8b-instruct-q4_0

# Test basic functionality
proxmox-ai status
proxmox-ai ask "Test question"
```

### Recovery from Corruption

**Model corruption recovery:**
```bash
# Remove all models
ollama rm --all

# Clear model cache
rm -rf ~/.ollama/models/*

# Re-download models
proxmox-ai optimize-hardware --auto --force-download

# Verify integrity
proxmox-ai ai-status --health-check
```

## 📞 Getting Help

### Diagnostic Information Collection

```bash
# Generate diagnostic report
proxmox-ai diagnose --output diagnostic-report.json

# System information
proxmox-ai system-info --detailed

# Performance metrics
proxmox-ai performance-stats --export performance-data.json
```

### Community Support

- **GitHub Issues**: Report bugs and get help
- **Discussions**: Community Q&A
- **Documentation**: Comprehensive guides and examples

### Professional Support

For enterprise environments:
- Technical support for production deployments
- Custom optimization consulting
- Priority issue resolution

---

**Remember**: Most issues can be resolved by ensuring Ollama is running, models are properly downloaded, and hardware resources are adequate for the selected model size.