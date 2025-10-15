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
    price = db.Column(db.Float, default=0.0)  # Selling price
    cost = db.Column(db.Float, default=0.0)   # Cost we paid for it
    quantity_in_stock = db.Column(db.Integer, default=0)
    minimum_stock_level = db.Column(db.Integer, default=0)
    location = db.Column(db.String(50))
    
    # Supplier information
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))  # Link to supplier contact
    supplier_part_number = db.Column(db.String(100))  # Supplier's part number
    supplier_url = db.Column(db.String(500))  # Link to supplier's product page
    last_order_date = db.Column(db.Date)  # When we last ordered this part
    last_order_cost = db.Column(db.Float)  # What we paid last time
    image_url = db.Column(db.String(500))  # URL or path to part image
    image_filename = db.Column(db.String(255))  # Original filename
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = db.relationship('Contact', backref='supplied_parts', foreign_keys=[supplier_id])
    
    def get_profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost and self.cost > 0:
            return round(((self.price - self.cost) / self.cost) * 100, 2)
        return 0
    
    def get_markup_percentage(self):
        """Calculate markup percentage"""
        if self.cost and self.cost > 0:
            return round(((self.price - self.cost) / self.price) * 100, 2)
        return 0
    
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
    
    # Vehicle Information (for customers)
    vehicle_year = db.Column(db.Integer)
    vehicle_make = db.Column(db.String(50))
    vehicle_model = db.Column(db.String(50))
    vehicle_color = db.Column(db.String(30))
    vehicle_vin = db.Column(db.String(17))
    vehicle_license_plate = db.Column(db.String(20))
    vehicle_mileage = db.Column(db.Integer)
    vehicle_photo_url = db.Column(db.String(500))  # URL to vehicle photo
    vehicle_photo_filename = db.Column(db.String(255))  # Original filename
    
    # Customer folder organization
    folder_notes = db.Column(db.Text)  # General notes about the customer
    preferred_contact_method = db.Column(db.String(20))  # 'phone', 'email', 'text'
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_vehicle_info(self):
        """Get formatted vehicle information"""
        if self.vehicle_year and self.vehicle_make and self.vehicle_model:
            vehicle_info = f"{self.vehicle_year} {self.vehicle_make} {self.vehicle_model}"
            if self.vehicle_color:
                vehicle_info += f" ({self.vehicle_color})"
            return vehicle_info
        return "No vehicle information"
    
    def __repr__(self):
        return f'<Contact {self.name}>'

class Vehicle(db.Model):
    """Vehicle model for customer vehicles (multiple vehicles per customer)"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    
    # Vehicle Information
    year = db.Column(db.Integer)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    color = db.Column(db.String(30))
    vin = db.Column(db.String(17))
    license_plate = db.Column(db.String(20))
    mileage = db.Column(db.Integer)
    
    # Photos and documentation
    photo_url = db.Column(db.String(500))  # URL to vehicle photo
    photo_filename = db.Column(db.String(255))  # Original filename
    
    # Vehicle details
    engine = db.Column(db.String(100))  # Engine type/size
    transmission = db.Column(db.String(50))  # Manual/Automatic
    fuel_type = db.Column(db.String(20))  # Gas/Diesel/Electric/Hybrid
    
    # Status and notes
    is_primary = db.Column(db.Boolean, default=False)  # Primary vehicle for customer
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)  # Special notes about this vehicle
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Contact', backref='vehicles')
    
    def get_display_name(self):
        """Get formatted vehicle display name"""
        parts = []
        if self.year:
            parts.append(str(self.year))
        if self.make:
            parts.append(self.make)
        if self.model:
            parts.append(self.model)
        
        if parts:
            vehicle_name = ' '.join(parts)
            if self.color:
                vehicle_name += f' ({self.color})'
            return vehicle_name
        return "Vehicle"
    
    def get_short_name(self):
        """Get short vehicle name for UI"""
        if self.make and self.model:
            return f"{self.make} {self.model}"
        elif self.make:
            return self.make
        return "Vehicle"
    
    def __repr__(self):
        return f'<Vehicle {self.get_display_name()}>'

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
    
    # Vehicle information for service requests
    vehicle_make = db.Column(db.String(50))
    vehicle_model = db.Column(db.String(50))
    vehicle_year = db.Column(db.Integer)
    service_description = db.Column(db.Text)  # What they want done
    
    # Session management
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
            'vehicle_make': self.vehicle_make,
            'vehicle_model': self.vehicle_model,
            'vehicle_year': self.vehicle_year,
            'service_description': self.service_description,
            'status': self.status,
            'assigned_admin_id': self.assigned_admin_id,
            'assigned_admin_name': self.assigned_admin.username if self.assigned_admin else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'

class ServiceRecord(db.Model):
    """Service record model for tracking all services performed"""
    __tablename__ = 'service_records'
    
    id = db.Column(db.Integer, primary_key=True)
    service_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    customer_name = db.Column(db.String(200))  # Fallback if no customer_id
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    
    # Vehicle Information
    vehicle_year = db.Column(db.Integer)
    vehicle_make = db.Column(db.String(50))
    vehicle_model = db.Column(db.String(50))
    vehicle_vin = db.Column(db.String(17))
    vehicle_mileage = db.Column(db.Integer)
    vehicle_license_plate = db.Column(db.String(20))
    
    # Service Details
    service_type = db.Column(db.String(50), nullable=False)  # 'service', 'modification', 'tune', 'repair'
    service_category = db.Column(db.String(50))  # 'maintenance', 'performance', 'cosmetic', 'repair'
    service_title = db.Column(db.String(200), nullable=False)
    service_description = db.Column(db.Text)
    
    # Technician and Timing
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    technician_name = db.Column(db.String(100))  # Fallback if no technician_id
    service_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    labor_hours = db.Column(db.Float, default=0.0)
    
    # Financial
    labor_cost = db.Column(db.Float, default=0.0)
    parts_cost = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    customer_paid = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # 'pending', 'partial', 'paid'
    payment_method = db.Column(db.String(20))  # 'cash', 'card', 'check', 'financing'
    
    # Status and Quality
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'in-progress', 'completed', 'cancelled'
    quality_rating = db.Column(db.Integer)  # 1-5 stars
    warranty_months = db.Column(db.Integer, default=6)
    warranty_miles = db.Column(db.Integer, default=12000)
    
    # Documentation
    before_photos = db.Column(db.Text)  # JSON array of photo filenames
    after_photos = db.Column(db.Text)  # JSON array of photo filenames
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)  # Private notes for staff
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Contact', backref='service_records')
    technician = db.relationship('User', foreign_keys=[technician_id], backref='services_performed')
    created_by_user = db.relationship('User', foreign_keys=[created_by], backref='service_records_created')
    
    def set_before_photos(self, photo_list):
        """Set before photos as JSON"""
        self.before_photos = json.dumps(photo_list) if photo_list else None
    
    def get_before_photos(self):
        """Get before photos as list"""
        if self.before_photos:
            return json.loads(self.before_photos)
        return []
    
    def set_after_photos(self, photo_list):
        """Set after photos as JSON"""
        self.after_photos = json.dumps(photo_list) if photo_list else None
    
    def get_after_photos(self):
        """Get after photos as list"""
        if self.after_photos:
            return json.loads(self.after_photos)
        return []
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'service_number': self.service_number,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'vehicle_info': f"{self.vehicle_year} {self.vehicle_make} {self.vehicle_model}" if self.vehicle_year else None,
            'service_type': self.service_type,
            'service_title': self.service_title,
            'service_description': self.service_description,
            'technician_name': self.technician_name,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'labor_hours': self.labor_hours,
            'total_cost': self.total_cost,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ServiceRecord {self.service_number}: {self.service_title}>'

class ServicePart(db.Model):
    """Parts used in service records"""
    __tablename__ = 'service_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    service_record_id = db.Column(db.Integer, db.ForeignKey('service_records.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'))
    part_name = db.Column(db.String(200))  # Fallback if no part_id
    part_number = db.Column(db.String(50))
    quantity_used = db.Column(db.Integer, default=1)
    unit_cost = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    supplier = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Relationships
    service_record = db.relationship('ServiceRecord', backref='parts_used')
    part = db.relationship('Part', backref='service_usage')
    
    def __repr__(self):
        return f'<ServicePart {self.part_name}: {self.quantity_used}x>'

class WorkOrder(db.Model):
    """Work order model for detailed workflow management"""
    __tablename__ = 'work_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_number = db.Column(db.String(50), unique=True, nullable=False)
    service_record_id = db.Column(db.Integer, db.ForeignKey('service_records.id'), nullable=False)
    
    # Assignment and Status
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    priority = db.Column(db.String(20), default='normal')  # 'low', 'normal', 'high', 'urgent'
    status = db.Column(db.String(20), default='assigned')  # 'assigned', 'in-progress', 'on-hold', 'completed', 'cancelled'
    
    # Timing
    scheduled_start = db.Column(db.DateTime)
    actual_start = db.Column(db.DateTime)
    estimated_completion = db.Column(db.DateTime)
    actual_completion = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float, default=0.0)
    actual_hours = db.Column(db.Float, default=0.0)
    
    # Work Details
    work_description = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    safety_notes = db.Column(db.Text)
    required_tools = db.Column(db.Text)  # JSON array of required tools
    
    # Quality Control
    quality_checklist_completed = db.Column(db.Boolean, default=False)
    quality_score = db.Column(db.Integer)  # 1-10 quality rating
    quality_notes = db.Column(db.Text)
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    inspection_date = db.Column(db.DateTime)
    
    # Documentation
    work_photos = db.Column(db.Text)  # JSON array of photo filenames
    technician_notes = db.Column(db.Text)
    supervisor_notes = db.Column(db.Text)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_record = db.relationship('ServiceRecord', backref='work_orders')
    assigned_technician = db.relationship('User', foreign_keys=[assigned_technician_id], backref='assigned_work_orders')
    inspector = db.relationship('User', foreign_keys=[inspector_id], backref='inspected_work_orders')
    created_by_user = db.relationship('User', foreign_keys=[created_by], backref='work_orders_created')
    
    def set_required_tools(self, tools_list):
        """Set required tools as JSON"""
        self.required_tools = json.dumps(tools_list) if tools_list else None
    
    def get_required_tools(self):
        """Get required tools as list"""
        if self.required_tools:
            return json.loads(self.required_tools)
        return []
    
    def set_work_photos(self, photo_list):
        """Set work photos as JSON"""
        self.work_photos = json.dumps(photo_list) if photo_list else None
    
    def get_work_photos(self):
        """Get work photos as list"""
        if self.work_photos:
            return json.loads(self.work_photos)
        return []
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'work_order_number': self.work_order_number,
            'service_record_id': self.service_record_id,
            'assigned_technician': self.assigned_technician.username if self.assigned_technician else None,
            'priority': self.priority,
            'status': self.status,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'actual_start': self.actual_start.isoformat() if self.actual_start else None,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'actual_completion': self.actual_completion.isoformat() if self.actual_completion else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'quality_checklist_completed': self.quality_checklist_completed,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<WorkOrder {self.work_order_number}>'

class TimeEntry(db.Model):
    """Time tracking model for technician work hours"""
    __tablename__ = 'time_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Time Tracking
    clock_in = db.Column(db.DateTime, nullable=False)
    clock_out = db.Column(db.DateTime)
    break_time_minutes = db.Column(db.Integer, default=0)
    total_minutes = db.Column(db.Integer)
    billable_minutes = db.Column(db.Integer)
    
    # Work Details
    work_performed = db.Column(db.Text)
    issues_encountered = db.Column(db.Text)
    materials_used = db.Column(db.Text)  # JSON array of materials/parts
    
    # Status
    is_billable = db.Column(db.Boolean, default=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    work_order = db.relationship('WorkOrder', backref='time_entries')
    technician = db.relationship('User', foreign_keys=[technician_id], backref='time_entries')
    approved_by_user = db.relationship('User', foreign_keys=[approved_by], backref='time_approvals')
    
    def calculate_hours(self):
        """Calculate total hours worked"""
        if self.clock_out and self.clock_in:
            total_seconds = (self.clock_out - self.clock_in).total_seconds()
            total_minutes = int(total_seconds / 60) - (self.break_time_minutes or 0)
            self.total_minutes = max(0, total_minutes)
            self.billable_minutes = self.total_minutes if self.is_billable else 0
            return self.total_minutes / 60
        return 0
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'work_order_id': self.work_order_id,
            'technician': self.technician.username if self.technician else None,
            'clock_in': self.clock_in.isoformat() if self.clock_in else None,
            'clock_out': self.clock_out.isoformat() if self.clock_out else None,
            'total_hours': round(self.total_minutes / 60, 2) if self.total_minutes else 0,
            'billable_hours': round(self.billable_minutes / 60, 2) if self.billable_minutes else 0,
            'work_performed': self.work_performed,
            'is_billable': self.is_billable,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TimeEntry {self.technician.username if self.technician else "Unknown"}: {self.total_minutes}min>'

class QualityChecklist(db.Model):
    """Quality control checklist templates"""
    __tablename__ = 'quality_checklists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    service_type = db.Column(db.String(50))  # 'service', 'modification', 'tune', 'repair', 'collision'
    service_category = db.Column(db.String(50))  # 'maintenance', 'performance', 'body', etc.
    
    # Checklist Items
    checklist_items = db.Column(db.Text, nullable=False)  # JSON array of checklist items
    required_photos = db.Column(db.Text)  # JSON array of required photo types
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = db.relationship('User', backref='quality_checklists_created')
    
    def set_checklist_items(self, items_list):
        """Set checklist items as JSON"""
        self.checklist_items = json.dumps(items_list) if items_list else None
    
    def get_checklist_items(self):
        """Get checklist items as list"""
        if self.checklist_items:
            return json.loads(self.checklist_items)
        return []
    
    def set_required_photos(self, photos_list):
        """Set required photos as JSON"""
        self.required_photos = json.dumps(photos_list) if photos_list else None
    
    def get_required_photos(self):
        """Get required photos as list"""
        if self.required_photos:
            return json.loads(self.required_photos)
        return []
    
    def __repr__(self):
        return f'<QualityChecklist {self.name}>'

class QualityChecklistEntry(db.Model):
    """Completed quality checklist for work orders"""
    __tablename__ = 'quality_checklist_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=False)
    checklist_id = db.Column(db.Integer, db.ForeignKey('quality_checklists.id'), nullable=False)
    
    # Completion Data
    completed_items = db.Column(db.Text)  # JSON object with item_id: {completed: bool, notes: str}
    overall_score = db.Column(db.Integer)  # Percentage score (0-100)
    inspector_signature = db.Column(db.String(200))
    
    # Photos
    inspection_photos = db.Column(db.Text)  # JSON array of photo filenames
    
    # Metadata
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    work_order = db.relationship('WorkOrder', backref='quality_entries')
    checklist = db.relationship('QualityChecklist', backref='entries')
    completed_by_user = db.relationship('User', backref='quality_inspections')
    
    def set_completed_items(self, items_dict):
        """Set completed items as JSON"""
        self.completed_items = json.dumps(items_dict) if items_dict else None
    
    def get_completed_items(self):
        """Get completed items as dict"""
        if self.completed_items:
            return json.loads(self.completed_items)
        return {}
    
    def set_inspection_photos(self, photo_list):
        """Set inspection photos as JSON"""
        self.inspection_photos = json.dumps(photo_list) if photo_list else None
    
    def get_inspection_photos(self):
        """Get inspection photos as list"""
        if self.inspection_photos:
            return json.loads(self.inspection_photos)
        return []
    
    def __repr__(self):
        return f'<QualityChecklistEntry WO:{self.work_order_id}>'

class WarrantyItem(db.Model):
    """Warranty tracking for services and parts"""
    __tablename__ = 'warranty_items'
    
    id = db.Column(db.Integer, primary_key=True)
    service_record_id = db.Column(db.Integer, db.ForeignKey('service_records.id'))
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'))
    
    # Warranty Details
    warranty_type = db.Column(db.String(50), nullable=False)  # 'labor', 'parts', 'comprehensive'
    warranty_description = db.Column(db.String(500))
    warranty_months = db.Column(db.Integer)
    warranty_miles = db.Column(db.Integer)
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date)
    expiration_mileage = db.Column(db.Integer)  # Starting mileage + warranty miles
    
    # Status
    status = db.Column(db.String(20), default='active')  # 'active', 'expired', 'claimed', 'voided'
    claim_count = db.Column(db.Integer, default=0)
    last_claim_date = db.Column(db.Date)
    
    # Customer Info (for easy lookup)
    customer_name = db.Column(db.String(200))
    vehicle_info = db.Column(db.String(200))
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_record = db.relationship('ServiceRecord', backref='warranty_items')
    work_order = db.relationship('WorkOrder', backref='warranty_items')
    part = db.relationship('Part', backref='warranty_items')
    created_by_user = db.relationship('User', backref='warranty_items_created')
    
    def is_expired(self):
        """Check if warranty is expired"""
        if self.expiration_date:
            return datetime.now().date() > self.expiration_date
        return False
    
    def days_until_expiration(self):
        """Calculate days until warranty expires"""
        if self.expiration_date:
            delta = self.expiration_date - datetime.now().date()
            return delta.days
        return None
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'warranty_type': self.warranty_type,
            'warranty_description': self.warranty_description,
            'warranty_months': self.warranty_months,
            'warranty_miles': self.warranty_miles,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'status': self.status,
            'days_until_expiration': self.days_until_expiration(),
            'is_expired': self.is_expired(),
            'customer_name': self.customer_name,
            'vehicle_info': self.vehicle_info,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<WarrantyItem {self.warranty_type}: {self.customer_name}>'

class Invoice(db.Model):
    """Invoice model for billing customers"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    service_record_id = db.Column(db.Integer, db.ForeignKey('service_records.id'))
    
    # Invoice Details
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    
    # Customer Information (snapshot for invoice)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20))
    billing_address = db.Column(db.Text)
    
    # Vehicle Information (if applicable)
    vehicle_year = db.Column(db.Integer)
    vehicle_make = db.Column(db.String(50))
    vehicle_model = db.Column(db.String(50))
    vehicle_vin = db.Column(db.String(17))
    vehicle_license_plate = db.Column(db.String(20))
    
    # Financial Information
    subtotal = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0875)  # Default CA tax rate
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    
    # Payment Information
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid, overdue
    payment_method = db.Column(db.String(20))  # cash, card, check, financing
    amount_paid = db.Column(db.Float, default=0.0)
    balance_due = db.Column(db.Float, default=0.0)
    
    # Invoice Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, cancelled, overdue
    
    # Notes and Terms
    notes = db.Column(db.Text)  # Special notes for customer
    terms = db.Column(db.Text)  # Payment terms and conditions
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime)  # When invoice was sent to customer
    paid_at = db.Column(db.DateTime)  # When invoice was fully paid
    
    # Relationships
    customer = db.relationship('Contact', backref='invoices')
    service_record = db.relationship('ServiceRecord', backref='invoices')
    created_by_user = db.relationship('User', backref='invoices_created')
    
    def calculate_totals(self):
        """Calculate invoice totals from line items"""
        line_items = InvoiceLineItem.query.filter_by(invoice_id=self.id).all()
        self.subtotal = sum(item.total_amount for item in line_items)
        self.tax_amount = round(self.subtotal * self.tax_rate, 2)
        self.total_amount = round(self.subtotal + self.tax_amount - self.discount_amount, 2)
        self.balance_due = round(self.total_amount - self.amount_paid, 2)
    
    def get_status_color(self):
        """Get color class for status display"""
        status_colors = {
            'draft': 'gray',
            'sent': 'blue',
            'paid': 'green',
            'overdue': 'red',
            'cancelled': 'red'
        }
        return status_colors.get(self.status, 'gray')
    
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.due_date and self.status in ['sent', 'partial']:
            return datetime.now().date() > self.due_date
        return False
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_name': self.customer_name,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'amount_paid': self.amount_paid,
            'balance_due': self.balance_due,
            'status': self.status,
            'payment_status': self.payment_status,
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}: {self.customer_name}>'

class InvoiceLineItem(db.Model):
    """Individual line items for invoices"""
    __tablename__ = 'invoice_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    # Item Details
    item_type = db.Column(db.String(20), nullable=False)  # 'labor', 'part', 'service', 'misc'
    description = db.Column(db.String(500), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id'))  # If this is a part
    
    # Quantity and Pricing
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Additional Info
    notes = db.Column(db.Text)
    
    # Relationships
    invoice = db.relationship('Invoice', backref='line_items')
    part = db.relationship('Part', backref='invoice_line_items')
    
    def __repr__(self):
        return f'<InvoiceLineItem {self.description}: ${self.total_amount}>'
