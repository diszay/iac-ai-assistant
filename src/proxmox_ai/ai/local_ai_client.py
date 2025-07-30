"""
Memory-Efficient Local AI Model Integration for Proxmox Infrastructure Automation.

Provides offline AI capabilities for IaC code generation and optimization
with automatic hardware optimization and quantized model support.
"""

import os
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager

import requests
import structlog

from ..core.hardware_detector import hardware_detector, ModelRecommendation

logger = structlog.get_logger(__name__)


@dataclass
class AIResponse:
    """Response from local AI model."""
    content: str
    success: bool
    model_used: str
    processing_time: float
    skill_level: str
    memory_used_mb: float
    tokens_generated: int


@dataclass
class ModelCache:
    """Model caching for faster inference."""
    model_name: str
    loaded_at: float
    last_used: float
    memory_usage_mb: float
    context_cache: Dict[str, str]


class OptimizedLocalAIClient:
    """
    Hardware-optimized local AI client for Infrastructure as Code automation.
    
    Features:
    - Automatic hardware detection and model selection
    - Memory-efficient quantized models (1-3GB max)
    - Smart caching and context management
    - Multi-skill level adaptation
    - Performance monitoring
    """
    
    def __init__(self, 
                 model_name: Optional[str] = None, 
                 ollama_host: str = "http://localhost:11434",
                 auto_optimize: bool = True):
        """Initialize optimized local AI client."""
        
        # Get hardware-optimized configuration
        self.hardware_config = hardware_detector.get_runtime_config()
        
        # Use auto-detected model or provided model
        self.model_name = model_name or self.hardware_config["model"]
        self.ollama_host = ollama_host
        self.auto_optimize = auto_optimize
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0.0
        self.cache_hits = 0
        
        # Model cache for faster inference
        self.model_cache: Optional[ModelCache] = None
        self.context_cache: Dict[str, str] = {}
        
        # Skill level configurations optimized for hardware
        self.skill_levels = self._initialize_skill_levels()
        
        logger.info(
            "Optimized local AI client initialized", 
            model=self.model_name,
            hardware_config=self.hardware_config,
            host=ollama_host
        )
    
    def _initialize_skill_levels(self) -> Dict[str, Dict[str, Any]]:
        """Initialize skill-level configurations optimized for hardware."""
        perf_profile = hardware_detector.get_performance_profile()
        
        base_levels = {
            "beginner": {
                "description": "Simple, guided explanations with step-by-step instructions",
                "max_tokens": min(512, self.hardware_config["max_context_length"] // 4),
                "temperature": 0.1,
                "complexity": "low"
            },
            "intermediate": {
                "description": "Balanced detail with best practices and common patterns",
                "max_tokens": min(1024, self.hardware_config["max_context_length"] // 2),
                "temperature": 0.2,
                "complexity": "medium"
            },
            "expert": {
                "description": "Advanced configurations, optimizations, and edge cases",
                "max_tokens": self.hardware_config["max_context_length"],
                "temperature": 0.1,
                "complexity": "high"
            }
        }
        
        # Adjust based on performance profile
        if perf_profile["model_quality"] == "Basic":
            # Reduce complexity for low-end hardware
            for level in base_levels.values():
                level["max_tokens"] = min(level["max_tokens"], 256)
        
        return base_levels
    
    async def is_available(self) -> bool:
        """Check if local AI model is available with async support."""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            available = response.status_code == 200
            
            if available:
                # Check if our specific model is available
                tags = response.json().get("models", [])
                model_available = any(tag["name"].startswith(self.model_name.split(":")[0]) 
                                    for tag in tags)
                if not model_available:
                    logger.warning(
                        "Specific model not available, will attempt to use alternative",
                        requested_model=self.model_name
                    )
            
            return available
        except Exception as e:
            logger.warning("Local AI model not available", error=str(e))
            return False
    
    def _get_cache_key(self, prompt: str, skill_level: str) -> str:
        """Generate cache key for prompt."""
        import hashlib
        content = f"{prompt}:{skill_level}:{self.model_name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check if response is cached."""
        return self.context_cache.get(cache_key)
    
    def _update_cache(self, cache_key: str, response: str):
        """Update response cache with size limit."""
        max_cache_size = 50  # Limit cache size for memory efficiency
        
        if len(self.context_cache) >= max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.context_cache))
            del self.context_cache[oldest_key]
        
        self.context_cache[cache_key] = response
    
    async def generate_terraform_config(self, 
                                       description: str, 
                                       skill_level: str = "intermediate",
                                       provider: str = "proxmox") -> AIResponse:
        """Generate optimized Terraform configuration based on description."""
        
        skill_config = self.skill_levels.get(skill_level, self.skill_levels["intermediate"])
        
        prompt = f"""You are an expert in Infrastructure as Code using Terraform for Proxmox.
Skill level: {skill_level} - {skill_config['description']}

Generate a Terraform configuration for: {description}

Requirements:
- Use Proxmox provider
- Include proper resource definitions  
- Add appropriate variables and outputs
- Include security best practices
- {self._get_skill_specific_requirements(skill_level)}

Keep response concise. Respond with clean Terraform HCL code only."""
        
        return await self._make_optimized_request(prompt, skill_level)
    
    async def generate_ansible_playbook(self, 
                                       description: str, 
                                       skill_level: str = "intermediate") -> AIResponse:
        """Generate optimized Ansible playbook for VM configuration."""
        
        skill_config = self.skill_levels.get(skill_level, self.skill_levels["intermediate"])
        
        prompt = f"""You are an expert in Ansible automation for infrastructure configuration.
Skill level: {skill_level} - {skill_config['description']}

Generate an Ansible playbook for: {description}

Requirements:
- YAML format
- Include proper tasks and handlers
- Add security hardening steps
- Include error handling
- {self._get_skill_specific_requirements(skill_level)}

Keep response concise. Respond with clean Ansible YAML only."""
        
        return await self._make_optimized_request(prompt, skill_level)
    
    async def optimize_infrastructure(self, 
                                     config: str, 
                                     skill_level: str = "intermediate") -> AIResponse:
        """Optimize existing infrastructure configuration with hardware-aware analysis."""
        
        skill_config = self.skill_levels.get(skill_level, self.skill_levels["intermediate"])
        
        # Truncate config if too long to prevent context overflow
        max_config_length = skill_config["max_tokens"] // 2
        if len(config) > max_config_length:
            config = config[:max_config_length] + "\n... [truncated]"
        
        prompt = f"""You are an expert in infrastructure optimization and best practices.
Skill level: {skill_level} - {skill_config['description']}

Review and optimize this infrastructure configuration:

{config}

Focus on:
- Performance improvements
- Security enhancements
- Cost optimization
- Best practices
- {self._get_skill_specific_requirements(skill_level)}

Provide optimized configuration with brief explanations."""
        
        return await self._make_optimized_request(prompt, skill_level)
    
    async def explain_configuration(self, 
                                   config: str, 
                                   skill_level: str = "beginner") -> AIResponse:
        """Explain infrastructure configuration for learning with adaptive detail."""
        
        skill_config = self.skill_levels.get(skill_level, self.skill_levels["beginner"])
        
        # Truncate config if too long
        max_config_length = skill_config["max_tokens"] // 2
        if len(config) > max_config_length:
            config = config[:max_config_length] + "\n... [truncated]"
        
        prompt = f"""You are an expert teacher in Infrastructure as Code.
Skill level: {skill_level} - {skill_config['description']}

Explain this infrastructure configuration:

{config}

Explanation should include:
- What each component does
- Why it's structured this way
- Security considerations
- Best practices demonstrated
- {self._get_skill_specific_requirements(skill_level)}

Keep explanation clear and concise."""
        
        return await self._make_optimized_request(prompt, skill_level)
    
    def _get_skill_specific_requirements(self, skill_level: str) -> str:
        """Get skill-level specific requirements optimized for hardware."""
        skill_config = self.skill_levels.get(skill_level, self.skill_levels["intermediate"])
        
        base_requirements = {
            "beginner": "Use simple, clear examples with detailed comments",
            "intermediate": "Include best practices and common patterns",
            "expert": "Show advanced patterns and enterprise configurations"
        }
        
        requirement = base_requirements.get(skill_level, base_requirements["intermediate"])
        
        # Add hardware-specific constraints
        if skill_config["complexity"] == "low":
            requirement += ". Keep solutions simple and lightweight."
        
        return requirement
    
    async def _make_optimized_request(self, prompt: str, skill_level: str) -> AIResponse:
        """Make optimized request to local AI model with caching and monitoring."""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, skill_level)
        cached_response = self._check_cache(cache_key) if self.hardware_config["cache_enabled"] else None
        
        if cached_response:
            self.cache_hits += 1
            logger.info("Cache hit for AI request", cache_key=cache_key)
            return AIResponse(
                content=cached_response,
                success=True,
                model_used=f"{self.model_name} (cached)",
                processing_time=0.01,
                skill_level=skill_level,
                memory_used_mb=0.0,
                tokens_generated=len(cached_response.split())
            )
        
        try:
            if not await self.is_available():
                return AIResponse(
                    content="Local AI model not available. Please ensure Ollama is running.",
                    success=False,
                    model_used=self.model_name,
                    processing_time=0.0,
                    skill_level=skill_level,
                    memory_used_mb=0.0,
                    tokens_generated=0
                )
            
            # Get skill-specific configuration
            skill_config = self.skill_levels.get(skill_level, self.skill_levels["intermediate"])
            
            # Monitor resource usage before request
            resource_before = hardware_detector.monitor_resource_usage()
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": self.hardware_config["stream_response"],
                "options": {
                    "temperature": skill_config.get("temperature", self.hardware_config["temperature"]),
                    "top_p": self.hardware_config["top_p"],
                    "num_ctx": skill_config["max_tokens"],
                    "num_thread": self.hardware_config["cpu_threads"],
                    "use_mmap": self.hardware_config["memory_map"],
                    "use_mlock": True,  # Lock model in memory for faster inference
                    "num_gpu": 1 if self.hardware_config["use_gpu"] else 0
                }
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=self.hardware_config["timeout"]
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "")
                
                # Monitor resource usage after request
                resource_after = hardware_detector.monitor_resource_usage()
                memory_used = max(0, resource_after["memory_used_percent"] - resource_before["memory_used_percent"])
                
                # Update cache
                if self.hardware_config["cache_enabled"] and content:
                    self._update_cache(cache_key, content)
                
                # Update performance metrics
                self.request_count += 1
                self.total_processing_time += processing_time
                
                logger.info(
                    "Optimized AI request successful",
                    model=self.model_name,
                    skill_level=skill_level,
                    processing_time=processing_time,
                    memory_delta=memory_used,
                    tokens=len(content.split())
                )
                
                return AIResponse(
                    content=content,
                    success=True,
                    model_used=self.model_name,
                    processing_time=processing_time,
                    skill_level=skill_level,
                    memory_used_mb=memory_used * 1024,  # Convert to MB estimate
                    tokens_generated=len(content.split())
                )
            else:
                logger.error("Local AI request failed", status_code=response.status_code)
                return AIResponse(
                    content=f"AI request failed with status {response.status_code}",
                    success=False,
                    model_used=self.model_name,
                    processing_time=processing_time,
                    skill_level=skill_level,
                    memory_used_mb=0.0,
                    tokens_generated=0
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error("Local AI request error", error=str(e), processing_time=processing_time)
            return AIResponse(
                content=f"Error: {str(e)}",
                success=False,
                model_used=self.model_name,
                processing_time=processing_time,
                skill_level=skill_level,
                memory_used_mb=0.0,
                tokens_generated=0
            )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the AI client."""
        avg_processing_time = (
            self.total_processing_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        cache_hit_rate = (
            self.cache_hits / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        return {
            "total_requests": self.request_count,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": cache_hit_rate,
            "avg_processing_time": avg_processing_time,
            "total_processing_time": self.total_processing_time,
            "model_name": self.model_name,
            "hardware_config": self.hardware_config
        }
    
    def clear_cache(self):
        """Clear the response cache."""
        self.context_cache.clear()
        logger.info("AI response cache cleared")
    
    async def warmup_model(self) -> bool:
        """Warm up the model with a simple request to reduce first-request latency."""
        try:
            warmup_prompt = "Hello, are you ready?"
            response = await self._make_optimized_request(warmup_prompt, "beginner")
            return response.success
        except Exception as e:
            logger.warning("Model warmup failed", error=str(e))
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model and configuration."""
        recommendation = hardware_detector.get_optimal_model_config()
        performance_profile = hardware_detector.get_performance_profile()
        
        return {
            "current_model": self.model_name,
            "recommended_model": recommendation.model_name,
            "model_size": recommendation.model_size,
            "quantization": recommendation.quantization,
            "memory_usage_gb": recommendation.memory_usage_gb,
            "performance_profile": performance_profile,
            "skill_levels": list(self.skill_levels.keys())
        }


class HardwareOptimizedSkillManager:
    """Hardware-optimized Infrastructure as Code skill level adaptation."""
    
    def __init__(self):
        """Initialize hardware-optimized skill manager."""
        self.hardware_specs = hardware_detector.specs
        self.performance_profile = hardware_detector.get_performance_profile()
        self.templates = self._load_hardware_optimized_templates()
    
    def get_template(self, skill_level: str, template_type: str) -> Dict[str, Any]:
        """Get hardware-optimized template for specific skill level."""
        return self.templates.get(skill_level, {}).get(template_type, {})
    
    def _load_hardware_optimized_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load templates optimized for current hardware capabilities."""
        
        # Base templates
        base_templates = {
            "beginner": {
                "vm_basic": {
                    "description": "Simple VM with basic configuration",
                    "complexity": "low",
                    "features": ["basic_networking", "simple_storage"],
                    "memory_efficient": True
                },
                "network_simple": {
                    "description": "Basic network setup", 
                    "complexity": "low",
                    "features": ["single_vlan", "basic_firewall"]
                }
            },
            "intermediate": {
                "vm_clustered": {
                    "description": "Multi-VM setup with load balancing",
                    "complexity": "medium",
                    "features": ["clustering", "load_balancing"]
                },
                "network_segmented": {
                    "description": "Segmented network with VLANs",
                    "complexity": "medium", 
                    "features": ["multiple_vlans", "advanced_firewall"]
                }
            },
            "expert": {
                "vm_enterprise": {
                    "description": "Enterprise VM deployment",
                    "complexity": "high",
                    "features": ["high_availability", "auto_scaling"]
                },
                "network_enterprise": {
                    "description": "Enterprise network security",
                    "complexity": "high",
                    "features": ["micro_segmentation", "zero_trust"]
                }
            }
        }
        
        # Optimize based on hardware
        if self.hardware_specs.available_memory_gb < 4.0:
            # Reduce complexity for low memory systems
            for skill_level in base_templates:
                for template_name, template in base_templates[skill_level].items():
                    template["features"] = template["features"][:2]  # Limit features
                    template["memory_optimized"] = True
        
        return base_templates
    
    def get_optimal_skill_level(self, user_experience: str = "intermediate") -> str:
        """Get optimal skill level based on hardware and user experience."""
        if self.performance_profile["model_quality"] == "Basic":
            # Force simpler responses for low-end hardware
            return "beginner"
        elif self.performance_profile["model_quality"] == "Medium":
            return "intermediate" if user_experience in ["intermediate", "expert"] else "beginner"
        else:
            return user_experience


# Backward compatibility alias
LocalAIClient = OptimizedLocalAIClient

# Global instances with hardware optimization
optimized_ai_client = OptimizedLocalAIClient()
skill_manager = HardwareOptimizedSkillManager()

# Legacy compatibility
local_ai_client = optimized_ai_client