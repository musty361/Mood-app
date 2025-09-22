#!/usr/bin/env python3
"""
Test DELETE endpoint for Moodify API
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

def test_delete_endpoint():
    """Test DELETE /api/moods/{mood_id} endpoint"""
    print("=== Testing DELETE Endpoint ===")
    
    # First create a mood entry to delete
    entry = {
        "mood": 4,
        "mood_emoji": "😊",
        "notes": "This entry will be deleted",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    }
    
    try:
        # Create entry
        response = requests.post(f"{API_URL}/moods", json=entry)
        if response.status_code != 200:
            print(f"Failed to create test entry: {response.status_code}")
            return False
        
        created_entry = response.json()
        mood_id = created_entry['id']
        print(f"Created test entry with ID: {mood_id}")
        
        # Delete the entry
        delete_response = requests.delete(f"{API_URL}/moods/{mood_id}")
        print(f"Delete status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            result = delete_response.json()
            print(f"Delete response: {result}")
            
            # Verify it's actually deleted by trying to get it by date
            get_response = requests.get(f"{API_URL}/moods/{entry['date']}")
            if get_response.status_code == 200:
                mood_data = get_response.json()
                if mood_data is None:
                    print("✅ Entry successfully deleted (not found by date)")
                    return True
                else:
                    print("⚠️  Entry still exists after deletion")
                    return False
            else:
                print(f"Error checking if entry was deleted: {get_response.status_code}")
                return False
        else:
            print(f"Delete failed: {delete_response.text}")
            return False
            
    except Exception as e:
        print(f"Error testing delete: {e}")
        return False

if __name__ == "__main__":
    success = test_delete_endpoint()
    print(f"Delete test {'PASSED' if success else 'FAILED'}")