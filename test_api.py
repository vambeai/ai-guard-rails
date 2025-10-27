"""
Simple test script to verify the FastAPI Guardrails Validator service is working.

Run this script after starting the server to test basic functionality.
"""

import requests
import json
import sys


BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health_check():
    """Test the health check endpoint."""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print(f"Make sure the server is running at {BASE_URL}")
        return False


def test_validation(name, text, guardrails, expect_pass=True):
    """Test a validation request."""
    print(f"\nTest: {name}")
    print(f"Text: {text}")
    print(f"Guardrails: {', '.join([g['name'] for g in guardrails])}")

    try:
        response = requests.post(
            f"{BASE_URL}/validate",
            json={
                "text": text,
                "guardrails": guardrails
            }
        )

        if response.status_code == 200:
            result = response.json()
            passed = result.get("passed", False)

            if passed and expect_pass:
                print("✅ Test passed as expected")
            elif not passed and not expect_pass:
                print("✅ Test failed as expected")
                print(f"Failed guardrails: {[fg['name'] for fg in result['failed_guardrails']]}")
            elif passed and not expect_pass:
                print("⚠️  Test passed but was expected to fail")
            else:
                print("⚠️  Test failed but was expected to pass")
                print(f"Failed guardrails: {[fg['name'] for fg in result['failed_guardrails']]}")

            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("  FastAPI Guardrails Validator - Test Suite")
    print("=" * 60)
    print(f"\nTesting server at: {BASE_URL}")

    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Server is not responding. Please start the server first.")
        sys.exit(1)

    # Test 2: Simple regex validation (passing)
    print_section("Test 1: Regex Match (Should Pass)")
    test_validation(
        "Phone Number Format",
        "Call me at 123-456-7890",
        [
            {
                "name": "RegexMatch",
                "config": {
                    "regex": "\\d{3}-\\d{3}-\\d{4}"
                }
            }
        ],
        expect_pass=True
    )

    # Test 3: Simple regex validation (failing)
    print_section("Test 2: Regex Match (Should Fail)")
    test_validation(
        "Invalid Phone Number Format",
        "Call me at 1234567890",
        [
            {
                "name": "RegexMatch",
                "config": {
                    "regex": "\\d{3}-\\d{3}-\\d{4}"
                }
            }
        ],
        expect_pass=False
    )

    # Test 4: Competitor check (passing)
    print_section("Test 3: Competitor Check (Should Pass)")
    test_validation(
        "No Competitor Mention",
        "Our product is excellent and provides great value!",
        [
            {
                "name": "CompetitorCheck",
                "config": {
                    "competitors": ["Apple", "Microsoft", "Google"]
                }
            }
        ],
        expect_pass=True
    )

    # Test 5: Competitor check (failing)
    print_section("Test 4: Competitor Check (Should Fail)")
    test_validation(
        "Competitor Mention",
        "Apple released a new product yesterday.",
        [
            {
                "name": "CompetitorCheck",
                "config": {
                    "competitors": ["Apple", "Microsoft", "Google"]
                }
            }
        ],
        expect_pass=False
    )

    # Test 6: Multiple guardrails (all passing)
    print_section("Test 5: Multiple Guardrails (Should Pass)")
    test_validation(
        "Multiple Validators - All Pass",
        "Our innovative solution is fantastic!",
        [
            {
                "name": "CompetitorCheck",
                "config": {
                    "competitors": ["Apple", "Microsoft", "Google"]
                }
            },
            {
                "name": "ToxicLanguage",
                "config": {
                    "threshold": 0.5,
                    "validation_method": "sentence"
                }
            }
        ],
        expect_pass=True
    )

    print_section("Test Summary")
    print("\n✅ All tests completed!")
    print("\nNote: Some tests may fail if the required validators are not installed.")
    print("To install validators, run:")
    print("  guardrails hub install hub://guardrails/regex_match")
    print("  guardrails hub install hub://guardrails/competitor_check")
    print("  guardrails hub install hub://guardrails/toxic_language")


if __name__ == "__main__":
    main()

