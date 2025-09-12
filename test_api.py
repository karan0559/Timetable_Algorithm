#!/usr/bin/env python3
"""
🧪 API Test Script
Test all API endpoints to ensure they work correctly
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:5000"

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing Timetable Generator API")
    print("=" * 40)
    
    # Test 1: API Info
    print("\n1️⃣ Testing API Info endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Info: {data['service']} v{data['version']}")
        else:
            print(f"❌ API Info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API Info error: {e}")
    
    # Test 2: Health Check
    print("\n2️⃣ Testing Health Check endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            print(f"   Solvers: {data['solvers']}")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check error: {e}")
    
    # Test 3: Sample Format
    print("\n3️⃣ Testing Sample Format endpoint...")
    try:
        response = requests.get(f"{API_BASE}/sample")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sample Format: {len(data['sample_input']['courses'])} sample courses")
        else:
            print(f"❌ Sample Format failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Sample Format error: {e}")
    
    # Test 4: Course Validation
    print("\n4️⃣ Testing Course Validation endpoint...")
    sample_courses = [
        {
            "course_name": "Mathematics",
            "faculty": "Dr. Arjun Mehta",
            "room": "Room 101",
            "duration": 1,
            "weekly_count": 3,
            "session_type": "lecture",
            "availability": "Mon1,Mon2,Tue1,Wed1,Thu1"
        },
        {
            "course_name": "Physics Lab",
            "faculty": "Prof. Kavita Sharma",
            "room": "Lab 101",
            "duration": 2,
            "weekly_count": 1,
            "session_type": "lab",
            "availability": "Mon3,Tue3,Wed3,Thu3,Fri3"
        }
    ]
    
    try:
        response = requests.post(
            f"{API_BASE}/validate",
            json={"courses": sample_courses},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Validation: {data['success']} for {data['total_courses']} courses")
            if data.get('warnings'):
                print(f"   Warnings: {len(data['warnings'])}")
        else:
            print(f"❌ Validation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Validation error: {e}")
    
    # Test 5: Timetable Generation
    print("\n5️⃣ Testing Timetable Generation endpoint...")
    try:
        response = requests.post(
            f"{API_BASE}/generate",
            json={
                "courses": sample_courses,
                "solver_preference": "simple",
                "options": {
                    "allow_conflicts": False,
                    "optimize_quality": True
                }
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generation: {data['success']}")
            print(f"   Statistics: {data['statistics']['quality_rating']}")
            print(f"   Sessions: {data['statistics']['total_sessions']}")
            print(f"   Coverage: {data['statistics']['coverage_percentage']}%")
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Generation error: {e}")
    
    # Test 6: Documentation
    print("\n6️⃣ Testing Documentation endpoint...")
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Documentation: {len(data['endpoints'])} endpoints documented")
        else:
            print(f"❌ Documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Documentation error: {e}")
    
    print(f"\n🎉 API testing completed!")

if __name__ == "__main__":
    print("⏳ Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    test_api_endpoints()
