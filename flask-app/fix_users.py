#!/usr/bin/env python3
"""
Fix user passwords to use bcrypt hashing
"""

from app import app
from database import db
from models.user import User

def main():
    """Fix demo users with correct bcrypt passwords"""
    with app.app_context():
        print("🔧 Fixing demo user passwords...")
        
        # Demo users with correct passwords
        users_data = [
            ('admin@autoshop.com', 'admin123'),
            ('manager@autoshop.com', 'manager123'), 
            ('employee@autoshop.com', 'employee123')
        ]
        
        for email, password in users_data:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"Updating password for {user.username}")
                user.set_password(password)  # This will use bcrypt
                db.session.add(user)
            else:
                print(f"User not found: {email}")
        
        try:
            db.session.commit()
            print("✅ User passwords updated successfully!")
            
            # Test password checking
            print("\n🧪 Testing password verification:")
            for email, password in users_data:
                user = User.query.filter_by(email=email).first()
                if user:
                    is_valid = user.check_password(password)
                    print(f"  {user.username}: {is_valid}")
                    
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating passwords: {e}")

if __name__ == "__main__":
    main()
