"""
Test Runner for TechAtlas Backend Services
Runs all service tests and generates a report
"""

import subprocess
import sys
import os
from datetime import datetime


def run_tests():
    """Run all tests and generate report"""
    
    print("=" * 80)
    print("🧪 TechAtlas Backend - Service Tests")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # List of test files
    test_files = [
        'tests/test_feasibility_analyzer.py',
        'tests/test_analytics_engine.py',
        'tests/test_risk_assessor.py',
        'tests/test_input_validator.py',
        'tests/test_text_processor.py'
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️  Test file not found: {test_file}")
            continue
        
        print(f"\n{'=' * 80}")
        print(f"Running: {test_file}")
        print('=' * 80)
        
        # Run pytest
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short'],
            capture_output=True,
            text=True
        )
        
        # Parse results
        output = result.stdout + result.stderr
        print(output)
        
        # Count passed/failed
        passed = output.count(' PASSED')
        failed = output.count(' FAILED')
        
        results[test_file] = {
            'passed': passed,
            'failed': failed,
            'return_code': result.returncode
        }
        
        total_passed += passed
        total_failed += failed
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    for test_file, result in results.items():
        status = "✅ PASS" if result['return_code'] == 0 else "❌ FAIL"
        print(f"{status} {test_file}")
        print(f"     Passed: {result['passed']}, Failed: {result['failed']}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    print("=" * 80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code
    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run_tests())
