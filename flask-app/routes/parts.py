from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import or_
from models.part import Part
from models.contact import Contact
from middleware.auth import auth_required, admin_required
from database import db

parts_bp = Blueprint('parts', __name__)

# Validation schemas
class PartSchema(Schema):
    part_number = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str()
    category = fields.Str(required=True, validate=lambda x: x in ['engine', 'brake', 'transmission', 'electrical', 'body', 'interior', 'exhaust', 'suspension', 'other'])
    brand = fields.Str(required=True)
    price = fields.Float(required=True, validate=lambda x: x >= 0)
    cost = fields.Float(required=True, validate=lambda x: x >= 0)
    quantity_in_stock = fields.Int(validate=lambda x: x >= 0)
    minimum_stock_level = fields.Int()
    supplier_id = fields.Int(required=True)
    warehouse = fields.Str()
    shelf = fields.Str()
    bin = fields.Str()
    specifications = fields.Dict()
    compatible_vehicles = fields.List(fields.Dict())
    images = fields.List(fields.Str())

@parts_bp.route('/', methods=['GET'])
@auth_required
def get_parts():
    """Get all parts with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        category = request.args.get('category')
        brand = request.args.get('brand')
        search = request.args.get('search')
        
        # Build query
        query = Part.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if brand:
            query = query.filter(Part.brand.ilike(f"%{brand}%"))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Part.name.ilike(search_term),
                    Part.part_number.ilike(search_term),
                    Part.description.ilike(search_term)
                )
            )
        
        # Apply pagination
        parts = query.order_by(Part.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return jsonify({
            'parts': [part.to_dict() for part in parts.items],
            'pagination': {
                'current_page': page,
                'per_page': limit,
                'total': parts.total,
                'pages': parts.pages
            }
        })
        
    except Exception as e:
        return jsonify({'message': 'Server error'}), 500

@parts_bp.route('/', methods=['POST'])
@auth_required
def create_part():
    """Create a new part"""
    schema = PartSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        # Check if supplier exists
        supplier = Contact.query.get(data['supplier_id'])
        if not supplier:
            return jsonify({'message': 'Supplier not found'}), 404
        
        part = Part(**data)
        db.session.add(part)
        db.session.commit()
        
        return jsonify({
            'message': 'Part created successfully',
            'part': part.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error during part creation'}), 500

# Additional routes would go here (GET by ID, PUT, DELETE, etc.)
# This is a basic structure to demonstrate the pattern 