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
        duration = self.get_course_duration(faculty)
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
        print("   ✅ Mon2,Wed2,Fri3")
        print("   ✅ Tue1,Thu1") 
        print("   ✅ monday2,wednesday3,friday1")
        print("   ✅ MON2,WED3,FRI1")
        
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
        
    def get_course_duration(self, faculty):
        """Get course duration with workload validation."""
        while True:
            duration_input = input("Duration (hours per week): ").strip()
            try:
                duration = int(duration_input)
                if duration <= 0:
                    print("❌ Duration must be positive")
                    continue
                    
                # Check faculty workload limit
                current_load = self.faculty_workload.get(faculty, 0)
                projected_load = current_load + duration
                
                if projected_load > 20:  # 20 hours per week limit
                    print(f"⚠️  WARNING: This will give {faculty} {projected_load} hours/week")
                    print("   (Recommended maximum: 20 hours/week)")
                    proceed = input("Continue anyway? (y/n): ").lower()
                    if proceed != 'y':
                        continue
                        
                return duration
                
            except ValueError:
                print("❌ Please enter a valid number")
                
    def parse_and_validate_availability(self, availability_str):
        """Parse and validate availability with better error handling."""
        day_mapping = {
            'monday': 'Mon', 'mon': 'Mon',
            'tuesday': 'Tue', 'tue': 'Tue', 'tues': 'Tue',
            'wednesday': 'Wed', 'wed': 'Wed',
            'thursday': 'Thu', 'thu': 'Thu', 'thurs': 'Thu',
            'friday': 'Fri', 'fri': 'Fri'
        }
        
        slots = []
        errors = []
        
        print(f"\n🔍 Parsing: '{availability_str}'")
        
        for slot in availability_str.split(','):
            slot = slot.strip()
            if not slot:
                continue
            
            print(f"   Processing slot: '{slot}'")
            
            # Handle different input formats
            slot_lower = slot.lower()
            
            # Try Mon2, Tue3, etc. format first (most common)
            if len(slot) >= 4:
                day_part = slot[:3].lower()
                time_part = slot[3:]
                
                print(f"   Day part: '{day_part}', Time part: '{time_part}'")
                
                # Check if day part matches our short format
                if day_part in ['mon', 'tue', 'wed', 'thu', 'fri']:
                    if time_part.isdigit() and time_part in self.time_slots:
                        formatted_slot = f"{day_part.capitalize()}{time_part}"
                        if formatted_slot not in slots:
                            slots.append(formatted_slot)
                            print(f"   ✅ Added: {formatted_slot}")
                        continue
                    else:
                        errors.append(f"Invalid time: '{time_part}' (use 1-8)")
                        continue
            
            # Extract day and time parts for other formats
            day_chars = ''.join([c for c in slot_lower if c.isalpha()])
            time_chars = ''.join([c for c in slot if c.isdigit()])
            
            print(f"   Extracted - Day: '{day_chars}', Time: '{time_chars}'")
            
            # Validate day
            if day_chars not in day_mapping:
                errors.append(f"Invalid day: '{day_chars}' (use Mon, Tue, Wed, Thu, Fri)")
                continue
                
            # Validate time
            if time_chars not in self.time_slots:
                errors.append(f"Invalid time: '{time_chars}' (use 1-8)")
                continue
                
            formatted_slot = f"{day_mapping[day_chars]}{time_chars}"
            if formatted_slot not in slots:
                slots.append(formatted_slot)
                print(f"   ✅ Added: {formatted_slot}")
                
        if errors:
            print("❌ Errors found:")
            for error in errors:
                print(f"   - {error}")
            print("\n💡 Correct format examples:")
            print("   - Mon2,Wed2,Fri3")
            print("   - Tuesday2,Thursday3")
            print("   - mon1,wed2,fri4")
            print("   - 2 = 10:00-11:00 AM, 3 = 11:00-12:00 PM, etc.")
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