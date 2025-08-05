"""
Context-Aware Infrastructure Recommendations Engine.

This module provides intelligent infrastructure recommendations based on context,
historical data, best practices, and real-time analysis. Optimized for Intel N150
hardware with efficient processing and caching strategies.
"""

import re
import json
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum
import math

import structlog

# Advanced analysis libraries
try:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from ..core.hardware_detector import hardware_detector
from ..core.performance_monitor import PerformanceMonitor

logger = structlog.get_logger(__name__)


class RecommendationType(Enum):
    """Types of recommendations."""
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    COST_SAVING = "cost_saving"
    BEST_PRACTICE = "best_practice"
    PERFORMANCE = "performance"
    SCALABILITY = "scalability"
    MONITORING = "monitoring"
    BACKUP = "backup"
    COMPLIANCE = "compliance"
    TROUBLESHOOTING = "troubleshooting"


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ContextType(Enum):
    """Types of context for recommendations."""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COST = "cost"
    COMPLIANCE = "compliance"


@dataclass
class Recommendation:
    """Represents a single infrastructure recommendation."""
    
    id: str
    title: str
    description: str
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    confidence: float  # 0.0 to 1.0
    
    # Implementation details
    implementation_steps: List[str] = field(default_factory=list)
    code_examples: Dict[str, str] = field(default_factory=dict)
    estimated_effort: str = "medium"  # low, medium, high
    estimated_time: str = "1-2 hours"
    
    # Context and rationale
    context: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    related_recommendations: List[str] = field(default_factory=list)
    documentation_links: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class InfrastructureContext:
    """Context information about the infrastructure."""
    
    # System information
    vm_count: int = 0
    total_cpu_cores: int = 0
    total_memory_gb: float = 0.0
    total_storage_gb: float = 0.0
    
    # Network information
    network_segments: List[str] = field(default_factory=list)
    external_access: bool = False
    load_balancers: int = 0
    
    # Services and applications
    databases: List[str] = field(default_factory=list)
    web_servers: List[str] = field(default_factory=list)
    monitoring_tools: List[str] = field(default_factory=list)
    
    # Security information
    firewalls: List[str] = field(default_factory=list)
    ssl_certificates: List[str] = field(default_factory=list)
    backup_systems: List[str] = field(default_factory=list)
    
    # Environment information
    environment_type: str = "production"  # dev, staging, production
    compliance_requirements: List[str] = field(default_factory=list)
    budget_constraints: Optional[str] = None
    
    # Performance metrics
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    storage_utilization: float = 0.0
    network_utilization: float = 0.0
    
    # Historical data
    incident_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    growth_patterns: Dict[str, float] = field(default_factory=dict)


class RecommendationRuleEngine:
    """Rule-based recommendation engine with advanced logic."""
    
    def __init__(self):
        self.rules = self._load_recommendation_rules()
        self.patterns = self._load_pattern_analysis()
        self.best_practices = self._load_best_practices_database()
        
        logger.info("Recommendation rule engine initialized")
    
    def _load_recommendation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load recommendation rules organized by category."""
        return {
            "security": [
                {
                    "id": "sec_001",
                    "condition": lambda ctx: not ctx.firewalls,
                    "title": "Implement Network Firewall",
                    "description": "No firewall detected in your infrastructure. This poses significant security risks.",
                    "priority": RecommendationPriority.CRITICAL,
                    "confidence": 0.95,
                    "implementation": [
                        "Deploy a firewall solution (pfSense, iptables, or cloud-native firewall)",
                        "Configure default deny rules",
                        "Allow only necessary ports and protocols",
                        "Implement logging and monitoring"
                    ],
                    "benefits": [
                        "Protects against unauthorized access",
                        "Reduces attack surface",
                        "Provides network traffic visibility"
                    ],
                    "code_examples": {
                        "terraform": '''resource "proxmox_vm_qemu" "firewall" {
  name        = "firewall"
  target_node = "proxmox-node"
  cores       = 2
  memory      = 2048
  
  disk {
    size    = "20G"
    type    = "scsi"
    storage = "local-lvm"
  }
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }
}''',
                        "ansible": '''- name: Configure iptables firewall
  iptables:
    chain: INPUT
    policy: DROP
  
- name: Allow SSH
  iptables:
    chain: INPUT
    protocol: tcp
    destination_port: 22
    jump: ACCEPT'''
                    }
                },
                {
                    "id": "sec_002",
                    "condition": lambda ctx: ctx.external_access and not ctx.ssl_certificates,
                    "title": "Implement SSL/TLS Encryption",
                    "description": "External access detected without SSL certificates. Implement HTTPS encryption.",
                    "priority": RecommendationPriority.HIGH,
                    "confidence": 0.90,
                    "implementation": [
                        "Obtain SSL certificates (Let's Encrypt or commercial)",
                        "Configure web servers for HTTPS",
                        "Redirect HTTP to HTTPS",
                        "Implement HSTS headers"
                    ]
                },
                {
                    "id": "sec_003",
                    "condition": lambda ctx: not ctx.backup_systems,
                    "title": "Implement Backup Strategy",
                    "description": "No backup systems detected. Implement comprehensive backup solution.",
                    "priority": RecommendationPriority.HIGH,
                    "confidence": 0.90,
                    "implementation": [
                        "Deploy backup software (Proxmox Backup Server, Veeam, etc.)",
                        "Configure automated daily backups",
                        "Implement 3-2-1 backup strategy",
                        "Test backup restoration procedures"
                    ]
                }
            ],
            
            "performance": [
                {
                    "id": "perf_001",
                    "condition": lambda ctx: ctx.cpu_utilization > 80,
                    "title": "High CPU Utilization Detected",
                    "description": "CPU utilization is consistently above 80%. Consider scaling resources.",
                    "priority": RecommendationPriority.HIGH,
                    "confidence": 0.85,
                    "implementation": [
                        "Analyze CPU usage patterns",
                        "Add more CPU cores to existing VMs",
                        "Distribute workload across multiple VMs",
                        "Optimize application performance"
                    ]
                },
                {
                    "id": "perf_002",
                    "condition": lambda ctx: ctx.memory_utilization > 85,
                    "title": "High Memory Utilization",
                    "description": "Memory utilization is above 85%. Risk of performance degradation.",
                    "priority": RecommendationPriority.HIGH,
                    "confidence": 0.85,
                    "implementation": [
                        "Monitor memory usage patterns",
                        "Increase RAM allocation",
                        "Optimize application memory usage",
                        "Implement memory caching strategies"
                    ]
                },
                {
                    "id": "perf_003",
                    "condition": lambda ctx: ctx.storage_utilization > 90,
                    "title": "Critical Storage Utilization",
                    "description": "Storage utilization above 90%. Immediate action required.",
                    "priority": RecommendationPriority.CRITICAL,
                    "confidence": 0.95,
                    "implementation": [
                        "Clean up unnecessary files and logs",
                        "Expand storage capacity",
                        "Implement log rotation",
                        "Archive old data"
                    ]
                }
            ],
            
            "cost_optimization": [
                {
                    "id": "cost_001",
                    "condition": lambda ctx: ctx.cpu_utilization < 20 and ctx.vm_count > 1,
                    "title": "Underutilized Resources Detected",
                    "description": "Low CPU utilization suggests resource over-provisioning.",
                    "priority": RecommendationPriority.MEDIUM,
                    "confidence": 0.75,
                    "implementation": [
                        "Analyze resource usage patterns",
                        "Consolidate underutilized VMs",
                        "Right-size VM resources",
                        "Implement auto-scaling"
                    ]
                },
                {
                    "id": "cost_002",
                    "condition": lambda ctx: len(ctx.databases) > 1 and ctx.vm_count < 5,
                    "title": "Database Consolidation Opportunity",
                    "description": "Multiple databases detected in small infrastructure. Consider consolidation.",
                    "priority": RecommendationPriority.LOW,
                    "confidence": 0.60,
                    "implementation": [
                        "Assess database compatibility",
                        "Plan database consolidation",
                        "Implement proper database isolation",
                        "Monitor performance after consolidation"
                    ]
                }
            ],
            
            "scalability": [
                {
                    "id": "scale_001",
                    "condition": lambda ctx: ctx.load_balancers == 0 and ctx.web_servers and len(ctx.web_servers) > 1,
                    "title": "Implement Load Balancing",
                    "description": "Multiple web servers detected without load balancing.",
                    "priority": RecommendationPriority.MEDIUM,
                    "confidence": 0.80,
                    "implementation": [
                        "Deploy load balancer (HAProxy, Nginx, etc.)",
                        "Configure health checks",
                        "Implement session persistence if needed",
                        "Monitor load distribution"
                    ]
                },
                {
                    "id": "scale_002",
                    "condition": lambda ctx: ctx.vm_count > 10 and not ctx.monitoring_tools,
                    "title": "Implement Infrastructure Monitoring",
                    "description": "Large infrastructure without proper monitoring detected.",
                    "priority": RecommendationPriority.HIGH,
                    "confidence": 0.90,
                    "implementation": [
                        "Deploy monitoring solution (Prometheus + Grafana)",
                        "Configure metric collection",
                        "Set up alerting rules",
                        "Create monitoring dashboards"
                    ]
                }
            ],
            
            "best_practices": [
                {
                    "id": "bp_001",
                    "condition": lambda ctx: ctx.environment_type == "production" and not ctx.backup_systems,
                    "title": "Production Backup Requirements",
                    "description": "Production environment requires comprehensive backup solution.",
                    "priority": RecommendationPriority.CRITICAL,
                    "confidence": 0.95
                },
                {
                    "id": "bp_002",
                    "condition": lambda ctx: len(ctx.network_segments) < 2 and ctx.vm_count > 5,
                    "title": "Network Segmentation",
                    "description": "Consider network segmentation for improved security and performance.",
                    "priority": RecommendationPriority.MEDIUM,
                    "confidence": 0.70
                }
            ]
        }
    
    def _load_pattern_analysis(self) -> Dict[str, Any]:
        """Load pattern analysis configurations."""
        return {
            "growth_patterns": {
                "cpu_growth_threshold": 0.1,  # 10% growth per month
                "memory_growth_threshold": 0.15,  # 15% growth per month
                "storage_growth_threshold": 0.2,  # 20% growth per month
            },
            "performance_patterns": {
                "peak_usage_threshold": 0.8,  # 80% utilization
                "sustained_high_usage_hours": 4,  # 4 hours of high usage
                "performance_degradation_threshold": 0.2  # 20% performance drop
            },
            "security_patterns": {
                "incident_frequency_threshold": 5,  # 5 incidents per month
                "vulnerability_age_threshold": 30,  # 30 days
                "access_pattern_anomalies": True
            }
        }
    
    def _load_best_practices_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load best practices database."""
        return {
            "virtualization": [
                {
                    "practice": "Use template-based VM deployment",
                    "rationale": "Ensures consistency and reduces configuration errors",
                    "implementation": "Create standardized VM templates"
                },
                {
                    "practice": "Implement resource reservations",
                    "rationale": "Guarantees critical VM performance",
                    "implementation": "Configure CPU and memory reservations"
                }
            ],
            "networking": [
                {
                    "practice": "Separate management and production networks",
                    "rationale": "Improves security and reduces management interference",
                    "implementation": "Use VLANs for network segmentation"
                }
            ],
            "storage": [
                {
                    "practice": "Implement RAID for data protection",
                    "rationale": "Protects against disk failures",
                    "implementation": "Configure RAID 1 or RAID 5"
                }
            ]
        }
    
    async def evaluate_rules(self, context: InfrastructureContext) -> List[Recommendation]:
        """Evaluate all rules against the current context."""
        recommendations = []
        
        for category, rules in self.rules.items():
            for rule in rules:
                try:
                    if rule["condition"](context):
                        recommendation = Recommendation(
                            id=rule["id"],
                            title=rule["title"],
                            description=rule["description"],
                            recommendation_type=RecommendationType(category.lower().replace("_", "_")),
                            priority=rule["priority"],
                            confidence=rule["confidence"],
                            implementation_steps=rule.get("implementation", []),
                            code_examples=rule.get("code_examples", {}),
                            benefits=rule.get("benefits", []),
                            context={"category": category},
                            rationale=rule.get("rationale", rule["description"])
                        )
                        recommendations.append(recommendation)
                        
                except Exception as e:
                    logger.warning(f"Rule evaluation failed", rule_id=rule["id"], error=str(e))
        
        return recommendations


class PatternAnalyzer:
    """Analyzes patterns in infrastructure data for predictive recommendations."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.use_ml = SKLEARN_AVAILABLE and hardware_detector.specs.available_memory_gb > 4.0
        
        if self.use_ml:
            self.scaler = StandardScaler()
            self.clustering_model = None
        
        logger.info(f"Pattern analyzer initialized (ML enabled: {self.use_ml})")
    
    async def analyze_growth_patterns(self, context: InfrastructureContext) -> List[Recommendation]:
        """Analyze growth patterns and predict future needs."""
        recommendations = []
        
        if not context.performance_trends:
            return recommendations
        
        # Analyze CPU growth
        if "cpu_utilization" in context.performance_trends:
            cpu_trend = context.performance_trends["cpu_utilization"]
            if len(cpu_trend) >= 3:
                growth_rate = self._calculate_growth_rate(cpu_trend)
                
                if growth_rate > 0.1:  # 10% growth
                    recommendations.append(Recommendation(
                        id="growth_001",
                        title="CPU Capacity Planning",
                        description=f"CPU utilization growing at {growth_rate:.1%} per period. Plan capacity expansion.",
                        recommendation_type=RecommendationType.SCALABILITY,
                        priority=RecommendationPriority.MEDIUM,
                        confidence=0.75,
                        implementation_steps=[
                            "Monitor CPU growth trend",
                            "Plan CPU capacity expansion",
                            "Consider adding more cores or VMs",
                            "Implement auto-scaling if possible"
                        ],
                        rationale="Proactive capacity planning prevents performance issues"
                    ))
        
        # Analyze memory growth
        if "memory_utilization" in context.performance_trends:
            memory_trend = context.performance_trends["memory_utilization"]
            if len(memory_trend) >= 3:
                growth_rate = self._calculate_growth_rate(memory_trend)
                
                if growth_rate > 0.15:  # 15% growth
                    recommendations.append(Recommendation(
                        id="growth_002",
                        title="Memory Capacity Planning",
                        description=f"Memory utilization growing at {growth_rate:.1%} per period. Plan memory expansion.",
                        recommendation_type=RecommendationType.SCALABILITY,
                        priority=RecommendationPriority.MEDIUM,
                        confidence=0.75,
                        implementation_steps=[
                            "Monitor memory growth trend",
                            "Plan memory capacity expansion",
                            "Optimize application memory usage",
                            "Consider adding more RAM"
                        ]
                    ))
        
        return recommendations
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate from a series of values."""
        if len(values) < 2:
            return 0.0
        
        # Simple linear growth calculation
        start_value = values[0]
        end_value = values[-1]
        periods = len(values) - 1
        
        if start_value == 0:
            return 0.0
        
        return ((end_value / start_value) ** (1/periods)) - 1
    
    async def analyze_performance_patterns(self, context: InfrastructureContext) -> List[Recommendation]:
        """Analyze performance patterns for optimization recommendations."""
        recommendations = []
        
        # Check for sustained high utilization
        if context.cpu_utilization > 80 and context.memory_utilization > 80:
            recommendations.append(Recommendation(
                id="perf_pattern_001",
                title="System Under Stress",
                description="Both CPU and memory showing high utilization simultaneously.",
                recommendation_type=RecommendationType.PERFORMANCE,
                priority=RecommendationPriority.HIGH,
                confidence=0.90,
                implementation_steps=[
                    "Immediate: Monitor system stability",
                    "Short-term: Optimize resource allocation",
                    "Long-term: Scale infrastructure"
                ]
            ))
        
        # Check for storage bottlenecks
        if context.storage_utilization > 85:
            recommendations.append(Recommendation(
                id="perf_pattern_002",
                title="Storage Bottleneck Risk",
                description="Storage utilization approaching critical levels.",
                recommendation_type=RecommendationType.PERFORMANCE,
                priority=RecommendationPriority.HIGH,
                confidence=0.85,
                implementation_steps=[
                    "Clean up unnecessary files",
                    "Implement log rotation",
                    "Plan storage expansion",
                    "Consider storage optimization"
                ]
            ))
        
        return recommendations
    
    async def detect_anomalies(self, context: InfrastructureContext) -> List[Recommendation]:
        """Detect anomalies in infrastructure patterns."""
        recommendations = []
        
        # Simple anomaly detection based on thresholds
        if context.network_utilization > 90:
            recommendations.append(Recommendation(
                id="anomaly_001",
                title="Network Utilization Anomaly",
                description="Unusually high network utilization detected.",
                recommendation_type=RecommendationType.TROUBLESHOOTING,
                priority=RecommendationPriority.HIGH,
                confidence=0.80,
                implementation_steps=[
                    "Investigate network traffic patterns",
                    "Check for DDoS attacks or data transfers",
                    "Monitor network performance",
                    "Consider network capacity upgrade"
                ]
            ))
        
        # Check for unusual VM resource allocation
        if context.vm_count > 0:
            avg_cpu_per_vm = context.total_cpu_cores / context.vm_count
            avg_memory_per_vm = context.total_memory_gb / context.vm_count
            
            if avg_cpu_per_vm > 8:  # More than 8 cores per VM on average
                recommendations.append(Recommendation(
                    id="anomaly_002",
                    title="High CPU Allocation Per VM",
                    description="VMs allocated with unusually high CPU resources.",
                    recommendation_type=RecommendationType.OPTIMIZATION,
                    priority=RecommendationPriority.MEDIUM,
                    confidence=0.70,
                    implementation_steps=[
                        "Review VM resource allocation",
                        "Right-size VM resources",
                        "Consider workload distribution",
                        "Monitor actual CPU usage"
                    ]
                ))
        
        return recommendations


class ContextAwareRecommendationEngine:
    """Main context-aware recommendation engine."""
    
    def __init__(self):
        self.rule_engine = RecommendationRuleEngine()
        self.pattern_analyzer = PatternAnalyzer()
        self.performance_monitor = PerformanceMonitor()
        
        # Caching for performance optimization
        self.recommendation_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        
        logger.info("Context-aware recommendation engine initialized")
    
    async def generate_recommendations(self, 
                                     context: InfrastructureContext,
                                     focus_areas: Optional[List[str]] = None) -> List[Recommendation]:
        """Generate comprehensive infrastructure recommendations."""
        start_time = time.time()
        
        try:
            # Check cache
            cache_key = self._get_cache_key(context, focus_areas)
            if cache_key in self.recommendation_cache:
                cache_entry = self.recommendation_cache[cache_key]
                if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                    logger.debug("Using cached recommendations")
                    return cache_entry["recommendations"]
            
            recommendations = []
            
            # Rule-based recommendations
            rule_recommendations = await self.rule_engine.evaluate_rules(context)
            recommendations.extend(rule_recommendations)
            
            # Pattern-based recommendations
            pattern_recommendations = await self.pattern_analyzer.analyze_growth_patterns(context)
            recommendations.extend(pattern_recommendations)
            
            performance_recommendations = await self.pattern_analyzer.analyze_performance_patterns(context)
            recommendations.extend(performance_recommendations)
            
            anomaly_recommendations = await self.pattern_analyzer.detect_anomalies(context)
            recommendations.extend(anomaly_recommendations)
            
            # Filter by focus areas if specified
            if focus_areas:
                recommendations = [
                    rec for rec in recommendations 
                    if rec.recommendation_type.value in focus_areas or
                    any(tag in focus_areas for tag in rec.tags)
                ]
            
            # Sort by priority and confidence
            recommendations = self._prioritize_recommendations(recommendations)
            
            # Add related recommendations
            recommendations = await self._add_related_recommendations(recommendations, context)
            
            # Cache results
            self.recommendation_cache[cache_key] = {
                "recommendations": recommendations,
                "timestamp": time.time()
            }
            
            # Clean old cache entries
            self._clean_cache()
            
            logger.info(
                "Recommendations generated",
                count=len(recommendations),
                processing_time=time.time() - start_time
            )
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            return []
    
    def _get_cache_key(self, context: InfrastructureContext, focus_areas: Optional[List[str]]) -> str:
        """Generate cache key for recommendations."""
        import hashlib
        
        # Create a hash from context and focus areas
        context_str = json.dumps({
            "vm_count": context.vm_count,
            "cpu_utilization": context.cpu_utilization,
            "memory_utilization": context.memory_utilization,
            "storage_utilization": context.storage_utilization,
            "environment_type": context.environment_type,
            "focus_areas": focus_areas or []
        }, sort_keys=True)
        
        return hashlib.md5(context_str.encode()).hexdigest()[:16]
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Prioritize recommendations by priority and confidence."""
        priority_order = {
            RecommendationPriority.CRITICAL: 0,
            RecommendationPriority.HIGH: 1,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 3,
            RecommendationPriority.INFO: 4
        }
        
        return sorted(
            recommendations,
            key=lambda x: (priority_order[x.priority], -x.confidence)
        )
    
    async def _add_related_recommendations(self, 
                                         recommendations: List[Recommendation],
                                         context: InfrastructureContext) -> List[Recommendation]:
        """Add related recommendations based on context."""
        # Simple related recommendation logic
        rec_types = [rec.recommendation_type for rec in recommendations]
        
        # If security recommendations exist, suggest monitoring
        if RecommendationType.SECURITY in rec_types and RecommendationType.MONITORING not in rec_types:
            recommendations.append(Recommendation(
                id="related_001",
                title="Security Monitoring",
                description="Implement security monitoring to complement security improvements.",
                recommendation_type=RecommendationType.MONITORING,
                priority=RecommendationPriority.MEDIUM,
                confidence=0.70,
                implementation_steps=[
                    "Deploy security monitoring tools",
                    "Configure security alerts",
                    "Set up log analysis",
                    "Implement intrusion detection"
                ]
            ))
        
        # If performance issues exist, suggest monitoring
        if RecommendationType.PERFORMANCE in rec_types and not context.monitoring_tools:
            recommendations.append(Recommendation(
                id="related_002",
                title="Performance Monitoring",
                description="Implement performance monitoring to track optimization results.",
                recommendation_type=RecommendationType.MONITORING,
                priority=RecommendationPriority.MEDIUM,
                confidence=0.75,
                implementation_steps=[
                    "Deploy performance monitoring solution",
                    "Configure performance metrics",
                    "Set up performance alerts",
                    "Create performance dashboards"
                ]
            ))
        
        return recommendations
    
    def _clean_cache(self):
        """Clean expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.recommendation_cache.items()
            if current_time - value["timestamp"] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.recommendation_cache[key]
    
    async def get_recommendation_by_id(self, recommendation_id: str) -> Optional[Recommendation]:
        """Get specific recommendation by ID."""
        # This would typically query a database
        # For now, return None as this is a demo implementation
        return None
    
    async def mark_recommendation_implemented(self, recommendation_id: str) -> bool:
        """Mark a recommendation as implemented."""
        # This would typically update a database
        logger.info(f"Recommendation {recommendation_id} marked as implemented")
        return True
    
    def get_recommendation_summary(self, recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Get summary of recommendations."""
        summary = {
            "total_count": len(recommendations),
            "by_priority": defaultdict(int),
            "by_type": defaultdict(int),
            "avg_confidence": 0.0,
            "critical_count": 0,
            "high_priority_count": 0
        }
        
        if not recommendations:
            return summary
        
        total_confidence = 0.0
        
        for rec in recommendations:
            summary["by_priority"][rec.priority.value] += 1
            summary["by_type"][rec.recommendation_type.value] += 1
            total_confidence += rec.confidence
            
            if rec.priority == RecommendationPriority.CRITICAL:
                summary["critical_count"] += 1
            elif rec.priority == RecommendationPriority.HIGH:
                summary["high_priority_count"] += 1
        
        summary["avg_confidence"] = total_confidence / len(recommendations)
        
        return summary


# Global recommendation engine instance
recommendation_engine = None

def get_recommendation_engine() -> ContextAwareRecommendationEngine:
    """Get global recommendation engine instance."""
    global recommendation_engine
    
    if recommendation_engine is None:
        recommendation_engine = ContextAwareRecommendationEngine()
    
    return recommendation_engine


# Utility functions for CLI usage
async def get_quick_recommendations(infrastructure_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Quick recommendations for CLI usage."""
    engine = get_recommendation_engine()
    
    # Create context from infrastructure data
    context = InfrastructureContext(
        vm_count=infrastructure_data.get("vm_count", 0),
        total_cpu_cores=infrastructure_data.get("cpu_cores", 0),
        total_memory_gb=infrastructure_data.get("memory_gb", 0.0),
        cpu_utilization=infrastructure_data.get("cpu_utilization", 0.0),
        memory_utilization=infrastructure_data.get("memory_utilization", 0.0),
        storage_utilization=infrastructure_data.get("storage_utilization", 0.0),
        environment_type=infrastructure_data.get("environment", "production")
    )
    
    recommendations = await engine.generate_recommendations(context)
    
    # Convert to simple dict format
    return [
        {
            "title": rec.title,
            "description": rec.description,
            "type": rec.recommendation_type.value,
            "priority": rec.priority.value,
            "confidence": rec.confidence,
            "steps": rec.implementation_steps[:3]  # Top 3 steps
        }
        for rec in recommendations[:5]  # Top 5 recommendations
    ]


# Export main classes and functions
__all__ = [
    'Recommendation',
    'InfrastructureContext',
    'RecommendationType',
    'RecommendationPriority',
    'ContextAwareRecommendationEngine',
    'RecommendationRuleEngine',
    'PatternAnalyzer',
    'get_recommendation_engine',
    'get_quick_recommendations'
]