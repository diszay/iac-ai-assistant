#!/usr/bin/env python3
"""
Configuration Drift Detection System for Proxmox Infrastructure
Monitors and detects configuration drift in Proxmox VMs and infrastructure
"""

import asyncio
import json
import logging
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from ..api.proxmox_client import ProxmoxClient
from ..core.config import Config

logger = logging.getLogger(__name__)

class DriftSeverity(Enum):
    """Drift detection severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DriftDetection:
    """Represents a detected configuration drift"""
    resource_type: str
    resource_id: str
    attribute: str
    expected_value: Any
    actual_value: Any
    severity: DriftSeverity
    detected_at: datetime
    remediation_required: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            **asdict(self),
            'detected_at': self.detected_at.isoformat(),
            'severity': self.severity.value
        }

class ProxmoxDriftDetector:
    """Main drift detection system for Proxmox infrastructure"""
    
    def __init__(self, config: Config):
        self.config = config
        self.proxmox_client = ProxmoxClient(config)
        self.baseline_path = Path("config/baselines")
        self.baseline_path.mkdir(parents=True, exist_ok=True)
        
    async def detect_all_drift(self) -> List[DriftDetection]:
        """
        Detect configuration drift across all monitored resources
        
        Returns:
            List of detected drift issues
        """
        detected_drift = []
        
        try:
            # Load baseline configurations
            baselines = await self.load_baselines()
            
            # Detect VM configuration drift
            vm_drift = await self.detect_vm_configuration_drift(baselines.get('vms', {}))
            detected_drift.extend(vm_drift)
            
            # Detect network configuration drift
            network_drift = await self.detect_network_drift(baselines.get('networks', {}))
            detected_drift.extend(network_drift)
            
            # Detect storage configuration drift
            storage_drift = await self.detect_storage_drift(baselines.get('storage', {}))
            detected_drift.extend(storage_drift)
            
            # Detect user/permission drift
            permission_drift = await self.detect_permission_drift(baselines.get('permissions', {}))
            detected_drift.extend(permission_drift)
            
            # Log drift summary
            if detected_drift:
                severity_counts = {}
                for drift in detected_drift:
                    severity_counts[drift.severity.value] = severity_counts.get(drift.severity.value, 0) + 1
                
                logger.warning(f"Configuration drift detected: {severity_counts}")
            else:
                logger.info("No configuration drift detected")
            
            return detected_drift
            
        except Exception as e:
            logger.error(f"Error during drift detection: {e}")
            return []
    
    async def detect_vm_configuration_drift(self, baseline_vms: Dict) -> List[DriftDetection]:
        """Detect drift in VM configurations"""
        drift_issues = []
        
        try:
            # Get current VM configurations
            current_vms = await self.proxmox_client.get_all_vms()
            
            for vm_id, vm_config in current_vms.items():
                if str(vm_id) not in baseline_vms:
                    # New VM detected (not necessarily drift)
                    logger.info(f"New VM detected: {vm_id}")
                    continue
                
                baseline_config = baseline_vms[str(vm_id)]
                
                # Check critical configuration parameters
                critical_params = ['memory', 'cores', 'sockets', 'boot', 'net0', 'scsi0']
                
                for param in critical_params:
                    if param in baseline_config and param in vm_config:
                        if baseline_config[param] != vm_config[param]:
                            drift_issues.append(DriftDetection(
                                resource_type="vm",
                                resource_id=str(vm_id),
                                attribute=param,
                                expected_value=baseline_config[param],
                                actual_value=vm_config[param],
                                severity=self._determine_vm_drift_severity(param),
                                detected_at=datetime.now(),
                                remediation_required=True
                            ))
                
                # Check for unauthorized changes in security-sensitive parameters
                security_params = ['firewall', 'protection', 'startup']
                for param in security_params:
                    if param in baseline_config and param in vm_config:
                        if baseline_config[param] != vm_config[param]:
                            drift_issues.append(DriftDetection(
                                resource_type="vm",
                                resource_id=str(vm_id),
                                attribute=param,
                                expected_value=baseline_config[param],
                                actual_value=vm_config[param],
                                severity=DriftSeverity.HIGH,
                                detected_at=datetime.now(),
                                remediation_required=True
                            ))
            
            return drift_issues
            
        except Exception as e:
            logger.error(f"Error detecting VM drift: {e}")
            return []
    
    async def detect_network_drift(self, baseline_networks: Dict) -> List[DriftDetection]:
        """Detect drift in network configurations"""
        drift_issues = []
        
        try:
            # Get current network configurations
            current_networks = await self.proxmox_client.get_network_config()
            
            for network_id, network_config in current_networks.items():
                if network_id not in baseline_networks:
                    continue
                
                baseline_config = baseline_networks[network_id]
                
                # Check critical network parameters
                critical_params = ['type', 'bridge_ports', 'cidr', 'gateway']
                
                for param in critical_params:
                    if (param in baseline_config and param in network_config and
                        baseline_config[param] != network_config[param]):
                        
                        drift_issues.append(DriftDetection(
                            resource_type="network",
                            resource_id=network_id,
                            attribute=param,
                            expected_value=baseline_config[param],
                            actual_value=network_config[param],
                            severity=DriftSeverity.HIGH,
                            detected_at=datetime.now(),
                            remediation_required=True
                        ))
            
            return drift_issues
            
        except Exception as e:
            logger.error(f"Error detecting network drift: {e}")
            return []
    
    async def detect_storage_drift(self, baseline_storage: Dict) -> List[DriftDetection]:
        """Detect drift in storage configurations"""
        drift_issues = []
        
        try:
            # Get current storage configurations
            current_storage = await self.proxmox_client.get_storage_config()
            
            for storage_id, storage_config in current_storage.items():
                if storage_id not in baseline_storage:
                    continue
                
                baseline_config = baseline_storage[storage_id]
                
                # Check critical storage parameters
                critical_params = ['type', 'path', 'content', 'maxfiles']
                
                for param in critical_params:
                    if (param in baseline_config and param in storage_config and
                        baseline_config[param] != storage_config[param]):
                        
                        drift_issues.append(DriftDetection(
                            resource_type="storage",
                            resource_id=storage_id,
                            attribute=param,
                            expected_value=baseline_config[param],
                            actual_value=storage_config[param],
                            severity=DriftSeverity.HIGH,
                            detected_at=datetime.now(),
                            remediation_required=True
                        ))
            
            return drift_issues
            
        except Exception as e:
            logger.error(f"Error detecting storage drift: {e}")
            return []
    
    async def detect_permission_drift(self, baseline_permissions: Dict) -> List[DriftDetection]:
        """Detect drift in user permissions and access control"""
        drift_issues = []
        
        try:
            # Get current user permissions
            current_permissions = await self.proxmox_client.get_user_permissions()
            
            for user_id, user_perms in current_permissions.items():
                if user_id not in baseline_permissions:
                    # New user detected - could be security concern
                    drift_issues.append(DriftDetection(
                        resource_type="user",
                        resource_id=user_id,
                        attribute="existence",
                        expected_value="not_present",
                        actual_value="present",
                        severity=DriftSeverity.CRITICAL,
                        detected_at=datetime.now(),
                        remediation_required=True
                    ))
                    continue
                
                baseline_perms = baseline_permissions[user_id]
                
                # Check permission changes
                for permission, granted in user_perms.items():
                    baseline_granted = baseline_perms.get(permission, False)
                    
                    if granted != baseline_granted:
                        severity = DriftSeverity.CRITICAL if granted else DriftSeverity.HIGH
                        
                        drift_issues.append(DriftDetection(
                            resource_type="user_permission",
                            resource_id=user_id,
                            attribute=permission,
                            expected_value=baseline_granted,
                            actual_value=granted,
                            severity=severity,
                            detected_at=datetime.now(),
                            remediation_required=True
                        ))
            
            return drift_issues
            
        except Exception as e:
            logger.error(f"Error detecting permission drift: {e}")
            return []
    
    def _determine_vm_drift_severity(self, parameter: str) -> DriftSeverity:
        """Determine severity level for VM configuration drift"""
        high_impact_params = ['memory', 'cores', 'boot', 'scsi0']
        medium_impact_params = ['sockets', 'net0']
        
        if parameter in high_impact_params:
            return DriftSeverity.HIGH
        elif parameter in medium_impact_params:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW
    
    async def load_baselines(self) -> Dict:
        """Load baseline configurations from files"""
        try:
            baseline_file = self.baseline_path / "infrastructure_baseline.yaml"
            
            if not baseline_file.exists():
                logger.warning("No baseline configuration found - creating initial baseline")
                await self.create_baseline()
                return {}
            
            with open(baseline_file, 'r') as f:
                return yaml.safe_load(f)
                
        except Exception as e:
            logger.error(f"Error loading baselines: {e}")
            return {}
    
    async def create_baseline(self) -> bool:
        """Create initial baseline configuration from current state"""
        try:
            baseline = {
                'created_at': datetime.now().isoformat(),
                'vms': await self.proxmox_client.get_all_vms(),
                'networks': await self.proxmox_client.get_network_config(),
                'storage': await self.proxmox_client.get_storage_config(),
                'permissions': await self.proxmox_client.get_user_permissions()
            }
            
            baseline_file = self.baseline_path / "infrastructure_baseline.yaml"
            with open(baseline_file, 'w') as f:
                yaml.dump(baseline, f, default_flow_style=False)
            
            logger.info(f"Baseline configuration created: {baseline_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating baseline: {e}")
            return False
    
    async def remediate_drift(self, drift_issue: DriftDetection) -> bool:
        """
        Attempt to remediate detected configuration drift
        
        Args:
            drift_issue: The drift issue to remediate
            
        Returns:
            True if remediation was successful
        """
        try:
            logger.info(f"Attempting to remediate drift: {drift_issue.resource_type}.{drift_issue.resource_id}.{drift_issue.attribute}")
            
            if drift_issue.resource_type == "vm":
                return await self._remediate_vm_drift(drift_issue)
            elif drift_issue.resource_type == "network":
                return await self._remediate_network_drift(drift_issue)
            elif drift_issue.resource_type == "storage":
                return await self._remediate_storage_drift(drift_issue)
            elif drift_issue.resource_type in ["user", "user_permission"]:
                return await self._remediate_permission_drift(drift_issue)
            
            return False
            
        except Exception as e:
            logger.error(f"Error during drift remediation: {e}")
            return False
    
    async def _remediate_vm_drift(self, drift_issue: DriftDetection) -> bool:
        """Remediate VM configuration drift"""
        try:
            vm_id = drift_issue.resource_id
            config_update = {drift_issue.attribute: drift_issue.expected_value}
            
            success = await self.proxmox_client.update_vm_config(vm_id, config_update)
            
            if success:
                logger.info(f"Successfully remediated VM {vm_id} drift: {drift_issue.attribute}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error remediating VM drift: {e}")
            return False
    
    async def _remediate_network_drift(self, drift_issue: DriftDetection) -> bool:
        """Remediate network configuration drift"""
        # Implementation would depend on specific network management APIs
        logger.warning(f"Network drift remediation not yet implemented: {drift_issue.resource_id}")
        return False
    
    async def _remediate_storage_drift(self, drift_issue: DriftDetection) -> bool:
        """Remediate storage configuration drift"""
        # Implementation would depend on specific storage management APIs
        logger.warning(f"Storage drift remediation not yet implemented: {drift_issue.resource_id}")
        return False
    
    async def _remediate_permission_drift(self, drift_issue: DriftDetection) -> bool:
        """Remediate user permission drift"""
        # Implementation would depend on user management APIs
        logger.warning(f"Permission drift remediation requires manual review: {drift_issue.resource_id}")
        return False
    
    async def generate_drift_report(self, drift_issues: List[DriftDetection]) -> str:
        """Generate detailed drift detection report"""
        report = {
            'report_generated_at': datetime.now().isoformat(),
            'total_drift_issues': len(drift_issues),
            'severity_breakdown': {},
            'drift_issues': [issue.to_dict() for issue in drift_issues]
        }
        
        # Calculate severity breakdown
        for issue in drift_issues:
            severity = issue.severity.value
            report['severity_breakdown'][severity] = report['severity_breakdown'].get(severity, 0) + 1
        
        # Save report
        report_file = Path("logs") / f"drift_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Drift report generated: {report_file}")
        return str(report_file)


class DriftMonitor:
    """Continuous monitoring service for configuration drift"""
    
    def __init__(self, config: Config, check_interval: int = 900):  # 15 minutes default
        self.config = config
        self.check_interval = check_interval
        self.detector = ProxmoxDriftDetector(config)
        self.running = False
    
    async def start_monitoring(self):
        """Start continuous drift monitoring"""
        self.running = True
        logger.info(f"Starting drift monitoring with {self.check_interval}s interval")
        
        while self.running:
            try:
                drift_issues = await self.detector.detect_all_drift()
                
                if drift_issues:
                    # Generate report
                    report_file = await self.detector.generate_drift_report(drift_issues)
                    
                    # Send alerts for critical issues
                    critical_issues = [d for d in drift_issues if d.severity == DriftSeverity.CRITICAL]
                    if critical_issues:
                        await self._send_alert(critical_issues, report_file)
                    
                    # Auto-remediate low-severity issues if configured
                    if self.config.get('auto_remediate_low_severity', False):
                        low_issues = [d for d in drift_issues if d.severity == DriftSeverity.LOW]
                        for issue in low_issues:
                            await self.detector.remediate_drift(issue)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in drift monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_monitoring(self):
        """Stop drift monitoring"""
        self.running = False
        logger.info("Drift monitoring stopped")
    
    async def _send_alert(self, critical_issues: List[DriftDetection], report_file: str):
        """Send alert for critical drift issues"""
        # Implementation would depend on alerting system (email, Slack, etc.)
        logger.critical(f"CRITICAL DRIFT DETECTED: {len(critical_issues)} issues found. Report: {report_file}")


# CLI entry point for drift detection
async def main():
    """Main entry point for drift detection CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Proxmox Configuration Drift Detection")
    parser.add_argument("--action", choices=["detect", "monitor", "baseline"], default="detect",
                       help="Action to perform")
    parser.add_argument("--config", default="config/config.yaml",
                       help="Configuration file path")
    parser.add_argument("--interval", type=int, default=900,
                       help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    if args.action == "detect":
        # One-time drift detection
        detector = ProxmoxDriftDetector(config)
        drift_issues = await detector.detect_all_drift()
        
        if drift_issues:
            report_file = await detector.generate_drift_report(drift_issues)
            print(f"Drift detected! Report saved to: {report_file}")
        else:
            print("No configuration drift detected.")
            
    elif args.action == "monitor":
        # Continuous monitoring
        monitor = DriftMonitor(config, args.interval)
        await monitor.start_monitoring()
        
    elif args.action == "baseline":
        # Create baseline
        detector = ProxmoxDriftDetector(config)
        success = await detector.create_baseline()
        print("Baseline created successfully!" if success else "Failed to create baseline.")


if __name__ == "__main__":
    asyncio.run(main())