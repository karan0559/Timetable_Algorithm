#!/usr/bin/env python3
"""
🚀 Timetable API Launcher
Quick startup script for the timetable generation API server
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask-cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print(f"📦 Installing missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print(f"✅ Successfully installed packages!")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install packages. Please run manually:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    return True

def start_api_server():
    """Start the Flask API server"""
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return False
    
    print("🚀 Starting Timetable API Server...")
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Check if api_server.py exists
    if not os.path.exists('api_server.py'):
        print("❌ api_server.py not found!")
        return False
    
    # Start the server
    try:
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['API_HOST'] = '0.0.0.0'
        env['API_PORT'] = '5000'
        
        print(f"""
🎓 Timetable Generator API Server
=================================
📡 Server: http://localhost:5000
🔧 Mode: Development
📚 Health Check: http://localhost:5000/health
🌐 Frontend Demo: file://{script_dir}/frontend_demo.html
💡 API Docs: http://localhost:5000/docs

⚡ Starting in 3 seconds... (Press Ctrl+C to stop)
        """)
        
        time.sleep(3)
        
        # Open frontend demo in browser
        demo_path = f"file://{script_dir}/frontend_demo.html"
        try:
            webbrowser.open(demo_path)
            print(f"🌐 Opening frontend demo in browser...")
        except:
            print(f"🌐 Demo available at: {demo_path}")
        
        # Start Flask server
        subprocess.run([sys.executable, 'api_server.py'], env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

if __name__ == '__main__':
    print("""
🎓 Timetable Generator - API Launcher
====================================
Smart India Hackathon (SIH) Ready
""")
    
    success = start_api_server()
    
    if not success:
        print("\n💡 Troubleshooting:")
        print("   1. Make sure Python 3.7+ is installed")
        print("   2. Install requirements: pip install -r requirements.txt")
        print("   3. Run manually: python api_server.py")
        sys.exit(1)
