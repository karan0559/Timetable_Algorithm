#!/usr/bin/env python3
"""
🎓 Timetable Generator API Server (Simplified)
Smart India Hackathon (SIH) Integration Ready

Flask API server providing intelligent timetable generation endpoints.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import traceback
from datetime import datetime
import logging

# Import our timetable solver
from timetable.simple_solver import SimpleTimetableSolver

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_VERSION = "1.0"
API_TITLE = "Timetable Generator API"
API_DESCRIPTION = "Intelligent timetable generation for educational institutions"

@app.route('/', methods=['GET'])
def api_info():
    """API Information endpoint"""
    return jsonify({
        "service": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "status": "running",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /sample": "Sample input format",
            "POST /validate": "Validate course data",
            "POST /generate": "Generate timetable (main endpoint)"
        },
        "documentation": "/docs",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "api_version": API_VERSION,
        "solvers": {
            "simple_solver": "available"
        },
        "data_files": {
            "training_dataset": os.path.exists('./data/training_dataset.json'),
            "courses_csv": os.path.exists('./courses.csv')
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/sample', methods=['GET'])
def sample_format():
    """Sample input format for frontend developers"""
    return jsonify({
        "sample_input": {
            "courses": [
                {
                    "course_name": "Mathematics",
                    "faculty": "Dr. Arjun Mehta",
                    "room": "Room 101",
                    "duration": 1,
                    "weekly_count": 3,
                    "session_type": "lecture",
                    "availability": "Mon1,Mon2,Tue1,Tue2,Wed1,Wed2,Thu1,Thu2,Fri1,Fri2"
                },
                {
                    "course_name": "Physics Lab",
                    "faculty": "Prof. Kavita Sharma",
                    "room": "Lab 101",
                    "duration": 2,
                    "weekly_count": 1,
                    "session_type": "lab",
                    "availability": "Mon3,Mon4,Tue3,Tue4,Wed3,Wed4,Thu3,Thu4,Fri3,Fri4"
                }
            ],
            "solver_preference": "simple",
            "options": {
                "allow_conflicts": False,
                "optimize_quality": True
            }
        },
        "expected_output": {
            "success": True,
            "timetable": {
                "Monday": {
                    "09:00-10:00": [
                        {
                            "course": "Mathematics",
                            "faculty": "Dr. Arjun Mehta",
                            "room": "Room 101",
                            "duration": 1,
                            "session_type": "lecture"
                        }
                    ]
                }
            },
            "statistics": {
                "total_courses": 2,
                "conflicts_resolved": 0,
                "quality_rating": "EXCELLENT"
            }
        }
    })

@app.route('/validate', methods=['POST'])
def validate_courses():
    """Validate course data endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        if 'courses' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'courses' field in request"
            }), 400
        
        courses = data['courses']
        validation_errors = []
        warnings = []
        
        # Validate each course
        for i, course in enumerate(courses):
            course_errors = []
            
            # Required fields
            required_fields = ['course_name', 'faculty', 'room', 'duration', 'weekly_count', 'session_type']
            for field in required_fields:
                if field not in course:
                    course_errors.append(f"Missing required field: {field}")
            
            # Validate data types
            if 'duration' in course and not isinstance(course['duration'], int):
                course_errors.append("Duration must be an integer")
            
            if 'weekly_count' in course and not isinstance(course['weekly_count'], int):
                course_errors.append("Weekly count must be an integer")
            
            if 'session_type' in course and course['session_type'] not in ['lecture', 'lab']:
                course_errors.append("Session type must be 'lecture' or 'lab'")
            
            # Check for potential conflicts
            if 'session_type' in course and course['session_type'] == 'lab' and course.get('duration', 1) < 2:
                warnings.append(f"Course {i+1}: Lab sessions typically require 2+ hours")
            
            if course_errors:
                validation_errors.append({
                    "course_index": i + 1,
                    "course_name": course.get('course_name', 'Unknown'),
                    "errors": course_errors
                })
        
        # Check for duplicate faculty-time conflicts (basic check)
        faculty_courses = {}
        for course in courses:
            faculty = course.get('faculty')
            if faculty:
                if faculty in faculty_courses:
                    faculty_courses[faculty].append(course.get('course_name', 'Unknown'))
                else:
                    faculty_courses[faculty] = [course.get('course_name', 'Unknown')]
        
        for faculty, course_list in faculty_courses.items():
            if len(course_list) > 1:
                warnings.append(f"Faculty '{faculty}' teaches multiple courses: {', '.join(course_list)}. Check for time conflicts.")
        
        return jsonify({
            "success": len(validation_errors) == 0,
            "total_courses": len(courses),
            "validation_errors": validation_errors,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Validation failed: {str(e)}"
        }), 500

@app.route('/generate', methods=['POST'])
def generate_timetable():
    """Main timetable generation endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Validate input
        if 'courses' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'courses' field in request"
            }), 400
        
        courses = data['courses']
        options = data.get('options', {})
        
        logger.info(f"Generating timetable for {len(courses)} courses using simple solver")
        
        # Use simple solver with direct course data (bypassing conversion)
        solver = SimpleTimetableSolver()
        
        # Generate timetable directly from API courses
        timetable = solver.solve_timetable_from_data(courses)
        
        if not timetable:
            return jsonify({
                "success": False,
                "error": "Failed to generate timetable - no solution found"
            }), 500
        
        # Generate statistics
        stats = generate_statistics(timetable, {"metadata": {"total_courses": len(courses)}}, solver)
        
        return jsonify({
            "success": True,
            "timetable": timetable,
            "statistics": stats,
            "solver_used": "simple",
            "generation_time": datetime.now().isoformat(),
            "total_courses": len(courses)
        })
        
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"Timetable generation failed: {str(e)}"
        }), 500

def convert_api_to_training_format(courses):
    """Convert API course format to internal training data format"""
    courses_info = {}
    
    for course in courses:
        course_name = course['course_name'].lower().strip()
        
        # Parse availability string to slot format
        availability = course.get('availability', '')
        available_slots = parse_availability_to_slots(availability)
        
        # Convert session_type to component format
        component = "Lecture" if course['session_type'] == "lecture" else "Lab"
        
        courses_info[course_name] = {
            "faculty": course['faculty'],
            "room": course['room'],
            "sessions": [  # ✅ Wrap in sessions array
                {
                    "component": component,  # ✅ Use "component" not "session_type"
                    "duration": course['duration'],
                    "weekly_count": course['weekly_count'],
                    "available_slots": available_slots
                }
            ]
        }
    
    return {
        "metadata": {
            "total_courses": len(courses),
            "generation_date": datetime.now().isoformat(),
            "format_version": "1.0",
            "description": "API generated dataset",
            "source": "api_request"
        },
        "courses_info": courses_info
    }

def parse_availability_to_slots(availability_string):
    """Parse availability string (e.g., 'Mon1,Mon2,Tue1') to slot format"""
    if not availability_string:
        # Default to all morning slots if no availability specified
        slots = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        times = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '14:00-15:00', '15:00-16:00']
        for day in days:
            for time in times:
                slots.append([day, time])
        return slots
    
    # Parse compact format like "Mon1,Mon2,Tue1"
    day_mapping = {
        'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 
        'Thu': 'Thursday', 'Fri': 'Friday'
    }
    
    time_mapping = {
        '1': '09:00-10:00', '2': '10:00-11:00', '3': '11:00-12:00',
        '4': '12:00-13:00', '5': '13:00-14:00', '6': '14:00-15:00',
        '7': '15:00-16:00', '8': '16:00-17:00', '9': '17:00-18:00'
    }
    
    slots = []
    parts = availability_string.split(',')
    
    for part in parts:
        part = part.strip()
        if len(part) >= 4:  # e.g., "Mon1"
            day_code = part[:3]
            time_code = part[3:]
            
            if day_code in day_mapping and time_code in time_mapping:
                day = day_mapping[day_code]
                time = time_mapping[time_code]
                slots.append([day, time])
    
    # If parsing failed, return default slots
    if not slots:
        slots = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        times = ['09:00-10:00', '10:00-11:00', '14:00-15:00']
        for day in days:
            for time in times:
                slots.append([day, time])
    
    return slots

def generate_statistics(timetable, training_data, solver):
    """Generate statistics about the generated timetable"""
    total_sessions = 0
    days_used = set()
    courses_scheduled = set()
    
    for day, day_schedule in timetable.items():
        # Skip non-day keys like 'penalty_analysis'
        if day == 'penalty_analysis':
            continue
            
        if any(day_schedule.values()):  # If day has any sessions
            days_used.add(day)
        
        for time_slot, sessions in day_schedule.items():
            if sessions:
                total_sessions += len(sessions)
                for session in sessions:
                    courses_scheduled.add(session['course'])
    
    # Calculate quality rating
    total_courses = training_data['metadata']['total_courses']
    coverage = len(courses_scheduled) / total_courses if total_courses > 0 else 0
    
    if coverage == 1.0:
        quality_rating = "EXCELLENT"
    elif coverage >= 0.8:
        quality_rating = "GOOD"
    elif coverage >= 0.6:
        quality_rating = "FAIR"
    else:
        quality_rating = "NEEDS_IMPROVEMENT"
    
    # Get penalty information if available
    penalty_score = getattr(solver, 'total_penalty_score', 0)
    
    return {
        "total_sessions": total_sessions,
        "total_courses": total_courses,
        "courses_scheduled": len(courses_scheduled),
        "days_utilized": len(days_used),
        "coverage_percentage": round(coverage * 100, 1),
        "quality_rating": quality_rating,
        "penalty_score": penalty_score,
        "conflicts_resolved": 0  # Could be enhanced to track actual conflicts
    }

@app.route('/docs', methods=['GET'])
def api_documentation():
    """API Documentation endpoint"""
    return jsonify({
        "documentation": "SIH_INTEGRATION_GUIDE.md",
        "endpoints": {
            "GET /": "API information and available endpoints",
            "GET /health": "Health check and system status",
            "GET /sample": "Sample input/output format for developers",
            "POST /validate": "Validate course data before generation",
            "POST /generate": "Generate timetable (main endpoint)"
        },
        "github": "https://github.com/karan0559/Timetable_Algorithm"
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/sample", "/validate", "/generate", "/docs"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "Please check server logs for details"
    }), 500

if __name__ == '__main__':
    print("🎓 Timetable Generator API Server")
    print("=================================")
    
    # Configuration from environment variables
    port = int(os.environ.get('API_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    host = os.environ.get('API_HOST', '127.0.0.1')
    
    print(f"🚀 Starting server...")
    print(f"📡 URL: http://{host}:{port}")
    print(f"🔧 Debug: {debug}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"💡 Health: http://{host}:{port}/health")
    print(f"🌐 Frontend: Open api_testing_demo.html in browser")
    print(f"")
    print(f"⚡ Server starting... (Press Ctrl+C to stop)")
    print(f"")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Start the Flask development server
    app.run(host=host, port=port, debug=debug)
