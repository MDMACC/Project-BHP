#!/usr/bin/env python3
"""
Seed the database with demo data
"""

from app import app
from database import db
from models.user import User
from models.contact import Contact
from models.part import Part
from models.order import Order
from models.schedule import Schedule
from models.shop import Shop
from datetime import datetime, date, timedelta
import random

def create_demo_users():
    """Create demo users"""
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

def create_demo_contacts():
    """Create demo contacts"""
    contacts = [
        {
            'name': 'NAPA Auto Parts',
            'company': 'NAPA Auto Parts',
            'type': 'supplier',
            'email': 'orders@napaonline.com',
            'phone': '555-0101',
            'street': '123 Parts Street',
            'city': 'Auto City',
            'state': 'CA',
            'zip_code': '90210',
            'payment_terms': 'net_30'
        },
        {
            'name': "O'Reilly Auto Parts",
            'company': "O'Reilly Auto Parts",
            'type': 'supplier',
            'email': 'orders@oreillyauto.com',
            'phone': '555-0102',
            'street': '456 Supply Ave',
            'city': 'Parts Town',
            'state': 'CA',
            'zip_code': '90211',
            'payment_terms': 'net_30'
        },
        {
            'name': 'John Smith',
            'company': '',
            'type': 'customer',
            'email': 'john.smith@email.com',
            'phone': '555-0201',
            'mobile': '555-0202',
            'street': '789 Customer Lane',
            'city': 'Client City',
            'state': 'CA',
            'zip_code': '90212'
        },
        {
            'name': 'Jane Doe',
            'company': 'Doe Enterprises',
            'type': 'customer',
            'email': 'jane@doeenterprises.com',
            'phone': '555-0301',
            'street': '321 Business Blvd',
            'city': 'Corporate City',
            'state': 'CA',
            'zip_code': '90213'
        }
    ]
    
    for contact_data in contacts:
        existing_contact = Contact.query.filter_by(email=contact_data['email']).first()
        if not existing_contact:
            contact = Contact(**contact_data)
            db.session.add(contact)
            print(f"Created contact: {contact_data['name']}")
        else:
            print(f"Contact already exists: {contact_data['name']}")

def create_demo_parts():
    """Create demo parts"""
    parts = [
        {
            'part_number': 'BRK-001',
            'name': 'Brake Pads - Front',
            'description': 'High-quality ceramic brake pads for front wheels',
            'category': 'Brakes',
            'price': 89.99,
            'cost': 45.00,
            'quantity_in_stock': 24,
            'minimum_stock_level': 10,
            'location': 'A1-B2',
            'supplier_part_number': 'BP-FRONT-001'
        },
        {
            'part_number': 'ENG-002',
            'name': 'Oil Filter',
            'description': 'Premium oil filter for most vehicles',
            'category': 'Engine',
            'price': 12.99,
            'cost': 6.50,
            'quantity_in_stock': 150,
            'minimum_stock_level': 50,
            'location': 'B2-C3',
            'supplier_part_number': 'OF-PREM-002'
        },
        {
            'part_number': 'SUS-003',
            'name': 'Shock Absorber',
            'description': 'Heavy-duty shock absorber',
            'category': 'Suspension',
            'price': 159.99,
            'cost': 80.00,
            'quantity_in_stock': 8,
            'minimum_stock_level': 5,
            'location': 'C3-D4',
            'supplier_part_number': 'SA-HD-003'
        },
        {
            'part_number': 'TIR-004',
            'name': 'All-Season Tire 225/60R16',
            'description': 'Premium all-season tire',
            'category': 'Tires',
            'price': 129.99,
            'cost': 75.00,
            'quantity_in_stock': 0,  # Out of stock
            'minimum_stock_level': 8,
            'location': 'D4-E5',
            'supplier_part_number': 'AST-225-60-16'
        }
    ]
    
    for part_data in parts:
        existing_part = Part.query.filter_by(part_number=part_data['part_number']).first()
        if not existing_part:
            part = Part(**part_data)
            db.session.add(part)
            print(f"Created part: {part_data['name']}")
        else:
            print(f"Part already exists: {part_data['name']}")

def create_demo_orders():
    """Create demo orders"""
    # Get suppliers
    napa = Contact.query.filter_by(name='NAPA Auto Parts').first()
    oreilly = Contact.query.filter_by(name="O'Reilly Auto Parts").first()
    
    if not napa or not oreilly:
        print("Suppliers not found, skipping order creation")
        return
    
    orders = [
        {
            'order_number': 'BHP-2024-001',
            'supplier_id': napa.id,
            'status': 'pending',
            'order_date': datetime.now() - timedelta(days=2),
            'expected_delivery_date': datetime.now() + timedelta(hours=5),
            'total_amount': 892.30,
            'notes': 'Urgent order for brake parts'
        },
        {
            'order_number': 'BHP-2024-002',
            'supplier_id': oreilly.id,
            'status': 'shipped',
            'order_date': datetime.now() - timedelta(days=5),
            'expected_delivery_date': datetime.now() + timedelta(hours=18),
            'total_amount': 2156.80,
            'notes': 'Regular parts order'
        },
        {
            'order_number': 'BHP-2024-003',
            'supplier_id': napa.id,
            'status': 'delivered',
            'order_date': datetime.now() - timedelta(days=10),
            'expected_delivery_date': datetime.now() - timedelta(days=3),
            'actual_delivery_date': datetime.now() - timedelta(days=3),
            'total_amount': 445.67,
            'notes': 'Oil filters and air filters'
        }
    ]
    
    for order_data in orders:
        existing_order = Order.query.filter_by(order_number=order_data['order_number']).first()
        if not existing_order:
            order = Order(**order_data)
            db.session.add(order)
            print(f"Created order: {order_data['order_number']}")
        else:
            print(f"Order already exists: {order_data['order_number']}")

def create_demo_schedule():
    """Create demo schedule entries"""
    # Get customers
    john = Contact.query.filter_by(name='John Smith').first()
    jane = Contact.query.filter_by(name='Jane Doe').first()
    
    if not john or not jane:
        print("Customers not found, skipping schedule creation")
        return
    
    today = date.today()
    schedules = [
        {
            'title': 'Brake Inspection',
            'description': 'Routine brake system inspection',
            'customer_id': john.id,
            'start_date': today,
            'end_date': today,
            'start_time': datetime.combine(today, datetime.min.time().replace(hour=9, minute=0)),
            'end_time': datetime.combine(today, datetime.min.time().replace(hour=10, minute=30)),
            'status': 'confirmed',
            'technician_name': 'Mike Johnson'
        },
        {
            'title': 'Oil Change',
            'description': 'Regular oil change service',
            'customer_id': jane.id,
            'start_date': today,
            'end_date': today,
            'start_time': datetime.combine(today, datetime.min.time().replace(hour=14, minute=0)),
            'end_time': datetime.combine(today, datetime.min.time().replace(hour=15, minute=0)),
            'status': 'confirmed',
            'technician_name': 'Sarah Wilson'
        },
        {
            'title': 'Tire Replacement',
            'description': 'Replace all four tires',
            'customer_id': john.id,
            'start_date': today + timedelta(days=1),
            'end_date': today + timedelta(days=1),
            'start_time': datetime.combine(today + timedelta(days=1), datetime.min.time().replace(hour=10, minute=0)),
            'end_time': datetime.combine(today + timedelta(days=1), datetime.min.time().replace(hour=12, minute=0)),
            'status': 'pending',
            'technician_name': 'Mike Johnson'
        }
    ]
    
    for schedule_data in schedules:
        # Check if similar appointment exists
        existing = Schedule.query.filter_by(
            title=schedule_data['title'],
            customer_id=schedule_data['customer_id'],
            start_date=schedule_data['start_date']
        ).first()
        
        if not existing:
            schedule = Schedule(**schedule_data)
            db.session.add(schedule)
            print(f"Created schedule: {schedule_data['title']}")
        else:
            print(f"Schedule already exists: {schedule_data['title']}")

def create_shop_info():
    """Create shop information"""
    existing_shop = Shop.query.first()
    if not existing_shop:
        shop = Shop(
            name='Bluez PowerHouse Auto Repair',
            address='123 Main Street',
            city='Auto City',
            state='CA',
            zip_code='90210',
            phone='555-AUTO-FIX',
            email='info@bluezpowerhouse.com',
            website='www.bluezpowerhouse.com',
            business_hours='Monday-Friday: 8AM-6PM, Saturday: 9AM-4PM',
            services_offered='Oil Changes, Brake Repair, Engine Diagnostics, Tire Services, Suspension Repair'
        )
        db.session.add(shop)
        print("Created shop information")
    else:
        print("Shop information already exists")

def main():
    """Main seeding function"""
    with app.app_context():
        print("🌱 Seeding database with demo data...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Create demo data
        create_demo_users()
        create_demo_contacts()
        create_demo_parts()
        create_demo_orders()
        create_demo_schedule()
        create_shop_info()
        
        # Commit all changes
        try:
            db.session.commit()
            print("✅ Database seeded successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error seeding database: {e}")

if __name__ == "__main__":
    main()
