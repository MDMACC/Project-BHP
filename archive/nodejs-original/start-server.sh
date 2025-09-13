#!/bin/bash

# Bluez PowerHouse Management Software - Server Startup Script
# This script starts the backend server with all necessary dependencies

echo "🚀 Starting Bluez PowerHouse Management Software..."
echo "=================================================="

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

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  Please edit .env file with your database and JWT settings before continuing."
        echo "   Press Enter to continue after editing .env file..."
        read
    else
        echo "❌ .env.example file not found. Please create a .env file manually."
        exit 1
    fi
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing backend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Backend dependencies installed"
fi

# Check if MongoDB is running (optional check)
echo "🔍 Checking MongoDB connection..."
node -e "
const mongoose = require('mongoose');
require('dotenv').config();
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/bluez-powerhouse', {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => {
    console.log('✅ MongoDB connection successful');
    process.exit(0);
}).catch((err) => {
    console.log('⚠️  MongoDB connection failed:', err.message);
    console.log('   Make sure MongoDB is running or update MONGODB_URI in .env file');
    process.exit(1);
});
"

if [ $? -ne 0 ]; then
    echo "⚠️  MongoDB connection failed. The server will still start but database operations may fail."
    echo "   Press Enter to continue anyway, or Ctrl+C to exit and fix MongoDB..."
    read
fi

# Start the server
echo "🚀 Starting Bluez PowerHouse backend server..."
echo "   Server will be available at: http://localhost:${PORT:-5000}"
echo "   API endpoints: http://localhost:${PORT:-5000}/api"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="

# Start the server with nodemon for development or node for production
if [ "$NODE_ENV" = "production" ]; then
    node server.js
else
    # Install nodemon if not present
    if ! command -v nodemon &> /dev/null; then
        echo "📦 Installing nodemon for development..."
        npm install -g nodemon
    fi
    nodemon server.js
fi
