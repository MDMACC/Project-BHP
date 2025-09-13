from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from models.order import Order
from middleware.auth import auth_required, admin_required
from database import db

orders_bp = Blueprint('orders', __name__)

# Validation schemas
class OrderSchema(Schema):
    supplier_id = fields.Int()
    custom_supplier = fields.Dict()
    parts = fields.List(fields.Dict(), required=True)
    total_amount = fields.Float(required=True, validate=lambda x: x >= 0)
    estimated_arrival_time = fields.Str(required=True)
    expected_delivery_date = fields.DateTime()
    shipping_info = fields.Dict()
    custom_time_limit = fields.Int()
    notes = fields.Str()

@orders_bp.route('/', methods=['GET'])
@auth_required
def get_orders():
    """Get all orders with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        status = request.args.get('status')
        
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'pagination': {
                'current_page': page,
                'per_page': limit,
                'total': orders.total,
                'pages': orders.pages
            }
        })
        
    except Exception as e:
        return jsonify({'message': 'Server error'}), 500

@orders_bp.route('/', methods=['POST'])
@auth_required
def create_order():
    """Create a new order"""
    schema = OrderSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        data['created_by_id'] = request.current_user.id
        order = Order(**data)
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error during order creation'}), 500

# Additional routes would go here 