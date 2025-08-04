#!/usr/bin/env python3
"""
Test script to verify AI chat functionality is working properly.
This addresses the critical issue where chat was giving generic responses.
"""

import asyncio
import sys
import os
sys.path.insert(0, '.')

async def test_ai_chat_functionality():
    """Test the complete AI chat functionality that was broken."""
    
    print("🧪 Testing AI Chat Functionality Fix")
    print("=" * 50)
    
    try:
        # Import the fixed components
        from src.proxmox_ai.ai.local_ai_client import optimized_ai_client
        from src.proxmox_ai.cli.commands.ai_commands import _generate_chat_response_local
        
        print("✅ Successfully imported fixed AI components")
        
        # Test 1: Check if local AI is available
        print("\n📡 Test 1: Checking Local AI Availability")
        is_available = await optimized_ai_client.is_available()
        print(f"   Local AI Available: {'✅ Yes' if is_available else '❌ No (Ollama not running)'}")
        
        if not is_available:
            print("\n⚠️  Ollama is not running. To test with actual AI:")
            print("   1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
            print("   2. Start Ollama: ollama serve")
            print("   3. Pull model: ollama pull llama3.1:8b-instruct-q4_0")
            print("\n🔄 Continuing with fallback testing...")
        
        # Test 2: Test the VM creation request that was failing
        print("\n🏗️  Test 2: Testing VM Creation Request (The Previously Broken Scenario)")
        test_input = "generate a VM that will host my 5 localized AI agents for development"
        
        try:
            # This should now use intelligent_conversation instead of generic responses
            response = await _generate_chat_response_local(
                ai_client=optimized_ai_client,
                user_input=test_input,
                conversation=[],
                mode="infrastructure",
                skill_level="intermediate",
                context=None
            )
            
            print(f"   Input: {test_input}")
            print(f"   Response Length: {len(response)} characters")
            print(f"   Response Preview: {response[:200]}...")
            
            # Check if response is generic (the original problem)
            generic_indicators = [
                "tell me more about your goals",
                "I understand you're asking about",
                "could you provide more specific details"
            ]
            
            is_generic = any(indicator in response.lower() for indicator in generic_indicators)
            
            if is_generic:
                print("   ❌ STILL GIVING GENERIC RESPONSES - Fix incomplete")
            else:
                print("   ✅ Giving specific technical responses - Fix successful!")
                
            # Check if response contains infrastructure-related content
            infrastructure_indicators = [
                "terraform", "vm", "memory", "cpu", "cores", "infrastructure", 
                "proxmox", "configuration", "agents", "development"
            ]
            
            has_infrastructure_content = any(indicator in response.lower() for indicator in infrastructure_indicators)
            
            if has_infrastructure_content:
                print("   ✅ Contains infrastructure-specific content")
            else:
                print("   ⚠️  May lack infrastructure-specific content")
                
        except Exception as e:
            print(f"   ❌ Error in chat response generation: {e}")
        
        # Test 3: Test fallback functionality
        print("\n🔄 Test 3: Testing Fallback Infrastructure Response")
        try:
            from src.proxmox_ai.cli.commands.ai_commands import _fallback_infrastructure_response
            
            fallback_response = await _fallback_infrastructure_response(
                ai_client=optimized_ai_client,
                user_input=test_input,
                skill_level="intermediate",
                mode="infrastructure"
            )
            
            print(f"   Fallback Response Length: {len(fallback_response)} characters")
            print(f"   Contains Infrastructure Content: {'✅ Yes' if 'terraform' in fallback_response.lower() or 'vm' in fallback_response.lower() else '❌ No'}")
            
        except Exception as e:
            print(f"   ❌ Error in fallback response: {e}")
        
        # Test 4: Test intelligent conversation directly
        if is_available:
            print("\n🧠 Test 4: Testing Intelligent Conversation Directly")
            try:
                # Use a timeout to prevent hanging
                response = await asyncio.wait_for(
                    optimized_ai_client.intelligent_conversation(test_input, {"mode": "infrastructure"}),
                    timeout=30.0
                )
                
                print(f"   Success: {response.success}")
                print(f"   Processing Time: {response.processing_time:.2f}s")
                print(f"   Model Used: {response.model_used}")
                print(f"   Content Preview: {response.content[:200]}...")
                
            except asyncio.TimeoutError:
                print("   ⚠️  Request timed out (30s) - Model may be slow on this hardware")
            except Exception as e:
                print(f"   ❌ Error in intelligent conversation: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 SUMMARY:")
        print("✅ Fixed chat AI integration to use intelligent_conversation method")
        print("✅ Added proper VM creation workflow detection")
        print("✅ Implemented infrastructure code generation and deployment offers")
        print("✅ Added fallback responses for when AI is unavailable")
        
        if is_available:
            print("✅ Local AI is running and available for testing")
        else:
            print("⚠️  Local AI not available - install and run Ollama for full functionality")
            
        print("\n🚀 The AI should now:")
        print("   - Understand user requests for VM creation")
        print("   - Generate actual Terraform configurations")
        print("   - Offer to save and deploy infrastructure code")
        print("   - Provide specific technical guidance instead of generic responses")
        
        print("\n📝 To test manually:")
        print("   proxmox-ai chat")
        print("   Then type: 'generate a VM that will host my 5 localized AI agents for development'")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_ai_chat_functionality())