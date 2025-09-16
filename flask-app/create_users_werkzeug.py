#!/usr/bin/env python3
"""
Create users with Werkzeug password hashing
"""

import sqlite3
from werkzeug.security import generate_password_hash

def main():
    """Create demo users using Werkzeug password hashing"""
    print("🌱 Creating demo users with Werkzeug hashing...")
    
    # Connect to database
    conn = sqlite3.connect('instance/autoshop_management.db')
    cursor = conn.cursor()
    
    # Delete existing users first
    cursor.execute('DELETE FROM users')
    print("Cleared existing users")
    
    # Demo users
    users = [
        ('admin', 'admin@autoshop.com', 'admin123', 'admin'),
        ('manager', 'manager@autoshop.com', 'manager123', 'manager'),
        ('employee', 'employee@autoshop.com', 'employee123', 'employee')
    ]
    
    for username, email, password, role in users:
        # Hash password with Werkzeug
        password_hash = generate_password_hash(password)
        
        # Insert user
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES (?, ?, ?, ?, 1)
        ''', (username, email, password_hash, role))
        
        print(f"Created user: {username} with email: {email}")
    
    conn.commit()
    
    # Verify users were created
    print("\n🔍 Verifying created users:")
    cursor.execute('SELECT id, username, email, role FROM users')
    users = cursor.fetchall()
    
    for user in users:
        user_id, username, email, role = user
        print(f"  ID: {user_id}, Username: {username}, Email: {email}, Role: {role}")
    
    conn.close()
    print("✅ Demo users created successfully with Werkzeug hashing!")

if __name__ == "__main__":
    main()
