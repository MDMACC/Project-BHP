from database import db
from datetime import datetime, timedelta
from sqlalchemy import Index
import random
import string

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Supplier Information
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    
    # Custom supplier information for non-contact suppliers (stored as JSON)
    custom_supplier = db.Column(db.JSON)
    
    # Parts information (stored as JSON array)
    parts = db.Column(db.JSON, nullable=False)  # Array of part objects
    
    total_amount = db.Column(db.Float, nullable=False)
    
    status = db.Column(db.Enum('pending', 'confirmed', 'shipped', 'delivered', 'cancelled', 
                              name='order_statuses'), default='pending')
    progress = db.Column(db.Enum('not_started', 'waiting_on_parts', 'started', 'finished', 
                                'waiting_for_pickup', name='order_progress'), default='not_started')
    
    # Dates
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.DateTime)
    estimated_arrival_time = db.Column(db.String(100), nullable=False)  # e.g., "3-5 business days"
    actual_delivery_date = db.Column(db.DateTime)
    
    # Shipping Information (stored as JSON)
    shipping_info = db.Column(db.JSON)  # tracking_number, carrier, shipping_method, shipping_cost
    
    # Countdown Information
    custom_time_limit = db.Column(db.Integer, default=72)  # in hours
    countdown_end_time = db.Column(db.DateTime)
    
    notes = db.Column(db.Text)
    
    # Foreign key to creator
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.generate_order_number()
        if self.custom_time_limit and not self.countdown_end_time:
            self.countdown_end_time = datetime.utcnow() + timedelta(hours=self.custom_time_limit)
    
    def generate_order_number(self):
        """Generate unique order number"""
        timestamp = str(int(datetime.utcnow().timestamp()))[-6:]
        self.order_number = f"ORD-{timestamp}"
    
    @property
    def countdown_status(self):
        """Get countdown status information"""
        if not self.countdown_end_time:
            return None
        
        now = datetime.utcnow()
        time_left = self.countdown_end_time - now
        
        if time_left.total_seconds() <= 0:
            return {
                'status': 'overdue',
                'time_left': 0,
                'message': 'Package is overdue'
            }
        
        total_seconds = int(time_left.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        return {
            'status': 'urgent' if hours < 24 else 'normal',
            'time_left': total_seconds,
            'hours': hours,
            'minutes': minutes,
            'message': f"{hours}h {minutes}m remaining"
        }
    
    @property
    def days_until_delivery(self):
        """Calculate days until expected delivery"""
        if not self.expected_delivery_date:
            return None
        
        now = datetime.utcnow()
        time_diff = self.expected_delivery_date - now
        return max(0, time_diff.days)
    
    def to_dict(self):
        """Convert order object to dictionary"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'custom_supplier': self.custom_supplier,
            'parts': self.parts or [],
            'total_amount': self.total_amount,
            'status': self.status,
            'progress': self.progress,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'estimated_arrival_time': self.estimated_arrival_time,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'shipping_info': self.shipping_info or {},
            'custom_time_limit': self.custom_time_limit,
            'countdown_end_time': self.countdown_end_time.isoformat() if self.countdown_end_time else None,
            'countdown_status': self.countdown_status,
            'days_until_delivery': self.days_until_delivery,
            'notes': self.notes,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

# Create indexes for better query performance
Index('idx_order_number', Order.order_number)
Index('idx_order_status', Order.status)
Index('idx_order_date', Order.order_date) 