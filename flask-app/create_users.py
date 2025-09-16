#!/usr/bin/env python3
"""
Create users directly in database using raw SQL
"""

import sqlite3
from werkzeug.security import generate_password_hash

def main():
    """Create demo users using raw SQL"""
    print("🌱 Creating demo users...")
    
    # Connect to database
    conn = sqlite3.connect('instance/autoshop_management.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) NOT NULL UNIQUE,
        email VARCHAR(120) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'employee',
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Demo users
    users = [
        ('admin', 'admin@autoshop.com', 'admin123', 'admin'),
        ('manager', 'manager@autoshop.com', 'manager123', 'manager'),
        ('employee', 'employee@autoshop.com', 'employee123', 'employee')
    ]
    
    for username, email, password, role in users:
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            print(f"User already exists: {username}")
            continue
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert user
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES (?, ?, ?, ?, 1)
        ''', (username, email, password_hash, role))
        
        print(f"Created user: {username}")
    
    conn.commit()
    conn.close()
    print("✅ Demo users created successfully!")

if __name__ == "__main__":
    main()
