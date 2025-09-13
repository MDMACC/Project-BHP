from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from models.shop import Shop
from middleware.auth import auth_required, admin_required
from database import db

shop_bp = Blueprint('shop', __name__)

# Validation schemas
class ShopSchema(Schema):
    name = fields.Str()
    street = fields.Str()
    city = fields.Str()
    state = fields.Str()
    zip_code = fields.Str()
    country = fields.Str()
    contact_info = fields.Dict()
    business_info = fields.Dict()
    settings = fields.Dict()

@shop_bp.route('/info', methods=['GET'])
@auth_required
def get_shop_info():
    """Get shop information"""
    try:
        shop = Shop.get_shop_info()
        return jsonify({'shop': shop.to_dict()})
    except Exception as e:
        return jsonify({'message': 'Server error'}), 500

@shop_bp.route('/info', methods=['PUT'])
@admin_required
def update_shop_info():
    """Update shop information"""
    schema = ShopSchema()
    
    try:
        data = schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        shop = Shop.get_shop_info()
        
        # Update shop fields
        for key, value in data.items():
            setattr(shop, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Shop information updated successfully',
            'shop': shop.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error during shop update'}), 500 