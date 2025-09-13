from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from email_validator import validate_email, EmailNotValidError
from models.user import User
from middleware.auth import auth_required
from database import db

auth_bp = Blueprint('auth', __name__)

# Validation schemas
class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)
    role = fields.Str(validate=lambda x: x in ['admin', 'manager', 'employee'])

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    schema = RegisterSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        username = data['username']
        email = data['email'].lower().strip()
        password = data['password']
        role = data.get('role', 'employee')
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            return jsonify({'message': 'User already exists'}), 400
        
        # Create new user
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error during registration'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    schema = LoginSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        email = data['email'].lower().strip()
        password = data['password']
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 400
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 400
        
        # Check password
        if not user.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 400
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
        
    except Exception as e:
        return jsonify({'message': 'Server error during login'}), 500

@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user():
    """Get current user information"""
    try:
        user = request.current_user
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active
            }
        })
    except Exception as e:
        return jsonify({'message': 'Server error'}), 500 