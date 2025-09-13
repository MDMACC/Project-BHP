from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import or_
from models.contact import Contact
from middleware.auth import auth_required, admin_required
from database import db

contacts_bp = Blueprint('contacts', __name__)

# Validation schemas
class ContactSchema(Schema):
    name = fields.Str(required=True)
    company = fields.Str()
    type = fields.Str(required=True, validate=lambda x: x in ['supplier', 'customer', 'vendor', 'distributor'])
    email = fields.Email()
    phone = fields.Str()
    mobile = fields.Str()
    fax = fields.Str()
    street = fields.Str()
    city = fields.Str()
    state = fields.Str()
    zip_code = fields.Str()
    country = fields.Str()
    tax_id = fields.Str()
    license_number = fields.Str()
    website = fields.Str()
    credit_limit = fields.Float()
    payment_terms = fields.Str(validate=lambda x: x in ['net_15', 'net_30', 'net_45', 'net_60', 'cash_on_delivery', 'prepaid'])
    specialties = fields.List(fields.Str())
    rating = fields.Int(validate=lambda x: 1 <= x <= 5)
    notes = fields.Str()

@contacts_bp.route('/', methods=['GET'])
@auth_required
def get_contacts():
    """Get all contacts with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        contact_type = request.args.get('type')
        search = request.args.get('search')
        
        # Build query
        query = Contact.query.filter_by(is_active=True)
        
        if contact_type:
            query = query.filter_by(type=contact_type)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Contact.name.ilike(search_term),
                    Contact.company.ilike(search_term),
                    Contact.email.ilike(search_term)
                )
            )
        
        # Apply pagination
        contacts = query.order_by(Contact.name).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return jsonify({
            'contacts': [contact.to_dict() for contact in contacts.items],
            'pagination': {
                'current_page': page,
                'per_page': limit,
                'total': contacts.total,
                'pages': contacts.pages
            }
        })
        
    except Exception as e:
        return jsonify({'message': 'Server error'}), 500

@contacts_bp.route('/', methods=['POST'])
@auth_required
def create_contact():
    """Create a new contact"""
    schema = ContactSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        contact = Contact(**data)
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'message': 'Contact created successfully',
            'contact': contact.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error during contact creation'}), 500

@contacts_bp.route('/<int:contact_id>', methods=['GET'])
@auth_required
def get_contact(contact_id):
    """Get a specific contact by ID"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        return jsonify({'contact': contact.to_dict()})
    except Exception as e:
        return jsonify({'message': 'Contact not found'}), 404

@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
@auth_required
def update_contact(contact_id):
    """Update a contact"""
    schema = ContactSchema()
    
    try:
        data = schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        # Update contact fields
        for key, value in data.items():
            setattr(contact, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Contact updated successfully',
            'contact': contact.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error during contact update'}), 500

@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
@admin_required
def delete_contact(contact_id):
    """Delete a contact (soft delete)"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        contact.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Contact deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error during contact deletion'}), 500

@contacts_bp.route('/suppliers', methods=['GET'])
@auth_required
def get_suppliers():
    """Get all active suppliers"""
    try:
        suppliers = Contact.query.filter_by(type='supplier', is_active=True).order_by(Contact.name).all()
        return jsonify({
            'suppliers': [supplier.to_dict() for supplier in suppliers]
        })
    except Exception as e:
        return jsonify({'message': 'Server error'}), 500 