#!/bin/bash
# Proxmox AI Assistant Startup Script
# This script helps you start the assistant with proper environment setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🤖 Proxmox AI Infrastructure Assistant${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is open
check_port() {
    nc -z localhost "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking Prerequisites...${NC}"

# Check Python version
if command_exists python3.12; then
    PYTHON_CMD="python3.12"
    print_status "Python 3.12+ found"
elif command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(echo "$PYTHON_VERSION >= 3.12" | bc -l) )); then
        PYTHON_CMD="python3"
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.12+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3.12+ not found. Please install Python 3.12 or later."
    exit 1
fi

# Check if we're in the project directory
if [[ ! -f "$PROJECT_DIR/pyproject.toml" ]]; then
    print_error "Please run this script from the project directory"
    exit 1
fi

# Check virtual environment
echo ""
echo -e "${BLUE}🐍 Setting Up Python Environment...${NC}"

if [[ ! -d "$PROJECT_DIR/venv" ]]; then
    print_info "Creating virtual environment..."
    cd "$PROJECT_DIR"
    $PYTHON_CMD -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
if [[ -f "$PROJECT_DIR/venv/bin/activate" ]]; then
    source "$PROJECT_DIR/venv/bin/activate"
    print_status "Virtual environment activated"
elif [[ -f "$PROJECT_DIR/venv/Scripts/activate" ]]; then
    source "$PROJECT_DIR/venv/Scripts/activate"
    print_status "Virtual environment activated (Windows)"
else
    print_error "Cannot find virtual environment activation script"
    exit 1
fi

# Install/update dependencies
if [[ ! -f "$PROJECT_DIR/venv/.dependencies_installed" ]] || [[ "$1" == "--force-install" ]]; then
    print_info "Installing dependencies..."
    cd "$PROJECT_DIR"
    pip install --upgrade pip
    pip install -e .
    touch "$PROJECT_DIR/venv/.dependencies_installed"
    print_status "Dependencies installed"
else
    print_status "Dependencies already installed (use --force-install to reinstall)"
fi

# Check Ollama
echo ""
echo -e "${BLUE}🧠 Checking Local AI (Ollama)...${NC}"

if ! command_exists ollama; then
    print_warning "Ollama not found. Installing Ollama..."
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
        print_status "Ollama installed"
    else
        print_error "Please install Ollama manually from https://ollama.ai/"
        exit 1
    fi
fi

# Check if Ollama is running
if ! check_port 11434; then
    print_info "Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 3
    
    if check_port 11434; then
        print_status "Ollama service started (PID: $OLLAMA_PID)"
    else
        print_error "Failed to start Ollama service"
        exit 1
    fi
else
    print_status "Ollama service is running"
fi

# Check if AI model is available
echo ""
echo -e "${BLUE}🎯 Checking AI Model...${NC}"

# Get hardware recommendation
print_info "Analyzing hardware for optimal model selection..."
cd "$PROJECT_DIR"

if $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
from proxmox_ai.core.hardware_detector import hardware_detector
rec = hardware_detector.get_model_recommendation()
print(f'Recommended model: {rec.model_name}')
print(f'Memory usage: {rec.memory_usage_gb}GB')
print(f'Performance: {rec.performance_tier}')
" 2>/dev/null; then
    print_status "Hardware analysis completed"
else
    print_warning "Hardware analysis failed, using default model"
fi

# Check if model is downloaded
AVAILABLE_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' ' ')

if [[ -z "$AVAILABLE_MODELS" ]]; then
    print_info "No AI models found. Downloading recommended model..."
    
    # Detect system RAM to choose appropriate model
    if command_exists free; then
        TOTAL_RAM_GB=$(($(free -m | awk 'NR==2{print $2}') / 1024))
    elif command_exists sysctl; then
        TOTAL_RAM_GB=$(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))
    else
        TOTAL_RAM_GB=8  # Default assumption
    fi
    
    if (( TOTAL_RAM_GB < 6 )); then
        MODEL="llama3.2:3b-instruct-q4_0"
        print_info "Downloading compact model for ${TOTAL_RAM_GB}GB RAM: $MODEL"
    elif (( TOTAL_RAM_GB < 12 )); then
        MODEL="llama3.1:8b-instruct-q4_0"
        print_info "Downloading standard model for ${TOTAL_RAM_GB}GB RAM: $MODEL"
    else
        MODEL="llama3.1:8b-instruct-q8_0"
        print_info "Downloading high-quality model for ${TOTAL_RAM_GB}GB RAM: $MODEL"
    fi
    
    ollama pull "$MODEL"
    print_status "AI model downloaded: $MODEL"
else
    print_status "AI models available: $AVAILABLE_MODELS"
fi

# Check configuration
echo ""
echo -e "${BLUE}⚙️ Checking Configuration...${NC}"

if [[ ! -f "$HOME/.config/proxmox-ai/config.yaml" ]] && [[ ! -f "$PROJECT_DIR/config/config.yaml" ]]; then
    print_warning "No configuration found. Run 'proxmox-ai config init' after startup."
else
    print_status "Configuration found"
fi

# Run health check
echo ""
echo -e "${BLUE}🏥 Running Health Check...${NC}"

cd "$PROJECT_DIR"
if timeout 30 $PYTHON_CMD -m src.proxmox_ai.cli.main status >/dev/null 2>&1; then
    print_status "Health check passed"
else
    print_warning "Health check incomplete - may need configuration"
fi

# Start interactive mode or show usage
echo ""
echo -e "${GREEN}🎉 Proxmox AI Assistant is Ready!${NC}"
echo ""
echo -e "${BLUE}Quick Start Options:${NC}"
echo ""
echo "1. Interactive Chat Mode:"
echo -e "   ${YELLOW}proxmox-ai chat${NC}"
echo ""
echo "2. Generate Infrastructure:"
echo -e "   ${YELLOW}proxmox-ai generate terraform \"Create a web server cluster\"${NC}"
echo ""
echo "3. System Status:"
echo -e "   ${YELLOW}proxmox-ai status${NC}"
echo ""
echo "4. Configuration Setup:"
echo -e "   ${YELLOW}proxmox-ai config init${NC}"
echo ""
echo "5. Get Help:"
echo -e "   ${YELLOW}proxmox-ai --help${NC}"
echo ""

# Auto-start based on arguments
case "${1:-}" in
    "chat"|"--chat")
        echo -e "${GREEN}Starting interactive chat mode...${NC}"
        echo ""
        exec $PYTHON_CMD -m src.proxmox_ai.cli.main chat
        ;;
    "config"|"--config")
        echo -e "${GREEN}Starting configuration setup...${NC}"
        echo ""
        exec $PYTHON_CMD -m src.proxmox_ai.cli.main config init
        ;;
    "status"|"--status")
        echo -e "${GREEN}Showing system status...${NC}"
        echo ""
        exec $PYTHON_CMD -m src.proxmox_ai.cli.main status
        ;;
    "doctor"|"--doctor")
        echo -e "${GREEN}Running comprehensive diagnostics...${NC}"
        echo ""
        exec $PYTHON_CMD -m src.proxmox_ai.cli.main doctor
        ;;
    ""|"--help")
        echo -e "${BLUE}💡 What would you like to do?${NC}"
        echo ""
        echo "Run one of the commands above, or:"
        echo -e "   ${YELLOW}./scripts/start-assistant.sh chat${NC}     # Start chat mode"
        echo -e "   ${YELLOW}./scripts/start-assistant.sh config${NC}   # Setup configuration"
        echo -e "   ${YELLOW}./scripts/start-assistant.sh status${NC}   # Check status"
        echo ""
        ;;
    *)
        echo -e "${GREEN}Executing: ${YELLOW}proxmox-ai $*${NC}"
        echo ""
        exec $PYTHON_CMD -m src.proxmox_ai.cli.main "$@"
        ;;
esac