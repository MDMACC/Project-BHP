from database import db
from datetime import datetime
from sqlalchemy import Index

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    type = db.Column(db.Enum('supplier', 'customer', 'vendor', 'distributor', name='contact_types'), 
                    nullable=False)
    
    # Contact Information
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    mobile = db.Column(db.String(50))
    fax = db.Column(db.String(50))
    
    # Address Information
    street = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='USA')
    
    # Business Information
    tax_id = db.Column(db.String(50))
    license_number = db.Column(db.String(100))
    website = db.Column(db.String(255))
    credit_limit = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.Enum('net_15', 'net_30', 'net_45', 'net_60', 
                                     'cash_on_delivery', 'prepaid', name='payment_terms'), 
                             default='net_30')
    
    # Additional Information
    specialties = db.Column(db.JSON)  # Store as JSON array
    rating = db.Column(db.Integer, default=3)  # 1-5 rating
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    last_contact_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='supplier_contact', lazy=True)
    parts = db.relationship('Part', backref='supplier_contact', lazy=True)
    
    def __init__(self, **kwargs):
        super(Contact, self).__init__(**kwargs)
        if self.email:
            self.email = self.email.lower().strip()
    
    @property
    def full_address(self):
        """Get full address as string"""
        parts = [self.street, self.city, self.state, self.zip_code]
        return ', '.join([part for part in parts if part])
    
    @property
    def primary_contact(self):
        """Get primary contact method"""
        return self.mobile or self.phone or self.email or 'No contact info'
    
    def to_dict(self):
        """Convert contact object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'type': self.type,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'fax': self.fax,
            'address': {
                'street': self.street,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code,
                'country': self.country
            },
            'business_info': {
                'tax_id': self.tax_id,
                'license_number': self.license_number,
                'website': self.website,
                'credit_limit': self.credit_limit,
                'payment_terms': self.payment_terms
            },
            'specialties': self.specialties or [],
            'rating': self.rating,
            'notes': self.notes,
            'is_active': self.is_active,
            'last_contact_date': self.last_contact_date.isoformat() if self.last_contact_date else None,
            'full_address': self.full_address,
            'primary_contact': self.primary_contact,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Contact {self.name}>'

# Create indexes for better search performance
Index('idx_contact_name_company', Contact.name, Contact.company)
Index('idx_contact_type', Contact.type)
Index('idx_contact_email', Contact.email) 