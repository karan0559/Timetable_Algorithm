#!/usr/bin/env python3
"""
Test the new super simple input format
"""

from timetable.simple_solver import SimpleTimetableSolver
import json

def test_super_simple_format():
    """Test the new super simple format."""
    
    print("🧪 Testing SUPER SIMPLE Format")
    print("=" * 40)
    
    # Test different simple formats
    test_cases = [
        ("monday,tuesday,friday", "Just day names"),
        ("monday 10am,wednesday 2pm,friday", "Mixed format"),
        ("tuesday 9am,thursday 3pm", "Specific times"),
        ("monday,wednesday,friday", "Default times"),
    ]
    
    solver = SimpleTimetableSolver()
    
    for availability, description in test_cases:
        print(f"\n📝 Testing: {description}")
        print(f"   Input: {availability}")
        
        result = solver.parse_availability_slots(availability)
        print(f"   Result: {result}")
        
        if result:
            print(f"   ✅ Parsed {len(result)} time slots")
            for day, time in result:
                print(f"      📅 {day} at {time}")
        else:
            print("   ❌ No slots parsed")
    
    print("\n" + "=" * 40)
    print("🚀 Testing Complete Timetable Generation")
    
    # Test complete timetable with simple format
    test_courses = {
        "courses_info": {
            "Data Structures": {
                "faculty": "Dr. Smith",
                "room": "Hall 102", 
                "duration": 3,
                "available_slots": "monday 10am,wednesday 10am,friday 11am"
            },
            "Database Systems": {
                "faculty": "Dr. Johnson",
                "room": "Computer Lab 201",
                "duration": 2, 
                "available_slots": "tuesday,thursday"
            },
            "Machine Learning": {
                "faculty": "Dr. Wilson",
                "room": "AI Lab 301",
                "duration": 3,
                "available_slots": "monday,wednesday,friday"
            }
        }
    }
    
    solver.training_data = test_courses
    timetable = solver.solve_timetable()
    
    if timetable:
        print("✅ SUCCESS! Timetable generated with simple format!")
        print("\n📅 Generated Schedule:")
        print("-" * 30)
        
        total_scheduled = 0
        for day, schedule in timetable.items():
            has_classes = any(courses for courses in schedule.values())
            if has_classes:
                print(f"\n📆 {day}:")
                for time_slot, courses in schedule.items():
                    if courses:
                        for course in courses:
                            print(f"   {time_slot}: {course}")
                            total_scheduled += 1
        
        print(f"\n📊 Total scheduled: {total_scheduled} classes")
        
        # Check conflicts
        conflicts = solver.validate_timetable(timetable)
        if conflicts:
            print(f"⚠️  Found {len(conflicts)} conflicts:")
            for conflict in conflicts:
                print(f"   ⚠️  {conflict}")
        else:
            print("✅ No conflicts - perfect schedule!")
            
    else:
        print("❌ Failed to generate timetable")

if __name__ == "__main__":
    test_super_simple_format()
