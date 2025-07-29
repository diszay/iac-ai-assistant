"""
Proxmox AI Infrastructure Assistant

A secure, AI-powered automation tool for Proxmox VE infrastructure management.
"""

__version__ = "0.1.0"
__author__ = "Proxmox AI Team"
__email__ = "dev@proxmox-ai.local"

from .core.config import Settings
from .core.logging import setup_logging

__all__ = ["Settings", "setup_logging"]