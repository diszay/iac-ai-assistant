"""
GitOps module for Proxmox Infrastructure Management

This module provides comprehensive GitOps workflow management for Proxmox infrastructure,
including configuration drift detection, automated deployments, and secure credential management.
"""

from .credentials import SecureCredentialManager, GitOpsCredentialManager
from .drift_detector import ProxmoxDriftDetector, DriftMonitor, DriftSeverity, DriftDetection
from .workflow_orchestrator import GitOpsWorkflowOrchestrator, WorkflowStatus, DeploymentEnvironment

__all__ = [
    'SecureCredentialManager',
    'GitOpsCredentialManager', 
    'ProxmoxDriftDetector',
    'DriftMonitor',
    'DriftSeverity',
    'DriftDetection',
    'GitOpsWorkflowOrchestrator',
    'WorkflowStatus',
    'DeploymentEnvironment'
]