#!/usr/bin/env python3
"""
Fix user passwords directly using bcrypt
"""

import sqlite3
import bcrypt

def main():
    """Fix demo user passwords using direct SQL"""
    print("🔧 Fixing demo user passwords...")
    
    # Connect to database
    conn = sqlite3.connect('instance/autoshop_management.db')
    cursor = conn.cursor()
    
    # Demo users with correct passwords
    users_data = [
        ('admin@autoshop.com', 'admin123'),
        ('manager@autoshop.com', 'manager123'), 
        ('employee@autoshop.com', 'employee123')
    ]
    
    for email, password in users_data:
        # Hash password with bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # Update user password
        cursor.execute(
            'UPDATE users SET password_hash = ? WHERE email = ?',
            (password_hash, email)
        )
        
        # Check if update was successful
        if cursor.rowcount > 0:
            print(f"Updated password for {email}")
        else:
            print(f"User not found: {email}")
    
    conn.commit()
    
    # Test password verification
    print("\n🧪 Testing password verification:")
    for email, password in users_data:
        cursor.execute('SELECT username, password_hash FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result:
            username, stored_hash = result
            is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f"  {username}: {is_valid}")
        else:
            print(f"  User not found: {email}")
    
    conn.close()
    print("✅ User passwords updated successfully!")

if __name__ == "__main__":
    main()
