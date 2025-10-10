"""
Simple Flask AutoShop Management System
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import logging
import hashlib
import hmac
import json
import webbrowser
import threading
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///autoshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from models import db, User, Part, Contact, Order, Schedule, Shop, ShippingAccount, ShippingOrder, TrackingEvent, WebhookLog, ChatMessage, ChatSession, StockHistory, ServiceRecord, ServicePart, WorkOrder, TimeEntry, QualityChecklist, QualityChecklistEntry, WarrantyItem
db.init_app(app)

# Configure file upload
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads', 'photos')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_webhook_signature(provider, payload, signature, secret):
    """Verify webhook signature for security"""
    if not signature or not secret:
        return False
    
    try:
        if provider.lower() in ['fedex', 'ups']:
            # Most carriers use HMAC-SHA256
            expected_signature = hmac.new(
                secret.encode('utf-8'), 
                payload, 
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        elif provider.lower() == 'usps':
            # USPS might use different signature method
            expected_signature = hmac.new(
                secret.encode('utf-8'), 
                payload, 
                hashlib.sha1
            ).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        else:
            # Generic HMAC-SHA256 for other providers
            expected_signature = hmac.new(
                secret.encode('utf-8'), 
                payload, 
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False

def save_package_photo(photo_url, tracking_number):
    """Download and save package photo locally"""
    try:
        import requests
        from urllib.parse import urlparse
        
        # Create upload directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Download the image
        response = requests.get(photo_url, timeout=30)
        response.raise_for_status()
        
        # Get file extension from URL or content type
        parsed_url = urlparse(photo_url)
        ext = os.path.splitext(parsed_url.path)[1]
        if not ext:
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'  # Default
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{tracking_number}_{timestamp}{ext}"
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Saved package photo: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error saving package photo: {e}")
        return None

# Authentication decorator
def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Enhanced Webhook Routes
@app.route('/webhooks/shipping/<provider>', methods=['POST'])
def shipping_webhook(provider):
    """Enhanced shipping webhook endpoint for all carriers"""
    try:
        # Log the webhook request
        webhook_log = WebhookLog(
            provider=provider,
            endpoint=f'/webhooks/shipping/{provider}',
            method=request.method,
            payload=request.get_data(as_text=True),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        webhook_log.set_headers(request.headers)
        
        # Get signature for verification
        signature = (
            request.headers.get('X-Signature') or 
            request.headers.get('X-Hub-Signature-256') or
            request.headers.get('X-UPS-Security-Token') or
            request.headers.get('Authorization')
        )
        if signature:
            webhook_log.signature = signature
        
        db.session.add(webhook_log)
        db.session.commit()
        
        # Parse JSON payload
        try:
            payload_data = request.get_json(force=True)
        except Exception:
            webhook_log.processing_error = "Invalid JSON payload"
            db.session.commit()
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Use enhanced webhook processor
        from shipping_apis_enhanced import WebhookProcessor
        result = WebhookProcessor.process_webhook(provider, payload_data, signature)
        
        if result['success']:
            webhook_log.processed = True
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Webhook processed'}), 200
        else:
            webhook_log.processing_error = result.get('error', 'Unknown error')
            db.session.commit()
            return jsonify({'error': result.get('error', 'Processing failed')}), 400
            
    except Exception as e:
        logger.error(f"Webhook error for {provider}: {e}")
        if 'webhook_log' in locals():
            webhook_log.processing_error = str(e)
            db.session.commit()
        return jsonify({'error': 'Internal server error'}), 500

def process_shipping_webhook(provider, data, webhook_log):
    """Process shipping webhook data based on provider"""
    try:
        # Extract common fields based on provider format
        tracking_number = None
        order_id = None
        status = None
        location = None
        estimated_delivery = None
        photo_url = None
        description = None
        
        if provider.lower() == 'fedex':
            # FedEx webhook format
            tracking_number = data.get('trackingNumber')
            order_id = data.get('shipmentId')
            status = data.get('statusDescription')
            location = data.get('location', {}).get('city')
            if data.get('estimatedDeliveryTimestamp'):
                estimated_delivery = datetime.fromisoformat(data['estimatedDeliveryTimestamp'].replace('Z', '+00:00'))
            photo_url = data.get('packagePhoto', {}).get('url')
            description = data.get('statusDescription')
            
        elif provider.lower() == 'ups':
            # UPS webhook format
            tracking_number = data.get('trackingNumber')
            order_id = data.get('shipmentReferenceNumber')
            status = data.get('status', {}).get('description')
            location_data = data.get('location', {})
            if location_data:
                location = f"{location_data.get('city', '')}, {location_data.get('stateProvince', '')}"
            if data.get('estimatedDelivery'):
                estimated_delivery = datetime.fromisoformat(data['estimatedDelivery'].replace('Z', '+00:00'))
            photo_url = data.get('deliveryPhoto', {}).get('imageUrl')
            description = data.get('activityDescription')
            
        elif provider.lower() == 'usps':
            # USPS webhook format
            tracking_number = data.get('trackingNumber')
            order_id = data.get('labelId')
            status = data.get('eventType')
            location = data.get('eventLocation')
            if data.get('expectedDeliveryDate'):
                estimated_delivery = datetime.strptime(data['expectedDeliveryDate'], '%Y-%m-%d')
            photo_url = data.get('imageUrl')
            description = data.get('eventDescription')
            
        elif provider.lower() == 'dhl':
            # DHL webhook format
            tracking_number = data.get('trackingNumber')
            order_id = data.get('shipmentId')
            status = data.get('status')
            location = data.get('location', {}).get('address', {}).get('addressLocality')
            if data.get('estimatedTimeOfDelivery'):
                estimated_delivery = datetime.fromisoformat(data['estimatedTimeOfDelivery'])
            photo_url = data.get('proofOfDelivery', {}).get('imageUrl')
            description = data.get('statusDescription')
            
        else:
            # Generic format for other carriers
            tracking_number = data.get('tracking_number') or data.get('trackingNumber')
            order_id = data.get('order_id') or data.get('orderId')
            status = data.get('status') or data.get('event_type')
            location = data.get('location') or data.get('city')
            if data.get('estimated_delivery'):
                try:
                    estimated_delivery = datetime.fromisoformat(data['estimated_delivery'].replace('Z', '+00:00'))
                except:
                    pass
            photo_url = data.get('photo_url') or data.get('image_url')
            description = data.get('description') or data.get('event_description')
        
        if not tracking_number:
            return {'success': False, 'error': 'No tracking number found in webhook data'}
        
        # Find or create shipping order
        shipping_order = ShippingOrder.query.filter_by(tracking_number=tracking_number).first()
        
        if not shipping_order:
            # Create new shipping order if not found
            shipping_order = ShippingOrder(
                account_id=1,  # Default account - you might want to match by provider
                order_id=order_id or tracking_number,
                tracking_number=tracking_number,
                carrier=provider.upper(),
                status=status or 'unknown',
                estimated_delivery=estimated_delivery
            )
            db.session.add(shipping_order)
            db.session.flush()  # Get the ID
        else:
            # Update existing order
            if status:
                shipping_order.status = status
            if estimated_delivery:
                shipping_order.estimated_delivery = estimated_delivery
            shipping_order.updated_at = datetime.utcnow()
        
        # Save package photo if provided
        photo_filename = None
        if photo_url:
            photo_filename = save_package_photo(photo_url, tracking_number)
        
        # Create tracking event
        tracking_event = TrackingEvent(
            shipping_order_id=shipping_order.id,
            event_date=datetime.utcnow(),
            status=status or 'update',
            description=description or f'Webhook update from {provider}',
            location=location,
            photo_url=photo_url,
            photo_filename=photo_filename
        )
        tracking_event.set_webhook_data(data)
        
        db.session.add(tracking_event)
        db.session.commit()
        
        logger.info(f"Processed {provider} webhook for tracking {tracking_number}")
        return {'success': True}
        
    except Exception as e:
        logger.error(f"Error processing {provider} webhook: {e}")
        db.session.rollback()
        return {'success': False, 'error': str(e)}

@app.route('/webhooks/test', methods=['POST'])
def test_webhook():
    """Test webhook endpoint for development"""
    try:
        data = request.get_json() or {}
        
        # Create a test tracking event
        test_data = {
            'tracking_number': data.get('tracking_number', 'TEST123456'),
            'status': data.get('status', 'in_transit'),
            'location': data.get('location', 'Distribution Center, CA'),
            'estimated_delivery': data.get('estimated_delivery', '2025-09-20T14:00:00Z'),
            'description': data.get('description', 'Package is in transit'),
            'photo_url': data.get('photo_url')
        }
        
        result = process_shipping_webhook('test', test_data, None)
        
        if result['success']:
            return jsonify({'status': 'success', 'message': 'Test webhook processed'}), 200
        else:
            return jsonify({'error': result.get('error')}), 400
            
    except Exception as e:
        logger.error(f"Test webhook error: {e}")
        return jsonify({'error': str(e)}), 500

# Routes
@app.route('/')
def home():
    """Customer portal home page"""
    return render_template('customer/home.html')

@app.route('/admin')
def admin_home():
    """Admin portal - redirect to admin dashboard or login"""
    if 'user_id' in session:
        user = session.get('user', {})
        if user.get('role') in ['admin', 'manager']:
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get basic statistics
        total_parts = Part.query.filter_by(is_active=True).count()
        total_contacts = Contact.query.filter_by(is_active=True).count()
        total_orders = Order.query.count()
        total_schedules = Schedule.query.filter_by(is_active=True).count()
        
        # Get inventory alerts
        out_of_stock = Part.query.filter_by(is_active=True, quantity_in_stock=0).count()
        low_stock = Part.query.filter(
            Part.is_active == True,
            Part.quantity_in_stock > 0,
            Part.quantity_in_stock <= Part.minimum_stock_level
        ).count()
        
        stats = {
            'total_parts': total_parts,
            'total_contacts': total_contacts,
            'total_orders': total_orders,
            'total_schedules': total_schedules,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock
        }
        
        return render_template('admin/dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        flash('Error loading admin dashboard', 'error')
        return render_template('admin/dashboard.html', stats={})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        try:
            user = User.query.filter_by(email=email).first()
            if user and user.is_active and user.check_password(password):
                session['user_id'] = user.id
                session['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
                logger.info(f"Login successful for user: {user.username}")
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"Login failed for email: {email}")
                flash('Invalid email or password', 'error')
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('An error occurred during login', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    user = session.get('user', {})
    username = user.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page - redirect to admin dashboard"""
    return redirect(url_for('admin_dashboard'))

@app.route('/parts')
@login_required
def parts():
    """Parts management page"""
    try:
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        query = Part.query.filter_by(is_active=True)
        
        if search:
            query = query.filter(
                (Part.name.contains(search)) | 
                (Part.part_number.contains(search)) |
                (Part.description.contains(search))
            )
        
        if category:
            query = query.filter_by(category=category)
        
        parts_list = query.order_by(Part.name).all()
        
        return render_template('parts.html', parts=parts_list, search=search, category=category)
    except Exception as e:
        logger.error(f"Parts page error: {e}")
        flash('Error loading parts', 'error')
        return render_template('parts.html', parts=[])

@app.route('/contacts')
@login_required
def contacts():
    """Contacts management page"""
    try:
        contacts_list = Contact.query.filter_by(is_active=True).order_by(Contact.name).all()
        return render_template('contacts.html', contacts=contacts_list)
    except Exception as e:
        logger.error(f"Contacts page error: {e}")
        flash('Error loading contacts', 'error')
        return render_template('contacts.html', contacts=[])

@app.route('/customer-management')
@login_required
def customer_management():
    """Customer management page with vehicle folders and service history"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get all customers with their service records
        customers = Contact.query.filter_by(type='customer', is_active=True)\
                                .order_by(Contact.name)\
                                .all()
        
        # Get service statistics for each customer
        customer_data = []
        for customer in customers:
            service_count = ServiceRecord.query.filter_by(customer_id=customer.id).count()
            last_service = ServiceRecord.query.filter_by(customer_id=customer.id)\
                                            .order_by(ServiceRecord.service_date.desc())\
                                            .first()
            
            customer_data.append({
                'customer': customer,
                'service_count': service_count,
                'last_service': last_service,
                'vehicle_info': customer.get_vehicle_info()
            })
        
        return render_template('admin/customer_management.html', customer_data=customer_data)
    except Exception as e:
        logger.error(f"Customer management page error: {e}")
        flash('Error loading customer data', 'error')
        return render_template('admin/customer_management.html', customer_data=[])

@app.route('/orders')
@login_required
def orders():
    """Redirect to customer management"""
    return redirect(url_for('customer_management'))

@app.route('/customer/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    """Individual customer folder with service history"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        customer = Contact.query.get_or_404(customer_id)
        
        # Get all service records for this customer
        service_records = ServiceRecord.query.filter_by(customer_id=customer_id)\
                                           .order_by(ServiceRecord.service_date.desc())\
                                           .all()
        
        # Get all appointments for this customer
        appointments = Schedule.query.filter_by(customer_id=customer_id)\
                                   .order_by(Schedule.start_date.desc())\
                                   .all()
        
        return render_template('admin/customer_detail.html', 
                             customer=customer,
                             service_records=service_records,
                             appointments=appointments)
    except Exception as e:
        logger.error(f"Customer detail page error: {e}")
        flash('Error loading customer data', 'error')
        return redirect(url_for('customer_management'))

@app.route('/schedule')
@login_required
def schedule():
    """Schedule management page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        from datetime import date
        today = date.today()
        
        # Get all active schedules ordered by date and time
        schedules_list = Schedule.query.filter_by(is_active=True)\
                                     .order_by(Schedule.start_date, Schedule.start_time)\
                                     .all()
        
        # Get all customers for appointment assignment
        contacts = Contact.query.filter_by(type='customer', is_active=True)\
                               .order_by(Contact.name)\
                               .all()
        
        # Get statistics
        today_appointments = Schedule.query.filter_by(is_active=True, start_date=today).count()
        pending_appointments = Schedule.query.filter_by(is_active=True, status='pending').count()
        confirmed_appointments = Schedule.query.filter_by(is_active=True, status='confirmed').count()
        
        return render_template('schedule.html', 
                             schedules=schedules_list,
                             contacts=contacts,
                             today=today,
                             today_appointments=today_appointments,
                             pending_appointments=pending_appointments,
                             confirmed_appointments=confirmed_appointments)
    except Exception as e:
        logger.error(f"Schedule page error: {e}")
        flash('Error loading schedule', 'error')
        return render_template('schedule.html', schedules=[], today=None)

@app.route('/inventory')
@login_required
def inventory():
    """Inventory management page - redirect to parts (now combined)"""
    return redirect(url_for('parts'))

@app.route('/schedule-appointment')
def schedule_appointment():
    """Public scheduling page"""
    return render_template('schedule_appointment.html')

@app.route('/shipping')
@login_required
def shipping():
    """Unified shipping management page (accounts + webhooks + orders)"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get all shipping orders with their tracking events
        shipping_orders = db.session.query(ShippingOrder).join(ShippingAccount).all()
        
        # Get all accounts
        accounts = ShippingAccount.query.all()
        
        # Get recent webhook logs
        webhook_logs = WebhookLog.query.order_by(WebhookLog.created_at.desc()).limit(50).all()
        
        # Get recent tracking events with photos
        tracking_events = TrackingEvent.query.filter(
            TrackingEvent.photo_filename.isnot(None)
        ).order_by(TrackingEvent.created_at.desc()).limit(20).all()
        
        return render_template('admin/shipping.html', 
                             shipping_orders=shipping_orders, 
                             accounts=accounts,
                             webhook_logs=webhook_logs,
                             tracking_events=tracking_events)
    except Exception as e:
        logger.error(f"Shipping page error: {e}")
        flash('Error loading shipping data', 'error')
        return render_template('admin/shipping.html', 
                             shipping_orders=[], 
                             accounts=[],
                             webhook_logs=[],
                             tracking_events=[])

# Redirect old routes to unified shipping page
@app.route('/admin/accounts')
@login_required
def admin_accounts():
    """Redirect to unified shipping page"""
    return redirect(url_for('shipping'))

@app.route('/admin/webhooks')
@login_required
def admin_webhooks():
    """Redirect to unified shipping page"""
    return redirect(url_for('shipping'))

@app.route('/admin/accounts/add', methods=['GET', 'POST'])
@login_required
def add_account():
    """Add new shipping account"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            provider = request.form.get('provider')
            account_name = request.form.get('account_name')
            username = request.form.get('username')
            api_key = request.form.get('api_key')
            api_secret = request.form.get('api_secret')
            
            if not provider or not account_name:
                flash('Provider and account name are required', 'error')
                return render_template('admin/add_account.html')
            
            # Create new account
            account = ShippingAccount(
                provider=provider,
                account_name=account_name,
                username=username,
                api_key=api_key,  # TODO: Encrypt this
                api_secret=api_secret  # TODO: Encrypt this
            )
            
            db.session.add(account)
            db.session.commit()
            
            flash(f'Account {account_name} added successfully!', 'success')
            return redirect(url_for('admin_accounts'))
            
        except Exception as e:
            logger.error(f"Error adding account: {e}")
            db.session.rollback()
            flash('Error adding account', 'error')
    
    return render_template('admin/add_account.html')

@app.route('/admin/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    """Edit shipping account"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    account = ShippingAccount.query.get_or_404(account_id)
    
    if request.method == 'POST':
        try:
            account.account_name = request.form.get('account_name')
            account.username = request.form.get('username')
            
            # Only update API keys if provided
            api_key = request.form.get('api_key')
            api_secret = request.form.get('api_secret')
            if api_key:
                account.api_key = api_key  # TODO: Encrypt this
            if api_secret:
                account.api_secret = api_secret  # TODO: Encrypt this
            
            account.is_active = 'is_active' in request.form
            account.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Account updated successfully!', 'success')
            return redirect(url_for('admin_accounts'))
            
        except Exception as e:
            logger.error(f"Error updating account: {e}")
            db.session.rollback()
            flash('Error updating account', 'error')
    
    return render_template('admin/edit_account.html', account=account)

@app.route('/admin/accounts/<int:account_id>/sync', methods=['POST'])
@login_required
def sync_account(account_id):
    """Sync shipping account data"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    account = ShippingAccount.query.get_or_404(account_id)
    
    try:
        from shipping_apis_enhanced import ShippingAPIFactory
        
        api = ShippingAPIFactory.create_api(account)
        if api and api.authenticate():
            synced_count = api.sync_orders()
            flash(f'Account {account.account_name} synced successfully! {synced_count} orders processed.', 'success')
        else:
            flash(f'Failed to authenticate with {account.account_name}', 'error')
    except Exception as e:
        logger.error(f"Error syncing account {account_id}: {e}")
        flash('Error syncing account', 'error')
    
    return redirect(url_for('admin_accounts'))

@app.route('/admin/sync-all', methods=['POST'])
@login_required
def sync_all_accounts():
    """Sync all active shipping accounts"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        from shipping_apis_enhanced import ShippingAPIFactory
        
        results = ShippingAPIFactory.sync_all_accounts()
        total_synced = sum(results.values())
        
        if total_synced > 0:
            flash(f'Successfully synced {total_synced} orders across all accounts!', 'success')
        else:
            flash('No new orders found during sync.', 'info')
            
    except Exception as e:
        logger.error(f"Error syncing all accounts: {e}")
        flash('Error syncing accounts', 'error')
    
    return redirect(url_for('admin_accounts'))

@app.route('/api/shipping/orders/<int:order_id>/tracking')
@login_required
def get_tracking_data(order_id):
    """Get tracking data for an order (API endpoint)"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        return {'error': 'Access denied'}, 403
    
    try:
        order = ShippingOrder.query.get_or_404(order_id)
        tracking_events = TrackingEvent.query.filter_by(shipping_order_id=order_id).order_by(TrackingEvent.event_date.desc()).all()
        
        return {
            'order': {
                'id': order.id,
                'order_id': order.order_id,
                'tracking_number': order.tracking_number,
                'status': order.status,
                'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None
            },
            'tracking_events': [{
                'date': event.event_date.isoformat(),
                'status': event.status,
                'description': event.description,
                'location': event.location,
                'latitude': event.latitude,
                'longitude': event.longitude,
                'photo_url': event.photo_url,
                'photo_filename': event.photo_filename
            } for event in tracking_events]
        }
    except Exception as e:
        logger.error(f"Error getting tracking data: {e}")
        return {'error': 'Error loading tracking data'}, 500

# Chat API Routes
@app.route('/api/chat/send', methods=['POST'])
def chat_send():
    """Send a chat message from customer"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Get or create session ID from session or generate new one
        session_id = session.get('chat_session_id')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['chat_session_id'] = session_id
        
        # Get or create chat session
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            chat_session = ChatSession(
                session_id=session_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(chat_session)
        
        # Update last activity
        chat_session.last_activity = datetime.utcnow()
        
        # Create message
        chat_message = ChatMessage(
            session_id=session_id,
            sender_type='customer',
            sender_name='Customer',
            message=message,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(chat_message)
        db.session.commit()
        
        # Generate auto-response (you can enhance this with AI later)
        auto_responses = [
            "Thank you for your message! A team member will respond shortly.",
            "We've received your inquiry and will get back to you soon.",
            "Thanks for contacting Bluez PowerHouse! How can we help with your automotive needs?",
            "Hello! We're here to help. What automotive service are you interested in?",
            "Great to hear from you! Our team will review your message and respond quickly."
        ]
        
        import random
        auto_response = random.choice(auto_responses)
        
        # Create admin response (simulate for now)
        admin_message = ChatMessage(
            session_id=session_id,
            sender_type='admin',
            sender_name='Bluez PowerHouse Team',
            message=auto_response
        )
        
        db.session.add(admin_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'response': auto_response,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Chat send error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500

@app.route('/api/chat/check', methods=['GET'])
def chat_check():
    """Check for new messages in customer's session"""
    try:
        session_id = session.get('chat_session_id')
        if not session_id:
            return jsonify({'hasNewMessages': False})
        
        # Check for unread admin messages in this session
        unread_count = ChatMessage.query.filter_by(
            session_id=session_id,
            sender_type='admin',
            is_read=False
        ).count()
        
        return jsonify({
            'hasNewMessages': unread_count > 0,
            'unreadCount': unread_count
        })
        
    except Exception as e:
        logger.error(f"Chat check error: {e}")
        return jsonify({'hasNewMessages': False})

@app.route('/api/chat/messages', methods=['GET'])
def chat_messages():
    """Get chat messages for current session"""
    try:
        session_id = session.get('chat_session_id')
        if not session_id:
            return jsonify({'messages': []})
        
        messages = ChatMessage.query.filter_by(session_id=session_id)\
                                  .order_by(ChatMessage.created_at.asc())\
                                  .all()
        
        # Mark admin messages as read
        ChatMessage.query.filter_by(
            session_id=session_id,
            sender_type='admin',
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        logger.error(f"Chat messages error: {e}")
        return jsonify({'messages': []})

@app.route('/admin/chat')
@login_required
def admin_chat():
    """Admin chat interface"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get active chat sessions
        chat_sessions = ChatSession.query.filter_by(status='active')\
                                        .order_by(ChatSession.last_activity.desc())\
                                        .all()
        
        return render_template('admin/chat.html', chat_sessions=chat_sessions)
    except Exception as e:
        logger.error(f"Admin chat error: {e}")
        flash('Error loading chat interface', 'error')
        return render_template('admin/chat.html', chat_sessions=[])

@app.route('/api/admin/chat/sessions', methods=['GET'])
@login_required
def admin_chat_sessions():
    """Get all chat sessions for admin"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        sessions = ChatSession.query.order_by(ChatSession.last_activity.desc()).all()
        return jsonify({
            'sessions': [s.to_dict() for s in sessions]
        })
    except Exception as e:
        logger.error(f"Admin chat sessions error: {e}")
        return jsonify({'error': 'Failed to load sessions'}), 500

@app.route('/api/admin/chat/<session_id>/messages', methods=['GET'])
@login_required
def admin_chat_messages(session_id):
    """Get messages for a specific chat session"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        messages = ChatMessage.query.filter_by(session_id=session_id)\
                                  .order_by(ChatMessage.created_at.asc())\
                                  .all()
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages]
        })
    except Exception as e:
        logger.error(f"Admin chat messages error: {e}")
        return jsonify({'error': 'Failed to load messages'}), 500

@app.route('/api/admin/chat/<session_id>/send', methods=['POST'])
@login_required
def admin_chat_send(session_id):
    """Send message as admin to customer"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Create admin message
        chat_message = ChatMessage(
            session_id=session_id,
            sender_type='admin',
            sender_name=user.get('username', 'Admin'),
            sender_id=user.get('id'),
            message=message
        )
        
        db.session.add(chat_message)
        
        # Update session activity
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if chat_session:
            chat_session.last_activity = datetime.utcnow()
            if not chat_session.assigned_admin_id:
                chat_session.assigned_admin_id = user.get('id')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': chat_message.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Admin chat send error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500

# Admin Tools Routes
@app.route('/admin/tools/database')
@login_required
def admin_database_tools():
    """Database management tools"""
    user = session.get('user', {})
    if user.get('role') not in ['admin']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    return render_template('admin/database_tools.html')

@app.route('/admin/tools/reports')
@login_required
def admin_reports():
    """System reports"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    return render_template('admin/reports.html')

@app.route('/admin/tools/settings')
@login_required
def admin_settings():
    """System settings"""
    user = session.get('user', {})
    if user.get('role') not in ['admin']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    return render_template('admin/settings.html')

@app.route('/api/admin/backup', methods=['POST'])
@login_required
def create_backup():
    """Create database backup"""
    user = session.get('user', {})
    if user.get('role') not in ['admin']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import shutil
        from datetime import datetime
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"autoshop_backup_{timestamp}.db"
        backup_path = os.path.join('backups', backup_filename)
        
        # Create backups directory if it doesn't exist
        os.makedirs('backups', exist_ok=True)
        
        # Copy database file
        shutil.copy2('autoshop.db', backup_path)
        
        return jsonify({
            'success': True,
            'filename': backup_filename,
            'path': backup_path
        })
        
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'error': 'Failed to create backup'}), 500

# Parts/Inventory API Routes
@app.route('/api/parts/<int:part_id>/stock', methods=['POST'])
@login_required
def adjust_part_stock(part_id):
    """Adjust part stock with history tracking"""
    try:
        data = request.get_json()
        adjustment = data.get('adjustment', 0)
        reason = data.get('reason', 'adjustment')
        notes = data.get('notes', '')
        
        part = Part.query.get_or_404(part_id)
        quantity_before = part.quantity_in_stock
        
        # Calculate new quantity
        new_quantity = max(0, quantity_before + adjustment)
        
        # Create stock history record
        stock_history = StockHistory(
            part_id=part_id,
            user_id=session.get('user', {}).get('id'),
            adjustment_type='add' if adjustment > 0 else 'remove',
            quantity_before=quantity_before,
            quantity_after=new_quantity,
            adjustment_amount=abs(adjustment),
            reason=reason,
            notes=notes
        )
        
        # Update part stock
        part.quantity_in_stock = new_quantity
        part.updated_at = datetime.utcnow()
        
        db.session.add(stock_history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_quantity': new_quantity,
            'adjustment': adjustment,
            'history_id': stock_history.id
        })
        
    except Exception as e:
        logger.error(f"Stock adjustment error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to adjust stock'}), 500

@app.route('/api/parts/<int:part_id>/image', methods=['POST'])
@login_required
def upload_part_image(part_id):
    """Upload image for a part"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            part = Part.query.get_or_404(part_id)
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"part_{part_id}_{timestamp}_{secure_filename(file.filename)}"
            
            # Create parts upload directory
            parts_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'parts')
            os.makedirs(parts_upload_dir, exist_ok=True)
            
            # Save file
            filepath = os.path.join(parts_upload_dir, filename)
            file.save(filepath)
            
            # Update part record
            part.image_filename = filename
            part.image_url = f"/static/uploads/photos/parts/{filename}"
            part.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'image_url': part.image_url,
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to upload image'}), 500

@app.route('/api/parts/<int:part_id>/archive', methods=['POST'])
@login_required
def archive_part(part_id):
    """Archive or restore a part"""
    try:
        data = request.get_json()
        archive = data.get('archive', True)
        
        part = Part.query.get_or_404(part_id)
        part.is_active = not archive
        part.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        action = 'archived' if archive else 'restored'
        return jsonify({
            'success': True,
            'message': f'Part {action} successfully',
            'is_active': part.is_active
        })
        
    except Exception as e:
        logger.error(f"Archive part error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update part status'}), 500

@app.route('/api/parts/<int:part_id>/history', methods=['GET'])
@login_required
def get_part_stock_history(part_id):
    """Get stock history for a part"""
    try:
        history = StockHistory.query.filter_by(part_id=part_id)\
                                  .order_by(StockHistory.created_at.desc())\
                                  .limit(50)\
                                  .all()
        
        return jsonify({
            'history': [h.to_dict() for h in history]
        })
        
    except Exception as e:
        logger.error(f"Stock history error: {e}")
        return jsonify({'error': 'Failed to load stock history'}), 500

@app.route('/add-part', methods=['GET', 'POST'])
@login_required
def add_part():
    """Add new part with photo upload"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            # Get form data
            part_number = request.form.get('part_number', '').strip()
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            price = float(request.form.get('price', 0) or 0)
            cost = float(request.form.get('cost', 0) or 0)
            quantity = int(request.form.get('quantity_in_stock', 0) or 0)
            minimum_stock = int(request.form.get('minimum_stock_level', 0) or 0)
            location = request.form.get('location', '').strip()
            
            # Validate required fields
            if not part_number or not name:
                flash('Part number and name are required', 'error')
                return render_template('admin/add_part.html')
            
            # Check if part number already exists
            existing_part = Part.query.filter_by(part_number=part_number).first()
            if existing_part:
                flash('Part number already exists', 'error')
                return render_template('admin/add_part.html')
            
            # Create new part
            new_part = Part(
                part_number=part_number,
                name=name,
                description=description,
                category=category,
                price=price,
                cost=cost,
                quantity_in_stock=quantity,
                minimum_stock_level=minimum_stock,
                location=location
            )
            
            db.session.add(new_part)
            db.session.flush()  # Get the ID
            
            # Handle photo upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Create upload directory if it doesn't exist
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # Generate unique filename
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    name_part, ext = os.path.splitext(filename)
                    unique_filename = f"part_{new_part.id}_{timestamp}_{name_part}{ext}"
                    
                    # Save file
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    
                    # Update part with image info
                    new_part.image_filename = unique_filename
                    new_part.image_url = url_for('static', filename=f'uploads/photos/{unique_filename}')
            
            db.session.commit()
            
            flash(f'Part "{name}" added successfully!', 'success')
            return redirect(url_for('parts'))
            
        except ValueError as e:
            flash('Invalid number format in price, cost, or quantity fields', 'error')
            return render_template('admin/add_part.html')
        except Exception as e:
            logger.error(f"Error adding part: {e}")
            db.session.rollback()
            flash('Error adding part', 'error')
            return render_template('admin/add_part.html')
    
    return render_template('admin/add_part.html')

@app.route('/api/schedule-appointment', methods=['POST'])
def schedule_appointment_api():
    """API endpoint to schedule appointments"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'time', 'firstName', 'lastName', 'phone', 'serviceType']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse date and time
        appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        appointment_time_str = data['time']
        
        # Convert time string to datetime
        time_obj = datetime.strptime(appointment_time_str, '%I:%M %p').time()
        start_datetime = datetime.combine(appointment_date, time_obj)
        end_datetime = start_datetime + timedelta(hours=1)  # Default 1 hour appointment
        
        # Create customer name
        customer_name = f"{data['firstName']} {data['lastName']}"
        
        # Check if customer exists in contacts
        customer = Contact.query.filter_by(
            name=customer_name,
            phone=data['phone']
        ).first()
        
        # If customer doesn't exist, create them
        if not customer:
            customer = Contact(
                name=customer_name,
                phone=data['phone'],
                email=data.get('email', ''),
                type='customer'
            )
            db.session.add(customer)
            db.session.flush()  # Get the ID
        
        # Generate appointment title
        service_type = data['serviceType']
        title = f"{service_type} - {customer_name}"
        
        # Create schedule entry
        schedule = Schedule(
            title=title,
            description=f"Service: {service_type}\nVehicle: {data.get('vehicle', 'Not specified')}\nNotes: {data.get('notes', '')}",
            customer_id=customer.id,
            customer_name=customer_name,
            start_date=appointment_date,
            end_date=appointment_date,
            start_time=start_datetime,
            end_time=end_datetime,
            status='pending',
            notes=data.get('notes', '')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        # Create a service record for tracking
        service_record = ServiceRecord(
            service_number=f"SVC-{datetime.now().strftime('%Y%m%d')}-{schedule.id:04d}",
            customer_id=customer.id,
            customer_name=customer_name,
            customer_phone=data['phone'],
            customer_email=data.get('email', ''),
            vehicle_year=None,  # Could be parsed from vehicle string
            vehicle_make=None,
            vehicle_model=None,
            service_type=service_type.lower(),
            service_category='maintenance',  # Default category
            service_title=title,
            service_description=f"Scheduled appointment for {service_type}",
            service_date=appointment_date,
            start_time=start_datetime,
            status='scheduled'
        )
        
        db.session.add(service_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment scheduled successfully!',
            'appointment_id': schedule.id,
            'service_record_id': service_record.id,
            'appointment_details': {
                'date': appointment_date.strftime('%B %d, %Y'),
                'time': appointment_time_str,
                'customer': customer_name,
                'service': service_type,
                'phone': data['phone']
            }
        })
        
    except ValueError as e:
        logger.error(f"Date/time parsing error: {e}")
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        logger.error(f"Schedule appointment error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to schedule appointment'}), 500

@app.route('/api/appointments/<int:appointment_id>/status', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    """Update appointment status (confirm, cancel, etc.)"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'confirmed', 'cancelled', 'completed', 'no-show']:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Update schedule
        schedule = Schedule.query.get_or_404(appointment_id)
        schedule.status = new_status
        
        # Update related service record if it exists
        service_record = ServiceRecord.query.filter_by(customer_id=schedule.customer_id, service_date=schedule.start_date).first()
        if service_record:
            if new_status == 'confirmed':
                service_record.status = 'scheduled'
            elif new_status == 'cancelled':
                service_record.status = 'cancelled'
            elif new_status == 'completed':
                service_record.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Appointment status updated to {new_status}',
            'appointment_id': appointment_id,
            'new_status': new_status
        })
        
    except Exception as e:
        logger.error(f"Update appointment status error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update appointment status'}), 500

@app.route('/api/admin/appointments', methods=['POST'])
@login_required
def create_admin_appointment():
    """Create appointment from admin panel"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'customerName', 'startDate', 'startTime']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse date and time
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        start_time_str = data['startTime']
        
        # Convert time string to datetime
        time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        start_datetime = datetime.combine(start_date, time_obj)
        end_datetime = start_datetime + timedelta(hours=1)  # Default 1 hour appointment
        
        customer_id = data.get('customerId')
        customer_name = data['customerName']
        
        # Handle customer assignment
        if customer_id:
            # Use existing customer
            customer = Contact.query.get_or_404(customer_id)
            customer_name = customer.name
        else:
            # Check if customer exists by name
            customer = Contact.query.filter_by(name=customer_name, type='customer').first()
            
            # If customer doesn't exist, create them
            if not customer:
                customer = Contact(
                    name=customer_name,
                    type='customer'
                )
                db.session.add(customer)
                db.session.flush()  # Get the ID
        
        # Create schedule entry
        schedule = Schedule(
            title=data['title'],
            description=data.get('description', ''),
            customer_id=customer.id,
            customer_name=customer_name,
            start_date=start_date,
            end_date=start_date,
            start_time=start_datetime,
            end_time=end_datetime,
            status=data.get('status', 'pending'),
            technician_name=data.get('technicianName', ''),
            notes=data.get('notes', '')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        # Create a service record for tracking
        service_record = ServiceRecord(
            service_number=f"SVC-{datetime.now().strftime('%Y%m%d')}-{schedule.id:04d}",
            customer_id=customer.id,
            customer_name=customer_name,
            service_type='maintenance',  # Default type
            service_category='maintenance',
            service_title=data['title'],
            service_description=data.get('description', ''),
            service_date=start_date,
            start_time=start_datetime,
            status='scheduled'
        )
        
        db.session.add(service_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment created successfully!',
            'appointment_id': schedule.id,
            'service_record_id': service_record.id
        })
        
    except ValueError as e:
        logger.error(f"Date/time parsing error: {e}")
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        logger.error(f"Create admin appointment error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create appointment'}), 500

@app.route('/api/customers', methods=['POST'])
@login_required
def create_customer():
    """Create new customer with vehicle information"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        logger.error(f"Access denied for user: {user}")
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        logger.info(f"Creating customer with data: {data}")
        
        # Validate required fields
        if not data or not data.get('name'):
            logger.error("Customer name is missing from request")
            return jsonify({'error': 'Customer name is required'}), 400
        
        customer_name = data['name'].strip()
        if not customer_name:
            logger.error("Customer name is empty after stripping")
            return jsonify({'error': 'Customer name cannot be empty'}), 400
        
        # Check if customer already exists
        existing_customer = Contact.query.filter_by(
            name=customer_name,
            type='customer'
        ).first()
        
        if existing_customer:
            logger.error(f"Customer already exists: {customer_name}")
            return jsonify({'error': f'Customer "{customer_name}" already exists'}), 400
        
        # Parse numeric fields safely
        vehicle_year = None
        vehicle_mileage = None
        
        try:
            if data.get('vehicleYear') and data['vehicleYear'].strip():
                vehicle_year = int(data['vehicleYear'])
        except (ValueError, AttributeError):
            logger.warning(f"Invalid vehicle year: {data.get('vehicleYear')}")
        
        try:
            if data.get('vehicleMileage') and data['vehicleMileage'].strip():
                vehicle_mileage = int(data['vehicleMileage'])
        except (ValueError, AttributeError):
            logger.warning(f"Invalid vehicle mileage: {data.get('vehicleMileage')}")
        
        # Create new customer
        customer = Contact(
            name=customer_name,
            type='customer',
            phone=data.get('phone', '').strip(),
            email=data.get('email', '').strip(),
            vehicle_year=vehicle_year,
            vehicle_make=data.get('vehicleMake', '').strip(),
            vehicle_model=data.get('vehicleModel', '').strip(),
            vehicle_color=data.get('vehicleColor', '').strip(),
            vehicle_license_plate=data.get('vehicleLicense', '').strip(),
            vehicle_mileage=vehicle_mileage,
            folder_notes=data.get('notes', '').strip(),
            preferred_contact_method=data.get('preferredContact', 'phone')
        )
        
        logger.info(f"Adding customer to database: {customer.name}")
        db.session.add(customer)
        db.session.commit()
        
        logger.info(f"Customer created successfully with ID: {customer.id}")
        return jsonify({
            'success': True,
            'message': 'Customer created successfully!',
            'customer_id': customer.id
        })
        
    except ValueError as e:
        logger.error(f"ValueError in create customer: {e}")
        return jsonify({'error': 'Invalid number format in year or mileage'}), 400
    except Exception as e:
        logger.error(f"Create customer error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': f'Failed to create customer: {str(e)}'}), 500

@app.route('/api/customers/<int:customer_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_customer(customer_id):
    """Get, update, or delete customer"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        return jsonify({'error': 'Access denied'}), 403
    
    customer = Contact.query.get_or_404(customer_id)
    
    if request.method == 'GET':
        # Get customer details
        return jsonify({
            'success': True,
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'vehicle_year': customer.vehicle_year,
                'vehicle_make': customer.vehicle_make,
                'vehicle_model': customer.vehicle_model,
                'vehicle_color': customer.vehicle_color,
                'vehicle_license_plate': customer.vehicle_license_plate,
                'vehicle_mileage': customer.vehicle_mileage,
                'vehicle_photo_url': customer.vehicle_photo_url,
                'folder_notes': customer.folder_notes,
                'preferred_contact_method': customer.preferred_contact_method,
                'vehicle_info': customer.get_vehicle_info()
            }
        })
    
    elif request.method == 'PUT':
        # Update customer
        try:
            data = request.get_json()
            logger.info(f"Updating customer {customer_id} with data: {data}")
            
            # Update fields
            if 'name' in data:
                customer.name = data['name'].strip()
            if 'phone' in data:
                customer.phone = data['phone'].strip()
            if 'email' in data:
                customer.email = data['email'].strip()
            if 'vehicleYear' in data and data['vehicleYear']:
                customer.vehicle_year = int(data['vehicleYear'])
            if 'vehicleMake' in data:
                customer.vehicle_make = data['vehicleMake'].strip()
            if 'vehicleModel' in data:
                customer.vehicle_model = data['vehicleModel'].strip()
            if 'vehicleColor' in data:
                customer.vehicle_color = data['vehicleColor'].strip()
            if 'vehicleLicense' in data:
                customer.vehicle_license_plate = data['vehicleLicense'].strip()
            if 'vehicleMileage' in data and data['vehicleMileage']:
                customer.vehicle_mileage = int(data['vehicleMileage'])
            if 'notes' in data:
                customer.folder_notes = data['notes'].strip()
            if 'preferredContact' in data:
                customer.preferred_contact_method = data['preferredContact']
            
            customer.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Customer updated successfully!'
            })
            
        except Exception as e:
            logger.error(f"Update customer error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to update customer'}), 500
    
    elif request.method == 'DELETE':
        # Soft delete customer
        try:
            customer.is_active = False
            customer.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Customer archived successfully!'
            })
            
        except Exception as e:
            logger.error(f"Delete customer error: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to archive customer'}), 500

@app.route('/api/test-auth', methods=['GET'])
@login_required
def test_auth():
    """Test endpoint to verify authentication is working"""
    user = session.get('user', {})
    return jsonify({
        'success': True,
        'message': 'Authentication working',
        'user': user,
        'session_data': dict(session)
    })

@app.route('/api/customers/test', methods=['POST'])
def test_customer_creation():
    """Test customer creation without authentication for debugging"""
    try:
        data = request.get_json()
        logger.info(f"Test customer creation with data: {data}")
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Simple test creation
        customer = Contact(
            name=data['name'],
            type='customer',
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Test customer created!',
            'customer_id': customer.id
        })
        
    except Exception as e:
        logger.error(f"Test customer creation error: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>/vehicle-photo', methods=['POST'])
@login_required
def upload_vehicle_photo(customer_id):
    """Upload vehicle photo for customer"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        customer = Contact.query.get_or_404(customer_id)
        
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo file provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Create upload directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            unique_filename = f"vehicle_{customer_id}_{timestamp}_{name}{ext}"
            
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Update customer with vehicle photo info
            customer.vehicle_photo_filename = unique_filename
            customer.vehicle_photo_url = url_for('static', filename=f'uploads/photos/{unique_filename}')
            customer.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'photo_url': customer.vehicle_photo_url,
                'filename': unique_filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Error uploading vehicle photo: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to upload photo'}), 500

# Enhanced Shipping & Webhook API Routes
@app.route('/api/shipping/track/<provider>/<tracking_number>', methods=['GET'])
@login_required
def track_shipment_api(provider, tracking_number):
    """Manual tracking lookup via API"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from shipping_apis_enhanced import ShippingAPIFactory
        result = ShippingAPIFactory.get_tracking_info(provider, tracking_number)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Tracking API error: {e}")
        return jsonify({'error': 'Failed to get tracking info'}), 500

@app.route('/api/shipping/sync-all', methods=['POST'])
@login_required
def sync_all_shipping_api():
    """Sync all shipping accounts via API"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        from shipping_apis_enhanced import ShippingAPIFactory
        results = ShippingAPIFactory.sync_all_accounts()
        total_synced = sum(results.values())
        
        return jsonify({
            'success': True,
            'results': results,
            'total_synced': total_synced
        })
    except Exception as e:
        logger.error(f"Sync all API error: {e}")
        return jsonify({'error': 'Failed to sync accounts'}), 500

@app.route('/api/webhooks/test/<provider>', methods=['POST'])
@login_required
def test_webhook_api(provider):
    """Test webhook endpoint for development"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Generate test webhook data
        test_data = {
            'tracking_number': f'TEST{provider.upper()}123456789',
            'status': 'in_transit',
            'location': 'Distribution Center, CA',
            'estimated_delivery': '2025-10-15T14:00:00Z',
            'description': f'Test webhook from {provider}',
            'order_id': f'ORDER_{provider.upper()}_001'
        }
        
        from shipping_apis_enhanced import WebhookProcessor
        result = WebhookProcessor.process_webhook(provider, test_data)
        
        return jsonify({
            'success': result['success'],
            'test_data': test_data,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Test webhook error: {e}")
        return jsonify({'error': 'Failed to test webhook'}), 500

@app.route('/api/accounts/<int:account_id>/test', methods=['POST'])
@login_required
def test_account_connection(account_id):
    """Test shipping account API connection"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        account = ShippingAccount.query.get_or_404(account_id)
        
        from shipping_apis_enhanced import ShippingAPIFactory
        api = ShippingAPIFactory.create_api(account)
        
        if api:
            test_result = api.test_connection()
            auth_result = api.authenticate()
            
            return jsonify({
                'success': test_result.get('success', False) and auth_result,
                'connection_test': test_result,
                'authentication': auth_result,
                'provider': account.provider,
                'account_name': account.account_name
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No API implementation for {account.provider}'
            })
            
    except Exception as e:
        logger.error(f"Account test error: {e}")
        return jsonify({'error': 'Failed to test account'}), 500

# Service Records Routes
@app.route('/service-records')
@login_required
def service_records():
    """Service records management page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get all service records
        records = ServiceRecord.query.order_by(ServiceRecord.service_date.desc()).all()
        
        # Get customers for dropdown
        customers = Contact.query.filter_by(type='customer', is_active=True).all()
        
        # Get technicians for dropdown
        technicians = User.query.filter_by(is_active=True).all()
        
        return render_template('admin/service_records.html', 
                             records=records,
                             customers=customers,
                             technicians=technicians)
    except Exception as e:
        logger.error(f"Service records page error: {e}")
        flash('Error loading service records', 'error')
        return render_template('admin/service_records.html', records=[], customers=[], technicians=[])

@app.route('/api/service-records', methods=['POST'])
@login_required
def create_service_record():
    """Create new service record"""
    try:
        data = request.get_json()
        
        # Generate service number
        import uuid
        service_number = f"SVC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create service record
        record = ServiceRecord(
            service_number=service_number,
            customer_id=data.get('customer_id'),
            customer_name=data.get('customer_name'),
            customer_phone=data.get('customer_phone'),
            customer_email=data.get('customer_email'),
            vehicle_year=data.get('vehicle_year'),
            vehicle_make=data.get('vehicle_make'),
            vehicle_model=data.get('vehicle_model'),
            vehicle_vin=data.get('vehicle_vin'),
            vehicle_mileage=data.get('vehicle_mileage'),
            vehicle_license_plate=data.get('vehicle_license_plate'),
            service_type=data.get('service_type'),
            service_category=data.get('service_category'),
            service_title=data.get('service_title'),
            service_description=data.get('service_description'),
            technician_id=data.get('technician_id'),
            technician_name=data.get('technician_name'),
            service_date=datetime.strptime(data.get('service_date'), '%Y-%m-%d').date(),
            labor_hours=data.get('labor_hours', 0),
            labor_cost=data.get('labor_cost', 0),
            parts_cost=data.get('parts_cost', 0),
            total_cost=data.get('total_cost', 0),
            warranty_months=data.get('warranty_months', 6),
            warranty_miles=data.get('warranty_miles', 12000),
            notes=data.get('notes'),
            internal_notes=data.get('internal_notes'),
            created_by=session.get('user', {}).get('id')
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'service_number': service_number,
            'record': record.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Create service record error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create service record'}), 500

@app.route('/api/service-records/<int:record_id>', methods=['PUT'])
@login_required
def update_service_record(record_id):
    """Update service record"""
    try:
        data = request.get_json()
        record = ServiceRecord.query.get_or_404(record_id)
        
        # Update fields
        for field in ['customer_name', 'customer_phone', 'customer_email', 'vehicle_year', 
                     'vehicle_make', 'vehicle_model', 'vehicle_vin', 'vehicle_mileage',
                     'service_type', 'service_category', 'service_title', 'service_description',
                     'technician_name', 'labor_hours', 'labor_cost', 'parts_cost', 'total_cost',
                     'status', 'payment_status', 'payment_method', 'notes', 'internal_notes']:
            if field in data:
                setattr(record, field, data[field])
        
        if 'service_date' in data:
            record.service_date = datetime.strptime(data['service_date'], '%Y-%m-%d').date()
        
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'record': record.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Update service record error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update service record'}), 500

@app.route('/api/service-records/<int:record_id>/photos', methods=['POST'])
@login_required
def upload_service_photos(record_id):
    """Upload before/after photos for service record"""
    try:
        record = ServiceRecord.query.get_or_404(record_id)
        photo_type = request.form.get('type', 'before')  # 'before' or 'after'
        
        if 'photos' not in request.files:
            return jsonify({'error': 'No photos provided'}), 400
        
        files = request.files.getlist('photos')
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Create filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"service_{record_id}_{photo_type}_{timestamp}_{secure_filename(file.filename)}"
                
                # Create service photos directory
                service_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'services')
                os.makedirs(service_upload_dir, exist_ok=True)
                
                # Save file
                filepath = os.path.join(service_upload_dir, filename)
                file.save(filepath)
                uploaded_files.append(filename)
        
        # Update record with photo filenames
        if photo_type == 'before':
            current_photos = record.get_before_photos()
            current_photos.extend(uploaded_files)
            record.set_before_photos(current_photos)
        else:
            current_photos = record.get_after_photos()
            current_photos.extend(uploaded_files)
            record.set_after_photos(current_photos)
        
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'uploaded_files': uploaded_files,
            'photo_type': photo_type
        })
        
    except Exception as e:
        logger.error(f"Service photo upload error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to upload photos'}), 500

# Work Order Management Routes
@app.route('/work-orders')
@login_required
def work_orders():
    """Work orders management page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get work orders based on user role
        if user.get('role') == 'employee':
            # Employees see only their assigned work orders
            orders = WorkOrder.query.filter_by(assigned_technician_id=user.get('id')).order_by(WorkOrder.scheduled_start.desc()).all()
        else:
            # Admins and managers see all work orders
            orders = WorkOrder.query.order_by(WorkOrder.scheduled_start.desc()).all()
        
        return render_template('admin/work_orders.html', work_orders=orders)
    except Exception as e:
        logger.error(f"Work orders page error: {e}")
        flash('Error loading work orders', 'error')
        return render_template('admin/work_orders.html', work_orders=[])

@app.route('/api/work-orders', methods=['POST'])
@login_required
def create_work_order():
    """Create new work order"""
    try:
        data = request.get_json()
        
        # Generate work order number
        import uuid
        work_order_number = f"WO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        
        # Create work order
        work_order = WorkOrder(
            work_order_number=work_order_number,
            service_record_id=data.get('service_record_id'),
            assigned_technician_id=data.get('assigned_technician_id'),
            priority=data.get('priority', 'normal'),
            scheduled_start=datetime.fromisoformat(data.get('scheduled_start')) if data.get('scheduled_start') else None,
            estimated_completion=datetime.fromisoformat(data.get('estimated_completion')) if data.get('estimated_completion') else None,
            estimated_hours=data.get('estimated_hours', 0),
            work_description=data.get('work_description'),
            special_instructions=data.get('special_instructions'),
            safety_notes=data.get('safety_notes'),
            created_by=session.get('user', {}).get('id')
        )
        
        # Set required tools if provided
        if data.get('required_tools'):
            work_order.set_required_tools(data['required_tools'])
        
        db.session.add(work_order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'work_order_number': work_order_number,
            'work_order': work_order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Create work order error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create work order'}), 500

@app.route('/api/work-orders/<int:work_order_id>/time', methods=['POST'])
@login_required
def clock_time(work_order_id):
    """Clock in/out for work order"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'clock_in' or 'clock_out'
        
        work_order = WorkOrder.query.get_or_404(work_order_id)
        user_id = session.get('user', {}).get('id')
        
        if action == 'clock_in':
            # Create new time entry
            time_entry = TimeEntry(
                work_order_id=work_order_id,
                technician_id=user_id,
                clock_in=datetime.utcnow(),
                work_performed=data.get('work_performed', '')
            )
            
            # Update work order status if not already in progress
            if work_order.status == 'assigned':
                work_order.status = 'in-progress'
                work_order.actual_start = datetime.utcnow()
            
            db.session.add(time_entry)
            
        elif action == 'clock_out':
            # Find the most recent uncompleted time entry
            time_entry = TimeEntry.query.filter_by(
                work_order_id=work_order_id,
                technician_id=user_id,
                clock_out=None
            ).order_by(TimeEntry.clock_in.desc()).first()
            
            if time_entry:
                time_entry.clock_out = datetime.utcnow()
                time_entry.work_performed = data.get('work_performed', time_entry.work_performed)
                time_entry.break_time_minutes = data.get('break_time_minutes', 0)
                time_entry.calculate_hours()
                
                # Update work order actual hours
                total_hours = sum([entry.total_minutes / 60 for entry in work_order.time_entries if entry.total_minutes])
                work_order.actual_hours = total_hours
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': action,
            'time_entry_id': time_entry.id if time_entry else None
        })
        
    except Exception as e:
        logger.error(f"Time tracking error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to track time'}), 500

@app.route('/api/work-orders/<int:work_order_id>/quality', methods=['POST'])
@login_required
def complete_quality_check(work_order_id):
    """Complete quality control checklist"""
    try:
        data = request.get_json()
        
        work_order = WorkOrder.query.get_or_404(work_order_id)
        
        # Update work order quality info
        work_order.quality_checklist_completed = True
        work_order.quality_score = data.get('quality_score', 10)
        work_order.quality_notes = data.get('quality_notes')
        work_order.inspector_id = session.get('user', {}).get('id')
        work_order.inspection_date = datetime.utcnow()
        work_order.status = 'completed'
        work_order.actual_completion = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'work_order': work_order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Quality check error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to complete quality check'}), 500

# Time Tracking API Routes
@app.route('/api/time-entries/active', methods=['GET'])
@login_required
def get_active_time_entry():
    """Get active time entry for current user"""
    try:
        user_id = session.get('user', {}).get('id')
        active_entry = TimeEntry.query.filter_by(
            technician_id=user_id,
            clock_out=None
        ).first()
        
        if active_entry:
            return jsonify({
                'active': True,
                'time_entry': active_entry.to_dict(),
                'work_order_number': active_entry.work_order.work_order_number if active_entry.work_order else None
            })
        else:
            return jsonify({'active': False})
            
    except Exception as e:
        logger.error(f"Get active time entry error: {e}")
        return jsonify({'error': 'Failed to get active time entry'}), 500

@app.route('/api/technician/dashboard')
@login_required
def technician_dashboard():
    """Technician dashboard with assigned work orders and time tracking"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    try:
        user_id = user.get('id')
        
        # Get assigned work orders
        assigned_orders = WorkOrder.query.filter_by(assigned_technician_id=user_id)\
                                        .filter(WorkOrder.status.in_(['assigned', 'in-progress']))\
                                        .order_by(WorkOrder.priority.desc(), WorkOrder.scheduled_start)\
                                        .all()
        
        # Get active time entry
        active_time_entry = TimeEntry.query.filter_by(
            technician_id=user_id,
            clock_out=None
        ).first()
        
        # Get today's completed work orders
        today = datetime.now().date()
        completed_today = WorkOrder.query.filter_by(assigned_technician_id=user_id)\
                                        .filter(WorkOrder.status == 'completed')\
                                        .filter(db.func.date(WorkOrder.actual_completion) == today)\
                                        .count()
        
        # Get today's total hours
        today_entries = TimeEntry.query.filter_by(technician_id=user_id)\
                                      .filter(db.func.date(TimeEntry.clock_in) == today)\
                                      .filter(TimeEntry.clock_out.isnot(None))\
                                      .all()
        
        total_hours_today = sum([entry.total_minutes / 60 for entry in today_entries if entry.total_minutes])
        
        return render_template('admin/technician_dashboard.html',
                             assigned_orders=assigned_orders,
                             active_time_entry=active_time_entry,
                             completed_today=completed_today,
                             total_hours_today=round(total_hours_today, 2))
        
    except Exception as e:
        logger.error(f"Technician dashboard error: {e}")
        flash('Error loading dashboard', 'error')
        return render_template('admin/technician_dashboard.html',
                             assigned_orders=[],
                             active_time_entry=None,
                             completed_today=0,
                             total_hours_today=0)

# Quality Control Routes
@app.route('/quality-checklists')
@login_required
def quality_checklists():
    """Quality checklists management page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        checklists = QualityChecklist.query.filter_by(is_active=True).all()
        return render_template('admin/quality_checklists.html', checklists=checklists)
    except Exception as e:
        logger.error(f"Quality checklists page error: {e}")
        flash('Error loading quality checklists', 'error')
        return render_template('admin/quality_checklists.html', checklists=[])

@app.route('/api/quality-checklists', methods=['POST'])
@login_required
def create_quality_checklist():
    """Create new quality checklist template"""
    try:
        data = request.get_json()
        
        checklist = QualityChecklist(
            name=data.get('name'),
            service_type=data.get('service_type'),
            service_category=data.get('service_category'),
            created_by=session.get('user', {}).get('id')
        )
        
        # Set checklist items
        if data.get('checklist_items'):
            checklist.set_checklist_items(data['checklist_items'])
        
        # Set required photos
        if data.get('required_photos'):
            checklist.set_required_photos(data['required_photos'])
        
        db.session.add(checklist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'checklist_id': checklist.id
        })
        
    except Exception as e:
        logger.error(f"Create quality checklist error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create quality checklist'}), 500

# Warranty Tracking Routes
@app.route('/warranty-tracking')
@login_required
def warranty_tracking():
    """Warranty tracking page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager', 'employee']:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get all warranties
        warranties = WarrantyItem.query.order_by(WarrantyItem.expiration_date.asc()).all()
        
        # Get expiring warranties (within 30 days)
        from datetime import timedelta
        expiring_soon = WarrantyItem.query.filter(
            WarrantyItem.expiration_date <= datetime.now().date() + timedelta(days=30),
            WarrantyItem.status == 'active'
        ).all()
        
        return render_template('admin/warranty_tracking.html', 
                             warranties=warranties,
                             expiring_soon=expiring_soon)
    except Exception as e:
        logger.error(f"Warranty tracking page error: {e}")
        flash('Error loading warranty tracking', 'error')
        return render_template('admin/warranty_tracking.html', warranties=[], expiring_soon=[])

# Initialize database and create demo data
def init_database():
    """Initialize database with demo data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we need to add new columns to existing tables
        try:
            # Check if photo_url column exists in tracking_events
            db.session.execute('SELECT photo_url FROM tracking_events LIMIT 1')
        except Exception:
            # Add new columns to tracking_events table
            logger.info("Adding new columns to tracking_events table...")
            try:
                db.session.execute('ALTER TABLE tracking_events ADD COLUMN photo_url VARCHAR(500)')
                db.session.execute('ALTER TABLE tracking_events ADD COLUMN photo_filename VARCHAR(255)')
                db.session.execute('ALTER TABLE tracking_events ADD COLUMN webhook_data TEXT')
                db.session.commit()
                logger.info("Successfully added new columns to tracking_events")
            except Exception as e:
                logger.error(f"Error adding columns to tracking_events: {e}")
                db.session.rollback()
        
        # Check if we already have data
        if User.query.count() > 0:
            logger.info("Database already initialized")
            return
        
        logger.info("Initializing database with demo data...")
        
        # Create demo users
        users = [
            User('admin', 'admin@autoshop.com', 'admin123', 'admin'),
            User('manager', 'manager@autoshop.com', 'manager123', 'manager'),
            User('employee', 'employee@autoshop.com', 'employee123', 'employee')
        ]
        
        for user in users:
            db.session.add(user)
        
        # Create supplier contacts (keep suppliers, remove fake customers)
        contacts = [
            Contact(name='NAPA Auto Parts', company='NAPA Auto Parts', type='supplier', 
                   email='orders@napaonline.com', phone='555-0101'),
            Contact(name="O'Reilly Auto Parts", company="O'Reilly Auto Parts", type='supplier',
                   email='orders@oreillyauto.com', phone='555-0102')
        ]
        
        for contact in contacts:
            db.session.add(contact)
        
        # Create demo parts
        parts = [
            Part(part_number='BRK-001', name='Brake Pads - Front', category='Brakes',
                 price=89.99, cost=45.00, quantity_in_stock=24, minimum_stock_level=10),
            Part(part_number='ENG-002', name='Oil Filter', category='Engine',
                 price=12.99, cost=6.50, quantity_in_stock=150, minimum_stock_level=50),
            Part(part_number='SUS-003', name='Shock Absorber', category='Suspension',
                 price=159.99, cost=80.00, quantity_in_stock=8, minimum_stock_level=5),
            Part(part_number='TIR-004', name='All-Season Tire 225/60R16', category='Tires',
                 price=129.99, cost=75.00, quantity_in_stock=0, minimum_stock_level=8)
        ]
        
        for part in parts:
            db.session.add(part)
        
        # Create shop info
        shop = Shop(
            name='Bluez PowerHouse Auto Repair (BPH Automotive)',
            address='8033 Remmet Ave',
            city='Canoga Park',
            state='CA',
            zip_code='91304',
            phone='(747) 474-9193',
            business_hours='Monday-Friday: 11AM-7PM, Saturday-Sunday: Closed',
            services_offered='Full-service automotive shop: Maintenance & Repairs, Performance Upgrades, Collision Repair, Body Kits & Modifications, Engine Tuning, New & Used Auto Sales. Specializing in high-performance and exotic vehicles.'
        )
        db.session.add(shop)
        
        try:
            db.session.commit()
            logger.info("Database initialized successfully!")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing database: {e}")

@app.route('/api/carousel-images')
def get_carousel_images():
    """Get images from the Cfrontpageimages folder following 'image Nc.jpeg' naming pattern"""
    try:
        import re
        
        images_dir = os.path.join(app.static_folder, 'images', 'Cfrontpageimages')
        if not os.path.exists(images_dir):
            return jsonify({'images': []})
        
        # Pattern to match 'imageNc.jpeg' where N is a number (no spaces)
        pattern = re.compile(r'^image(\d+)c\.jpeg$', re.IGNORECASE)
        images = []
        
        for filename in os.listdir(images_dir):
            match = pattern.match(filename)
            if match:
                number = int(match.group(1))  # Extract the number for sorting
                images.append({
                    'filename': filename,
                    'url': url_for('static', filename=f'images/Cfrontpageimages/{filename}'),
                    'order': number
                })
        
        # Sort images by the number in their filename
        images.sort(key=lambda x: x['order'])
        
        return jsonify({'images': images})
    except Exception as e:
        logger.error(f"Error getting carousel images: {e}")
        return jsonify({'images': []})

def open_browser():
    """Open the default browser to the application URL"""
    webbrowser.open('http://localhost:5001')

if __name__ == '__main__':
    init_database()
    logger.info("Starting Bluez PowerHouse Management System")
    
    # Open browser after a short delay to ensure server is running
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(1.5, open_browser).start()
    
    app.run(host='0.0.0.0', port=5001, debug=True)