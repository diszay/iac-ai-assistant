"""
Memory usage profiling tests for local AI implementation.

Validates that the local AI system operates within target memory constraints (<3GB RAM)
and provides detailed memory usage analysis for optimization.
"""

import os
import sys
import time
import pytest
import psutil
import threading
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from contextlib import contextmanager

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from proxmox_ai.ai.local_ai_client import LocalAIClient


@dataclass
class MemorySnapshot:
    """Memory usage snapshot at a specific point in time."""
    timestamp: float
    rss_mb: float  # Resident Set Size in MB
    vms_mb: float  # Virtual Memory Size in MB
    shared_mb: float  # Shared memory in MB
    data_mb: float  # Data segment size in MB
    peak_rss_mb: float  # Peak RSS usage in MB


class MemoryProfiler:
    """Profiles memory usage during AI operations."""
    
    def __init__(self, target_pid: Optional[int] = None):
        """Initialize memory profiler."""
        self.target_pid = target_pid or os.getpid()
        self.process = psutil.Process(self.target_pid)
        self.snapshots: List[MemorySnapshot] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self, interval: float = 0.1):
        """Start continuous memory monitoring."""
        self.monitoring = True
        self.snapshots.clear()
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self) -> List[MemorySnapshot]:
        """Stop monitoring and return collected snapshots."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        return self.snapshots.copy()
        
    def _monitor_loop(self, interval: float):
        """Continuous monitoring loop."""
        while self.monitoring:
            try:
                memory_info = self.process.memory_info()
                memory_full = self.process.memory_full_info()
                
                snapshot = MemorySnapshot(
                    timestamp=time.time(),
                    rss_mb=memory_info.rss / 1024 / 1024,
                    vms_mb=memory_info.vms / 1024 / 1024,
                    shared_mb=memory_full.shared / 1024 / 1024,
                    data_mb=getattr(memory_full, 'data', 0) / 1024 / 1024,
                    peak_rss_mb=getattr(memory_full, 'peak_wset', memory_info.rss) / 1024 / 1024
                )
                
                self.snapshots.append(snapshot)
                time.sleep(interval)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            except Exception as e:
                print(f"Memory monitoring error: {e}")
                time.sleep(interval)
                
    def get_peak_memory(self) -> Tuple[float, float]:
        """Get peak RSS and VMS memory usage in MB."""
        if not self.snapshots:
            return 0.0, 0.0
            
        peak_rss = max(snapshot.rss_mb for snapshot in self.snapshots)
        peak_vms = max(snapshot.vms_mb for snapshot in self.snapshots)
        return peak_rss, peak_vms
        
    def get_memory_stats(self) -> Dict[str, float]:
        """Get comprehensive memory usage statistics."""
        if not self.snapshots:
            return {}
            
        rss_values = [s.rss_mb for s in self.snapshots]
        vms_values = [s.vms_mb for s in self.snapshots]
        
        return {
            'peak_rss_mb': max(rss_values),
            'avg_rss_mb': sum(rss_values) / len(rss_values),
            'min_rss_mb': min(rss_values),
            'peak_vms_mb': max(vms_values),
            'avg_vms_mb': sum(vms_values) / len(vms_values),
            'min_vms_mb': min(vms_values),
            'memory_growth_mb': max(rss_values) - min(rss_values),
            'sample_count': len(self.snapshots)
        }


@contextmanager
def memory_profiling(interval: float = 0.1):
    """Context manager for memory profiling."""
    profiler = MemoryProfiler()
    profiler.start_monitoring(interval)
    try:
        yield profiler
    finally:
        profiler.stop_monitoring()


class TestMemoryProfiling:
    """Test suite for memory usage profiling of local AI operations."""
    
    # Memory constraints (configurable)
    MEMORY_TARGET_MB = 3072  # 3GB target
    MEMORY_WARNING_MB = 2560  # 2.5GB warning threshold
    MEMORY_CRITICAL_MB = 3584  # 3.5GB critical threshold
    
    @pytest.fixture
    def ai_client(self):
        """Create local AI client for testing."""
        return LocalAIClient(model_name="llama3.2:latest")
        
    def test_baseline_memory_usage(self, ai_client):
        """Test baseline memory usage without AI operations."""
        with memory_profiling(interval=0.05) as profiler:
            # Just wait and measure baseline
            time.sleep(2.0)
            
        stats = profiler.get_memory_stats()
        
        assert stats['peak_rss_mb'] > 0, "Should have measurable memory usage"
        assert stats['peak_rss_mb'] < 1024, "Baseline should be under 1GB"
        
        print(f"Baseline Memory Usage: {stats['avg_rss_mb']:.1f}MB (Peak: {stats['peak_rss_mb']:.1f}MB)")
        
    def test_ai_client_initialization_memory(self, ai_client):
        """Test memory usage during AI client initialization."""
        with memory_profiling() as profiler:
            # Client already initialized, test availability check
            is_available = ai_client.is_available()
            time.sleep(1.0)
            
        stats = profiler.get_memory_stats()
        peak_rss, peak_vms = profiler.get_peak_memory()
        
        # Validate memory constraints
        assert peak_rss < self.MEMORY_TARGET_MB, \
            f"Peak RSS {peak_rss:.1f}MB exceeds target {self.MEMORY_TARGET_MB}MB"
            
        if peak_rss > self.MEMORY_WARNING_MB:
            pytest.warns(UserWarning, 
                f"Memory usage {peak_rss:.1f}MB exceeds warning threshold {self.MEMORY_WARNING_MB}MB")
            
        print(f"AI Client Init Memory: {stats['avg_rss_mb']:.1f}MB (Peak: {peak_rss:.1f}MB)")
        
    @pytest.mark.skipif(not LocalAIClient().is_available(), 
                       reason="Local AI model not available")
    def test_terraform_generation_memory(self, ai_client):
        """Test memory usage during Terraform code generation."""
        test_description = "Create a simple Ubuntu VM with 2GB RAM and 20GB disk"
        
        with memory_profiling() as profiler:
            response = ai_client.generate_terraform_config(
                description=test_description,
                skill_level="intermediate"
            )
            
        stats = profiler.get_memory_stats()
        peak_rss, peak_vms = profiler.get_peak_memory()
        
        # Validate generation worked
        assert response.success, f"Terraform generation failed: {response.content}"
        assert len(response.content) > 0, "Should generate non-empty content"
        
        # Validate memory constraints
        assert peak_rss < self.MEMORY_TARGET_MB, \
            f"Peak RSS {peak_rss:.1f}MB exceeds target {self.MEMORY_TARGET_MB}MB"
            
        # Check for memory leaks (growth should be reasonable)
        assert stats['memory_growth_mb'] < 500, \
            f"Memory growth {stats['memory_growth_mb']:.1f}MB suggests possible leak"
        
        print(f"Terraform Generation Memory: {stats['avg_rss_mb']:.1f}MB "
              f"(Peak: {peak_rss:.1f}MB, Growth: {stats['memory_growth_mb']:.1f}MB)")
        
    @pytest.mark.skipif(not LocalAIClient().is_available(), 
                       reason="Local AI model not available")
    def test_ansible_generation_memory(self, ai_client):
        """Test memory usage during Ansible playbook generation."""  
        test_description = "Configure nginx web server with SSL and firewall"
        
        with memory_profiling() as profiler:
            response = ai_client.generate_ansible_playbook(
                description=test_description,
                skill_level="intermediate"
            )
            
        stats = profiler.get_memory_stats()
        peak_rss, peak_vms = profiler.get_peak_memory()
        
        # Validate generation worked
        assert response.success, f"Ansible generation failed: {response.content}"
        assert len(response.content) > 0, "Should generate non-empty content"
        
        # Validate memory constraints
        assert peak_rss < self.MEMORY_TARGET_MB, \
            f"Peak RSS {peak_rss:.1f}MB exceeds target {self.MEMORY_TARGET_MB}MB"
            
        print(f"Ansible Generation Memory: {stats['avg_rss_mb']:.1f}MB "
              f"(Peak: {peak_rss:.1f}MB)")
        
    @pytest.mark.skipif(not LocalAIClient().is_available(), 
                       reason="Local AI model not available")
    def test_multiple_requests_memory_stability(self, ai_client):
        """Test memory stability across multiple AI requests."""
        requests = [
            ("Create a PostgreSQL database server", "beginner"),
            ("Setup Docker container orchestration", "intermediate"), 
            ("Configure Kubernetes cluster with HA", "expert"),
            ("Deploy monitoring stack with Prometheus", "intermediate"),
            ("Setup backup automation system", "beginner")
        ]
        
        memory_snapshots = []
        
        with memory_profiling() as profiler:
            for description, skill_level in requests:
                start_memory = profiler.process.memory_info().rss / 1024 / 1024
                
                response = ai_client.generate_terraform_config(
                    description=description,
                    skill_level=skill_level
                )
                
                end_memory = profiler.process.memory_info().rss / 1024 / 1024
                memory_snapshots.append((start_memory, end_memory, end_memory - start_memory))
                
                # Validate each generation worked
                assert response.success, f"Generation failed for: {description}"
                
                # Small delay between requests
                time.sleep(0.5)
                
        stats = profiler.get_memory_stats()
        peak_rss, peak_vms = profiler.get_peak_memory()
        
        # Validate overall memory constraints
        assert peak_rss < self.MEMORY_TARGET_MB, \
            f"Peak RSS {peak_rss:.1f}MB exceeds target {self.MEMORY_TARGET_MB}MB"
            
        # Check for memory leaks across requests
        total_growth = sum(growth for _, _, growth in memory_snapshots)
        avg_growth_per_request = total_growth / len(requests)
        
        assert avg_growth_per_request < 100, \
            f"Average memory growth per request {avg_growth_per_request:.1f}MB too high"
            
        # Final memory should not be significantly higher than initial
        final_memory = memory_snapshots[-1][1]
        initial_memory = memory_snapshots[0][0]
        total_session_growth = final_memory - initial_memory
        
        assert total_session_growth < 200, \
            f"Total session memory growth {total_session_growth:.1f}MB suggests memory leak"
        
        print(f"Multiple Requests Memory Stability:")
        print(f"  Peak: {peak_rss:.1f}MB, Average: {stats['avg_rss_mb']:.1f}MB")
        print(f"  Total Growth: {total_session_growth:.1f}MB")
        print(f"  Average per Request: {avg_growth_per_request:.1f}MB")
        
    def test_skill_level_memory_comparison(self, ai_client):
        """Compare memory usage across different skill levels."""
        if not ai_client.is_available():
            pytest.skip("Local AI model not available")
            
        description = "Deploy web application with database backend"
        skill_levels = ["beginner", "intermediate", "expert"]
        memory_results = {}
        
        for skill_level in skill_levels:
            with memory_profiling() as profiler:
                response = ai_client.generate_terraform_config(
                    description=description,
                    skill_level=skill_level
                )
                
            stats = profiler.get_memory_stats()
            memory_results[skill_level] = {
                'peak_rss': stats['peak_rss_mb'],
                'avg_rss': stats['avg_rss_mb'],
                'response_length': len(response.content),
                'processing_time': response.processing_time
            }
            
            # Validate each response
            assert response.success, f"Generation failed for skill level: {skill_level}"
            
        # Analyze memory usage patterns
        for skill_level, results in memory_results.items():
            assert results['peak_rss'] < self.MEMORY_TARGET_MB, \
                f"Skill level {skill_level} peak RSS {results['peak_rss']:.1f}MB exceeds target"
            
        print("Skill Level Memory Comparison:")
        for skill_level, results in memory_results.items():
            print(f"  {skill_level}: Peak={results['peak_rss']:.1f}MB, "
                  f"Avg={results['avg_rss']:.1f}MB, "
                  f"Time={results['processing_time']:.1f}s")
                  
    def test_memory_optimization_recommendations(self, ai_client):
        """Test memory usage during infrastructure optimization requests."""
        if not ai_client.is_available():
            pytest.skip("Local AI model not available")
            
        sample_config = """
        resource "proxmox_vm_qemu" "web_server" {
          name = "webserver"
          memory = 1024
          cores = 1
          disk {
            size = "10G"
            type = "virtio"
          }
        }
        """
        
        with memory_profiling() as profiler:
            response = ai_client.optimize_infrastructure(
                config=sample_config,
                skill_level="expert"
            )
            
        stats = profiler.get_memory_stats()
        peak_rss, peak_vms = profiler.get_peak_memory()
        
        # Validate optimization worked
        assert response.success, f"Optimization failed: {response.content}"
        assert len(response.content) > 0, "Should generate optimization recommendations"
        
        # Validate memory constraints
        assert peak_rss < self.MEMORY_TARGET_MB, \
            f"Peak RSS {peak_rss:.1f}MB exceeds target {self.MEMORY_TARGET_MB}MB"
            
        print(f"Optimization Memory: {stats['avg_rss_mb']:.1f}MB (Peak: {peak_rss:.1f}MB)")
        
    def test_concurrent_requests_memory_pressure(self, ai_client):
        """Test memory usage under concurrent AI request pressure."""
        if not ai_client.is_available():
            pytest.skip("Local AI model not available")
            
        import concurrent.futures
        import threading
        
        def generate_config(description: str, skill_level: str) -> bool:
            """Generate configuration and return success status."""
            try:
                response = ai_client.generate_terraform_config(description, skill_level)
                return response.success
            except Exception:
                return False
                
        requests = [
            ("Create load balancer", "intermediate"),
            ("Setup monitoring", "beginner"),
            ("Configure database cluster", "expert"),
            ("Deploy microservices", "intermediate")
        ]
        
        with memory_profiling() as profiler:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(generate_config, desc, skill)
                    for desc, skill in requests
                ]
                
                # Wait for all to complete
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
                
        stats = profiler.get_memory_stats()
        peak_rss, peak_vms = profiler.get_peak_memory()
        
        # Validate all requests succeeded
        assert all(results), "All concurrent requests should succeed"
        
        # Validate memory under pressure
        assert peak_rss < self.MEMORY_CRITICAL_MB, \
            f"Peak RSS under pressure {peak_rss:.1f}MB exceeds critical threshold"
            
        print(f"Concurrent Requests Memory: {stats['avg_rss_mb']:.1f}MB "
              f"(Peak: {peak_rss:.1f}MB)")


def test_system_memory_requirements():
    """Test overall system memory requirements and availability."""
    system_memory = psutil.virtual_memory()
    available_mb = system_memory.available / 1024 / 1024
    total_mb = system_memory.total / 1024 / 1024
    
    # Ensure system has sufficient memory for local AI operations
    assert available_mb > TestMemoryProfiling.MEMORY_TARGET_MB, \
        f"System available memory {available_mb:.1f}MB insufficient for target {TestMemoryProfiling.MEMORY_TARGET_MB}MB"
        
    # Recommend minimum system memory
    recommended_memory_mb = TestMemoryProfiling.MEMORY_TARGET_MB * 1.5  # 50% overhead
    if total_mb < recommended_memory_mb:
        pytest.warns(UserWarning, 
            f"System memory {total_mb:.1f}MB below recommended {recommended_memory_mb:.1f}MB")
    
    print(f"System Memory: {total_mb:.1f}MB total, {available_mb:.1f}MB available")


if __name__ == "__main__":
    # Run memory profiling tests directly
    pytest.main([__file__, "-v", "--tb=short"])