# Hardware Compatibility Troubleshooting Guide

This guide helps you diagnose and resolve hardware-specific issues with the Proxmox AI Infrastructure Assistant.

## 🔍 Hardware Requirements Quick Check

### Minimum System Requirements

```bash
# Check if your system meets minimum requirements
proxmox-ai hardware-info --check-requirements

# Basic system information
proxmox-ai system-info --hardware
```

| Component | Minimum | Recommended | High Performance |
|-----------|---------|-------------|------------------|
| **RAM** | 4GB | 8GB | 16GB+ |
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **Storage** | 10GB free | 20GB free | 50GB+ free |
| **GPU** | None | Optional | NVIDIA/AMD |

## 💾 Memory Issues

### Insufficient RAM

**Symptoms:**
- System becomes unresponsive during AI operations
- Out of memory errors
- Swap thrashing
- Model loading failures

**Diagnosis:**
```bash
# Check current memory usage
free -h

# Monitor memory during AI operations
proxmox-ai performance-stats --live --memory-focus

# Check for memory leaks
ps aux --sort=-%mem | head -10
```

**Solutions by System Memory:**

#### 4GB RAM Systems
```bash
# Use the smallest available model
ollama pull llama3.2:3b-instruct-q4_0
proxmox-ai config set ai.model "llama3.2:3b-instruct-q4_0"

# Enable aggressive memory optimization
proxmox-ai config set ai.memory_optimize aggressive
proxmox-ai config set ai.max_memory_gb 2.5

# Disable memory-intensive features
proxmox-ai config set ai.cache_enabled false
proxmox-ai config set ai.use_mmap false
```

#### 6-8GB RAM Systems
```bash
# Use balanced model
ollama pull llama3.1:8b-instruct-q4_0
proxmox-ai config set ai.model "llama3.1:8b-instruct-q4_0"

# Moderate memory optimization
proxmox-ai config set ai.memory_optimize moderate
proxmox-ai config set ai.max_memory_gb 5

# Enable selective caching
proxmox-ai config set ai.cache_enabled true
proxmox-ai config set ai.cache_size_mb 512
```

#### 16GB+ RAM Systems
```bash
# Use high-quality model
ollama pull llama3.1:8b-instruct-q8_0
proxmox-ai config set ai.model "llama3.1:8b-instruct-q8_0"

# Full feature set enabled
proxmox-ai config set ai.memory_optimize minimal
proxmox-ai config set ai.max_memory_gb 12
proxmox-ai config set ai.cache_enabled true
proxmox-ai config set ai.cache_size_mb 2048
```

### Memory Leak Detection

**Symptoms:**
- Gradually increasing memory usage
- System slowdown over time
- Need to restart services frequently

**Diagnosis:**
```bash
# Monitor memory usage over time
proxmox-ai monitor-memory --duration 3600 --interval 60

# Check for memory leaks in Ollama
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | grep ollama

# Memory profiling
valgrind --tool=memcheck --leak-check=full ollama serve
```

**Solutions:**
```bash
# Enable automatic memory cleanup
proxmox-ai config set ai.memory_cleanup_interval 300

# Restart Ollama periodically
proxmox-ai config set ai.restart_interval 3600

# Enable memory monitoring
proxmox-ai config set monitoring.memory_alerts true
```

## 🖥️ CPU Compatibility

### CPU Architecture Issues

**Symptoms:**
- "Illegal instruction" errors
- Models fail to load
- Extremely slow performance

**Diagnosis:**
```bash
# Check CPU information
lscpu

# Check CPU features
cat /proc/cpuinfo | grep flags

# Test CPU compatibility
proxmox-ai hardware-info --cpu-features
```

**Solutions by CPU Type:**

#### ARM64 (Apple Silicon, ARM servers)
```bash
# Use ARM-optimized models
ollama pull llama3.1:8b-instruct-q4_0

# Enable ARM optimizations
proxmox-ai config set ai.cpu_arch arm64
proxmox-ai config set ai.optimize_for_arm true

# Check for ARM-specific issues
proxmox-ai diagnose --arch arm64
```

#### Older x86_64 CPUs
```bash
# Disable advanced CPU features
proxmox-ai config set ai.use_avx2 false
proxmox-ai config set ai.use_fma false

# Use compatibility mode
proxmox-ai config set ai.cpu_compatibility_mode true

# Reduce thread count for older CPUs
proxmox-ai config set ai.cpu_threads 2
```

#### Modern x86_64 CPUs
```bash
# Enable all optimizations
proxmox-ai config set ai.use_avx2 true
proxmox-ai config set ai.use_fma true
proxmox-ai config set ai.use_avx512 auto

# Optimize thread usage
proxmox-ai optimize-hardware --cpu-focus
```

### CPU Performance Issues

**Symptoms:**
- Very slow AI responses
- High CPU usage
- System becomes unresponsive

**Solutions:**

1. **Thread Optimization:**
```bash
# Auto-detect optimal thread count
proxmox-ai optimize-hardware --cpu-threads auto

# Manual thread configuration
proxmox-ai config set ai.cpu_threads 4

# Check thread efficiency
proxmox-ai benchmark --test cpu-scaling
```

2. **CPU Frequency Scaling:**
```bash
# Check current CPU governor
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Set performance governor
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Or use cpufrequtils
sudo cpufreq-set -g performance
```

3. **Process Priority:**
```bash
# Run with higher priority
sudo renice -10 $(pgrep ollama)

# Or start with high priority
sudo nice -n -10 ollama serve
```

## 🎮 GPU Compatibility

### GPU Detection Issues

**Symptoms:**
- GPU not detected by Ollama
- Falling back to CPU processing
- CUDA/OpenCL errors

**Diagnosis:**
```bash
# Check GPU availability
proxmox-ai hardware-info --gpu-detailed

# NVIDIA GPU check
nvidia-smi

# AMD GPU check
rocm-smi

# Intel GPU check
intel_gpu_top
```

### NVIDIA GPU Issues

**Common Problems and Solutions:**

1. **CUDA Installation:**
```bash
# Check CUDA version
nvcc --version

# Install CUDA (Ubuntu)
sudo apt update
sudo apt install nvidia-cuda-toolkit

# Verify CUDA installation
nvidia-smi
```

2. **Driver Issues:**
```bash
# Check driver version
nvidia-smi

# Install latest drivers (Ubuntu)
sudo apt install nvidia-driver-535

# Reboot after driver installation
sudo reboot
```

3. **Memory Issues:**
```bash
# Check GPU memory
nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv

# Limit GPU memory usage
proxmox-ai config set ai.gpu_memory_limit 6

# Enable GPU memory optimization
proxmox-ai config set ai.gpu_optimize true
```

### AMD GPU Issues

**ROCm Setup:**
```bash
# Install ROCm (Ubuntu)
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/debian/ ubuntu main' | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update
sudo apt install rocm-dev

# Configure ROCm
echo 'export PATH=$PATH:/opt/rocm/bin' >> ~/.bashrc
source ~/.bashrc

# Test ROCm
rocm-smi
```

### Intel GPU Issues

**Intel GPU Support:**
```bash
# Install Intel GPU drivers
sudo apt install intel-gpu-tools

# Check Intel GPU status
intel_gpu_top

# Configure for AI workloads
proxmox-ai config set ai.intel_gpu_enabled true
```

## 💽 Storage Issues

### Insufficient Storage Space

**Symptoms:**
- Model download failures
- "No space left on device" errors
- Application crashes during model loading

**Diagnosis:**
```bash
# Check available space
df -h

# Check model storage location
proxmox-ai config get ai.models_path
du -sh ~/.ollama/models/

# Check for large files
find ~/.ollama -size +1G -type f
```

**Solutions:**

1. **Clean Up Old Models:**
```bash
# List installed models
ollama list

# Remove unused models
ollama rm old-model-name

# Clean up model cache
proxmox-ai clean-cache --models
```

2. **Move Models to Larger Drive:**
```bash
# Create new models directory
mkdir /path/to/larger/drive/ollama-models

# Move existing models
mv ~/.ollama/models/* /path/to/larger/drive/ollama-models/

# Update configuration
export OLLAMA_MODELS=/path/to/larger/drive/ollama-models
proxmox-ai config set ai.models_path "/path/to/larger/drive/ollama-models"
```

3. **Use Smaller Models:**
```bash
# Switch to smaller model
ollama pull llama3.2:3b-instruct-q4_0
proxmox-ai config set ai.model "llama3.2:3b-instruct-q4_0"

# Remove larger models
ollama rm llama3.1:70b-instruct-q4_0
```

### Storage Performance Issues

**Symptoms:**
- Slow model loading
- High disk I/O during operations
- System becomes unresponsive during model access

**Solutions:**

1. **SSD Optimization:**
```bash
# Check if using SSD
lsblk -d -o name,rota

# Enable SSD optimizations
proxmox-ai config set storage.ssd_optimizations true

# Enable model preloading
proxmox-ai config set ai.preload_models true
```

2. **I/O Scheduling:**
```bash
# Check current I/O scheduler
cat /sys/block/sda/queue/scheduler

# Use deadline scheduler for better AI workload performance
echo deadline | sudo tee /sys/block/sda/queue/scheduler
```

## 🌐 Network Hardware Issues

### Network Interface Problems

**Symptoms:**
- Cannot connect to Proxmox host
- Network timeouts
- SSH connection failures

**Diagnosis:**
```bash
# Check network interfaces
ip addr show

# Test connectivity
ping your-proxmox-host

# Check routing
ip route show

# DNS resolution test
nslookup your-proxmox-host
```

**Solutions:**

1. **Network Configuration:**
```bash
# Configure static IP (if needed)
sudo ip addr add 192.168.1.100/24 dev eth0

# Add default route
sudo ip route add default via 192.168.1.1

# Update DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

2. **Network Performance:**
```bash
# Test network performance to Proxmox host
iperf3 -c your-proxmox-host

# Optimize network settings
proxmox-ai config set network.tcp_window_size 65536
proxmox-ai config set network.connection_pooling true
```

## 🔧 Hardware-Specific Optimizations

### Intel Systems

```bash
# Enable Intel-specific optimizations
proxmox-ai config set hardware.intel_optimizations true

# Use Intel MKL if available
proxmox-ai config set ai.use_mkl true

# Enable Intel GPU (if available)
proxmox-ai config set ai.intel_gpu_enabled auto
```

### AMD Systems

```bash
# Enable AMD-specific optimizations
proxmox-ai config set hardware.amd_optimizations true

# Use ROCm for GPU acceleration
proxmox-ai config set ai.use_rocm true

# Optimize for AMD CPUs
proxmox-ai config set ai.amd_cpu_optimizations true
```

### Apple Silicon (M1/M2/M3)

```bash
# Enable Apple Silicon optimizations
proxmox-ai config set hardware.apple_silicon true

# Use Metal Performance Shaders
proxmox-ai config set ai.use_metal true

# Optimize memory usage for unified memory
proxmox-ai config set ai.unified_memory_optimization true
```

## 📊 Performance Benchmarking

### Hardware Performance Testing

```bash
# Comprehensive hardware benchmark
proxmox-ai benchmark --full --output hardware-benchmark.json

# CPU-specific benchmark
proxmox-ai benchmark --test cpu --duration 300

# Memory benchmark
proxmox-ai benchmark --test memory --pattern random

# Storage benchmark
proxmox-ai benchmark --test storage --target ~/.ollama/models

# GPU benchmark (if available)
proxmox-ai benchmark --test gpu --duration 120
```

### Model Performance by Hardware

```bash
# Test all models on current hardware
proxmox-ai benchmark-models --all --hardware-report

# Compare performance across different configurations
proxmox-ai benchmark-models --compare-configs config1.yaml config2.yaml

# Generate hardware-specific recommendations
proxmox-ai hardware-info --performance-recommendations
```

## 🚨 Emergency Hardware Procedures

### System Recovery

**When hardware issues cause system instability:**

1. **Safe Mode Operation:**
```bash
# Minimal configuration for unstable systems
proxmox-ai config set ai.safe_mode true
proxmox-ai config set ai.model "llama3.2:3b-instruct-q4_0"
proxmox-ai config set ai.cpu_threads 1
proxmox-ai config set ai.max_memory_gb 2
```

2. **Hardware Diagnostics:**
```bash
# Comprehensive hardware test
proxmox-ai diagnose --hardware --detailed

# Memory test
memtest86+ (reboot required)

# CPU stress test
stress-ng --cpu 8 --timeout 60s

# Storage test
badblocks -v /dev/sda
```

### Thermal Issues

**Symptoms:**
- System shutdowns during AI operations
- CPU/GPU throttling
- Performance degradation over time

**Solutions:**

1. **Temperature Monitoring:**
```bash
# Monitor system temperatures
sensors

# Watch temperatures during AI operations
proxmox-ai monitor --temperature --duration 300

# Check thermal throttling
dmesg | grep -i thermal
```

2. **Thermal Management:**
```bash
# Reduce CPU load
proxmox-ai config set ai.cpu_threads 2
proxmox-ai config set ai.thermal_protection true

# Enable automatic throttling
proxmox-ai config set ai.auto_throttle true

# Set temperature limits
proxmox-ai config set ai.max_temperature 80
```

## 📱 Platform-Specific Issues

### Windows-Specific Issues

```powershell
# Check Windows version compatibility
systeminfo

# Install Visual C++ Redistributables
# Download from Microsoft website

# Windows Defender exclusions
Add-MpPreference -ExclusionPath "C:\Users\%USERNAME%\.ollama"

# Check Windows firewall
netsh firewall show state
```

### macOS-Specific Issues

```bash
# Check macOS version
sw_vers

# Install Xcode Command Line Tools
xcode-select --install

# Check system integrity
sudo fsck -fy

# Reset network settings (if needed)
sudo dscacheutil -flushcache
```

### Linux Distribution Issues

#### Ubuntu/Debian
```bash
# Update package database
sudo apt update && sudo apt upgrade

# Install build essentials
sudo apt install build-essential

# Fix broken dependencies
sudo apt --fix-broken install
```

#### CentOS/RHEL/Fedora
```bash
# Update packages
sudo yum update

# Install development tools
sudo yum groupinstall "Development Tools"

# Check SELinux status
sestatus
```

## 🔍 Advanced Hardware Debugging

### Low-Level Diagnostics

```bash
# Hardware information
sudo lshw -short

# PCI devices
lspci -v

# USB devices
lsusb -v

# Block devices
lsblk -a

# CPU information
sudo dmidecode -t processor

# Memory information
sudo dmidecode -t memory
```

### Performance Profiling

```bash
# System-wide profiling
perf record -g proxmox-ai generate terraform "test config"
perf report

# Memory profiling
valgrind --tool=massif proxmox-ai ask "test question"

# I/O profiling
iotop -p $(pgrep ollama)
```

---

**Remember**: Hardware compatibility issues are often resolved by using appropriate model sizes for your system's capabilities and ensuring drivers are up to date.