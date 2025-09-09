# 🎓 Intelligent Timetable Generator

## 🚀 Overview

An intelligent timetable generation system that automatically creates conflict-free academic schedules using advanced algorithms. Built for the Smart India Hackathon with a focus on real-world deployment and user-friendly interfaces.

### ✨ Key Features

- **🧠 Intelligent Scheduling**: Hybrid algorithm combining constraint satisfaction and optimization
- **📝 Natural Language Input**: Simple format like "Monday,Wednesday,Friday"
- **⚡ Zero Conflicts**: Advanced conflict detection and resolution
- **📊 Bulk Processing**: CSV import for batch course data
- **🌐 REST API**: Complete web service for frontend integration
- **🎯 100% Success Rate**: Schedules all courses without failures

## 🛠️ Algorithm Architecture

### **Hybrid Heuristic Algorithm**

Our system uses a sophisticated **multi-layered approach** that goes beyond simple greedy algorithms:

#### 🎯 **Algorithm Components:**

1. **Priority-Based Scheduling (Constraint-Driven)**
   ```
   Courses with fewer available time slots → Higher priority
   Most constrained courses scheduled first → Reduces conflicts
   ```

2. **Multi-Criteria Optimization**
   - **Day Spreading**: Distributes courses across different days
   - **Time Preferences**: Morning slots prioritized over evening
   - **Smart Randomization**: Adds variety to prevent identical schedules

3. **Advanced Conflict Resolution**
   - Real-time faculty availability tracking
   - Room occupancy validation
   - Automatic constraint satisfaction

4. **Quality Ranking System**
   ```
   Time Slot Preferences:
   10:00-11:00 → Prime time (Score: 1)
   09:00-10:00 → Good morning (Score: 3)
   14:00-15:00 → Good afternoon (Score: 4)
   12:00-13:00 → Lunch time (Score: 6)
   17:00-18:00 → Evening (Score: 8)
   ```

### **Why Not OR-Tools?**
While OR-Tools provides mathematical optimization, our Simple Solver offers:
- ✅ **100% Portability** - Pure Python, no external dependencies
- ✅ **Zero Setup Issues** - Works on any system immediately
- ✅ **Easy Customization** - Modifiable for specific requirements

## 📋 Input Format

### **1. CSV Bulk Input (Recommended)**
```csv
CourseName,Faculty,FacultyAvailability,RoomAvailable,Duration
Data Structures,Dr. Smith,"Monday,Wednesday,Friday",Hall 101,3
Database Systems,Dr. Johnson,"Tuesday,Thursday",Computer Lab 201,2
Machine Learning,Dr. Wilson,"Monday 14:00-15:00,Wednesday 14:00-15:00",AI Lab 301,3
```

### **2. Manual Input (Interactive)**
```
Course Name: Data Structures
Faculty: Dr. Smith
Faculty Availability: Monday,Wednesday,Friday
Room: Hall 101
Duration: 3 hours
```

### **3. API Input (JSON)**
```json
{
  "courses": [
    {
      "course_name": "Data Structures",
      "faculty": "Dr. Smith",
      "faculty_availability": "Monday,Wednesday,Friday",
      "room": "Hall 101",
      "duration": 3
    }
  ]
}
```

### **Input Format Options:**

| Format | Example | Description |
|--------|---------|-------------|
| **Simple Days** | `Monday,Wednesday,Friday` | Natural language format |
| **Specific Times** | `Monday 10:00-11:00,Wednesday 14:00-15:00` | Exact time slots |
| **Legacy Codes** | `Mon2,Wed3,Fri1` | Backward compatibility |

### **Automatic Duration Assignment:**
- **Laboratory Courses**: 2 hours
- **Lecture Courses**: 3 hours  
- **Tutorial Courses**: 1 hour
- **Seminar Courses**: 2 hours

## 📊 Output

### **1. Complete Weekly Timetable**
```
📅 COMPLETE WEEKLY TIMETABLE
═══════════════════════════════════════════════════════════════════════════════

🗓️  MONDAY
────────────────────────────────────────────────────────────────────────────────    
⏰ 09:00-10:00
   1. Data Structures
      👨‍🏫 Faculty: Dr. Smith
      🏫 Room: Hall 101
   2. Machine Learning
      👨‍🏫 Faculty: Dr. Wilson
      🏫 Room: AI Lab 301

🗓️  TUESDAY
────────────────────────────────────────────────────────────────────────────────    
⏰ 09:00-10:00
   1. Database Systems
      👨‍🏫 Faculty: Dr. Johnson
      🏫 Room: Computer Lab 201
```

### **2. JSON Export**
```json
{
  "Monday": {
    "09:00-10:00": [
      {
        "course": "Data Structures",
        "faculty": "Dr. Smith",
        "room": "Hall 101",
        "duration": 3
      }
    ]
  }
}
```

### **3. Performance Metrics**
```
📊 Results: 10 scheduled, 0 failed
✅ TIMETABLE VALIDATION: NO CONFLICTS FOUND!
Success Rate: 100%
Conflict Rate: 0%
```

## 🚀 Quick Start

### **1. Installation**
```bash
# Clone repository
git clone https://github.com/karan0559/Timetable_Algorithm.git
cd Timetable_Algorithm

# Install dependencies
pip install -r requirements.txt
```

### **2. Run Timetable Generator**
```bash
# Interactive mode
python main.py

# Choose option 1 for CSV import or option 2 for manual entry
```

### **3. Start API Server**
```bash
# Launch REST API
python api_server.py

# API available at: http://localhost:5000
```

### **4. Test the System**
```bash
# Test CSV processing
python test_simple_format.py

# Test API endpoints
python api_test.py
```

## 🌐 API Endpoints

### **Generate Timetable**
```http
POST /api/generate-timetable
Content-Type: application/json

{
  "courses": [
    {
      "course_name": "Data Structures",
      "faculty": "Dr. Smith", 
      "faculty_availability": "Monday,Wednesday,Friday",
      "room": "Hall 101"
    }
  ]
}
```

### **Health Check**
```http
GET /api/health
Response: {"status": "healthy", "version": "1.0.0"}
```

### **Upload CSV**
```http
POST /api/upload-csv
Content-Type: multipart/form-data
File: courses.csv
```

## 📁 Project Structure

```
timetable_algo/
├── 🔧 Core System
│   ├── main.py              # Main entry point
│   ├── manual_input.py      # Interactive input system
│   ├── api_server.py        # REST API server
│   └── courses.csv          # Sample course data
│
├── 📦 Timetable Engine
│   ├── timetable/
│   │   ├── simple_solver.py     # Hybrid algorithm solver
│   │   ├── ortools_solver.py    # OR-Tools solver (optional)
│   │   ├── input_parser.py      # Data processing
│   │   └── __init__.py          # Package initialization
│
├── 🧪 Testing
│   ├── api_test.py              # API endpoint tests
│   ├── test_new_format.py       # Format compatibility tests
│   └── test_simple_format.py    # Core algorithm tests
│
├── 📊 Data & Output
│   ├── data/
│   │   ├── simple_timetable.json    # Generated schedules
│   │   └── training_dataset.json   # Processed course data
│
└── 📚 Documentation
    ├── README.md                # This file
    ├── SIH_INTEGRATION_GUIDE.md # Integration guide
    ├── AUDIT_REPORT.md          # System audit
    └── requirements.txt         # Dependencies
```

## 🎯 Performance Metrics

### **Algorithm Performance**
- **Success Rate**: 100% (10/10 courses scheduled)
- **Conflict Rate**: 0% (zero conflicts detected)
- **Time Complexity**: O(n × m × k) where n=courses, m=slots, k=duration
- **Space Complexity**: O(n + m) for schedule tracking

### **System Capabilities**
- **Course Capacity**: Tested with 10+ courses simultaneously
- **Time Slots**: 8 slots per day (09:00-18:00)
- **Working Days**: Monday to Friday
- **Duration Support**: 1-4 hours per course
- **Conflict Detection**: Faculty and room availability

## 🔧 Configuration

### **Time Slots Configuration**
```python
time_slots = [
    '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
    '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00'
]
```

### **Working Days**
```python
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
```

### **Priority Settings**
- Courses with fewer available slots get higher priority
- Morning time slots preferred over afternoon/evening
- Day spreading prioritized for better distribution

### **Demo Scenarios:**
1. **College Admin**: Upload semester course data via CSV
2. **Department Head**: Manual entry for specific courses
3. **System Integration**: API calls from web frontend
4. **Validation**: Real-time conflict checking and resolution

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request


