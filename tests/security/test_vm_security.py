"""
VM Security Configuration Testing

Tests for VM security hardening including:
- SSH key authentication validation
- Firewall configuration verification
- LUKS encryption validation
- Service exposure assessment
- CIS benchmark compliance
"""

import pytest
import asyncio
import subprocess
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import paramiko
import nmap
import socket

logger = logging.getLogger(__name__)


class VMSecurityTester:
    """Comprehensive VM security testing framework."""
    
    def __init__(self, vm_ip: str, ssh_key_path: str):
        self.vm_ip = vm_ip
        self.ssh_key_path = ssh_key_path
        self.nm = nmap.PortScanner()
        
    async def test_ssh_key_authentication(self) -> Dict[str, bool]:
        """Test SSH key-based authentication and disable password auth."""
        results = {
            'ssh_key_auth_works': False,
            'password_auth_disabled': False,
            'root_login_disabled': False,
            'ssh_protocol_v2_only': False
        }
        
        try:
            # Test SSH key authentication
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Test key-based auth
            ssh.connect(
                hostname=self.vm_ip,
                username='root',
                key_filename=self.ssh_key_path,
                timeout=10
            )
            results['ssh_key_auth_works'] = True
            
            # Check SSH configuration
            stdin, stdout, stderr = ssh.exec_command('cat /etc/ssh/sshd_config')
            ssh_config = stdout.read().decode()
            
            # Verify security settings
            if 'PasswordAuthentication no' in ssh_config:
                results['password_auth_disabled'] = True
            if 'PermitRootLogin no' in ssh_config or 'PermitRootLogin prohibit-password' in ssh_config:
                results['root_login_disabled'] = True
            if 'Protocol 2' in ssh_config:
                results['ssh_protocol_v2_only'] = True
                
            ssh.close()
            
        except Exception as e:
            logger.error(f"SSH authentication test failed: {e}")
            
        return results
    
    async def test_firewall_configuration(self) -> Dict[str, any]:
        """Test firewall rules and port exposure."""
        results = {
            'firewall_active': False,
            'exposed_ports': [],
            'dangerous_services': [],
            'firewall_rules_count': 0
        }
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.vm_ip, key_filename=self.ssh_key_path)
            
            # Check if firewall is active
            stdin, stdout, stderr = ssh.exec_command('systemctl is-active ufw || systemctl is-active firewalld || systemctl is-active iptables')
            firewall_status = stdout.read().decode().strip()
            results['firewall_active'] = firewall_status == 'active'
            
            # Get firewall rules count
            stdin, stdout, stderr = ssh.exec_command('iptables -L | wc -l')
            rules_count = stdout.read().decode().strip()
            results['firewall_rules_count'] = int(rules_count) if rules_count.isdigit() else 0
            
            # Port scan to identify exposed services
            scan_result = self.nm.scan(self.vm_ip, '1-65535')
            if self.vm_ip in scan_result['scan']:
                for port in scan_result['scan'][self.vm_ip]['tcp']:
                    port_info = scan_result['scan'][self.vm_ip]['tcp'][port]
                    if port_info['state'] == 'open':
                        results['exposed_ports'].append({
                            'port': port,
                            'service': port_info.get('name', 'unknown'),
                            'version': port_info.get('version', 'unknown')
                        })
                        
                        # Identify dangerous services
                        dangerous_services = ['telnet', 'ftp', 'rsh', 'rlogin', 'tftp']
                        if port_info.get('name', '').lower() in dangerous_services:
                            results['dangerous_services'].append(port_info.get('name'))
            
            ssh.close()
            
        except Exception as e:
            logger.error(f"Firewall configuration test failed: {e}")
            
        return results
    
    async def test_luks_encryption(self) -> Dict[str, bool]:
        """Test LUKS disk encryption status."""
        results = {
            'luks_encrypted': False,
            'strong_cipher': False,
            'key_slots_used': 0
        }
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.vm_ip, key_filename=self.ssh_key_path)
            
            # Check for LUKS devices
            stdin, stdout, stderr = ssh.exec_command('lsblk -f | grep crypto_LUKS')
            luks_devices = stdout.read().decode().strip()
            results['luks_encrypted'] = bool(luks_devices)
            
            if luks_devices:
                # Get LUKS device info
                stdin, stdout, stderr = ssh.exec_command('cryptsetup luksDump /dev/sda2 2>/dev/null || cryptsetup luksDump /dev/vda2 2>/dev/null')
                luks_info = stdout.read().decode()
                
                # Check cipher strength
                if 'aes-xts-plain64' in luks_info.lower():
                    results['strong_cipher'] = True
                    
                # Count key slots
                key_slot_count = luks_info.count('Key Slot')
                results['key_slots_used'] = key_slot_count
            
            ssh.close()
            
        except Exception as e:
            logger.error(f"LUKS encryption test failed: {e}")
            
        return results
    
    async def test_cis_benchmark_compliance(self) -> Dict[str, bool]:
        """Test CIS benchmark compliance."""
        results = {
            'no_unused_filesystems': False,
            'secure_boot_settings': False,
            'kernel_parameters_secure': False,
            'logging_configured': False,
            'time_sync_enabled': False,
            'audit_logging_enabled': False
        }
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.vm_ip, key_filename=self.ssh_key_path)
            
            # Check for unused filesystems
            stdin, stdout, stderr = ssh.exec_command('lsmod | grep -E "(cramfs|freevxfs|jffs2|hfs|hfsplus|squashfs|udf|fat|vfat)"')
            unused_fs = stdout.read().decode().strip()
            results['no_unused_filesystems'] = not bool(unused_fs)
            
            # Check kernel parameters
            stdin, stdout, stderr = ssh.exec_command('sysctl kernel.randomize_va_space')
            va_space = stdout.read().decode().strip()
            results['kernel_parameters_secure'] = 'kernel.randomize_va_space = 2' in va_space
            
            # Check logging
            stdin, stdout, stderr = ssh.exec_command('systemctl is-active rsyslog')
            logging_status = stdout.read().decode().strip()
            results['logging_configured'] = logging_status == 'active'
            
            # Check time synchronization
            stdin, stdout, stderr = ssh.exec_command('systemctl is-active ntp || systemctl is-active chronyd')
            time_sync = stdout.read().decode().strip()
            results['time_sync_enabled'] = time_sync == 'active'
            
            # Check audit logging
            stdin, stdout, stderr = ssh.exec_command('systemctl is-active auditd')
            audit_status = stdout.read().decode().strip()
            results['audit_logging_enabled'] = audit_status == 'active'
            
            ssh.close()
            
        except Exception as e:
            logger.error(f"CIS benchmark test failed: {e}")
            
        return results
    
    async def test_network_isolation(self, target_ips: List[str]) -> Dict[str, any]:
        """Test network isolation between VMs."""
        results = {
            'isolated_networks': True,
            'unreachable_targets': [],
            'reachable_targets': [],
            'network_policies_active': False
        }
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.vm_ip, key_filename=self.ssh_key_path)
            
            for target_ip in target_ips:
                # Test network connectivity
                stdin, stdout, stderr = ssh.exec_command(f'ping -c 3 -W 2 {target_ip}')
                ping_result = stdout.read().decode()
                
                if '3 received' in ping_result:
                    results['reachable_targets'].append(target_ip)
                else:
                    results['unreachable_targets'].append(target_ip)
            
            # Overall isolation check
            results['isolated_networks'] = len(results['reachable_targets']) == 0
            
            ssh.close()
            
        except Exception as e:
            logger.error(f"Network isolation test failed: {e}")
            
        return results


class TestVMSecurity:
    """Pytest test class for VM security validation."""
    
    @pytest.fixture
    def vm_tester(self):
        """Fixture to create VM security tester instance."""
        # These should be configured through environment variables
        vm_ip = "192.168.1.101"  # Example VM IP
        ssh_key_path = "/path/to/ssh/key"  # Should be configurable
        return VMSecurityTester(vm_ip, ssh_key_path)
    
    @pytest.mark.asyncio
    async def test_ssh_security(self, vm_tester):
        """Test SSH security configuration."""
        results = await vm_tester.test_ssh_key_authentication()
        
        assert results['ssh_key_auth_works'], "SSH key authentication must work"
        assert results['password_auth_disabled'], "Password authentication must be disabled"
        assert results['ssh_protocol_v2_only'], "Only SSH protocol version 2 should be enabled"
    
    @pytest.mark.asyncio
    async def test_firewall_security(self, vm_tester):
        """Test firewall configuration and port exposure."""
        results = await vm_tester.test_firewall_configuration()
        
        assert results['firewall_active'], "Firewall must be active"
        assert len(results['dangerous_services']) == 0, f"Dangerous services found: {results['dangerous_services']}"
        assert results['firewall_rules_count'] > 5, "Insufficient firewall rules configured"
    
    @pytest.mark.asyncio
    async def test_encryption_security(self, vm_tester):
        """Test disk encryption configuration."""
        results = await vm_tester.test_luks_encryption()
        
        assert results['luks_encrypted'], "Disk encryption must be enabled"
        assert results['strong_cipher'], "Strong encryption cipher must be used"
        assert results['key_slots_used'] > 0, "LUKS key slots must be configured"
    
    @pytest.mark.asyncio
    async def test_cis_compliance(self, vm_tester):
        """Test CIS benchmark compliance."""
        results = await vm_tester.test_cis_benchmark_compliance()
        
        assert results['no_unused_filesystems'], "Unused filesystems must be disabled"
        assert results['kernel_parameters_secure'], "Secure kernel parameters must be set"
        assert results['logging_configured'], "System logging must be configured"
        assert results['time_sync_enabled'], "Time synchronization must be enabled"
        assert results['audit_logging_enabled'], "Audit logging must be enabled"
    
    @pytest.mark.asyncio
    async def test_network_isolation(self, vm_tester):
        """Test network isolation between VMs."""
        target_ips = ["192.168.1.102", "192.168.1.103"]  # Example target VMs
        results = await vm_tester.test_network_isolation(target_ips)
        
        assert results['isolated_networks'], "VMs must be properly isolated"
        assert len(results['reachable_targets']) == 0, f"Unexpected network access to: {results['reachable_targets']}"


if __name__ == "__main__":
    # Example usage for manual testing
    async def main():
        tester = VMSecurityTester("192.168.1.101", "/path/to/ssh/key")
        
        print("Running VM Security Tests...")
        
        ssh_results = await tester.test_ssh_key_authentication()
        print(f"SSH Security: {ssh_results}")
        
        firewall_results = await tester.test_firewall_configuration()
        print(f"Firewall Security: {firewall_results}")
        
        encryption_results = await tester.test_luks_encryption()
        print(f"Encryption Security: {encryption_results}")
        
        cis_results = await tester.test_cis_benchmark_compliance()
        print(f"CIS Compliance: {cis_results}")
        
    asyncio.run(main())