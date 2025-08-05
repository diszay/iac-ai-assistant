"""
Comprehensive Metrics and Telemetry System.

This module provides enterprise-grade metrics collection, telemetry, monitoring,
and analytics capabilities optimized for Intel N150 hardware while maintaining
comprehensive observability and performance insights.
"""

import asyncio
import json
import time
import threading
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from enum import Enum
from pathlib import Path
import statistics
import weakref

import structlog

# Optional Prometheus client for advanced metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    from prometheus_client.core import REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Optional APM and monitoring libraries
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .hardware_detector import hardware_detector
from .performance_monitor import PerformanceMonitor

logger = structlog.get_logger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"       # Monotonically increasing
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    SUMMARY = "summary"      # Similar to histogram but with percentiles
    TIMER = "timer"          # Time-based measurements


class MetricUnit(Enum):
    """Units for metrics."""
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    GIGABYTES = "gigabytes"
    PERCENT = "percent"
    COUNT = "count"
    RATE = "rate"
    REQUESTS_PER_SECOND = "requests_per_second"


@dataclass
class MetricPoint:
    """A single metric data point."""
    
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    unit: MetricUnit = MetricUnit.COUNT
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """A series of metric points."""
    
    name: str
    metric_type: MetricType
    unit: MetricUnit
    description: str
    points: deque = field(default_factory=lambda: deque(maxlen=1000))  # Keep last 1000 points
    tags: Dict[str, str] = field(default_factory=dict)
    
    def add_point(self, value: float, timestamp: Optional[float] = None, tags: Optional[Dict[str, str]] = None):
        """Add a point to the series."""
        point = MetricPoint(
            name=self.name,
            value=value,
            timestamp=timestamp or time.time(),
            tags={**self.tags, **(tags or {})},
            unit=self.unit
        )
        self.points.append(point)
    
    def get_latest_value(self) -> Optional[float]:
        """Get the latest value."""
        return self.points[-1].value if self.points else None
    
    def get_average(self, window_seconds: Optional[float] = None) -> Optional[float]:
        """Get average value over time window."""
        if not self.points:
            return None
        
        if window_seconds is None:
            values = [p.value for p in self.points]
        else:
            cutoff_time = time.time() - window_seconds
            values = [p.value for p in self.points if p.timestamp >= cutoff_time]
        
        return statistics.mean(values) if values else None
    
    def get_percentile(self, percentile: float, window_seconds: Optional[float] = None) -> Optional[float]:
        """Get percentile value over time window."""
        if not self.points:
            return None
        
        if window_seconds is None:
            values = [p.value for p in self.points]
        else:
            cutoff_time = time.time() - window_seconds
            values = [p.value for p in self.points if p.timestamp >= cutoff_time]
        
        if not values:
            return None
        
        return statistics.quantiles(values, n=100)[int(percentile) - 1] if len(values) > 1 else values[0]


class SystemMetricsCollector:
    """Collects system-level metrics."""
    
    def __init__(self):
        self.enabled = PSUTIL_AVAILABLE
        self.collection_interval = 10  # seconds
        self.running = False
        self._task = None
        
    async def start_collection(self):
        """Start collecting system metrics."""
        if not self.enabled:
            logger.warning("System metrics collection disabled - psutil not available")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._collection_loop())
        logger.info("System metrics collection started")
    
    async def stop_collection(self):
        """Stop collecting system metrics."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("System metrics collection stopped")
    
    async def _collection_loop(self):
        """Main collection loop."""
        metrics_registry = get_metrics_registry()
        
        while self.running:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                metrics_registry.record_gauge("system.cpu.utilization", cpu_percent, unit=MetricUnit.PERCENT)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                metrics_registry.record_gauge("system.memory.utilization", memory.percent, unit=MetricUnit.PERCENT)
                metrics_registry.record_gauge("system.memory.available", memory.available / (1024**3), unit=MetricUnit.GIGABYTES)
                metrics_registry.record_gauge("system.memory.used", memory.used / (1024**3), unit=MetricUnit.GIGABYTES)
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                metrics_registry.record_gauge("system.disk.utilization", (disk.used / disk.total) * 100, unit=MetricUnit.PERCENT)
                metrics_registry.record_gauge("system.disk.free", disk.free / (1024**3), unit=MetricUnit.GIGABYTES)
                
                # Network metrics (if available)
                try:
                    net_io = psutil.net_io_counters()
                    metrics_registry.record_counter("system.network.bytes_sent", net_io.bytes_sent, unit=MetricUnit.BYTES)
                    metrics_registry.record_counter("system.network.bytes_recv", net_io.bytes_recv, unit=MetricUnit.BYTES)
                except:
                    pass  # Network metrics might not be available
                
                # Load average (Linux/Unix only)
                try:
                    load_avg = psutil.getloadavg()
                    metrics_registry.record_gauge("system.load.avg_1min", load_avg[0])
                    metrics_registry.record_gauge("system.load.avg_5min", load_avg[1])
                    metrics_registry.record_gauge("system.load.avg_15min", load_avg[2])
                except:
                    pass  # Load average might not be available on all systems
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("System metrics collection error", error=str(e))
                await asyncio.sleep(self.collection_interval)


class ApplicationMetricsCollector:
    """Collects application-specific metrics."""
    
    def __init__(self):
        self.metrics_registry = None
        self.performance_monitor = PerformanceMonitor()
        
    def set_registry(self, registry):
        """Set the metrics registry."""
        self.metrics_registry = registry
    
    def record_ai_request(self, model_name: str, processing_time: float, success: bool):
        """Record AI request metrics."""
        if not self.metrics_registry:
            return
        
        tags = {"model": model_name, "success": str(success)}
        
        self.metrics_registry.record_counter("ai.requests.total", 1, tags=tags)
        self.metrics_registry.record_histogram("ai.request.duration", processing_time, tags=tags, unit=MetricUnit.SECONDS)
        
        if not success:
            self.metrics_registry.record_counter("ai.requests.errors", 1, tags=tags)
    
    def record_code_generation(self, code_type: str, lines_generated: int, generation_time: float):
        """Record code generation metrics."""
        if not self.metrics_registry:
            return
        
        tags = {"code_type": code_type}
        
        self.metrics_registry.record_counter("code_generation.requests", 1, tags=tags)
        self.metrics_registry.record_gauge("code_generation.lines_generated", lines_generated, tags=tags)
        self.metrics_registry.record_histogram("code_generation.duration", generation_time, tags=tags, unit=MetricUnit.SECONDS)
    
    def record_security_scan(self, scan_type: str, vulnerabilities_found: int, scan_duration: float):
        """Record security scan metrics."""
        if not self.metrics_registry:
            return
        
        tags = {"scan_type": scan_type}
        
        self.metrics_registry.record_counter("security.scans.total", 1, tags=tags)
        self.metrics_registry.record_gauge("security.vulnerabilities.found", vulnerabilities_found, tags=tags)
        self.metrics_registry.record_histogram("security.scan.duration", scan_duration, tags=tags, unit=MetricUnit.SECONDS)
    
    def record_cache_operation(self, operation: str, cache_level: str, hit: bool, latency: float):
        """Record cache operation metrics."""
        if not self.metrics_registry:
            return
        
        tags = {"operation": operation, "cache_level": cache_level, "hit": str(hit)}
        
        self.metrics_registry.record_counter("cache.operations.total", 1, tags=tags)
        self.metrics_registry.record_histogram("cache.operation.latency", latency, tags=tags, unit=MetricUnit.MILLISECONDS)
        
        if hit:
            self.metrics_registry.record_counter("cache.hits", 1, tags={"cache_level": cache_level})
        else:
            self.metrics_registry.record_counter("cache.misses", 1, tags={"cache_level": cache_level})
    
    def record_infrastructure_operation(self, operation: str, resource_type: str, success: bool, duration: float):
        """Record infrastructure operation metrics."""
        if not self.metrics_registry:
            return
        
        tags = {"operation": operation, "resource_type": resource_type, "success": str(success)}
        
        self.metrics_registry.record_counter("infrastructure.operations.total", 1, tags=tags)
        self.metrics_registry.record_histogram("infrastructure.operation.duration", duration, tags=tags, unit=MetricUnit.SECONDS)
        
        if not success:
            self.metrics_registry.record_counter("infrastructure.operations.errors", 1, tags=tags)


class PrometheusExporter:
    """Exports metrics in Prometheus format."""
    
    def __init__(self):
        self.enabled = PROMETHEUS_AVAILABLE
        self.registry = CollectorRegistry() if self.enabled else None
        self.metrics = {}
        
        if self.enabled:
            logger.info("Prometheus exporter initialized")
        else:
            logger.warning("Prometheus exporter disabled - prometheus_client not available")
    
    def create_counter(self, name: str, description: str, labels: Optional[List[str]] = None):
        """Create a Prometheus counter."""
        if not self.enabled:
            return None
        
        counter = Counter(name, description, labelnames=labels or [], registry=self.registry)
        self.metrics[name] = counter
        return counter
    
    def create_gauge(self, name: str, description: str, labels: Optional[List[str]] = None):
        """Create a Prometheus gauge."""
        if not self.enabled:
            return None
        
        gauge = Gauge(name, description, labelnames=labels or [], registry=self.registry)
        self.metrics[name] = gauge
        return gauge
    
    def create_histogram(self, name: str, description: str, labels: Optional[List[str]] = None, buckets: Optional[List[float]] = None):
        """Create a Prometheus histogram."""
        if not self.enabled:
            return None
        
        histogram = Histogram(name, description, labelnames=labels or [], buckets=buckets, registry=self.registry)
        self.metrics[name] = histogram
        return histogram
    
    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format."""
        if not self.enabled:
            return ""
        
        return generate_latest(self.registry).decode('utf-8')
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, tags: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        if not self.enabled or name not in self.metrics:
            return
        
        metric = self.metrics[name]
        labels = tags or {}
        
        if metric_type == MetricType.COUNTER:
            if labels:
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)
        elif metric_type == MetricType.GAUGE:
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
        elif metric_type == MetricType.HISTOGRAM:
            if labels:
                metric.labels(**labels).observe(value)
            else:
                metric.observe(value)


class MetricsRegistry:
    """Central registry for all metrics."""
    
    def __init__(self):
        self.series: Dict[str, MetricSeries] = {}
        self.collectors = []
        self.exporters = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance optimization for Intel N150
        self.batch_size = 100  # Batch metric operations
        self.flush_interval = 30  # seconds
        self._pending_operations = []
        self._last_flush = time.time()
        
        # Initialize exporters
        if PROMETHEUS_AVAILABLE:
            prometheus_exporter = PrometheusExporter()
            self.exporters.append(prometheus_exporter)
        
        logger.info("Metrics registry initialized")
    
    def register_series(self, 
                       name: str, 
                       metric_type: MetricType,
                       description: str,
                       unit: MetricUnit = MetricUnit.COUNT,
                       tags: Optional[Dict[str, str]] = None) -> MetricSeries:
        """Register a new metric series."""
        
        with self._lock:
            if name in self.series:
                return self.series[name]
            
            series = MetricSeries(
                name=name,
                metric_type=metric_type,
                unit=unit,
                description=description,
                tags=tags or {}
            )
            
            self.series[name] = series
            
            # Create corresponding Prometheus metrics
            for exporter in self.exporters:
                if isinstance(exporter, PrometheusExporter):
                    label_names = list(tags.keys()) if tags else []
                    
                    if metric_type == MetricType.COUNTER:
                        exporter.create_counter(name, description, label_names)
                    elif metric_type == MetricType.GAUGE:
                        exporter.create_gauge(name, description, label_names)
                    elif metric_type == MetricType.HISTOGRAM:
                        exporter.create_histogram(name, description, label_names)
            
            logger.debug(f"Registered metric series: {name}")
            return series
    
    def record_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None, unit: MetricUnit = MetricUnit.COUNT):
        """Record a counter metric."""
        self._record_metric(name, value, MetricType.COUNTER, tags, unit)
    
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, unit: MetricUnit = MetricUnit.COUNT):
        """Record a gauge metric."""
        self._record_metric(name, value, MetricType.GAUGE, tags, unit)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None, unit: MetricUnit = MetricUnit.COUNT):
        """Record a histogram metric."""
        self._record_metric(name, value, MetricType.HISTOGRAM, tags, unit)
    
    def _record_metric(self, name: str, value: float, metric_type: MetricType, tags: Optional[Dict[str, str]], unit: MetricUnit):
        """Internal method to record a metric."""
        
        # Batch operations for performance
        operation = {
            'name': name,
            'value': value,
            'metric_type': metric_type,
            'tags': tags,
            'unit': unit,
            'timestamp': time.time()
        }
        
        self._pending_operations.append(operation)
        
        # Flush if batch is full or time threshold reached
        if (len(self._pending_operations) >= self.batch_size or 
            time.time() - self._last_flush > self.flush_interval):
            self._flush_operations()
    
    def _flush_operations(self):
        """Flush pending metric operations."""
        if not self._pending_operations:
            return
        
        with self._lock:
            for op in self._pending_operations:
                try:
                    # Ensure series exists
                    if op['name'] not in self.series:
                        self.register_series(
                            op['name'], 
                            op['metric_type'], 
                            f"Auto-generated metric: {op['name']}",
                            op['unit'],
                            op['tags']
                        )
                    
                    # Add point to series
                    series = self.series[op['name']]
                    series.add_point(op['value'], op['timestamp'], op['tags'])
                    
                    # Export to external systems
                    for exporter in self.exporters:
                        if isinstance(exporter, PrometheusExporter):
                            exporter.record_metric(op['name'], op['value'], op['metric_type'], op['tags'])
                
                except Exception as e:
                    logger.error(f"Failed to process metric operation", operation=op, error=str(e))
            
            self._pending_operations.clear()
            self._last_flush = time.time()
    
    def get_series(self, name: str) -> Optional[MetricSeries]:
        """Get a metric series by name."""
        return self.series.get(name)
    
    def get_all_series(self) -> Dict[str, MetricSeries]:
        """Get all metric series."""
        with self._lock:
            return self.series.copy()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        self._flush_operations()  # Ensure all operations are processed
        
        summary = {
            'total_series': len(self.series),
            'metrics_by_type': defaultdict(int),
            'latest_values': {},
            'collection_timestamp': time.time()
        }
        
        with self._lock:
            for name, series in self.series.items():
                summary['metrics_by_type'][series.metric_type.value] += 1
                
                latest_value = series.get_latest_value()
                if latest_value is not None:
                    summary['latest_values'][name] = {
                        'value': latest_value,
                        'unit': series.unit.value,
                        'description': series.description
                    }
        
        return summary
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        self._flush_operations()
        
        for exporter in self.exporters:
            if isinstance(exporter, PrometheusExporter):
                return exporter.get_metrics_text()
        
        return ""
    
    def clear_all_metrics(self):
        """Clear all metrics (useful for testing)."""
        with self._lock:
            self.series.clear()
            self._pending_operations.clear()
            logger.info("All metrics cleared")


class MetricsManager:
    """Main metrics management system."""
    
    def __init__(self):
        self.registry = MetricsRegistry()
        self.system_collector = SystemMetricsCollector()
        self.app_collector = ApplicationMetricsCollector()
        
        # Set up collectors
        self.app_collector.set_registry(self.registry)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize standard metrics
        self._initialize_standard_metrics()
        
        logger.info("Metrics manager initialized")
    
    def _initialize_standard_metrics(self):
        """Initialize standard application metrics."""
        
        # Application metrics
        self.registry.register_series("app.startup.duration", MetricType.HISTOGRAM, "Application startup time", MetricUnit.SECONDS)
        self.registry.register_series("app.requests.total", MetricType.COUNTER, "Total application requests")
        self.registry.register_series("app.errors.total", MetricType.COUNTER, "Total application errors")
        
        # AI metrics
        self.registry.register_series("ai.requests.total", MetricType.COUNTER, "Total AI requests")
        self.registry.register_series("ai.request.duration", MetricType.HISTOGRAM, "AI request duration", MetricUnit.SECONDS)
        self.registry.register_series("ai.model_load.duration", MetricType.HISTOGRAM, "AI model load time", MetricUnit.SECONDS)
        
        # Infrastructure metrics
        self.registry.register_series("infrastructure.operations.total", MetricType.COUNTER, "Total infrastructure operations")
        self.registry.register_series("infrastructure.operation.duration", MetricType.HISTOGRAM, "Infrastructure operation duration", MetricUnit.SECONDS)
        
        # Cache metrics
        self.registry.register_series("cache.hits", MetricType.COUNTER, "Cache hits")
        self.registry.register_series("cache.misses", MetricType.COUNTER, "Cache misses")
        self.registry.register_series("cache.operation.latency", MetricType.HISTOGRAM, "Cache operation latency", MetricUnit.MILLISECONDS)
        
        # Security metrics
        self.registry.register_series("security.scans.total", MetricType.COUNTER, "Total security scans")
        self.registry.register_series("security.vulnerabilities.found", MetricType.GAUGE, "Vulnerabilities found")
        
        logger.debug("Standard metrics initialized")
    
    async def start(self):
        """Start metrics collection."""
        await self.system_collector.start_collection()
        logger.info("Metrics collection started")
    
    async def stop(self):
        """Stop metrics collection."""
        await self.system_collector.stop_collection()
        # Flush any pending operations
        self.registry._flush_operations()
        logger.info("Metrics collection stopped")
    
    def get_registry(self) -> MetricsRegistry:
        """Get the metrics registry."""
        return self.registry
    
    def get_app_collector(self) -> ApplicationMetricsCollector:
        """Get the application metrics collector."""
        return self.app_collector
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status based on metrics."""
        summary = self.registry.get_metrics_summary()
        
        # Simple health checks based on metrics
        health_status = {
            'status': 'healthy',
            'checks': {},
            'metrics_summary': summary,
            'timestamp': time.time()
        }
        
        # Check system metrics if available
        try:
            cpu_series = self.registry.get_series('system.cpu.utilization')
            if cpu_series:
                cpu_usage = cpu_series.get_latest_value()
                if cpu_usage and cpu_usage > 90:
                    health_status['status'] = 'warning'
                    health_status['checks']['cpu'] = f'High CPU usage: {cpu_usage:.1f}%'
                else:
                    health_status['checks']['cpu'] = 'OK'
            
            memory_series = self.registry.get_series('system.memory.utilization')
            if memory_series:
                memory_usage = memory_series.get_latest_value()
                if memory_usage and memory_usage > 95:
                    health_status['status'] = 'critical'
                    health_status['checks']['memory'] = f'Critical memory usage: {memory_usage:.1f}%'
                elif memory_usage and memory_usage > 85:
                    health_status['status'] = 'warning'
                    health_status['checks']['memory'] = f'High memory usage: {memory_usage:.1f}%'
                else:
                    health_status['checks']['memory'] = 'OK'
            
        except Exception as e:
            logger.warning("Health check failed", error=str(e))
            health_status['checks']['health_check'] = f'Error: {str(e)}'
        
        return health_status


# Global metrics manager instance
metrics_manager = None

def get_metrics_manager() -> MetricsManager:
    """Get global metrics manager instance."""
    global metrics_manager
    
    if metrics_manager is None:
        metrics_manager = MetricsManager()
    
    return metrics_manager


def get_metrics_registry() -> MetricsRegistry:
    """Get global metrics registry instance."""
    return get_metrics_manager().get_registry()


def get_app_metrics_collector() -> ApplicationMetricsCollector:
    """Get global application metrics collector."""
    return get_metrics_manager().get_app_collector()


# Decorator for timing function execution
def timed_metric(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Decorator for automatically timing function execution."""
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                registry = get_metrics_registry()
                registry.record_histogram(metric_name, duration, tags, MetricUnit.SECONDS)
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                registry = get_metrics_registry()
                error_tags = {**(tags or {}), 'error': 'true'}
                registry.record_histogram(metric_name, duration, error_tags, MetricUnit.SECONDS)
                raise
        
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Export main classes and functions
__all__ = [
    'MetricsManager',
    'MetricsRegistry',
    'MetricSeries',
    'MetricPoint',
    'MetricType',
    'MetricUnit',
    'SystemMetricsCollector',
    'ApplicationMetricsCollector',
    'PrometheusExporter',
    'get_metrics_manager',
    'get_metrics_registry',
    'get_app_metrics_collector',
    'timed_metric'
]