#!/usr/bin/env python3
"""
Quick setup validation script to test the GETTING_STARTED.md instructions.
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"Testing: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run setup validation tests."""
    print("🧪 Proxmox AI Infrastructure Assistant - Setup Validation")
    print("=" * 60)
    
    # Check basic requirements
    tests = [
        ("python3 --version", "Python 3 availability"),
        ("source venv/bin/activate && python --version", "Virtual environment activation"),
        ("source venv/bin/activate && pip list | grep typer", "Required packages installed"),
        ("ls -la GETTING_STARTED.md", "Setup documentation exists"),
        ("ls -la docs/INDEX.md", "Documentation index exists"),
    ]
    
    results = []
    for cmd, desc in tests:
        results.append(run_command(cmd, desc))
    
    # Test CLI functionality (basic)
    print("\n🔧 Testing CLI functionality...")
    cli_tests = [
        ("source venv/bin/activate && timeout 10 python -m src.proxmox_ai.cli.main --help", "CLI help display"),
        ("source venv/bin/activate && timeout 10 python -m src.proxmox_ai.cli.main --version", "Version display"),
    ]
    
    for cmd, desc in cli_tests:
        results.append(run_command(cmd, desc))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Setup instructions are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Setup instructions may need updates.")
        return 1

if __name__ == "__main__":
    sys.exit(main())