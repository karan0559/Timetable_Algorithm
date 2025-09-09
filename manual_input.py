import pandas as pd
import os
from typing import List, Dict

class AdvancedManualInput:
    def __init__(self):
        self.courses = []
        self.faculty_workload = {}  # Track faculty hours
        self.room_usage = {}        # Track room usage
        self.time_slots = {
            '1': '09:00-10:00', '2': '10:00-11:00', '3': '11:00-12:00', '4': '12:00-13:00',
            '5': '14:00-15:00', '6': '15:00-16:00', '7': '16:00-17:00', '8': '17:00-18:00'
        }
        
    def show_menu(self):
        """Display main menu options."""
        print("\n" + "="*60)
        print("🎓 ADVANCED TIMETABLE INPUT SYSTEM")
        print("="*60)
        print("1. ➕ Add New Course")
        print("2. 📋 View All Courses")
        print("3. ✏️  Edit Course")
        print("4. 🗑️  Delete Course")
        print("5. 📊 Faculty Workload Summary")
        print("6. 🏫 Room Usage Summary")
        print("7. ⚠️  Check Conflicts")
        print("8. 💾 Save & Exit")
        print("9. ❌ Exit Without Saving")
        print("="*60)
        
    def add_course(self):
        """Add a new course with comprehensive details."""
        print(f"\n➕ ADDING COURSE #{len(self.courses) + 1}")
        print("-" * 40)
        
        # Get course name
        course_name = input("📚 Course name: ").strip()
        if not course_name:
            print("❌ Course name cannot be empty")
            return False
            
        # Get course type
        print("\n📝 Course Type:")
        print("1. Lecture")
        print("2. Laboratory")
        print("3. Seminar")
        print("4. Tutorial")
        
        course_type_map = {'1': 'Lecture', '2': 'Laboratory', '3': 'Seminar', '4': 'Tutorial'}
        course_type_choice = input("Select course type (1-4): ").strip()
        course_type = course_type_map.get(course_type_choice, 'Lecture')
        
        # Get faculty
        faculty = input("👨‍🏫 Faculty name: ").strip()
        if not faculty:
            print("❌ Faculty name cannot be empty")
            return False
            
        # Get faculty availability
        availability = self.get_faculty_availability(faculty)
        if not availability:
            return False
            
        # Get room details
        room_info = self.get_room_details(course_type)
        if not room_info:
            return False
            
        # Get duration with validation
        duration = self.get_course_duration(faculty, course_type)
        if not duration:
            return False
            
        # Create course record
        course = {
            'CourseName': course_name,
            'CourseType': course_type,
            'Faculty': faculty,
            'FacultyAvailability': availability,
            'RoomAvailable': room_info['name'],
            'RoomType': room_info['type'],
            'RoomCapacity': room_info['capacity'],
            'Duration': duration
        }
        
        # Check for conflicts
        conflicts = self.check_course_conflicts(course)
        if conflicts:
            print(f"\n⚠️  POTENTIAL CONFLICTS DETECTED:")
            for conflict in conflicts:
                print(f"   - {conflict}")
            
            proceed = input("\nProceed anyway? (y/n): ").lower()
            if proceed != 'y':
                print("❌ Course not added")
                return False
        
        # Add course
        self.courses.append(course)
        self.update_tracking(course)
        
        print(f"\n✅ Successfully added: {course_name}")
        self.show_course_summary(course)
        return True
        
    def get_faculty_availability(self, faculty):
        """Get faculty availability with validation."""
        print(f"\n📅 When is {faculty} available?")
        print("⏰ TIME SLOTS:")
        print("   1 = 9:00-10:00 AM    |  5 = 2:00-3:00 PM")
        print("   2 = 10:00-11:00 AM   |  6 = 3:00-4:00 PM") 
        print("   3 = 11:00-12:00 PM   |  7 = 4:00-5:00 PM")
        print("   4 = 12:00-1:00 PM    |  8 = 5:00-6:00 PM")
        print()
        print("📝 FORMAT EXAMPLES:")
        print("   ✨ SIMPLE: Monday,Wednesday,Friday")
        print("   ✨ FULL: Monday 10:00-11:00,Wednesday 11:00-12:00")
        print("   ✅ LEGACY: Mon2,Wed2,Fri3")
        print("   💡 TIP: Just type day names for automatic time assignment!")
        
        # Show current workload
        if faculty in self.faculty_workload:
            current_hours = self.faculty_workload[faculty]
            print(f"📊 Current workload: {current_hours} hours/week")
            
        while True:
            availability = input("\nAvailable time slots: ").strip()
            if availability:
                parsed = self.parse_and_validate_availability(availability)
                if parsed:
                    return parsed
                else:
                    print("❌ Invalid format. Please try again.")
            else:
                print("❌ Please enter at least one time slot.")
                
    def get_room_details(self, course_type):
        """Get room details with type-based suggestions."""
        print(f"\n🏫 Room details for {course_type}:")
        
        # Suggest room types based on course type
        if course_type == 'Laboratory':
            print("💡 Suggested: Lab rooms (Lab 101, Computer Lab, Physics Lab)")
        elif course_type == 'Lecture':
            print("💡 Suggested: Lecture halls (Hall 101, Auditorium)")
        elif course_type == 'Seminar':
            print("💡 Suggested: Seminar rooms (Seminar Room 301)")
        else:
            print("💡 Any suitable room")
            
        room_name = input("Room name/number: ").strip()
        if not room_name:
            print("❌ Room name cannot be empty")
            return None
            
        # Auto-detect room type
        room_name_lower = room_name.lower()
        if 'lab' in room_name_lower:
            suggested_type = 'Laboratory'
        elif 'hall' in room_name_lower or 'auditorium' in room_name_lower:
            suggested_type = 'Lecture Hall'
        elif 'seminar' in room_name_lower:
            suggested_type = 'Seminar Room'
        else:
            suggested_type = 'General'
            
        print(f"Auto-detected room type: {suggested_type}")
        confirm = input("Is this correct? (y/n): ").lower()
        
        if confirm != 'y':
            print("Room types: 1=Laboratory, 2=Lecture Hall, 3=Seminar Room, 4=General")
            type_choice = input("Select room type (1-4): ").strip()
            type_map = {'1': 'Laboratory', '2': 'Lecture Hall', '3': 'Seminar Room', '4': 'General'}
            room_type = type_map.get(type_choice, 'General')
        else:
            room_type = suggested_type
            
        # Get capacity
        while True:
            capacity_input = input("Room capacity (number of students): ").strip()
            try:
                capacity = int(capacity_input)
                if capacity > 0:
                    break
                else:
                    print("❌ Capacity must be positive")
            except ValueError:
                print("❌ Please enter a valid number")
                
        return {
            'name': room_name,
            'type': room_type,
            'capacity': capacity
        }
        
    def get_course_duration(self, faculty, course_type):
        """Get course duration with automatic assignment based on course type."""
        
        # 🎯 AUTOMATIC DURATION ASSIGNMENT BY COURSE TYPE
        type_durations = {
            'Lecture': 3,      # Lecture: 3 hours/week (typical)
            'Laboratory': 2,   # Laboratory: 2 hours/week  
            'Tutorial': 1,     # Tutorial: 1 hour/week
            'Seminar': 2       # Seminar: 2 hours/week
        }
        
        suggested_duration = type_durations.get(course_type, 3)
        
        print(f"\n⏱️  DURATION ASSIGNMENT:")
        print(f"   📚 Course Type: {course_type}")
        print(f"   ⭐ Suggested Duration: {suggested_duration} hours/week")
        print(f"   💡 Standard durations:")
        print(f"      • Laboratory: 2 hours/week")
        print(f"      • Tutorial: 1 hour/week") 
        print(f"      • Seminar: 2 hours/week")
        print(f"      • Lecture: 3 hours/week")
        
        # Ask if user wants to use suggested duration or custom
        use_suggested = input(f"\nUse suggested duration ({suggested_duration} hours)? (y/n): ").lower()
        
        if use_suggested == 'y':
            duration = suggested_duration
            print(f"✅ Using {duration} hours/week for {course_type}")
        else:
            # Manual input
            while True:
                duration_input = input("Enter custom duration (hours per week): ").strip()
                try:
                    duration = int(duration_input)
                    if duration <= 0:
                        print("❌ Duration must be positive")
                        continue
                    break
                except ValueError:
                    print("❌ Please enter a valid number")
        
        # Check faculty workload limit
        current_load = self.faculty_workload.get(faculty, 0)
        projected_load = current_load + duration
        
        if projected_load > 20:  # 20 hours per week limit
            print(f"⚠️  WARNING: This will give {faculty} {projected_load} hours/week")
            print("   (Recommended maximum: 20 hours/week)")
            proceed = input("Continue anyway? (y/n): ").lower()
            if proceed != 'y':
                return None
                
        return duration
                
    def parse_and_validate_availability(self, availability_str):
        """Parse and validate availability with intelligent time assignment.
        Combines smart distribution, randomization, and optimization.
        Supports multiple formats:
        1. Simple: Monday,Wednesday,Friday (intelligent auto-assignment)
        2. Full: Monday 10:00-11:00,Wednesday 11:00-12:00
        3. Legacy: Mon2,Wed3,Fri1
        """
        import random
        
        day_mapping = {
            'monday': 'Mon', 'mon': 'Mon',
            'tuesday': 'Tue', 'tue': 'Tue', 'tues': 'Tue',
            'wednesday': 'Wed', 'wed': 'Wed',
            'thursday': 'Thu', 'thu': 'Thu', 'thurs': 'Thu',
            'friday': 'Fri', 'fri': 'Fri'
        }
        
        time_slot_mapping = {
            '09:00-10:00': '1', '10:00-11:00': '2', '11:00-12:00': '3', '12:00-13:00': '4',
            '14:00-15:00': '5', '15:00-16:00': '6', '16:00-17:00': '7', '17:00-18:00': '8'
        }
        
        # Smart time slot preferences based on course type and faculty load
        preferred_times = {
            'morning': ['2', '3', '1'],  # 10-11, 11-12, 9-10
            'afternoon': ['5', '6', '7'], # 2-3, 3-4, 4-5
            'flexible': ['2', '3', '5', '1', '6'] # Best general times
        }
        
        slots = []
        errors = []
        
        print(f"\n🔍 Parsing: '{availability_str}'")
        
        # Count existing courses to determine smart distribution
        total_existing_courses = len(self.courses)
        
        for slot_idx, slot in enumerate(availability_str.split(',')):
            slot = slot.strip()
            if not slot:
                continue
            
            print(f"   Processing slot: '{slot}'")
            slot_lower = slot.lower()
            
            # Format 1: Intelligent day-only assignment
            if slot_lower in day_mapping:
                day_code = day_mapping[slot_lower]
                
                # 🧠 INTELLIGENT TIME ASSIGNMENT
                if total_existing_courses == 0:
                    # First course gets prime morning slot
                    smart_time = '2'  # 10:00-11:00
                    method = "first course (prime time)"
                elif total_existing_courses == 1:
                    # Second course gets different time to avoid conflicts
                    smart_time = '3'  # 11:00-12:00
                    method = "second course (distributed)"
                elif total_existing_courses == 2:
                    # Third course gets afternoon slot
                    smart_time = '5'  # 14:00-15:00
                    method = "third course (afternoon)"
                else:
                    # 🎲 SMART RANDOMIZATION for variety
                    available_times = preferred_times['flexible'].copy()
                    
                    # 🔍 OPTIMIZATION: Avoid already used times
                    used_times = set()
                    for existing_course in self.courses:
                        for existing_slot in existing_course.get('availability', '').split(','):
                            if len(existing_slot) >= 4 and existing_slot[-1].isdigit():
                                used_times.add(existing_slot[-1])
                    
                    # Remove heavily used times to spread load
                    preferred_unused = [t for t in available_times if t not in used_times]
                    if preferred_unused:
                        smart_time = random.choice(preferred_unused)
                        method = "optimized random (avoiding conflicts)"
                    else:
                        smart_time = random.choice(available_times)
                        method = "smart random"
                
                formatted_slot = f"{day_code}{smart_time}"
                if formatted_slot not in slots:
                    slots.append(formatted_slot)
                    time_display = {
                        '1': '09:00-10:00', '2': '10:00-11:00', '3': '11:00-12:00', '4': '12:00-13:00',
                        '5': '14:00-15:00', '6': '15:00-16:00', '7': '16:00-17:00', '8': '17:00-18:00'
                    }[smart_time]
                    print(f"   ✅ Added: {formatted_slot} ({time_display}) - {method}")
                continue
            
            # Format 2: Full format (Monday 10:00-11:00)
            if ':' in slot and '-' in slot:
                parts = slot.split()
                if len(parts) >= 2:
                    day_part = parts[0].lower()
                    time_part = ' '.join(parts[1:])
                    
                    if day_part in day_mapping and time_part in time_slot_mapping:
                        day_code = day_mapping[day_part]
                        time_code = time_slot_mapping[time_part]
                        formatted_slot = f"{day_code}{time_code}"
                        if formatted_slot not in slots:
                            slots.append(formatted_slot)
                            print(f"   ✅ Added: {formatted_slot} ({time_part}) - explicit time")
                        continue
            
            # Format 3: Legacy format (Mon2, Tue3, etc.)
            if len(slot) >= 4:
                day_part = slot[:3].lower()
                time_part = slot[3:]
                
                if day_part in ['mon', 'tue', 'wed', 'thu', 'fri']:
                    if time_part.isdigit() and time_part in self.time_slots:
                        formatted_slot = f"{day_part.capitalize()}{time_part}"
                        if formatted_slot not in slots:
                            slots.append(formatted_slot)
                            print(f"   ✅ Added: {formatted_slot} - legacy format")
                        continue
                    else:
                        errors.append(f"Invalid time: '{time_part}' (use 1-8)")
                        continue
            
            # Format 4: Extract day and time parts for mixed formats
            day_chars = ''.join([c for c in slot_lower if c.isalpha()])
            time_chars = ''.join([c for c in slot if c.isdigit()])
            
            if day_chars in day_mapping:
                time_code = time_chars if time_chars and time_chars in self.time_slots else '2'
                formatted_slot = f"{day_mapping[day_chars]}{time_code}"
                if formatted_slot not in slots:
                    slots.append(formatted_slot)
                    print(f"   ✅ Added: {formatted_slot} - mixed format")
            else:
                errors.append(f"Invalid day: '{day_chars}' - use full names like Monday, Tuesday, etc.")
                
        if errors:
            print("❌ Errors found:")
            for error in errors:
                print(f"   - {error}")
            print("\n💡 Correct format examples:")
            print("   ✨ Simple: Monday,Wednesday,Friday (intelligent auto-assignment)")
            print("   ✨ Full: Monday 10:00-11:00,Wednesday 11:00-12:00")
            print("   ✨ Legacy: Mon2,Wed3,Fri1")
            return None
            
        print(f"✅ Successfully parsed: {slots}")
        return ','.join(slots) if slots else None
        
    def check_course_conflicts(self, new_course):
        """Check for conflicts with existing courses."""
        conflicts = []
        new_slots = set(new_course['FacultyAvailability'].split(','))
        
        for existing in self.courses:
            existing_slots = set(existing['FacultyAvailability'].split(','))
            common_slots = new_slots.intersection(existing_slots)
            
            if common_slots:
                # Faculty conflict
                if existing['Faculty'] == new_course['Faculty']:
                    conflicts.append(f"Faculty {existing['Faculty']} conflict with {existing['CourseName']} at {common_slots}")
                    
                # Room conflict
                if existing['RoomAvailable'] == new_course['RoomAvailable']:
                    conflicts.append(f"Room {existing['RoomAvailable']} conflict with {existing['CourseName']} at {common_slots}")
                    
        return conflicts
        
    def update_tracking(self, course):
        """Update faculty workload and room usage tracking."""
        faculty = course['Faculty']
        room = course['RoomAvailable']
        duration = course['Duration']
        
        # Update faculty workload
        if faculty not in self.faculty_workload:
            self.faculty_workload[faculty] = 0
        self.faculty_workload[faculty] += duration
        
        # Update room usage
        if room not in self.room_usage:
            self.room_usage[room] = []
        self.room_usage[room].append({
            'course': course['CourseName'],
            'faculty': faculty,
            'slots': course['FacultyAvailability']
        })
        
    def show_course_summary(self, course):
        """Show detailed course summary."""
        print("\n📋 COURSE SUMMARY:")
        print(f"   📚 Course: {course['CourseName']} ({course['CourseType']})")
        print(f"   👨‍🏫 Faculty: {course['Faculty']}")
        print(f"   📅 Available: {course['FacultyAvailability']}")
        print(f"   🏫 Room: {course['RoomAvailable']} ({course['RoomType']}, Capacity: {course['RoomCapacity']})")
        print(f"   ⏱️  Duration: {course['Duration']} hours/week")
        
    def view_all_courses(self):
        """Display all entered courses."""
        if not self.courses:
            print("\n📭 No courses entered yet")
            return
            
        print(f"\n📋 ALL COURSES ({len(self.courses)} total)")
        print("="*80)
        
        for i, course in enumerate(self.courses, 1):
            print(f"\n{i}. {course['CourseName']} ({course['CourseType']})")
            print(f"   👨‍🏫 {course['Faculty']} | 🏫 {course['RoomAvailable']} | ⏱️ {course['Duration']}h")
            print(f"   📅 Available: {course['FacultyAvailability']}")
            
    def show_faculty_workload(self):
        """Show faculty workload summary."""
        if not self.faculty_workload:
            print("\n📭 No faculty data available")
            return
            
        print(f"\n👨‍🏫 FACULTY WORKLOAD SUMMARY")
        print("="*50)
        
        for faculty, hours in sorted(self.faculty_workload.items()):
            status = "⚠️ " if hours > 20 else "✅ "
            print(f"{status}{faculty}: {hours} hours/week")
            
        avg_load = sum(self.faculty_workload.values()) / len(self.faculty_workload)
        print(f"\n📊 Average load: {avg_load:.1f} hours/week")
        
    def save_courses(self):
        """Save courses to CSV."""
        if not self.courses:
            print("❌ No courses to save")
            return False
            
        # Prepare data for CSV (backward compatibility)
        csv_data = []
        for course in self.courses:
            csv_data.append({
                'CourseName': course['CourseName'],
                'Faculty': course['Faculty'],
                'FacultyAvailability': course['FacultyAvailability'],
                'RoomAvailable': course['RoomAvailable'],
                'Duration': course['Duration']
            })
            
        df = pd.DataFrame(csv_data)
        df.to_csv('manual_courses.csv', index=False)
        
        # Also save detailed data
        detailed_df = pd.DataFrame(self.courses)
        detailed_df.to_csv('detailed_courses.csv', index=False)
        
        print(f"\n✅ Saved {len(self.courses)} courses")
        print("📁 Files created:")
        print("   - manual_courses.csv (for timetable generation)")
        print("   - detailed_courses.csv (with all details)")
        
        return True
        
    def run(self):
        """Main input loop."""
        print("🎓 Welcome to Advanced Timetable Input System!")
        
        while True:
            self.show_menu()
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == '1':
                self.add_course()
            elif choice == '2':
                self.view_all_courses()
            elif choice == '3':
                print("✏️ Edit functionality - Coming soon!")
            elif choice == '4':
                print("🗑️ Delete functionality - Coming soon!")
            elif choice == '5':
                self.show_faculty_workload()
            elif choice == '6':
                print("🏫 Room usage summary - Coming soon!")
            elif choice == '7':
                print("⚠️ Conflict checker - Coming soon!")
            elif choice == '8':
                if self.save_courses():
                    print("✅ Data saved successfully!")
                    return True
                else:
                    continue
            elif choice == '9':
                confirm = input("❌ Exit without saving? (y/n): ").lower()
                if confirm == 'y':
                    return False
            else:
                print("❌ Invalid choice. Please select 1-9.")
                
            input("\nPress Enter to continue...")

def get_manual_input():
    """Entry point for manual input system."""
    system = AdvancedManualInput()
    return system.run()

if __name__ == "__main__":
    get_manual_input()