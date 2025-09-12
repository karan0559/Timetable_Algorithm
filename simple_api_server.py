#!/usr/bin/env python3
"""
Simple API Server for Timetable Generator
Basic Flask server for timetable generation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

# Import our timetable components
from timetable.simple_solver import SimpleTimetableSolver

app = Flask(__name__)
CORS(app)

# Global solver instance
solver = SimpleTimetableSolver()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            'GET /api/health',
            'POST /api/generate-timetable'
        ]
    })

@app.route('/api/generate-timetable', methods=['POST'])
def generate_timetable():
    """Generate timetable from course data."""
    try:
        data = request.get_json()
        
        if not data or 'courses' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing courses data',
                'message': 'Request must include courses array'
            }), 400
        
        courses_data = data['courses']
        
        # Convert to simple format for solver
        courses_info = {}
        for i, course in enumerate(courses_data):
            course_name = course.get('course_name', '').strip().lower()
            faculty = course.get('faculty', '').strip().lower()
            availability = course.get('faculty_availability', '').strip()
            room = course.get('room', '').strip()
            duration = int(course.get('duration', 2))
            weekly_count = int(course.get('weekly_count', duration))
            
            courses_info[course_name] = {
                'id': i,
                'faculty': faculty,
                'room': room,
                'duration': duration,
                'session_type': course.get('session_type', 'lecture'),
                'weekly_count': weekly_count,
                'available_slots': availability,
                'room_type': 'lab' if 'lab' in room.lower() else 'lecture'
            }
        
        # Create dataset for solver
        dataset = {
            'metadata': {'total_courses': len(courses_info)},
            'courses_info': courses_info
        }
        
        # Generate timetable
        timetable = solver.solve_timetable_from_data(dataset)
        
        if timetable:
            # Calculate metrics
            total_courses = len(courses_info)
            scheduled_courses = set()
            total_sessions = 0
            
            for day_schedule in timetable.values():
                for time_classes in day_schedule.values():
                    total_sessions += len(time_classes)
                    for class_info in time_classes:
                        scheduled_courses.add(class_info['course'])
            
            success_rate = (len(scheduled_courses) / total_courses) * 100
            
            return jsonify({
                'success': True,
                'timetable': timetable,
                'metrics': {
                    'total_courses': total_courses,
                    'scheduled_courses': len(scheduled_courses),
                    'success_rate': f"{success_rate:.1f}%",
                    'total_sessions': total_sessions
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Timetable generation failed',
                'message': 'Unable to generate valid timetable'
            }), 422
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Internal server error'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Simple Timetable API Server...")
    print("📍 Health check: http://localhost:5000/api/health")
    print("📝 Generate timetable: POST http://localhost:5000/api/generate-timetable")
    print("✅ Ready for requests!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
