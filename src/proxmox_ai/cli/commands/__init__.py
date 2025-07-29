"""
CLI command modules for Proxmox AI Assistant.

This package contains all the command-line interface modules organized by functionality:
- vm_commands: Virtual machine lifecycle operations
- config_commands: Configuration management 
- ai_commands: AI-powered automation and code generation
"""

from .vm_commands import app as vm_commands
from .config_commands import app as config_commands
from .ai_commands import app as ai_commands

__all__ = ['vm_commands', 'config_commands', 'ai_commands']