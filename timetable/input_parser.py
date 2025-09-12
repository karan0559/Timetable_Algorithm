import pandas as pd
import json
import os
from typing import Dict, List, Set, Tuple

class CSVToDataConverter:
    def __init__(self):
        self.course_data = None
        
    def load_csv_data(self, csv_file_path: str):
        """Load course data from CSV file."""
        try:
            self.course_data = pd.read_csv(csv_file_path)
            print(f"✅ Loaded {len(self.course_data)} courses from CSV")
            print(f"📊 Columns: {list(self.course_data.columns)}")
            return True
        except FileNotFoundError:
            print(f"❌ File {csv_file_path} not found")
            return False
        except Exception as e:
            print(f"❌ Error loading CSV: {str(e)}")
            return False
    
    def parse_availability(self, availability_str: str) -> str:
        """Parse faculty availability string and return as string (not list)."""
        if pd.isna(availability_str) or availability_str == "Mon-Fri" or availability_str == "":
            return ""
        
        # Handle different input formats
        if isinstance(availability_str, (int, float)):
            return ""
        
        # Keep as string instead of converting to list
        return str(availability_str).strip()
    
    def generate_training_features(self) -> Dict:
        """Generate features suitable for ML training."""
        if self.course_data is None:
            print("❌ No data loaded. Call load_csv_data() first.")
            return {}
        # --- Aggregate duplicate course rows (same CourseName) ---
        # Enhanced: Handle course components (e.g., "Database Systems,Lecture" vs "Database Systems,Lab")
        df = self.course_data.copy()
        
        # Check if Component column exists for mixed lecture/lab courses
        has_component = 'Component' in df.columns
        
        if has_component:
            # NEW: Create separate keys for each component (lecture/lab treated separately)
            df['CourseKey'] = df['CourseName'].str.strip() + "_" + df['Component'].str.strip().str.lower()
            print("🔧 Detected Component column - treating lecture/lab as separate sessions")
        else:
            # Original behavior: just course name
            df['CourseKey'] = df['CourseName'].str.strip()
        
        agg_records = {}
        for _, row in df.iterrows():
            key = row['CourseKey']
            course_base = row['CourseName'].strip()
            component = row.get('Component', '').strip() if has_component else ''
            
            # Create display name for separate components
            if has_component and component:
                display_name = f"{course_base} ({component})"
            else:
                display_name = course_base
            
            # Default logic: If WeeklyCount not specified and component is Lecture, default to 3
            if 'WeeklyCount' in row and not pd.isna(row['WeeklyCount']):
                weekly = int(row['WeeklyCount'])
            elif component.lower() == 'lecture':
                weekly = 3  # Default to 3 lectures if not specified
                print(f"🔧 Defaulting {course_base} lecture sessions to 3")
            else:
                weekly = 1 if component.lower() in ['lab', 'tutorial'] else 3  # Default lab/tutorial to 1, others to 3
            
            avail_raw = self.parse_availability(row['FacultyAvailability'])
            avail_set = set([a.strip() for a in avail_raw.split(',') if a.strip()]) if avail_raw else set()
            
            # Each component is treated as a separate course entity
            agg_records[key] = {
                'CourseName': display_name,  # Use component-specific display name
                'Faculty': row['Faculty'],  # Keep faculty separate for each component
                'RoomAvailable': row['RoomAvailable'],  # Keep room separate for each component
                'SessionType': component.lower() if component else 'lecture',
                'WeeklyCount': weekly,
                'AvailabilitySet': avail_set,
                'Duration': int(row.get('Duration', 1)) if pd.notna(row.get('Duration', 1)) else 1,
                'Components': [component] if component else []
            }
        
        # Build aggregated DataFrame
        agg_rows = []
        for rec in agg_records.values():
            rec_out = {
                'CourseName': rec['CourseName'],
                'Faculty': rec['Faculty'],
                'FacultyAvailability': ','.join(sorted(rec['AvailabilitySet'])) if rec['AvailabilitySet'] else '',
                'RoomAvailable': rec['RoomAvailable'],
                'SessionType': rec['SessionType'],
                'WeeklyCount': rec['WeeklyCount'],
                'Duration': rec.get('Duration', 1)
            }
            if has_component:
                rec_out['Components'] = ','.join(rec['Components']) if rec['Components'] else ''
            agg_rows.append(rec_out)
        
        aggregated_df = pd.DataFrame(agg_rows)
        self.course_data = aggregated_df  # replace with aggregated version
        print(f"🔄 Aggregated courses: {len(df)} rows -> {len(aggregated_df)} unique course entries")

        # Extract unique entities
        unique_courses = self.course_data['CourseName'].unique().tolist()
        unique_faculty = self.course_data['Faculty'].unique().tolist()
        unique_rooms = self.course_data['RoomAvailable'].unique().tolist()
        
        # Parse all time slots from faculty availability
        all_time_slots = set()
        for availability in self.course_data['FacultyAvailability']:
            availability_str = self.parse_availability(availability)
            if availability_str:
                slots = [slot.strip() for slot in availability_str.split(',')]
                all_time_slots.update(slots)
        
        unique_time_slots = sorted(list(all_time_slots))
        
        # Create course mappings
        courses_info = {}
        faculty_courses = {}
        room_courses = {}
        
        for idx, row in self.course_data.iterrows():
            course_name = str(row['CourseName'])
            faculty_name = str(row['Faculty'])
            room_name = str(row['RoomAvailable'])
            
            # Handle new format with SessionType and WeeklyCount
            if 'SessionType' in row and 'WeeklyCount' in row:
                session_type = str(row['SessionType']).lower()
                weekly_count = int(row['WeeklyCount']) if pd.notna(row['WeeklyCount']) else 1
                
                # Determine duration based on session type
                if session_type == 'lab':
                    duration = 2  # Lab sessions are 2 hours (e.g., 9:00-11:00)
                else:  # lecture
                    duration = weekly_count  # Lectures: 3 weekly lectures = duration 3
            else:
                # Fallback for old format
                duration = int(row['Duration']) if pd.notna(row['Duration']) else 2
                session_type = 'lab' if 'Lab' in str(room_name) else 'lecture'
                weekly_count = duration
            
            availability = self.parse_availability(row['FacultyAvailability'])
            
            # Course information - keep availability as string
            courses_info[course_name] = {
                'id': int(idx),
                'faculty': faculty_name,
                'room': room_name,
                'duration': duration,
                'session_type': session_type,
                'weekly_count': weekly_count,
                'available_slots': availability,  # Keep as string
                'room_type': 'lab' if 'Lab' in str(room_name) else 'lecture' if 'Lecture' in str(room_name) else 'seminar'
            }
            
            # Faculty-course mapping
            if faculty_name not in faculty_courses:
                faculty_courses[faculty_name] = []
            faculty_courses[faculty_name].append({
                'course': course_name,
                'duration': duration,
                'session_type': session_type,
                'weekly_count': weekly_count,
                'available_slots': availability  # Keep as string
            })
            
            # Room-course mapping
            if room_name not in room_courses:
                room_courses[room_name] = []
            room_courses[room_name].append({
                'course': course_name,
                'faculty': faculty_name,
                'duration': duration,
                'session_type': session_type
            })
        
        # Generate potential conflicts (courses that could clash)
        potential_conflicts = []
        for i, row1 in self.course_data.iterrows():
            for j, row2 in self.course_data.iterrows():
                if i < j:  # Avoid duplicates
                    avail1 = self.parse_availability(row1['FacultyAvailability'])
                    avail2 = self.parse_availability(row2['FacultyAvailability'])
                    
                    slots1 = set(avail1.split(',')) if avail1 else set()
                    slots2 = set(avail2.split(',')) if avail2 else set()
                    
                    # Check for overlapping time slots
                    common_slots = slots1.intersection(slots2)
                    
                    # Check for same faculty or same room
                    same_faculty = str(row1['Faculty']) == str(row2['Faculty'])
                    same_room = str(row1['RoomAvailable']) == str(row2['RoomAvailable'])
                    
                    if common_slots and (same_faculty or same_room):
                        potential_conflicts.append({
                            'course1': str(row1['CourseName']),
                            'course2': str(row2['CourseName']),
                            'conflict_type': 'faculty' if same_faculty else 'room',
                            'common_slots': list(common_slots),
                            'conflict_count': len(common_slots)
                        })
        
        return {
            'metadata': {
                'total_courses': len(unique_courses),
                'total_faculty': len(unique_faculty),
                'total_rooms': len(unique_rooms),
                'total_time_slots': len(unique_time_slots),
                'total_potential_conflicts': len(potential_conflicts)
            },
            'entities': {
                'courses': unique_courses,
                'faculty': unique_faculty,
                'rooms': unique_rooms,
                'time_slots': unique_time_slots
            },
            'courses_info': courses_info,
            'faculty_courses': faculty_courses,
            'room_courses': room_courses,
            'potential_conflicts': potential_conflicts
        }
    
    def create_ml_datasets(self) -> Dict[str, pd.DataFrame]:
        """Create various ML-ready datasets."""
        if self.course_data is None:
            return {}
        
        datasets = {}
        
        # 1. Basic course dataset
        datasets['courses'] = self.course_data.copy()
        
        # 2. Faculty workload analysis
        faculty_workload = self.course_data.groupby('Faculty').agg({
            'Duration': ['sum', 'count', 'mean'],
            'CourseName': lambda x: list(x)
        }).round(2)
        faculty_workload.columns = ['total_hours', 'course_count', 'avg_duration', 'courses']
        datasets['faculty_workload'] = faculty_workload.reset_index()
        
        # 3. Room utilization analysis
        room_utilization = self.course_data.groupby('RoomAvailable').agg({
            'Duration': ['sum', 'count'],
            'Faculty': lambda x: list(set(x)),
            'CourseName': lambda x: list(x)
        }).round(2)
        room_utilization.columns = ['total_hours', 'course_count', 'faculty_list', 'courses']
        datasets['room_utilization'] = room_utilization.reset_index()
        
        # 4. Time slot analysis
        time_slot_data = []
        for idx, row in self.course_data.iterrows():
            availability = self.parse_availability(row['FacultyAvailability'])
            if availability:
                slots = [slot.strip() for slot in availability.split(',')]
                for slot in slots:
                    time_slot_data.append({
                        'course': str(row['CourseName']),
                        'faculty': str(row['Faculty']),
                        'room': str(row['RoomAvailable']),
                        'time_slot': slot,
                        'duration': int(row['Duration']) if pd.notna(row['Duration']) else 2
                    })
        
        if time_slot_data:
            datasets['time_slot_mapping'] = pd.DataFrame(time_slot_data)
        
        return datasets
    
    def export_to_csv(self, output_dir: str = './data/'):
        """Export data to CSV files."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Export original data
            self.course_data.to_csv(f'{output_dir}original_courses.csv', index=False)
            
            # Export ML datasets
            datasets = self.create_ml_datasets()
            
            for name, df in datasets.items():
                df.to_csv(f'{output_dir}{name}.csv', index=False)
                print(f"   - {name}.csv ({len(df)} records)")
            
            print(f"✅ CSV files exported to {output_dir}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {str(e)}")
    
    def export_to_json(self, output_dir: str = './data/'):
        """Export data to JSON files."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Export training features
            training_data = self.generate_training_features()
            
            with open(f'{output_dir}training_dataset.json', 'w') as f:
                json.dump(training_data, f, indent=2)
            
            print(f"✅ JSON files exported to {output_dir}")
            print(f"📋 Files created:")
            print(f"   - training_dataset.json (structured for ML training)")
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {str(e)}")

def convert_csv_to_training_data():
    """Convert CSV data to training format."""
    try:
        # Use the CSVToDataConverter class to get proper aggregation
        converter = CSVToDataConverter()
        
        # Load and aggregate the CSV data
        if not converter.load_csv_data('courses.csv'):
            return False
        
        # Generate training features (this includes aggregation)
        training_data = converter.generate_training_features()
        
        if not training_data:
            print("❌ Failed to generate training features")
            return False
        
        # Create data directory
        os.makedirs('./data', exist_ok=True)
        
        # Save JSON
        with open('./data/training_dataset.json', 'w') as f:
            json.dump(training_data, f, indent=2)
        
        print("✅ Conversion completed! Data ready for training.")
        return True
        
    except Exception as e:
        print(f"❌ Error converting data: {e}")
        return False

# Keep the old SQL function for backward compatibility
def convert_sql_to_training_data():
    """Legacy function - redirects to CSV converter."""
    print("⚠️  SQL conversion not available. Using CSV converter instead.")
    return convert_csv_to_training_data()

if __name__ == "__main__":
    # Disabled auto-conversion to prevent overwriting user data
    # convert_csv_to_training_data()
    print("Input parser module loaded. Use convert_csv_to_training_data() manually if needed.")