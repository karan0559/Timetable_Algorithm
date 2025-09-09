from ortools.sat.python import cp_model
import json
from typing import Dict, List, Tuple
from collections import defaultdict

class ORToolsTimetableSolver:
    def __init__(self):
        self.training_data = None
        self.model = None
        self.solver = None
        
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
        
        # Variables for optimization
        self.course_vars = {}
        self.courses = []
        self.faculty_list = []
        self.room_list = []
        
    def initialize_solver(self):
        """Initialize OR-Tools model and solver safely."""
        try:
            self.model = cp_model.CpModel()
            self.solver = cp_model.CpSolver()
            return True
        except Exception as e:
            print(f"❌ OR-Tools initialization failed: {e}")
            return False
        
    def load_training_data(self, file_path: str = './data/training_dataset.json'):
        """Load training data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                self.training_data = json.load(f)
            print(f"🤖 OR-Tools Solver: Loaded {self.training_data['metadata']['total_courses']} courses")
            return True
        except FileNotFoundError:
            print(f"❌ Training data file not found: {file_path}")
            return False
        except Exception as e:
            print(f"❌ Error loading training data: {str(e)}")
            return False
    
    def parse_availability_slots(self, availability_str):
        """Parse availability string into (day_idx, time_idx) tuples."""
        if not availability_str:
            return []
            
        slots = []
        for slot in str(availability_str).split(','):
            slot = slot.strip()
            if not slot:
                continue
                
            # Extract day and time number
            day_part = ''.join([c for c in slot if c.isalpha()])
            time_part = ''.join([c for c in slot if c.isdigit()])
            
            # Map to indices
            full_day = self.day_mapping.get(day_part.capitalize(), None)
            full_time = self.slot_mapping.get(time_part, None)
            
            if full_day and full_time:
                day_idx = self.days.index(full_day)
                time_idx = self.time_slots.index(full_time)
                slots.append((day_idx, time_idx))
                
        return slots
    
    def create_variables(self):
        """Create decision variables for the optimization."""
        courses_info = self.training_data['courses_info']
        
        # Prepare course data
        for course_name, info in courses_info.items():
            available_slots = self.parse_availability_slots(info.get('available_slots', []))
            
            course_data = {
                'name': course_name,
                'faculty': info['faculty'],
                'room': info['room'],
                'duration': info.get('duration', 1),
                'available_slots': available_slots
            }
            self.courses.append(course_data)
            
            if info['faculty'] not in self.faculty_list:
                self.faculty_list.append(info['faculty'])
            if info['room'] not in self.room_list:
                self.room_list.append(info['room'])
        
        # Create binary variables: course_vars[c][d][t] = 1 if course c is scheduled on day d at time t
        for c, course in enumerate(self.courses):
            self.course_vars[c] = {}
            for d in range(len(self.days)):
                self.course_vars[c][d] = {}
                for t in range(len(self.time_slots)):
                    self.course_vars[c][d][t] = self.model.NewBoolVar(f'course_{c}_day_{d}_time_{t}')
    
    def add_constraints(self):
        """Add constraints to the optimization model."""
        
        # 1. Each course must be scheduled exactly once (based on duration)
        for c, course in enumerate(self.courses):
            scheduled_slots = []
            for d in range(len(self.days)):
                for t in range(len(self.time_slots)):
                    scheduled_slots.append(self.course_vars[c][d][t])
            
            # Schedule exactly 'duration' number of slots for this course
            self.model.Add(sum(scheduled_slots) == course['duration'])
        
        # 2. Courses can only be scheduled in their available time slots
        for c, course in enumerate(self.courses):
            available_slots = course['available_slots']
            
            for d in range(len(self.days)):
                for t in range(len(self.time_slots)):
                    if (d, t) not in available_slots:
                        # Force this slot to be 0 if not available
                        self.model.Add(self.course_vars[c][d][t] == 0)
        
        # 3. Faculty constraint: No faculty can teach more than one course at the same time
        for faculty in self.faculty_list:
            # Get all courses taught by this faculty
            faculty_courses = [c for c, course in enumerate(self.courses) if course['faculty'] == faculty]
            
            for d in range(len(self.days)):
                for t in range(len(self.time_slots)):
                    # At most one course per faculty per time slot
                    faculty_slots = [self.course_vars[c][d][t] for c in faculty_courses]
                    self.model.Add(sum(faculty_slots) <= 1)
        
        # 4. Room constraint: No room can host more than one course at the same time
        for room in self.room_list:
            # Get all courses using this room
            room_courses = [c for c, course in enumerate(self.courses) if course['room'] == room]
            
            for d in range(len(self.days)):
                for t in range(len(self.time_slots)):
                    # At most one course per room per time slot
                    room_slots = [self.course_vars[c][d][t] for c in room_courses]
                    self.model.Add(sum(room_slots) <= 1)
    
    def add_objectives(self):
        """Add optimization objectives."""
        # Objective 1: Maximize the number of scheduled courses
        total_scheduled = []
        for c in range(len(self.courses)):
            course_scheduled = []
            for d in range(len(self.days)):
                for t in range(len(self.time_slots)):
                    course_scheduled.append(self.course_vars[c][d][t])
            total_scheduled.extend(course_scheduled)
        
        self.model.Maximize(sum(total_scheduled))
    
    def solve_timetable(self) -> Dict:
        """Solve the timetable optimization problem."""
        if not self.training_data:
            if not self.load_training_data():
                return None
        
        # Initialize solver safely
        if not self.initialize_solver():
            print("❌ Failed to initialize OR-Tools solver")
            return None
        
        print("🤖 OR-Tools Constraint Solver initialized")
        print(f"🚀 Optimizing timetable for {len(self.training_data['courses_info'])} courses...")
        print("=" * 60)
        
        # Create the optimization model
        self.create_variables()
        self.add_constraints()
        self.add_objectives()
        
        # Solve the model
        print("🔄 Running OR-Tools optimization...")
        status = self.solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("✅ OR-Tools found optimal solution!")
            return self.extract_solution()
        else:
            print("❌ OR-Tools could not find a feasible solution")
            return None
    
    def extract_solution(self) -> Dict:
        """Extract the solution from the solved model."""
        timetable = {}
        scheduled_count = 0
        
        # Initialize timetable
        for day in self.days:
            timetable[day] = {}
            for time_slot in self.time_slots:
                timetable[day][time_slot] = []
        
        # Extract scheduled courses
        for c, course in enumerate(self.courses):
            course_scheduled = False
            for d in range(len(self.days)):
                for t in range(len(self.time_slots)):
                    if self.solver.Value(self.course_vars[c][d][t]) == 1:
                        day = self.days[d]
                        time_slot = self.time_slots[t]
                        
                        timetable[day][time_slot].append({
                            'course': course['name'],
                            'faculty': course['faculty'],
                            'room': course['room']
                        })
                        
                        course_scheduled = True
                        print(f"✅ Scheduled: {course['name']} -> {day} {time_slot}")
            
            if course_scheduled:
                scheduled_count += 1
        
        print(f"\n📊 OR-Tools Results: {scheduled_count}/{len(self.courses)} courses scheduled")
        return timetable
    
    def export_solution(self, timetable: Dict, filename: str = './data/ortools_timetable.json'):
        """Export timetable solution to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(timetable, f, indent=2)
            
            print(f"✅ OR-Tools solution exported to: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting solution: {str(e)}")
            return False
    
    def print_solver_statistics(self):
        """Print solver statistics."""
        print(f"\n📊 OR-Tools Solver Statistics:")
        print(f"   ⏱️  Solve time: {self.solver.WallTime():.2f} seconds")
        print(f"   🔢 Variables: {self.model.Proto().variables}")
        print(f"   📋 Constraints: {len(self.model.Proto().constraints)}")

if __name__ == "__main__":
    solver = ORToolsTimetableSolver()
    timetable = solver.solve_timetable()
    
    if timetable:
        solver.export_solution(timetable)
        solver.print_solver_statistics()
    else:
        print("❌ Failed to generate optimized timetable")