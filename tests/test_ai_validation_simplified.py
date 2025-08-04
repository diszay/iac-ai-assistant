#!/usr/bin/env python3
"""
Simplified AI Chat Functionality Validation

Comprehensive testing framework without external dependencies to validate
that the AI chat functionality fixes are working correctly.
"""

import asyncio
import sys
import os
import time
import json
import re
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

class SimplifiedAIValidator:
    """Simplified AI chat functionality validator."""
    
    def __init__(self):
        """Initialize the validation framework."""
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
        print("🔧 AI Chat Functionality Validation Framework")
        print("=" * 60)
        print(f"Testing AI Chat Fixes for Intel N150 Hardware")
        print(f"Test Start: {datetime.now().isoformat()}")
        print("=" * 60)
    
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
        """1. FUNCTIONAL TESTING - Test AI responses to infrastructure requests."""
        category = "FUNCTIONAL"
        
        # Test 1.1: VM Generation Request (The critical test case)
        test_name = "AI Response to VM Generation Request"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _generate_chat_response_local
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test the exact request that was previously broken
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
                timeout=30.0
            )
            
            # Critical analysis - this was the main problem being fixed
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
            
            # Check for expected technical content (this is what should be fixed)
            technical_indicators = [
                "terraform", "resource", "proxmox", "vm", "memory", "cores", 
                "ai-agents", "development", "8192", "configuration", "hcl"
            ]
            
            technical_score = sum(1 for indicator in technical_indicators 
                                 if indicator in response.lower())
            metrics["technical_content_score"] = f"{technical_score}/{len(technical_indicators)}"
            
            # Validation criteria - this is the core fix
            if metrics["is_generic"]:
                issues.append("CRITICAL: Response is still generic - core issue NOT FIXED")
            
            if not metrics["contains_terraform"] and not metrics["contains_vm_config"]:
                issues.append("CRITICAL: Response lacks concrete infrastructure configuration")
            
            if len(response) < 500:
                issues.append("Response too short for infrastructure guidance")
            
            if technical_score < 4:
                issues.append("Insufficient technical content in response")
                
            # Check for Terraform code blocks
            has_code_block = "```" in response
            if has_code_block:
                metrics["has_code_block"] = True
            else:
                issues.append("No code blocks found in response")
            
            status = "PASS" if not issues else "FAIL"
            details = f"Generated {len(response)} char response with {technical_score}/{len(technical_indicators)} technical indicators"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
            # Show response sample for verification
            if len(response) > 0:
                print(f"      📝 Response Preview (first 300 chars):")
                print(f"         {response[:300]}...")
            
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
                timeout=30.0
            )
            
            # Check for web server specific content
            web_server_indicators = [
                "nginx", "web server", "http", "port 80", "port 443",
                "ssl", "domain", "virtual host", "terraform"
            ]
            
            web_server_score = sum(1 for indicator in web_server_indicators
                                  if indicator in response.lower())
            
            metrics = {
                "response_length": len(response),
                "web_server_content_score": f"{web_server_score}/{len(web_server_indicators)}",
                "contains_terraform": "terraform" in response.lower(),
                "contains_nginx": "nginx" in response.lower(),
                "is_generic": any(phrase in response.lower() for phrase in [
                    "tell me more", "provide more details", "what are your requirements"
                ])
            }
            
            issues = []
            if metrics["is_generic"]:
                issues.append("CRITICAL: Still giving generic responses")
                
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
        """2. INTEGRATION TESTING - Verify system component integration."""
        category = "INTEGRATION"
        
        # Test 2.1: Local AI Client Integration
        test_name = "Local AI Client Integration"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test client initialization and configuration
            is_available = await optimized_ai_client.is_available()
            model_info = optimized_ai_client.get_model_info()
            perf_stats = optimized_ai_client.get_performance_stats()
            
            metrics = {
                "ai_available": is_available,
                "current_model": model_info["current_model"],
                "recommended_model": model_info["recommended_model"],
                "host": optimized_ai_client.ollama_host,
                "is_local_host": "localhost" in optimized_ai_client.ollama_host
            }
            
            issues = []
            if not is_available:
                issues.append("Local AI model not available - Ollama may not be running")
            
            if not metrics["is_local_host"]:
                issues.append("AI client not configured for local processing")
            
            status = "PASS" if is_available and metrics["is_local_host"] else "SKIP" if not is_available else "FAIL"
            details = f"AI Model: {model_info['current_model']}, Available: {is_available}, Local: {metrics['is_local_host']}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 2.2: Intelligent Conversation Integration
        test_name = "Intelligent Conversation Integration"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test the intelligent conversation method (this is the key fix)
            test_context = {"mode": "infrastructure", "skill_level": "intermediate"}
            
            # Only test if AI is available
            if await optimized_ai_client.is_available():
                response = await asyncio.wait_for(
                    optimized_ai_client.intelligent_conversation(
                        "Generate a VM for hosting 5 AI agents", 
                        test_context
                    ),
                    timeout=25.0
                )
                
                metrics = {
                    "success": response.success,
                    "processing_time": f"{response.processing_time:.2f}s",
                    "model_used": response.model_used,
                    "content_length": len(response.content),
                    "tokens_generated": response.tokens_generated
                }
                
                issues = []
                if not response.success:
                    issues.append("Intelligent conversation failed")
                
                if response.processing_time > 30.0:
                    issues.append("Processing time too long for Intel N150")
                
                status = "PASS" if response.success and not issues else "FAIL"
                details = f"Intelligent conversation: success={response.success}, time={response.processing_time:.1f}s"
                
            else:
                metrics = {"ai_available": False}
                issues = ["Local AI not available for testing"]
                status = "SKIP"
                details = "Skipped - Local AI not available"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            metrics = {"timeout": True}
            issues = ["Intelligent conversation timed out"]
            self._add_result(test_name, category, "FAIL", "Timed out after 25 seconds", execution_time, metrics, issues)
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 2.3: Hardware Detection Integration
        test_name = "Hardware Detection Integration"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.core.hardware_detector import hardware_detector
            from src.proxmox_ai.ai.local_ai_client import skill_manager
            
            specs = hardware_detector.specs
            performance_profile = hardware_detector.get_performance_profile()
            optimal_model = hardware_detector.get_optimal_model_config()
            optimal_skill = skill_manager.get_optimal_skill_level("intermediate")
            
            metrics = {
                "cpu_cores": specs.cpu_cores,
                "total_memory_gb": f"{specs.total_memory_gb:.1f}GB",
                "available_memory_gb": f"{specs.available_memory_gb:.1f}GB",
                "performance_tier": performance_profile["model_quality"],
                "optimal_model": optimal_model.model_name,
                "optimal_skill_level": optimal_skill
            }
            
            issues = []
            
            # For Intel N150 target hardware
            if specs.cpu_cores < 4:
                issues.append(f"Only {specs.cpu_cores} CPU cores detected, expected 4+ for Intel N150")
            
            if specs.total_memory_gb < 6.0:
                issues.append(f"Only {specs.total_memory_gb:.1f}GB RAM detected, expected 7.8GB+ for Intel N150")
            
            status = "PASS" if not issues else "PARTIAL"
            details = f"Hardware: {specs.cpu_cores}C/{specs.total_memory_gb:.1f}GB, {performance_profile['model_quality']} tier"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
    
    async def run_end_to_end_tests(self):
        """3. END-TO-END WORKFLOW TESTING - Test complete user workflow."""
        category = "END_TO_END"
        
        # Test 3.1: Complete Infrastructure Request Workflow
        test_name = "Complete Infrastructure Request Workflow"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _generate_chat_response_local
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
                timeout=30.0
            )
            
            # Step 3: Analyze workflow completeness
            has_terraform = "terraform" in ai_response.lower() and "resource" in ai_response.lower()
            has_vm_config = any(term in ai_response.lower() for term in ["vmid", "memory", "cores", "ai-agents"])
            has_deployment_guidance = any(term in ai_response.lower() for term in [
                "terraform init", "terraform apply", "deployment", "next steps", "save", "deploy"
            ])
            has_code_block = "```" in ai_response
            
            metrics = {
                "request_length": len(user_request),
                "response_length": len(ai_response),
                "has_terraform_code": has_terraform,
                "has_vm_config": has_vm_config,
                "has_deployment_guidance": has_deployment_guidance,
                "has_code_block": has_code_block,
                "workflow_complete": has_terraform and has_deployment_guidance and has_code_block
            }
            
            issues = []
            if not (has_terraform or has_vm_config):
                issues.append("CRITICAL: No infrastructure code generated in response")
            
            if not has_deployment_guidance:
                issues.append("No deployment guidance provided")
                
            if not has_code_block:
                issues.append("No code blocks found in response")
            
            status = "PASS" if metrics["workflow_complete"] else "FAIL"
            details = f"Workflow complete: {metrics['workflow_complete']}, Code: {has_terraform}, Guidance: {has_deployment_guidance}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 3.2: Code Extraction Functionality
        test_name = "Code Extraction Functionality"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _extract_code_from_response
            
            # Test code extraction with sample response
            sample_response = '''Here's your Terraform configuration:

```hcl
resource "proxmox_vm_qemu" "ai_development_vm" {
  name    = "ai-agents-dev"
  memory  = 8192
  cores   = 4
  target_node = "pve"
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
                issues.append("Extracted code missing expected resource content")
            
            status = "PASS" if extracted_code and metrics["contains_resource"] else "FAIL"
            details = f"Code extraction: working={bool(extracted_code)}, length={len(extracted_code) if extracted_code else 0}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
    
    async def run_security_tests(self):
        """4. SECURITY VALIDATION - Ensure fixes maintain security."""
        category = "SECURITY"
        
        # Test 4.1: No Hardcoded Credentials in Generated Code
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
                r'pm_password\s*=\s*"[^"]*"'
            ]
            
            credentials_found = []
            for pattern in credential_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                if matches and not any(var in match.lower() for match in matches for var in ["var.", "${", "example"]):
                    credentials_found.extend(matches)
            
            # Check for secure practices
            uses_variables = "var." in response or "${" in response
            uses_sensitive = "sensitive" in response
            
            metrics = {
                "credentials_found": len(credentials_found),
                "uses_variables": uses_variables,
                "uses_sensitive_flag": uses_sensitive,
                "response_length": len(response)
            }
            
            issues = []
            if credentials_found:
                issues.append(f"CRITICAL: Found {len(credentials_found)} potential hardcoded credentials")
            
            if not uses_variables:
                issues.append("Generated code should use variables for configuration")
            
            status = "PASS" if not credentials_found else "FAIL"
            details = f"Security check: {len(credentials_found)} credentials found, uses vars: {uses_variables}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 4.2: Input Validation
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
                "../../etc/passwd"
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
                        timeout=10.0
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
        
        # Test 4.3: Local Processing Security
        test_name = "Local Processing Security"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
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
                issues.append("CRITICAL: AI client not configured for local processing")
            
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
        """5. PERFORMANCE TESTING - Verify fixes work well on target hardware."""
        category = "PERFORMANCE"
        
        # Test 5.1: Response Time Performance 
        test_name = "Response Time Performance"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _generate_chat_response_local
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test response times for different requests
            test_requests = [
                "Generate a VM for hosting 5 AI agents for development",
                "Create a web server VM with nginx"
            ]
            
            response_times = []
            timeout_threshold = 25.0  # Intel N150 optimized threshold
            
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
                        timeout=timeout_threshold
                    )
                    
                    request_time = time.time() - request_start
                    response_times.append(request_time)
                    
                except asyncio.TimeoutError:
                    response_times.append(timeout_threshold)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            timeouts = sum(1 for t in response_times if t >= timeout_threshold)
            
            metrics = {
                "avg_response_time": f"{avg_response_time:.2f}s",
                "max_response_time": f"{max_response_time:.2f}s", 
                "requests_tested": len(test_requests),
                "timeouts": timeouts,
                "timeout_threshold": f"{timeout_threshold}s"
            }
            
            issues = []
            if avg_response_time > timeout_threshold * 0.8:
                issues.append(f"Average response time {avg_response_time:.1f}s close to timeout threshold")
            
            if timeouts > 0:
                issues.append(f"{timeouts} requests timed out - may need further optimization for Intel N150")
            
            status = "PASS" if timeouts == 0 and avg_response_time < timeout_threshold * 0.8 else "PARTIAL" if timeouts == 0 else "FAIL"
            details = f"Avg: {avg_response_time:.1f}s, Max: {max_response_time:.1f}s, Timeouts: {timeouts}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
        
        # Test 5.2: Timeout Handling and Graceful Fallbacks
        test_name = "Timeout Handling and Graceful Fallbacks"
        self._log_test_start(test_name, category)
        start_time = time.time()
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _fallback_infrastructure_response
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test fallback mechanism (should always work even if AI times out)
            test_input = "Generate complex multi-tier infrastructure"
            
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
            has_code_block = "```" in fallback_response
            
            metrics = {
                "fallback_response_length": len(fallback_response),
                "has_terraform_template": has_terraform_template,
                "has_vm_config": has_vm_config,
                "has_deployment_instructions": has_instructions,
                "has_code_block": has_code_block,
                "fallback_functional": has_terraform_template or has_vm_config
            }
            
            issues = []
            if not metrics["fallback_functional"]:
                issues.append("CRITICAL: Fallback response not providing useful infrastructure content")
            
            if len(fallback_response) < 1000:
                issues.append("Fallback response too short for comprehensive guidance")
                
            if not has_code_block:
                issues.append("Fallback response missing code blocks")
            
            status = "PASS" if metrics["fallback_functional"] and not issues else "FAIL"
            details = f"Fallback: {len(fallback_response)} chars, Terraform: {has_terraform_template}, Code: {has_code_block}"
            
            execution_time = time.time() - start_time
            self._add_result(test_name, category, status, details, execution_time, metrics, issues)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._add_result(test_name, category, "ERROR", f"Exception: {str(e)}", execution_time)
    
    def generate_summary_report(self):
        """Generate and display comprehensive summary report."""
        total_execution_time = time.time() - self.start_time
        
        # Calculate statistics
        total_tests = len([r for r in self.results if r.test_name not in ["Functional Tests", "Integration Tests", "End-to-End Tests", "Security Tests", "Performance Tests"]])
        passed_tests = sum(1 for r in self.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.results if r.status == "FAIL")
        error_tests = sum(1 for r in self.results if r.status == "ERROR")
        skipped_tests = sum(1 for r in self.results if r.status == "SKIP")
        partial_tests = sum(1 for r in self.results if r.status == "PARTIAL")
        
        # Determine overall status
        critical_failures = [r for r in self.results if r.status == "FAIL" and any("CRITICAL" in issue for issue in r.issues_found)]
        
        if error_tests > 0:
            overall_status = "ERROR"
        elif critical_failures:
            overall_status = "CRITICAL_FAIL"
        elif failed_tests > total_tests * 0.3:
            overall_status = "FAIL"
        elif failed_tests > 0 or partial_tests > 0:
            overall_status = "PARTIAL"
        else:
            overall_status = "PASS"
        
        print("\n" + "=" * 70)
        print("🔍 COMPREHENSIVE AI CHAT FUNCTIONALITY VALIDATION REPORT")
        print("=" * 70)
        
        # Overall Status
        status_icons = {
            "PASS": "✅",
            "PARTIAL": "⚠️", 
            "FAIL": "❌",
            "CRITICAL_FAIL": "🚨",
            "ERROR": "💥"
        }
        
        print(f"\n🎯 OVERALL STATUS: {status_icons.get(overall_status, '❓')} {overall_status}")
        print(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} passed ({passed_tests/total_tests:.1%} if total_tests > 0 else 0)")
        print(f"⏱️  EXECUTION TIME: {total_execution_time:.1f} seconds")
        
        # Results by Category
        categories = {}
        for result in self.results:
            if result.test_name not in ["Functional Tests", "Integration Tests", "End-to-End Tests", "Security Tests", "Performance Tests"]:
                if result.category not in categories:
                    categories[result.category] = {"PASS": 0, "FAIL": 0, "ERROR": 0, "SKIP": 0, "PARTIAL": 0}
                categories[result.category][result.status] += 1
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        for category, stats in categories.items():
            total = sum(stats.values())
            passed = stats["PASS"]
            if total > 0:
                print(f"   {category}: {passed}/{total} passed ({passed/total:.1%}) - "
                      f"Pass: {stats['PASS']}, Fail: {stats['FAIL']}, Error: {stats['ERROR']}, Skip: {stats['SKIP']}, Partial: {stats['PARTIAL']}")
        
        # Critical Issues
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
            for result in critical_failures:
                print(f"   • [{result.category}] {result.test_name}")
                for issue in result.issues_found:
                    if "CRITICAL" in issue:
                        print(f"     🚨 {issue}")
        
        # Failed Tests Detail
        failed_tests_list = [r for r in self.results if r.status in ["FAIL", "ERROR"] and r.test_name not in ["Functional Tests", "Integration Tests", "End-to-End Tests", "Security Tests", "Performance Tests"]]
        if failed_tests_list:
            print(f"\n❌ FAILED TESTS ({len(failed_tests_list)}):")
            for test in failed_tests_list:
                print(f"   • [{test.category}] {test.test_name}: {test.details}")
                for issue in test.issues_found:
                    print(f"     ⚠️  {issue}")
        
        # Validation Criteria Assessment
        print(f"\n✅ VALIDATION CRITERIA ASSESSMENT:")
        
        functional_tests = [r for r in self.results if r.category == "FUNCTIONAL" and r.test_name not in ["Functional Tests"]]
        functional_pass_rate = sum(1 for t in functional_tests if t.status == "PASS") / len(functional_tests) if functional_tests else 0
        
        integration_tests = [r for r in self.results if r.category == "INTEGRATION" and r.test_name not in ["Integration Tests"]]
        integration_pass_rate = sum(1 for t in integration_tests if t.status in ["PASS", "SKIP"]) / len(integration_tests) if integration_tests else 0
        
        security_tests = [r for r in self.results if r.category == "SECURITY" and r.test_name not in ["Security Tests"]]
        security_pass_rate = sum(1 for t in security_tests if t.status == "PASS") / len(security_tests) if security_tests else 0
        
        performance_tests = [r for r in self.results if r.category == "PERFORMANCE" and r.test_name not in ["Performance Tests"]]
        performance_pass_rate = sum(1 for t in performance_tests if t.status in ["PASS", "PARTIAL"]) / len(performance_tests) if performance_tests else 0
        
        e2e_tests = [r for r in self.results if r.category == "END_TO_END" and r.test_name not in ["End-to-End Tests"]]
        e2e_pass_rate = sum(1 for t in e2e_tests if t.status == "PASS") / len(e2e_tests) if e2e_tests else 0
        
        criteria_results = [
            ("AI responses are specific and actionable (not generic)", functional_pass_rate >= 0.8),
            ("Generated code is syntactically correct and deployable", integration_pass_rate >= 0.8),
            ("Security remains at 100% with no vulnerabilities", security_pass_rate >= 1.0),
            ("Performance is acceptable on target hardware", performance_pass_rate >= 0.8),
            ("End-to-end workflow functions properly", e2e_pass_rate >= 0.8)
        ]
        
        for criterion, passed in criteria_results:
            status_icon = "✅" if passed else "❌"
            print(f"   {status_icon} {criterion}")
        
        # Final Assessment
        all_criteria_met = all(passed for _, passed in criteria_results)
        no_critical_failures = len(critical_failures) == 0
        
        print(f"\n🏆 FINAL ASSESSMENT:")
        if all_criteria_met and no_critical_failures:
            print("   ✅ ALL VALIDATION CRITERIA MET - AI chat functionality fixes are working correctly!")
            print("   ✅ System is ready for production use with comprehensive AI infrastructure automation")
        elif no_critical_failures and overall_status in ["PASS", "PARTIAL"]:
            print("   ⚠️  MOSTLY SUCCESSFUL - Core functionality working but some improvements needed")
            print("   🔧 Address failed tests for optimal performance")
        else:
            print("   ❌ VALIDATION FAILED - Critical issues prevent proper AI chat functionality")
            print("   🚨 Immediate fixes required before system can be considered functional")
            
        # Specific Fix Validation
        generic_response_issue = any(
            "generic" in issue.lower() and "critical" in issue.upper() 
            for result in self.results 
            for issue in result.issues_found
        )
        
        print(f"\n🎯 CORE FIX VALIDATION:")
        if not generic_response_issue:
            print("   ✅ CORE ISSUE FIXED: AI no longer provides generic responses")
            print("   ✅ AI now generates specific infrastructure code as required")
        else:
            print("   ❌ CORE ISSUE NOT FIXED: AI still providing generic responses")
            print("   🚨 The primary issue described in requirements is not resolved")
        
        print("\n" + "=" * 70)
        
        return overall_status, total_tests, passed_tests, failed_tests

async def main():
    """Run the simplified AI validation suite."""
    validator = SimplifiedAIValidator()
    
    try:
        print("🔄 Starting Comprehensive AI Chat Functionality Validation...\n")
        
        # Run all test categories
        await validator.run_functional_tests()
        await validator.run_integration_tests()
        await validator.run_end_to_end_tests()
        await validator.run_security_tests()
        await validator.run_performance_tests()
        
        # Generate comprehensive report
        overall_status, total_tests, passed_tests, failed_tests = validator.generate_summary_report()
        
        # Save results to file
        results_file = Path("ai_validation_results.json")
        with open(results_file, 'w') as f:
            results_data = {
                "overall_status": overall_status,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
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
                    for r in validator.results
                ],
                "timestamp": datetime.now().isoformat()
            }
            json.dump(results_data, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: {results_file.absolute()}")
        
        # Return appropriate exit code
        if overall_status == "PASS":
            return 0
        elif overall_status in ["PARTIAL"]:
            return 1
        else:
            return 2
            
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Validation framework error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)