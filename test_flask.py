#!/usr/bin/env python3
"""
Quick test script for the Flask app
"""
import sys
import os

# Add flask-app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'flask-app'))

try:
    # Change to flask-app directory and import
    os.chdir('flask-app')
    from app import app
    print("✅ Flask app imported successfully!")
    
    # Test the routes
    with app.test_client() as client:
        print("\n🧪 Testing routes:")
        
        # Test home route
        response = client.get('/')
        print(f"GET / -> Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Home route working!")
        else:
            print(f"❌ Home route failed: {response.get_data(as_text=True)}")
        
        # Test health route
        response = client.get('/api/health')
        print(f"GET /api/health -> Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health route working!")
            print(f"Response: {response.get_json()}")
        else:
            print(f"❌ Health route failed: {response.get_data(as_text=True)}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
