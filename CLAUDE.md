# Claude.md - Proxmox AI Infrastructure Assistant

## 🤖 Project Overview

**Proxmox AI Infrastructure Assistant** is an enterprise-grade, AI-powered CLI tool that automates virtual machine lifecycle management, infrastructure provisioning, and security hardening on local Proxmox hypervisor environments. This project demonstrates advanced DevOps, Infrastructure as Code (IaC), and AI integration skills for cloud engineering career advancement.

## 🎯 Main Purpose

### **Primary Objectives:**
1. **Automate VM Operations**: Create, configure, and manage VMs through intelligent CLI commands
2. **AI-Powered Infrastructure**: Generate Terraform/Ansible configurations using AI assistance  
3. **Security-First Approach**: Implement enterprise-grade security automation and hardening
4. **Cost-Effective Learning**: Provide cloud-like experience without ongoing cloud costs
5. **Career Portfolio**: Demonstrate cutting-edge skills for Cloud/Systems Engineer roles

### **Target Use Cases:**
- **Development Environment Provisioning**: Spin up development stacks instantly
- **Security Compliance Automation**: Apply consistent security policies across VMs
- **Infrastructure Documentation**: Auto-generate infrastructure documentation and runbooks
- **Learning Platform**: Practice cloud concepts in a controlled, local environment
- **Portfolio Demonstration**: Showcase advanced automation and AI integration skills

## 🏗️ Architecture & Technology Stack

### **Core Technologies:**
- **Hypervisor**: Proxmox VE (Enterprise virtualization platform) - Host: YOUR_PROXMOX_HOST
- **Programming Language**: Python 3.12+ with modern async capabilities
- **CLI Framework**: Typer (modern, type-safe CLI framework)
- **UI/UX**: Rich (beautiful terminal interfaces)
- **API Integration**: Proxmoxer (Proxmox API client)
- **Infrastructure**: Terraform + Ansible (IaC and configuration management)
- **AI Integration**: Anthropic Claude API (code generation and optimization)
- **Security**: SSH key management, LUKS encryption, fail2ban, encrypted communications

### **Security Architecture:**
```
External Access (Client Device) 
    ↓ SSH Key Authentication (Custom Port)
Router/Firewall 
    ↓ Port Forwarding (Encrypted)
Proxmox Host (YOUR_PROXMOX_HOST)
    ↓ VM Network Bridge (vmbr0) + Firewall Rules
AI Assistant VM (YOUR_VM_IP) - LUKS Encrypted
    ↓ Secure Internal Communication (TLS + SSH Keys)
Target VMs (YOUR_VM_RANGE) - Individual Security Hardening
```

## 🎭 Five Development Agents (Role-Based with Proxmox Specialization)

### **Agent 1: QA Engineer & Security Specialist**
**Role**: Quality Assurance and comprehensive security testing for Proxmox infrastructure
**Proxmox Specialization**: VM security hardening, Proxmox API security, network isolation testing
**Responsibilities**:
- **Automated Testing**: Create comprehensive test suites for all Proxmox VM operations
- **Security Auditing**: Regular penetration testing of VM configurations and network isolation
- **Compliance Verification**: Ensure all VMs meet CIS benchmarks and enterprise security standards
- **Performance Testing**: Load testing for Proxmox API calls and VM deployment scalability
- **Vulnerability Management**: Continuous security scanning and automated patch management

### **Agent 2: Project Manager & Infrastructure Orchestrator**
**Role**: Project coordination and high-level infrastructure strategy for Proxmox environments
**Proxmox Specialization**: Resource planning, capacity management, disaster recovery coordination
**Responsibilities**:
- **Resource Planning**: Optimize Proxmox cluster resource allocation and capacity planning
- **Timeline Management**: Coordinate VM deployment schedules and maintenance windows
- **Risk Assessment**: Identify infrastructure risks and create mitigation strategies
- **Stakeholder Communication**: Generate executive reports on infrastructure health and costs
- **Change Management**: Oversee infrastructure changes and deployment processes

### **Agent 3: Version Control & Configuration Manager**
**Role**: Git workflow management and Infrastructure as Code versioning for Proxmox
**Proxmox Specialization**: VM template versioning, configuration drift detection, backup strategies
**Responsibilities**:
- **GitOps Implementation**: Manage infrastructure state through Git-based workflows
- **Template Management**: Version control for Proxmox VM templates and cloud-init configurations
- **Configuration Drift Detection**: Monitor and alert on unauthorized VM configuration changes
- **Rollback Strategies**: Implement safe rollback procedures for infrastructure changes
- **Backup Coordination**: Automate and verify Proxmox backup procedures with version tracking

### **Agent 4: Software Engineer & Automation Developer**
**Role**: Core development and advanced automation features for Proxmox integration
**Proxmox Specialization**: API optimization, VM lifecycle automation, network programming
**Responsibilities**:
- **Core Development**: Build and maintain the CLI framework and Proxmox API integration
- **Automation Engineering**: Create intelligent VM provisioning and scaling algorithms
- **API Integration**: Optimize Proxmox API calls for performance and reliability
- **AI Integration**: Implement Claude API integration for infrastructure code generation
- **Performance Optimization**: Monitor and optimize system performance and resource usage

### **Agent 5: Documentation Lead & Knowledge Manager**
**Role**: Comprehensive documentation and knowledge management for Proxmox operations
**Proxmox Specialization**: VM runbooks, network diagrams, security procedures documentation
**Responsibilities**:
- **Technical Documentation**: Create detailed guides for all Proxmox operations and procedures
- **Architecture Documentation**: Maintain network diagrams and infrastructure blueprints
- **Security Runbooks**: Document incident response and security procedures
- **Training Materials**: Develop tutorials and learning resources for team members
- **Knowledge Base**: Maintain searchable documentation and troubleshooting guides

## 📋 Development Workflow & Security Guidelines

### **Development Process Protocol:**

#### **1. Initial Analysis and Planning**
- **Objective**: First think through the problem, read the codebase for relevant files, and write a plan to `tasks/todo.md`
- **Security Focus**: Every plan must include security impact assessment and threat modeling
- **Approach**: Analyze current state, identify gaps, and create actionable tasks with security checkpoints

#### **2. Todo List Structure**
- **Format**: The plan should have a list of todo items that you can check off as you complete them
- **Security Requirements**: Each task must include security validation criteria
- **Priority**: Tasks ranked by business impact, technical dependencies, and security criticality

#### **3. Plan Verification**
- **Process**: Before you begin working, check in with me and I will verify the plan
- **Security Review**: All plans require security architecture review before implementation
- **Approval**: No development work begins without explicit plan approval and security sign-off

#### **4. Task Execution**
- **Methodology**: Begin working on the todo items, marking them as complete as you go
- **Security Testing**: Each task completion requires security validation and testing
- **Focus**: Work on one task at a time to maintain quality and security posture

#### **5. Communication**
- **Frequency**: Please every step of the way just give me a high level explanation of what changes you made
- **Security Updates**: Include security implications and any new attack surface considerations
- **Clarity**: Focus on business impact, user-facing changes, and security improvements

#### **6. Simplicity Principle**
- **Philosophy**: Make every task and code change you do as simple as possible
- **Security by Design**: Simple code is more secure code - avoid complex security mechanisms
- **Impact**: Every change should impact as little code as possible while maintaining security boundaries

#### **7. Process Documentation**
- **Activity Logging**: Every time you perform actions related to the project, write a log of your actions to `docs/activity.md`
- **Security Logging**: Document all security-related decisions and their rationale
- **Reference**: Read that file whenever you find it necessary to assist you

#### **8. Review Process**
- **Completion**: Finally, add a review section to the `todo.md` file with a summary of the changes you made
- **Security Assessment**: Include security impact analysis and any residual risks
- **Documentation**: Update relevant security documentation with new features or changes

### **Comprehensive Security Requirements:**

#### **Code Security Standards:**
- **No Hardcoded Secrets**: All credentials, API keys, and sensitive data must be externalized
- **Input Validation**: Sanitize and validate all user inputs and Proxmox API parameters
- **Least Privilege**: Minimal required permissions for all operations and service accounts
- **Secure Communication**: All network communications must use TLS 1.3 or SSH encryption
- **Error Handling**: Never expose sensitive information in error messages or logs

#### **Infrastructure Security:**
- **VM Isolation**: Each VM must be properly isolated with dedicated firewall rules
- **Network Segmentation**: Use VLANs and network policies to isolate different environments
- **Encrypted Storage**: All VM disks must use LUKS encryption with strong passphrases
- **SSH Key Management**: Implement automated key rotation and secure key distribution
- **Backup Security**: All backups must be encrypted and stored with access controls

#### **Operational Security:**
- **Audit Logging**: Log all infrastructure changes, access attempts, and administrative actions
- **Monitoring**: Implement real-time monitoring for security events and anomalies
- **Incident Response**: Maintain documented incident response procedures and contact lists
- **Compliance**: Ensure all operations meet relevant security frameworks (CIS, NIST)
- **Regular Security Assessments**: Schedule periodic security reviews and penetration testing

#### **Development Security:**
- **Secure Development**: Follow secure coding practices and regular security code reviews
- **Dependency Management**: Regular security scanning of all dependencies and libraries
- **Secrets Management**: Use proper secrets management solutions, never commit secrets to Git
- **Access Controls**: Implement proper access controls for development and production environments
- **Security Testing**: Automated security testing in CI/CD pipelines

## 🎯 Success Metrics

### **Technical Achievements:**
- **100% Automation**: Complete VM lifecycle without manual Proxmox web interface interaction
- **Security Compliance**: All VMs meet enterprise security standards automatically
- **Performance**: Sub-30-second VM deployment times using secured Proxmox API
- **Reliability**: 99.9% uptime for critical infrastructure components
- **Security Posture**: Zero security incidents and 100% compliance with security policies

### **Career Impact:**
- **Portfolio Quality**: Production-ready code suitable for enterprise Proxmox environments
- **Skill Demonstration**: Advanced DevOps, AI, security, and virtualization integration
- **Security Expertise**: Demonstrated ability to implement enterprise-grade security practices
- **Industry Relevance**: Technologies and practices used in high-security enterprise environments
- **Interview Advantage**: Concrete examples of security-first infrastructure automation

## 🔮 Project Roadmap

### **Phase 1: Secure Foundation (Weeks 1-2)**
- Complete secured Proxmox API integration with TLS and authentication
- Implement SSH key management and comprehensive security hardening
- Create core CLI framework with encrypted configuration management
- Establish security monitoring and audit logging

### **Phase 2: Intelligence Layer (Weeks 3-4)**
- Integrate Anthropic Claude API with secure credential management
- Build template system with security-validated VM configurations
- Implement Ansible integration with encrypted communication channels
- Add security monitoring and compliance checking capabilities

### **Phase 3: Advanced Security Automation (Weeks 5-6)**
- Network automation with security-focused VLAN and firewall management
- Advanced storage operations with encryption and secure backup automation
- Automated security compliance scanning and remediation
- Performance optimization with security constraint awareness

### **Phase 4: Secure DevOps Integration (Weeks 7-8)**
- CI/CD pipeline automation with security gates and approval workflows
- Container platform deployment with security policies and network isolation
- Comprehensive monitoring stack with security event correlation
- Security documentation automation and incident response procedures

**This project demonstrates the ability to build secure, enterprise-grade infrastructure automation while maintaining the highest levels of security and compliance throughout the development and deployment process.**
## Notes for Future Development

This project appears to be focused on Infrastructure as Code automation with AI assistance. As the project develops, this file should be updated with:
- Specific build and test commands
- API endpoints and usage
- Database setup instructions
- Deployment procedures
- Architecture details
