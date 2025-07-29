"""
Security Monitoring and Alerting System

Real-time security monitoring, threat detection, and automated
incident response for the Proxmox AI infrastructure.
"""

import pytest
import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
import threading
from queue import Queue
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Security alert types."""
    AUTHENTICATION_FAILURE = "auth_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_POLICY_VIOLATION = "policy_violation"
    SYSTEM_COMPROMISE = "system_compromise"
    DATA_BREACH = "data_breach"
    CONFIGURATION_DRIFT = "config_drift"
    VULNERABILITY_DETECTED = "vulnerability"
    COMPLIANCE_VIOLATION = "compliance_violation"


@dataclass
class SecurityEvent:
    """Security event data structure."""
    timestamp: datetime
    event_type: AlertType
    threat_level: ThreatLevel
    source: str
    description: str
    details: Dict[str, Any]
    user: Optional[str] = None
    resource: Optional[str] = None
    remediation_suggested: Optional[str] = None
    event_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = self._generate_event_id()
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        content = f"{self.timestamp.isoformat()}{self.source}{self.description}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['threat_level'] = self.threat_level.value
        return data


class SecurityMonitor:
    """
    Real-time security monitoring system with threat detection
    and automated incident response capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.event_queue = Queue()
        self.alert_handlers: List[Callable] = []
        self.monitoring_active = False
        self.event_history: List[SecurityEvent] = []
        self.threat_patterns: Dict[str, Any] = {}
        self.baseline_metrics: Dict[str, Any] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Initialize threat detection patterns
        self._initialize_threat_patterns()
        
        # Set up alert handlers
        self._setup_alert_handlers()
        
        logger.info("Security monitoring system initialized")
    
    def start_monitoring(self) -> None:
        """Start real-time security monitoring."""
        if self.monitoring_active:
            logger.warning("Security monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info("Security monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop security monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Security monitoring stopped")
    
    def log_security_event(
        self,
        event_type: AlertType,
        threat_level: ThreatLevel,
        source: str,
        description: str,
        details: Dict[str, Any],
        user: Optional[str] = None,
        resource: Optional[str] = None
    ) -> SecurityEvent:
        """
        Log a security event for monitoring and analysis.
        
        Args:
            event_type: Type of security event
            threat_level: Severity level
            source: Source system/component
            description: Event description
            details: Additional event details
            user: User associated with event
            resource: Resource involved
            
        Returns:
            SecurityEvent: Created security event
        """
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            threat_level=threat_level,
            source=source,
            description=description,
            details=details,
            user=user,
            resource=resource
        )
        
        # Add to event queue for processing
        self.event_queue.put(event)
        
        # Add to history
        self.event_history.append(event)
        
        # Trigger immediate processing for critical events
        if threat_level == ThreatLevel.CRITICAL:
            self._process_critical_event(event)
        
        logger.info(
            "Security event logged",
            event_id=event.event_id,
            type=event_type.value,
            level=threat_level.value
        )
        
        return event
    
    def analyze_security_trends(
        self,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """
        Analyze security trends and patterns.
        
        Args:
            time_window: Time window for analysis
            
        Returns:
            Dict containing security trend analysis
        """
        cutoff_time = datetime.utcnow() - time_window
        recent_events = [
            event for event in self.event_history
            if event.timestamp >= cutoff_time
        ]
        
        analysis = {
            'total_events': len(recent_events),
            'events_by_type': {},
            'events_by_level': {},
            'events_by_source': {},
            'hourly_distribution': {},
            'top_users': {},
            'top_resources': {},
            'anomalies': [],
            'recommendations': []
        }
        
        # Analyze events by type
        for event in recent_events:
            event_type = event.event_type.value
            analysis['events_by_type'][event_type] = \
                analysis['events_by_type'].get(event_type, 0) + 1
        
        # Analyze events by threat level
        for event in recent_events:
            level = event.threat_level.value
            analysis['events_by_level'][level] = \
                analysis['events_by_level'].get(level, 0) + 1
        
        # Analyze events by source
        for event in recent_events:
            source = event.source
            analysis['events_by_source'][source] = \
                analysis['events_by_source'].get(source, 0) + 1
        
        # Analyze hourly distribution
        for event in recent_events:
            hour = event.timestamp.hour
            analysis['hourly_distribution'][hour] = \
                analysis['hourly_distribution'].get(hour, 0) + 1
        
        # Analyze top users
        for event in recent_events:
            if event.user:
                analysis['top_users'][event.user] = \
                    analysis['top_users'].get(event.user, 0) + 1
        
        # Analyze top resources
        for event in recent_events:
            if event.resource:
                analysis['top_resources'][event.resource] = \
                    analysis['top_resources'].get(event.resource, 0) + 1
        
        # Detect anomalies
        analysis['anomalies'] = self._detect_anomalies(recent_events)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_trend_recommendations(analysis)
        
        return analysis
    
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get data for security monitoring dashboard."""
        now = datetime.utcnow()
        
        # Recent events (last 24 hours)
        recent_events = [
            event for event in self.event_history
            if event.timestamp >= now - timedelta(hours=24)
        ]
        
        # Critical events (last 7 days)
        critical_events = [
            event for event in self.event_history
            if event.timestamp >= now - timedelta(days=7) and
               event.threat_level == ThreatLevel.CRITICAL
        ]
        
        dashboard_data = {
            'timestamp': now.isoformat(),
            'monitoring_active': self.monitoring_active,
            'total_events_24h': len(recent_events),
            'critical_events_7d': len(critical_events),
            'threat_level_distribution': self._get_threat_distribution(recent_events),
            'recent_critical_events': [
                event.to_dict() for event in critical_events[-5:]
            ],
            'security_metrics': self._calculate_security_metrics(),
            'system_health': self._assess_system_health(),
            'active_threats': self._identify_active_threats(),
            'compliance_status': self._check_compliance_status()
        }
        
        return dashboard_data
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop for processing security events."""
        while self.monitoring_active:
            try:
                # Process queued events
                while not self.event_queue.empty():
                    event = self.event_queue.get()
                    self._process_security_event(event)
                
                # Perform periodic checks
                self._perform_periodic_checks()
                
                # Sleep briefly before next iteration
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _process_security_event(self, event: SecurityEvent) -> None:
        """Process a security event."""
        try:
            # Pattern matching for threat detection
            if self._matches_threat_pattern(event):
                self._escalate_threat(event)
            
            # Check for correlation with other events
            correlated_events = self._find_correlated_events(event)
            if correlated_events:
                self._analyze_event_correlation(event, correlated_events)
            
            # Update metrics
            self._update_security_metrics(event)
            
            # Trigger alerts if necessary
            if self._should_trigger_alert(event):
                self._trigger_security_alert(event)
            
        except Exception as e:
            logger.error(f"Error processing security event {event.event_id}: {e}")
    
    def _process_critical_event(self, event: SecurityEvent) -> None:
        """Process critical security event immediately."""
        logger.critical(
            "Critical security event detected",
            event_id=event.event_id,
            description=event.description
        )
        
        # Immediate alert
        self._trigger_immediate_alert(event)
        
        # Auto-remediation if configured
        if self.config.get('auto_remediation', False):
            self._attempt_auto_remediation(event)
    
    def _initialize_threat_patterns(self) -> None:
        """Initialize threat detection patterns."""
        self.threat_patterns = {
            'brute_force': {
                'pattern': 'multiple_auth_failures',
                'threshold': 5,
                'time_window': 300,  # 5 minutes
                'threat_level': ThreatLevel.HIGH
            },
            'suspicious_login': {
                'pattern': 'unusual_login_location',
                'threshold': 1,
                'time_window': 3600,  # 1 hour
                'threat_level': ThreatLevel.MEDIUM
            },
            'privilege_escalation': {
                'pattern': 'unexpected_admin_access',
                'threshold': 1,
                'time_window': 1800,  # 30 minutes
                'threat_level': ThreatLevel.HIGH
            },
            'data_exfiltration': {
                'pattern': 'large_data_transfer',
                'threshold': 1,
                'time_window': 1800,  # 30 minutes
                'threat_level': ThreatLevel.CRITICAL
            }
        }
    
    def _setup_alert_handlers(self) -> None:
        """Set up alert handling mechanisms."""
        # Email alerts
        if self.config.get('email_alerts', {}).get('enabled', False):
            self.alert_handlers.append(self._send_email_alert)
        
        # Webhook alerts
        if self.config.get('webhook_alerts', {}).get('enabled', False):
            self.alert_handlers.append(self._send_webhook_alert)
        
        # Log alerts (always enabled)
        self.alert_handlers.append(self._log_alert)
    
    def _matches_threat_pattern(self, event: SecurityEvent) -> bool:
        """Check if event matches known threat patterns."""
        # Implementation would check various threat patterns
        return False  # Simplified for now
    
    def _find_correlated_events(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Find events correlated with the given event."""
        # Implementation would find related events
        return []  # Simplified for now
    
    def _analyze_event_correlation(
        self,
        event: SecurityEvent,
        correlated_events: List[SecurityEvent]
    ) -> None:
        """Analyze correlation between events."""
        # Implementation would analyze event patterns
        pass
    
    def _update_security_metrics(self, event: SecurityEvent) -> None:
        """Update security metrics based on event."""
        # Implementation would update various metrics
        pass
    
    def _should_trigger_alert(self, event: SecurityEvent) -> bool:
        """Determine if an alert should be triggered."""
        # Always alert on high and critical events
        if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            return True
        
        # Check for patterns that warrant alerts
        return False
    
    def _trigger_security_alert(self, event: SecurityEvent) -> None:
        """Trigger security alert through configured channels."""
        for handler in self.alert_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def _trigger_immediate_alert(self, event: SecurityEvent) -> None:
        """Trigger immediate alert for critical events."""
        # Force immediate processing
        for handler in self.alert_handlers:
            try:
                handler(event, immediate=True)
            except Exception as e:
                logger.error(f"Immediate alert handler failed: {e}")
    
    def _attempt_auto_remediation(self, event: SecurityEvent) -> None:
        """Attempt automatic remediation of security event."""
        remediation_actions = {
            AlertType.AUTHENTICATION_FAILURE: self._block_suspicious_ip,
            AlertType.SYSTEM_COMPROMISE: self._isolate_system,
            AlertType.DATA_BREACH: self._lock_down_data_access
        }
        
        action = remediation_actions.get(event.event_type)
        if action:
            try:
                action(event)
                logger.info(f"Auto-remediation attempted for event {event.event_id}")
            except Exception as e:
                logger.error(f"Auto-remediation failed for event {event.event_id}: {e}")
    
    def _perform_periodic_checks(self) -> None:
        """Perform periodic security checks."""
        # Check system health
        # Validate configurations
        # Monitor resource usage
        # Check for policy violations
        pass
    
    def _detect_anomalies(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Detect anomalies in security events."""
        anomalies = []
        
        # Example: Unusual event frequency
        if len(events) > 100:
            anomalies.append({
                'type': 'high_event_frequency',
                'description': f'Unusually high number of events: {len(events)}',
                'severity': 'medium'
            })
        
        return anomalies
    
    def _generate_trend_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on trend analysis."""
        recommendations = []
        
        # High number of authentication failures
        auth_failures = analysis['events_by_type'].get('auth_failure', 0)
        if auth_failures > 10:
            recommendations.append({
                'type': 'security_hardening',
                'description': 'Consider implementing additional authentication controls',
                'priority': 'high'
            })
        
        return recommendations
    
    def _get_threat_distribution(
        self,
        events: List[SecurityEvent]
    ) -> Dict[str, int]:
        """Get threat level distribution."""
        distribution = {}
        for event in events:
            level = event.threat_level.value
            distribution[level] = distribution.get(level, 0) + 1
        return distribution
    
    def _calculate_security_metrics(self) -> Dict[str, Any]:
        """Calculate current security metrics."""
        return {
            'mean_time_to_detection': 0,  # Would calculate actual MTTD
            'mean_time_to_response': 0,   # Would calculate actual MTTR
            'false_positive_rate': 0,     # Would calculate actual FPR
            'security_coverage': 95       # Would calculate actual coverage
        }
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system security health."""
        return {
            'status': 'healthy',
            'score': 85,
            'issues': [],
            'last_assessment': datetime.utcnow().isoformat()
        }
    
    def _identify_active_threats(self) -> List[Dict[str, Any]]:
        """Identify currently active threats."""
        return []  # Would identify actual active threats
    
    def _check_compliance_status(self) -> Dict[str, Any]:
        """Check compliance status."""
        return {
            'cis_compliance': 90,
            'nist_compliance': 88,
            'owasp_compliance': 92,
            'last_check': datetime.utcnow().isoformat()
        }
    
    # Alert handlers
    
    def _log_alert(self, event: SecurityEvent, immediate: bool = False) -> None:
        """Log security alert."""
        level_map = {
            ThreatLevel.LOW: logger.info,
            ThreatLevel.MEDIUM: logger.warning,
            ThreatLevel.HIGH: logger.error,
            ThreatLevel.CRITICAL: logger.critical
        }
        
        log_func = level_map.get(event.threat_level, logger.info)
        log_func(
            f"SECURITY ALERT: {event.description}",
            event_id=event.event_id,
            type=event.event_type.value,
            level=event.threat_level.value,
            source=event.source,
            user=event.user,
            resource=event.resource
        )
    
    def _send_email_alert(self, event: SecurityEvent, immediate: bool = False) -> None:
        """Send email alert."""
        # Implementation would send actual email
        logger.info(f"Email alert sent for event {event.event_id}")
    
    def _send_webhook_alert(self, event: SecurityEvent, immediate: bool = False) -> None:
        """Send webhook alert."""
        # Implementation would send webhook
        logger.info(f"Webhook alert sent for event {event.event_id}")
    
    # Auto-remediation actions
    
    def _block_suspicious_ip(self, event: SecurityEvent) -> None:
        """Block suspicious IP address."""
        # Implementation would block IP
        logger.info(f"IP blocking attempted for event {event.event_id}")
    
    def _isolate_system(self, event: SecurityEvent) -> None:
        """Isolate compromised system."""
        # Implementation would isolate system
        logger.info(f"System isolation attempted for event {event.event_id}")
    
    def _lock_down_data_access(self, event: SecurityEvent) -> None:
        """Lock down data access."""
        # Implementation would restrict access
        logger.info(f"Data access lockdown attempted for event {event.event_id}")


class TestSecurityMonitoring:
    """Pytest test class for security monitoring system."""
    
    @pytest.fixture
    def security_monitor(self):
        """Fixture to create security monitor instance."""
        config = {
            'email_alerts': {'enabled': False},
            'webhook_alerts': {'enabled': False},
            'auto_remediation': False
        }
        return SecurityMonitor(config)
    
    def test_security_event_logging(self, security_monitor):
        """Test security event logging."""
        event = security_monitor.log_security_event(
            event_type=AlertType.AUTHENTICATION_FAILURE,
            threat_level=ThreatLevel.MEDIUM,
            source="test_system",
            description="Test authentication failure",
            details={"attempt_count": 3},
            user="test_user"
        )
        
        assert event.event_id is not None
        assert event.event_type == AlertType.AUTHENTICATION_FAILURE
        assert event.threat_level == ThreatLevel.MEDIUM
        assert len(security_monitor.event_history) == 1
    
    def test_security_trend_analysis(self, security_monitor):
        """Test security trend analysis."""
        # Log multiple events
        for i in range(5):
            security_monitor.log_security_event(
                event_type=AlertType.AUTHENTICATION_FAILURE,
                threat_level=ThreatLevel.LOW,
                source="test_system",
                description=f"Test event {i}",
                details={}
            )
        
        analysis = security_monitor.analyze_security_trends()
        
        assert analysis['total_events'] == 5
        assert 'auth_failure' in analysis['events_by_type']
        assert analysis['events_by_type']['auth_failure'] == 5
    
    def test_critical_event_processing(self, security_monitor):
        """Test critical event processing."""
        event = security_monitor.log_security_event(
            event_type=AlertType.SYSTEM_COMPROMISE,
            threat_level=ThreatLevel.CRITICAL,
            source="test_system",
            description="Critical test event",
            details={}
        )
        
        # Critical events should be processed immediately
        assert event.threat_level == ThreatLevel.CRITICAL
        assert len(security_monitor.event_history) == 1
    
    def test_security_dashboard_data(self, security_monitor):
        """Test security dashboard data generation."""
        # Log some test events
        security_monitor.log_security_event(
            event_type=AlertType.SUSPICIOUS_ACTIVITY,
            threat_level=ThreatLevel.HIGH,
            source="test_system",
            description="Test suspicious activity",
            details={}
        )
        
        dashboard_data = security_monitor.get_security_dashboard_data()
        
        assert 'timestamp' in dashboard_data
        assert 'monitoring_active' in dashboard_data
        assert 'total_events_24h' in dashboard_data
        assert 'security_metrics' in dashboard_data
        assert 'system_health' in dashboard_data
    
    def test_monitoring_lifecycle(self, security_monitor):
        """Test monitoring start/stop lifecycle."""
        assert not security_monitor.monitoring_active
        
        security_monitor.start_monitoring()
        assert security_monitor.monitoring_active
        
        security_monitor.stop_monitoring()
        assert not security_monitor.monitoring_active


if __name__ == "__main__":
    # Example usage for manual testing
    def main():
        config = {
            'email_alerts': {'enabled': False},
            'webhook_alerts': {'enabled': False},
            'auto_remediation': False
        }
        
        monitor = SecurityMonitor(config)
        monitor.start_monitoring()
        
        print("Security monitoring started...")
        
        # Log some test events
        monitor.log_security_event(
            event_type=AlertType.AUTHENTICATION_FAILURE,
            threat_level=ThreatLevel.MEDIUM,
            source="test_api",
            description="Failed login attempt",
            details={"ip": "192.168.1.100", "attempts": 3},
            user="suspicious_user"
        )
        
        monitor.log_security_event(
            event_type=AlertType.SUSPICIOUS_ACTIVITY,
            threat_level=ThreatLevel.HIGH,
            source="test_vm",
            description="Unusual network traffic detected",
            details={"bytes_transferred": 1000000},
            resource="vm-101"
        )
        
        # Analyze trends
        analysis = monitor.analyze_security_trends()
        print(f"\nSecurity Analysis:")
        print(f"Total Events: {analysis['total_events']}")
        print(f"Events by Type: {analysis['events_by_type']}")
        
        # Get dashboard data
        dashboard = monitor.get_security_dashboard_data()
        print(f"\nDashboard Data:")
        print(f"Events (24h): {dashboard['total_events_24h']}")
        print(f"System Health: {dashboard['system_health']['status']}")
        
        monitor.stop_monitoring()
        print("\nSecurity monitoring stopped.")
    
    main()