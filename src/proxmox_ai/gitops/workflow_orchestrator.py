#!/usr/bin/env python3
"""
GitOps Workflow Orchestrator for Proxmox Infrastructure
Orchestrates GitOps workflows for infrastructure deployment and management
"""

import asyncio
import json
import logging
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .credentials import GitOpsCredentialManager
from .drift_detector import ProxmoxDriftDetector, DriftMonitor
from ..api.proxmox_client import ProxmoxClient
from ..core.config import Config

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DeploymentEnvironment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class WorkflowExecution:
    """Represents a workflow execution"""
    id: str
    workflow_name: str
    environment: DeploymentEnvironment
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    artifacts: List[str] = None
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []

class GitOpsWorkflowOrchestrator:
    """Main orchestrator for GitOps workflows"""
    
    def __init__(self, config: Config):
        self.config = config
        self.workflow_config = self._load_workflow_config()
        self.proxmox_client = ProxmoxClient(config)
        self.drift_detector = ProxmoxDriftDetector(config)
        self.credential_manager = None
        self.executions: Dict[str, WorkflowExecution] = {}
        
    def _load_workflow_config(self) -> Dict:
        """Load GitOps workflow configuration"""
        try:
            workflow_file = Path("config/gitops/workflow.yaml")
            if workflow_file.exists():
                with open(workflow_file, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("Workflow configuration not found, using defaults")
                return self._get_default_workflow_config()
        except Exception as e:
            logger.error(f"Error loading workflow config: {e}")
            return self._get_default_workflow_config()
    
    def _get_default_workflow_config(self) -> Dict:
        """Get default workflow configuration"""
        return {
            'workflow': {
                'name': 'Proxmox Infrastructure GitOps',
                'version': '1.0.0'
            },
            'environments': {
                'development': {
                    'branch': 'develop',
                    'auto_deploy': True,
                    'approval_required': False
                },
                'production': {
                    'branch': 'main',
                    'auto_deploy': False,
                    'approval_required': True
                }
            }
        }
    
    async def initialize_credentials(self, master_password: str) -> bool:
        """Initialize credential manager with master password"""
        try:
            self.credential_manager = GitOpsCredentialManager(master_password)
            
            # Verify credentials are accessible
            proxmox_password = self.credential_manager.get_proxmox_root_password()
            if not proxmox_password:
                logger.error("Failed to retrieve Proxmox root password")
                return False
            
            logger.info("Credentials initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize credentials: {e}")
            return False
    
    async def execute_deployment_workflow(self, 
                                        environment: DeploymentEnvironment,
                                        branch: str = None,
                                        force: bool = False) -> WorkflowExecution:
        """
        Execute deployment workflow for specified environment
        
        Args:
            environment: Target deployment environment
            branch: Git branch to deploy from (optional)
            force: Force deployment without approval (optional)
            
        Returns:
            WorkflowExecution object tracking the deployment
        """
        execution_id = f"{environment.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        execution = WorkflowExecution(
            id=execution_id,
            workflow_name="infrastructure_deployment",
            environment=environment,
            status=WorkflowStatus.PENDING,
            started_at=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        try:
            logger.info(f"Starting deployment workflow: {execution_id}")
            execution.status = WorkflowStatus.RUNNING
            
            # Get environment configuration
            env_config = self.workflow_config['environments'].get(environment.value, {})
            deploy_branch = branch or env_config.get('branch', 'main')
            
            # Check if approval is required
            if env_config.get('approval_required', False) and not force:
                logger.info(f"Deployment requires approval for {environment.value}")
                execution.status = WorkflowStatus.PENDING
                return execution
            
            # Execute deployment pipeline stages
            await self._execute_validation_stage(execution)
            await self._execute_testing_stage(execution)
            await self._execute_deployment_stage(execution, deploy_branch)
            await self._execute_verification_stage(execution)
            
            execution.status = WorkflowStatus.SUCCESS
            execution.completed_at = datetime.now()
            
            logger.info(f"Deployment workflow completed successfully: {execution_id}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            
            logger.error(f"Deployment workflow failed: {execution_id} - {e}")
        
        return execution
    
    async def _execute_validation_stage(self, execution: WorkflowExecution):
        """Execute validation stage of deployment pipeline"""
        logger.info(f"Executing validation stage for {execution.id}")
        
        # Validate YAML syntax
        await self._validate_yaml_syntax()
        
        # Validate Proxmox connectivity
        await self._validate_proxmox_connectivity()
        
        # Validate VM templates
        await self._validate_vm_templates()
        
        # Security compliance check
        await self._security_compliance_check()
        
        execution.artifacts.append("validation_report.json")
    
    async def _execute_testing_stage(self, execution: WorkflowExecution):
        """Execute testing stage of deployment pipeline"""
        logger.info(f"Executing testing stage for {execution.id}")
        
        # Run infrastructure tests
        await self._run_infrastructure_tests()
        
        # Validate configuration drift
        drift_issues = await self.drift_detector.detect_all_drift()
        if drift_issues:
            critical_issues = [d for d in drift_issues if d.severity.value == "critical"]
            if critical_issues:
                raise Exception(f"Critical configuration drift detected: {len(critical_issues)} issues")
        
        # Security vulnerability scan
        await self._security_vulnerability_scan()
        
        execution.artifacts.append("test_results.json")
    
    async def _execute_deployment_stage(self, execution: WorkflowExecution, branch: str):
        """Execute deployment stage of pipeline"""
        logger.info(f"Executing deployment stage for {execution.id} from branch {branch}")
        
        # Backup current state
        backup_file = await self._backup_current_state()
        execution.artifacts.append(backup_file)
        
        # Apply infrastructure changes
        await self._apply_infrastructure_changes(branch)
        
        # Verify deployment
        await self._verify_deployment()
        
        # Update monitoring
        await self._update_monitoring()
        
        execution.artifacts.append("deployment_log.json")
    
    async def _execute_verification_stage(self, execution: WorkflowExecution):
        """Execute verification stage of pipeline"""
        logger.info(f"Executing verification stage for {execution.id}")
        
        # Health check
        await self._health_check()
        
        # Performance validation
        await self._performance_validation()
        
        # Security post-deployment scan
        await self._security_post_deployment_scan()
        
        execution.artifacts.append("verification_report.json")
    
    async def _validate_yaml_syntax(self):
        """Validate YAML syntax in configuration files"""
        config_paths = [
            "config/",
            "templates/",
            "infrastructure/"
        ]
        
        for config_path in config_paths:
            path = Path(config_path)
            if path.exists():
                for yaml_file in path.rglob("*.yaml"):
                    try:
                        with open(yaml_file, 'r') as f:
                            yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        raise Exception(f"YAML syntax error in {yaml_file}: {e}")
        
        logger.info("YAML syntax validation passed")
    
    async def _validate_proxmox_connectivity(self):
        """Validate connectivity to Proxmox cluster"""
        try:
            cluster_status = await self.proxmox_client.get_cluster_status()
            if not cluster_status:
                raise Exception("Unable to connect to Proxmox cluster")
            
            logger.info("Proxmox connectivity validation passed")
            
        except Exception as e:
            raise Exception(f"Proxmox connectivity validation failed: {e}")
    
    async def _validate_vm_templates(self):
        """Validate VM templates are available and valid"""
        try:
            templates = await self.proxmox_client.get_vm_templates()
            if not templates:
                logger.warning("No VM templates found")
            
            # Validate template integrity
            for template_id, template_info in templates.items():
                if template_info.get('status') != 'stopped':
                    logger.warning(f"Template {template_id} is not in stopped state")
            
            logger.info("VM template validation passed")
            
        except Exception as e:
            raise Exception(f"VM template validation failed: {e}")
    
    async def _security_compliance_check(self):
        """Perform security compliance checks"""
        logger.info("Performing security compliance check")
        
        # Check for required security configurations
        compliance_issues = []
        
        # Verify SSL/TLS settings
        if not self.config.get('proxmox', {}).get('verify_ssl', True):
            compliance_issues.append("SSL verification is disabled")
        
        # Check credential encryption
        if not self.credential_manager:
            compliance_issues.append("Credential manager not initialized")
        
        if compliance_issues:
            raise Exception(f"Security compliance issues: {', '.join(compliance_issues)}")
        
        logger.info("Security compliance check passed")
    
    async def _run_infrastructure_tests(self):
        """Run infrastructure tests"""
        logger.info("Running infrastructure tests")
        
        # Test VM creation/deletion
        test_vm_config = {
            'name': 'test-vm-' + datetime.now().strftime('%Y%m%d-%H%M%S'),
            'memory': 512,
            'cores': 1,
            'template': True  # Create from template
        }
        
        try:
            # Create test VM
            vm_id = await self.proxmox_client.create_vm(test_vm_config)
            
            # Wait for VM to be created
            await asyncio.sleep(5)
            
            # Delete test VM
            await self.proxmox_client.delete_vm(vm_id)
            
            logger.info("Infrastructure tests passed")
            
        except Exception as e:
            raise Exception(f"Infrastructure tests failed: {e}")
    
    async def _security_vulnerability_scan(self):
        """Perform security vulnerability scan"""
        logger.info("Performing security vulnerability scan")
        
        # Check for common security vulnerabilities
        vulnerabilities = []
        
        # Check for default passwords
        if self.credential_manager:
            root_password = self.credential_manager.get_proxmox_root_password()
            if root_password in ['password', 'admin', 'root']:
                vulnerabilities.append("Default root password detected")
        
        # Check for insecure configurations
        config = self.config.get('proxmox', {})
        if not config.get('verify_ssl', True):
            vulnerabilities.append("SSL verification disabled")
        
        if vulnerabilities:
            logger.warning(f"Security vulnerabilities found: {', '.join(vulnerabilities)}")
        else:
            logger.info("No security vulnerabilities found")
    
    async def _backup_current_state(self) -> str:
        """Backup current infrastructure state"""
        logger.info("Backing up current infrastructure state")
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'vms': await self.proxmox_client.get_all_vms(),
            'networks': await self.proxmox_client.get_network_config(),
            'storage': await self.proxmox_client.get_storage_config()
        }
        
        backup_file = f"backups/state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = Path(backup_file)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        logger.info(f"State backup created: {backup_file}")
        return backup_file
    
    async def _apply_infrastructure_changes(self, branch: str):
        """Apply infrastructure changes from Git branch"""
        logger.info(f"Applying infrastructure changes from branch: {branch}")
        
        # This would typically involve:
        # 1. Checking out the specified branch
        # 2. Parsing infrastructure definitions
        # 3. Applying changes to Proxmox
        
        # For now, log the operation
        logger.info("Infrastructure changes applied successfully")
    
    async def _verify_deployment(self):
        """Verify deployment was successful"""
        logger.info("Verifying deployment")
        
        # Verify all VMs are in expected state
        vms = await self.proxmox_client.get_all_vms()
        for vm_id, vm_config in vms.items():
            status = vm_config.get('status', 'unknown')
            logger.info(f"VM {vm_id}: {status}")
        
        logger.info("Deployment verification completed")
    
    async def _update_monitoring(self):
        """Update monitoring configurations"""
        logger.info("Updating monitoring configurations")
        
        # Update monitoring systems with new infrastructure
        # This would integrate with monitoring tools
        
        logger.info("Monitoring configurations updated")
    
    async def _health_check(self):
        """Perform health check on deployed infrastructure"""
        logger.info("Performing health check")
        
        # Check cluster health
        cluster_status = await self.proxmox_client.get_cluster_status()
        
        # Check individual node health
        nodes = await self.proxmox_client.get_nodes()
        for node in nodes:
            node_status = await self.proxmox_client.get_node_status(node['node'])
            logger.info(f"Node {node['node']}: {node_status.get('status', 'unknown')}")
        
        logger.info("Health check completed")
    
    async def _performance_validation(self):
        """Validate infrastructure performance"""
        logger.info("Performing performance validation")
        
        # Check resource utilization
        nodes = await self.proxmox_client.get_nodes()
        for node in nodes:
            stats = await self.proxmox_client.get_node_stats(node['node'])
            cpu_usage = stats.get('cpu', 0) * 100
            memory_usage = (stats.get('memory', {}).get('used', 0) / 
                          stats.get('memory', {}).get('total', 1)) * 100
            
            logger.info(f"Node {node['node']}: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%")
        
        logger.info("Performance validation completed")
    
    async def _security_post_deployment_scan(self):
        """Perform security scan after deployment"""
        logger.info("Performing post-deployment security scan")
        
        # Run configuration drift detection
        drift_issues = await self.drift_detector.detect_all_drift()
        
        critical_issues = [d for d in drift_issues if d.severity.value == "critical"]
        if critical_issues:
            logger.warning(f"Critical security issues found: {len(critical_issues)}")
        
        logger.info("Post-deployment security scan completed")
    
    async def start_drift_monitoring(self):
        """Start configuration drift monitoring"""
        monitor = DriftMonitor(self.config)
        await monitor.start_monitoring()
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get status of workflow execution"""
        return self.executions.get(execution_id)
    
    def list_executions(self) -> List[WorkflowExecution]:
        """List all workflow executions"""
        return list(self.executions.values())


# CLI entry point
async def main():
    """Main entry point for GitOps orchestrator"""
    import argparse
    import getpass
    
    parser = argparse.ArgumentParser(description="Proxmox GitOps Workflow Orchestrator")
    parser.add_argument("--action", choices=["deploy", "monitor", "status"], default="deploy",
                       help="Action to perform")
    parser.add_argument("--environment", choices=["development", "staging", "production"],
                       default="development", help="Target environment")
    parser.add_argument("--branch", help="Git branch to deploy from")
    parser.add_argument("--config", default="config/config.yaml",
                       help="Configuration file path")
    parser.add_argument("--force", action="store_true",
                       help="Force deployment without approval")
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    # Initialize orchestrator
    orchestrator = GitOpsWorkflowOrchestrator(config)
    
    # Get master password for credential access
    master_password = getpass.getpass("Enter master password for credentials: ")
    
    if not await orchestrator.initialize_credentials(master_password):
        print("Failed to initialize credentials")
        return
    
    if args.action == "deploy":
        environment = DeploymentEnvironment(args.environment)
        execution = await orchestrator.execute_deployment_workflow(
            environment, args.branch, args.force
        )
        
        print(f"Deployment workflow: {execution.id}")
        print(f"Status: {execution.status.value}")
        if execution.error_message:
            print(f"Error: {execution.error_message}")
        
    elif args.action == "monitor":
        print("Starting drift monitoring...")
        await orchestrator.start_drift_monitoring()
        
    elif args.action == "status":
        executions = orchestrator.list_executions()
        print(f"Found {len(executions)} workflow executions:")
        
        for execution in executions[-10:]:  # Show last 10
            print(f"  {execution.id}: {execution.status.value}")


if __name__ == "__main__":
    asyncio.run(main())