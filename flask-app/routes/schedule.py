from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from models.schedule import Schedule
from middleware.auth import auth_required, admin_required
from database import db

schedule_bp = Blueprint('schedule', __name__)

# Validation schemas
class ScheduleSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str()
    type = fields.Str(required=True, validate=lambda x: x in ['appointment', 'maintenance', 'repair', 'inspection', 'delivery', 'meeting', 'other'])
    customer = fields.Dict()
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    duration = fields.Int(required=True)
    assigned_technician_id = fields.Int()
    required_parts = fields.List(fields.Dict())
    estimated_cost = fields.Dict()
    notes = fields.Str()
    reminders = fields.List(fields.Dict())

@schedule_bp.route('/', methods=['GET'])
@auth_required
def get_schedules():
    """Get all schedules with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 20, type=int), 100)
        status = request.args.get('status')
        
        query = Schedule.query
        
        if status:
            query = query.filter_by(status=status)
        
        schedules = query.order_by(Schedule.start_time).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return jsonify({
            'schedules': [schedule.to_dict() for schedule in schedules.items],
            'pagination': {
                'current_page': page,
                'per_page': limit,
                'total': schedules.total,
                'pages': schedules.pages
            }
        })
        
    except Exception as e:
        return jsonify({'message': 'Server error'}), 500

@schedule_bp.route('/', methods=['POST'])
@auth_required
def create_schedule():
    """Create a new schedule"""
    schema = ScheduleSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        data['created_by_id'] = request.current_user.id
        schedule = Schedule(**data)
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule created successfully',
            'schedule': schedule.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Server error during schedule creation'}), 500

# Additional routes would go here 