#!/usr/bin/env python3
"""
Additional validation and edge case testing for Moodify API
"""

import requests
import json
from datetime import datetime, timezone

# Get backend URL
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
        return None

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

def test_mood_validation():
    """Test mood value validation"""
    print("=== Testing Mood Value Validation ===")
    
    # Test cases: (mood_value, should_pass)
    test_cases = [
        (0, False),   # Below range
        (1, True),    # Valid minimum
        (3, True),    # Valid middle
        (5, True),    # Valid maximum
        (6, False),   # Above range
        (10, False),  # Way above range
        (-1, False),  # Negative
    ]
    
    validation_issues = []
    
    for mood_value, should_pass in test_cases:
        entry = {
            "mood": mood_value,
            "mood_emoji": "😐",
            "notes": f"Testing mood value {mood_value}",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
        }
        
        try:
            response = requests.post(f"{API_URL}/moods", json=entry)
            passed = response.status_code == 200
            
            print(f"Mood {mood_value}: Status {response.status_code} - {'PASS' if passed == should_pass else 'VALIDATION ISSUE'}")
            
            if passed != should_pass:
                validation_issues.append(f"Mood {mood_value}: Expected {'pass' if should_pass else 'fail'}, got {'pass' if passed else 'fail'}")
                
        except Exception as e:
            print(f"Error testing mood {mood_value}: {e}")
            validation_issues.append(f"Mood {mood_value}: Exception - {e}")
    
    return validation_issues

def test_required_fields():
    """Test required field validation"""
    print("\n=== Testing Required Fields ===")
    
    validation_issues = []
    
    # Test missing mood field
    entry_no_mood = {
        "mood_emoji": "😐",
        "notes": "Missing mood field",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.post(f"{API_URL}/moods", json=entry_no_mood)
        if response.status_code == 200:
            validation_issues.append("Missing mood field was accepted (should be rejected)")
        print(f"Missing mood field: Status {response.status_code}")
    except Exception as e:
        print(f"Error testing missing mood: {e}")
    
    # Test missing emoji field
    entry_no_emoji = {
        "mood": 3,
        "notes": "Missing emoji field",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.post(f"{API_URL}/moods", json=entry_no_emoji)
        if response.status_code == 200:
            validation_issues.append("Missing mood_emoji field was accepted (should be rejected)")
        print(f"Missing emoji field: Status {response.status_code}")
    except Exception as e:
        print(f"Error testing missing emoji: {e}")
    
    # Test missing date field
    entry_no_date = {
        "mood": 3,
        "mood_emoji": "😐",
        "notes": "Missing date field"
    }
    
    try:
        response = requests.post(f"{API_URL}/moods", json=entry_no_date)
        if response.status_code == 200:
            validation_issues.append("Missing date field was accepted (should be rejected)")
        print(f"Missing date field: Status {response.status_code}")
    except Exception as e:
        print(f"Error testing missing date: {e}")
    
    return validation_issues

def test_date_formats():
    """Test different date formats"""
    print("\n=== Testing Date Formats ===")
    
    date_issues = []
    
    # Test cases: (date_value, should_pass, description)
    date_test_cases = [
        ("2025-09-22", True, "Valid ISO date"),
        ("2025-13-01", False, "Invalid month"),
        ("2025-02-30", False, "Invalid day for February"),
        ("invalid-date", False, "Invalid format"),
        ("", False, "Empty date"),
    ]
    
    for date_value, should_pass, description in date_test_cases:
        entry = {
            "mood": 3,
            "mood_emoji": "😐",
            "notes": f"Testing {description}",
            "date": date_value
        }
        
        try:
            response = requests.post(f"{API_URL}/moods", json=entry)
            passed = response.status_code == 200
            
            print(f"{description}: Status {response.status_code} - {'PASS' if passed == should_pass else 'ISSUE'}")
            
            if passed != should_pass:
                date_issues.append(f"{description}: Expected {'pass' if should_pass else 'fail'}, got {'pass' if passed else 'fail'}")
                
        except Exception as e:
            print(f"Error testing {description}: {e}")
            date_issues.append(f"{description}: Exception - {e}")
    
    return date_issues

def main():
    """Run validation tests"""
    print("=" * 60)
    print("MOODIFY API VALIDATION TESTING")
    print("=" * 60)
    
    all_issues = []
    
    # Test mood validation
    mood_issues = test_mood_validation()
    all_issues.extend(mood_issues)
    
    # Test required fields
    field_issues = test_required_fields()
    all_issues.extend(field_issues)
    
    # Test date formats
    date_issues = test_date_formats()
    all_issues.extend(date_issues)
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION TEST RESULTS")
    print("=" * 60)
    
    if all_issues:
        print("⚠️  VALIDATION ISSUES FOUND:")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("✅ All validation tests passed!")
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()