#!/bin/bash

# Test script for Guardrails Validators
# Tests all installed validators against the deployed API

# Configuration
API_URL="${1:-http://localhost:8000}"
echo "Testing API at: $API_URL"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test an endpoint
test_validator() {
    local name="$1"
    local payload="$2"
    local should_pass="$3"

    echo ""
    echo "Testing: $name"
    echo "---"

    response=$(curl -s -X POST "$API_URL/validate" \
        -H "Content-Type: application/json" \
        -d "$payload")

    passed=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('passed', 'error'))" 2>/dev/null)

    if [ "$passed" = "error" ]; then
        echo -e "${RED}❌ ERROR: Invalid response${NC}"
        echo "$response"
        return 1
    fi

    if [ "$should_pass" = "true" ]; then
        if [ "$passed" = "True" ] || [ "$passed" = "true" ]; then
            echo -e "${GREEN}✅ PASS: Validation passed as expected${NC}"
            return 0
        else
            echo -e "${RED}❌ FAIL: Expected to pass but failed${NC}"
            echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            return 1
        fi
    else
        if [ "$passed" = "False" ] || [ "$passed" = "false" ]; then
            echo -e "${GREEN}✅ PASS: Validation failed as expected${NC}"
            echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            return 0
        else
            echo -e "${RED}❌ FAIL: Expected to fail but passed${NC}"
            return 1
        fi
    fi
}

# Test 1: RegexMatch - Should PASS
test_validator "RegexMatch (valid phone)" '{
    "text": "Call me at 123-456-7890",
    "guardrails": [
        {
            "name": "RegexMatch",
            "config": {
                "regex": "\\d{3}-\\d{3}-\\d{4}"
            }
        }
    ]
}' "true"

# Test 2: RegexMatch - Should FAIL
test_validator "RegexMatch (invalid format)" '{
    "text": "Call me at 1234567890",
    "guardrails": [
        {
            "name": "RegexMatch",
            "config": {
                "regex": "\\d{3}-\\d{3}-\\d{4}"
            }
        }
    ]
}' "false"

# Test 3: CompetitorCheck - Should PASS
test_validator "CompetitorCheck (no competitors)" '{
    "text": "Our product is excellent and provides great value!",
    "guardrails": [
        {
            "name": "CompetitorCheck",
            "config": {
                "competitors": ["Apple", "Microsoft", "Google"]
            }
        }
    ]
}' "true"

# Test 4: CompetitorCheck - Should FAIL
test_validator "CompetitorCheck (mentions competitor)" '{
    "text": "Apple released a new iPhone yesterday.",
    "guardrails": [
        {
            "name": "CompetitorCheck",
            "config": {
                "competitors": ["Apple", "Microsoft", "Google"]
            }
        }
    ]
}' "false"

# Test 5: ToxicLanguage - Should PASS
test_validator "ToxicLanguage (clean text)" '{
    "text": "This is a wonderful product that I really enjoy!",
    "guardrails": [
        {
            "name": "ToxicLanguage",
            "config": {
                "threshold": 0.5,
                "validation_method": "sentence"
            }
        }
    ]
}' "true"

# Test 6: DetectPII - Should PASS (no PII)
test_validator "DetectPII (no personal info)" '{
    "text": "This is a general discussion about technology trends.",
    "guardrails": [
        {
            "name": "DetectPII",
            "config": {}
        }
    ]
}' "true"

# Test 7: Multiple Guardrails - Should PASS
test_validator "Multiple Guardrails (all pass)" '{
    "text": "Our innovative solution provides excellent value!",
    "guardrails": [
        {
            "name": "CompetitorCheck",
            "config": {
                "competitors": ["Apple", "Microsoft"]
            }
        },
        {
            "name": "ToxicLanguage",
            "config": {
                "threshold": 0.5,
                "validation_method": "sentence"
            }
        }
    ]
}' "true"

# Test 8: Multiple Guardrails - Should FAIL
test_validator "Multiple Guardrails (one fails)" '{
    "text": "Apple makes great products!",
    "guardrails": [
        {
            "name": "CompetitorCheck",
            "config": {
                "competitors": ["Apple", "Microsoft"]
            }
        },
        {
            "name": "ToxicLanguage",
            "config": {
                "threshold": 0.5,
                "validation_method": "sentence"
            }
        }
    ]
}' "false"

# Summary
echo ""
echo "================================"
echo -e "${YELLOW}Test suite completed!${NC}"
echo ""
echo "To test against your Railway deployment, run:"
echo "  ./test_validators.sh https://ai-guard-rails-production.up.railway.app"
echo ""

