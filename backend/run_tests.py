"""
Simple test runner for MedEasy AI 2.0.

Usage:
    python run_tests.py              # Run all unit tests
    python run_tests.py --integration # Include integration tests (requires API keys)
    python run_tests.py --coverage    # Run with coverage report
"""

import sys
import pytest

def main():
    args = ["tests/", "-v"]
    
    # Check command line arguments
    if "--integration" in sys.argv:
        # Include integration tests
        pass  # No marker filter needed
    else:
        # Skip integration tests by default
        args.extend(["-m", "not integration"])
    
    if "--coverage" in sys.argv:
        args.extend(["--cov=medical_nlp", "--cov-report=html", "--cov-report=term"])
    
    # Run pytest
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
