#!/usr/bin/env python3
"""
Quick test script for enhanced AI assistant capabilities.

Tests the core functionality without requiring all dependencies.
"""

import subprocess
import json
import time


def test_ollama_availability():
    """Test if Ollama is available and has the correct model."""
    print("🔍 Testing Ollama availability...")
    
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = result.stdout
            if "llama3.1:8b-instruct-q4_0" in models:
                print("✅ Ollama is available with llama3.1:8b-instruct-q4_0 model")
                return True
            else:
                print("❌ llama3.1:8b-instruct-q4_0 model not found")
                print("Available models:")
                print(models)
                return False
        else:
            print("❌ Ollama not responding")
            return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False


def test_basic_api_call():
    """Test basic API call to Ollama."""
    print("\n🧠 Testing basic AI API call...")
    
    try:
        import requests
        
        payload = {
            "model": "llama3.1:8b-instruct-q4_0",
            "prompt": "What is Proxmox VE? Answer in 2-3 sentences.",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 1024,
                "num_thread": 3,
                "num_predict": 100
            }
        }
        
        print("Making API request...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            
            print(f"✅ API call successful ({end_time - start_time:.2f}s)")
            print(f"Response: {content[:200]}...")
            
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            return False
            
    except ImportError:
        print("❌ requests library not available")
        return False
    except Exception as e:
        print(f"❌ Error in API call: {e}")
        return False


def test_technical_knowledge():
    """Test AI's technical knowledge capabilities."""
    print("\n🎯 Testing technical knowledge integration...")
    
    try:
        import requests
        
        # Test infrastructure generation
        technical_prompt = """You are a world-class Infrastructure as Code expert specializing in enterprise-grade solutions.

Your expertise spans:
- Proxmox VE virtualization and cluster management
- Infrastructure as Code (Terraform, Ansible, Pulumi, CloudFormation)
- Containerization and orchestration (Docker, Kubernetes, microservices)
- System engineering and Linux administration
- Network design and security architecture

USER REQUEST: Create a Terraform configuration for a basic Proxmox VM with 2GB RAM, 2 CPU cores, and Ubuntu 22.04. Include security best practices.

Please provide a complete, working configuration with security hardening measures and comprehensive comments."""
        
        payload = {
            "model": "llama3.1:8b-instruct-q4_0",
            "prompt": technical_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 2048,
                "num_thread": 3,
                "num_predict": 512,
                "top_k": 40,
                "repeat_penalty": 1.1
            }
        }
        
        print("Testing technical knowledge with Terraform generation...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=90
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            
            # Check for technical indicators
            technical_indicators = [
                "terraform", "resource", "proxmox_vm", "provider", 
                "security", "variable", "output", "cpu", "memory"
            ]
            
            found_indicators = [ind for ind in technical_indicators if ind.lower() in content.lower()]
            
            print(f"✅ Technical knowledge test successful ({end_time - start_time:.2f}s)")
            print(f"Found technical indicators: {found_indicators}")
            print("Response preview:")
            print(content[:500] + "..." if len(content) > 500 else content)
            
            return len(found_indicators) >= 5  # At least 5 technical indicators
        else:
            print(f"❌ Technical knowledge test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in technical knowledge test: {e}")
        return False


def test_security_awareness():
    """Test AI's security awareness."""
    print("\n🔒 Testing security awareness...")
    
    try:
        import requests
        
        security_prompt = """You are a cybersecurity expert and infrastructure security architect.

SECURITY REQUIREMENTS:
- Implement zero-trust architecture principles
- Use multi-factor authentication and strong encryption
- Apply principle of least privilege throughout
- Enable comprehensive audit logging and monitoring

USER REQUEST: How do I secure a Proxmox VE cluster for production use?

Provide security best practices with specific implementation steps."""
        
        payload = {
            "model": "llama3.1:8b-instruct-q4_0",
            "prompt": security_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 2048,
                "num_thread": 3,
                "num_predict": 400
            }
        }
        
        print("Testing security knowledge...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=90
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("response", "")
            
            # Check for security indicators
            security_indicators = [
                "authentication", "encryption", "firewall", "security", 
                "backup", "monitoring", "access", "certificate", "ssl", "tls"
            ]
            
            found_security = [ind for ind in security_indicators if ind.lower() in content.lower()]
            
            print(f"✅ Security awareness test successful ({end_time - start_time:.2f}s)")
            print(f"Found security indicators: {found_security}")
            
            return len(found_security) >= 4  # At least 4 security indicators
        else:
            print(f"❌ Security awareness test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in security awareness test: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Enhanced Proxmox AI Assistant - System Test")
    print("=" * 50)
    
    tests = [
        ("Ollama Availability", test_ollama_availability),
        ("Basic API Call", test_basic_api_call),
        ("Technical Knowledge", test_technical_knowledge),
        ("Security Awareness", test_security_awareness)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Enhanced AI assistant is ready for world-class infrastructure automation!")
    elif passed >= total * 0.75:
        print("\n⚡ Most tests passed! Enhanced AI assistant is functional with minor issues.")
    else:
        print("\n⚠️  Several tests failed. Please check the system configuration.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)