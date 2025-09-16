#!/usr/bin/env python3
"""
Debug user authentication directly
"""

import sqlite3
import bcrypt
from models.user import User
from database import db
from flask import Flask
import logging

# Simple Flask app for testing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/autoshop_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

db.init_app(app)

def test_direct_sql():
    """Test user authentication with direct SQL"""
    print("🔍 Testing with direct SQL...")
    
    conn = sqlite3.connect('instance/autoshop_management.db')
    cursor = conn.cursor()
    
    # Check users in database
    cursor.execute('SELECT id, username, email, password_hash FROM users')
    users = cursor.fetchall()
    
    print(f"Found {len(users)} users in database:")
    for user in users:
        user_id, username, email, password_hash = user
        print(f"  ID: {user_id}, Username: {username}, Email: {email}")
        
        # Test password for admin
        if email == 'admin@autoshop.com':
            test_password = 'admin123'
            is_valid = bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8'))
            print(f"  Password check for {username}: {is_valid}")
    
    conn.close()

def test_with_sqlalchemy():
    """Test user authentication with SQLAlchemy"""
    print("\n🔍 Testing with SQLAlchemy...")
    
    with app.app_context():
        try:
            # Test basic query
            user_count = User.query.count()
            print(f"Total users found: {user_count}")
            
            # Test specific user lookup
            admin_user = User.query.filter_by(email='admin@autoshop.com').first()
            if admin_user:
                print(f"Found admin user: {admin_user.username}")
                
                # Test password check
                is_valid = admin_user.check_password('admin123')
                print(f"Password check for admin: {is_valid}")
            else:
                print("Admin user not found!")
                
        except Exception as e:
            print(f"SQLAlchemy error: {e}")
            logger.exception("Full error details:")

if __name__ == "__main__":
    test_direct_sql()
    test_with_sqlalchemy()
