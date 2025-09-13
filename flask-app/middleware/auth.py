from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models.user import User

def auth_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            user = User.query.filter_by(id=user_id, is_active=True).first()
            if not user:
                return jsonify({'message': 'Token is not valid'}), 401
            
            # Add user to request context
            request.current_user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'message': 'Token is not valid'}), 401
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin or manager privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            user = User.query.filter_by(id=user_id, is_active=True).first()
            if not user:
                return jsonify({'message': 'Token is not valid'}), 401
            
            if user.role not in ['admin', 'manager']:
                return jsonify({'message': 'Access denied. Admin privileges required.'}), 403
            
            # Add user to request context
            request.current_user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'message': 'Authorization failed'}), 401
    
    return decorated_function 