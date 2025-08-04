#!/usr/bin/env python3
"""
Core AI Chat Functionality Testing

Direct testing of the AI chat fixes without external dependencies.
This focuses on testing the core functionality that was supposedly fixed.
"""

import asyncio
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

class CoreAITester:
    """Core AI functionality tester without external dependencies."""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
        print("🔧 Core AI Chat Functionality Testing")
        print("=" * 50)
        print("Testing critical AI chat fixes for infrastructure automation")
        print("=" * 50)
    
    def log_result(self, test_name, status, details, issues=None):
        """Log a test result."""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "issues": issues or [],
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥", "SKIP": "⏭️"}.get(status, "❓")
        print(f"\n{status_icon} {test_name}: {status}")
        print(f"   Details: {details}")
        if issues:
            for issue in issues:
                print(f"   ⚠️  {issue}")
    
    async def test_basic_imports(self):
        """Test that core components can be imported."""
        print("\n🧪 Testing Basic Imports...")
        
        try:
            # Test importing key components
            from src.proxmox_ai.cli.commands.ai_commands import _fallback_infrastructure_response
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            self.log_result(
                "Import Core AI Components",
                "PASS",
                "Successfully imported core AI chat components"
            )
            return True
            
        except ImportError as e:
            self.log_result(
                "Import Core AI Components", 
                "ERROR",
                f"Failed to import core components: {e}"
            )
            return False
        except Exception as e:
            self.log_result(
                "Import Core AI Components",
                "ERROR", 
                f"Unexpected error: {e}"
            )
            return False
    
    async def test_fallback_infrastructure_response(self):
        """Test the fallback infrastructure response functionality."""
        print("\n🧪 Testing Fallback Infrastructure Response...")
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _fallback_infrastructure_response
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test the critical request that was failing before
            test_input = "Generate a VM for hosting 5 AI agents for development"
            
            # Call the fallback response function
            response = await _fallback_infrastructure_response(
                ai_client=optimized_ai_client,
                user_input=test_input,
                skill_level="intermediate",
                mode="infrastructure"
            )
            
            # Analyze the response
            issues = []
            
            # Check if it's a generic response (the original problem)
            generic_phrases = [
                "tell me more about your goals",
                "could you provide more specific details",
                "what are your requirements"
            ]
            is_generic = any(phrase in response.lower() for phrase in generic_phrases)
            
            if is_generic:
                issues.append("CRITICAL: Still providing generic responses - core issue NOT FIXED")
            
            # Check for infrastructure content
            infrastructure_indicators = [
                "terraform", "resource", "vm", "memory", "cores", "ai-agents", 
                "development", "configuration", "hcl", "proxmox"
            ]
            
            infrastructure_score = sum(1 for indicator in infrastructure_indicators 
                                     if indicator in response.lower())
            
            if infrastructure_score < 5:
                issues.append("Insufficient infrastructure-specific content")
            
            # Check for code blocks
            has_code_block = "```" in response
            if not has_code_block:
                issues.append("No code blocks found in response")
            
            # Check for deployment guidance
            has_deployment_guidance = any(term in response.lower() for term in [
                "terraform init", "terraform apply", "deployment", "next steps"
            ])
            
            if not has_deployment_guidance:
                issues.append("No deployment guidance provided")
            
            # Determine status
            if is_generic:
                status = "FAIL"
            elif not issues:
                status = "PASS"
            elif len(issues) <= 2:
                status = "PARTIAL"
            else:
                status = "FAIL"
            
            self.log_result(
                "Fallback Infrastructure Response",
                status,
                f"Response length: {len(response)}, Infrastructure score: {infrastructure_score}/{len(infrastructure_indicators)}, Generic: {is_generic}",
                issues
            )
            
            # Show response preview for manual verification
            print(f"   📝 Response Preview (first 400 chars):")
            print(f"      {response[:400]}...")
            
            return status == "PASS"
            
        except Exception as e:
            self.log_result(
                "Fallback Infrastructure Response",
                "ERROR",
                f"Exception during testing: {e}"
            )
            return False
    
    async def test_ai_client_configuration(self):
        """Test AI client configuration."""
        print("\n🧪 Testing AI Client Configuration...")
        
        try:
            from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
            
            # Test client configuration
            model_info = optimized_ai_client.get_model_info()
            host = optimized_ai_client.ollama_host
            
            issues = []
            
            # Check for local configuration
            if "localhost" not in host and "127.0.0.1" not in host:
                issues.append("AI client not configured for local processing")
            
            # Check model configuration
            if not model_info.get("current_model"):
                issues.append("No current model configured")
            
            status = "PASS" if not issues else "FAIL"
            
            self.log_result(
                "AI Client Configuration",
                status,
                f"Host: {host}, Model: {model_info.get('current_model', 'Unknown')}",
                issues
            )
            
            return status == "PASS"
            
        except Exception as e:
            self.log_result(
                "AI Client Configuration",
                "ERROR",
                f"Exception during testing: {e}"
            )
            return False
    
    async def test_code_extraction(self):
        """Test code extraction functionality."""
        print("\n🧪 Testing Code Extraction...")
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _extract_code_from_response
            
            # Test with sample response containing Terraform code
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
            
            issues = []
            
            if not extracted_code:
                issues.append("Code extraction failed - returned None")
            elif "resource" not in extracted_code:
                issues.append("Extracted code missing expected resource definition")
            elif "ai-agents-dev" not in extracted_code:
                issues.append("Extracted code missing expected VM name")
            
            status = "PASS" if not issues else "FAIL"
            
            self.log_result(
                "Code Extraction",
                status,
                f"Extracted {len(extracted_code) if extracted_code else 0} characters of code",
                issues
            )
            
            if extracted_code:
                print(f"   📝 Extracted Code:")
                print(f"      {extracted_code[:200]}...")
            
            return status == "PASS"
            
        except Exception as e:
            self.log_result(
                "Code Extraction",
                "ERROR",
                f"Exception during testing: {e}"
            )
            return False
    
    async def test_vm_template_provision(self):
        """Test VM template provision functionality.""" 
        print("\n🧪 Testing VM Template Provision...")
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _provide_vm_template_for_ai_agents
            
            # Test the VM template function
            response = _provide_vm_template_for_ai_agents()
            
            issues = []
            
            # Check for essential VM template content
            required_elements = [
                "terraform", "resource", "proxmox_vm_qemu", "ai-agents-dev",
                "memory", "cores", "8192", "4", "ubuntu", "deployment"
            ]
            
            missing_elements = [elem for elem in required_elements if elem not in response.lower()]
            
            if missing_elements:
                issues.append(f"Missing required elements: {', '.join(missing_elements)}")
            
            if len(response) < 2000:
                issues.append("VM template response too short for comprehensive configuration")
            
            # Check for deployment instructions
            has_deployment_steps = any(step in response.lower() for step in [
                "terraform init", "terraform apply", "terraform plan"
            ])
            
            if not has_deployment_steps:
                issues.append("Missing deployment instructions")
            
            # Check for security considerations
            has_security_info = any(security in response.lower() for security in [
                "ssh", "security", "firewall", "access"
            ])
            
            if not has_security_info:
                issues.append("Missing security configuration guidance")
            
            status = "PASS" if not issues else "FAIL"
            
            self.log_result(
                "VM Template Provision",
                status,
                f"Template length: {len(response)}, Missing elements: {len(missing_elements)}",
                issues
            )
            
            return status == "PASS"
            
        except Exception as e:
            self.log_result(
                "VM Template Provision",
                "ERROR", 
                f"Exception during testing: {e}"
            )
            return False
    
    async def test_security_patterns(self):
        """Test for security patterns in generated responses."""
        print("\n🧪 Testing Security Patterns...")
        
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _provide_vm_template_for_ai_agents
            
            # Get a sample response
            response = _provide_vm_template_for_ai_agents()
            
            issues = []
            
            # Check for hardcoded credentials (this should NOT be present)
            import re
            credential_patterns = [
                r'password\s*=\s*"[^"]*"',
                r'pm_password\s*=\s*"[^"]*"'
            ]
            
            credentials_found = []
            for pattern in credential_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                # Filter out variable references
                real_credentials = [m for m in matches if not any(var in m.lower() for var in ["var.", "${", "your-"])]
                if real_credentials:
                    credentials_found.extend(real_credentials)
            
            if credentials_found:
                issues.append(f"CRITICAL: Found {len(credentials_found)} hardcoded credentials")
            
            # Check for proper variable usage
            uses_variables = "var." in response or "${" in response
            if not uses_variables:
                issues.append("Should use variables for sensitive configuration")
            
            # Check for sensitive flag usage
            uses_sensitive = "sensitive" in response
            if not uses_sensitive:
                issues.append("Should mark sensitive variables appropriately")
            
            status = "PASS" if not credentials_found else "FAIL"
            
            self.log_result(
                "Security Patterns",
                status,
                f"Credentials found: {len(credentials_found)}, Uses variables: {uses_variables}, Uses sensitive: {uses_sensitive}",
                issues
            )
            
            return status == "PASS"
            
        except Exception as e:
            self.log_result(
                "Security Patterns",
                "ERROR",
                f"Exception during testing: {e}"
            )
            return False
    
    def generate_final_report(self):
        """Generate final test report."""
        execution_time = time.time() - self.start_time
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "FAIL")
        error_tests = sum(1 for r in self.test_results if r["status"] == "ERROR")
        
        # Check for critical failures
        critical_failures = [
            r for r in self.test_results 
            if r["status"] == "FAIL" and any("CRITICAL" in issue for issue in r["issues"])
        ]
        
        print("\n" + "=" * 60)
        print("🔍 CORE AI CHAT FUNCTIONALITY TEST REPORT")
        print("=" * 60)
        
        if critical_failures:
            overall_status = "CRITICAL_FAIL"
            status_icon = "🚨"
        elif error_tests > 0:
            overall_status = "ERROR"
            status_icon = "💥"
        elif failed_tests > 0:
            overall_status = "FAIL"
            status_icon = "❌"
        else:
            overall_status = "PASS"
            status_icon = "✅"
        
        print(f"\n🎯 OVERALL STATUS: {status_icon} {overall_status}")
        print(f"📊 TEST SUMMARY: {passed_tests}/{total_tests} passed ({passed_tests/total_tests:.1%})")
        print(f"⏱️  EXECUTION TIME: {execution_time:.1f} seconds")
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   • {failure['test_name']}: {failure['details']}")
                for issue in failure["issues"]:
                    if "CRITICAL" in issue:
                        print(f"     🚨 {issue}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}.get(result["status"], "❓")
            print(f"   {status_icon} {result['test_name']}: {result['status']}")
        
        # Key validation criteria
        print(f"\n✅ KEY VALIDATION CRITERIA:")
        
        # Check if the core issue is fixed
        generic_response_issue = any(
            "CRITICAL" in issue and "generic" in issue.lower()
            for result in self.test_results
            for issue in result["issues"]
        )
        
        print(f"   {'❌' if generic_response_issue else '✅'} AI no longer provides generic responses")
        print(f"   {'✅' if passed_tests >= total_tests * 0.8 else '❌'} Core functionality is working")
        print(f"   {'✅' if not critical_failures else '❌'} No critical security issues")
        
        # Save results
        results_file = "core_ai_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "overall_status": overall_status,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "execution_time": execution_time,
                "test_results": self.test_results,
                "critical_failures": len(critical_failures),
                "generic_response_issue_fixed": not generic_response_issue
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Final assessment
        print(f"\n🏆 FINAL ASSESSMENT:")
        if overall_status == "PASS":
            print("   ✅ AI chat functionality fixes are working correctly!")
            print("   ✅ Core issue with generic responses has been resolved")
            print("   ✅ System is ready for infrastructure automation use")
        elif overall_status == "CRITICAL_FAIL":
            print("   🚨 CRITICAL FAILURE: Core AI chat functionality is still broken")
            print("   🚨 The main issue (generic responses) has NOT been fixed")
            print("   🚨 Immediate remediation required")
        else:
            print("   ⚠️  Partial success - some issues remain")
            print("   🔧 Review failed tests and address issues")
        
        print("=" * 60)
        
        return overall_status

async def main():
    """Run core AI functionality tests."""
    tester = CoreAITester()
    
    try:
        # Run core tests in sequence
        print("Starting core AI chat functionality testing...")
        
        await tester.test_basic_imports()
        await tester.test_fallback_infrastructure_response()
        await tester.test_ai_client_configuration()
        await tester.test_code_extraction()
        await tester.test_vm_template_provision()
        await tester.test_security_patterns()
        
        # Generate final report
        overall_status = tester.generate_final_report()
        
        # Return appropriate exit code
        if overall_status == "PASS":
            return 0
        elif overall_status == "CRITICAL_FAIL":
            return 2
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Testing framework error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)