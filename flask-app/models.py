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
    image_url = db.Column(db.String(500))  # URL or path to part image
    image_filename = db.Column(db.String(255))  # Original filename
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Part {self.name}>'

class StockHistory(db.Model):
    """Stock history model for tracking inventory changes"""
    __tablename__ = 'stock_history'
    
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    adjustment_type = db.Column(db.String(20), nullable=False)  # 'add', 'remove', 'set'
    quantity_before = db.Column(db.Integer, nullable=False)
    quantity_after = db.Column(db.Integer, nullable=False)
    adjustment_amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(50))  # 'sale', 'restock', 'damaged', etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    part = db.relationship('Part', backref='stock_history')
    user = db.relationship('User', backref='stock_adjustments')
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'part_id': self.part_id,
            'part_name': self.part.name if self.part else None,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'adjustment_type': self.adjustment_type,
            'quantity_before': self.quantity_before,
            'quantity_after': self.quantity_after,
            'adjustment_amount': self.adjustment_amount,
            'reason': self.reason,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<StockHistory {self.part.name if self.part else "Unknown"}: {self.adjustment_amount}>'

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
    photo_url = db.Column(db.String(500))  # URL to package photo
    photo_filename = db.Column(db.String(255))  # Local filename if stored locally
    webhook_data = db.Column(db.Text)  # Raw webhook JSON data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    shipping_order = db.relationship('ShippingOrder', backref='tracking_events')
    
    def set_webhook_data(self, data_dict):
        """Set webhook data as JSON"""
        self.webhook_data = json.dumps(data_dict)
    
    def get_webhook_data(self):
        """Get webhook data as dict"""
        if self.webhook_data:
            return json.loads(self.webhook_data)
        return {}
    
    def __repr__(self):
        return f'<TrackingEvent {self.status} at {self.location}>'

class WebhookLog(db.Model):
    """Log of webhook requests for debugging and security"""
    __tablename__ = 'webhook_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    headers = db.Column(db.Text)  # JSON of headers
    payload = db.Column(db.Text)  # Raw payload
    signature = db.Column(db.String(255))  # Webhook signature if provided
    processed = db.Column(db.Boolean, default=False)
    processing_error = db.Column(db.Text)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_headers(self, headers_dict):
        """Set headers as JSON"""
        self.headers = json.dumps(dict(headers_dict))
    
    def get_headers(self):
        """Get headers as dict"""
        if self.headers:
            return json.loads(self.headers)
        return {}
    
    def __repr__(self):
        return f'<WebhookLog {self.provider} {self.endpoint}>'

class ChatMessage(db.Model):
    """Chat message model for customer support"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)  # Unique session identifier
    sender_type = db.Column(db.String(20), nullable=False)  # 'customer' or 'admin'
    sender_name = db.Column(db.String(200))  # Name of sender
    sender_id = db.Column(db.Integer)  # User ID if admin, null for customers
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))  # Customer IP for session tracking
    user_agent = db.Column(db.String(500))  # Browser info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert message to dictionary for JSON response"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender_type': self.sender_type,
            'sender_name': self.sender_name,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.sender_type}: {self.message[:50]}...>'

class ChatSession(db.Model):
    """Chat session model for tracking conversations"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')  # active, closed, archived
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    assigned_admin = db.relationship('User', backref='chat_sessions')
    
    def to_dict(self):
        """Convert session to dictionary for JSON response"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'status': self.status,
            'assigned_admin_id': self.assigned_admin_id,
            'assigned_admin_name': self.assigned_admin.username if self.assigned_admin else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'
