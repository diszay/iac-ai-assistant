"""
Enterprise-Grade Caching and Performance Optimization System.

This module provides advanced caching mechanisms, performance optimization,
and scalable data management optimized for Intel N150 hardware constraints
while maintaining enterprise-level functionality.
"""

import asyncio
import json
import time
import threading
import hashlib
import pickle
import zlib
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict
from enum import Enum
from pathlib import Path
import weakref
import gc

import structlog

# Optional Redis support for distributed caching
try:
    import redis
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Optional compression libraries
try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

from .hardware_detector import hardware_detector
from .performance_monitor import PerformanceMonitor

logger = structlog.get_logger(__name__)


class CacheLevel(Enum):
    """Cache levels for hierarchical caching."""
    L1_MEMORY = "l1_memory"      # In-memory cache (fastest)
    L2_COMPRESSED = "l2_compressed"  # Compressed memory cache
    L3_DISK = "l3_disk"          # Disk-based cache
    L4_DISTRIBUTED = "l4_distributed"  # Distributed cache (Redis)


class EvictionPolicy(Enum):
    """Cache eviction policies."""
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used
    TTL = "ttl"              # Time To Live
    SIZE_BASED = "size_based"  # Size-based eviction
    ADAPTIVE = "adaptive"     # Adaptive policy based on usage patterns


@dataclass
class CacheStats:
    """Statistics for cache performance monitoring."""
    
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    storage_bytes: int = 0
    compression_ratio: float = 1.0
    avg_access_time_ms: float = 0.0
    
    # Advanced metrics
    hit_rate_by_type: Dict[str, float] = field(default_factory=dict)
    memory_efficiency: float = 0.0
    compression_savings_bytes: int = 0
    cache_warming_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate overall hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def memory_usage_mb(self) -> float:
        """Calculate memory usage in MB."""
        return self.storage_bytes / (1024 * 1024)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0
    compressed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)
    
    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return time.time() - self.created_at


class AdvancedMemoryCache:
    """Advanced in-memory cache with intelligent eviction and compression."""
    
    def __init__(self, 
                 max_size_mb: float = 100,
                 max_entries: int = 1000,
                 eviction_policy: EvictionPolicy = EvictionPolicy.ADAPTIVE,
                 compression_threshold_bytes: int = 1024,
                 enable_compression: bool = True):
        
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.max_entries = max_entries
        self.eviction_policy = eviction_policy
        self.compression_threshold = compression_threshold_bytes
        self.enable_compression = enable_compression and (LZ4_AVAILABLE or True)
        
        # Storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._access_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = defaultdict(int)
        
        # Statistics
        self.stats = CacheStats()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance optimization
        self._size_tracker = 0
        self._cleanup_interval = 60  # seconds
        self._last_cleanup = time.time()
        
        logger.info(
            "Advanced memory cache initialized",
            max_size_mb=max_size_mb,
            max_entries=max_entries,
            eviction_policy=eviction_policy.value,
            compression_enabled=self.enable_compression
        )
    
    def _calculate_entry_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes."""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float)):
                return 8  # Approximate
            else:
                # Use pickle for complex objects
                return len(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))
        except Exception:
            return 100  # Default fallback
    
    def _compress_value(self, value: Any) -> Tuple[Any, bool]:
        """Compress value if beneficial."""
        if not self.enable_compression:
            return value, False
        
        try:
            # Serialize value
            serialized = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Compress if above threshold
            if len(serialized) >= self.compression_threshold:
                if LZ4_AVAILABLE:
                    compressed = lz4.frame.compress(serialized)
                else:
                    compressed = zlib.compress(serialized, level=6)
                
                # Only use compression if it actually saves space
                if len(compressed) < len(serialized) * 0.9:  # At least 10% savings
                    self.stats.compression_savings_bytes += len(serialized) - len(compressed)
                    return compressed, True
            
            return serialized, False
            
        except Exception as e:
            logger.warning("Compression failed", error=str(e))
            return value, False
    
    def _decompress_value(self, value: Any, compressed: bool) -> Any:
        """Decompress value if needed."""
        if not compressed:
            if isinstance(value, bytes):
                try:
                    return pickle.loads(value)
                except:
                    return value
            return value
        
        try:
            if LZ4_AVAILABLE:
                decompressed = lz4.frame.decompress(value)
            else:
                decompressed = zlib.decompress(value)
            
            return pickle.loads(decompressed)
            
        except Exception as e:
            logger.error("Decompression failed", error=str(e))
            return value
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        start_time = time.time()
        
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self.stats.misses += 1
                return None
            
            # Check expiration
            if entry.is_expired:
                self._remove_entry(key)
                self.stats.misses += 1
                return None
            
            # Update access statistics
            entry.last_accessed = time.time()
            entry.access_count += 1
            self._access_times[key] = entry.last_accessed
            self._access_counts[key] += 1
            
            # Move to end for LRU
            if self.eviction_policy == EvictionPolicy.LRU:
                self._cache.move_to_end(key)
            
            self.stats.hits += 1
            
            # Update average access time
            access_time_ms = (time.time() - start_time) * 1000
            self.stats.avg_access_time_ms = (
                (self.stats.avg_access_time_ms * (self.stats.hits - 1) + access_time_ms) / 
                self.stats.hits
            )
            
            # Decompress if needed
            value = self._decompress_value(entry.value, entry.compressed)
            
            return value
    
    async def set(self, 
                 key: str, 
                 value: Any, 
                 ttl: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set value in cache."""
        
        with self._lock:
            # Remove existing entry if present
            if key in self._cache:
                self._remove_entry(key)
            
            # Compress value
            compressed_value, is_compressed = self._compress_value(value)
            
            # Calculate size
            size_bytes = self._calculate_entry_size(compressed_value)
            
            # Check if we need to evict entries
            await self._ensure_space(size_bytes)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=compressed_value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl,
                size_bytes=size_bytes,
                compressed=is_compressed,
                metadata=metadata or {}
            )
            
            # Store entry
            self._cache[key] = entry
            self._access_times[key] = entry.last_accessed
            self._size_tracker += size_bytes
            
            # Update statistics
            self.stats.storage_bytes = self._size_tracker
            if is_compressed:
                original_size = self._calculate_entry_size(value)
                self.stats.compression_ratio = size_bytes / original_size
            
            return True
    
    async def _ensure_space(self, required_bytes: int):
        """Ensure there's enough space by evicting entries if necessary."""
        
        # Check size limit
        while (self._size_tracker + required_bytes > self.max_size_bytes or 
               len(self._cache) >= self.max_entries):
            
            if not self._cache:
                break
            
            evict_key = self._select_eviction_candidate()
            if evict_key:
                self._remove_entry(evict_key)
                self.stats.evictions += 1
            else:
                break
    
    def _select_eviction_candidate(self) -> Optional[str]:
        """Select entry for eviction based on policy."""
        
        if not self._cache:
            return None
        
        if self.eviction_policy == EvictionPolicy.LRU:
            # First item is least recently used
            return next(iter(self._cache))
        
        elif self.eviction_policy == EvictionPolicy.LFU:
            # Find least frequently used
            min_count = float('inf')
            lfu_key = None
            for key, entry in self._cache.items():
                if entry.access_count < min_count:
                    min_count = entry.access_count
                    lfu_key = key
            return lfu_key
        
        elif self.eviction_policy == EvictionPolicy.TTL:
            # Find expired or oldest entry
            oldest_key = None
            oldest_time = float('inf')
            for key, entry in self._cache.items():
                if entry.is_expired:
                    return key
                if entry.created_at < oldest_time:
                    oldest_time = entry.created_at
                    oldest_key = key
            return oldest_key
        
        elif self.eviction_policy == EvictionPolicy.SIZE_BASED:
            # Find largest entry
            max_size = 0
            largest_key = None
            for key, entry in self._cache.items():
                if entry.size_bytes > max_size:
                    max_size = entry.size_bytes
                    largest_key = key
            return largest_key
        
        elif self.eviction_policy == EvictionPolicy.ADAPTIVE:
            # Adaptive policy considering access patterns and size
            best_score = float('inf')
            best_key = None
            
            current_time = time.time()
            
            for key, entry in self._cache.items():
                # Score based on: recency, frequency, size, and age
                recency_score = current_time - entry.last_accessed
                frequency_score = 1.0 / max(1, entry.access_count)
                size_score = entry.size_bytes / 1024  # Normalize to KB
                age_score = entry.age_seconds / 3600  # Normalize to hours
                
                total_score = recency_score + frequency_score + size_score * 0.1 + age_score * 0.1
                
                if total_score < best_score:
                    best_score = total_score
                    best_key = key
            
            return best_key
        
        # Default: LRU
        return next(iter(self._cache))
    
    def _remove_entry(self, key: str):
        """Remove entry from cache."""
        entry = self._cache.pop(key, None)
        if entry:
            self._size_tracker -= entry.size_bytes
            self._access_times.pop(key, None)
            self._access_counts.pop(key, None)
    
    async def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                return True
            return False
    
    async def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._access_counts.clear()
            self._size_tracker = 0
            self.stats = CacheStats()
    
    async def keys(self) -> List[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())
    
    async def cleanup_expired(self):
        """Remove expired entries."""
        current_time = time.time()
        
        # Only run cleanup periodically to avoid performance impact
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
            
            self._last_cleanup = current_time
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            self.stats.storage_bytes = self._size_tracker
            self.stats.memory_efficiency = (
                self.stats.hits / max(1, len(self._cache)) if self._cache else 0.0
            )
            return self.stats


class HierarchicalCacheManager:
    """Hierarchical cache manager with multiple cache levels."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        
        # Configure cache levels based on hardware
        available_memory = hardware_detector.specs.available_memory_gb
        
        # L1: Fast in-memory cache
        l1_size = min(50, available_memory * 0.1)  # 10% of available memory, max 50MB
        self.l1_cache = AdvancedMemoryCache(
            max_size_mb=l1_size,
            max_entries=500,
            eviction_policy=EvictionPolicy.LRU,
            enable_compression=False  # No compression for L1 (speed priority)
        )
        
        # L2: Compressed memory cache
        l2_size = min(200, available_memory * 0.2)  # 20% of available memory, max 200MB
        self.l2_cache = AdvancedMemoryCache(
            max_size_mb=l2_size,
            max_entries=2000,
            eviction_policy=EvictionPolicy.ADAPTIVE,
            enable_compression=True
        )
        
        # L3: Disk cache (future implementation)
        self.l3_cache = None
        
        # L4: Distributed cache (Redis if available)
        self.l4_cache = None
        if REDIS_AVAILABLE:
            self._initialize_redis_cache()
        
        # Cache routing logic
        self.cache_routing = self._initialize_cache_routing()
        
        logger.info(
            "Hierarchical cache manager initialized",
            l1_size_mb=l1_size,
            l2_size_mb=l2_size,
            redis_available=self.l4_cache is not None
        )
    
    def _initialize_redis_cache(self):
        """Initialize Redis cache if available."""
        try:
            # Try to connect to Redis
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
            redis_client.ping()
            
            self.l4_cache = redis_client
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.info("Redis not available, skipping distributed cache", error=str(e))
            self.l4_cache = None
    
    def _initialize_cache_routing(self) -> Dict[str, CacheLevel]:
        """Initialize cache routing rules based on data patterns."""
        return {
            # Small, frequently accessed data -> L1
            "ai_model_configs": CacheLevel.L1_MEMORY,
            "user_preferences": CacheLevel.L1_MEMORY,
            "system_status": CacheLevel.L1_MEMORY,
            
            # Medium-sized, moderately accessed data -> L2
            "generated_code": CacheLevel.L2_COMPRESSED,
            "analysis_results": CacheLevel.L2_COMPRESSED,
            "recommendations": CacheLevel.L2_COMPRESSED,
            
            # Large, infrequently accessed data -> L3/L4
            "model_embeddings": CacheLevel.L4_DISTRIBUTED,
            "training_data": CacheLevel.L4_DISTRIBUTED,
            "historical_metrics": CacheLevel.L3_DISK
        }
    
    def _determine_cache_level(self, key: str, data_size_bytes: int) -> CacheLevel:
        """Determine appropriate cache level for data."""
        
        # Check routing rules first
        for pattern, level in self.cache_routing.items():
            if pattern in key:
                return level
        
        # Size-based routing
        if data_size_bytes < 1024:  # < 1KB
            return CacheLevel.L1_MEMORY
        elif data_size_bytes < 100 * 1024:  # < 100KB
            return CacheLevel.L2_COMPRESSED
        elif data_size_bytes < 10 * 1024 * 1024:  # < 10MB
            return CacheLevel.L3_DISK
        else:
            return CacheLevel.L4_DISTRIBUTED
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from appropriate cache level."""
        start_time = time.time()
        
        try:
            # Try L1 first (fastest)
            value = await self.l1_cache.get(key)
            if value is not None:
                logger.debug("Cache hit L1", key=key[:50])
                return value
            
            # Try L2 (compressed memory)
            value = await self.l2_cache.get(key)
            if value is not None:
                # Promote to L1 for future access
                await self.l1_cache.set(key, value, ttl=300)  # 5 min TTL in L1
                logger.debug("Cache hit L2", key=key[:50])
                return value
            
            # Try L4 (Redis) if available
            if self.l4_cache:
                try:
                    cached_data = self.l4_cache.get(key)
                    if cached_data:
                        value = pickle.loads(cached_data)
                        # Promote to L2
                        await self.l2_cache.set(key, value, ttl=3600)  # 1 hour TTL in L2
                        logger.debug("Cache hit L4", key=key[:50])
                        return value
                except Exception as e:
                    logger.warning("Redis get failed", key=key[:50], error=str(e))
            
            logger.debug("Cache miss", key=key[:50])
            return None
            
        except Exception as e:
            logger.error("Cache get failed", key=key[:50], error=str(e))
            return None
    
    async def set(self, 
                 key: str, 
                 value: Any, 
                 ttl: Optional[float] = None,
                 cache_level: Optional[CacheLevel] = None) -> bool:
        """Set value in appropriate cache level."""
        
        try:
            # Calculate data size
            data_size = len(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))
            
            # Determine cache level
            if cache_level is None:
                cache_level = self._determine_cache_level(key, data_size)
            
            success = False
            
            # Store in appropriate cache
            if cache_level == CacheLevel.L1_MEMORY:
                success = await self.l1_cache.set(key, value, ttl)
                
            elif cache_level == CacheLevel.L2_COMPRESSED:
                success = await self.l2_cache.set(key, value, ttl)
                
            elif cache_level == CacheLevel.L4_DISTRIBUTED and self.l4_cache:
                try:
                    serialized = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
                    if ttl:
                        success = self.l4_cache.setex(key, int(ttl), serialized)
                    else:
                        success = self.l4_cache.set(key, serialized)
                except Exception as e:
                    logger.warning("Redis set failed", key=key[:50], error=str(e))
                    # Fallback to L2
                    success = await self.l2_cache.set(key, value, ttl)
            
            else:
                # Default to L2
                success = await self.l2_cache.set(key, value, ttl)
            
            if success:
                logger.debug("Cache set", key=key[:50], level=cache_level.value, size_bytes=data_size)
            
            return success
            
        except Exception as e:
            logger.error("Cache set failed", key=key[:50], error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels."""
        success = True
        
        # Delete from all levels
        success &= await self.l1_cache.delete(key)
        success &= await self.l2_cache.delete(key)
        
        if self.l4_cache:
            try:
                self.l4_cache.delete(key)
            except Exception as e:
                logger.warning("Redis delete failed", key=key[:50], error=str(e))
                success = False
        
        return success
    
    async def clear_all(self):
        """Clear all cache levels."""
        await self.l1_cache.clear()
        await self.l2_cache.clear()
        
        if self.l4_cache:
            try:
                self.l4_cache.flushdb()
            except Exception as e:
                logger.warning("Redis clear failed", error=str(e))
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            "l1_cache": self.l1_cache.get_stats().__dict__,
            "l2_cache": self.l2_cache.get_stats().__dict__,
            "l4_cache": None
        }
        
        if self.l4_cache:
            try:
                redis_info = self.l4_cache.info()
                stats["l4_cache"] = {
                    "used_memory": redis_info.get("used_memory", 0),
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "total_commands_processed": redis_info.get("total_commands_processed", 0),
                    "keyspace_hits": redis_info.get("keyspace_hits", 0),
                    "keyspace_misses": redis_info.get("keyspace_misses", 0)
                }
            except Exception as e:
                logger.warning("Failed to get Redis stats", error=str(e))
        
        # Calculate overall statistics
        total_hits = stats["l1_cache"]["hits"] + stats["l2_cache"]["hits"]
        total_misses = stats["l1_cache"]["misses"] + stats["l2_cache"]["misses"]
        
        if stats["l4_cache"]:
            total_hits += stats["l4_cache"]["keyspace_hits"]
            total_misses += stats["l4_cache"]["keyspace_misses"]
        
        stats["overall"] = {
            "total_hits": total_hits,
            "total_misses": total_misses,
            "overall_hit_rate": total_hits / max(1, total_hits + total_misses),
            "total_memory_usage_mb": (
                stats["l1_cache"]["memory_usage_mb"] + stats["l2_cache"]["memory_usage_mb"]
            )
        }
        
        return stats
    
    async def optimize_performance(self):
        """Optimize cache performance based on usage patterns."""
        try:
            # Clean up expired entries
            await self.l1_cache.cleanup_expired()
            await self.l2_cache.cleanup_expired()
            
            # Get current statistics
            l1_stats = self.l1_cache.get_stats()
            l2_stats = self.l2_cache.get_stats()
            
            # Adjust cache sizes based on hit rates
            if l1_stats.hit_rate < 0.5 and l2_stats.hit_rate > 0.8:
                # L1 underperforming, L2 doing well - could adjust allocation
                logger.info("Cache performance optimization: L1 underperforming")
            
            # Force garbage collection to free memory
            gc.collect()
            
            logger.debug("Cache performance optimization completed")
            
        except Exception as e:
            logger.error("Cache optimization failed", error=str(e))


class CacheWarmer:
    """Intelligent cache warming system."""
    
    def __init__(self, cache_manager: HierarchicalCacheManager):
        self.cache_manager = cache_manager
        self.warming_patterns = self._load_warming_patterns()
        
    def _load_warming_patterns(self) -> Dict[str, List[str]]:
        """Load cache warming patterns."""
        return {
            "startup": [
                "system_config",
                "user_preferences",
                "ai_model_metadata",
                "hardware_specs"
            ],
            "ai_generation": [
                "terraform_templates",
                "ansible_templates", 
                "best_practices",
                "security_rules"
            ],
            "analysis": [
                "vulnerability_patterns",
                "performance_baselines",
                "compliance_rules"
            ]
        }
    
    async def warm_cache(self, pattern_name: str, data_provider: Callable):
        """Warm cache with specific pattern."""
        if pattern_name not in self.warming_patterns:
            logger.warning(f"Unknown warming pattern: {pattern_name}")
            return
        
        start_time = time.time()
        warmed_count = 0
        
        try:
            keys = self.warming_patterns[pattern_name]
            
            for key in keys:
                try:
                    # Check if already cached
                    cached_value = await self.cache_manager.get(key)
                    if cached_value is None:
                        # Generate and cache data
                        data = await data_provider(key)
                        if data is not None:
                            await self.cache_manager.set(key, data, ttl=3600)  # 1 hour TTL
                            warmed_count += 1
                
                except Exception as e:
                    logger.warning(f"Failed to warm cache key {key}", error=str(e))
            
            warming_time = time.time() - start_time
            logger.info(
                "Cache warming completed",
                pattern=pattern_name,
                warmed_count=warmed_count,
                time_seconds=warming_time
            )
            
        except Exception as e:
            logger.error("Cache warming failed", pattern=pattern_name, error=str(e))


# Global cache manager instance
cache_manager = None

def get_cache_manager() -> HierarchicalCacheManager:
    """Get global cache manager instance."""
    global cache_manager
    
    if cache_manager is None:
        cache_manager = HierarchicalCacheManager()
    
    return cache_manager


# Decorator for caching function results
def cached(ttl: Optional[float] = 3600, cache_level: Optional[CacheLevel] = None):
    """Decorator for caching function results."""
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            cache_key = f"func_{hashlib.md5(str(key_data).encode()).hexdigest()}"
            
            # Try to get from cache
            cache_mgr = get_cache_manager()
            cached_result = await cache_mgr.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache_mgr.set(cache_key, result, ttl, cache_level)
            return result
        
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Export main classes and functions
__all__ = [
    'HierarchicalCacheManager',
    'AdvancedMemoryCache',
    'CacheWarmer',
    'CacheLevel',
    'EvictionPolicy',
    'CacheStats',
    'CacheEntry',
    'get_cache_manager',
    'cached'
]