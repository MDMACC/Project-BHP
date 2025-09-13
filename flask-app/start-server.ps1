#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Startup script for the Flask AutoShop Management server
.DESCRIPTION
    This script sets up the Python environment and starts the Flask development server
#>

Write-Host "🚗 Starting AutoShop Management Flask Server..." -ForegroundColor Green

# Check if virtual environment exists
$venvPath = "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "⚠️  Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv $venvPath
    Write-Host "✅ Virtual environment created." -ForegroundColor Green
}

# Activate virtual environment
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    $pipCmd = Join-Path $venvPath "Scripts\pip.exe"
    $pythonCmd = Join-Path $venvPath "Scripts\python.exe"
} else {
    $activateScript = Join-Path $venvPath "bin/activate"
    $pipCmd = Join-Path $venvPath "bin/pip"
    $pythonCmd = Join-Path $venvPath "bin/python"
}

# Install requirements
try {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Blue
    & $pipCmd install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully." -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies. Please check requirements.txt" -ForegroundColor Red
    exit 1
}

# Set environment variables
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

Write-Host "🌐 Starting Flask development server..." -ForegroundColor Blue
Write-Host "📍 Server will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📍 API Health Check: http://localhost:5000/api/health" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow

# Start the Flask application
try {
    & $pythonCmd app.py
} catch {
    Write-Host "❌ Server failed to start: $_" -ForegroundColor Red
    exit 1
} 