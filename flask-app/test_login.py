#!/usr/bin/env python3
"""
Test login functionality
"""

import requests
import sys

def test_login():
    """Test login with demo credentials"""
    base_url = "http://localhost:5000"
    
    # Test credentials
    credentials = [
        ("admin@autoshop.com", "admin123"),
        ("manager@autoshop.com", "manager123"), 
        ("employee@autoshop.com", "employee123")
    ]
    
    print("🧪 Testing login functionality...")
    
    for email, password in credentials:
        print(f"\nTesting login for: {email}")
        
        try:
            # Create a session
            session = requests.Session()
            
            # Get login page first to establish session
            login_page = session.get(f"{base_url}/auth/login")
            if login_page.status_code != 200:
                print(f"  ❌ Failed to get login page: {login_page.status_code}")
                continue
            
            # Attempt login
            login_data = {
                'email': email,
                'password': password
            }
            
            response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
            
            if response.status_code == 302:  # Redirect indicates success
                print(f"  ✅ Login successful - redirected to: {response.headers.get('Location', 'unknown')}")
                
                # Try to access dashboard
                dashboard_response = session.get(f"{base_url}/dashboard")
                if dashboard_response.status_code == 200:
                    print(f"  ✅ Dashboard access successful")
                else:
                    print(f"  ⚠️  Dashboard access failed: {dashboard_response.status_code}")
                    
            else:
                print(f"  ❌ Login failed - status: {response.status_code}")
                if 'Invalid email or password' in response.text:
                    print(f"  ❌ Invalid credentials error")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Cannot connect to Flask app at {base_url}")
            print("  Make sure the Flask app is running on port 5000")
            return False
        except Exception as e:
            print(f"  ❌ Error testing {email}: {str(e)}")
    
    return True

if __name__ == "__main__":
    success = test_login()
    if not success:
        sys.exit(1)
