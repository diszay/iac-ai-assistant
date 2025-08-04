"""
Efficient Model Manager for Lightweight Local AI.

Handles model loading, caching, quantization, and memory optimization
for hardware-constrained environments.
"""

import os
import json
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import structlog
import requests

from .hardware_detector import hardware_detector, ModelRecommendation

logger = structlog.get_logger(__name__)


@dataclass
class ModelInfo:
    """Information about an available model."""
    name: str
    size_gb: float
    quantization: str
    family: str
    description: str
    downloaded: bool
    last_used: Optional[datetime]
    performance_score: float


@dataclass 
class ModelPerformance:
    """Performance metrics for a model."""
    tokens_per_second: float
    memory_usage_mb: float
    first_token_latency_ms: float
    context_length: int
    quality_score: float


class EfficientModelManager:
    """
    Manages model lifecycle for memory-efficient local AI inference.
    
    Features:
    - Automatic model selection based on hardware
    - Smart model caching and memory management
    - Quantized model support
    - Performance monitoring and optimization
    """
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """Initialize efficient model manager."""
        self.ollama_host = ollama_host
        self.hardware_config = hardware_detector.get_runtime_config()
        self.performance_history: Dict[str, List[ModelPerformance]] = {}
        self.model_cache: Dict[str, datetime] = {}
        
        # Model catalog optimized for different hardware tiers
        self.model_catalog = self._initialize_model_catalog()
        
        logger.info("Efficient model manager initialized", hardware_config=self.hardware_config)
    
    def _initialize_model_catalog(self) -> Dict[str, ModelInfo]:
        """Initialize catalog of optimized models for different hardware tiers."""
        
        catalog = {
            # Ultra-lightweight models (< 2GB)
            "tinyllama:1.1b-chat-q4_0": ModelInfo(
                name="tinyllama:1.1b-chat-q4_0",
                size_gb=1.2,
                quantization="Q4_0",
                family="tinyllama",
                description="Ultra-lightweight model for basic tasks",
                downloaded=False,
                last_used=None,
                performance_score=6.0
            ),
            
            "deepseek-coder:1.3b-instruct-q4_K_M": ModelInfo(
                name="deepseek-coder:1.3b-instruct-q4_K_M", 
                size_gb=1.8,
                quantization="Q4_K_M",
                family="deepseek-coder",
                description="Lightweight coding model",
                downloaded=False,
                last_used=None,
                performance_score=7.5
            ),
            
            # Mid-range models (2-4GB)
            "phi:2.7b-chat-q4_K_M": ModelInfo(
                name="phi:2.7b-chat-q4_K_M",
                size_gb=2.8,
                quantization="Q4_K_M", 
                family="phi",
                description="Balanced performance and efficiency",
                downloaded=False,
                last_used=None,
                performance_score=8.0
            ),
            
            "codellama:7b-instruct-q4_0": ModelInfo(
                name="codellama:7b-instruct-q4_0",
                size_gb=3.2,
                quantization="Q4_0",
                family="codellama",
                description="Code-focused model with good performance",
                downloaded=False,
                last_used=None,
                performance_score=8.5
            ),
            
            # High-performance models (4GB+)
            "llama3.1:8b-instruct-q4_0": ModelInfo(
                name="llama3.1:8b-instruct-q4_0",
                size_gb=4.7,
                quantization="Q4_0",
                family="llama3.1",
                description="Advanced 8B model excellent for IaC and technical tasks",
                downloaded=False,
                last_used=None,
                performance_score=9.5
            ),
            
            "codellama:7b-instruct-q4_K_M": ModelInfo(
                name="codellama:7b-instruct-q4_K_M",
                size_gb=4.5,
                quantization="Q4_K_M",
                family="codellama",
                description="High-quality code generation",
                downloaded=False,
                last_used=None,
                performance_score=9.0
            ),
            
            "mistral:7b-instruct-q4_K_M": ModelInfo(
                name="mistral:7b-instruct-q4_K_M",
                size_gb=4.2,
                quantization="Q4_K_M",
                family="mistral",
                description="High-quality general purpose model",
                downloaded=False,
                last_used=None,
                performance_score=9.2
            )
        }
        
        return catalog
    
    async def get_optimal_model(self) -> ModelInfo:
        """Get the optimal model for current hardware configuration."""
        available_memory = hardware_detector.specs.available_memory_gb
        
        # Filter models by memory constraints
        suitable_models = [
            model for model in self.model_catalog.values()
            if model.size_gb <= (available_memory * 0.8)  # Leave 20% buffer
        ]
        
        if not suitable_models:
            # Fallback to smallest model
            return min(self.model_catalog.values(), key=lambda m: m.size_gb)
        
        # Sort by performance score and select best
        best_model = max(suitable_models, key=lambda m: m.performance_score)
        
        logger.info(
            "Optimal model selected",
            model=best_model.name,
            size_gb=best_model.size_gb,
            available_memory_gb=available_memory
        )
        
        return best_model
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """Ensure model is downloaded and available."""
        try:
            # Check if model exists
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code != 200:
                logger.error("Ollama not available")
                return False
            
            models = response.json().get("models", [])
            model_exists = any(m["name"] == model_name for m in models)
            
            if model_exists:
                logger.info("Model already available", model=model_name)
                return True
            
            # Download model
            logger.info("Downloading model", model=model_name)
            return await self._download_model(model_name)
            
        except Exception as e:
            logger.error("Failed to ensure model availability", model=model_name, error=str(e))
            return False
    
    async def _download_model(self, model_name: str) -> bool:
        """Download model with progress monitoring."""
        try:
            # Use subprocess for better control
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor download progress
            start_time = time.time()
            while True:
                return_code = process.poll()
                if return_code is not None:
                    break
                
                # Check if download is taking too long
                if time.time() - start_time > 600:  # 10 minutes timeout
                    process.terminate()
                    logger.error("Model download timeout", model=model_name)
                    return False
                
                await asyncio.sleep(1)
            
            if return_code == 0:
                logger.info("Model download completed", model=model_name)
                # Update catalog
                if model_name in self.model_catalog:
                    self.model_catalog[model_name].downloaded = True
                return True
            else:
                stderr = process.stderr.read() if process.stderr else ""
                logger.error("Model download failed", model=model_name, error=stderr)
                return False
                
        except Exception as e:
            logger.error("Model download error", model=model_name, error=str(e))
            return False
    
    def get_model_recommendations(self) -> List[ModelInfo]:
        """Get list of recommended models for current hardware."""
        available_memory = hardware_detector.specs.available_memory_gb
        
        recommendations = []
        for model in self.model_catalog.values():
            if model.size_gb <= available_memory * 0.9:  # 10% buffer
                recommendations.append(model)
        
        # Sort by performance score descending
        recommendations.sort(key=lambda m: m.performance_score, reverse=True)
        
        return recommendations[:3]  # Top 3 recommendations
    
    async def benchmark_model(self, model_name: str) -> Optional[ModelPerformance]:
        """Benchmark model performance on current hardware."""
        try:
            # Ensure model is available
            if not await self.ensure_model_available(model_name):
                return None
            
            # Simple benchmark prompt
            benchmark_prompt = "Write a simple Terraform resource for a VM with 2GB RAM and 2 CPU cores."
            
            # Measure performance
            start_time = time.time()
            memory_before = hardware_detector.monitor_resource_usage()
            
            # Make test request
            payload = {
                "model": model_name,
                "prompt": benchmark_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 512,  # Small context for benchmarking
                    "num_thread": self.hardware_config["cpu_threads"]
                }
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=60
            )
            
            end_time = time.time()
            memory_after = hardware_detector.monitor_resource_usage()
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Calculate metrics
                tokens_generated = len(response_text.split())
                total_time = end_time - start_time
                tokens_per_second = tokens_generated / total_time if total_time > 0 else 0
                
                memory_delta = memory_after["memory_used_percent"] - memory_before["memory_used_percent"]
                memory_usage_mb = memory_delta * hardware_detector.specs.total_memory_gb * 1024 / 100
                
                performance = ModelPerformance(
                    tokens_per_second=tokens_per_second,
                    memory_usage_mb=max(0, memory_usage_mb),
                    first_token_latency_ms=total_time * 1000,  # Simplified
                    context_length=512,
                    quality_score=8.0 if len(response_text) > 50 else 6.0  # Simple quality heuristic
                )
                
                # Store performance history
                if model_name not in self.performance_history:
                    self.performance_history[model_name] = []
                self.performance_history[model_name].append(performance)
                
                logger.info(
                    "Model benchmark completed",
                    model=model_name,
                    tokens_per_second=tokens_per_second,
                    memory_usage_mb=memory_usage_mb
                )
                
                return performance
            
        except Exception as e:
            logger.error("Model benchmark failed", model=model_name, error=str(e))
        
        return None
    
    def get_performance_history(self, model_name: str) -> List[ModelPerformance]:
        """Get performance history for a model."""
        return self.performance_history.get(model_name, [])
    
    async def cleanup_unused_models(self, keep_count: int = 2) -> int:
        """Clean up unused models to free memory."""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code != 200:
                return 0
            
            models = response.json().get("models", [])
            if len(models) <= keep_count:
                return 0
            
            # Sort by last used time (oldest first)
            models_with_usage = []
            for model in models:
                model_name = model["name"]
                last_used = self.model_cache.get(model_name, datetime.min)
                models_with_usage.append((model_name, last_used))
            
            models_with_usage.sort(key=lambda x: x[1])
            
            # Remove oldest models
            removed_count = 0
            models_to_remove = models_with_usage[:-keep_count]
            
            for model_name, _ in models_to_remove:
                try:
                    # Remove model
                    subprocess.run(["ollama", "rm", model_name], check=True, timeout=30)
                    removed_count += 1
                    logger.info("Removed unused model", model=model_name)
                except Exception as e:
                    logger.warning("Failed to remove model", model=model_name, error=str(e))
            
            return removed_count
            
        except Exception as e:
            logger.error("Cleanup failed", error=str(e))
            return 0
    
    def update_model_usage(self, model_name: str):
        """Update last used time for a model."""
        self.model_cache[model_name] = datetime.now()
    
    def get_memory_usage_estimate(self, model_name: str) -> float:
        """Get estimated memory usage for a model in GB."""
        if model_name in self.model_catalog:
            return self.model_catalog[model_name].size_gb
        
        # Fallback estimation based on model name
        if "1.1b" in model_name or "1.3b" in model_name:
            return 1.5
        elif "2.7b" in model_name or "3b" in model_name:
            return 2.5
        elif "7b" in model_name:
            return 4.0
        elif "8b" in model_name:
            return 4.7
        elif "13b" in model_name:
            return 8.0
        else:
            return 2.0  # Conservative estimate
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system and model status."""
        hardware_status = hardware_detector.monitor_resource_usage()
        
        # Get loaded models
        loaded_models = []
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    model_name = model["name"]
                    loaded_models.append({
                        "name": model_name,
                        "size_gb": self.get_memory_usage_estimate(model_name),
                        "last_used": self.model_cache.get(model_name)
                    })
        except Exception:
            pass
        
        return {
            "hardware": hardware_status,
            "loaded_models": loaded_models,
            "recommended_model": self.hardware_config["model"],
            "cache_count": len(self.model_cache),
            "performance_records": len(self.performance_history)
        }


# Global instance
model_manager = EfficientModelManager()