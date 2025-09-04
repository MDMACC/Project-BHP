#!/bin/bash

# Bluez PowerHouse Management Software - Frontend Startup Script
# This script starts the React frontend with all necessary dependencies

echo "🎨 Starting Bluez PowerHouse Frontend..."
echo "========================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Check if client directory exists
if [ ! -d "client" ]; then
    echo "❌ Client directory not found. Please run this script from the project root."
    exit 1
fi

# Navigate to client directory
cd client

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Frontend dependencies installed"
fi

# Check if backend is running (optional)
echo "🔍 Checking backend connection..."
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Backend server is running"
else
    echo "⚠️  Backend server is not running on port 5000"
    echo "   Make sure to start the backend server first with: ./start-server.sh"
    echo "   Press Enter to continue anyway..."
    read
fi

# Start the development server
echo "🚀 Starting Bluez PowerHouse frontend development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Make sure backend is running on: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

npm start
