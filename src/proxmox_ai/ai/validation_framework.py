"""
Technical Validation Framework for Proxmox AI Assistant.

Provides comprehensive validation and security-conscious recommendation system
for all infrastructure configurations and user inputs. Ensures enterprise-grade
security and compliance throughout the AI assistant interactions.

Features:
- Multi-layer input validation and sanitization
- Configuration security validation
- Best practices compliance checking
- Risk assessment and mitigation
- Threat modeling integration
- Automated security recommendations
"""

import re
import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

from .knowledge_base import TechnicalDomain, technical_knowledge_base

logger = structlog.get_logger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationCategory(Enum):
    """Categories of validation checks."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    BEST_PRACTICES = "best_practices"
    SYNTAX = "syntax"
    LOGIC = "logic"
    COMPATIBILITY = "compatibility"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    category: ValidationCategory
    level: ValidationLevel
    risk_level: RiskLevel
    message: str
    description: str
    remediation: str
    affected_components: List[str]
    compliance_frameworks: List[str]
    references: List[str]
    auto_fixable: bool = False
    fix_command: Optional[str] = None


@dataclass
class SecurityAssessment:
    """Comprehensive security assessment."""
    overall_score: float  # 0-100
    risk_level: RiskLevel
    critical_issues: List[ValidationResult]
    high_risk_issues: List[ValidationResult]
    medium_risk_issues: List[ValidationResult]
    recommendations: List[str]
    compliance_status: Dict[str, bool]
    threat_vectors: List[str]


class TechnicalValidationFramework:
    """
    Comprehensive technical validation and security framework.
    
    Provides enterprise-grade validation for:
    - User input sanitization and security
    - Infrastructure configuration validation
    - Security posture assessment
    - Compliance checking (CIS, NIST, SOC2, ISO27001)
    - Best practices enforcement
    - Risk assessment and mitigation
    """
    
    def __init__(self):
        """Initialize the validation framework."""
        
        # Input validation patterns
        self.dangerous_patterns = self._initialize_dangerous_patterns()
        self.sanitization_rules = self._initialize_sanitization_rules()
        
        # Configuration validators
        self.config_validators = self._initialize_config_validators()
        
        # Security baselines
        self.security_baselines = self._initialize_security_baselines()
        
        # Compliance frameworks
        self.compliance_frameworks = self._initialize_compliance_frameworks()
        
        # Risk assessment matrices
        self.risk_matrices = self._initialize_risk_matrices()
        
        logger.info("Technical validation framework initialized")
    
    def _initialize_dangerous_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for dangerous input detection."""
        return {
            "command_injection": [
                r";\s*(?:rm|del|format|fdisk|mkfs)",
                r"&&\s*(?:rm|del|format|fdisk|mkfs)",
                r"\|\s*(?:rm|del|format|fdisk|mkfs)",
                r"`.*(?:rm|del|format|fdisk|mkfs)",
                r"\$\(.*(?:rm|del|format|fdisk|mkfs)",
                r"exec\s*\(",
                r"eval\s*\(",
                r"system\s*\(",
                r"passthru\s*\(",
                r"shell_exec\s*\("
            ],
            "sql_injection": [
                r"(?:'|\"|`)\s*(?:OR|AND)\s*(?:'|\"|`)",
                r"(?:'|\"|`)\s*(?:UNION|SELECT|INSERT|UPDATE|DELETE|DROP)",
                r"(?:'|\"|`)\s*(?:;|--|\#)",
                r"(?:OR|AND)\s+\d+\s*=\s*\d+",
                r"(?:UNION|SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*(?:FROM|INTO|SET|TABLE)"
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c",
                r"\\.\\.\\",
                r"/etc/passwd",
                r"/etc/shadow",
                r"\\windows\\system32"
            ],
            "code_injection": [
                r"<script.*?>",
                r"javascript:",
                r"vbscript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"onclick\s*=",
                r"<?php",
                r"<%.*%>",
                r"{{.*}}",
                r"{%.*%}"
            ],
            "network_attacks": [
                r"(?:0\.0\.0\.0|127\.0\.0\.1|localhost)(?::\d+)?/",
                r"(?:192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)[\d.]+(?::\d+)?/",
                r"(?:http|https|ftp|ssh|telnet)://.*(?:@|:).*(?:@|:)",
                r"nc\s+-[a-z]*l",
                r"netcat\s+-[a-z]*l",
                r"nmap\s+",
                r"masscan\s+"
            ]
        }
    
    def _initialize_sanitization_rules(self) -> Dict[str, str]:
        """Initialize input sanitization rules."""
        return {
            "remove_dangerous_chars": r"[;&|`$(){}[\]<>\"']",
            "normalize_whitespace": r"\s+",
            "limit_length": 10000,  # Maximum input length
            "allowed_protocols": ["http", "https", "ssh", "ftp"],
            "blocked_extensions": [".exe", ".bat", ".cmd", ".ps1", ".sh", ".php", ".jsp", ".asp"],
            "allowed_domains": []  # Define allowed domains for URL validation
        }
    
    def _initialize_config_validators(self) -> Dict[str, Dict[str, Any]]:
        """Initialize configuration validators for different domains."""
        return {
            "proxmox": {
                "vm_config": {
                    "required_fields": ["name", "memory", "cores", "net0", "bootdisk"],
                    "memory_limits": {"min": 512, "max": 131072},  # 512MB to 128GB
                    "cores_limits": {"min": 1, "max": 64},
                    "security_requirements": [
                        "agent_enabled",
                        "firewall_enabled", 
                        "secure_boot_recommended"
                    ]
                },
                "cluster_config": {
                    "required_fields": ["nodes", "ring0_addr", "ring1_addr"],
                    "min_nodes": 3,
                    "quorum_requirements": True,
                    "fencing_required": True
                },
                "storage_config": {
                    "encryption_required": True,
                    "backup_retention": {"min": 7, "recommended": 30},
                    "replication_factor": {"min": 2, "recommended": 3}
                }
            },
            "terraform": {
                "syntax_validation": {
                    "required_blocks": ["terraform", "provider"],
                    "version_constraints": True,
                    "variable_validation": True
                },
                "security_validation": {
                    "no_hardcoded_secrets": True,
                    "encryption_at_rest": True,
                    "encryption_in_transit": True,
                    "iam_least_privilege": True
                }
            },
            "ansible": {
                "playbook_validation": {
                    "required_fields": ["name", "hosts", "tasks"],
                    "handler_definitions": True,
                    "idempotency_check": True
                },
                "security_validation": {
                    "no_sudo_all": True,
                    "vault_for_secrets": True,
                    "ssh_key_auth": True,
                    "privilege_escalation_explicit": True
                }
            },
            "docker": {
                "dockerfile_validation": {
                    "user_not_root": True,
                    "minimal_base_image": True,
                    "multi_stage_build": True,
                    "health_check": True
                },
                "compose_validation": {
                    "version_specified": True,
                    "resource_limits": True,
                    "secrets_management": True,
                    "network_security": True
                }
            },
            "kubernetes": {
                "manifest_validation": {
                    "resource_limits": True,
                    "security_context": True,
                    "network_policies": True,
                    "rbac_defined": True
                },
                "security_validation": {
                    "pod_security_standards": True,
                    "secrets_encrypted": True,
                    "admission_controllers": True,
                    "audit_logging": True
                }
            }
        }
    
    def _initialize_security_baselines(self) -> Dict[str, Dict[str, Any]]:
        """Initialize security baselines for different systems."""
        return {
            "linux": {
                "user_management": [
                    "No direct root login via SSH",
                    "SSH key-based authentication required",
                    "Password complexity requirements enforced",
                    "Account lockout policies implemented",
                    "Regular user access reviews"
                ],
                "network_security": [
                    "Firewall enabled and configured",
                    "Unnecessary services disabled",
                    "Network segmentation implemented",
                    "Intrusion detection system deployed",
                    "Regular security updates applied"
                ],
                "file_system": [
                    "Proper file permissions enforced",
                    "Disk encryption enabled",
                    "Regular integrity checks",
                    "Audit logging configured",
                    "Backup encryption enabled"
                ]
            },
            "proxmox": {
                "cluster_security": [
                    "Cluster communication encrypted",
                    "API access restricted by IP",
                    "Two-factor authentication enabled",
                    "Regular security updates applied",
                    "Audit logging enabled"
                ],
                "vm_security": [
                    "VM isolation properly configured",
                    "Network segmentation implemented",
                    "Guest agent security configured",
                    "Backup encryption enabled",
                    "Resource limits enforced"
                ]
            },
            "cloud": {
                "identity_access": [
                    "Multi-factor authentication required",
                    "Least privilege access enforced",
                    "Regular access reviews conducted",
                    "Service accounts properly managed",
                    "API key rotation implemented"
                ],
                "data_protection": [
                    "Encryption at rest enabled",
                    "Encryption in transit enforced",
                    "Key management centralized",
                    "Data classification implemented",
                    "Backup encryption enabled"
                ]
            }
        }
    
    def _initialize_compliance_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance framework requirements."""
        return {
            "CIS": {
                "description": "Center for Internet Security Benchmarks",
                "controls": {
                    "access_control": ["Multi-factor authentication", "Privileged access management"],
                    "system_hardening": ["Remove unnecessary software", "Configure secure boot"],
                    "logging_monitoring": ["Centralized logging", "Security event monitoring"],
                    "network_security": ["Firewall configuration", "Network segmentation"]
                }
            },
            "NIST": {
                "description": "NIST Cybersecurity Framework",
                "functions": {
                    "identify": ["Asset management", "Risk assessment"],
                    "protect": ["Access control", "Data security"],
                    "detect": ["Security monitoring", "Anomaly detection"],
                    "respond": ["Incident response", "Communications"],
                    "recover": ["Recovery planning", "Improvements"]
                }
            },
            "SOC2": {
                "description": "Service Organization Control 2",
                "trust_criteria": {
                    "security": ["Access controls", "System monitoring"],
                    "availability": ["System uptime", "Performance monitoring"],
                    "processing_integrity": ["Data validation", "Error handling"],
                    "confidentiality": ["Data encryption", "Access restrictions"],
                    "privacy": ["Data collection", "Data retention"]
                }
            },
            "ISO27001": {
                "description": "Information Security Management System",
                "domains": {
                    "security_policy": ["Information security policies"],
                    "organization": ["Organization of information security"],
                    "human_resources": ["Human resource security"],
                    "asset_management": ["Asset management"],
                    "access_control": ["Access control"],
                    "cryptography": ["Cryptography"],
                    "physical_security": ["Physical and environmental security"],
                    "operations": ["Operations security"],
                    "communications": ["Communications security"],
                    "acquisition": ["System acquisition, development and maintenance"],
                    "supplier": ["Supplier relationships"],
                    "incident_management": ["Information security incident management"],
                    "continuity": ["Information security aspects of business continuity"],
                    "compliance": ["Compliance"]
                }
            }
        }
    
    def _initialize_risk_matrices(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk assessment matrices."""
        return {
            "likelihood": {
                "very_low": {"score": 1, "description": "Very unlikely to occur"},
                "low": {"score": 2, "description": "Unlikely to occur"},
                "medium": {"score": 3, "description": "Possible to occur"},
                "high": {"score": 4, "description": "Likely to occur"},
                "very_high": {"score": 5, "description": "Almost certain to occur"}
            },
            "impact": {
                "negligible": {"score": 1, "description": "Minimal impact on operations"},
                "minor": {"score": 2, "description": "Limited impact on operations"},
                "moderate": {"score": 3, "description": "Significant impact on operations"},
                "major": {"score": 4, "description": "Severe impact on operations"},
                "catastrophic": {"score": 5, "description": "Critical impact on operations"}
            },
            "risk_matrix": {
                # Risk score = likelihood * impact
                (1, 5): RiskLevel.LOW,      # 1-5: Low
                (6, 10): RiskLevel.MEDIUM,  # 6-10: Medium
                (11, 15): RiskLevel.HIGH,   # 11-15: High
                (16, 25): RiskLevel.CRITICAL # 16-25: Critical
            }
        }
    
    def validate_user_input(self, user_input: str, context: Dict[str, Any] = None) -> List[ValidationResult]:
        """
        Comprehensive user input validation and sanitization.
        
        Args:
            user_input: Raw user input to validate
            context: Additional context for validation
            
        Returns:
            List of validation results
        """
        results = []
        
        try:
            # Length validation
            if len(user_input) > self.sanitization_rules["limit_length"]:
                results.append(ValidationResult(
                    category=ValidationCategory.SECURITY,
                    level=ValidationLevel.ERROR,
                    risk_level=RiskLevel.HIGH,
                    message="Input exceeds maximum allowed length",
                    description=f"Input length {len(user_input)} exceeds limit of {self.sanitization_rules['limit_length']}",
                    remediation="Reduce input length or split into multiple requests",
                    affected_components=["user_input"],
                    compliance_frameworks=["security_policy"],
                    references=["input_validation_policy"],
                    auto_fixable=True,
                    fix_command=f"truncate_input({self.sanitization_rules['limit_length']})"
                ))
            
            # Dangerous pattern detection
            for category, patterns in self.dangerous_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, user_input, re.IGNORECASE):
                        results.append(ValidationResult(
                            category=ValidationCategory.SECURITY,
                            level=ValidationLevel.CRITICAL,
                            risk_level=RiskLevel.CRITICAL,
                            message=f"Potentially dangerous {category} pattern detected",
                            description=f"Input contains pattern that may indicate {category} attempt",
                            remediation=f"Remove or sanitize {category} patterns from input",
                            affected_components=["user_input", "system_security"],
                            compliance_frameworks=["CIS", "NIST", "SOC2"],
                            references=[f"{category}_prevention_guide"],
                            auto_fixable=True,
                            fix_command=f"sanitize_{category}(input)"
                        ))
            
            # URL validation if URLs are present
            url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[^\s<>"\']{2,}'
            urls = re.findall(url_pattern, user_input, re.IGNORECASE)
            
            for url in urls:
                url_results = self._validate_url(url)
                results.extend(url_results)
            
            # File path validation
            file_patterns = [
                r'/[a-zA-Z0-9_./\-]+',
                r'[A-Z]:[\\\/][a-zA-Z0-9_\\\/\-]+',
                r'~[/\\][a-zA-Z0-9_/\\-]+'
            ]
            
            for pattern in file_patterns:
                paths = re.findall(pattern, user_input)
                for path in paths:
                    path_results = self._validate_file_path(path)
                    results.extend(path_results)
            
            # Encoding validation
            encoding_results = self._validate_encoding(user_input)
            results.extend(encoding_results)
            
            logger.info(
                "User input validation completed",
                input_length=len(user_input),
                issues_found=len(results),
                critical_issues=len([r for r in results if r.level == ValidationLevel.CRITICAL])
            )
            
        except Exception as e:
            logger.error("User input validation failed", error=str(e))
            results.append(ValidationResult(
                category=ValidationCategory.SYNTAX,
                level=ValidationLevel.ERROR,
                risk_level=RiskLevel.HIGH,
                message="Input validation failed",
                description=f"Validation error: {str(e)}",
                remediation="Review input format and content",
                affected_components=["validation_system"],
                compliance_frameworks=[],
                references=["validation_troubleshooting"],
                auto_fixable=False
            ))
        
        return results
    
    def _validate_url(self, url: str) -> List[ValidationResult]:
        """Validate URL for security issues."""
        results = []
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            # Protocol validation
            if parsed.scheme not in self.sanitization_rules["allowed_protocols"]:
                results.append(ValidationResult(
                    category=ValidationCategory.SECURITY,
                    level=ValidationLevel.WARNING,
                    risk_level=RiskLevel.MEDIUM,
                    message="Potentially unsafe URL protocol",
                    description=f"Protocol '{parsed.scheme}' not in allowed list",
                    remediation="Use approved protocols (http, https, ssh, ftp)",
                    affected_components=["url_validation"],
                    compliance_frameworks=["security_policy"],
                    references=["url_security_guide"],
                    auto_fixable=False
                ))
            
            # Private/internal network detection
            hostname = parsed.hostname or ""
            private_patterns = [
                r'^127\.',
                r'^10\.',
                r'^172\.(1[6-9]|2[0-9]|3[01])\.',
                r'^192\.168\.',
                r'^localhost$',
                r'^.*\.local$'
            ]
            
            for pattern in private_patterns:
                if re.match(pattern, hostname, re.IGNORECASE):
                    results.append(ValidationResult(
                        category=ValidationCategory.SECURITY,
                        level=ValidationLevel.WARNING,
                        risk_level=RiskLevel.MEDIUM,
                        message="URL points to private/internal network",
                        description=f"URL hostname '{hostname}' appears to be internal",
                        remediation="Verify if internal network access is intended",
                        affected_components=["network_security"],
                        compliance_frameworks=["network_security_policy"],
                        references=["internal_network_access_guide"],
                        auto_fixable=False
                    ))
            
        except Exception as e:
            results.append(ValidationResult(
                category=ValidationCategory.SYNTAX,
                level=ValidationLevel.ERROR,
                risk_level=RiskLevel.MEDIUM,
                message="URL parsing failed",
                description=f"Unable to parse URL: {str(e)}",
                remediation="Check URL format and syntax",
                affected_components=["url_validation"],
                compliance_frameworks=[],
                references=["url_format_guide"],
                auto_fixable=False
            ))
        
        return results
    
    def _validate_file_path(self, path: str) -> List[ValidationResult]:
        """Validate file path for security issues."""
        results = []
        
        # Path traversal detection
        dangerous_path_patterns = [
            r'\.\.',
            r'/etc/',
            r'/proc/',
            r'/sys/',
            r'\\windows\\',
            r'\\system32\\',
            r'/root/',
            r'~root/'
        ]
        
        for pattern in dangerous_path_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                results.append(ValidationResult(
                    category=ValidationCategory.SECURITY,
                    level=ValidationLevel.CRITICAL,
                    risk_level=RiskLevel.HIGH,
                    message="Potentially dangerous file path detected",
                    description=f"Path contains pattern that may indicate path traversal: {pattern}",
                    remediation="Use safe, relative paths within allowed directories",
                    affected_components=["file_system", "path_validation"],
                    compliance_frameworks=["CIS", "NIST"],
                    references=["path_traversal_prevention"],
                    auto_fixable=True,
                    fix_command="sanitize_path(path)"
                ))
        
        # File extension validation
        file_extension = Path(path).suffix.lower()
        if file_extension in self.sanitization_rules["blocked_extensions"]:
            results.append(ValidationResult(
                category=ValidationCategory.SECURITY,
                level=ValidationLevel.ERROR,
                risk_level=RiskLevel.HIGH,
                message="Potentially dangerous file extension",
                description=f"File extension '{file_extension}' is blocked for security",
                remediation="Use approved file types for configuration",
                affected_components=["file_validation"],
                compliance_frameworks=["security_policy"],
                references=["allowed_file_types"],
                auto_fixable=False
            ))
        
        return results
    
    def _validate_encoding(self, text: str) -> List[ValidationResult]:
        """Validate text encoding and detect potential encoding attacks."""
        results = []
        
        try:
            # Check for valid UTF-8 encoding
            text.encode('utf-8')
            
            # Detect potential encoding attacks
            suspicious_encodings = [
                r'%[0-9a-fA-F]{2}',  # URL encoding
                r'&#[0-9]+;',        # HTML entity encoding
                r'\\u[0-9a-fA-F]{4}', # Unicode escape sequences
                r'\\x[0-9a-fA-F]{2}', # Hex escape sequences
                r'\\[0-7]{3}'        # Octal escape sequences
            ]
            
            for pattern in suspicious_encodings:
                if re.search(pattern, text):
                    results.append(ValidationResult(
                        category=ValidationCategory.SECURITY,
                        level=ValidationLevel.WARNING,
                        risk_level=RiskLevel.MEDIUM,
                        message="Suspicious encoding detected",
                        description=f"Text contains encoded characters that may bypass filters",
                        remediation="Decode and validate encoded content",
                        affected_components=["input_validation"],
                        compliance_frameworks=["input_validation_policy"],
                        references=["encoding_security_guide"],
                        auto_fixable=True,
                        fix_command="decode_and_validate(text)"
                    ))
                    break  # Only report once per input
            
        except UnicodeEncodeError as e:
            results.append(ValidationResult(
                category=ValidationCategory.SYNTAX,
                level=ValidationLevel.ERROR,
                risk_level=RiskLevel.MEDIUM,
                message="Invalid text encoding",
                description=f"Text contains invalid UTF-8 characters: {str(e)}",
                remediation="Ensure text uses valid UTF-8 encoding",
                affected_components=["encoding_validation"],
                compliance_frameworks=[],
                references=["encoding_troubleshooting"],
                auto_fixable=True,
                fix_command="fix_encoding(text)"
            ))
        
        return results
    
    def validate_infrastructure_config(
        self,
        config: Union[str, Dict[str, Any]],
        config_type: str,
        domain: TechnicalDomain
    ) -> List[ValidationResult]:
        """
        Validate infrastructure configuration for security and best practices.
        
        Args:
            config: Configuration content (JSON, YAML, or HCL string, or dict)
            config_type: Type of configuration (terraform, ansible, docker, etc.)
            domain: Technical domain for context-specific validation
            
        Returns:
            List of validation results
        """
        results = []
        
        try:
          # Parse configuration if it's a string
            parsed_config = self._parse_config(config, config_type)
            
            # Get appropriate validator
            validator_key = self._get_validator_key(config_type, domain)
            if validator_key not in self.config_validators:
                results.append(ValidationResult(
                    category=ValidationCategory.LOGIC,
                    level=ValidationLevel.WARNING,
                    risk_level=RiskLevel.LOW,
                    message=f"No specific validator for {config_type}",
                    description="Generic validation will be applied",
                    remediation="Consider adding specific validator for this configuration type",
                    affected_components=["validation_system"],
                    compliance_frameworks=[],
                    references=["validator_development_guide"],
                    auto_fixable=False
                ))
                validator_config = {}
            else:
                validator_config = self.config_validators[validator_key]
            
            # Perform domain-specific validation
            domain_results = self._validate_by_domain(parsed_config, domain, validator_config)
            results.extend(domain_results)
            
            # Security validation
            security_results = self._validate_security_config(parsed_config, config_type)
            results.extend(security_results)
            
            # Best practices validation
            best_practices_results = self._validate_best_practices(parsed_config, config_type, domain)
            results.extend(best_practices_results)
            
            # Compliance validation
            compliance_results = self._validate_compliance(parsed_config, config_type)
            results.extend(compliance_results)
            
            logger.info(
                "Infrastructure config validation completed",
                config_type=config_type,
                domain=domain.value,
                issues_found=len(results),
                critical_issues=len([r for r in results if r.level == ValidationLevel.CRITICAL])
            )
            
        except Exception as e:
            logger.error("Infrastructure config validation failed", error=str(e))
            results.append(ValidationResult(
                category=ValidationCategory.SYNTAX,
                level=ValidationLevel.ERROR,
                risk_level=RiskLevel.HIGH,
                message="Configuration validation failed",
                description=f"Validation error: {str(e)}",
                remediation="Check configuration syntax and format",
                affected_components=["config_validation"],
                compliance_frameworks=[],
                references=["config_troubleshooting"],
                auto_fixable=False
            ))
        
        return results
    
    def _parse_config(self, config: Union[str, Dict], config_type: str) -> Dict[str, Any]:
        """Parse configuration string into dictionary."""
        if isinstance(config, dict):
            return config
        
        if isinstance(config, str):
            # Try JSON first
            try:
                return json.loads(config)
            except json.JSONDecodeError:
                pass
            
            # Try YAML
            try:
                return yaml.safe_load(config)
            except yaml.YAMLError:
                pass
            
            # For HCL (Terraform), we'd need a specific parser
            # For now, return a structured representation
            if config_type.lower() in ['terraform', 'hcl']:
                return {"raw_hcl": config, "parsed": False}
        
        # If all parsing fails, return raw content
        return {"raw_content": str(config), "parsed": False}
    
    def _get_validator_key(self, config_type: str, domain: TechnicalDomain) -> str:
        """Get appropriate validator key based on config type and domain."""
        config_type_lower = config_type.lower()
        
        # Direct mapping
        if config_type_lower in self.config_validators:
            return config_type_lower
        
        # Domain-based mapping
        domain_mapping = {
            TechnicalDomain.VIRTUALIZATION: "proxmox",
            TechnicalDomain.INFRASTRUCTURE_AS_CODE: "terraform",
            TechnicalDomain.CONTAINERIZATION: "docker",
            TechnicalDomain.CLOUD_COMPUTING: "terraform"
        }
        
        return domain_mapping.get(domain, "generic")
    
    def _validate_by_domain(
        self,
        config: Dict[str, Any],
        domain: TechnicalDomain,
        validator_config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Perform domain-specific validation."""
        results = []
        
        if domain == TechnicalDomain.VIRTUALIZATION:
            results.extend(self._validate_virtualization_config(config, validator_config))
        elif domain == TechnicalDomain.INFRASTRUCTURE_AS_CODE:
            results.extend(self._validate_iac_config(config, validator_config))
        elif domain == TechnicalDomain.CONTAINERIZATION:
            results.extend(self._validate_container_config(config, validator_config))
        elif domain == TechnicalDomain.CLOUD_COMPUTING:
            results.extend(self._validate_cloud_config(config, validator_config))
        
        return results
    
    def _validate_virtualization_config(
        self,
        config: Dict[str, Any],
        validator_config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate virtualization (Proxmox) configuration."""
        results = []
        
        # VM configuration validation
        if "vm_config" in validator_config and any(key in config for key in ["memory", "cores", "name"]):
            vm_validator = validator_config["vm_config"]
            
            # Required fields check
            for field in vm_validator.get("required_fields", []):
                if field not in config:
                    results.append(ValidationResult(
                        category=ValidationCategory.LOGIC,
                        level=ValidationLevel.ERROR,
                        risk_level=RiskLevel.MEDIUM,
                        message=f"Missing required VM configuration field: {field}",
                        description=f"VM configuration must include {field}",
                        remediation=f"Add {field} to VM configuration",
                        affected_components=["vm_config"],
                        compliance_frameworks=["best_practices"],
                        references=["vm_config_guide"],
                        auto_fixable=True,
                        fix_command=f"add_required_field('{field}')"
                    ))
            
            # Memory validation
            if "memory" in config:
                memory = config["memory"]
                limits = vm_validator.get("memory_limits", {})
                
                if memory < limits.get("min", 0):
                    results.append(ValidationResult(
                        category=ValidationCategory.PERFORMANCE,
                        level=ValidationLevel.WARNING,
                        risk_level=RiskLevel.LOW,
                        message="VM memory below recommended minimum",
                        description=f"Memory {memory}MB is below minimum {limits.get('min', 0)}MB",
                        remediation=f"Increase memory to at least {limits.get('min', 512)}MB",
                        affected_components=["vm_performance"],
                        compliance_frameworks=["performance_guidelines"],
                        references=["vm_sizing_guide"],
                        auto_fixable=True,
                        fix_command=f"set_memory({limits.get('min', 512)})"
                    ))
                
                if memory > limits.get("max", 999999):
                    results.append(ValidationResult(
                        category=ValidationCategory.PERFORMANCE,
                        level=ValidationLevel.WARNING,
                        risk_level=RiskLevel.LOW,
                        message="VM memory exceeds recommended maximum",
                        description=f"Memory {memory}MB exceeds maximum {limits.get('max', 131072)}MB",
                        remediation="Verify high memory requirement is necessary",
                        affected_components=["resource_management"],
                        compliance_frameworks=["resource_policy"],
                        references=["resource_planning_guide"],
                        auto_fixable=False
                    ))
            
            # Security requirements check
            security_reqs = vm_validator.get("security_requirements", [])
            for requirement in security_reqs:
                if requirement == "agent_enabled" and config.get("agent") != "1":
                    results.append(ValidationResult(
                        category=ValidationCategory.SECURITY,
                        level=ValidationLevel.WARNING,
                        risk_level=RiskLevel.MEDIUM,
                        message="QEMU guest agent not enabled",
                        description="Guest agent provides enhanced VM management capabilities",
                        remediation="Enable guest agent by setting 'agent: 1'",
                        affected_components=["vm_management"],
                        compliance_frameworks=["CIS"],
                        references=["guest_agent_guide"],
                        auto_fixable=True,
                        fix_command="enable_guest_agent()"
                    ))
        
        return results
    
    def _validate_iac_config(
        self,
        config: Dict[str, Any],
        validator_config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate Infrastructure as Code configuration."""
        results = []
        
        # Check for hardcoded secrets (common patterns)
        config_str = json.dumps(config, default=str).lower()
        secret_patterns = [
            r'password\s*[=:]\s*["\'][^"\']+["\']',
            r'secret\s*[=:]\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*[=:]\s*["\'][^"\']+["\']',
            r'access[_-]?key\s*[=:]\s*["\'][^"\']+["\']',
            r'private[_-]?key\s*[=:]\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, config_str, re.IGNORECASE):
                results.append(ValidationResult(
                    category=ValidationCategory.SECURITY,
                    level=ValidationLevel.CRITICAL,
                    risk_level=RiskLevel.CRITICAL,
                    message="Hardcoded secrets detected in configuration",
                    description="Configuration contains what appears to be hardcoded credentials",
                    remediation="Use secure secret management (Vault, encrypted variables, etc.)",
                    affected_components=["secret_management"],
                    compliance_frameworks=["CIS", "NIST", "SOC2"],
                    references=["secret_management_guide"],
                    auto_fixable=False
                ))
                break  # Only report once
        
        return results
    
    def _validate_container_config(
        self,
        config: Dict[str, Any],
        validator_config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate container configuration."""
        results = []
        
        # Check for running as root
        if "user" in config and config["user"] in ["root", "0", 0]:
            results.append(ValidationResult(
                category=ValidationCategory.SECURITY,
                level=ValidationLevel.WARNING,
                risk_level=RiskLevel.HIGH,
                message="Container configured to run as root",
                description="Running containers as root increases security risk",
                remediation="Create and use a non-root user for container execution",
                affected_components=["container_security"],
                compliance_frameworks=["CIS", "Docker_Bench"],
                references=["container_security_guide"],
                auto_fixable=True,
                fix_command="create_nonroot_user()"
            ))
        
        # Check for resource limits
        if "services" in config:  # Docker Compose
            for service_name, service_config in config["services"].items():
                if "deploy" not in service_config or "resources" not in service_config["deploy"]:
                    results.append(ValidationResult(
                        category=ValidationCategory.PERFORMANCE,
                        level=ValidationLevel.WARNING,
                        risk_level=RiskLevel.MEDIUM,
                        message=f"No resource limits defined for service {service_name}",
                        description="Services without resource limits can consume all available resources",
                        remediation="Define CPU and memory limits for all services",
                        affected_components=["resource_management"],
                        compliance_frameworks=["best_practices"],
                        references=["resource_limits_guide"],
                        auto_fixable=True,
                        fix_command=f"add_resource_limits('{service_name}')"
                    ))
        
        return results
    
    def _validate_cloud_config(
        self,
        config: Dict[str, Any],
        validator_config: Dict[str, Any]
    ) -> List[ValidationResult]:
        """Validate cloud configuration."""
        results = []
        
        # This would contain cloud-specific validation logic
        # For brevity, adding a placeholder
        
        return results
    
    def _validate_security_config(
        self,
        config: Dict[str, Any],
        config_type: str
    ) -> List[ValidationResult]:
        """Validate security aspects of configuration."""
        results = []
        
        # Check encryption settings
        config_str = str(config).lower()
        
        if "encrypt" not in config_str and "tls" not in config_str and "ssl" not in config_str:
            results.append(ValidationResult(
                category=ValidationCategory.SECURITY,
                level=ValidationLevel.WARNING,
                risk_level=RiskLevel.MEDIUM,
                message="No encryption configuration detected",
                description="Configuration does not appear to include encryption settings",
                remediation="Enable encryption for data at rest and in transit",
                affected_components=["data_protection"],
                compliance_frameworks=["NIST", "SOC2", "ISO27001"],
                references=["encryption_guide"],
                auto_fixable=False
            ))
        
        return results
    
    def _validate_best_practices(
        self,
        config: Dict[str, Any],
        config_type: str,
        domain: TechnicalDomain
    ) -> List[ValidationResult]:
        """Validate against best practices."""
        results = []
        
        # Get best practices from knowledge base
        try:
            from .knowledge_base import KnowledgeContext, ExpertiseLevel
            
            knowledge_context = KnowledgeContext(
                domain=domain,
                expertise_level=ExpertiseLevel.EXPERT,
                specific_technologies=[config_type],
                use_case="validation",
                security_requirements="high",
                compliance_needs=["CIS", "NIST"]
            )
            
            domain_knowledge = technical_knowledge_base.get_domain_knowledge(knowledge_context)
            
            # Extract best practices and check against config
            for topic, knowledge in domain_knowledge.items():
                if "best_practices" in knowledge:
                    practices = knowledge["best_practices"]
                    # This would contain specific logic to check practices
                    # against the configuration
                    pass
            
        except Exception as e:
            logger.debug("Could not load best practices from knowledge base", error=str(e))
        
        return results
    
    def _validate_compliance(
        self,
        config: Dict[str, Any],
        config_type: str
    ) -> List[ValidationResult]:
        """Validate against compliance frameworks."""
        results = []
        
        # This would contain specific compliance validation logic
        # For now, adding basic compliance checks
        
        return results
    
    def assess_security_posture(
        self,
        configurations: List[Dict[str, Any]],
        environment_type: str = "production"
    ) -> SecurityAssessment:
        """
        Perform comprehensive security assessment.
        
        Args:
            configurations: List of configuration objects to assess
            environment_type: Environment type (production, staging, development)
            
        Returns:
            Comprehensive security assessment
        """
        all_results = []
        
        # Validate all configurations
        for i, config in enumerate(configurations):
            config_type = config.get("type", "unknown")
            domain = TechnicalDomain(config.get("domain", "system_engineering"))
            
            config_results = self.validate_infrastructure_config(
                config.get("content", {}),
                config_type,
                domain
            )
            all_results.extend(config_results)
        
        # Categorize issues by severity
        critical_issues = [r for r in all_results if r.level == ValidationLevel.CRITICAL]
        high_risk_issues = [r for r in all_results if r.risk_level == RiskLevel.HIGH]
        medium_risk_issues = [r for r in all_results if r.risk_level == RiskLevel.MEDIUM]
        
        # Calculate overall security score (0-100)
        total_issues = len(all_results)
        if total_issues == 0:
            overall_score = 100.0
            overall_risk = RiskLevel.LOW
        else:
            # Weight issues by severity
            severity_weights = {
                ValidationLevel.CRITICAL: 10,
                ValidationLevel.ERROR: 5,
                ValidationLevel.WARNING: 2,
                ValidationLevel.INFO: 1
            }
            
            weighted_score = sum(severity_weights.get(r.level, 1) for r in all_results)
            max_possible_score = total_issues * 10  # If all were critical
            
            overall_score = max(0, 100 - (weighted_score / max_possible_score * 100))
            
            if len(critical_issues) > 0:
                overall_risk = RiskLevel.CRITICAL
            elif len(high_risk_issues) > 2:
                overall_risk = RiskLevel.HIGH
            elif len(medium_risk_issues) > 5:
                overall_risk = RiskLevel.MEDIUM
            else:
                overall_risk = RiskLevel.LOW
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations(all_results)
        
        # Check compliance status
        compliance_status = self._assess_compliance_status(all_results)
        
        # Identify threat vectors
        threat_vectors = self._identify_threat_vectors(all_results)
        
        assessment = SecurityAssessment(
            overall_score=overall_score,
            risk_level=overall_risk,
            critical_issues=critical_issues,
            high_risk_issues=high_risk_issues,
            medium_risk_issues=medium_risk_issues,
            recommendations=recommendations,
            compliance_status=compliance_status,
            threat_vectors=threat_vectors
        )
        
        logger.info(
            "Security assessment completed",
            overall_score=overall_score,
            risk_level=overall_risk.value,
            total_issues=total_issues,
            critical_issues=len(critical_issues)
        )
        
        return assessment
    
    def _generate_security_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate prioritized security recommendations."""
        recommendations = []
        
        # Group by category
        categories = {}
        for result in results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # Generate recommendations for each category
        for category, category_results in categories.items():
            if category == ValidationCategory.SECURITY:
                recommendations.append(
                    f"Address {len(category_results)} security issues, prioritizing critical and high-risk items"
                )
            elif category == ValidationCategory.COMPLIANCE:
                recommendations.append(
                    f"Review and remediate {len(category_results)} compliance violations"
                )
            elif category == ValidationCategory.BEST_PRACTICES:
                recommendations.append(
                    f"Implement {len(category_results)} best practice improvements"
                )
        
        # Add general recommendations
        if any(r.level == ValidationLevel.CRITICAL for r in results):
            recommendations.insert(0, "IMMEDIATE ACTION REQUIRED: Address all critical security issues")
        
        recommendations.extend([
            "Implement continuous security monitoring and validation",
            "Regular security assessments and penetration testing",
            "Security awareness training for all team members",
            "Establish incident response procedures",
            "Implement automated security scanning in CI/CD pipelines"
        ])
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _assess_compliance_status(self, results: List[ValidationResult]) -> Dict[str, bool]:
        """Assess compliance status for various frameworks."""
        compliance_status = {}
        
        # Initialize all frameworks as compliant
        for framework in ["CIS", "NIST", "SOC2", "ISO27001"]:
            compliance_status[framework] = True
        
        # Check for violations
        for result in results:
            for framework in result.compliance_frameworks:
                if framework in compliance_status and result.level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR]:
                    compliance_status[framework] = False
        
        return compliance_status
    
    def _identify_threat_vectors(self, results: List[ValidationResult]) -> List[str]:
        """Identify potential threat vectors from validation results."""
        threat_vectors = set()
        
        for result in results:
            if result.category == ValidationCategory.SECURITY:
                if "injection" in result.message.lower():
                    threat_vectors.add("Code/Command Injection")
                elif "authentication" in result.message.lower():
                    threat_vectors.add("Authentication Bypass")
                elif "encryption" in result.message.lower():
                    threat_vectors.add("Data Interception")
                elif "access" in result.message.lower():
                    threat_vectors.add("Unauthorized Access")
                elif "network" in result.message.lower():
                    threat_vectors.add("Network Attacks")
                elif "privilege" in result.message.lower():
                    threat_vectors.add("Privilege Escalation")
                else:
                    threat_vectors.add("General Security Risk")
        
        return list(threat_vectors)


# Global validation framework instance
validation_framework = TechnicalValidationFramework()