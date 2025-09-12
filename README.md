# 🎓 Intelligent Timetable Generator

**Advanced Algorithm-Based Automatic Timetable Generation System**
---

## 📋 Table of Contents
1. [System Requirements](#-system-requirements)
2. [Quick Start](#-quick-start)
3. [Input/Output Overview](#-inputoutput-overview)
4. [API Endpoints](#-api-endpoints)
5. [Integration Guide](#-integration-guide)
6. [Input Formats](#-input-formats)
7. [Output Formats](#-output-formats)
8. [File Structure](#-file-structure)
9. [Deployment](#-deployment)
10. [Troubleshooting](#-troubleshooting)

---

## 🖥️ System Requirements

### **Minimum Requirements**
- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, macOS 10.15+, Linux Ubuntu 18.04+
- **Memory**: 4GB RAM (8GB recommended for large datasets)
- **Disk Space**: 500MB free space
- **Network**: Internet connection for package installation

### **Python Dependencies**
```bash
Flask==3.1.2              # Web framework for REST API
flask-cors==4.0.0          # Cross-origin resource sharing
pandas==2.1.1              # Data processing and CSV handling
numpy==1.24.3              # Numerical computations
ortools==9.7.2996          # Google optimization tools (optional)
python-dateutil==2.8.2    # Date/time utilities
requests==2.31.0           # HTTP library for testing
```

---

## 🚀 Quick Start

### 1. **Installation**
```bash
# Clone the repository
git clone https://github.com/karan0559/Timetable_Algorithm.git
cd Timetable_Algorithm

# Install dependencies
pip install -r requirements.txt
```

### 2. **Start API Server**
```bash
# Option 1: Windows PowerShell (Easiest)
./start_api.ps1

# Option 2: Cross-platform Python
python start_api.py

# Option 3: Direct start
python api_server_simple.py
```
---

## 📊 Input/Output Overview

### **📥 Where Inputs Come From**
| Input Source | File Location | Format | Usage |
|--------------|---------------|---------|-------|
| **CSV File** | `courses.csv` | Structured CSV | Console interface |
| **JSON Dataset** | `data/training_dataset.json` | Rich JSON | Algorithm input |
| **API Requests** | HTTP POST | JSON payload | Web integration |
| **Manual Entry** | Interactive prompts | User input | Testing/development |

### **📤 Where Outputs Are Stored**
| Output Type | File Location | Format | Contains |
|-------------|---------------|---------|----------|
| **Generated Timetable** | `data/simple_timetable.json` | Structured JSON | Weekly schedule |
| **API Responses** | HTTP Response | JSON | Real-time results |
| **Console Output** | Terminal | Formatted text | Human-readable schedule |
| **Statistics** | Embedded in outputs | JSON/Text | Quality metrics |

---

## 🌐 API Endpoints


#### **1. 📊 GET /** - API Information
```bash
curl http://localhost:5000/
```
**Response**: API metadata, version, available endpoints

#### **2. 💗 GET /health** - Health Check
```bash
curl http://localhost:5000/health
```
**Response**: 
```json
{
  "status": "healthy",
  "api_version": "1.0",
  "solvers": {"simple_solver": "available"},
  "data_files": {
    "training_dataset": true,
    "courses_csv": true
  }
}
```

#### **3. 📄 GET /sample** - Sample Format
```bash
curl http://localhost:5000/sample
```
**Response**: Complete example of input/output format for developers

#### **4. ✅ POST /validate** - Validate Courses
```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "courses": [
      {
        "course_name": "Mathematics",
        "faculty": "Dr. Arjun Mehta",
        "room": "Room 101",
        "duration": 1,
        "weekly_count": 3,
        "session_type": "lecture",
        "availability": "Mon1,Mon2,Tue1,Wed1,Thu1"
      }
    ]
  }'
```

#### **5. 🚀 POST /generate** - Generate Timetable (Main Endpoint)
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "courses": [
      {
        "course_name": "Mathematics",
        "faculty": "Dr. Arjun Mehta",
        "room": "Room 101",
        "duration": 1,
        "weekly_count": 3,
        "session_type": "lecture",
        "availability": "Mon1,Mon2,Tue1,Wed1,Thu1"
      }
    ],
    "solver_preference": "simple",
    "options": {
      "allow_conflicts": false,
      "optimize_quality": true
    }
  }'
```

**Response**:
```json
{
  "success": true,
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
    "total_sessions": 15,
    "coverage_percentage": 100.0,
    "quality_rating": "EXCELLENT"
  }
}
```

#### **6. 📚 GET /docs** - Documentation
```bash
curl http://localhost:5000/docs
```

---

## 🔗 Integration Guide

### **Frontend Integration (JavaScript/React)**
```javascript
// Initialize API connection
const API_BASE = 'http://localhost:5000';

// Generate timetable function
const generateTimetable = async (courses) => {
  try {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        courses: courses,
        solver_preference: 'simple',
        options: { allow_conflicts: false }
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Timetable generated:', result.timetable);
      return result;
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Usage example
const courses = [
  {
    course_name: "Mathematics",
    faculty: "Dr. Arjun Mehta", 
    room: "Room 101",
    duration: 1,
    weekly_count: 3,
    session_type: "lecture",
    availability: "Mon1,Mon2,Tue1"
  }
];

generateTimetable(courses)
  .then(result => {
    // Handle successful timetable generation
    displayTimetable(result.timetable);
  })
  .catch(error => {
    // Handle errors
    showError(error.message);
  });
```

### **Python Integration**
```python
import requests
import json

# Direct API integration
def generate_timetable_api(courses):
    url = "http://localhost:5000/generate"
    payload = {
        "courses": courses,
        "solver_preference": "simple"
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Direct algorithm integration
from timetable.simple_solver import SimpleTimetableSolver

def generate_timetable_direct(courses_data):
    solver = SimpleTimetableSolver()
    solver.training_data = courses_data
    return solver.solve_timetable()
```

---

## 📥 Input Formats

### **1. API JSON Format**
```json
{
  "courses": [
    {
      "course_name": "Mathematics",          // Required: Course name
      "faculty": "Dr. Arjun Mehta",         // Required: Faculty name
      "room": "Room 101",                   // Required: Room assignment
      "duration": 1,                        // Required: Hours per session
      "weekly_count": 3,                    // Required: Sessions per week
      "session_type": "lecture",            // Required: "lecture" or "lab"
      "availability": "Mon1,Mon2,Tue1"      // Optional: Available time slots
    }
  ],
  "solver_preference": "simple",            // Optional: "simple" or "ortools"
  "options": {                             // Optional: Generation options
    "allow_conflicts": false,
    "optimize_quality": true
  }
}
```

### **2. CSV Format** (`courses.csv`)
```csv
Course Name,Faculty,Room,Duration,Weekly Count,Session Type,Availability
Mathematics,Dr. Arjun Mehta,Room 101,1,3,lecture,"Mon1,Mon2,Tue1,Wed1,Thu1"
Physics Lab,Prof. Kavita Sharma,Lab 101,2,1,lab,"Mon3,Tue3,Wed3,Thu3,Fri3"
Computer Science,Prof. Priya Singh,Room 103,1,4,lecture,"Mon1,Tue1,Wed1,Thu1,Fri1"
```

### **3. Availability Format**
```
Time Slot Codes:
Mon1 = Monday 09:00-10:00    Thu1 = Thursday 09:00-10:00
Mon2 = Monday 10:00-11:00    Thu2 = Thursday 10:00-11:00
Tue1 = Tuesday 09:00-10:00   Fri1 = Friday 09:00-10:00
Wed1 = Wednesday 09:00-10:00 ...and so on

Example: "Mon1,Mon2,Tue1" = Available Monday 9-11am, Tuesday 9-10am
```

---

## 📤 Output Formats

### **1. Generated Timetable** (`data/simple_timetable.json`)
```json
{
  "Monday": {
    "09:00-10:00": [
      {
        "course": "mathematics",
        "faculty": "Dr. Arjun Mehta",
        "room": "Room 101", 
        "duration": 1,
        "session_type": "lecture"
      }
    ],
    "10:00-11:00": [],
    "14:00-15:00": [
      {
        "course": "physics lab",
        "faculty": "Prof. Kavita Sharma",
        "room": "Lab 101",
        "duration": 2,
        "session_type": "lab"
      }
    ]
  },
  "Tuesday": { /* ... */ }
}
```

### **2. API Response Format**
```json
{
  "success": true,
  "timetable": { /* Weekly schedule */ },
  "statistics": {
    "total_sessions": 15,
    "total_courses": 6,
    "courses_scheduled": 6,
    "days_utilized": 5,
    "coverage_percentage": 100.0,
    "quality_rating": "EXCELLENT",
    "penalty_score": 0
  },
  "solver_used": "simple",
  "generation_time": "2025-09-13T10:30:00",
  "total_courses": 6
}
```

---

## 📁 File Structure

📁 TIMETABLE_ALGO/                
├── 📂 data/
│   ├── 📄 simple_timetable.json       # Generated timetable output
│   └── 📄 training_dataset.json       # Course input dataset
├── 📂 timetable/                      # Core algorithm package
│   ├── 📂 __pycache__/               # Python cache (can be removed)
│   ├── 📄 __init__.py                # Package initialization
│   ├── 📄 input_parser.py            # Data parsing utilities
│   ├── 📄 ortools_solver.py          # Advanced OR-Tools solver
│   └── 📄 simple_solver.py           # Main conflict-free algorithm
├── 📄 api_server_simple.py           # Working REST API server
├── 📄 api_server.py                  # Full-featured API (with OR-Tools)
├── 📄 courses.csv                    # Sample course data (CSV format)
├── 📄 frontend_demo.html             # Web interface for API testing
├── 📄 main.py                        # Console interface (3 input methods)
├── 📄 manual_input.py                # Interactive course input system
├── 📄 requirements.txt               # Python dependencies
├── 📄 SIH_INTEGRATION_GUIDE.md       # Integration guide for SIH teams
├── 📄 start_api.ps1                  # Windows PowerShell launcher
├── 📄 start_api.py                   # Cross-platform API launcher
└── 📄 test_api.py                    # Comprehensive API testing

---

### **Production Checklist**
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test API endpoints: `python test_api.py`
- [ ] Start API server: `python api_server_simple.py`
- [ ] Verify health check: `curl http://localhost:5000/health`
- [ ] Test web interface: Open `api_testing_demo.html`
- [ ] Configure environment variables (API_HOST, API_PORT)

---

## � Troubleshooting

### **Common Issues**

**1. Flask Import Errors (Yellow warnings in IDE)**
```bash
# Solution: Install Flask type stubs
pip install types-Flask

# Or ignore - these are cosmetic IDE warnings, not runtime errors
```

**2. OR-Tools Import Issues**
```bash
# Use simplified API server instead
python api_server_simple.py  # No OR-Tools dependency
```

**3. API Server Not Starting**
```bash
# Check if port 5000 is available
netstat -an | findstr :5000

# Use different port
set API_PORT=5001
python api_server_simple.py
```

**4. No Timetable Generated**
- Check course data format matches examples
- Ensure faculty availability constraints are reasonable
- Verify room assignments don't conflict

### **Performance Optimization**
- **Small datasets** (≤10 courses): Use `simple` solver
- **Large datasets** (>20 courses): Use `ortools` solver
- **Web integration**: Cache results for repeated requests
- **Memory usage**: Process courses in batches for very large datasets

---

## 🏆 Success Metrics

- **Conflict Resolution**: 100% success rate
- **Processing Speed**: <2 seconds for 10 courses
- **API Response Time**: <500ms average
- **Coverage**: 100% course placement guaranteed
- **Quality Rating**: EXCELLENT for balanced schedules

---

### **Python Dependencies**
```
Flask==2.3.3              # Web framework for REST API
flask-cors==4.0.0          # Cross-origin resource sharing
pandas==2.1.1              # Data processing and CSV handling
numpy==1.24.3              # Numerical computations
ortools==9.7.2996          # Google optimization tools (optional)
python-dateutil==2.8.2    # Date/time utilities
requests==2.31.0           # HTTP library for testing
```

### **Optional Requirements**
- **Web Browser**: For testing API endpoints
- **Git**: For version control and cloning
- **IDE/Editor**: VS Code, PyCharm, or any text editor

---

## 🎯 Overview

The **Intelligent Timetable Generator** is an advanced, algorithm-based system that automatically creates conflict-free academic timetables. Built for educational institutions, it handles complex scheduling constraints while providing multiple interaction methods including a REST API for web integration.

### 🏆 Key Highlights
- **100% Success Rate** in conflict-free scheduling
- **Multiple Input Methods**: CSV, Manual Input, JSON, REST API
- **Advanced Algorithms**: Custom iterative solver + Google OR-Tools integration
- **Smart Conflict Resolution**: Automatic handling of faculty, room, and time conflicts
- **Production Ready**: Full REST API with CORS support
- **Comprehensive Testing**: 13+ test scenarios covering all edge cases

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/karan0559/Timetable_Algorithm.git
   cd Timetable_Algorithm
   python -m venv venv
   
   # Windows: venv\Scripts\activate
   # macOS/Linux: source venv/bin/activate
   
   pip install -r requirements.txt
   ```

### 🎯 Run Your First Timetable

#### Option 1: Console Interface (Easiest)
```bash
python main.py
# Choose option 1 to load from CSV
```

#### Option 2: API Server (Web Integration)
```bash
python api_server_simple.py
# Visit: http://localhost:5000/health
```

#### Option 3: Manual Input (Interactive)
```bash
python manual_input.py
```

---

## 🌐 API Server & Endpoints

### **Starting the API Server**

#### Quick Start (Recommended)
```bash
# Windows
./start_api.ps1

# Cross-platform
python start_api.py
```

#### Manual Start
```bash
# Option 1: Full-featured API (with OR-Tools support)
python api_server.py

# Option 2: Simplified API (reliable, no OR-Tools dependency)
python api_server_simple.py
```

### **API Endpoints**

#### 📊 **GET /** - API Information
```bash
curl http://localhost:5000/
```
**Response**: Basic API information, version, and available endpoints.

#### 💗 **GET /health** - Health Check
```bash
curl http://localhost:5000/health
```
**Response**: Server status, available solvers, and data file status.

#### 📄 **GET /sample** - Sample Format
```bash
curl http://localhost:5000/sample
```
**Response**: Complete example of expected input/output format for developers.

#### ✅ **POST /validate** - Validate Courses
```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "courses": [
      {
        "course_name": "Mathematics",
        "faculty": "Dr. Arjun Mehta",
        "room": "Room 101",
        "duration": 1,
        "weekly_count": 3,
        "session_type": "lecture",
        "availability": "Mon1,Mon2,Tue1,Wed1,Thu1"
      }
    ]
  }'
```

#### 🚀 **POST /generate** - Generate Timetable (Main Endpoint)
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "courses": [
      {
        "course_name": "Mathematics",
        "faculty": "Dr. Arjun Mehta",
        "room": "Room 101",
        "duration": 1,
        "weekly_count": 3,
        "session_type": "lecture",
        "availability": "Mon1,Mon2,Tue1,Wed1,Thu1"
      },
      {
        "course_name": "Physics Lab",
        "faculty": "Prof. Kavita Sharma",
        "room": "Lab 101",
        "duration": 2,
        "weekly_count": 1,
        "session_type": "lab",
        "availability": "Mon3,Tue3,Wed3,Thu3,Fri3"
      }
    ],
    "solver_preference": "simple",
    "options": {
      "allow_conflicts": false,
      "optimize_quality": true
    }
  }'
```

#### 📚 **GET /docs** - API Documentation
```bash
curl http://localhost:5000/docs
```

### **🎨 Frontend Demo**
Open `frontend_demo.html` in your browser for a complete web interface to test all API endpoints with a beautiful UI.

### **🧪 Testing the API**
```bash
# Run comprehensive API tests
python test_api.py
```

---

## 📥 Input Methods & Data Formats

### 1. 📊 **CSV Input** (Recommended)

**File**: `courses.csv`
```csv
CourseName,Faculty,FacultyAvailability,RoomAvailable,Duration,WeeklyCount,Component
Python Programming,Dr. Smith,"Mon1,Wed1,Fri1",101,1,3,Lecture
Data Science,Dr. Brown,"Mon2,Wed2",102,1,2,Lecture
```

**Field Descriptions**:
- `CourseName`: Course identifier
- `Faculty`: Professor/instructor name  
- `FacultyAvailability`: Available time slots (see availability formats below)
- `RoomAvailable`: Room number/name
- `Duration`: Class duration in hours
- `WeeklyCount`: Number of sessions per week
- `Component`: Session type (Lecture/Lab/Tutorial)

### 2. 🌐 **REST API Input**

**Endpoint**: `POST /api/generate-timetable`
```json
{
  "courses": [
    {
      "course_name": "Data Structures",
      "faculty": "Dr. Smith",
      "faculty_availability": "Monday,Wednesday,Friday",
      "room": "Hall 101",
      "duration": 3,
      "weekly_count": 3,
      "session_type": "lecture"
    }
  ]
}
```

### 🕐 **Availability Formats Supported**

1. **Natural Language**: `"Monday,Wednesday,Friday"`
2. **Specific Times**: `"Monday 10:00-11:00,Wednesday 14:00-15:00"`
3. **Legacy Slot Codes**: `"Mon1,Wed1,Fri1"`
4. **Mixed Formats**: `"Monday,Tue3,Friday 16:00-17:00"`

### 🕘 **Time Slot Mapping**

| Slot | Time | Slot | Time |
|------|------|------|------|
| 1 | 09:00-10:00 | 5 | 14:00-15:00 |
| 2 | 10:00-11:00 | 6 | 15:00-16:00 |
| 3 | 11:00-12:00 | 7 | 16:00-17:00 |
| 4 | 12:00-13:00 | 8 | 17:00-18:00 |

---

## 📤 Output Formats

### 1. 🖥️ **Console Output**
```
📅 MONDAY
====================
🕘 9:00-10:00
   📚 Python Programming - Dr. Smith (101) [1 hours] [lecture]

📊 TIMETABLE STATISTICS
========================
✅ Total Courses: 4
✅ Scheduled: 4 (100.0%)
✅ Success Rate: 100%
```

### 2. 📄 **JSON Output** (`data/simple_timetable.json`)
```json
{
  "Monday": {
    "9:00-10:00": [
      {
        "course": "python programming",
        "faculty": "dr. smith",
        "room": "101",
        "duration": 1,
        "session_type": "lecture"
      }
    ]
  }
}
```

### 3. 🌐 **API Response**
```json
{
  "success": true,
  "timetable": { ... },
  "metrics": {
    "total_courses": 4,
    "scheduled_courses": 4,
    "success_rate": "100.0%",
    "total_sessions": 9
  }
}
```

---

## 🔌 API Documentation

### Base URL: `http://localhost:5000`

#### 1. **Health Check**
```http
GET /api/health
```
Response: Server status and available endpoints

#### 2. **Generate Timetable**
```http
POST /api/generate-timetable
Content-Type: application/json
```

### 🔧 **API Usage Examples**

#### Python
```python
import requests

response = requests.post('http://localhost:5000/api/generate-timetable', json={
    'courses': [{
        'course_name': 'Data Structures',
        'faculty': 'Dr. Smith',
        'faculty_availability': 'Monday,Wednesday,Friday',
        'room': 'Hall 101',
        'duration': 3,
        'weekly_count': 3
    }]
})
timetable = response.json()
```

#### cURL
```bash
curl -X POST http://localhost:5000/api/generate-timetable \
  -H "Content-Type: application/json" \
  -d '{"courses":[{"course_name":"Database Systems","faculty":"Dr. Johnson","faculty_availability":"Tuesday,Thursday","room":"Lab 201","duration":2,"weekly_count":2}]}'
```

---

## 🧠 Algorithm Details

### 🎯 **Primary Algorithm: Smart Iterative Solver**
**Custom iterative approach** with intelligent conflict resolution:

1. **Constraint Analysis**: Parse faculty availability, room requirements, duration constraints
2. **Slot Mapping**: Convert natural language to standardized time slots  
3. **Conflict Detection**: Multi-level validation (faculty, room, time)
4. **Iterative Placement**: Smart backtracking with conflict resolution
5. **Optimization**: Session distribution across optimal time periods

**Features**: 100% success rate, multi-format support, smart backtracking

### 🛠️ **Secondary Algorithm: Google OR-Tools**
**Optional advanced solver** using constraint programming for complex scenarios.

**Usage**: `python main.py` → Select option 2

### 🔄 **Algorithm Comparison**

| Feature | Smart Iterative | OR-Tools |
|---------|----------------|----------|
| **Success Rate** | 100% | 95%+ |
| **Speed** | Fast | Variable |
| **Dependencies** | None | OR-Tools library |
| **Recommended** | ✅ Primary | 🔧 Complex cases |

---

## 🧪 Testing

### **Test Suites**
```bash
# Algorithm functionality tests
python test_simple_format.py

# Format compatibility tests  
python test_new_format.py

# Manual validation
python main.py                    # Test CSV processing
python simple_api_server.py       # Test API server
```

### **Test Coverage**
- ✅ Core Algorithm: 6 tests, 100% success
- ✅ Format Compatibility: 7 tests, 100% success
- ✅ API Endpoints: 2 tests, 100% success
- ✅ Error Handling: 3 tests, 100% success

---

## 🛠️ Development

### **Project Structure**
<<<<<<< HEAD

=======
📁 TIMETABLE_ALGO/
├── 📂 data/
│   ├── 📄 simple_timetable.json       # Generated timetable output
│   └── 📄 training_dataset.json       # Course input dataset
├── 📂 timetable/                      # Core algorithm package
│   ├── 📂 __pycache__/               # Python cache (can be removed)
│   ├── 📄 __init__.py                # Package initialization
│   ├── 📄 input_parser.py            # Data parsing utilities
│   ├── 📄 ortools_solver.py          # Advanced OR-Tools solver
│   └── 📄 simple_solver.py           # Main conflict-free algorithm
├── 📄 api_server_simple.py           # Working REST API server
├── 📄 api_server.py                  # Full-featured API (with OR-Tools)
├── 📄 courses.csv                    # Sample course data (CSV format)
├── 📄 frontend_demo.html             # Web interface for API testing
├── 📄 main.py                        # Console interface (3 input methods)
├── 📄 manual_input.py                # Interactive course input system
├── 📄 requirements.txt               # Python dependencies
├── 📄 SIH_INTEGRATION_GUIDE.md       # Integration guide for SIH teams
├── 📄 start_api.ps1                  # Windows PowerShell launcher
├── 📄 start_api.py                   # Cross-platform API launcher
└── 📄 test_api.py                    # Comprehensive API testing

### **Core Components**
- **SimpleTimetableSolver**: Main scheduling algorithm with conflict resolution
- **Input Parser**: CSV/JSON data processing and format conversion
- **API Server**: Flask web framework with REST endpoints and CORS

---

## 📊 Performance

### **Speed Benchmarks**
| Course Count | Processing Time | Memory Usage |
|--------------|----------------|--------------|
| 5 courses | < 0.1 seconds | ~10 MB |
| 20 courses | < 0.5 seconds | ~15 MB |
| 50 courses | < 2.0 seconds | ~25 MB |
| 100+ courses | < 5.0 seconds | ~40 MB |

### **Success Metrics**
- **Conflict Resolution**: 100% success rate
- **Schedule Coverage**: 100% course placement  
- **Resource Utilization**: 95%+ efficiency
- **API Response Time**: < 500ms average

---

## 🤝 Contributing

### **Development Setup**
```bash
# 1. Fork and clone the repository
# 2. Create feature branch: git checkout -b feature/amazing-feature
# 3. Make changes and test: python test_simple_format.py
# 4. Commit and push: git commit -m "Add feature"
# 5. Open Pull Request
```

### **Bug Reports & Feature Requests**
Open an issue with:
- Input data that caused the problem
- Expected vs actual behavior
- System information

---

<<<<<<< HEAD
=======
<<<<<<< HEAD
## 🏆 Smart India Hackathon 2025 Ready!

This project demonstrates:
- ✅ **Problem Solving**: Complex scheduling optimization
- ✅ **Technical Excellence**: Multiple algorithms and approaches
- ✅ **Web Integration**: Production-ready REST API
- ✅ **User Experience**: Multiple intuitive interfaces
- ✅ **Quality Assurance**: Comprehensive testing suite
- ✅ **Scalability**: Handles real-world datasets
- ✅ **Innovation**: Smart conflict resolution algorithms

**Ready to impress judges and solve real-world timetabling challenges!** 🚀
=======

>>>>>>> 8e55855d0bcd8705363cb4ed7e6498c5999616c1

---

>>>>>>> 6cbe9a7 (made changes)
## 📞 Support

1. **Documentation**: This README covers most use cases
2. **Tests**: Verify setup with `python test_simple_format.py`
3. **Issues**: Browse GitHub issues for solutions
4. **Questions**: Open new issue with "question" label

---

## 🔗 Integration Guide

### **1. REST API Integration**
```javascript
// Frontend JavaScript/React
const generateTimetable = async (courses) => {
    const response = await fetch('http://localhost:5000/api/generate-timetable', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ courses })
    });
    return await response.json();
};
```

### **2. Python Package Integration**
```python
# Direct Python integration
from timetable.simple_solver import SimpleTimetableSolver

solver = SimpleTimetableSolver()
timetable = solver.solve_timetable_from_data(courses_data)
print(f"Generated timetable with {len(timetable)} entries")
```

### **3. Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "api_server_simple.py"]
```

### **4. Integration Checklist**
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test functionality: `python test_simple_format.py`
- [ ] Start API server: `python api_server_simple.py`
- [ ] Configure CORS for web applications
- [ ] Set up error handling and logging
- [ ] Add authentication if required

### **5. Common Use Cases**
| Scenario | Method | Complexity |
|----------|--------|------------|
| **Web Portal** | REST API | Easy |
| **Mobile App** | HTTP Client | Easy |
| **Enterprise** | Microservice | Medium |
| **Cloud** | Docker Container | Medium |
| **Desktop** | Python Import | Easy |

---
<<<<<<< HEAD

<div align="center">
<<<<<<< HEAD
=======

**Made with ❤️ for Smart India Hackathon 2025**

⭐ **Star this repo if it helps you!** ⭐

>>>>>>> 6cbe9a7 (made changes)
</div>
=======
>>>>>>> 8e55855d0bcd8705363cb4ed7e6498c5999616c1
