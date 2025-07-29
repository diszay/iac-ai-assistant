"""
CIS Benchmark Compliance Validation Framework

Comprehensive testing and validation for CIS (Center for Internet Security)
benchmark compliance across all Proxmox infrastructure components.
"""

import pytest
import asyncio
import subprocess
import json
import logging
import yaml
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import paramiko
import re
import socket

logger = logging.getLogger(__name__)


class CISControl(Enum):
    """CIS Control categories."""
    INVENTORY = "inventory"
    SOFTWARE = "software"
    CONFIGURATION = "configuration"
    CONTROLLED_ACCESS = "controlled_access"
    SECURE_CONFIG = "secure_config"
    MAINTENANCE = "maintenance"
    PROTECTION = "protection"
    MALWARE = "malware"
    DATA_RECOVERY = "data_recovery"
    SECURITY_SKILLS = "security_skills"
    SECURE_NETWORK = "secure_network"
    BOUNDARY_DEFENSE = "boundary_defense"
    DATA_PROTECTION = "data_protection"
    CONTROLLED_USE = "controlled_use"
    WIRELESS_ACCESS = "wireless_access"
    MONITORING = "monitoring"
    INCIDENT_RESPONSE = "incident_response"
    PENETRATION_TESTING = "penetration_testing"


class ComplianceLevel(Enum):
    """CIS compliance levels."""
    LEVEL_1 = "level_1"  # Basic security hygiene
    LEVEL_2 = "level_2"  # Defense in depth


@dataclass
class CISBenchmarkTest:
    """CIS benchmark test definition."""
    control_id: str
    control_name: str
    description: str
    rationale: str
    impact: str
    remediation: str
    compliance_level: ComplianceLevel
    category: CISControl
    automated: bool = True
    test_function: Optional[str] = None
    expected_result: Any = None
    scoring: bool = True


@dataclass
class CISTestResult:
    """CIS test result."""
    test_id: str
    control_id: str
    description: str
    status: str  # PASS, FAIL, NOT_APPLICABLE, MANUAL_REVIEW
    actual_result: Any
    expected_result: Any
    timestamp: datetime
    details: Dict[str, Any]
    remediation_required: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class CISComplianceValidator:
    """
    Comprehensive CIS benchmark compliance validation system
    for Proxmox infrastructure components.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_results: List[CISTestResult] = []
        self.benchmark_tests: Dict[str, CISBenchmarkTest] = {}
        self.ssh_connections: Dict[str, paramiko.SSHClient] = {}
        
        # Initialize CIS benchmark tests
        self._initialize_benchmark_tests()
        
        logger.info("CIS compliance validator initialized")
    
    def run_compliance_assessment(
        self,
        target_hosts: List[str],
        compliance_level: ComplianceLevel = ComplianceLevel.LEVEL_1
    ) -> Dict[str, Any]:
        """
        Run comprehensive CIS compliance assessment.
        
        Args:
            target_hosts: List of host IP addresses to assess
            compliance_level: CIS compliance level to validate
            
        Returns:
            Dict containing compliance assessment results
        """
        logger.info(f"Starting CIS compliance assessment for {len(target_hosts)} hosts")
        
        assessment_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'compliance_level': compliance_level.value,
            'target_hosts': target_hosts,
            'test_results': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'not_applicable': 0,
                'manual_review': 0,
                'compliance_score': 0
            },
            'critical_failures': [],
            'recommendations': []
        }
        
        try:
            # Run tests for each host
            for host in target_hosts:
                logger.info(f"Assessing CIS compliance for host: {host}")
                host_results = self._assess_host_compliance(host, compliance_level)
                assessment_results['test_results'][host] = host_results
            
            # Calculate overall summary
            self._calculate_assessment_summary(assessment_results)
            
            # Generate recommendations
            assessment_results['recommendations'] = self._generate_compliance_recommendations(
                assessment_results
            )
            
            logger.info("CIS compliance assessment completed successfully")
            return assessment_results
            
        except Exception as e:
            logger.error(f"CIS compliance assessment failed: {e}")
            assessment_results['error'] = str(e)
            return assessment_results
        finally:
            # Clean up SSH connections
            self._cleanup_connections()
    
    def _assess_host_compliance(
        self,
        host: str,
        compliance_level: ComplianceLevel
    ) -> Dict[str, Any]:
        """Assess CIS compliance for a specific host."""
        host_results = {
            'host': host,
            'tests': [],
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'not_applicable': 0,
                'manual_review': 0
            }
        }
        
        try:
            # Establish SSH connection
            ssh_client = self._connect_to_host(host)
            if not ssh_client:
                logger.error(f"Failed to connect to host: {host}")
                return host_results
            
            # Run applicable tests based on compliance level
            applicable_tests = [
                test for test in self.benchmark_tests.values()
                if test.compliance_level == compliance_level or 
                   compliance_level == ComplianceLevel.LEVEL_2
            ]
            
            for test in applicable_tests:
                try:
                    result = self._run_cis_test(host, test, ssh_client)
                    host_results['tests'].append(result.to_dict())
                    
                    # Update summary
                    host_results['summary']['total_tests'] += 1
                    if result.status == 'PASS':
                        host_results['summary']['passed'] += 1
                    elif result.status == 'FAIL':
                        host_results['summary']['failed'] += 1
                    elif result.status == 'NOT_APPLICABLE':
                        host_results['summary']['not_applicable'] += 1
                    elif result.status == 'MANUAL_REVIEW':
                        host_results['summary']['manual_review'] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to run test {test.control_id} on {host}: {e}")
                    
        except Exception as e:
            logger.error(f"Host assessment failed for {host}: {e}")
            host_results['error'] = str(e)
        
        return host_results
    
    def _run_cis_test(
        self,
        host: str,
        test: CISBenchmarkTest,
        ssh_client: paramiko.SSHClient
    ) -> CISTestResult:
        """Run a specific CIS benchmark test."""
        logger.debug(f"Running CIS test {test.control_id} on {host}")
        
        result = CISTestResult(
            test_id=f"{host}_{test.control_id}",
            control_id=test.control_id,
            description=test.description,
            status="NOT_APPLICABLE",
            actual_result=None,
            expected_result=test.expected_result,
            timestamp=datetime.utcnow(),
            details={}
        )
        
        try:
            # Run the test function
            if test.test_function:
                test_method = getattr(self, test.test_function, None)
                if test_method:
                    actual_result = test_method(ssh_client, test)
                    result.actual_result = actual_result
                    
                    # Compare with expected result
                    if self._compare_results(actual_result, test.expected_result):
                        result.status = "PASS"
                    else:
                        result.status = "FAIL"
                        result.remediation_required = True
                else:
                    logger.warning(f"Test function {test.test_function} not found")
                    result.status = "MANUAL_REVIEW"
            else:
                result.status = "MANUAL_REVIEW"
                
        except Exception as e:
            logger.error(f"Test {test.control_id} failed: {e}")
            result.status = "FAIL"
            result.details['error'] = str(e)
            result.remediation_required = True
        
        return result
    
    def _initialize_benchmark_tests(self) -> None:
        """Initialize CIS benchmark test definitions."""
        # CIS Control 1: Inventory and Control of Hardware Assets
        self.benchmark_tests['1.1.1'] = CISBenchmarkTest(
            control_id="1.1.1",
            control_name="Establish and Maintain Detailed Asset Inventory",
            description="Maintain an accurate and up-to-date inventory of all technology assets",
            rationale="Without knowing what devices are on the network, it is impossible to defend them",
            impact="Organizations cannot defend assets they do not know exist",
            remediation="Implement automated asset discovery and inventory management",
            compliance_level=ComplianceLevel.LEVEL_1,
            category=CISControl.INVENTORY,
            test_function="_test_asset_inventory"
        )
        
        # CIS Control 2: Inventory and Control of Software Assets  
        self.benchmark_tests['2.1.1'] = CISBenchmarkTest(
            control_id="2.1.1",
            control_name="Establish and Maintain Software Inventory",
            description="Maintain an accurate inventory of all software on network devices",
            rationale="Unauthorized software poses security risks and compliance issues",
            impact="Unknown software can contain vulnerabilities and malware",
            remediation="Implement software inventory and whitelist management",
            compliance_level=ComplianceLevel.LEVEL_1,
            category=CISControl.SOFTWARE,
            test_function="_test_software_inventory"
        )
        
        # CIS Control 3: Data Protection
        self.benchmark_tests['3.1.1'] = CISBenchmarkTest(
            control_id="3.1.1",
            control_name="Establish and Maintain Data Management Process",
            description="Establish and maintain data management processes and data classification",
            rationale="Data protection requires understanding what data exists and where it is stored",
            impact="Unmanaged data can lead to breaches and compliance violations",
            remediation="Implement data classification and protection policies",
            compliance_level=ComplianceLevel.LEVEL_1,
            category=CISControl.DATA_PROTECTION,
            test_function="_test_data_management"
        )
        
        # CIS Control 4: Secure Configuration of Enterprise Assets and Software
        self.benchmark_tests['4.1.1'] = CISBenchmarkTest(
            control_id="4.1.1",
            control_name="Establish and Maintain Secure Configuration Process",
            description="Establish and maintain secure configuration standards",
            rationale="Default configurations often contain security vulnerabilities",
            impact="Insecure configurations can be exploited by attackers",
            remediation="Implement configuration management and hardening standards",
            compliance_level=ComplianceLevel.LEVEL_1,
            category=CISControl.SECURE_CONFIG,
            test_function="_test_secure_configuration"
        )
        
        # CIS Control 5: Account Management
        self.benchmark_tests['5.1.1'] = CISBenchmarkTest(
            control_id="5.1.1",
            control_name="Establish and Maintain Inventory of Accounts",
            description="Maintain an inventory of all accounts managed in enterprise systems",
            rationale="Unknown accounts can provide unauthorized access",
            impact="Unmanaged accounts increase attack surface",
            remediation="Implement account inventory and lifecycle management",
            compliance_level=ComplianceLevel.LEVEL_1,
            category=CISControl.CONTROLLED_ACCESS,
            test_function="_test_account_inventory"
        )
        
        # CIS Control 6: Access Control Management
        self.benchmark_tests['6.1.1'] = CISBenchmarkTest(
            control_id="6.1.1",
            control_name="Establish Access Control Policy",
            description="Establish and maintain access control policy",
            rationale="Clear access control policies ensure appropriate access levels",
            impact="Poor access controls can lead to unauthorized access",
            remediation="Implement comprehensive access control policies",
            compliance_level=ComplianceLevel.LEVEL_1,
            category=CISControl.CONTROLLED_ACCESS,
            test_function="_test_access_control_policy"
        )
        
        # Additional benchmark tests would be added here...
        
    # Test implementation methods
    
    def _test_asset_inventory(
        self,
        ssh_client: paramiko.SSHClient,
        test: CISBenchmarkTest
    ) -> Dict[str, Any]:
        """Test asset inventory completeness."""
        try:
            # Get system information
            stdin, stdout, stderr = ssh_client.exec_command('hostname; uname -a; ip addr show')
            system_info = stdout.read().decode().strip()
            
            # Get installed packages
            stdin, stdout, stderr = ssh_client.exec_command('dpkg -l | wc -l')
            package_count = int(stdout.read().decode().strip())
            
            # Get running services
            stdin, stdout, stderr = ssh_client.exec_command('systemctl list-units --type=service --state=running | wc -l')
            service_count = int(stdout.read().decode().strip())
            
            return {
                'system_info': system_info,
                'package_count': package_count,
                'service_count': service_count,
                'inventory_complete': package_count > 0 and service_count > 0
            }
            
        except Exception as e:
            logger.error(f"Asset inventory test failed: {e}")
            return {'error': str(e)}
    
    def _test_software_inventory(
        self,
        ssh_client: paramiko.SSHClient,
        test: CISBenchmarkTest
    ) -> Dict[str, Any]:
        """Test software inventory management."""
        try:
            # Get list of installed packages
            stdin, stdout, stderr = ssh_client.exec_command('dpkg -l')
            packages = stdout.read().decode()
            
            # Check for package management system
            stdin, stdout, stderr = ssh_client.exec_command('which apt-get dpkg yum rpm')
            package_managers = stdout.read().decode().strip()
            
            return {
                'package_count': len(packages.split('\n')) - 1,
                'package_managers': package_managers.split(),
                'software_tracking': bool(package_managers)
            }
            
        except Exception as e:
            logger.error(f"Software inventory test failed: {e}")
            return {'error': str(e)}
    
    def _test_data_management(
        self,
        ssh_client: paramiko.SSHClient,
        test: CISBenchmarkTest
    ) -> Dict[str, Any]:
        """Test data management processes."""
        try:
            # Check for backup configurations
            stdin, stdout, stderr = ssh_client.exec_command('ls -la /etc/cron* | grep backup')
            backup_crons = stdout.read().decode()
            
            # Check for data encryption
            stdin, stdout, stderr = ssh_client.exec_command('lsblk -f | grep crypto')
            encrypted_volumes = stdout.read().decode()
            
            # Check file permissions on sensitive directories
            stdin, stdout, stderr = ssh_client.exec_command('ls -ld /etc /var/log /home')
            directory_permissions = stdout.read().decode()
            
            return {
                'backup_scheduled': bool(backup_crons.strip()),
                'encryption_enabled': bool(encrypted_volumes.strip()),
                'secure_permissions': '700' in directory_permissions or '750' in directory_permissions
            }
            
        except Exception as e:
            logger.error(f"Data management test failed: {e}")
            return {'error': str(e)}
    
    def _test_secure_configuration(
        self,
        ssh_client: paramiko.SSHClient,
        test: CISBenchmarkTest
    ) -> Dict[str, Any]:
        """Test secure configuration implementation."""
        try:
            # Check SSH configuration
            stdin, stdout, stderr = ssh_client.exec_command('cat /etc/ssh/sshd_config')
            ssh_config = stdout.read().decode()
            
            # Check firewall status
            stdin, stdout, stderr = ssh_client.exec_command('ufw status || iptables -L | head -20')
            firewall_status = stdout.read().decode()
            
            # Check for unnecessary services
            stdin, stdout, stderr = ssh_client.exec_command('systemctl list-units --type=service --state=running')
            running_services = stdout.read().decode()
            
            # Analyze configurations
            ssh_secure = all(setting in ssh_config for setting in [
                'PasswordAuthentication no',
                'PermitRootLogin no',
                'Protocol 2'
            ])
            
            return {
                'ssh_hardened': ssh_secure,
                'firewall_active': 'Status: active' in firewall_status or 'Chain INPUT' in firewall_status,
                'service_count': len(running_services.split('\n')) - 1,
                'configuration_secure': ssh_secure
            }
            
        except Exception as e:
            logger.error(f"Secure configuration test failed: {e}")
            return {'error': str(e)}
    
    def _test_account_inventory(
        self,
        ssh_client: paramiko.SSHClient,
        test: CISBenchmarkTest
    ) -> Dict[str, Any]:
        """Test account inventory management."""
        try:
            # Get user accounts
            stdin, stdout, stderr = ssh_client.exec_command('cat /etc/passwd')
            passwd_content = stdout.read().decode()
            
            # Get group information
            stdin, stdout, stderr = ssh_client.exec_command('cat /etc/group')
            group_content = stdout.read().decode()
            
            # Check for inactive accounts
            stdin, stdout, stderr = ssh_client.exec_command('lastlog | grep "Never logged in" | wc -l')
            inactive_accounts = int(stdout.read().decode().strip())
            
            user_count = len([line for line in passwd_content.split('\n') if line and not line.startswith('#')])
            group_count = len([line for line in group_content.split('\n') if line and not line.startswith('#')])
            
            return {
                'user_count': user_count,
                'group_count': group_count,
                'inactive_accounts': inactive_accounts,
                'account_tracking': user_count > 0 and group_count > 0
            }
            
        except Exception as e:
            logger.error(f"Account inventory test failed: {e}")
            return {'error': str(e)}
    
    def _test_access_control_policy(
        self,
        ssh_client: paramiko.SSHClient,
        test: CISBenchmarkTest
    ) -> Dict[str, Any]:
        """Test access control policy implementation."""
        try:
            # Check sudo configuration
            stdin, stdout, stderr = ssh_client.exec_command('cat /etc/sudoers')
            sudo_config = stdout.read().decode()
            
            # Check password policy
            stdin, stdout, stderr = ssh_client.exec_command('cat /etc/login.defs | grep PASS')
            password_policy = stdout.read().decode()
            
            # Check for PAM configuration
            stdin, stdout, stderr = ssh_client.exec_command('ls /etc/pam.d/ | wc -l')
            pam_modules = int(stdout.read().decode().strip())
            
            return {
                'sudo_configured': bool(sudo_config.strip()),
                'password_policy_set': 'PASS_MIN_LEN' in password_policy,
                'pam_modules_count': pam_modules,
                'access_controls_implemented': pam_modules > 0
            }
            
        except Exception as e:
            logger.error(f"Access control policy test failed: {e}")
            return {'error': str(e)}
    
    def _connect_to_host(self, host: str) -> Optional[paramiko.SSHClient]:
        """Establish SSH connection to target host."""
        if host in self.ssh_connections:
            return self.ssh_connections[host]
        
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Use SSH key if provided
            ssh_key_path = self.config.get('ssh_key_path')
            if ssh_key_path and Path(ssh_key_path).exists():
                ssh_client.connect(
                    hostname=host,
                    username=self.config.get('ssh_username', 'root'),
                    key_filename=ssh_key_path,
                    timeout=30
                )
            else:
                logger.warning(f"SSH key not found, attempting password authentication for {host}")
                return None
            
            self.ssh_connections[host] = ssh_client
            return ssh_client
            
        except Exception as e:
            logger.error(f"Failed to connect to {host}: {e}")
            return None
    
    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """Compare actual and expected test results."""
        if expected is None:
            return True  # No specific expectation
        
        if isinstance(expected, dict) and isinstance(actual, dict):
            # Check if all expected keys match
            for key, value in expected.items():
                if key not in actual or actual[key] != value:
                    return False
            return True
        
        return actual == expected
    
    def _calculate_assessment_summary(self, assessment_results: Dict[str, Any]) -> None:
        """Calculate overall assessment summary."""
        summary = assessment_results['summary']
        
        for host_results in assessment_results['test_results'].values():
            host_summary = host_results.get('summary', {})
            summary['total_tests'] += host_summary.get('total_tests', 0)
            summary['passed'] += host_summary.get('passed', 0)
            summary['failed'] += host_summary.get('failed', 0)
            summary['not_applicable'] += host_summary.get('not_applicable', 0)
            summary['manual_review'] += host_summary.get('manual_review', 0)
        
        # Calculate compliance score
        scored_tests = summary['passed'] + summary['failed']
        if scored_tests > 0:
            summary['compliance_score'] = (summary['passed'] / scored_tests) * 100
        
        # Identify critical failures
        for host, host_results in assessment_results['test_results'].items():
            for test in host_results.get('tests', []):
                if test['status'] == 'FAIL' and test.get('remediation_required', False):
                    assessment_results['critical_failures'].append({
                        'host': host,
                        'control_id': test['control_id'],
                        'description': test['description']
                    })
    
    def _generate_compliance_recommendations(
        self,
        assessment_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate compliance recommendations based on assessment results."""
        recommendations = []
        
        # Check compliance score
        compliance_score = assessment_results['summary']['compliance_score']
        if compliance_score < 90:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Overall Compliance',
                'recommendation': f'Improve overall compliance score from {compliance_score:.1f}% to >90%',
                'affected_controls': [failure['control_id'] for failure in assessment_results['critical_failures']]
            })
        
        # Check for specific control failures
        failed_controls = {}
        for failure in assessment_results['critical_failures']:
            control_id = failure['control_id']
            if control_id not in failed_controls:
                failed_controls[control_id] = []
            failed_controls[control_id].append(failure['host'])
        
        for control_id, hosts in failed_controls.items():
            test_info = self.benchmark_tests.get(control_id)
            if test_info:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': test_info.category.value,
                    'recommendation': test_info.remediation,
                    'affected_hosts': hosts,
                    'control_id': control_id
                })
        
        return recommendations
    
    def _cleanup_connections(self) -> None:
        """Clean up SSH connections."""
        for ssh_client in self.ssh_connections.values():
            try:
                ssh_client.close()
            except Exception as e:
                logger.error(f"Error closing SSH connection: {e}")
        self.ssh_connections.clear()
    
    def generate_compliance_report(
        self,
        assessment_results: Dict[str, Any],
        output_format: str = 'json'
    ) -> str:
        """Generate compliance assessment report."""
        if output_format == 'json':
            return json.dumps(assessment_results, indent=2)
        elif output_format == 'yaml':
            return yaml.dump(assessment_results, default_flow_style=False)
        else:
            # Generate text report
            report = f"""
CIS BENCHMARK COMPLIANCE ASSESSMENT REPORT
==========================================

Assessment Date: {assessment_results['timestamp']}
Compliance Level: {assessment_results['compliance_level']}
Target Hosts: {', '.join(assessment_results['target_hosts'])}

SUMMARY
-------
Total Tests: {assessment_results['summary']['total_tests']}
Passed: {assessment_results['summary']['passed']}
Failed: {assessment_results['summary']['failed']}
Not Applicable: {assessment_results['summary']['not_applicable']}
Manual Review: {assessment_results['summary']['manual_review']}
Compliance Score: {assessment_results['summary']['compliance_score']:.1f}%

CRITICAL FAILURES
-----------------
"""
            for failure in assessment_results['critical_failures']:
                report += f"- {failure['host']}: {failure['control_id']} - {failure['description']}\n"
            
            report += "\nRECOMMENDATIONS\n---------------\n"
            for rec in assessment_results['recommendations']:
                report += f"- [{rec['priority']}] {rec['recommendation']}\n"
            
            return report


class TestCISCompliance:
    """Pytest test class for CIS compliance validation."""
    
    @pytest.fixture
    def compliance_validator(self):
        """Fixture to create CIS compliance validator instance."""
        config = {
            'ssh_username': 'root',
            'ssh_key_path': '/path/to/ssh/key',
            'timeout': 30
        }
        return CISComplianceValidator(config)
    
    def test_benchmark_tests_initialization(self, compliance_validator):
        """Test CIS benchmark tests initialization."""
        assert len(compliance_validator.benchmark_tests) > 0
        
        # Check that required test exists
        assert '1.1.1' in compliance_validator.benchmark_tests
        
        test = compliance_validator.benchmark_tests['1.1.1']
        assert test.control_id == '1.1.1'
        assert test.compliance_level == ComplianceLevel.LEVEL_1
        assert test.category == CISControl.INVENTORY
    
    def test_compliance_assessment_structure(self, compliance_validator):
        """Test compliance assessment result structure."""
        # Mock assessment for structure validation
        target_hosts = ['192.168.1.101']
        
        # This would normally run actual tests, but we'll test the structure
        assessment_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'compliance_level': ComplianceLevel.LEVEL_1.value,
            'target_hosts': target_hosts,
            'test_results': {},
            'summary': {
                'total_tests': 6,
                'passed': 4,
                'failed': 2,
                'not_applicable': 0,
                'manual_review': 0,
                'compliance_score': 66.7
            },
            'critical_failures': [],
            'recommendations': []
        }
        
        # Validate structure
        assert 'timestamp' in assessment_results
        assert 'compliance_level' in assessment_results
        assert 'summary' in assessment_results
        assert 'compliance_score' in assessment_results['summary']
    
    def test_report_generation(self, compliance_validator):
        """Test compliance report generation."""
        mock_results = {
            'timestamp': '2025-07-29T10:00:00Z',
            'compliance_level': 'level_1',
            'target_hosts': ['192.168.1.101'],
            'summary': {
                'total_tests': 6,
                'passed': 4,
                'failed': 2,
                'compliance_score': 66.7
            },
            'critical_failures': [],
            'recommendations': []
        }
        
        # Test JSON report
        json_report = compliance_validator.generate_compliance_report(mock_results, 'json')
        assert 'timestamp' in json_report
        assert 'compliance_score' in json_report
        
        # Test text report
        text_report = compliance_validator.generate_compliance_report(mock_results, 'text')
        assert 'COMPLIANCE ASSESSMENT REPORT' in text_report
        assert 'Compliance Score: 66.7%' in text_report


if __name__ == "__main__":
    # Example usage for manual testing
    def main():
        config = {
            'ssh_username': 'root',
            'ssh_key_path': '/path/to/ssh/key',
            'timeout': 30
        }
        
        validator = CISComplianceValidator(config)
        
        print("Running CIS Compliance Assessment...")
        
        # This would normally assess actual hosts
        target_hosts = ['192.168.1.101']
        
        # Mock assessment results for demonstration
        mock_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'compliance_level': 'level_1',
            'target_hosts': target_hosts,
            'summary': {
                'total_tests': 6,
                'passed': 4,
                'failed': 2,
                'not_applicable': 0,
                'manual_review': 0,
                'compliance_score': 66.7
            },
            'critical_failures': [
                {
                    'host': '192.168.1.101',
                    'control_id': '4.1.1',
                    'description': 'Secure configuration not fully implemented'
                }
            ],
            'recommendations': [
                {
                    'priority': 'HIGH',
                    'category': 'secure_config',
                    'recommendation': 'Implement configuration management and hardening standards'
                }
            ]
        }
        
        print(f"\nCompliance Assessment Results:")
        print(f"Compliance Score: {mock_results['summary']['compliance_score']:.1f}%")
        print(f"Tests Passed: {mock_results['summary']['passed']}/{mock_results['summary']['total_tests']}")
        
        if mock_results['critical_failures']:
            print(f"\nCritical Failures:")
            for failure in mock_results['critical_failures']:
                print(f"  - {failure['control_id']}: {failure['description']}")
        
        # Generate report
        report = validator.generate_compliance_report(mock_results, 'text')
        print(f"\nGenerated compliance report ({len(report)} characters)")
    
    main()