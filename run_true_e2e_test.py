#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
True End-to-End Test Runner
Runs comprehensive tests with real API calls
"""
import os
import sys
import subprocess
from pathlib import Path


def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ .env file loaded")
    else:
        print("📄 No .env file found")


def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment setup...")
    
    # Load .env file if it exists
    load_env_file()
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Error: Run this script from the project root directory")
        return False
    
    # Check if mamba environment is active
    if "butterfly" not in os.environ.get("CONDA_DEFAULT_ENV", ""):
        print("⚠️  Warning: butterfly environment not active")
        print("   Run: mamba activate butterfly")
        return False
    
    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  Warning: GOOGLE_API_KEY not set")
        print("   Some tests will be skipped")
        print("   Set with: export GOOGLE_API_KEY='your_key_here'")
        print("   Or create a .env file with: GOOGLE_API_KEY=your_key_here")
    else:
        print("✅ GOOGLE_API_KEY found")
    
    print("✅ Environment check complete")
    return True


def run_tests():
    """Run the true end-to-end tests"""
    print("\n🚀 Running True End-to-End Tests")
    print("=" * 50)
    
    # Run pytest with verbose output
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_true_end_to_end.py", 
        "-v", 
        "--tb=short",
        "--no-header"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nExit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_individual_test_suite():
    """Run the individual test suite function"""
    print("\n🔬 Running Individual Test Suite")
    print("=" * 50)
    
    try:
        # Import and run the test suite
        sys.path.insert(0, ".")
        from tests.test_true_end_to_end import test_run_true_end_to_end_suite
        test_run_true_end_to_end_suite()
        return True
        
    except Exception as e:
        print(f"❌ Error running individual test suite: {e}")
        return False


def main():
    """Main function"""
    print("🧪 True End-to-End Test Runner")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed")
        return 1
    
    # Automatically run both test modes
    print("\n🚀 Running both test modes automatically...")
    
    success = True
    
    # Run pytest tests
    print("\n" + "="*50)
    print("📋 RUNNING PYTEST TESTS")
    print("="*50)
    success &= run_tests()
    
    # Run individual test suite
    print("\n" + "="*50)
    print("🔬 RUNNING INDIVIDUAL TEST SUITE")
    print("="*50)
    success &= run_individual_test_suite()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n💥 Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
