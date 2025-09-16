#!/usr/bin/env python3
"""
Simple seed script to create demo users
"""

from app import app
from database import db
from models.user import User
from werkzeug.security import generate_password_hash

def main():
    """Create demo users"""
    with app.app_context():
        print("🌱 Creating demo users...")
        
        # Create tables
        db.create_all()
        
        # Demo users
        users = [
            {
                'username': 'admin',
                'email': 'admin@autoshop.com',
                'password': 'admin123',
                'role': 'admin'
            },
            {
                'username': 'manager',
                'email': 'manager@autoshop.com',
                'password': 'manager123',
                'role': 'manager'
            },
            {
                'username': 'employee',
                'email': 'employee@autoshop.com',
                'password': 'employee123',
                'role': 'employee'
            }
        ]
        
        for user_data in users:
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role']
                )
                db.session.add(user)
                print(f"Created user: {user_data['username']}")
            else:
                print(f"User already exists: {user_data['username']}")
        
        try:
            db.session.commit()
            print("✅ Demo users created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating users: {e}")

if __name__ == "__main__":
    main()
