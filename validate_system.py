#!/usr/bin/env python3
"""
Quick system validation script for Proxmox AI Assistant.
Use this script to verify the system is working after changes.
"""

import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, description, timeout=30):
    """Run a command and return success status."""
    print(f"Testing: {description}...")
    try:
        result = subprocess.run(
            cmd, 
            cwd=str(Path(__file__).parent),
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} (timeout)")
        return False
    except Exception as e:
        print(f"❌ {description} (exception: {e})")
        return False

def main():
    """Run quick validation tests."""
    print("=" * 60)
    print("PROXMOX AI ASSISTANT - QUICK VALIDATION")
    print("=" * 60)
    
    # Check if virtual environment is available
    venv_activate = "source venv/bin/activate &&"
    
    tests = [
        # Basic CLI functionality
        (f"{venv_activate} python -m src.proxmox_ai.cli.main_basic --help", "CLI Help"),
        (f"{venv_activate} python -m src.proxmox_ai.cli.main_basic --version", "Version Display"),
        (f"{venv_activate} python -m src.proxmox_ai.cli.main_basic status", "System Status"),
        (f"{venv_activate} python -m src.proxmox_ai.cli.main_basic ai --help", "AI Commands Help"),
        (f"{venv_activate} python -m src.proxmox_ai.cli.main_basic ai status", "AI Status"),
        (f"{venv_activate} python -m src.proxmox_ai.cli.main_basic config --help", "Config Commands"),
        (f"{venv_activate} python -m src.proxmox_ai.cli.main_basic vm --help", "VM Commands"),
        
        # Test scripts
        (f"{venv_activate} python test_basic_cli.py", "Basic CLI Test"),
        (f"{venv_activate} python test_error_handling.py", "Error Handling Test"),
        (f"{venv_activate} python test_basic_security.py", "Security Validation"),
    ]
    
    passed = 0
    total = len(tests)
    
    print()
    for cmd, description in tests:
        if run_command(["bash", "-c", cmd], description):
            passed += 1
        print()
    
    print("=" * 60)
    print(f"VALIDATION RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR USE")
        return 0
    else:
        print(f"⚠️  {total - passed} TEST(S) FAILED - REVIEW ISSUES ABOVE")
        return 1

if __name__ == "__main__":
    sys.exit(main())