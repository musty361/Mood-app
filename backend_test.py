#!/usr/bin/env python3
"""
Backend API Testing for Moodify Mood Tracker
Tests all backend endpoints with realistic data
"""

import requests
import json
from datetime import datetime, timezone, timedelta
import uuid
import sys
import os

# Get backend URL from frontend .env file
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
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Testing backend API at: {API_URL}")

# Test data with realistic mood entries
MOOD_EMOJIS = {
    1: "😢",  # Very sad
    2: "😔",  # Sad  
    3: "😐",  # Neutral
    4: "😊",  # Happy
    5: "😄"   # Very happy
}

def create_test_mood_entries():
    """Create realistic test mood entries"""
    today = datetime.now(timezone.utc)
    test_entries = []
    
    # Create entries for the last 7 days
    for i in range(7):
        date_obj = today - timedelta(days=i)
        mood_level = (i % 5) + 1  # Cycle through mood levels 1-5
        
        entry = {
            "mood": mood_level,
            "mood_emoji": MOOD_EMOJIS[mood_level],
            "notes": f"Feeling {'great' if mood_level >= 4 else 'okay' if mood_level == 3 else 'down'} today. Had a {'wonderful' if mood_level >= 4 else 'regular' if mood_level == 3 else 'challenging'} day.",
            "date": date_obj.strftime("%Y-%m-%d")
        }
        test_entries.append(entry)
    
    return test_entries

def test_api_root():
    """Test the API root endpoint"""
    print("\n=== Testing API Root ===")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_create_mood_entry():
    """Test POST /api/moods - Create mood entries"""
    print("\n=== Testing Mood Entry Creation ===")
    test_entries = create_test_mood_entries()
    created_entries = []
    
    for i, entry in enumerate(test_entries):
        try:
            print(f"\nCreating entry {i+1}: {entry['date']} - Mood {entry['mood']} {entry['mood_emoji']}")
            response = requests.post(f"{API_URL}/moods", json=entry)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Created entry ID: {data['id']}")
                print(f"Timestamp: {data['timestamp']}")
                created_entries.append(data)
            else:
                print(f"ERROR: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"ERROR creating entry: {e}")
            return False, []
    
    print(f"\nSuccessfully created {len(created_entries)} mood entries")
    return True, created_entries

def test_get_all_moods():
    """Test GET /api/moods - Retrieve all mood entries"""
    print("\n=== Testing Get All Mood Entries ===")
    try:
        response = requests.get(f"{API_URL}/moods")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            moods = response.json()
            print(f"Retrieved {len(moods)} mood entries")
            
            # Check if sorted by timestamp descending
            if len(moods) > 1:
                timestamps = [datetime.fromisoformat(mood['timestamp'].replace('Z', '+00:00')) for mood in moods]
                is_sorted = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
                print(f"Entries sorted by timestamp (descending): {is_sorted}")
                
                # Show first few entries
                for i, mood in enumerate(moods[:3]):
                    print(f"Entry {i+1}: {mood['date']} - Mood {mood['mood']} {mood['mood_emoji']}")
                    
            return True, moods
        else:
            print(f"ERROR: {response.text}")
            return False, []
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False, []

def test_get_mood_by_date(test_date):
    """Test GET /api/moods/{date} - Get mood by specific date"""
    print(f"\n=== Testing Get Mood by Date: {test_date} ===")
    try:
        response = requests.get(f"{API_URL}/moods/{test_date}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            mood = response.json()
            if mood:
                print(f"Found mood for {test_date}: Mood {mood['mood']} {mood['mood_emoji']}")
                print(f"Notes: {mood['notes']}")
                return True, mood
            else:
                print(f"No mood entry found for {test_date}")
                return True, None
        else:
            print(f"ERROR: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False, None

def test_update_mood_entry(mood_id):
    """Test PUT /api/moods/{mood_id} - Update existing mood entry"""
    print(f"\n=== Testing Update Mood Entry: {mood_id} ===")
    
    updated_data = {
        "mood": 5,
        "mood_emoji": "😄",
        "notes": "Updated: Feeling amazing after testing the API!",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.put(f"{API_URL}/moods/{mood_id}", json=updated_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            updated_mood = response.json()
            print(f"Updated mood: {updated_mood['mood']} {updated_mood['mood_emoji']}")
            print(f"Updated notes: {updated_mood['notes']}")
            return True, updated_mood
        else:
            print(f"ERROR: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False, None

def test_csv_export():
    """Test GET /api/moods/export/csv - Export mood data as CSV"""
    print("\n=== Testing CSV Export ===")
    try:
        response = requests.get(f"{API_URL}/moods/export/csv")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            csv_content = data.get('content', '')
            filename = data.get('filename', '')
            
            print(f"CSV filename: {filename}")
            print(f"CSV content length: {len(csv_content)} characters")
            
            # Check CSV format
            lines = csv_content.strip().split('\n')
            if len(lines) > 0:
                header = lines[0]
                print(f"CSV header: {header}")
                
                # Check if header has expected columns
                expected_columns = ['Date', 'Mood', 'Emoji', 'Notes', 'Timestamp']
                header_columns = [col.strip('"') for col in header.split(',')]
                has_all_columns = all(col in header_columns for col in expected_columns)
                print(f"Has all expected columns: {has_all_columns}")
                
                # Show first data row if available
                if len(lines) > 1:
                    print(f"First data row: {lines[1]}")
                    
            return True, data
        else:
            print(f"ERROR: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False, None

def test_error_handling():
    """Test error handling scenarios"""
    print("\n=== Testing Error Handling ===")
    
    # Test invalid mood value
    print("\nTesting invalid mood value (out of range):")
    invalid_entry = {
        "mood": 10,  # Invalid - should be 1-5
        "mood_emoji": "😄",
        "notes": "Invalid mood test",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.post(f"{API_URL}/moods", json=invalid_entry)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test updating non-existent mood
    print("\nTesting update of non-existent mood:")
    fake_id = str(uuid.uuid4())
    update_data = {
        "mood": 3,
        "mood_emoji": "😐",
        "notes": "This should fail",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.put(f"{API_URL}/moods/{fake_id}", json=update_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Run all backend API tests"""
    print("=" * 60)
    print("MOODIFY BACKEND API TESTING")
    print("=" * 60)
    
    # Test results tracking
    results = {
        "api_root": False,
        "create_moods": False,
        "get_all_moods": False,
        "get_mood_by_date": False,
        "update_mood": False,
        "csv_export": False
    }
    
    # Test API root
    results["api_root"] = test_api_root()
    
    # Test mood creation
    create_success, created_entries = test_create_mood_entry()
    results["create_moods"] = create_success
    
    if create_success and created_entries:
        # Test getting all moods
        get_all_success, all_moods = test_get_all_moods()
        results["get_all_moods"] = get_all_success
        
        # Test getting mood by date
        test_date = created_entries[0]['date']
        get_by_date_success, mood_by_date = test_get_mood_by_date(test_date)
        results["get_mood_by_date"] = get_by_date_success
        
        # Test updating a mood entry
        mood_id = created_entries[0]['id']
        update_success, updated_mood = test_update_mood_entry(mood_id)
        results["update_mood"] = update_success
        
        # Test CSV export
        csv_success, csv_data = test_csv_export()
        results["csv_export"] = csv_success
    
    # Test error handling
    test_error_handling()
    
    # Print final results
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All backend API tests PASSED!")
        return True
    else:
        print("⚠️  Some backend API tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)