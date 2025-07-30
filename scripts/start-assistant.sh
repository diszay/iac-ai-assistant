#!/bin/bash
# Proxmox AI Assistant Startup Script
# This script helps you start the assistant with proper environment setup

# CRITICAL FIX: Remove 'set -e' to prevent auto-close on errors
# Instead, we'll handle errors gracefully with explicit error checking

# Trap to handle script interruption and cleanup
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        echo ""
        print_error "Script encountered an error (exit code: $exit_code)"
        print_info "Press Enter to close this window or Ctrl+C to abort..."
        read -r
    fi
}
trap cleanup EXIT

# Detect if running from GUI file manager
if [[ -z "$TERM" ]] || [[ "$TERM" == "dumb" ]]; then
    GUI_MODE=true
    echo "Detected GUI execution mode - terminal will stay open for debugging"
else
    GUI_MODE=false
fi

# Function to pause execution in GUI mode
pause_if_gui() {
    if [[ "$GUI_MODE" == "true" ]]; then
        echo "Press Enter to continue..."
        read -r
    fi
}

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

# Check Python version with improved error handling
if command_exists python3.12; then
    PYTHON_CMD="python3.12"
    print_status "Python 3.12+ found"
elif command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ -n "$PYTHON_VERSION" ]] && command_exists bc && (( $(echo "$PYTHON_VERSION >= 3.12" | bc -l 2>/dev/null) )); then
        PYTHON_CMD="python3"
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.12+ required, found $PYTHON_VERSION"
        print_info "Please install Python 3.12 or later from https://python.org"
        pause_if_gui
        exit 1
    fi
else
    print_error "Python 3.12+ not found. Please install Python 3.12 or later."
    print_info "Visit https://python.org for installation instructions"
    pause_if_gui
    exit 1
fi

# Check if we're in the project directory
if [[ ! -f "$PROJECT_DIR/pyproject.toml" ]]; then
    print_error "Project configuration not found at: $PROJECT_DIR/pyproject.toml"
    print_info "Current directory: $(pwd)"
    print_info "Script directory: $SCRIPT_DIR"
    print_info "Project directory: $PROJECT_DIR"
    print_info "Please ensure you're running this script from the correct location"
    pause_if_gui
    exit 1
fi

# Check virtual environment
echo ""
echo -e "${BLUE}🐍 Setting Up Python Environment...${NC}"

if [[ ! -d "$PROJECT_DIR/venv" ]]; then
    print_info "Creating virtual environment..."
    cd "$PROJECT_DIR" || {
        print_error "Failed to change to project directory: $PROJECT_DIR"
        pause_if_gui
        exit 1
    }
    
    if ! $PYTHON_CMD -m venv venv; then
        print_error "Failed to create virtual environment"
        print_info "Please check if $PYTHON_CMD has venv module installed"
        pause_if_gui
        exit 1
    fi
    print_status "Virtual environment created"
fi

# Activate virtual environment
if [[ -f "$PROJECT_DIR/venv/bin/activate" ]]; then
    if source "$PROJECT_DIR/venv/bin/activate"; then
        print_status "Virtual environment activated"
    else
        print_error "Failed to activate virtual environment"
        pause_if_gui
        exit 1
    fi
elif [[ -f "$PROJECT_DIR/venv/Scripts/activate" ]]; then
    if source "$PROJECT_DIR/venv/Scripts/activate"; then
        print_status "Virtual environment activated (Windows)"
    else
        print_error "Failed to activate virtual environment (Windows)"
        pause_if_gui
        exit 1
    fi
else
    print_error "Cannot find virtual environment activation script"
    print_info "Expected locations:"
    print_info "  - $PROJECT_DIR/venv/bin/activate (Unix/Linux/macOS)"
    print_info "  - $PROJECT_DIR/venv/Scripts/activate (Windows)"
    pause_if_gui
    exit 1
fi

# Install/update dependencies
if [[ ! -f "$PROJECT_DIR/venv/.dependencies_installed" ]] || [[ "$1" == "--force-install" ]]; then
    print_info "Installing dependencies..."
    cd "$PROJECT_DIR" || {
        print_error "Failed to change to project directory for dependency installation"
        pause_if_gui
        exit 1
    }
    
    print_info "Upgrading pip..."
    if ! pip install --upgrade pip; then
        print_warning "Failed to upgrade pip, continuing with current version"
    fi
    
    print_info "Installing project dependencies..."
    if pip install -e .; then
        touch "$PROJECT_DIR/venv/.dependencies_installed"
        print_status "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        print_info "Please check the pip output above for specific errors"
        pause_if_gui
        exit 1
    fi
else
    print_status "Dependencies already installed (use --force-install to reinstall)"
fi

# Check Ollama
echo ""
echo -e "${BLUE}🧠 Checking Local AI (Ollama)...${NC}"

if ! command_exists ollama; then
    print_warning "Ollama not found. Installing Ollama..."
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        print_info "Downloading and installing Ollama (this may take a few minutes)..."
        if curl -fsSL https://ollama.ai/install.sh | sh; then
            print_status "Ollama installed successfully"
        else
            print_error "Failed to install Ollama automatically"
            print_info "Please install Ollama manually:"
            print_info "1. Visit https://ollama.ai/"
            print_info "2. Download the installer for your system"
            print_info "3. Run the installer and restart this script"
            pause_if_gui
            exit 1
        fi
    else
        print_error "Automatic Ollama installation not supported on this system"
        print_info "Please install Ollama manually:"
        print_info "1. Visit https://ollama.ai/"
        print_info "2. Download the installer for your system"
        print_info "3. Run the installer and restart this script"
        pause_if_gui
        exit 1
    fi
fi

# Check if Ollama is running
if ! check_port 11434; then
    print_info "Starting Ollama service..."
    
    # Try to start Ollama service
    if ollama serve &>/dev/null &
    then
        OLLAMA_PID=$!
        print_info "Ollama service starting (PID: $OLLAMA_PID)..."
        
        # Wait up to 15 seconds for service to start
        for i in {1..15}; do
            if check_port 11434; then
                print_status "Ollama service started successfully"
                break
            fi
            print_info "Waiting for Ollama service... ($i/15)"
            sleep 1
        done
        
        if ! check_port 11434; then
            print_error "Ollama service failed to start within 15 seconds"
            print_info "This might be due to:"
            print_info "1. Insufficient system resources"
            print_info "2. Port 11434 already in use"
            print_info "3. Ollama installation issues"
            print_info "Try running 'ollama serve' manually to see error details"
            pause_if_gui
            exit 1
        fi
    else
        print_error "Failed to start Ollama service"
        print_info "Try running 'ollama serve' manually to diagnose the issue"
        pause_if_gui
        exit 1
    fi
else
    print_status "Ollama service is already running"
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

# Function to show download progress
show_download_progress() {
    local model="$1"
    print_info "Downloading $model - this may take 10-30 minutes depending on your internet speed"
    print_info "The download will continue even if you close this window"
    print_info "You can check progress anytime by running: ollama list"
    echo ""
}

# Function to download model with robust error handling
download_model_robust() {
    local model="$1"
    local max_attempts=3
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        print_info "Download attempt $attempt/$max_attempts for model: $model"
        show_download_progress "$model"
        
        # Create a temporary log file for this download attempt
        local log_file="/tmp/ollama_download_$$.log"
        
        # Run ollama pull with progress output
        if timeout 1800 ollama pull "$model" 2>&1 | tee "$log_file"; then
            print_status "Model $model downloaded successfully"
            rm -f "$log_file"
            return 0
        else
            local exit_code=$?
            print_warning "Download attempt $attempt failed (exit code: $exit_code)"
            
            if [[ $exit_code -eq 124 ]]; then
                print_warning "Download timed out after 30 minutes"
            fi
            
            # Check if it was a partial download that can be resumed
            if ollama list | grep -q "$model"; then
                print_info "Partial download detected, attempting to resume..."
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                print_error "Failed to download model after $max_attempts attempts"
                print_info "You can try downloading manually later with: ollama pull $model"
                rm -f "$log_file"
                return 1
            fi
            
            print_info "Waiting 10 seconds before retry..."
            sleep 10
            ((attempt++))
        fi
    done
}

# Check if model is downloaded
print_info "Checking for available AI models..."
AVAILABLE_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' ' ')

if [[ -z "$AVAILABLE_MODELS" ]] || [[ "$AVAILABLE_MODELS" =~ ^[[:space:]]*$ ]]; then
    print_warning "No AI models found. Downloading recommended model..."
    
    # Detect system RAM to choose appropriate model
    if command_exists free; then
        TOTAL_RAM_GB=$(($(free -m 2>/dev/null | awk 'NR==2{print $2}') / 1024))
    elif command_exists sysctl; then
        TOTAL_RAM_GB=$(($(sysctl -n hw.memsize 2>/dev/null || echo 8589934592) / 1024 / 1024 / 1024))
    else
        TOTAL_RAM_GB=8  # Default assumption
    fi
    
    print_info "Detected system RAM: ${TOTAL_RAM_GB}GB"
    
    if (( TOTAL_RAM_GB < 6 )); then
        MODEL="llama3.2:3b-instruct-q4_0"
        print_info "Selected compact model for low RAM system: $MODEL"
    elif (( TOTAL_RAM_GB < 12 )); then
        MODEL="llama3.1:8b-instruct-q4_0"
        print_info "Selected standard model for medium RAM system: $MODEL"
    else
        MODEL="llama3.1:8b-instruct-q8_0"
        print_info "Selected high-quality model for high RAM system: $MODEL"
    fi
    
    # Download the model with robust error handling
    if download_model_robust "$MODEL"; then
        print_status "AI model setup completed: $MODEL"
    else
        print_warning "Model download failed, but continuing with setup"
        print_info "You can download a model later with: ollama pull <model-name>"
        print_info "Available models: llama3.2:3b, llama3.1:8b, codellama:7b"
    fi
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

cd "$PROJECT_DIR" || {
    print_error "Failed to change to project directory for health check"
    pause_if_gui
    exit 1
}

print_info "Running system health check..."
if timeout 30 $PYTHON_CMD -m src.proxmox_ai.cli.main status >/dev/null 2>&1; then
    print_status "Health check passed - all systems operational"
else
    print_warning "Health check incomplete - may need configuration"
    print_info "This is normal for first-time setup. You can configure the system after startup."
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
        
        # In GUI mode, pause to let user read the instructions
        if [[ "$GUI_MODE" == "true" ]]; then
            echo -e "${BLUE}💡 This window will stay open so you can see the setup results.${NC}"
            echo ""
            print_info "To continue:"
            echo "1. Open a new terminal"
            echo "2. Navigate to: $PROJECT_DIR"
            echo "3. Run one of the commands above"
            echo ""
            print_info "Or restart this script with a command:"
            echo "   ./scripts/start-assistant.sh chat"
            echo ""
            pause_if_gui
        fi
        ;;
    *)
        echo -e "${GREEN}Executing: ${YELLOW}proxmox-ai $*${NC}"
        echo ""
        if ! $PYTHON_CMD -m src.proxmox_ai.cli.main "$@"; then
            print_error "Command failed with exit code $?"
            pause_if_gui
            exit 1
        fi
        ;;
esac

# Final cleanup and success message
if [[ "$GUI_MODE" == "true" ]] && [[ "${1:-}" == "" ]]; then
    echo ""
    print_status "Setup completed successfully!"
    print_info "You can now close this window and start using the assistant."
fi