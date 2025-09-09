from timetable.input_parser import convert_csv_to_training_data
from manual_input import get_manual_input
import os
import shutil

# Try to import OR-Tools with better error handling
ORTOOLS_AVAILABLE = False
try:
    from ortools.sat.python import cp_model
    # Test runtime initialization
    test_model = cp_model.CpModel()
    test_solver = cp_model.CpSolver()
    del test_model, test_solver
    
    from timetable.ortools_solver import ORToolsTimetableSolver
    ORTOOLS_AVAILABLE = True
    print("✅ OR-Tools available")
except ImportError as e:
    print(f"⚠️  OR-Tools import failed: {e}")
except Exception as e:
    print(f"⚠️  OR-Tools runtime error: {e}")

# Always import simple solver as fallback
from timetable.simple_solver import SimpleTimetableSolver

def show_full_timetable(timetable):
    """Display complete Monday-Friday timetable."""
    print("\n" + "="*80)
    print("📅 COMPLETE WEEKLY TIMETABLE")
    print("="*80)
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00', 
             '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00']
    
    for day in days:
        print(f"\n🗓️  {day.upper()}")
        print("-" * 60)
        
        day_schedule = timetable.get(day, {})
        has_classes = False
        
        for time in times:
            classes = day_schedule.get(time, [])
            if classes:
                has_classes = True
                print(f"⏰ {time}")
                for i, class_info in enumerate(classes, 1):
                    course = class_info['course']
                    faculty = class_info['faculty']
                    room = class_info['room']
                    print(f"   {i}. {course}")
                    print(f"      👨‍🏫 Faculty: {faculty}")
                    print(f"      🏫 Room: {room}")
                print()
        
        if not has_classes:
            print("   📭 No classes scheduled")

def clean_old_data():
    """Clean old training data."""
    files_to_clean = [
        './data/training_dataset.json',
        './data/raw_dataset.json',
        './data/ortools_timetable.json',
        './data/simple_timetable.json'
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    """Main entry point."""
    
    if ORTOOLS_AVAILABLE:
        print("🎓 OR-TOOLS TIMETABLE OPTIMIZER")
    else:
        print("🎓 TIMETABLE GENERATOR (Conflict-Free Solver)")
    print("=" * 50)
    
    print("\n📝 Choose input method:")
    print("1. Use existing CSV file (courses.csv)")
    print("2. Enter course data manually")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "2":
        print("\n🔄 Starting manual input...")
        clean_old_data()
        success = get_manual_input()
        
        if success:
            shutil.copy('manual_courses.csv', 'courses.csv')
            print("✅ Using manually entered data")
        else:
            print("❌ Manual input cancelled")
            return
    else:
        if not os.path.exists('courses.csv'):
            print("❌ courses.csv not found!")
            return
        print("✅ Using existing courses.csv")
    
    # Convert data
    print("\n📊 Converting data...")
    success = convert_csv_to_training_data()
    
    if not success:
        return
    
    # Use appropriate solver
    if os.path.exists('./data/training_dataset.json'):
        if ORTOOLS_AVAILABLE:
            print("\n🤖 Using OR-Tools optimization...")
            solver = ORToolsTimetableSolver()
        else:
            print("\n🤖 Using conflict-free solver...")
            solver = SimpleTimetableSolver()
        
        timetable = solver.solve_timetable()
        
        if timetable:
            solver.export_solution(timetable)
            if ORTOOLS_AVAILABLE:
                solver.print_solver_statistics()
            else:
                solver.print_validation_report(timetable)
            
            print("\n✅ Timetable generated successfully!")
            show_full_timetable(timetable)
        else:
            print("❌ Failed to generate timetable")

if __name__ == "__main__":
    main()