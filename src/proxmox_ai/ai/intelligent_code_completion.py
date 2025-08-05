"""
Intelligent Code Completion and Suggestions System.

This module provides advanced code completion, intelligent suggestions, and
context-aware code generation for infrastructure automation, optimized for
Intel N150 hardware with efficient caching and processing.
"""

import re
import json
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from pathlib import Path
import ast
import yaml

import structlog

# Code analysis libraries
try:
    import jedi
    from jedi import Script
    JEDI_AVAILABLE = True
except ImportError:
    JEDI_AVAILABLE = False

try:
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

from ..core.hardware_detector import hardware_detector
from ..core.performance_monitor import PerformanceMonitor

logger = structlog.get_logger(__name__)


@dataclass
class CodeSuggestion:
    """Represents a code completion suggestion."""
    
    completion_text: str
    suggestion_type: str  # 'completion', 'snippet', 'template', 'fix'
    confidence: float
    description: str
    insert_position: int
    replace_length: int = 0
    category: str = "general"  # 'terraform', 'ansible', 'bash', 'yaml'
    template_variables: Dict[str, str] = field(default_factory=dict)
    documentation: Optional[str] = None
    priority: int = 1  # 1 = highest priority


@dataclass
class CodeContext:
    """Represents the context around code being edited."""
    
    file_type: str  # 'terraform', 'ansible', 'yaml', 'bash', 'python'
    file_path: Optional[str] = None
    cursor_position: int = 0
    current_line: str = ""
    preceding_lines: List[str] = field(default_factory=list)
    following_lines: List[str] = field(default_factory=list)
    indentation_level: int = 0
    in_block: Optional[str] = None  # 'resource', 'data', 'variable', 'task'
    block_type: Optional[str] = None
    variables_in_scope: List[str] = field(default_factory=list)


@dataclass
class CodeAnalysis:
    """Results of analyzing code for suggestions."""
    
    syntax_errors: List[str] = field(default_factory=list)
    suggestions: List[CodeSuggestion] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    optimizations: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)


class InfrastructureCodeTemplates:
    """Template library for infrastructure code snippets."""
    
    def __init__(self):
        self.terraform_templates = self._load_terraform_templates()
        self.ansible_templates = self._load_ansible_templates()
        self.kubernetes_templates = self._load_kubernetes_templates()
        self.bash_templates = self._load_bash_templates()
        
        logger.info("Infrastructure code templates loaded")
    
    def _load_terraform_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load Terraform code templates."""
        return {
            "proxmox_vm": {
                "trigger": ["resource", "proxmox_vm_qemu"],
                "template": '''resource "proxmox_vm_qemu" "${1:vm_name}" {
  name        = "${2:vm-name}"
  target_node = "${3:proxmox-node}"
  
  cores  = ${4:2}
  memory = ${5:2048}
  
  disk {
    size    = "${6:20G}"
    type    = "${7:scsi}"
    storage = "${8:local-lvm}"
  }
  
  network {
    model  = "${9:virtio}"
    bridge = "${10:vmbr0}"
  }
  
  os_type = "${11:cloud-init}"
}''',
                "description": "Create a Proxmox VM resource",
                "category": "virtualization"
            },
            
            "data_source": {
                "trigger": ["data"],
                "template": '''data "${1:data_source_type}" "${2:name}" {
  ${3:# Configuration}
}''',
                "description": "Create a data source",
                "category": "data"
            },
            
            "variable": {
                "trigger": ["variable"],
                "template": '''variable "${1:name}" {
  description = "${2:Description}"
  type        = ${3:string}
  default     = "${4:default_value}"
}''',
                "description": "Create a variable",
                "category": "variables"
            },
            
            "output": {
                "trigger": ["output"],
                "template": '''output "${1:name}" {
  description = "${2:Description}"
  value       = ${3:value}
}''',
                "description": "Create an output",
                "category": "outputs"
            },
            
            "locals": {
                "trigger": ["locals"],
                "template": '''locals {
  ${1:name} = "${2:value}"
}''',
                "description": "Create local values",
                "category": "locals"
            }
        }
    
    def _load_ansible_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load Ansible playbook templates."""
        return {
            "playbook": {
                "trigger": ["---", "playbook"],
                "template": '''---
- name: ${1:Playbook description}
  hosts: ${2:target_hosts}
  become: ${3:yes}
  
  vars:
    ${4:variable_name}: "${5:value}"
  
  tasks:
    - name: ${6:Task description}
      ${7:module_name}:
        ${8:parameter}: "${9:value}"''',
                "description": "Create an Ansible playbook",
                "category": "playbook"
            },
            
            "task": {
                "trigger": ["- name", "task"],
                "template": '''- name: ${1:Task description}
  ${2:module_name}:
    ${3:parameter}: "${4:value}"
  ${5:when: condition}
  ${6:notify: handler_name}''',
                "description": "Create an Ansible task",
                "category": "task"
            },
            
            "handler": {
                "trigger": ["handlers"],
                "template": '''handlers:
  - name: ${1:Handler name}
    ${2:module_name}:
      ${3:parameter}: "${4:value}"''',
                "description": "Create Ansible handlers",
                "category": "handlers"
            },
            
            "role": {
                "trigger": ["roles"],
                "template": '''roles:
  - name: ${1:role_name}
    vars:
      ${2:variable}: "${3:value}"''',
                "description": "Include an Ansible role",
                "category": "roles"
            }
        }
    
    def _load_kubernetes_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load Kubernetes manifest templates."""
        return {
            "deployment": {
                "trigger": ["apiVersion", "Deployment"],
                "template": '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${1:app-name}
  labels:
    app: ${2:app-name}
spec:
  replicas: ${3:3}
  selector:
    matchLabels:
      app: ${4:app-name}
  template:
    metadata:
      labels:
        app: ${5:app-name}
    spec:
      containers:
      - name: ${6:container-name}
        image: ${7:image:tag}
        ports:
        - containerPort: ${8:80}''',
                "description": "Create a Kubernetes Deployment",
                "category": "workloads"
            },
            
            "service": {
                "trigger": ["Service"],
                "template": '''apiVersion: v1
kind: Service
metadata:
  name: ${1:service-name}
spec:
  selector:
    app: ${2:app-name}
  ports:
  - port: ${3:80}
    targetPort: ${4:8080}
  type: ${5:ClusterIP}''',
                "description": "Create a Kubernetes Service",
                "category": "networking"
            },
            
            "configmap": {
                "trigger": ["ConfigMap"],
                "template": '''apiVersion: v1
kind: ConfigMap
metadata:
  name: ${1:config-name}
data:
  ${2:key}: "${3:value}"''',
                "description": "Create a ConfigMap",
                "category": "configuration"
            }
        }
    
    def _load_bash_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load Bash script templates."""
        return {
            "script_header": {
                "trigger": ["#!/bin/bash"],
                "template": '''#!/bin/bash
set -euo pipefail

# ${1:Script description}
# Author: ${2:Your Name}
# Date: $(date +%Y-%m-%d)

${3:# Script content}''',
                "description": "Bash script header with best practices",
                "category": "script"
            },
            
            "function": {
                "trigger": ["function"],
                "template": '''${1:function_name}() {
    local ${2:param}="$1"
    
    ${3:# Function body}
    
    return 0
}''',
                "description": "Bash function template",
                "category": "function"
            },
            
            "error_handling": {
                "trigger": ["error", "trap"],
                "template": '''cleanup() {
    ${1:# Cleanup code}
    exit $?
}

trap cleanup EXIT ERR''',
                "description": "Error handling and cleanup",
                "category": "error_handling"
            }
        }
    
    def get_templates_for_context(self, context: CodeContext) -> List[Dict[str, Any]]:
        """Get relevant templates for the current context."""
        if context.file_type == "terraform":
            return list(self.terraform_templates.values())
        elif context.file_type == "ansible":
            return list(self.ansible_templates.values())
        elif context.file_type == "kubernetes" or context.file_type == "yaml":
            return list(self.kubernetes_templates.values())
        elif context.file_type == "bash":
            return list(self.bash_templates.values())
        else:
            return []


class IntelligentCodeAnalyzer:
    """Analyzes code for completion suggestions and improvements."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.syntax_patterns = self._load_syntax_patterns()
        self.common_mistakes = self._load_common_mistakes()
        self.best_practices = self._load_best_practices()
        
        # Initialize Jedi for Python completion if available
        self.jedi_available = JEDI_AVAILABLE
        
        logger.info(
            "Intelligent code analyzer initialized",
            jedi_available=self.jedi_available
        )
    
    def _load_syntax_patterns(self) -> Dict[str, List[str]]:
        """Load syntax patterns for different file types."""
        return {
            "terraform": [
                r'resource\s+"([^"]+)"\s+"([^"]+)"\s*{',
                r'data\s+"([^"]+)"\s+"([^"]+)"\s*{',
                r'variable\s+"([^"]+)"\s*{',
                r'output\s+"([^"]+)"\s*{',
                r'locals\s*{',
                r'provider\s+"([^"]+)"\s*{'
            ],
            "ansible": [
                r'- name:\s*(.+)',
                r'hosts:\s*(.+)',
                r'vars:\s*',
                r'tasks:\s*',
                r'handlers:\s*',
                r'roles:\s*'
            ],
            "kubernetes": [
                r'apiVersion:\s*(.+)',
                r'kind:\s*(.+)',
                r'metadata:\s*',
                r'spec:\s*',
                r'data:\s*',
                r'containers:\s*'
            ]
        }
    
    def _load_common_mistakes(self) -> Dict[str, List[Dict[str, str]]]:
        """Load common mistakes and their fixes."""
        return {
            "terraform": [
                {
                    "pattern": r'resource\s+"proxmox_vm_qemu"\s+"[^"]+"\s*{\s*name\s*=\s*"[^"]*"\s*target_node\s*=\s*"[^"]*"\s*cores\s*=\s*\d+\s*memory\s*=\s*\d+\s*}',
                    "issue": "Missing disk and network configuration",
                    "suggestion": "Add disk and network blocks to VM resource"
                },
                {
                    "pattern": r'variable\s+"[^"]+"\s*{\s*}',
                    "issue": "Variable without type or description",
                    "suggestion": "Add type and description to variable"
                }
            ],
            "ansible": [
                {
                    "pattern": r'- name:\s*(.+)\s+\w+:\s*',
                    "issue": "Task without proper module structure",
                    "suggestion": "Ensure proper indentation for module parameters"
                }
            ]
        }
    
    def _load_best_practices(self) -> Dict[str, List[str]]:
        """Load best practices for different file types."""
        return {
            "terraform": [
                "Use meaningful resource names",
                "Always include descriptions for variables",
                "Use data sources instead of hardcoded values",
                "Implement proper tagging strategy",
                "Use terraform fmt for consistent formatting"
            ],
            "ansible": [
                "Use descriptive task names",
                "Implement proper error handling",
                "Use variables for repeated values",
                "Include become only when necessary",
                "Use handlers for service restarts"
            ],
            "kubernetes": [
                "Always specify resource limits",
                "Use namespaces for organization",
                "Implement health checks",
                "Use ConfigMaps for configuration",
                "Label resources consistently"
            ]
        }
    
    async def analyze_code(self, code: str, context: CodeContext) -> CodeAnalysis:
        """Analyze code and provide suggestions."""
        start_time = time.time()
        
        analysis = CodeAnalysis()
        
        try:
            # Syntax analysis
            syntax_errors = await self._check_syntax(code, context)
            analysis.syntax_errors.extend(syntax_errors)
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(code, context)
            analysis.suggestions.extend(suggestions)
            
            # Check for common mistakes
            warnings = await self._check_common_mistakes(code, context)
            analysis.warnings.extend(warnings)
            
            # Security analysis
            security_issues = await self._check_security_issues(code, context)
            analysis.security_issues.extend(security_issues)
            
            # Best practices check
            best_practices = await self._check_best_practices(code, context)
            analysis.best_practices.extend(best_practices)
            
            logger.info(
                "Code analysis completed",
                file_type=context.file_type,
                suggestions_count=len(analysis.suggestions),
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error("Code analysis failed", error=str(e))
        
        return analysis
    
    async def _check_syntax(self, code: str, context: CodeContext) -> List[str]:
        """Check syntax errors in code."""
        errors = []
        
        if context.file_type == "terraform":
            # Basic Terraform syntax checks
            if not re.search(r'{\s*$', code.strip(), re.MULTILINE):
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if re.search(r'(resource|data|variable|output)\s+"[^"]+"\s*"?[^"]*"?\s*$', line.strip()):
                        errors.append(f"Line {i+1}: Missing opening brace after block declaration")
        
        elif context.file_type == "yaml" or context.file_type == "ansible":
            try:
                yaml.safe_load(code)
            except yaml.YAMLError as e:
                errors.append(f"YAML syntax error: {str(e)}")
        
        elif context.file_type == "python" and self.jedi_available:
            try:
                script = Script(code=code)
                # Jedi doesn't directly provide syntax errors in this version
                # This is a placeholder for more advanced syntax checking
            except Exception as e:
                errors.append(f"Python syntax error: {str(e)}")
        
        return errors
    
    async def _generate_suggestions(self, code: str, context: CodeContext) -> List[CodeSuggestion]:
        """Generate intelligent code suggestions."""
        suggestions = []
        
        # Context-aware suggestions based on cursor position
        current_line = context.current_line.strip()
        
        if context.file_type == "terraform":
            suggestions.extend(await self._terraform_suggestions(current_line, context))
        elif context.file_type == "ansible":
            suggestions.extend(await self._ansible_suggestions(current_line, context))
        elif context.file_type == "kubernetes":
            suggestions.extend(await self._kubernetes_suggestions(current_line, context))
        elif context.file_type == "bash":
            suggestions.extend(await self._bash_suggestions(current_line, context))
        
        # Sort by priority and confidence
        suggestions.sort(key=lambda x: (x.priority, -x.confidence))
        
        return suggestions[:10]  # Limit to top 10 suggestions
    
    async def _terraform_suggestions(self, current_line: str, context: CodeContext) -> List[CodeSuggestion]:
        """Generate Terraform-specific suggestions."""
        suggestions = []
        
        # Resource block suggestions
        if current_line.startswith("resource"):
            if "proxmox" in current_line:
                suggestions.append(CodeSuggestion(
                    completion_text="proxmox_vm_qemu",
                    suggestion_type="completion",
                    confidence=0.9,
                    description="Create a Proxmox VM resource",
                    insert_position=context.cursor_position,
                    category="terraform"
                ))
        
        # Variable completion
        elif current_line.startswith("var."):
            for var in context.variables_in_scope:
                suggestions.append(CodeSuggestion(
                    completion_text=var,
                    suggestion_type="completion",
                    confidence=0.8,
                    description=f"Variable: {var}",
                    insert_position=context.cursor_position,
                    category="terraform"
                ))
        
        # Block completion
        elif current_line.endswith("{"):
            if context.in_block == "resource" and "proxmox_vm_qemu" in context.preceding_lines[-1]:
                suggestions.append(CodeSuggestion(
                    completion_text='''  name        = "vm-name"
  target_node = "proxmox-node"
  
  cores  = 2
  memory = 2048
  
  disk {
    size    = "20G"
    type    = "scsi"
    storage = "local-lvm"
  }
  
  network {
    model  = "virtio"
    bridge = "vmbr0"
  }''',
                    suggestion_type="snippet",
                    confidence=0.9,
                    description="Complete Proxmox VM configuration",
                    insert_position=context.cursor_position,
                    category="terraform"
                ))
        
        return suggestions
    
    async def _ansible_suggestions(self, current_line: str, context: CodeContext) -> List[CodeSuggestion]:
        """Generate Ansible-specific suggestions."""
        suggestions = []
        
        # Task name completion
        if current_line.strip().startswith("- name:"):
            suggestions.append(CodeSuggestion(
                completion_text="Install and configure service",
                suggestion_type="completion",
                confidence=0.7,
                description="Descriptive task name",
                insert_position=context.cursor_position,
                category="ansible"
            ))
        
        # Module suggestions
        elif context.indentation_level > 0 and not current_line.strip().startswith("-"):
            common_modules = ["package", "service", "copy", "template", "file", "user", "group"]
            for module in common_modules:
                suggestions.append(CodeSuggestion(
                    completion_text=f"{module}:",
                    suggestion_type="completion",
                    confidence=0.6,
                    description=f"Ansible {module} module",
                    insert_position=context.cursor_position,
                    category="ansible"
                ))
        
        return suggestions
    
    async def _kubernetes_suggestions(self, current_line: str, context: CodeContext) -> List[CodeSuggestion]:
        """Generate Kubernetes-specific suggestions."""
        suggestions = []
        
        # API version suggestions
        if current_line.startswith("apiVersion:"):
            api_versions = ["v1", "apps/v1", "networking.k8s.io/v1", "extensions/v1beta1"]
            for version in api_versions:
                suggestions.append(CodeSuggestion(
                    completion_text=version,
                    suggestion_type="completion",
                    confidence=0.8,
                    description=f"Kubernetes API version {version}",
                    insert_position=context.cursor_position,
                    category="kubernetes"
                ))
        
        # Kind suggestions
        elif current_line.startswith("kind:"):
            kinds = ["Deployment", "Service", "ConfigMap", "Secret", "Ingress", "Pod"]
            for kind in kinds:
                suggestions.append(CodeSuggestion(
                    completion_text=kind,
                    suggestion_type="completion",
                    confidence=0.8,
                    description=f"Kubernetes {kind} resource",
                    insert_position=context.cursor_position,
                    category="kubernetes"
                ))
        
        return suggestions
    
    async def _bash_suggestions(self, current_line: str, context: CodeContext) -> List[CodeSuggestion]:
        """Generate Bash-specific suggestions."""
        suggestions = []
        
        # Shebang suggestion
        if context.cursor_position == 0 or current_line.startswith("#!"):
            suggestions.append(CodeSuggestion(
                completion_text="#!/bin/bash",
                suggestion_type="completion",
                confidence=0.9,
                description="Bash shebang",
                insert_position=context.cursor_position,
                category="bash"
            ))
        
        # Common commands
        if current_line.strip() == "":
            common_commands = ["echo", "cd", "ls", "mkdir", "cp", "mv", "rm", "grep", "sed", "awk"]
            for cmd in common_commands:
                suggestions.append(CodeSuggestion(
                    completion_text=cmd,
                    suggestion_type="completion",
                    confidence=0.5,
                    description=f"Bash command: {cmd}",
                    insert_position=context.cursor_position,
                    category="bash"
                ))
        
        return suggestions
    
    async def _check_common_mistakes(self, code: str, context: CodeContext) -> List[str]:
        """Check for common mistakes."""
        warnings = []
        
        mistakes = self.common_mistakes.get(context.file_type, [])
        for mistake in mistakes:
            if re.search(mistake["pattern"], code, re.IGNORECASE | re.MULTILINE):
                warnings.append(f"{mistake['issue']}: {mistake['suggestion']}")
        
        return warnings
    
    async def _check_security_issues(self, code: str, context: CodeContext) -> List[str]:
        """Check for security issues."""
        issues = []
        
        # Common security anti-patterns
        security_patterns = {
            "hardcoded_password": r'password\s*[:=]\s*["\']([^"\']+)["\']',
            "hardcoded_key": r'(?:api_key|secret|token)\s*[:=]\s*["\']([^"\']+)["\']',
            "insecure_protocol": r'http://(?!localhost|127\.0\.0\.1)',
            "weak_permissions": r'chmod\s+777',
            "sudo_without_validation": r'sudo\s+\w+.*\$\{.*\}'
        }
        
        for issue_type, pattern in security_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                if issue_type == "hardcoded_password":
                    issues.append("Hardcoded password detected - use variables or secrets")
                elif issue_type == "hardcoded_key":
                    issues.append("Hardcoded API key/secret detected - use secure storage")
                elif issue_type == "insecure_protocol":
                    issues.append("Insecure HTTP protocol - consider using HTTPS")
                elif issue_type == "weak_permissions":
                    issues.append("Overly permissive file permissions (777) detected")
                elif issue_type == "sudo_without_validation":
                    issues.append("Potentially unsafe sudo command with variables")
        
        return issues
    
    async def _check_best_practices(self, code: str, context: CodeContext) -> List[str]:
        """Check adherence to best practices."""
        recommendations = []
        
        practices = self.best_practices.get(context.file_type, [])
        
        if context.file_type == "terraform":
            # Check for missing descriptions
            if re.search(r'variable\s+"[^"]+"\s*{[^}]*}', code) and "description" not in code:
                recommendations.append("Add descriptions to variables for better documentation")
            
            # Check for hardcoded values
            if re.search(r'["\'][0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}["\']', code):
                recommendations.append("Consider using variables for IP addresses")
        
        elif context.file_type == "ansible":
            # Check for become usage
            if "become: yes" in code and "become_user" not in code:
                recommendations.append("Consider specifying become_user when using become")
        
        return recommendations


class IntelligentCodeCompletion:
    """Main intelligent code completion system."""
    
    def __init__(self):
        self.templates = InfrastructureCodeTemplates()
        self.analyzer = IntelligentCodeAnalyzer()
        self.performance_monitor = PerformanceMonitor()
        
        # Caching for performance on Intel N150
        self.suggestion_cache = {}
        self.cache_size_limit = 50  # Keep cache small for memory constraints
        
        logger.info("Intelligent code completion system initialized")
    
    def _get_cache_key(self, code: str, context: CodeContext) -> str:
        """Generate cache key for suggestions."""
        import hashlib
        content = f"{code[-100:]}:{context.file_type}:{context.cursor_position}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def get_suggestions(self, code: str, context: CodeContext) -> List[CodeSuggestion]:
        """Get intelligent code suggestions."""
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(code, context)
        if cache_key in self.suggestion_cache:
            logger.debug("Cache hit for code suggestions")
            return self.suggestion_cache[cache_key]
        
        try:
            suggestions = []
            
            # Get template-based suggestions
            template_suggestions = await self._get_template_suggestions(context)
            suggestions.extend(template_suggestions)
            
            # Get analyzer-based suggestions
            analysis = await self.analyzer.analyze_code(code, context)
            suggestions.extend(analysis.suggestions)
            
            # Remove duplicates and sort
            suggestions = self._deduplicate_suggestions(suggestions)
            suggestions.sort(key=lambda x: (x.priority, -x.confidence))
            
            # Cache results
            if len(self.suggestion_cache) < self.cache_size_limit:
                self.suggestion_cache[cache_key] = suggestions[:10]
            
            logger.info(
                "Code suggestions generated",
                suggestions_count=len(suggestions),
                processing_time=time.time() - start_time
            )
            
            return suggestions[:10]  # Return top 10 suggestions
            
        except Exception as e:
            logger.error("Failed to generate code suggestions", error=str(e))
            return []
    
    async def _get_template_suggestions(self, context: CodeContext) -> List[CodeSuggestion]:
        """Get template-based suggestions."""
        suggestions = []
        
        templates = self.templates.get_templates_for_context(context)
        
        for template in templates:
            # Check if template is relevant to current context
            if self._is_template_relevant(template, context):
                suggestions.append(CodeSuggestion(
                    completion_text=template["template"],
                    suggestion_type="template",
                    confidence=0.7,
                    description=template["description"],
                    insert_position=context.cursor_position,
                    category=template["category"],
                    priority=2
                ))
        
        return suggestions
    
    def _is_template_relevant(self, template: Dict[str, Any], context: CodeContext) -> bool:
        """Check if template is relevant to current context."""
        triggers = template.get("trigger", [])
        current_line = context.current_line.lower()
        
        for trigger in triggers:
            if trigger.lower() in current_line:
                return True
        
        return False
    
    def _deduplicate_suggestions(self, suggestions: List[CodeSuggestion]) -> List[CodeSuggestion]:
        """Remove duplicate suggestions."""
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            # Create a key based on completion text and type
            key = (suggestion.completion_text[:50], suggestion.suggestion_type)
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    async def analyze_and_suggest(self, code: str, context: CodeContext) -> Dict[str, Any]:
        """Comprehensive analysis and suggestions."""
        start_time = time.time()
        
        # Get suggestions
        suggestions = await self.get_suggestions(code, context)
        
        # Get full analysis
        analysis = await self.analyzer.analyze_code(code, context)
        
        return {
            "suggestions": [
                {
                    "text": s.completion_text,
                    "type": s.suggestion_type,
                    "confidence": s.confidence,
                    "description": s.description,
                    "category": s.category,
                    "priority": s.priority
                }
                for s in suggestions
            ],
            "analysis": {
                "syntax_errors": analysis.syntax_errors,
                "warnings": analysis.warnings,
                "security_issues": analysis.security_issues,
                "best_practices": analysis.best_practices
            },
            "processing_time": time.time() - start_time,
            "context": {
                "file_type": context.file_type,
                "in_block": context.in_block,
                "indentation_level": context.indentation_level
            }
        }
    
    def clear_cache(self):
        """Clear suggestion cache."""
        self.suggestion_cache.clear()
        logger.info("Code suggestion cache cleared")


# Global intelligent code completion instance
intelligent_completion = None

def get_intelligent_completion() -> IntelligentCodeCompletion:
    """Get global intelligent code completion instance."""
    global intelligent_completion
    
    if intelligent_completion is None:
        intelligent_completion = IntelligentCodeCompletion()
    
    return intelligent_completion


# Quick completion function for CLI usage
async def get_quick_suggestions(code: str, file_type: str, cursor_position: int = 0) -> List[Dict[str, Any]]:
    """Quick suggestions for CLI usage."""
    completion_system = get_intelligent_completion()
    
    context = CodeContext(
        file_type=file_type,
        cursor_position=cursor_position,
        current_line=code.split('\n')[cursor_position] if '\n' in code else code
    )
    
    suggestions = await completion_system.get_suggestions(code, context)
    
    return [
        {
            "text": s.completion_text,
            "description": s.description,
            "confidence": s.confidence,
            "type": s.suggestion_type
        }
        for s in suggestions[:5]  # Top 5 suggestions
    ]


# Export main classes and functions
__all__ = [
    'CodeSuggestion',
    'CodeContext',
    'CodeAnalysis',
    'IntelligentCodeCompletion',
    'InfrastructureCodeTemplates',
    'IntelligentCodeAnalyzer',
    'get_intelligent_completion',
    'get_quick_suggestions'
]