#!/usr/bin/env python3
"""
🎓 TIMETABLE GENERATOR API SERVER
Created for Smart India Hackathon (SIH)
Provides REST API endpoints for frontend integration
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import pandas as pd
from datetime import datetime
import tempfile
import uuid

# Import our timetable modules
from timetable.input_parser import CSVToDataConverter
from timetable.simple_solver import SimpleTimetableSolver

# Try to import OR-Tools solver
try:
    from timetable.ortools_solver import ORToolsTimetableSolver
    ORTOOLS_AVAILABLE = True
except:
    ORTOOLS_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

class TimetableAPI:
    def __init__(self):
        self.data_converter = CSVToDataConverter()
        self.simple_solver = SimpleTimetableSolver()
        if ORTOOLS_AVAILABLE:
            self.ortools_solver = ORToolsTimetableSolver()
        
    def validate_course_data(self, course_data):
        """Validate incoming course data from frontend."""
        required_fields = ['CourseName', 'Faculty', 'FacultyAvailability', 'RoomAvailable', 'Duration']
        
        if not isinstance(course_data, list):
            return False, "Course data must be a list of courses"
        
        if len(course_data) == 0:
            return False, "No courses provided"
        
        for i, course in enumerate(course_data):
            if not isinstance(course, dict):
                return False, f"Course {i+1} must be an object"
            
            for field in required_fields:
                if field not in course:
                    return False, f"Course {i+1} missing required field: {field}"
            
            # Validate duration
            try:
                duration = int(course['Duration'])
                if duration < 1 or duration > 8:
                    return False, f"Course {i+1} duration must be between 1-8 hours"
            except:
                return False, f"Course {i+1} duration must be a number"
        
        return True, "Valid"
    
    def process_courses(self, course_data):
        """Process course data and generate timetable."""
        try:
            # Create temporary CSV file
            session_id = str(uuid.uuid4())[:8]
            temp_csv = f"temp_courses_{session_id}.csv"
            
            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(course_data)
            df.to_csv(temp_csv, index=False)
            
            # Load and convert data
            self.data_converter.load_csv_data(temp_csv)
            self.data_converter.export_to_json('./data/')
            
            # Generate timetable using Simple Solver (more reliable)
            timetable = self.simple_solver.solve_timetable()
            
            if timetable:
                # Export solution
                solution_file = f"./data/timetable_{session_id}.json"
                self.simple_solver.export_solution(timetable, solution_file)
                
                # Validate for conflicts
                conflicts = self.simple_solver.validate_timetable(timetable)
                
                # Clean up
                if os.path.exists(temp_csv):
                    os.remove(temp_csv)
                
                return {
                    'success': True,
                    'timetable': timetable,
                    'conflicts': conflicts,
                    'session_id': session_id,
                    'total_courses': len(course_data),
                    'scheduled_courses': sum(1 for day in timetable.values() for time in day.values() for course in time if course),
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to generate timetable',
                    'session_id': session_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Processing error: {str(e)}'
            }

# Initialize API
timetable_api = TimetableAPI()

@app.route('/', methods=['GET'])
def home():
    """API information endpoint."""
    return jsonify({
        'service': 'Timetable Generator API',
        'version': '1.0.0',
        'hackathon': 'Smart India Hackathon (SIH)',
        'status': 'active',
        'endpoints': {
            'POST /generate': 'Generate timetable from course data',
            'GET /health': 'Health check',
            'GET /sample': 'Get sample input format',
            'POST /validate': 'Validate course data format'
        },
        'ortools_available': ORTOOLS_AVAILABLE
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'solvers': {
            'simple_solver': True,
            'ortools_solver': ORTOOLS_AVAILABLE
        }
    })

@app.route('/sample', methods=['GET'])
def get_sample_format():
    """Get sample input format for frontend developers."""
    sample_data = [
        {
            "CourseName": "Data Structures",
            "Faculty": "Dr. Smith",
            "FacultyAvailability": "Mon2,Wed2,Fri3",
            "RoomAvailable": "Hall 102",
            "Duration": 3
        },
        {
            "CourseName": "Database Systems", 
            "Faculty": "Dr. Johnson",
            "FacultyAvailability": "Tue3,Thu3,Thu4",
            "RoomAvailable": "Computer Lab 201",
            "Duration": 2
        },
        {
            "CourseName": "Machine Learning",
            "Faculty": "Dr. Wilson",
            "FacultyAvailability": "Mon1,Wed1,Fri1",
            "RoomAvailable": "AI Lab 301",
            "Duration": 3
        }
    ]
    
    return jsonify({
        'sample_input': sample_data,
        'field_descriptions': {
            'CourseName': 'Name of the course (string)',
            'Faculty': 'Faculty member name (string)',
            'FacultyAvailability': 'Available time slots as comma-separated values (e.g., Mon2,Wed3,Fri1)',
            'RoomAvailable': 'Room name or number (string)',
            'Duration': 'Course duration in hours per week (integer, 1-8)'
        },
        'time_slot_format': {
            'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            'slots': {
                '1': '09:00-10:00',
                '2': '10:00-11:00', 
                '3': '11:00-12:00',
                '4': '12:00-13:00',
                '5': '14:00-15:00',
                '6': '15:00-16:00',
                '7': '16:00-17:00',
                '8': '17:00-18:00'
            }
        }
    })

@app.route('/validate', methods=['POST'])
def validate_data():
    """Validate course data format."""
    try:
        data = request.get_json()
        
        if not data or 'courses' not in data:
            return jsonify({
                'valid': False,
                'error': 'Request must contain "courses" field with course data'
            }), 400
        
        is_valid, message = timetable_api.validate_course_data(data['courses'])
        
        return jsonify({
            'valid': is_valid,
            'message': message,
            'course_count': len(data['courses']) if is_valid else 0
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Validation error: {str(e)}'
        }), 400

@app.route('/generate', methods=['POST'])
def generate_timetable():
    """Main endpoint to generate timetable from course data."""
    try:
        data = request.get_json()
        
        if not data or 'courses' not in data:
            return jsonify({
                'success': False,
                'error': 'Request must contain "courses" field with course data'
            }), 400
        
        # Validate data
        is_valid, validation_message = timetable_api.validate_course_data(data['courses'])
        if not is_valid:
            return jsonify({
                'success': False,
                'error': f'Invalid data: {validation_message}'
            }), 400
        
        # Process and generate timetable
        result = timetable_api.process_courses(data['courses'])
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/download/<session_id>', methods=['GET'])
def download_timetable(session_id):
    """Download generated timetable as JSON file."""
    try:
        file_path = f"./data/timetable_{session_id}.json"
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=f'timetable_{session_id}.json')
        else:
            return jsonify({'error': 'Timetable file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('./data', exist_ok=True)
    
    print("🎓 TIMETABLE GENERATOR API SERVER")
    print("=" * 50)
    print("🚀 Starting server for SIH Hackathon...")
    print("📡 Frontend teams can now integrate!")
    print("📚 Available endpoints:")
    print("   GET  /          - API information")
    print("   GET  /health    - Health check")
    print("   GET  /sample    - Sample input format")
    print("   POST /validate  - Validate data")
    print("   POST /generate  - Generate timetable")
    print("   GET  /download/<id> - Download timetable")
    print("=" * 50)
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True)
