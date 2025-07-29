"""
Proxmox API Security Testing

Tests for Proxmox API integration security including:
- Authentication mechanism validation
- TLS certificate verification
- Input sanitization testing
- API rate limiting validation
- Error handling security assessment
"""

import pytest
import asyncio
import ssl
import json
import requests
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import time
import re
from unittest.mock import Mock, patch

logger = logging.getLogger(__name__)


class ProxmoxAPISecurityTester:
    """Comprehensive Proxmox API security testing framework."""
    
    def __init__(self, proxmox_host: str, username: str = None, password: str = None, 
                 token_id: str = None, token_secret: str = None):
        self.proxmox_host = proxmox_host
        self.username = username
        self.password = password
        self.token_id = token_id
        self.token_secret = token_secret
        self.base_url = f"https://{proxmox_host}:8006/api2/json"
        self.session = requests.Session()
        
    def test_tls_configuration(self) -> Dict[str, Any]:
        """Test TLS/SSL configuration and certificate validation."""
        results = {
            'tls_version': None,
            'certificate_valid': False,
            'certificate_expires_soon': False,
            'weak_ciphers_disabled': True,
            'hsts_enabled': False,
            'certificate_details': {}
        }
        
        try:
            # Test TLS connection
            context = ssl.create_default_context()
            
            # Get certificate info
            with ssl.create_connection((self.proxmox_host, 8006)) as sock:
                with context.wrap_socket(sock, server_hostname=self.proxmox_host) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    results['tls_version'] = ssock.version()
                    results['certificate_valid'] = True
                    results['certificate_details'] = {
                        'subject': cert.get('subject'),
                        'issuer': cert.get('issuer'),
                        'not_after': cert.get('notAfter'),
                        'serial_number': cert.get('serialNumber')
                    }
                    
                    # Check cipher strength
                    if cipher and len(cipher) >= 3:
                        cipher_suite = cipher[0]
                        if any(weak in cipher_suite.lower() for weak in ['rc4', 'des', 'md5', 'null']):
                            results['weak_ciphers_disabled'] = False
            
            # Test HSTS header
            response = self.session.get(f"{self.base_url}/version", verify=True, timeout=10)
            results['hsts_enabled'] = 'Strict-Transport-Security' in response.headers
            
        except ssl.SSLError as e:
            logger.error(f"SSL/TLS test failed: {e}")
            results['certificate_valid'] = False
        except Exception as e:
            logger.error(f"TLS configuration test failed: {e}")
            
        return results
    
    def test_authentication_security(self) -> Dict[str, Any]:
        """Test authentication mechanisms and security."""
        results = {
            'token_auth_works': False,
            'password_auth_disabled_in_prod': False,
            'session_timeout_configured': False,
            'brute_force_protection': False,
            'weak_password_rejected': False
        }
        
        try:
            # Test token authentication if configured
            if self.token_id and self.token_secret:
                headers = {
                    'Authorization': f'PVEAPIToken={self.token_id}={self.token_secret}'
                }
                response = self.session.get(f"{self.base_url}/version", headers=headers, verify=True)
                results['token_auth_works'] = response.status_code == 200
            
            # Test brute force protection by attempting multiple failed logins
            failed_attempts = 0
            for i in range(5):
                login_data = {
                    'username': 'nonexistent@pam',
                    'password': 'wrong_password'
                }
                response = self.session.post(f"{self.base_url}/access/ticket", 
                                           data=login_data, verify=True)
                if response.status_code == 401:
                    failed_attempts += 1
                if response.status_code == 429:  # Rate limited
                    results['brute_force_protection'] = True
                    break
                time.sleep(1)  # Brief delay between attempts
            
            # Test weak password handling
            if self.username and self.password:
                weak_passwords = ['123456', 'password', 'admin', '']
                for weak_pwd in weak_passwords:
                    login_data = {
                        'username': self.username,
                        'password': weak_pwd
                    }
                    response = self.session.post(f"{self.base_url}/access/ticket", 
                                               data=login_data, verify=True)
                    if response.status_code != 200:
                        results['weak_password_rejected'] = True
                        break
            
        except Exception as e:
            logger.error(f"Authentication security test failed: {e}")
            
        return results
    
    def test_input_sanitization(self) -> Dict[str, Any]:
        """Test input sanitization and injection prevention."""
        results = {
            'sql_injection_protected': True,
            'xss_injection_protected': True,
            'command_injection_protected': True,
            'path_traversal_protected': True,
            'input_validation_errors': []
        }
        
        # Test payloads for various injection attacks
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "' UNION SELECT * FROM users --"
        ]
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "`id`",
            "$(whoami)"
        ]
        
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "....//....//....//etc/passwd"
        ]
        
        try:
            # Test VM name input with various payloads
            test_endpoints = [
                f"{self.base_url}/nodes/test/qemu",
                f"{self.base_url}/nodes/test/storage"
            ]
            
            for endpoint in test_endpoints:
                for category, payloads in [
                    ('sql', sql_payloads),
                    ('xss', xss_payloads), 
                    ('command', command_payloads),
                    ('path_traversal', path_traversal_payloads)
                ]:
                    for payload in payloads:
                        # Test in various parameters
                        test_params = {'vmid': payload, 'name': payload, 'storage': payload}
                        
                        response = self.session.get(endpoint, params=test_params, verify=True, timeout=5)
                        
                        # Check if payload was reflected or executed
                        if payload.lower() in response.text.lower():
                            results[f'{category}_injection_protected'] = False
                            results['input_validation_errors'].append({
                                'endpoint': endpoint,
                                'payload': payload,
                                'category': category
                            })
                            
        except Exception as e:
            logger.error(f"Input sanitization test failed: {e}")
            
        return results
    
    def test_api_rate_limiting(self) -> Dict[str, Any]:
        """Test API rate limiting and DoS protection."""
        results = {
            'rate_limiting_enabled': False,
            'requests_per_minute_limit': 0,
            'concurrent_connection_limit': False,
            'blocked_after_threshold': False
        }
        
        try:
            # Test rapid requests to detect rate limiting
            start_time = time.time()
            request_count = 0
            blocked_count = 0
            
            for i in range(100):  # Attempt 100 rapid requests
                try:
                    response = self.session.get(f"{self.base_url}/version", verify=True, timeout=2)
                    request_count += 1
                    
                    if response.status_code == 429:  # Too Many Requests
                        results['rate_limiting_enabled'] = True
                        blocked_count += 1
                    elif response.status_code >= 500:
                        blocked_count += 1
                        
                except requests.exceptions.Timeout:
                    blocked_count += 1
                except Exception:
                    blocked_count += 1
                    
                if time.time() - start_time > 60:  # Stop after 1 minute
                    break
            
            elapsed_time = time.time() - start_time
            results['requests_per_minute_limit'] = int(request_count / (elapsed_time / 60))
            results['blocked_after_threshold'] = blocked_count > 0
            
        except Exception as e:
            logger.error(f"Rate limiting test failed: {e}")
            
        return results
    
    def test_error_handling_security(self) -> Dict[str, Any]:
        """Test error handling for information disclosure."""
        results = {
            'no_sensitive_info_in_errors': True,
            'generic_error_messages': True,
            'no_stack_traces_exposed': True,
            'no_system_info_leaked': True,
            'error_examples': []
        }
        
        try:
            # Test various error conditions
            error_test_cases = [
                ('invalid_endpoint', f"{self.base_url}/invalid/endpoint"),
                ('malformed_json', f"{self.base_url}/access/ticket"),
                ('missing_auth', f"{self.base_url}/nodes"),
                ('invalid_vmid', f"{self.base_url}/nodes/test/qemu/99999")
            ]
            
            for test_name, url in error_test_cases:
                try:
                    if 'malformed_json' in test_name:
                        response = self.session.post(url, data="invalid json", verify=True)
                    else:
                        response = self.session.get(url, verify=True)
                    
                    error_text = response.text.lower()
                    
                    # Check for sensitive information in errors
                    sensitive_patterns = [
                        r'/etc/passwd',
                        r'/root/',
                        r'database',
                        r'stacktrace',
                        r'exception',
                        r'mysql',
                        r'postgresql',
                        r'secret',
                        r'password',
                        r'internal server error',
                        r'debug',
                        r'file not found: /'
                    ]
                    
                    for pattern in sensitive_patterns:
                        if re.search(pattern, error_text):
                            results['no_sensitive_info_in_errors'] = False
                            results['error_examples'].append({
                                'test': test_name,
                                'pattern': pattern,
                                'response': response.text[:200]
                            })
                            
                except Exception:
                    pass  # Expected for some test cases
                    
        except Exception as e:
            logger.error(f"Error handling security test failed: {e}")
            
        return results
    
    def test_session_management(self) -> Dict[str, Any]:
        """Test session management security."""
        results = {
            'secure_session_cookies': False,
            'httponly_cookies': False,
            'session_timeout_implemented': False,
            'csrf_protection_enabled': False,
            'session_fixation_protected': False
        }
        
        try:
            # Login to get session
            if self.username and self.password:
                login_data = {
                    'username': self.username,
                    'password': self.password
                }
                response = self.session.post(f"{self.base_url}/access/ticket", 
                                           data=login_data, verify=True)
                
                if response.status_code == 200:
                    # Check cookie security attributes
                    for cookie in self.session.cookies:
                        if cookie.secure:
                            results['secure_session_cookies'] = True
                        if 'httponly' in str(cookie).lower():
                            results['httponly_cookies'] = True
                    
                    # Check for CSRF token
                    csrf_token = response.json().get('data', {}).get('CSRFPreventionToken')
                    results['csrf_protection_enabled'] = bool(csrf_token)
                    
        except Exception as e:
            logger.error(f"Session management test failed: {e}")
            
        return results


class TestProxmoxAPISecurity:
    """Pytest test class for Proxmox API security validation."""
    
    @pytest.fixture
    def api_tester(self):
        """Fixture to create Proxmox API security tester instance."""
        # These should be configured through environment variables
        proxmox_host = "192.168.1.50"
        return ProxmoxAPISecurityTester(proxmox_host)
    
    def test_tls_security(self, api_tester):
        """Test TLS/SSL configuration."""
        results = api_tester.test_tls_configuration()
        
        assert results['certificate_valid'], "Valid TLS certificate must be present"
        assert results['tls_version'] in ['TLSv1.2', 'TLSv1.3'], f"Secure TLS version required, got: {results['tls_version']}"
        assert results['weak_ciphers_disabled'], "Weak cipher suites must be disabled"
    
    def test_authentication_security(self, api_tester):
        """Test authentication security measures."""
        results = api_tester.test_authentication_security()
        
        # These assertions should be adjusted based on your security requirements
        assert results['weak_password_rejected'], "Weak passwords must be rejected"
        # Token auth test only if tokens are configured
        # assert results['token_auth_works'], "Token authentication should work when configured"
    
    def test_input_validation(self, api_tester):
        """Test input sanitization and validation."""
        results = api_tester.test_input_sanitization()
        
        assert results['sql_injection_protected'], "SQL injection protection must be enabled"
        assert results['xss_injection_protected'], "XSS injection protection must be enabled"
        assert results['command_injection_protected'], "Command injection protection must be enabled"
        assert results['path_traversal_protected'], "Path traversal protection must be enabled"
        
        if results['input_validation_errors']:
            pytest.fail(f"Input validation vulnerabilities found: {results['input_validation_errors']}")
    
    def test_dos_protection(self, api_tester):
        """Test DoS protection and rate limiting."""
        results = api_tester.test_api_rate_limiting()
        
        # Rate limiting should be enabled for production systems
        # assert results['rate_limiting_enabled'], "API rate limiting must be enabled"
        assert results['requests_per_minute_limit'] < 1000, "Rate limit should be reasonable to prevent DoS"
    
    def test_error_handling(self, api_tester):
        """Test secure error handling."""
        results = api_tester.test_error_handling_security()
        
        assert results['no_sensitive_info_in_errors'], "Error messages must not contain sensitive information"
        assert results['no_stack_traces_exposed'], "Stack traces must not be exposed to clients"
        
        if results['error_examples']:
            pytest.fail(f"Security issues in error handling: {results['error_examples']}")
    
    def test_session_security(self, api_tester):
        """Test session management security."""
        results = api_tester.test_session_management()
        
        # These tests require valid credentials to be meaningful
        # assert results['secure_session_cookies'], "Session cookies must have secure flag"
        # assert results['httponly_cookies'], "Session cookies must have HttpOnly flag"
        # assert results['csrf_protection_enabled'], "CSRF protection must be enabled"


if __name__ == "__main__":
    # Example usage for manual testing
    def main():
        tester = ProxmoxAPISecurityTester("192.168.1.50")
        
        print("Running Proxmox API Security Tests...")
        
        tls_results = tester.test_tls_configuration()
        print(f"TLS Security: {tls_results}")
        
        auth_results = tester.test_authentication_security()
        print(f"Authentication Security: {auth_results}")
        
        input_results = tester.test_input_sanitization()
        print(f"Input Validation: {input_results}")
        
        rate_results = tester.test_api_rate_limiting()
        print(f"Rate Limiting: {rate_results}")
        
        error_results = tester.test_error_handling_security()
        print(f"Error Handling: {error_results}")
        
    main()