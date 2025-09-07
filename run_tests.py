#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test runner script with support for API test flags
"""
import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_tests(include_api=False, verbose=False, specific_test=None, include_slow=False):
    """Run tests with optional API tests"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add specific test if provided
    if specific_test:
        cmd.append(specific_test)
    else:
        cmd.append("tests/")
    
    # Build marker expression
    markers = ["not api"]
    if not include_slow:
        markers.append("not slow")
    
    marker_expr = " and ".join(markers)
    cmd.extend(["-m", marker_expr])
    
    if not include_api and not include_slow:
        print("🚀 Running tests (excluding API and slow tests)")
        print("   Use --api flag to include API tests")
        print("   Use --slow flag to include slow tests")
    elif include_api and not include_slow:
        print("🚀 Running tests (including API tests, excluding slow tests)")
        print("   ⚠️  API tests require GOOGLE_API_KEY environment variable")
    elif not include_api and include_slow:
        print("🚀 Running tests (excluding API tests, including slow tests)")
    else:
        print("🚀 Running tests (including API and slow tests)")
        print("   ⚠️  API tests require GOOGLE_API_KEY environment variable")
    
    # Add short traceback for better output
    cmd.extend(["--tb=short"])
    
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check if we're in the right directory
    if not Path("pytest.ini").exists():
        print("❌ pytest.ini not found. Are you in the project root?")
        return False
    
    # Check if src directory exists
    if not Path("src").exists():
        print("❌ src directory not found. Are you in the project root?")
        return False
    
    # Check if tests directory exists
    if not Path("tests").exists():
        print("❌ tests directory not found. Are you in the project root?")
        return False
    
    print("✅ Environment check passed")
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run test suite with optional API tests")
    parser.add_argument("--api", action="store_true", 
                       help="Include API tests (requires GOOGLE_API_KEY)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("-t", "--test", type=str,
                       help="Run specific test file or test function")
    parser.add_argument("--slow", action="store_true",
                       help="Include slow tests")
    parser.add_argument("--list-api", action="store_true",
                       help="List all API tests without running them")
    
    args = parser.parse_args()
    
    # Check environment first
    if not check_environment():
        sys.exit(1)
    
    # List API tests if requested
    if args.list_api:
        print("🔍 API Tests:")
        print("=" * 40)
        try:
            result = subprocess.run([
                "python", "-m", "pytest", "--collect-only", "-m", "api", "-q"
            ], capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')
            api_tests = [line for line in lines if '::' in line and 'test_' in line]
            
            if api_tests:
                for test in api_tests:
                    print(f"  • {test}")
            else:
                print("  No API tests found")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error listing API tests: {e}")
            sys.exit(1)
        return
    
    # Run tests
    exit_code = run_tests(
        include_api=args.api,
        verbose=args.verbose,
        specific_test=args.test,
        include_slow=args.slow
    )
    
    # Print summary
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    print("=" * 60)
    
    # Show usage examples
    if exit_code != 0:
        print("\n💡 Usage examples:")
        print("  python run_tests.py                    # Run fast tests only")
        print("  python run_tests.py --slow             # Include slow tests")
        print("  python run_tests.py --api              # Include API tests")
        print("  python run_tests.py -v                 # Verbose output")
        print("  python run_tests.py -t test_file.py    # Run specific test file")
        print("  python run_tests.py --list-api         # List API tests")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
