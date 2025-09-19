"""
Simple models for the AutoShop Management System
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='employee', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, username, email, password, role='employee'):
        self.username = username
        self.email = email.lower().strip()
        self.role = role
        self.set_password(password)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Part(db.Model):
    """Part model for inventory management"""
    __tablename__ = 'parts'
    
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, default=0.0)
    cost = db.Column(db.Float, default=0.0)
    quantity_in_stock = db.Column(db.Integer, default=0)
    minimum_stock_level = db.Column(db.Integer, default=0)
    location = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Part {self.name}>'

class Contact(db.Model):
    """Contact model for customers and suppliers"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    type = db.Column(db.String(20), nullable=False)  # supplier, customer, vendor
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    street = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name}>'

class Order(db.Model):
    """Order model for parts ordering"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    status = db.Column(db.String(20), default='pending')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.DateTime)
    total_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class Schedule(db.Model):
    """Schedule model for appointments"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    customer_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    customer_name = db.Column(db.String(200))  # Fallback if no customer_id
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    technician_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Schedule {self.title}>'

class Shop(db.Model):
    """Shop information model"""
    __tablename__ = 'shop_info'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    business_hours = db.Column(db.Text)
    services_offered = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Shop {self.name}>'

class ShippingAccount(db.Model):
    """Shipping account model for API integrations"""
    __tablename__ = 'shipping_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)  # fcpeuro, orielly, autozone, harborfreight, amazon
    account_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200))
    api_key = db.Column(db.Text)  # Encrypted API key
    api_secret = db.Column(db.Text)  # Encrypted API secret
    additional_config = db.Column(db.Text)  # JSON for additional config
    is_active = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_config(self, config_dict):
        """Set additional configuration as JSON"""
        self.additional_config = json.dumps(config_dict)
    
    def get_config(self):
        """Get additional configuration as dict"""
        if self.additional_config:
            return json.loads(self.additional_config)
        return {}
    
    def __repr__(self):
        return f'<ShippingAccount {self.provider}: {self.account_name}>'

class ShippingOrder(db.Model):
    """Shipping order model for tracking orders"""
    __tablename__ = 'shipping_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('shipping_accounts.id'), nullable=False)
    order_id = db.Column(db.String(100), nullable=False)  # External order ID
    order_number = db.Column(db.String(100))  # Our internal order number
    tracking_number = db.Column(db.String(100))
    carrier = db.Column(db.String(50))  # UPS, FedEx, USPS, etc.
    status = db.Column(db.String(50))  # ordered, shipped, in_transit, delivered, etc.
    order_date = db.Column(db.DateTime)
    ship_date = db.Column(db.DateTime)
    estimated_delivery = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    total_amount = db.Column(db.Float)
    items_count = db.Column(db.Integer, default=0)
    shipping_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    account = db.relationship('ShippingAccount', backref='orders')
    
    def __repr__(self):
        return f'<ShippingOrder {self.order_id}>'

class TrackingEvent(db.Model):
    """Tracking event model for shipping updates"""
    __tablename__ = 'tracking_events'
    
    id = db.Column(db.Integer, primary_key=True)
    shipping_order_id = db.Column(db.Integer, db.ForeignKey('shipping_orders.id'), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))  # City, State or facility name
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    carrier_event_code = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    shipping_order = db.relationship('ShippingOrder', backref='tracking_events')
    
    def __repr__(self):
        return f'<TrackingEvent {self.status} at {self.location}>'
