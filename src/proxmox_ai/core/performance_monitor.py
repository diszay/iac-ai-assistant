"""
Performance Monitoring and Benchmarking System for Local AI.

Provides comprehensive performance analysis, monitoring, and optimization
recommendations for hardware-constrained local AI inference.
"""

import os
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict

import structlog
import psutil

from .hardware_detector import hardware_detector

logger = structlog.get_logger(__name__)


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]


@dataclass
class BenchmarkResult:
    """Comprehensive benchmark result."""
    model_name: str
    hardware_config: Dict[str, Any]
    test_suite: str
    results: Dict[str, float]
    metadata: Dict[str, Any]
    timestamp: datetime
    duration_seconds: float


@dataclass
class SystemSnapshot:
    """System resource snapshot."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    load_average: float
    temperature: Optional[float]
    disk_io: Dict[str, Any]


class PerformanceMonitor:
    """
    Advanced performance monitoring system for local AI inference.
    
    Features:
    - Real-time system monitoring
    - AI inference performance tracking
    - Memory usage optimization
    - Temperature monitoring
    - Historical performance analysis
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize performance monitor."""
        self.data_dir = data_dir or Path.home() / ".proxmox-ai" / "performance"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance data storage
        self.metrics: List[PerformanceMetric] = []
        self.benchmarks: List[BenchmarkResult] = []
        self.snapshots: List[SystemSnapshot] = []
        
        # Monitoring configuration
        self.monitoring_enabled = False
        self.snapshot_interval = 5.0  # seconds
        self.max_metrics_history = 1000
        
        logger.info("Performance monitor initialized", data_dir=str(self.data_dir))
    
    def start_monitoring(self):
        """Start continuous system monitoring."""
        if not self.monitoring_enabled:
            self.monitoring_enabled = True
            asyncio.create_task(self._monitoring_loop())
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_enabled = False
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_enabled:
            try:
                snapshot = self._take_system_snapshot()
                self.snapshots.append(snapshot)
                
                # Keep only recent snapshots (last hour)
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.snapshots = [s for s in self.snapshots if s.timestamp > cutoff_time]
                
                await asyncio.sleep(self.snapshot_interval)
                
            except Exception as e:
                logger.error("Monitoring loop error", error=str(e))
                await asyncio.sleep(10)  # Wait longer on error
    
    def _take_system_snapshot(self) -> SystemSnapshot:
        """Take a snapshot of current system resources."""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get load average (Unix only)
        load_avg = 0.0
        if hasattr(os, 'getloadavg'):
            load_avg = os.getloadavg()[0]
        
        # Get temperature if available
        temperature = None
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get CPU temperature if available
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            temperature = entries[0].current if entries else None
                            break
        except Exception:
            pass
        
        # Get disk I/O stats
        disk_io = {}
        try:
            disk_counters = psutil.disk_io_counters()
            if disk_counters:
                disk_io = {
                    'read_bytes': disk_counters.read_bytes,
                    'write_bytes': disk_counters.write_bytes,
                    'read_count': disk_counters.read_count,
                    'write_count': disk_counters.write_count
                }
        except Exception:
            pass
        
        return SystemSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_gb=memory.available / (1024**3),
            load_average=load_avg,
            temperature=temperature,
            disk_io=disk_io
        )
    
    def record_metric(self, name: str, value: float, unit: str, context: Dict[str, Any] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_name=name,
            value=value,
            unit=unit,
            context=context or {}
        )
        
        self.metrics.append(metric)
        
        # Keep only recent metrics
        if len(self.metrics) > self.max_metrics_history:
            self.metrics = self.metrics[-self.max_metrics_history:]
    
    async def run_comprehensive_benchmark(self, model_name: str) -> BenchmarkResult:
        """Run comprehensive AI model benchmark."""
        logger.info("Starting comprehensive benchmark", model=model_name)
        
        start_time = time.time()
        hardware_config = hardware_detector.get_runtime_config()
        
        # Start monitoring for benchmark
        was_monitoring = self.monitoring_enabled
        if not was_monitoring:
            self.start_monitoring()
        
        try:
            # Test suite
            test_results = {}
            
            # 1. Simple prompt test
            simple_result = await self._benchmark_simple_prompt(model_name)
            test_results.update(simple_result)
            
            # 2. Complex code generation test
            complex_result = await self._benchmark_complex_generation(model_name)
            test_results.update(complex_result)
            
            # 3. Memory stress test
            memory_result = await self._benchmark_memory_usage(model_name)
            test_results.update(memory_result)
            
            # 4. Concurrent request test
            concurrent_result = await self._benchmark_concurrent_requests(model_name)
            test_results.update(concurrent_result)
            
            # 5. Context length test
            context_result = await self._benchmark_context_length(model_name)
            test_results.update(context_result)
            
            duration = time.time() - start_time
            
            benchmark = BenchmarkResult(
                model_name=model_name,
                hardware_config=hardware_config,
                test_suite="comprehensive",
                results=test_results,
                metadata={
                    "hardware_specs": asdict(hardware_detector.specs),
                    "test_timestamp": datetime.now().isoformat(),
                    "benchmark_version": "1.0"
                },
                timestamp=datetime.now(),
                duration_seconds=duration
            )
            
            self.benchmarks.append(benchmark)
            await self._save_benchmark(benchmark)
            
            logger.info("Benchmark completed", model=model_name, duration=duration)
            return benchmark
            
        finally:
            if not was_monitoring:
                self.stop_monitoring()
    
    async def _benchmark_simple_prompt(self, model_name: str) -> Dict[str, float]:
        """Benchmark simple prompt response."""
        from ..ai.local_ai_client import optimized_ai_client
        
        prompt = "Hello, respond with a simple greeting."
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().percent
        
        try:
            response = await optimized_ai_client._make_optimized_request(prompt, "beginner")
            
            end_time = time.time()
            memory_after = psutil.virtual_memory().percent
            
            if response.success:
                return {
                    "simple_response_time": end_time - start_time,
                    "simple_tokens_generated": response.tokens_generated,
                    "simple_memory_delta": memory_after - memory_before,
                    "simple_tokens_per_second": response.tokens_generated / (end_time - start_time) if end_time > start_time else 0
                }
        except Exception as e:
            logger.error("Simple prompt benchmark failed", error=str(e))
        
        return {
            "simple_response_time": 0,
            "simple_tokens_generated": 0,
            "simple_memory_delta": 0,
            "simple_tokens_per_second": 0
        }
    
    async def _benchmark_complex_generation(self, model_name: str) -> Dict[str, float]:
        """Benchmark complex code generation."""
        from ..ai.local_ai_client import optimized_ai_client
        
        prompt = """Generate a Terraform configuration for a web server with:
        - Ubuntu 22.04 VM with 4GB RAM and 2 CPU cores
        - Nginx web server configuration
        - SSL certificate setup
        - Firewall rules for HTTP/HTTPS
        - Monitoring and logging configuration"""
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().percent
        
        try:
            response = await optimized_ai_client._make_optimized_request(prompt, "intermediate")
            
            end_time = time.time()
            memory_after = psutil.virtual_memory().percent
            
            if response.success:
                return {
                    "complex_response_time": end_time - start_time,
                    "complex_tokens_generated": response.tokens_generated,
                    "complex_memory_delta": memory_after - memory_before,
                    "complex_tokens_per_second": response.tokens_generated / (end_time - start_time) if end_time > start_time else 0
                }
        except Exception as e:
            logger.error("Complex generation benchmark failed", error=str(e))
        
        return {
            "complex_response_time": 0,
            "complex_tokens_generated": 0,
            "complex_memory_delta": 0,
            "complex_tokens_per_second": 0
        }
    
    async def _benchmark_memory_usage(self, model_name: str) -> Dict[str, float]:
        """Benchmark memory usage patterns."""
        memory_samples = []
        
        # Take memory samples during inference
        for i in range(5):
            memory_before = psutil.virtual_memory().percent
            
            try:
                from ..ai.local_ai_client import optimized_ai_client
                prompt = f"Generate a small Terraform resource example {i+1}."
                await optimized_ai_client._make_optimized_request(prompt, "beginner")
                
                memory_after = psutil.virtual_memory().percent
                memory_samples.append(memory_after - memory_before)
                
            except Exception:
                memory_samples.append(0)
            
            await asyncio.sleep(1)  # Small delay between tests
        
        return {
            "memory_usage_avg": sum(memory_samples) / len(memory_samples) if memory_samples else 0,
            "memory_usage_max": max(memory_samples) if memory_samples else 0,
            "memory_usage_min": min(memory_samples) if memory_samples else 0,
            "memory_stability": 1.0 - (max(memory_samples) - min(memory_samples)) / 100 if memory_samples else 0
        }
    
    async def _benchmark_concurrent_requests(self, model_name: str) -> Dict[str, float]:
        """Benchmark concurrent request handling."""
        from ..ai.local_ai_client import optimized_ai_client
        
        async def single_request(request_id: int):
            start_time = time.time()
            try:
                prompt = f"Generate a simple VM configuration example #{request_id}."
                response = await optimized_ai_client._make_optimized_request(prompt, "beginner")
                return time.time() - start_time if response.success else None
            except Exception:
                return None
        
        # Run 3 concurrent requests (limited for memory efficiency)
        start_time = time.time()
        tasks = [single_request(i) for i in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_times = [r for r in results if isinstance(r, (int, float)) and r is not None]
        
        return {
            "concurrent_requests": len(tasks),
            "concurrent_successful": len(successful_times),
            "concurrent_total_time": total_time,
            "concurrent_avg_response_time": sum(successful_times) / len(successful_times) if successful_times else 0,
            "concurrent_throughput": len(successful_times) / total_time if total_time > 0 else 0
        }
    
    async def _benchmark_context_length(self, model_name: str) -> Dict[str, float]:
        """Benchmark context length handling."""
        from ..ai.local_ai_client import optimized_ai_client
        
        # Test different context lengths
        context_tests = [
            ("short", "Generate a simple Terraform variable."),
            ("medium", "Generate a Terraform configuration with: " + " ".join(["requirement"] * 50)),
            ("long", "Generate a comprehensive Terraform setup with: " + " ".join(["detailed requirement"] * 100))
        ]
        
        results = {}
        
        for test_name, prompt in context_tests:
            start_time = time.time()
            
            try:
                response = await optimized_ai_client._make_optimized_request(prompt, "intermediate")
                response_time = time.time() - start_time
                
                results[f"context_{test_name}_time"] = response_time
                results[f"context_{test_name}_success"] = 1.0 if response.success else 0.0
                results[f"context_{test_name}_tokens"] = response.tokens_generated if response.success else 0
                
            except Exception:
                results[f"context_{test_name}_time"] = 0
                results[f"context_{test_name}_success"] = 0.0
                results[f"context_{test_name}_tokens"] = 0
        
        return results
    
    async def _save_benchmark(self, benchmark: BenchmarkResult):
        """Save benchmark results to disk."""
        try:
            timestamp = benchmark.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_{benchmark.model_name.replace(':', '_')}_{timestamp}.json"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w') as f:
                # Convert dataclass to dict for JSON serialization
                data = asdict(benchmark)
                data['timestamp'] = benchmark.timestamp.isoformat()
                json.dump(data, f, indent=2, default=str)
            
            logger.info("Benchmark saved", filepath=str(filepath))
            
        except Exception as e:
            logger.error("Failed to save benchmark", error=str(e))
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        # Recent system metrics
        recent_snapshots = [s for s in self.snapshots if s.timestamp > datetime.now() - timedelta(minutes=10)]
        
        # Recent performance metrics
        recent_metrics = [m for m in self.metrics if m.timestamp > datetime.now() - timedelta(minutes=10)]
        
        # Latest benchmark
        latest_benchmark = self.benchmarks[-1] if self.benchmarks else None
        
        summary = {
            "system_status": {
                "monitoring_active": self.monitoring_enabled,
                "recent_snapshots": len(recent_snapshots),
                "avg_cpu_usage": sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots) if recent_snapshots else 0,
                "avg_memory_usage": sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots) if recent_snapshots else 0,
                "current_memory_available": recent_snapshots[-1].memory_available_gb if recent_snapshots else 0
            },
            "ai_performance": {
                "total_metrics": len(self.metrics),
                "recent_metrics": len(recent_metrics),
                "benchmarks_available": len(self.benchmarks)
            },
            "hardware_info": {
                "specs": asdict(hardware_detector.specs),
                "runtime_config": hardware_detector.get_runtime_config()
            }
        }
        
        if latest_benchmark:
            summary["latest_benchmark"] = {
                "model": latest_benchmark.model_name,
                "timestamp": latest_benchmark.timestamp.isoformat(),
                "duration": latest_benchmark.duration_seconds,
                "key_results": {
                    "simple_tokens_per_second": latest_benchmark.results.get("simple_tokens_per_second", 0),
                    "complex_tokens_per_second": latest_benchmark.results.get("complex_tokens_per_second", 0),
                    "memory_stability": latest_benchmark.results.get("memory_stability", 0),
                    "concurrent_throughput": latest_benchmark.results.get("concurrent_throughput", 0)
                }
            }
        
        return summary
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        
        # Analyze recent performance
        recent_snapshots = [s for s in self.snapshots if s.timestamp > datetime.now() - timedelta(minutes=10)]
        
        if recent_snapshots:
            avg_memory = sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots)
            avg_cpu = sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots)
            
            if avg_memory > 85:
                recommendations.append("High memory usage - consider using a smaller quantized model (Q4_0)")
            
            if avg_cpu > 80:
                recommendations.append("High CPU usage - reduce concurrent requests or model complexity")
            
            if hardware_detector.specs.available_memory_gb < 4:
                recommendations.append("Limited memory - use beginner skill level for faster responses")
            
            # Temperature warnings
            if recent_snapshots[-1].temperature and recent_snapshots[-1].temperature > 80:
                recommendations.append("High CPU temperature - consider reducing inference frequency")
        
        # Analyze benchmark results
        if self.benchmarks:
            latest = self.benchmarks[-1]
            
            if latest.results.get("simple_tokens_per_second", 0) < 5:
                recommendations.append("Slow inference speed - consider switching to TinyLlama model")
            
            if latest.results.get("memory_stability", 1) < 0.8:
                recommendations.append("Unstable memory usage - enable model caching")
            
            if latest.results.get("concurrent_throughput", 0) < 1:
                recommendations.append("Poor concurrent performance - limit to single requests")
        
        if not recommendations:
            recommendations.append("Performance is optimal for your hardware configuration")
        
        return recommendations


# Global instance
performance_monitor = PerformanceMonitor()