import json
import random
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class SimpleTimetableSolver:
    def __init__(self):
        self.training_data = None
        self.scheduled_slots = defaultdict(list)  # Track what's scheduled when
        self.faculty_schedule = defaultdict(set)  # Track faculty availability
        self.room_schedule = defaultdict(set)     # Track room availability
        
        # Define time structure
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.time_slots = [
            '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
            '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00'
        ]
        
        # Map slot numbers to time slots
        self.slot_mapping = {
            '1': '09:00-10:00', '2': '10:00-11:00', '3': '11:00-12:00', '4': '12:00-13:00',
            '5': '14:00-15:00', '6': '15:00-16:00', '7': '16:00-17:00', '8': '17:00-18:00'
        }
        
        # Map days
        self.day_mapping = {
            'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 
            'Thu': 'Thursday', 'Fri': 'Friday'
        }
        
    def load_training_data(self, file_path: str = './data/training_dataset.json'):
        """Load training data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                self.training_data = json.load(f)
            print(f"✅ Loaded training data: {self.training_data['metadata']['total_courses']} courses")
            return True
        except FileNotFoundError:
            print(f"❌ Training data file not found: {file_path}")
            return False
        except Exception as e:
            print(f"❌ Error loading training data: {str(e)}")
            return False
    
    def parse_availability_slots(self, availability_data):
        """Parse availability string or list into (day, time_slot) tuples."""
        if not availability_data:
            return []
        
        # Handle both string and list formats
        if isinstance(availability_data, list):
            availability_str = ','.join(str(slot) for slot in availability_data)
        else:
            availability_str = str(availability_data)
            
        slots = []
        for slot in availability_str.split(','):
            slot = slot.strip()
            if not slot:
                continue
                
            # Extract day and time number
            day_part = ''.join([c for c in slot if c.isalpha()])
            time_part = ''.join([c for c in slot if c.isdigit()])
            
            # Map to full names
            full_day = self.day_mapping.get(day_part.capitalize(), None)
            full_time = self.slot_mapping.get(time_part, None)
            
            if full_day and full_time:
                slots.append((full_day, full_time))
                
        return slots
    
    def is_slot_available(self, day: str, time_slot: str, faculty: str, room: str) -> bool:
        """Check if a specific slot is available for faculty and room."""
        slot_key = f"{day}_{time_slot}"
        
        # Check if faculty is busy
        if slot_key in self.faculty_schedule[faculty]:
            return False
            
        # Check if room is busy
        if slot_key in self.room_schedule[room]:
            return False
            
        return True
    
    def schedule_course(self, course_info: Dict, available_slots: List[Tuple[str, str]]) -> bool:
        """Try to schedule a course in available slots."""
        course_name = course_info['course']
        faculty = course_info['faculty']
        room = course_info['room']
        duration = course_info.get('duration', 1)
        
        print(f"🔍 Scheduling {course_name}: faculty={faculty}, room={room}, duration={duration}")
        print(f"   Available slots: {available_slots}")
        
        # Find available slots for this course
        valid_slots = []
        for day, time_slot in available_slots:
            if self.is_slot_available(day, time_slot, faculty, room):
                valid_slots.append((day, time_slot))
        
        print(f"   Valid slots after conflict check: {valid_slots}")
        
        # Try to schedule based on duration
        if len(valid_slots) >= duration:
            # Take first 'duration' number of available slots
            selected_slots = valid_slots[:duration]
            
            for day, time_slot in selected_slots:
                slot_key = f"{day}_{time_slot}"
                
                # Mark faculty and room as busy
                self.faculty_schedule[faculty].add(slot_key)
                self.room_schedule[room].add(slot_key)
                
                # Add to timetable
                if day not in self.scheduled_slots:
                    self.scheduled_slots[day] = {}
                if time_slot not in self.scheduled_slots[day]:
                    self.scheduled_slots[day][time_slot] = []
                    
                self.scheduled_slots[day][time_slot].append({
                    'course': course_name,
                    'faculty': faculty,
                    'room': room,
                    'duration': duration
                })
            
            print(f"   ✅ Successfully scheduled in slots: {selected_slots}")
            return True
        else:
            print(f"   ❌ Not enough valid slots (need {duration}, have {len(valid_slots)})")
        
        return False
    
    def solve_timetable(self) -> Dict:
        """Generate conflict-free timetable."""
        if not self.training_data:
            if not self.load_training_data():
                return None
        
        print("🤖 Simple Solver initialized")
        print(f"\n🚀 Solving timetable for {self.training_data['metadata']['total_courses']} courses...")
        print("=" * 50)
        
        # Clear previous schedules
        self.scheduled_slots.clear()
        self.faculty_schedule.clear()
        self.room_schedule.clear()
        
        courses_info = self.training_data['courses_info']
        scheduled_count = 0
        failed_courses = []
        
        # Sort courses by priority (fewer available slots first)
        course_priority = []
        for course_name, info in courses_info.items():
            available_slots = self.parse_availability_slots(info.get('available_slots', []))
            course_priority.append({
                'name': course_name,
                'info': info,
                'available_slots': available_slots,
                'priority': len(available_slots)  # Fewer slots = higher priority
            })
        
        # Sort by priority (ascending - fewer slots first)
        course_priority.sort(key=lambda x: x['priority'])
        
        # Try to schedule each course
        for course_data in course_priority:
            course_name = course_data['name']
            course_info = {
                'course': course_name,
                'faculty': course_data['info']['faculty'],
                'room': course_data['info']['room'],
                'duration': course_data['info'].get('duration', 1)
            }
            
            available_slots = course_data['available_slots']
            
            if self.schedule_course(course_info, available_slots):
                print(f"✅ Scheduled: {course_name}")
                scheduled_count += 1
            else:
                print(f"❌ Failed: {course_name}")
                failed_courses.append(course_name)
        
        print(f"\n📊 Results: {scheduled_count} scheduled, {len(failed_courses)} failed")
        
        if failed_courses:
            print("❌ Failed courses:")
            for course in failed_courses:
                print(f"   - {course}")
        
        return dict(self.scheduled_slots)
    
    def export_solution(self, timetable: Dict, filename: str = './data/simple_timetable.json'):
        """Export timetable solution to JSON file."""
        try:
            # Convert to clean format
            clean_timetable = {}
            
            for day in self.days:
                clean_timetable[day] = {}
                for time_slot in self.time_slots:
                    if day in timetable and time_slot in timetable[day]:
                        clean_timetable[day][time_slot] = timetable[day][time_slot]
                    else:
                        clean_timetable[day][time_slot] = []
            
            with open(filename, 'w') as f:
                json.dump(clean_timetable, f, indent=2)
            
            print(f"✅ Solution exported to: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting solution: {str(e)}")
            return False
    
    def validate_timetable(self, timetable: Dict) -> Dict:
        """Validate timetable for conflicts."""
        conflicts = {
            'faculty_conflicts': [],
            'room_conflicts': [],
            'total_conflicts': 0
        }
        
        # Check each time slot for conflicts
        for day in timetable:
            for time_slot in timetable[day]:
                classes = timetable[day][time_slot]
                
                if len(classes) <= 1:
                    continue
                
                # Check faculty conflicts
                faculty_list = [cls['faculty'] for cls in classes]
                faculty_duplicates = set([f for f in faculty_list if faculty_list.count(f) > 1])
                
                for faculty in faculty_duplicates:
                    conflicts['faculty_conflicts'].append({
                        'day': day,
                        'time': time_slot,
                        'faculty': faculty,
                        'courses': [cls['course'] for cls in classes if cls['faculty'] == faculty]
                    })
                
                # Check room conflicts
                room_list = [cls['room'] for cls in classes]
                room_duplicates = set([r for r in room_list if room_list.count(r) > 1])
                
                for room in room_duplicates:
                    conflicts['room_conflicts'].append({
                        'day': day,
                        'time': time_slot,
                        'room': room,
                        'courses': [cls['course'] for cls in classes if cls['room'] == room]
                    })
        
        conflicts['total_conflicts'] = len(conflicts['faculty_conflicts']) + len(conflicts['room_conflicts'])
        return conflicts
    
    def print_validation_report(self, timetable: Dict):
        """Print validation report."""
        conflicts = self.validate_timetable(timetable)
        
        if conflicts['total_conflicts'] == 0:
            print("\n✅ TIMETABLE VALIDATION: NO CONFLICTS FOUND!")
        else:
            print(f"\n⚠️ TIMETABLE VALIDATION: {conflicts['total_conflicts']} CONFLICTS FOUND")
            
            if conflicts['faculty_conflicts']:
                print("\n👨‍🏫 Faculty Conflicts:")
                for conflict in conflicts['faculty_conflicts']:
                    print(f"   - {conflict['faculty']} on {conflict['day']} {conflict['time']}")
                    print(f"     Courses: {', '.join(conflict['courses'])}")
            
            if conflicts['room_conflicts']:
                print("\n🏫 Room Conflicts:")
                for conflict in conflicts['room_conflicts']:
                    print(f"   - {conflict['room']} on {conflict['day']} {conflict['time']}")
                    print(f"     Courses: {', '.join(conflict['courses'])}")

if __name__ == "__main__":
    solver = SimpleTimetableSolver()
    timetable = solver.solve_timetable()
    
    if timetable:
        solver.export_solution(timetable)
        solver.print_validation_report(timetable)
    else:
        print("❌ Failed to generate timetable")