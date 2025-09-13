from database import db
from datetime import datetime

class Shop(db.Model):
    __tablename__ = 'shop'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, default='Bluez PowerHouse')
    
    # Address Information
    street = db.Column(db.String(255), nullable=False, default='250 W Spazier Ave 101')
    city = db.Column(db.String(100), nullable=False, default='Burbank')
    state = db.Column(db.String(50), nullable=False, default='CA')
    zip_code = db.Column(db.String(20), nullable=False, default='91502')
    country = db.Column(db.String(100), default='USA')
    
    # Contact Information (stored as JSON)
    contact_info = db.Column(db.JSON)  # phone, email, website
    
    # Business Information (stored as JSON)
    business_info = db.Column(db.JSON)  # tax_id, license_number, business_hours
    
    # Settings (stored as JSON)
    settings = db.Column(db.JSON)  # timezone, currency, default_order_time_limit
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Shop, self).__init__(**kwargs)
        # Initialize default structures
        if not self.contact_info:
            self.contact_info = {'phone': '', 'email': '', 'website': ''}
        if not self.business_info:
            self.business_info = {
                'tax_id': '',
                'license_number': '',
                'business_hours': {
                    'monday': {'open': '08:00', 'close': '17:00'},
                    'tuesday': {'open': '08:00', 'close': '17:00'},
                    'wednesday': {'open': '08:00', 'close': '17:00'},
                    'thursday': {'open': '08:00', 'close': '17:00'},
                    'friday': {'open': '08:00', 'close': '17:00'},
                    'saturday': {'open': '09:00', 'close': '15:00'},
                    'sunday': {'open': 'closed', 'close': 'closed'}
                }
            }
        if not self.settings:
            self.settings = {
                'timezone': 'America/Los_Angeles',
                'currency': 'USD',
                'default_order_time_limit': 72
            }
    
    @property
    def full_address(self):
        """Get full address as string"""
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"
    
    @classmethod
    def get_shop_info(cls):
        """Get shop information (singleton pattern)"""
        shop = cls.query.first()
        if not shop:
            shop = cls()
            db.session.add(shop)
            db.session.commit()
        return shop
    
    def to_dict(self):
        """Convert shop object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'address': {
                'street': self.street,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code,
                'country': self.country,
                'full_address': self.full_address
            },
            'contact_info': self.contact_info or {},
            'business_info': self.business_info or {},
            'settings': self.settings or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Shop {self.name}>' 