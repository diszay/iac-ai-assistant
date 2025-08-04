"""
Advanced Technical Knowledge Base for Proxmox AI Assistant.

Provides comprehensive domain-specific knowledge and expertise across:
- Virtualization & Proxmox (VMware, KVM, QEMU, containers, hypervisors)
- Infrastructure as Code (Terraform, Ansible, Pulumi, CloudFormation)
- Containerization (Docker, Kubernetes, microservices, service mesh)
- System Engineering (Linux administration, networking, security)
- Cloud Computing (AWS, Azure, GCP, multi-cloud, serverless)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class TechnicalDomain(Enum):
    """Technical knowledge domains."""
    VIRTUALIZATION = "virtualization"
    INFRASTRUCTURE_AS_CODE = "infrastructure_as_code"
    CONTAINERIZATION = "containerization"
    SYSTEM_ENGINEERING = "system_engineering"
    CLOUD_COMPUTING = "cloud_computing"
    NETWORKING = "networking"
    SECURITY = "security"
    MONITORING = "monitoring"
    DATABASE = "database"
    AUTOMATION = "automation"


class ExpertiseLevel(Enum):
    """Expertise levels for responses."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


@dataclass
class KnowledgeContext:
    """Context information for knowledge retrieval."""
    domain: TechnicalDomain
    expertise_level: ExpertiseLevel
    specific_technologies: List[str]
    use_case: str
    security_requirements: str
    compliance_needs: List[str]


@dataclass
class TechnicalKnowledge:
    """Technical knowledge entry."""
    domain: TechnicalDomain
    topic: str
    technologies: List[str]
    concepts: Dict[str, str]
    best_practices: List[str]
    security_considerations: List[str]
    common_patterns: Dict[str, str]
    troubleshooting_guides: Dict[str, str]
    expert_tips: List[str]
    related_topics: List[str]


class TechnicalKnowledgeBase:
    """
    Comprehensive technical knowledge base with domain expertise.
    
    Features:
    - Domain-specific knowledge repositories
    - Expertise-level appropriate responses
    - Security-first recommendations
    - Best practices and patterns
    - Troubleshooting guides
    - Technology cross-references
    """
    
    def __init__(self):
        """Initialize the technical knowledge base."""
        self.knowledge_db: Dict[TechnicalDomain, Dict[str, TechnicalKnowledge]] = {}
        self.technology_index: Dict[str, List[Tuple[TechnicalDomain, str]]] = {}
        self.pattern_index: Dict[str, List[str]] = {}
        
        self._initialize_knowledge_base()
        logger.info("Technical knowledge base initialized")
    
    def _initialize_knowledge_base(self):
        """Initialize comprehensive technical knowledge base."""
        
        # Virtualization & Proxmox Knowledge
        self._load_virtualization_knowledge()
        
        # Infrastructure as Code Knowledge
        self._load_iac_knowledge()
        
        # Containerization Knowledge
        self._load_containerization_knowledge()
        
        # System Engineering Knowledge
        self._load_system_engineering_knowledge()
        
        # Cloud Computing Knowledge
        self._load_cloud_computing_knowledge()
        
        # Security Knowledge
        self._load_security_knowledge()
        
        # Networking Knowledge
        self._load_networking_knowledge()
        
        # Monitoring & Observability Knowledge
        self._load_monitoring_knowledge()
        
        # Build technology and pattern indices
        self._build_indices()
    
    def _load_virtualization_knowledge(self):
        """Load virtualization and Proxmox knowledge."""
        virtualization_knowledge = {
            "proxmox_fundamentals": TechnicalKnowledge(
                domain=TechnicalDomain.VIRTUALIZATION,
                topic="Proxmox VE Fundamentals",
                technologies=["Proxmox VE", "KVM", "QEMU", "LXC"],
                concepts={
                    "hypervisor": "Type-1 bare-metal hypervisor built on Debian Linux",
                    "kvm": "Kernel-based Virtual Machine for hardware-assisted virtualization",
                    "qemu": "Quick Emulator for virtual machine management and hardware emulation",
                    "lxc": "Linux Containers for OS-level virtualization",
                    "cluster": "Multiple Proxmox nodes working together for HA and load distribution",
                    "storage": "Shared storage systems (Ceph, ZFS, NFS, iSCSI) for VM data"
                },
                best_practices=[
                    "Always use dedicated network for cluster communication",
                    "Implement shared storage for live migration capabilities",
                    "Configure proper backup strategies with PBS or external tools",
                    "Use resource pools for organized resource management",
                    "Enable HA for critical VMs with proper fencing",
                    "Regular cluster and VM backups to prevent data loss",
                    "Monitor resource usage and set appropriate limits",
                    "Use templates for consistent VM deployment"
                ],
                security_considerations=[
                    "Separate management network from production traffic",
                    "Enable two-factor authentication for web interface",
                    "Use proper SSL certificates for HTTPS access",
                    "Implement firewall rules at host and VM level",
                    "Regular security updates for Proxmox and guest systems",
                    "Restrict API access with proper user permissions",
                    "Audit user activities and access logs",
                    "Secure storage communication with encryption"
                ],
                common_patterns={
                    "vm_template_workflow": "Create base VM → Install OS → Configure → Convert to template → Clone for deployment",
                    "cluster_setup": "Install Proxmox → Configure network → Create cluster → Join nodes → Setup shared storage",
                    "backup_strategy": "Daily incremental backups → Weekly full backups → Offsite storage → Test restore procedures",
                    "ha_configuration": "Cluster setup → Shared storage → Fencing configuration → HA resource groups"
                },
                troubleshooting_guides={
                    "vm_wont_start": "Check: Resource availability → Storage accessibility → Network configuration → VM settings → Host status",
                    "cluster_split_brain": "Verify: Network connectivity → Quorum status → Fencing configuration → Time synchronization",
                    "storage_issues": "Diagnose: Storage backend health → Network connectivity → Permission issues → Disk space",
                    "performance_degradation": "Monitor: CPU usage → Memory pressure → Storage I/O → Network bottlenecks"
                },
                expert_tips=[
                    "Use ZFS with proper arc_max settings for optimal memory usage",
                    "Configure CPU affinity for performance-critical VMs",
                    "Implement custom hooks for advanced automation",
                    "Use PCI passthrough for GPU or high-performance network cards",
                    "Optimize VM memory with ballooning and KSM",
                    "Use SPICE or noVNC with proper security settings"
                ],
                related_topics=[
                    "vmware_migration", "hyper_v_comparison", "openstack_integration",
                    "kubernetes_virtualization", "storage_optimization"
                ]
            ),
            
            "vm_lifecycle_management": TechnicalKnowledge(
                domain=TechnicalDomain.VIRTUALIZATION,
                topic="VM Lifecycle Management",
                technologies=["Proxmox VE", "Cloud-init", "Ansible", "Terraform"],
                concepts={
                    "vm_lifecycle": "Planning → Provisioning → Configuration → Deployment → Monitoring → Maintenance → Decommission",
                    "cloud_init": "Industry-standard method for VM initialization and configuration",
                    "templates": "Golden images for consistent and rapid VM deployment",
                    "snapshots": "Point-in-time VM state capture for backup and testing",
                    "migration": "Moving VMs between hosts for maintenance or load balancing"
                },
                best_practices=[
                    "Use cloud-init for automated VM initialization",
                    "Create standardized templates for different OS types",
                    "Implement proper naming conventions for VMs and resources",
                    "Use tags for VM organization and automated management",
                    "Regular snapshot management with retention policies",
                    "Document VM configurations and dependencies",
                    "Implement automated patching and updates",
                    "Use configuration management tools for consistency"
                ],
                security_considerations=[
                    "Harden VM templates before deployment",
                    "Use unique SSH keys for each VM instance",
                    "Implement proper user access controls",
                    "Regular security scanning of VM images",
                    "Secure VM communication with VPNs or VLANs",
                    "Monitor VM activities for anomalies"
                ],
                common_patterns={
                    "template_creation": "Base OS install → Security hardening → Software installation → Sysprep/generalize → Template conversion",
                    "automated_deployment": "Template selection → Variable definition → Cloud-init configuration → Provisioning → Post-deployment validation"
                },
                troubleshooting_guides={
                    "cloud_init_failure": "Check: Configuration syntax → Network connectivity → Package repositories → Log files",
                    "template_issues": "Verify: Template integrity → Storage accessibility → Configuration settings → Permissions"
                },
                expert_tips=[
                    "Use Packer for automated template building",
                    "Implement VM scheduling for cost optimization",
                    "Use Ansible dynamic inventory for VM management"
                ],
                related_topics=["automation", "configuration_management", "infrastructure_as_code"]
            ),
            
            "storage_and_networking": TechnicalKnowledge(
                domain=TechnicalDomain.VIRTUALIZATION,
                topic="Storage and Networking",
                technologies=["ZFS", "Ceph", "NFS", "iSCSI", "Open vSwitch", "Linux Bridge"],
                concepts={
                    "storage_types": "Local storage (ZFS, LVM) vs Shared storage (Ceph, NFS, iSCSI)",
                    "network_models": "Linux Bridge vs Open vSwitch for different use cases",
                    "vlans": "Virtual LANs for network segmentation and security",
                    "bonding": "Network interface aggregation for redundancy and bandwidth"
                },
                best_practices=[
                    "Use ZFS for local storage with proper dataset configuration",
                    "Implement Ceph for distributed storage with proper replica settings",
                    "Configure multiple network interfaces for different traffic types",
                    "Use VLANs for network segmentation and security",
                    "Implement network bonding for high availability",
                    "Monitor storage and network performance regularly"
                ],
                security_considerations=[
                    "Encrypt storage communications and data at rest",
                    "Implement network segmentation for isolation",
                    "Use proper firewall rules for storage traffic",
                    "Secure NFS and iSCSI communications"
                ],
                common_patterns={
                    "ceph_setup": "Node preparation → OSD creation → Pool configuration → RBD/CephFS setup",
                    "network_segregation": "Management VLAN → Storage VLAN → VM traffic VLAN → Backup VLAN"
                },
                troubleshooting_guides={
                    "storage_performance": "Monitor: Disk I/O → Network latency → CPU usage → Memory pressure",
                    "network_connectivity": "Check: Cable connections → Switch configuration → VLAN settings → Firewall rules"
                },
                expert_tips=[
                    "Use dedicated SSDs for Ceph journal/WAL devices",
                    "Implement proper network QoS for different traffic types",
                    "Use SR-IOV for high-performance network virtualization"
                ],
                related_topics=["backup_strategies", "disaster_recovery", "performance_tuning"]
            )
        }
        
        self.knowledge_db[TechnicalDomain.VIRTUALIZATION] = virtualization_knowledge
    
    def _load_iac_knowledge(self):
        """Load Infrastructure as Code knowledge."""
        iac_knowledge = {
            "terraform_fundamentals": TechnicalKnowledge(
                domain=TechnicalDomain.INFRASTRUCTURE_AS_CODE,
                topic="Terraform Fundamentals",
                technologies=["Terraform", "HCL", "Proxmox Provider", "Cloud Providers"],
                concepts={
                    "declarative_infrastructure": "Define desired state and let Terraform manage the implementation",
                    "state_management": "Terraform state tracks real-world resource mappings",
                    "providers": "Plugins that interface with APIs of infrastructure platforms",
                    "modules": "Reusable Terraform configurations for common patterns",
                    "workspaces": "Multiple named states within single configuration"
                },
                best_practices=[
                    "Use remote state backend with locking mechanism",
                    "Implement proper variable management with tfvars files",
                    "Use modules for reusable infrastructure components",
                    "Version control all Terraform configurations",
                    "Implement proper naming conventions and tagging",
                    "Use terraform plan before apply for change validation",
                    "Implement automated testing with tools like Terratest",
                    "Use workspaces for environment separation"
                ],
                security_considerations=[
                    "Store sensitive variables in secure backends (Vault, AWS Secrets Manager)",
                    "Use least-privilege IAM policies for Terraform execution",
                    "Encrypt state files and use secure state backends",
                    "Implement proper access controls for Terraform Cloud/Enterprise",
                    "Regular security scanning of Terraform configurations",
                    "Use terraform validate and security linting tools"
                ],
                common_patterns={
                    "proxmox_vm_pattern": "Provider configuration → Variable definitions → VM resources → Output values",
                    "multi_environment": "Workspace per environment → Environment-specific tfvars → Shared modules",
                    "module_structure": "Variables.tf → Main.tf → Outputs.tf → README.md → Examples/"
                },
                troubleshooting_guides={
                    "state_lock_issues": "Check: Backend connectivity → Lock file status → Process conflicts → Permissions",
                    "provider_errors": "Verify: Provider version compatibility → API credentials → Network connectivity → Resource quotas",
                    "plan_apply_drift": "Investigate: Manual changes → Resource dependencies → State corruption → Provider bugs"
                },
                expert_tips=[
                    "Use terraform-docs for automatic documentation generation",
                    "Implement pre-commit hooks for code quality",
                    "Use dynamic blocks for conditional resource creation",
                    "Implement custom providers for specialized resources",
                    "Use terraform import for existing infrastructure adoption"
                ],
                related_topics=["ansible_integration", "cicd_pipelines", "gitops_workflows"]
            ),
            
            "ansible_automation": TechnicalKnowledge(
                domain=TechnicalDomain.INFRASTRUCTURE_AS_CODE,
                topic="Ansible Automation",
                technologies=["Ansible", "YAML", "Jinja2", "Python", "SSH"],
                concepts={
                    "playbooks": "YAML files describing automation tasks and their execution order",
                    "inventory": "List of managed hosts and their groupings",
                    "roles": "Reusable collections of tasks, variables, and templates",
                    "handlers": "Tasks triggered by notifications for service management",
                    "vault": "Encrypted storage for sensitive data like passwords and keys"
                },
                best_practices=[
                    "Use roles for modular and reusable automation",
                    "Implement proper inventory management with groups",
                    "Use Ansible Vault for sensitive data encryption",
                    "Write idempotent tasks that can run safely multiple times",
                    "Use meaningful task names and comments",
                    "Implement proper error handling and rollback strategies",
                    "Use tags for selective task execution",
                    "Test playbooks in staging before production"
                ],
                security_considerations=[
                    "Use SSH key-based authentication instead of passwords",
                    "Implement proper sudo/become privilege escalation",
                    "Use Ansible Vault for all sensitive variables",
                    "Limit SSH access and use jump hosts where needed",
                    "Regular rotation of SSH keys and vault passwords",
                    "Audit playbook execution logs for security events"
                ],
                common_patterns={
                    "web_server_setup": "Package installation → Configuration templating → Service management → Firewall rules",
                    "security_hardening": "User management → SSH configuration → Firewall setup → System updates",
                    "application_deployment": "Code checkout → Dependencies → Configuration → Service restart → Health checks"
                },
                troubleshooting_guides={
                    "connection_failures": "Check: SSH connectivity → Host keys → Authentication → Network routing",
                    "task_failures": "Debug: Task syntax → Variable values → Target system state → Permission issues",
                    "performance_issues": "Optimize: Parallel execution → Task efficiency → Inventory size → Network latency"
                },
                expert_tips=[
                    "Use ansible-lint for playbook quality checking",
                    "Implement dynamic inventory for cloud environments",
                    "Use callback plugins for integration with monitoring systems",
                    "Develop custom modules for specialized tasks",
                    "Use Ansible AWX/Tower for enterprise automation workflows"
                ],
                related_topics=["configuration_management", "cicd_integration", "infrastructure_testing"]
            ),
            
            "gitops_and_cicd": TechnicalKnowledge(
                domain=TechnicalDomain.INFRASTRUCTURE_AS_CODE,
                topic="GitOps and CI/CD",
                technologies=["Git", "GitLab CI", "GitHub Actions", "Jenkins", "ArgoCD", "Flux"],
                concepts={
                    "gitops": "Using Git as single source of truth for infrastructure and applications",
                    "infrastructure_pipeline": "Automated testing, validation, and deployment of infrastructure changes",
                    "policy_as_code": "Infrastructure policies defined and enforced through code",
                    "continuous_compliance": "Automated compliance checking throughout the pipeline"
                },
                best_practices=[
                    "Use feature branches for infrastructure changes",
                    "Implement automated testing at multiple pipeline stages",
                    "Use semantic versioning for infrastructure releases",
                    "Implement proper code review processes",
                    "Use environment promotion strategies",
                    "Implement automated rollback mechanisms",
                    "Monitor infrastructure changes and their impacts"
                ],
                security_considerations=[
                    "Use signed commits for authenticity",
                    "Implement branch protection rules",
                    "Use least-privilege service accounts for pipeline execution",
                    "Scan infrastructure code for security vulnerabilities",
                    "Implement secrets management in CI/CD pipelines"
                ],
                common_patterns={
                    "infrastructure_pipeline": "Code commit → Validation → Testing → Security scan → Deployment → Monitoring",
                    "environment_promotion": "Development → Staging → Production with approval gates"
                },
                troubleshooting_guides={
                    "pipeline_failures": "Check: Code syntax → Dependencies → Credentials → Resource limits",
                    "deployment_issues": "Verify: Target environment → Permissions → Network connectivity → Resource conflicts"
                },
                expert_tips=[
                    "Use infrastructure testing frameworks like Terratest or InSpec",
                    "Implement drift detection and remediation",
                    "Use policy engines like Open Policy Agent for governance"
                ],
                related_topics=["security_scanning", "compliance_automation", "monitoring_integration"]
            )
        }
        
        self.knowledge_db[TechnicalDomain.INFRASTRUCTURE_AS_CODE] = iac_knowledge
    
    def _load_containerization_knowledge(self):
        """Load containerization and orchestration knowledge."""
        containerization_knowledge = {
            "docker_fundamentals": TechnicalKnowledge(
                domain=TechnicalDomain.CONTAINERIZATION,
                topic="Docker Fundamentals",
                technologies=["Docker", "Docker Compose", "Dockerfile", "Docker Registry"],
                concepts={
                    "containers": "Lightweight, portable application packaging using OS-level virtualization",
                    "images": "Read-only templates used to create containers",
                    "dockerfile": "Text file with instructions to build Docker images",
                    "registry": "Centralized storage and distribution system for Docker images",
                    "volumes": "Persistent data storage mechanism for containers"
                },
                best_practices=[
                    "Use multi-stage builds to minimize image sizes",
                    "Implement proper layer caching strategies",
                    "Use specific version tags instead of 'latest'",
                    "Run containers as non-root users",
                    "Use .dockerignore to exclude unnecessary files",
                    "Implement health checks for container monitoring",
                    "Use docker-compose for multi-container applications",
                    "Regular base image updates for security patches"
                ],
                security_considerations=[
                    "Scan images for vulnerabilities before deployment",
                    "Use minimal base images (Alpine, distroless)",
                    "Implement proper secrets management",
                    "Use read-only filesystems where possible",
                    "Implement network segmentation for containers",
                    "Regular security updates for base images and dependencies"
                ],
                common_patterns={
                    "microservice_pattern": "Single responsibility → Lightweight image → Health checks → Service discovery",
                    "development_workflow": "Local development → Build → Test → Push to registry → Deploy",
                    "production_deployment": "Load balancer → Multiple container instances → Shared storage → Monitoring"
                },
                troubleshooting_guides={
                    "container_startup_issues": "Check: Image availability → Resource limits → Environment variables → Dependencies",
                    "networking_problems": "Verify: Port mappings → Network connectivity → DNS resolution → Firewall rules",
                    "storage_issues": "Investigate: Volume mounts → Permissions → Disk space → Storage drivers"
                },
                expert_tips=[
                    "Use BuildKit for advanced build features",
                    "Implement container image signing and verification",
                    "Use init systems in containers for proper signal handling",
                    "Optimize images with tools like dive for layer analysis"
                ],
                related_topics=["kubernetes", "service_mesh", "container_security"]
            ),
            
            "kubernetes_orchestration": TechnicalKnowledge(
                domain=TechnicalDomain.CONTAINERIZATION,
                topic="Kubernetes Orchestration",
                technologies=["Kubernetes", "kubectl", "Helm", "Istio", "Prometheus"],
                concepts={
                    "cluster": "Set of nodes running containerized applications managed by Kubernetes",
                    "pods": "Smallest deployable units containing one or more containers",
                    "services": "Stable network endpoints for accessing pods",
                    "deployments": "Declarative way to manage replica sets and pods",
                    "ingress": "HTTP/HTTPS routing to services within cluster"
                },
                best_practices=[
                    "Use namespaces for resource organization and isolation",
                    "Implement resource requests and limits for all containers",
                    "Use liveness and readiness probes for health checking",
                    "Implement proper RBAC for security",
                    "Use Helm charts for application packaging",
                    "Implement horizontal pod autoscaling",
                    "Use persistent volumes for stateful applications",
                    "Regular cluster and etcd backups"
                ],
                security_considerations=[
                    "Enable RBAC and use least-privilege principles",
                    "Use network policies for traffic segmentation",
                    "Implement pod security policies or admission controllers",
                    "Regular security scanning of container images",
                    "Use secrets management for sensitive data",
                    "Enable audit logging for cluster activities"
                ],
                common_patterns={
                    "application_deployment": "Deployment → Service → Ingress → ConfigMap/Secret",
                    "stateful_application": "StatefulSet → Persistent Volume → Headless Service",
                    "batch_processing": "Job/CronJob → Resource limits → Result storage"
                },
                troubleshooting_guides={
                    "pod_issues": "Check: Resource availability → Image pull → Configuration → Node status",
                    "networking_problems": "Verify: Service endpoints → Ingress configuration → Network policies → DNS",
                    "storage_issues": "Investigate: PV/PVC status → Storage class → Node connectivity → Permissions"
                },
                expert_tips=[
                    "Use kubectl plugins for enhanced functionality",
                    "Implement GitOps with ArgoCD or Flux",
                    "Use service mesh for advanced traffic management",
                    "Implement cluster autoscaling for cost optimization"
                ],
                related_topics=["service_mesh", "observability", "gitops"]
            ),
            
            "service_mesh": TechnicalKnowledge(
                domain=TechnicalDomain.CONTAINERIZATION,
                topic="Service Mesh",
                technologies=["Istio", "Linkerd", "Consul Connect", "Envoy"],
                concepts={
                    "service_mesh": "Infrastructure layer for service-to-service communication",
                    "sidecar_proxy": "Proxy deployed alongside each service instance",
                    "traffic_management": "Routing, load balancing, and failover capabilities",
                    "security": "Mutual TLS, authentication, and authorization",
                    "observability": "Metrics, logging, and tracing for microservices"
                },
                best_practices=[
                    "Implement gradual service mesh adoption",
                    "Use mutual TLS for service-to-service security",
                    "Implement proper traffic policies and routing rules",
                    "Monitor service mesh performance and overhead",
                    "Use distributed tracing for request flow analysis",
                    "Implement circuit breakers for resilience"
                ],
                security_considerations=[
                    "Enable mutual TLS for all service communication",
                    "Implement proper authorization policies",
                    "Regular certificate rotation and management",
                    "Monitor for security policy violations"
                ],
                common_patterns={
                    "canary_deployment": "Traffic routing → Gradual traffic increase → Monitoring → Rollback capability",
                    "circuit_breaker": "Failure detection → Service isolation → Fallback mechanisms → Recovery"
                },
                troubleshooting_guides={
                    "connectivity_issues": "Check: Proxy status → TLS certificates → Policy configuration → Network connectivity",
                    "performance_problems": "Monitor: Proxy overhead → Resource usage → Traffic patterns → Configuration efficiency"
                },
                expert_tips=[
                    "Use service mesh for cross-cluster communication",
                    "Implement proper observability stack integration",
                    "Use traffic mirroring for testing in production"
                ],
                related_topics=["microservices", "zero_trust_security", "observability"]
            )
        }
        
        self.knowledge_db[TechnicalDomain.CONTAINERIZATION] = containerization_knowledge
    
    def _load_system_engineering_knowledge(self):
        """Load system engineering and Linux administration knowledge."""
        system_knowledge = {
            "linux_administration": TechnicalKnowledge(
                domain=TechnicalDomain.SYSTEM_ENGINEERING,
                topic="Linux Administration",
                technologies=["Linux", "systemd", "bash", "cron", "SSH"],
                concepts={
                    "filesystem_hierarchy": "Standard directory structure and file organization",
                    "process_management": "Process lifecycle, signals, and resource management",
                    "service_management": "systemd units, services, and dependency management",
                    "user_management": "Users, groups, permissions, and access control",
                    "package_management": "Software installation, updates, and dependency resolution"
                },
                best_practices=[
                    "Use configuration management for consistent system setup",
                    "Implement proper backup strategies for critical data",
                    "Regular system updates and security patches",
                    "Use SSH key-based authentication",
                    "Implement log rotation and monitoring",
                    "Use sudo for privilege escalation instead of root login",
                    "Regular security audits and hardening",
                    "Document system configurations and procedures"
                ],
                security_considerations=[
                    "Disable root SSH login and use key-based authentication",
                    "Configure firewall rules and fail2ban for intrusion prevention",
                    "Regular security updates and vulnerability scanning",
                    "Implement proper file permissions and access controls",
                    "Use SELinux or AppArmor for mandatory access control",
                    "Monitor system logs for security events"
                ],
                common_patterns={
                    "system_hardening": "User management → SSH configuration → Firewall setup → Service management → Monitoring",
                    "service_deployment": "Package installation → Configuration → Service enablement → Health checks"
                },
                troubleshooting_guides={
                    "boot_issues": "Check: GRUB configuration → Filesystem integrity → Hardware status → Kernel logs",
                    "performance_problems": "Monitor: CPU usage → Memory consumption → Disk I/O → Network activity",
                    "service_failures": "Investigate: Service logs → Dependencies → Configuration → Resource availability"
                },
                expert_tips=[
                    "Use tools like htop, iotop, and netstat for system monitoring",
                    "Implement centralized logging with rsyslog or journald",
                    "Use cgroups for resource limitation and management",
                    "Implement automated system monitoring and alerting"
                ],
                related_topics=["security_hardening", "monitoring", "automation"]
            ),
            
            "performance_tuning": TechnicalKnowledge(
                domain=TechnicalDomain.SYSTEM_ENGINEERING,
                topic="Performance Tuning",
                technologies=["Linux", "perf", "sar", "iotop", "htop"],
                concepts={
                    "performance_metrics": "CPU, memory, disk I/O, and network performance indicators",
                    "bottleneck_identification": "Finding system components limiting overall performance",
                    "resource_optimization": "Tuning system parameters for optimal resource utilization",
                    "monitoring_tools": "Tools for performance measurement and analysis"
                },
                best_practices=[
                    "Establish performance baselines before optimization",
                    "Use monitoring tools to identify bottlenecks",
                    "Implement gradual tuning with measurement validation",
                    "Document all performance changes and their impacts",
                    "Regular performance testing and capacity planning",
                    "Use appropriate tools for different performance aspects"
                ],
                security_considerations=[
                    "Performance monitoring should not expose sensitive data",
                    "Secure monitoring tool access and data transmission",
                    "Consider security implications of performance optimizations"
                ],
                common_patterns={
                    "performance_analysis": "Baseline measurement → Bottleneck identification → Optimization → Validation",
                    "capacity_planning": "Current usage analysis → Growth projection → Resource planning → Implementation"
                },
                troubleshooting_guides={
                    "high_cpu_usage": "Identify: Top processes → CPU-bound tasks → Context switching → Interrupt handling",
                    "memory_issues": "Check: Memory usage → Swap activity → Memory leaks → Cache efficiency",
                    "disk_io_problems": "Monitor: Disk utilization → I/O wait times → Queue depths → Filesystem performance"
                },
                expert_tips=[
                    "Use flame graphs for CPU profiling visualization",
                    "Implement automated performance testing in CI/CD",
                    "Use BPF tools for advanced system tracing"
                ],
                related_topics=["monitoring", "capacity_planning", "troubleshooting"]
            )
        }
        
        self.knowledge_db[TechnicalDomain.SYSTEM_ENGINEERING] = system_knowledge
    
    def _load_cloud_computing_knowledge(self):
        """Load cloud computing knowledge."""
        cloud_knowledge = {
            "multi_cloud_strategies": TechnicalKnowledge(
                domain=TechnicalDomain.CLOUD_COMPUTING,
                topic="Multi-Cloud Strategies",
                technologies=["AWS", "Azure", "GCP", "Terraform", "Kubernetes"],
                concepts={
                    "multi_cloud": "Using multiple cloud providers for different services or redundancy",
                    "hybrid_cloud": "Combination of on-premises and cloud infrastructure",
                    "cloud_native": "Applications designed specifically for cloud environments",
                    "serverless": "Event-driven computing without server management"
                },
                best_practices=[
                    "Use infrastructure as code for consistency across clouds",
                    "Implement proper cloud resource tagging and cost management",
                    "Design for cloud portability with containerization",
                    "Use managed services when appropriate for reduced operational overhead",
                    "Implement proper identity and access management",
                    "Regular cost optimization and right-sizing exercises"
                ],
                security_considerations=[
                    "Implement zero-trust security model",
                    "Use cloud-native security services",
                    "Encrypt data in transit and at rest",
                    "Regular security assessments and compliance audits",
                    "Implement proper secrets management",
                    "Use cloud security posture management tools"
                ],
                common_patterns={
                    "lift_and_shift": "VM migration → Application adaptation → Optimization → Cloud-native transformation",
                    "cloud_native_design": "Microservices → Containers → Managed services → Serverless functions"
                },
                troubleshooting_guides={
                    "connectivity_issues": "Check: Network configuration → Security groups → Routing → DNS resolution",
                    "performance_problems": "Monitor: Resource utilization → Network latency → Service limits → Cost optimization"
                },
                expert_tips=[
                    "Use cloud cost management tools for optimization",
                    "Implement disaster recovery across multiple regions",
                    "Use cloud-native monitoring and observability solutions"
                ],
                related_topics=["cost_optimization", "disaster_recovery", "compliance"]
            )
        }
        
        self.knowledge_db[TechnicalDomain.CLOUD_COMPUTING] = cloud_knowledge
    
    def _load_security_knowledge(self):
        """Load security and compliance knowledge."""
        security_knowledge = {
            "zero_trust_security": TechnicalKnowledge(
                domain=TechnicalDomain.SECURITY,
                topic="Zero Trust Security",
                technologies=["Identity Providers", "Network Segmentation", "mTLS", "RBAC"],
                concepts={
                    "zero_trust": "Security model that assumes no implicit trust and verifies every transaction",
                    "identity_verification": "Continuous authentication and authorization of users and devices",
                    "network_segmentation": "Dividing network into security zones with controlled access",
                    "least_privilege": "Granting minimum necessary access rights to users and systems"
                },
                best_practices=[
                    "Implement strong identity and access management",
                    "Use multi-factor authentication for all access",
                    "Implement network micro-segmentation",
                    "Continuous monitoring and threat detection",
                    "Regular security assessments and penetration testing",
                    "Implement proper incident response procedures"
                ],
                security_considerations=[
                    "All network traffic should be encrypted",
                    "Regular access reviews and privilege audits",
                    "Implement proper logging and monitoring",
                    "Use behavioral analytics for anomaly detection"
                ],
                common_patterns={
                    "zero_trust_implementation": "Identity foundation → Device security → Network security → Application security → Data security",
                    "incident_response": "Detection → Containment → Investigation → Eradication → Recovery → Lessons learned"
                },
                troubleshooting_guides={
                    "access_denied_issues": "Check: User permissions → Group memberships → Policy configuration → Authentication status",
                    "security_incidents": "Isolate: Affected systems → Collect evidence → Analyze logs → Implement countermeasures"
                },
                expert_tips=[
                    "Use SIEM solutions for centralized security monitoring",
                    "Implement security automation and orchestration",
                    "Regular security awareness training for users"
                ],
                related_topics=["compliance", "incident_response", "threat_detection"]
            )
        }
        
        self.knowledge_db[TechnicalDomain.SECURITY] = security_knowledge
    
    def _load_networking_knowledge(self):
        """Load networking knowledge."""
        networking_knowledge = {
            "network_fundamentals": TechnicalKnowledge(
                domain=TechnicalDomain.NETWORKING,
                topic="Network Fundamentals",
                technologies=["TCP/IP", "VLANs", "VPN", "Load Balancers", "Firewalls"],
                concepts={
                    "osi_model": "Seven-layer model for network communication",
                    "subnetting": "Dividing networks into smaller segments",
                    "routing": "Path determination for network traffic",
                    "switching": "Frame forwarding within network segments"
                },
                best_practices=[
                    "Implement network segmentation for security",
                    "Use VLANs for logical network separation",
                    "Implement redundant network paths",
                    "Regular network monitoring and capacity planning",
                    "Document network topology and configurations",
                    "Use network automation for consistent configuration"
                ],
                security_considerations=[
                    "Implement proper firewall rules",
                    "Use VPNs for secure remote access",
                    "Network traffic encryption where possible",
                    "Regular security scans and vulnerability assessments"
                ],
                common_patterns={
                    "network_design": "Requirements analysis → Topology design → Security implementation → Monitoring setup",
                    "troubleshooting": "Layer 1 → Layer 2 → Layer 3 → Application layer investigation"
                },
                troubleshooting_guides={
                    "connectivity_issues": "Check: Physical connectivity → IP configuration → Routing → Firewall rules → DNS resolution",
                    "performance_problems": "Monitor: Bandwidth utilization → Latency → Packet loss → Error rates"
                },
                expert_tips=[
                    "Use network monitoring tools for proactive issue detection",
                    "Implement Quality of Service (QoS) for critical applications",
                    "Use network automation tools like Ansible for configuration management"
                ],
                related_topics=["security", "monitoring", "automation"]
            )
        }
        
        self.knowledge_db[TechnicalDomain.NETWORKING] = networking_knowledge
    
    def _load_monitoring_knowledge(self):
        """Load monitoring and observability knowledge."""
        monitoring_knowledge = {
            "observability_fundamentals": TechnicalKnowledge(
                domain=TechnicalDomain.MONITORING,
                topic="Observability Fundamentals",
                technologies=["Prometheus", "Grafana", "ELK Stack", "Jaeger", "OpenTelemetry"],
                concepts={
                    "metrics": "Numerical measurements of system behavior over time",
                    "logs": "Structured or unstructured records of system events",
                    "traces": "Records of request flows through distributed systems",
                    "alerting": "Automated notifications based on system conditions"
                },
                best_practices=[
                    "Implement comprehensive monitoring across all system layers",
                    "Use standardized metrics and logging formats",
                    "Set up meaningful alerts with proper thresholds",
                    "Implement distributed tracing for microservices",
                    "Regular review and optimization of monitoring configurations",
                    "Use dashboards for visualization and trending"
                ],
                security_considerations=[
                    "Secure monitoring data transmission and storage",
                    "Implement proper access controls for monitoring systems",
                    "Avoid logging sensitive information",
                    "Regular security updates for monitoring tools"
                ],
                common_patterns={
                    "monitoring_stack": "Data collection → Storage → Visualization → Alerting",
                    "incident_response": "Alert → Investigation → Diagnosis → Resolution → Post-mortem"
                },
                troubleshooting_guides={
                    "missing_metrics": "Check: Data collection → Network connectivity → Configuration → Storage capacity",
                    "alert_fatigue": "Review: Alert thresholds → Notification frequency → Relevance → Escalation procedures"
                },
                expert_tips=[
                    "Use SLIs and SLOs for service reliability measurement",
                    "Implement chaos engineering for system resilience testing",
                    "Use synthetic monitoring for proactive issue detection"
                ],
                related_topics=["incident_response", "performance_tuning", "automation"]
            )
        }
        
        self.knowledge_db[TechnicalDomain.MONITORING] = monitoring_knowledge
    
    def _build_indices(self):
        """Build search indices for technologies and patterns."""
        # Build technology index
        for domain, knowledge_items in self.knowledge_db.items():
            for topic, knowledge in knowledge_items.items():
                for tech in knowledge.technologies:
                    if tech.lower() not in self.technology_index:
                        self.technology_index[tech.lower()] = []
                    self.technology_index[tech.lower()].append((domain, topic))
        
        # Build pattern index
        for domain, knowledge_items in self.knowledge_db.items():
            for topic, knowledge in knowledge_items.items():
                for pattern_name, pattern_desc in knowledge.common_patterns.items():
                    if pattern_name not in self.pattern_index:
                        self.pattern_index[pattern_name] = []
                    self.pattern_index[pattern_name].append(f"{domain.value}/{topic}")
    
    def get_domain_knowledge(
        self,
        context: KnowledgeContext
    ) -> Dict[str, Any]:
        """
        Get comprehensive knowledge for a specific domain and context.
        
        Args:
            context: Knowledge context with domain, expertise level, and requirements
            
        Returns:
            Structured knowledge appropriate for the context
        """
        domain_knowledge = self.knowledge_db.get(context.domain, {})
        
        if not domain_knowledge:
            logger.warning("No knowledge found for domain", domain=context.domain.value)
            return {}
        
        # Filter and adapt knowledge based on expertise level
        adapted_knowledge = {}
        
        for topic, knowledge in domain_knowledge.items():
            adapted_knowledge[topic] = self._adapt_knowledge_for_expertise(
                knowledge, context.expertise_level
            )
        
        # Add relevant cross-domain knowledge
        related_knowledge = self._get_related_knowledge(context)
        if related_knowledge:
            adapted_knowledge["related_domains"] = related_knowledge
        
        logger.info(
            "Retrieved domain knowledge",
            domain=context.domain.value,
            expertise_level=context.expertise_level.value,
            topics_count=len(adapted_knowledge)
        )
        
        return adapted_knowledge
    
    def _adapt_knowledge_for_expertise(
        self,
        knowledge: TechnicalKnowledge,
        expertise_level: ExpertiseLevel
    ) -> Dict[str, Any]:
        """Adapt knowledge content based on expertise level."""
        adapted = {
            "topic": knowledge.topic,
            "technologies": knowledge.technologies,
            "concepts": knowledge.concepts
        }
        
        if expertise_level == ExpertiseLevel.BEGINNER:
            # For beginners: Basic concepts, essential best practices, common patterns
            adapted["best_practices"] = knowledge.best_practices[:5]  # Top 5 practices
            adapted["security_considerations"] = knowledge.security_considerations[:3]  # Essential security
            adapted["common_patterns"] = dict(list(knowledge.common_patterns.items())[:2])  # Basic patterns
            adapted["related_topics"] = knowledge.related_topics[:3]  # Most relevant topics
            
        elif expertise_level == ExpertiseLevel.INTERMEDIATE:
            # For intermediate: Full best practices, detailed patterns, more security
            adapted["best_practices"] = knowledge.best_practices
            adapted["security_considerations"] = knowledge.security_considerations
            adapted["common_patterns"] = knowledge.common_patterns
            adapted["troubleshooting_guides"] = dict(list(knowledge.troubleshooting_guides.items())[:3])
            adapted["related_topics"] = knowledge.related_topics
            
        else:  # EXPERT
            # For experts: Everything including expert tips and advanced troubleshooting
            adapted["best_practices"] = knowledge.best_practices
            adapted["security_considerations"] = knowledge.security_considerations
            adapted["common_patterns"] = knowledge.common_patterns
            adapted["troubleshooting_guides"] = knowledge.troubleshooting_guides
            adapted["expert_tips"] = knowledge.expert_tips
            adapted["related_topics"] = knowledge.related_topics
        
        return adapted
    
    def _get_related_knowledge(self, context: KnowledgeContext) -> Dict[str, List[str]]:
        """Get knowledge from related domains."""
        related = {}
        
        # Map related domains based on the primary domain
        domain_relationships = {
            TechnicalDomain.VIRTUALIZATION: [TechnicalDomain.NETWORKING, TechnicalDomain.SECURITY, TechnicalDomain.MONITORING],
            TechnicalDomain.INFRASTRUCTURE_AS_CODE: [TechnicalDomain.AUTOMATION, TechnicalDomain.SECURITY, TechnicalDomain.CLOUD_COMPUTING],
            TechnicalDomain.CONTAINERIZATION: [TechnicalDomain.MONITORING, TechnicalDomain.NETWORKING, TechnicalDomain.SECURITY],
            TechnicalDomain.CLOUD_COMPUTING: [TechnicalDomain.SECURITY, TechnicalDomain.NETWORKING, TechnicalDomain.MONITORING],
            TechnicalDomain.SECURITY: [TechnicalDomain.NETWORKING, TechnicalDomain.MONITORING, TechnicalDomain.SYSTEM_ENGINEERING]
        }
        
        related_domains = domain_relationships.get(context.domain, [])
        
        for related_domain in related_domains:
            if related_domain in self.knowledge_db:
                related[related_domain.value] = list(self.knowledge_db[related_domain].keys())
        
        return related
    
    def search_by_technology(self, technology: str) -> List[Tuple[TechnicalDomain, str]]:
        """Search knowledge by technology name."""
        return self.technology_index.get(technology.lower(), [])
    
    def get_security_recommendations(
        self,
        domain: TechnicalDomain,
        technologies: List[str]
    ) -> List[str]:
        """Get security recommendations for specific domain and technologies."""
        recommendations = []
        
        # Get domain-specific security knowledge
        if domain in self.knowledge_db:
            for knowledge in self.knowledge_db[domain].values():
                if any(tech.lower() in [t.lower() for t in knowledge.technologies] for tech in technologies):
                    recommendations.extend(knowledge.security_considerations)
        
        # Add general security recommendations
        if TechnicalDomain.SECURITY in self.knowledge_db:
            for knowledge in self.knowledge_db[TechnicalDomain.SECURITY].values():
                recommendations.extend(knowledge.security_considerations[:3])  # Top 3 general recommendations
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]  # Return top 10 recommendations
    
    def get_troubleshooting_guide(
        self,
        domain: TechnicalDomain,
        issue_keywords: List[str]
    ) -> Dict[str, str]:
        """Get troubleshooting guides based on domain and issue keywords."""
        guides = {}
        
        if domain not in self.knowledge_db:
            return guides
        
        for knowledge in self.knowledge_db[domain].values():
            for guide_name, guide_content in knowledge.troubleshooting_guides.items():
                # Check if any keyword matches the guide name or content
                if any(keyword.lower() in guide_name.lower() or keyword.lower() in guide_content.lower() 
                       for keyword in issue_keywords):
                    guides[guide_name] = guide_content
        
        return guides


# Global knowledge base instance
technical_knowledge_base = TechnicalKnowledgeBase()