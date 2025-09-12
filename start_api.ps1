# 🎓 Timetable Generator API - Windows Launcher
# PowerShell script for easy API server startup

Write-Host ""
Write-Host "🎓 Timetable Generator - API Server" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Smart India Hackathon (SIH) Ready" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.7+ first." -ForegroundColor Red
    Write-Host "   Download from: https://python.org/downloads" -ForegroundColor Yellow
    pause
    exit 1
}

# Check current directory
$currentDir = Get-Location
Write-Host "📁 Working directory: $currentDir" -ForegroundColor Blue

# Check if we're in the right directory
if (-not (Test-Path "api_server.py")) {
    Write-Host "❌ api_server.py not found!" -ForegroundColor Red
    Write-Host "   Please run this script from the timetable_algo directory" -ForegroundColor Yellow
    pause
    exit 1
}

# Install dependencies if needed
Write-Host "📦 Checking dependencies..." -ForegroundColor Blue
try {
    if (Test-Path "requirements.txt") {
        Write-Host "   Installing requirements from requirements.txt..." -ForegroundColor Yellow
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install requirements"
        }
    } else {
        Write-Host "   Installing Flask and CORS..." -ForegroundColor Yellow
        python -m pip install flask flask-cors
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install Flask"
        }
    }
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host "   Please run manually: pip install flask flask-cors" -ForegroundColor Yellow
    pause
    exit 1
}

# Start the API server
Write-Host ""
Write-Host "🚀 Starting Timetable API Server..." -ForegroundColor Green
Write-Host ""
Write-Host "📡 Server URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host "💗 Health Check: http://localhost:5000/health" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:5000/docs" -ForegroundColor Cyan
Write-Host "🌐 Frontend Demo: $currentDir\frontend_demo.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚡ Starting server... (Press Ctrl+C to stop)" -ForegroundColor Yellow
Write-Host ""

# Set environment variables for development
$env:FLASK_ENV = "development"
$env:API_HOST = "0.0.0.0"
$env:API_PORT = "5000"

# Open frontend demo in default browser
try {
    $demoPath = Join-Path $currentDir "frontend_demo.html"
    if (Test-Path $demoPath) {
        Write-Host "🌐 Opening frontend demo in browser..." -ForegroundColor Green
        Start-Process $demoPath
    }
} catch {
    Write-Host "🌐 Frontend demo available at: $demoPath" -ForegroundColor Yellow
}

# Start the Flask server
try {
    python api_server.py
} catch {
    Write-Host ""
    Write-Host "🛑 Server stopped" -ForegroundColor Yellow
} finally {
    Write-Host ""
    Write-Host "💡 Troubleshooting:" -ForegroundColor Cyan
    Write-Host "   1. Make sure Python 3.7+ is installed" -ForegroundColor White
    Write-Host "   2. Install requirements: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "   3. Run manually: python api_server.py" -ForegroundColor White
    Write-Host ""
    pause
}
