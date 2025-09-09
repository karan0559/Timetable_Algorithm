import requests
import json

def test_api_with_new_format():
    """Test API with new input format."""
    
    print("🌐 Testing API Server with New Format")
    print("=" * 50)
    
    # Test data with new format
    test_data = {
        "courses": [
            {
                "CourseName": "Data Structures",
                "Faculty": "Dr. Smith",
                "FacultyAvailability": "Monday 10:00-11:00,Wednesday 10:00-11:00,Friday 11:00-12:00",
                "RoomAvailable": "Hall 102",
                "Duration": 3
            },
            {
                "CourseName": "Database Systems",
                "Faculty": "Dr. Johnson",
                "FacultyAvailability": "Tuesday,Thursday",
                "RoomAvailable": "Computer Lab 201",
                "Duration": 2
            }
        ]
    }
    
    try:
        # Test sample endpoint
        print("1. Testing /sample endpoint...")
        response = requests.get('http://localhost:5000/sample')
        if response.status_code == 200:
            sample_data = response.json()
            print("✅ Sample endpoint working")
            print(f"📝 Sample format: {sample_data['availability_formats']}")
        else:
            print(f"❌ Sample endpoint failed: {response.status_code}")
            
        # Test generation
        print("\n2. Testing /generate endpoint with new format...")
        response = requests.post('http://localhost:5000/generate', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Generation successful!")
                print(f"📊 Scheduled: {result['scheduled_courses']}/{result['total_courses']} courses")
                print(f"⚠️  Conflicts: {len(result['conflicts'])}")
                
                # Show timetable
                print("\n📅 Generated Timetable:")
                for day, schedule in result['timetable'].items():
                    if any(schedule.values()):
                        print(f"\n{day}:")
                        for time, courses in schedule.items():
                            if courses:
                                for course in courses:
                                    print(f"  {time}: {course}")
            else:
                print(f"❌ Generation failed: {result['error']}")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Is it running on localhost:5000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_with_new_format()
