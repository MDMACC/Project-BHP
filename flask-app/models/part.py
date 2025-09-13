from database import db
from datetime import datetime
from sqlalchemy import Index

class Part(db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.Enum('engine', 'brake', 'transmission', 'electrical', 
                                'body', 'interior', 'exhaust', 'suspension', 'other', 
                                name='part_categories'), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock_level = db.Column(db.Integer, default=5)
    
    # Foreign key to supplier
    supplier_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    
    # Location Information
    warehouse = db.Column(db.String(100))
    shelf = db.Column(db.String(50))
    bin = db.Column(db.String(50))
    
    # Specifications (stored as JSON)
    specifications = db.Column(db.JSON)  # Will contain weight, dimensions, material, color
    
    # Compatible Vehicles (stored as JSON array)
    compatible_vehicles = db.Column(db.JSON)  # Array of {make, model, year: {start, end}}
    
    # Images (stored as JSON array of URLs)
    images = db.Column(db.JSON)
    
    is_active = db.Column(db.Boolean, default=True)
    last_restocked = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Part, self).__init__(**kwargs)
        if self.part_number:
            self.part_number = self.part_number.upper().strip()
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost > 0:
            return round(((self.price - self.cost) / self.cost * 100), 2)
        return 0
    
    @property
    def stock_status(self):
        """Get current stock status"""
        if self.quantity_in_stock == 0:
            return 'out_of_stock'
        elif self.quantity_in_stock <= self.minimum_stock_level:
            return 'low_stock'
        return 'in_stock'
    
    @property
    def location_string(self):
        """Get location as formatted string"""
        parts = [self.warehouse, self.shelf, self.bin]
        return ' - '.join([part for part in parts if part])
    
    def to_dict(self):
        """Convert part object to dictionary"""
        return {
            'id': self.id,
            'part_number': self.part_number,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'brand': self.brand,
            'price': self.price,
            'cost': self.cost,
            'quantity_in_stock': self.quantity_in_stock,
            'minimum_stock_level': self.minimum_stock_level,
            'supplier_id': self.supplier_id,
            'location': {
                'warehouse': self.warehouse,
                'shelf': self.shelf,
                'bin': self.bin,
                'location_string': self.location_string
            },
            'specifications': self.specifications or {},
            'compatible_vehicles': self.compatible_vehicles or [],
            'images': self.images or [],
            'is_active': self.is_active,
            'last_restocked': self.last_restocked.isoformat() if self.last_restocked else None,
            'profit_margin': self.profit_margin,
            'stock_status': self.stock_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Part {self.part_number}: {self.name}>'

# Create indexes for better search performance
Index('idx_part_number', Part.part_number)
Index('idx_part_category_brand', Part.category, Part.brand) 