#!/usr/bin/env python3
"""Test DecisionDetector directly to isolate the issue"""

import sys
sys.path.append('.')

from services.detector import DecisionDetector

print("Testing DecisionDetector directly...")

try:
    detector = DecisionDetector()
    print("✅ DecisionDetector initialized")

    # Test 1: Non-decision (should work)
    print("\n1. Testing non-decision...")
    message1 = "Hey team, how is everyone doing today?"
    result1 = detector.detect(message1)
    print(f"Result: {result1}")

    # Test 2: Decision (this might fail)
    print("\n2. Testing decision...")
    message2 = "We decided to migrate to PostgreSQL because the schema is stable"
    print(f"Message: {message2}")
    print("Calling detector.detect()...")
    result2 = detector.detect(message2)
    print(f"Result: {result2}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone.")
