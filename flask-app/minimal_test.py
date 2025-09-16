#!/usr/bin/env python3
"""
Minimal test of login functionality without complex relationships
"""

import sqlite3
import bcrypt
from flask import Flask, request, render_template, redirect, url_for, session, flash
import os

# Create minimal Flask app
app = Flask(__name__)
app.secret_key = 'test-secret-key'

def check_user_credentials(email, password):
    """Check user credentials directly with SQL"""
    try:
        conn = sqlite3.connect('instance/autoshop_management.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, password_hash, role, is_active FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            return None, "User not found"
        
        user_id, username, user_email, password_hash, role, is_active = user_data
        
        if not is_active:
            return None, "Account deactivated"
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return {
                'id': user_id,
                'username': username,
                'email': user_email,
                'role': role
            }, "Success"
        else:
            return None, "Invalid password"
            
    except Exception as e:
        return None, f"Database error: {str(e)}"

@app.route('/test-login', methods=['GET', 'POST'])
def test_login():
    """Test login page"""
    if request.method == 'GET':
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>Test Login</title></head>
        <body>
            <h1>Test Login</h1>
            <form method="POST">
                <p>
                    <label>Email:</label><br>
                    <input type="email" name="email" value="admin@autoshop.com" required>
                </p>
                <p>
                    <label>Password:</label><br>
                    <input type="password" name="password" value="admin123" required>
                </p>
                <p>
                    <button type="submit">Login</button>
                </p>
            </form>
            <p>Test credentials:</p>
            <ul>
                <li>admin@autoshop.com / admin123</li>
                <li>manager@autoshop.com / manager123</li>
                <li>employee@autoshop.com / employee123</li>
            </ul>
        </body>
        </html>
        '''
    
    # Handle login
    email = request.form.get('email', '').lower().strip()
    password = request.form.get('password', '')
    
    print(f"Login attempt: {email}")
    
    if not email or not password:
        return "Missing email or password", 400
    
    user, message = check_user_credentials(email, password)
    
    if user:
        session['user'] = user
        return f"<h1>Login Successful!</h1><p>Welcome {user['username']} ({user['role']})</p><a href='/test-dashboard'>Go to Dashboard</a>"
    else:
        return f"<h1>Login Failed</h1><p>{message}</p><a href='/test-login'>Try Again</a>", 401

@app.route('/test-dashboard')
def test_dashboard():
    """Test dashboard"""
    if 'user' not in session:
        return redirect(url_for('test_login'))
    
    user = session['user']
    return f'''
    <h1>Dashboard</h1>
    <p>Welcome {user['username']}!</p>
    <p>Role: {user['role']}</p>
    <p>Email: {user['email']}</p>
    <a href='/test-logout'>Logout</a>
    '''

@app.route('/test-logout')
def test_logout():
    """Test logout"""
    session.clear()
    return '<h1>Logged Out</h1><a href="/test-login">Login Again</a>'

if __name__ == '__main__':
    print("🧪 Starting minimal login test server on http://localhost:5001/test-login")
    app.run(host='0.0.0.0', port=5001, debug=True)
