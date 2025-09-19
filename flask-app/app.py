"""
Simple Flask AutoShop Management System
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import logging
from datetime import datetime, timedelta

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
from models import db, User, Part, Contact, Order, Schedule, Shop, ShippingAccount, ShippingOrder, TrackingEvent
db.init_app(app)

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
    """Dashboard page"""
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
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash('Error loading dashboard', 'error')
        return render_template('dashboard.html', stats={})

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
        from shipping_apis import ShippingAPIFactory
        
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
        from shipping_apis import ShippingAPIFactory
        
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
                'longitude': event.longitude
            } for event in tracking_events]
        }
    except Exception as e:
        logger.error(f"Error getting tracking data: {e}")
        return {'error': 'Error loading tracking data'}, 500

# Initialize database and create demo data
def init_database():
    """Initialize database with demo data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
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

if __name__ == '__main__':
    init_database()
    logger.info("Starting Bluez PowerHouse Management System")
    app.run(host='0.0.0.0', port=5000, debug=True)