import json
import pandas as pd
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class TimetableSolver:
    def __init__(self, data_path: str = './data/training_dataset.json'):
        """Initialize the timetable solver with training data."""
        self.data = self.load_training_data(data_path)
        self.schedule = {}
        self.time_slots = self.create_time_slots()
        
    def load_training_data(self, data_path: str) -> Dict:
        """Load training data from JSON file."""
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
            print(f"✅ Training data loaded successfully")
            return data
        except FileNotFoundError:
            print(f"❌ Training data file not found: {data_path}")
            return {}
        except Exception as e:
            print(f"❌ Error loading training data: {e}")
            return {}
    
    def create_time_slots(self) -> Dict[str, List[str]]:
        """Create standardized time slots for the week."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_periods = [
            '09:00-10:00', '10:00-11:00', '11:00-12:00', 
            '12:00-13:00', '14:00-15:00', '15:00-16:00', 
            '16:00-17:00', '17:00-18:00'
        ]
        
        slots = {}
        for day in days:
            slots[day] = time_periods.copy()
        
        return slots
    
    def generate_schedule(self) -> Dict:
        """Generate a complete timetable schedule."""
        print("\n🚀 Generating Timetable Schedule...")
        print("=" * 40)
        
        if not self.data:
            print("❌ No training data available")
            return {}
        
        courses_info = self.data.get('courses_info', {})
        schedule = {}
        
        # Initialize empty schedule
        for day in self.time_slots:
            schedule[day] = {}
            for time in self.time_slots[day]:
                schedule[day][time] = []
        
        # Sort courses by constraints (labs need longer slots)
        sorted_courses = self.sort_courses_by_priority(courses_info)
        
        scheduled_count = 0
        conflict_count = 0
        
        for course_name, course_info in sorted_courses:
            result = self.schedule_course(course_name, course_info, schedule)
            if result['success']:
                scheduled_count += 1
                print(f"✅ Scheduled: {course_name}")
            else:
                conflict_count += 1
                print(f"⚠️  Conflict: {course_name} - {result['reason']}")
        
        print(f"\n📊 Scheduling Results:")
        print(f"   ✅ Successfully scheduled: {scheduled_count} courses")
        print(f"   ⚠️  Conflicts/Unscheduled: {conflict_count} courses")
        
        self.schedule = schedule
        return schedule
    
    def sort_courses_by_priority(self, courses_info: Dict) -> List[Tuple]:
        """Sort courses by scheduling priority."""
        course_list = list(courses_info.items())
        
        # Priority: Labs first (need consecutive slots), then by duration
        def priority_key(item):
            course_name, course_info = item
            is_lab = course_info.get('room_type') == 'lab'
            duration = course_info.get('duration', 1)
            available_slots = len(course_info.get('available_slots', []))
            
            # Higher priority = scheduled first
            return (is_lab, duration, -available_slots)
        
        return sorted(course_list, key=priority_key, reverse=True)
    
    def schedule_course(self, course_name: str, course_info: Dict, schedule: Dict) -> Dict:
        """Try to schedule a single course."""
        faculty = course_info.get('faculty')
        room = course_info.get('room')
        duration = course_info.get('duration', 1)
        available_slots = course_info.get('available_slots', [])
        
        # Convert available slots to day-time format
        possible_slots = self.parse_available_slots(available_slots)
        
        for day, time_period in possible_slots:
            if self.can_schedule_at(day, time_period, duration, faculty, room, schedule):
                # Schedule the course
                for i in range(duration):
                    time_idx = self.time_slots[day].index(time_period) + i
                    if time_idx < len(self.time_slots[day]):
                        slot_time = self.time_slots[day][time_idx]
                        schedule[day][slot_time].append({
                            'course': course_name,
                            'faculty': faculty,
                            'room': room,
                            'duration': duration,
                            'slot_number': i + 1
                        })
                
                return {'success': True, 'day': day, 'time': time_period}
        
        return {'success': False, 'reason': 'No available slots found'}
    
    def parse_available_slots(self, available_slots: List[str]) -> List[Tuple[str, str]]:
        """Convert availability strings to (day, time) tuples."""
        day_mapping = {
            'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday',
            'Thu': 'Thursday', 'Fri': 'Friday'
        }
        
        time_mapping = {
            '1': '09:00-10:00', '2': '10:00-11:00', '3': '11:00-12:00',
            '4': '12:00-13:00', '5': '14:00-15:00', '6': '15:00-16:00',
            '7': '16:00-17:00', '8': '17:00-18:00'
        }
        
        parsed_slots = []
        
        for slot in available_slots:
            # Extract day and time from strings like "Mon2", "Wed3"
            day_part = ''.join([c for c in slot if c.isalpha()])
            time_part = ''.join([c for c in slot if c.isdigit()])
            
            if day_part in day_mapping and time_part in time_mapping:
                day = day_mapping[day_part]
                time = time_mapping[time_part]
                parsed_slots.append((day, time))
        
        return parsed_slots
    
    def can_schedule_at(self, day: str, start_time: str, duration: int, 
                       faculty: str, room: str, schedule: Dict) -> bool:
        """Check if a course can be scheduled at given time."""
        start_idx = self.time_slots[day].index(start_time)
        
        # Check if enough consecutive slots available
        for i in range(duration):
            time_idx = start_idx + i
            if time_idx >= len(self.time_slots[day]):
                return False
            
            slot_time = self.time_slots[day][time_idx]
            existing_classes = schedule[day][slot_time]
            
            # Check faculty conflict
            for existing in existing_classes:
                if existing['faculty'] == faculty:
                    return False
                if existing['room'] == room:
                    return False
        
        return True
    
    def export_schedule(self, output_path: str = './data/generated_timetable.json'):
        """Export the generated schedule."""
        if not self.schedule:
            print("❌ No schedule generated yet")
            return False
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.schedule, f, indent=2)
            print(f"✅ Schedule exported to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error exporting schedule: {e}")
            return False

def generate_timetable():
    """Main function to generate timetable."""
    solver = TimetableSolver()
    schedule = solver.generate_schedule()
    
    if schedule:
        solver.export_schedule()
        return schedule
    else:
        print("❌ Failed to generate schedule")
        return None

if __name__ == "__main__":
    generate_timetable()