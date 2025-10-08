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
from models import db, User, Part, Contact, Order, Schedule, Shop, ShippingAccount, ShippingOrder, TrackingEvent, WebhookLog, ChatMessage, ChatSession, StockHistory
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

@app.route('/orders')
@login_required
def orders():
    """Orders management page"""
    try:
        orders_list = Order.query.order_by(Order.created_at.desc()).all()
        return render_template('orders.html', orders=orders_list)
    except Exception as e:
        logger.error(f"Orders page error: {e}")
        flash('Error loading orders', 'error')
        return render_template('orders.html', orders=[])

@app.route('/schedule')
@login_required
def schedule():
    """Schedule management page"""
    try:
        schedules_list = Schedule.query.filter_by(is_active=True).order_by(Schedule.start_date).all()
        return render_template('schedule.html', schedules=schedules_list)
    except Exception as e:
        logger.error(f"Schedule page error: {e}")
        flash('Error loading schedule', 'error')
        return render_template('schedule.html', schedules=[])

@app.route('/inventory')
@login_required
def inventory():
    """Inventory management page"""
    return redirect(url_for('parts'))

@app.route('/schedule-appointment')
def schedule_appointment():
    """Public scheduling page"""
    return render_template('schedule_appointment.html')

@app.route('/shipping')
@login_required
def shipping():
    """Shipping management page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get all shipping orders with their tracking events
        shipping_orders = db.session.query(ShippingOrder).join(ShippingAccount).all()
        
        # Get accounts for filtering
        accounts = ShippingAccount.query.filter_by(is_active=True).all()
        
        return render_template('admin/shipping.html', 
                             shipping_orders=shipping_orders, 
                             accounts=accounts)
    except Exception as e:
        logger.error(f"Shipping page error: {e}")
        flash('Error loading shipping data', 'error')
        return render_template('admin/shipping.html', shipping_orders=[], accounts=[])

@app.route('/admin/accounts')
@login_required
def admin_accounts():
    """Admin accounts management page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        accounts = ShippingAccount.query.all()
        return render_template('admin/accounts.html', accounts=accounts)
    except Exception as e:
        logger.error(f"Admin accounts page error: {e}")
        flash('Error loading accounts', 'error')
        return render_template('admin/accounts.html', accounts=[])

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

@app.route('/admin/webhooks')
@login_required
def admin_webhooks():
    """Admin webhook management page"""
    user = session.get('user', {})
    if user.get('role') not in ['admin', 'manager']:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get recent webhook logs
        webhook_logs = WebhookLog.query.order_by(WebhookLog.created_at.desc()).limit(50).all()
        
        # Get recent tracking events with photos
        tracking_events = TrackingEvent.query.filter(
            TrackingEvent.photo_filename.isnot(None)
        ).order_by(TrackingEvent.created_at.desc()).limit(20).all()
        
        return render_template('admin/webhooks.html', 
                             webhook_logs=webhook_logs,
                             tracking_events=tracking_events)
    except Exception as e:
        logger.error(f"Admin webhooks page error: {e}")
        flash('Error loading webhook data', 'error')
        return render_template('admin/webhooks.html', webhook_logs=[], tracking_events=[])

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
        
        # Create demo contacts
        contacts = [
            Contact(name='NAPA Auto Parts', company='NAPA Auto Parts', type='supplier', 
                   email='orders@napaonline.com', phone='555-0101'),
            Contact(name="O'Reilly Auto Parts", company="O'Reilly Auto Parts", type='supplier',
                   email='orders@oreillyauto.com', phone='555-0102'),
            Contact(name='John Smith', type='customer', email='john.smith@email.com', phone='555-0201'),
            Contact(name='Jane Doe', company='Doe Enterprises', type='customer',
                   email='jane@doeenterprises.com', phone='555-0301')
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
            name='Bluez PowerHouse Auto Repair',
            address='123 Main Street',
            city='Auto City',
            state='CA',
            zip_code='90210',
            phone='555-AUTO-FIX',
            business_hours='Monday-Saturday: 9AM-6PM, Sunday: Closed'
        )
        db.session.add(shop)
        
        try:
            db.session.commit()
            logger.info("Database initialized successfully!")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing database: {e}")

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