from database import db
from datetime import datetime
from sqlalchemy import Index

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.Enum('appointment', 'maintenance', 'repair', 'inspection', 
                            'delivery', 'meeting', 'other', name='schedule_types'), 
                    nullable=False)
    
    # Customer Information (stored as JSON)
    customer = db.Column(db.JSON)  # name, phone, email, vehicle info
    
    # Time Information
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    
    status = db.Column(db.Enum('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show', 
                              name='schedule_statuses'), default='scheduled')
    
    # Assigned Technician
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Required Parts (stored as JSON array)
    required_parts = db.Column(db.JSON)  # Array of {part_id, quantity, is_available}
    
    # Cost Information (stored as JSON)
    estimated_cost = db.Column(db.JSON)  # {labor, parts, total}
    actual_cost = db.Column(db.JSON)     # {labor, parts, total}
    
    notes = db.Column(db.Text)
    
    # Reminders (stored as JSON array)
    reminders = db.Column(db.JSON)  # Array of {type, time, sent}
    
    # Foreign key to creator
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_technician = db.relationship('User', foreign_keys=[assigned_technician_id], backref='assigned_schedules')
    
    def __init__(self, **kwargs):
        super(Schedule, self).__init__(**kwargs)
        # Initialize cost structures if not provided
        if not self.estimated_cost:
            self.estimated_cost = {'labor': 0, 'parts': 0, 'total': 0}
        if not self.actual_cost:
            self.actual_cost = {'labor': 0, 'parts': 0, 'total': 0}
    
    def calculate_total_estimated_cost(self):
        """Calculate total estimated cost"""
        if self.estimated_cost:
            labor = self.estimated_cost.get('labor', 0)
            parts = self.estimated_cost.get('parts', 0)
            self.estimated_cost['total'] = labor + parts
    
    def calculate_total_actual_cost(self):
        """Calculate total actual cost"""
        if self.actual_cost:
            labor = self.actual_cost.get('labor', 0)
            parts = self.actual_cost.get('parts', 0)
            self.actual_cost['total'] = labor + parts
    
    @property
    def has_conflicts(self):
        """Check for scheduling conflicts (placeholder)"""
        # This would be implemented to check for overlapping schedules
        return False
    
    @property
    def duration_hours(self):
        """Get duration in hours"""
        return self.duration / 60 if self.duration else 0
    
    def to_dict(self):
        """Convert schedule object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'customer': self.customer or {},
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'duration_hours': self.duration_hours,
            'status': self.status,
            'assigned_technician_id': self.assigned_technician_id,
            'required_parts': self.required_parts or [],
            'estimated_cost': self.estimated_cost or {},
            'actual_cost': self.actual_cost or {},
            'notes': self.notes,
            'reminders': self.reminders or [],
            'has_conflicts': self.has_conflicts,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Schedule {self.title}>'

# Create indexes for better query performance
Index('idx_schedule_time', Schedule.start_time, Schedule.end_time)
Index('idx_schedule_status', Schedule.status)
Index('idx_schedule_technician', Schedule.assigned_technician_id) 