#!/usr/bin/env python3
"""
Test script for new input format support
"""

import json
import requests

def test_new_format():
    """Test the new user-friendly input format."""
    
    print("🧪 Testing New Input Format Support")
    print("=" * 50)
    
    # Test data with new format
    test_courses = {
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
                "FacultyAvailability": "Tuesday,Thursday",  # Simple format
                "RoomAvailable": "Computer Lab 201",
                "Duration": 2
            },
            {
                "CourseName": "Machine Learning",
                "Faculty": "Dr. Wilson",
                "FacultyAvailability": "Mon1,Wed1,Fri1",  # Legacy format
                "RoomAvailable": "AI Lab 301", 
                "Duration": 3
            }
        ]
    }
    
    print("📝 Test Input (Multiple Formats):")
    print("1. Full format: Monday 10:00-11:00,Wednesday 10:00-11:00,Friday 11:00-12:00")
    print("2. Simple format: Tuesday,Thursday") 
    print("3. Legacy format: Mon1,Wed1,Fri1")
    print()
    
    try:
        # Test local generation (bypass API)
        from timetable.simple_solver import SimpleTimetableSolver
        
        solver = SimpleTimetableSolver()
        
        # Convert to internal format
        courses_info = {}
        for course in test_courses["courses"]:
            courses_info[course["CourseName"]] = {
                "faculty": course["Faculty"],
                "room": course["RoomAvailable"],
                "duration": course["Duration"],
                "available_slots": course["FacultyAvailability"]
            }
        
        solver.training_data = {"courses_info": courses_info}
        
        print("🔄 Generating timetable...")
        timetable = solver.solve_timetable()
        
        if timetable:
            print("✅ SUCCESS! New format parsing works!")
            print()
            print("📅 Generated Timetable:")
            print("-" * 30)
            
            scheduled_count = 0
            for day, day_schedule in timetable.items():
                print(f"\n📆 {day}:")
                for time_slot, courses in day_schedule.items():
                    if courses:
                        for course in courses:
                            print(f"   {time_slot}: {course}")
                            scheduled_count += 1
                    
            print(f"\n📊 Summary: {scheduled_count} slots scheduled")
            print(f"📊 Total courses: {len(test_courses['courses'])}")
            
            # Test conflicts
            conflicts = solver.validate_timetable(timetable)
            if conflicts:
                print(f"⚠️  Found {len(conflicts)} conflicts")
                for conflict in conflicts:
                    print(f"   ⚠️  {conflict}")
            else:
                print("✅ No conflicts detected!")
                
        else:
            print("❌ FAILED: Could not generate timetable")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_format()
