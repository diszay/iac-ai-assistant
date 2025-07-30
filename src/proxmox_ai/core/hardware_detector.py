"""
Hardware Detection and Auto-Configuration System.

Optimizes local AI model selection based on available system resources.
"""

import os
import psutil
import platform
import subprocess
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class HardwareSpecs:
    """System hardware specifications."""
    total_memory_gb: float
    available_memory_gb: float
    cpu_cores: int
    cpu_model: str
    gpu_available: bool
    gpu_memory_gb: float
    architecture: str
    platform_system: str


@dataclass
class ModelRecommendation:
    """AI model recommendation based on hardware."""
    model_name: str
    model_size: str
    memory_usage_gb: float
    quantization: str
    inference_engine: str
    max_context_length: int
    expected_performance: str


class HardwareDetector:
    """
    Detects system hardware capabilities and recommends optimal AI model configurations.
    """
    
    def __init__(self):
        """Initialize hardware detector."""
        self.specs = self._detect_hardware()
        logger.info("Hardware detected", specs=self.specs)
    
    def _detect_hardware(self) -> HardwareSpecs:
        """Detect current system hardware specifications."""
        memory = psutil.virtual_memory()
        
        # Get CPU information
        cpu_count = psutil.cpu_count(logical=False)
        cpu_model = self._get_cpu_model()
        
        # Check for GPU
        gpu_available, gpu_memory = self._detect_gpu()
        
        specs = HardwareSpecs(
            total_memory_gb=memory.total / (1024**3),
            available_memory_gb=memory.available / (1024**3),
            cpu_cores=cpu_count,
            cpu_model=cpu_model,
            gpu_available=gpu_available,
            gpu_memory_gb=gpu_memory,
            architecture=platform.machine(),
            platform_system=platform.system()
        )
        
        return specs
    
    def _get_cpu_model(self) -> str:
        """Get CPU model information."""
        try:
            if platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
        except Exception:
            pass
        
        return f"{platform.processor()} ({platform.machine()})"
    
    def _detect_gpu(self) -> Tuple[bool, float]:
        """Detect GPU availability and memory."""
        gpu_memory = 0.0
        gpu_available = False
        
        try:
            # Try NVIDIA GPU detection
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                gpu_memory = float(result.stdout.strip()) / 1024  # Convert MB to GB
                gpu_available = True
                logger.info("NVIDIA GPU detected", gpu_memory_gb=gpu_memory)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        if not gpu_available:
            # Try Intel GPU detection (basic)
            try:
                result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
                if "VGA" in result.stdout and any(vendor in result.stdout.lower() 
                                                for vendor in ["intel", "amd"]):
                    gpu_available = True
                    gpu_memory = 1.0  # Estimate for integrated graphics
                    logger.info("Integrated GPU detected")
            except Exception:
                pass
        
        return gpu_available, gpu_memory
    
    def get_optimal_model_config(self) -> ModelRecommendation:
        """Get optimal model configuration based on hardware."""
        available_memory = self.specs.available_memory_gb
        
        # Model recommendations based on available memory
        if available_memory >= 6.0:
            # High-end configuration
            return ModelRecommendation(
                model_name="codellama:7b-instruct-q4_K_M",
                model_size="7B",
                memory_usage_gb=4.5,
                quantization="Q4_K_M",
                inference_engine="llama.cpp",
                max_context_length=4096,
                expected_performance="High"
            )
        elif available_memory >= 4.0:
            # Medium configuration
            return ModelRecommendation(
                model_name="codellama:7b-instruct-q4_0",
                model_size="7B",
                memory_usage_gb=3.2,
                quantization="Q4_0",
                inference_engine="llama.cpp",
                max_context_length=2048,
                expected_performance="Medium"
            )
        elif available_memory >= 2.5:
            # Low-memory configuration
            return ModelRecommendation(
                model_name="deepseek-coder:1.3b-instruct-q4_K_M",
                model_size="1.3B",
                memory_usage_gb=1.8,
                quantization="Q4_K_M",
                inference_engine="llama.cpp",
                max_context_length=2048,
                expected_performance="Medium"
            )
        else:
            # Ultra-low memory configuration
            return ModelRecommendation(
                model_name="tinyllama:1.1b-chat-q4_0",
                model_size="1.1B",
                memory_usage_gb=1.2,
                quantization="Q4_0",
                inference_engine="llama.cpp",
                max_context_length=1024,
                expected_performance="Basic"
            )
    
    def get_runtime_config(self) -> Dict[str, Any]:
        """Get runtime configuration optimized for current hardware."""
        recommendation = self.get_optimal_model_config()
        
        # CPU thread optimization
        cpu_threads = min(self.specs.cpu_cores, 4)  # Cap at 4 for efficiency
        
        config = {
            "model": recommendation.model_name,
            "quantization": recommendation.quantization,
            "max_context_length": recommendation.max_context_length,
            "cpu_threads": cpu_threads,
            "memory_map": True,
            "use_gpu": self.specs.gpu_available and self.specs.gpu_memory_gb > 2.0,
            "batch_size": 1,  # Keep small for responsiveness
            "temperature": 0.1,
            "top_p": 0.9,
            "timeout": 30,  # Reasonable timeout for local inference
            "cache_enabled": True,
            "stream_response": False  # Disable streaming for CLI usage
        }
        
        return config
    
    def validate_model_compatibility(self, model_name: str) -> bool:
        """Validate if a model can run on current hardware."""
        model_memory_requirements = {
            "codellama:7b": 4.5,
            "codellama:13b": 8.0,
            "deepseek-coder:1.3b": 1.8,
            "tinyllama:1.1b": 1.2,
            "phi:2.7b": 2.8,
            "mistral:7b": 4.2
        }
        
        # Extract base model name
        base_model = model_name.split(":")[0] + ":" + model_name.split(":")[1].split("-")[0]
        required_memory = model_memory_requirements.get(base_model, 2.0)
        
        return self.specs.available_memory_gb >= required_memory
    
    def get_performance_profile(self) -> Dict[str, str]:
        """Get expected performance profile for current hardware."""
        recommendation = self.get_optimal_model_config()
        
        profile = {
            "inference_speed": "Fast" if self.specs.cpu_cores >= 4 else "Medium",
            "model_quality": recommendation.expected_performance,
            "memory_usage": f"{recommendation.memory_usage_gb:.1f}GB",
            "context_window": f"{recommendation.max_context_length} tokens",
            "recommended_use": self._get_use_case_recommendation()
        }
        
        return profile
    
    def _get_use_case_recommendation(self) -> str:
        """Get recommended use cases based on hardware."""
        if self.specs.available_memory_gb >= 6.0:
            return "Full IaC generation, optimization, and complex analysis"
        elif self.specs.available_memory_gb >= 4.0:
            return "IaC generation and basic optimization"
        elif self.specs.available_memory_gb >= 2.5:
            return "Simple IaC templates and configuration assistance"
        else:
            return "Basic configuration help and simple templates"
    
    def monitor_resource_usage(self) -> Dict[str, float]:
        """Monitor current resource usage."""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "memory_used_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),  
            "cpu_usage_percent": cpu_percent,
            "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
        }


# Global instance
hardware_detector = HardwareDetector()