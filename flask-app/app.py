from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta
import os
from dotenv import load_dotenv
from database import db

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///autoshop_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'fallback_jwt_secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# Import models
from models.user import User
from models.contact import Contact
from models.order import Order
from models.part import Part
from models.schedule import Schedule
from models.shop import Shop

# Import and register blueprints
from routes.auth import auth_bp
from routes.contacts import contacts_bp
from routes.orders import orders_bp
from routes.parts import parts_bp
from routes.schedule import schedule_bp
from routes.shop import shop_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(contacts_bp, url_prefix='/api/contacts')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(parts_bp, url_prefix='/api/parts')
app.register_blueprint(schedule_bp, url_prefix='/api/schedule')
app.register_blueprint(shop_bp, url_prefix='/api/shop')

# Home page route
@app.route('/')
def home():
    # Check if request wants JSON (API client) or HTML (browser)
    if request.headers.get('Accept') and 'application/json' in request.headers.get('Accept'):
        return jsonify({
            'message': 'Welcome to AutoShop Management API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth/*',
                'contacts': '/api/contacts/*',
                'orders': '/api/orders/*',
                'parts': '/api/parts/*',
                'schedule': '/api/schedule/*',
                'shop': '/api/shop/*'
            },
            'frontend': 'React app should be served separately on port 3000',
            'documentation': 'See README.md for full API documentation'
        })
    
    # Return HTML for browser requests
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AutoShop Management API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                line-height: 1.6;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c5282; margin-bottom: 0.5rem; }
            h2 { color: #2d3748; margin-top: 2rem; }
            .status { 
                display: inline-block;
                background: #48bb78;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 4px;
                font-size: 0.875rem;
                margin-left: 1rem;
            }
            .endpoint {
                background: #edf2f7;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                margin: 0.5rem 0;
                font-family: monospace;
            }
            .note {
                background: #bee3f8;
                border-left: 4px solid #3182ce;
                padding: 1rem;
                margin: 1rem 0;
            }
            .button {
                display: inline-block;
                background: #3182ce;
                color: white;
                padding: 0.75rem 1.5rem;
                text-decoration: none;
                border-radius: 4px;
                margin: 0.5rem 0.5rem 0.5rem 0;
            }
            .button:hover { background: #2c5282; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 AutoShop Management API <span class="status">Running</span></h1>
            <p><strong>Bluez PowerHouse Management System</strong></p>
            <p>Flask/Python backend API for automotive repair shop management.</p>
            
            <h2>📡 Available Endpoints</h2>
            <div class="endpoint">GET /api/health - Health check</div>
            <div class="endpoint">POST /api/auth/register - Register user</div>
            <div class="endpoint">POST /api/auth/login - User login</div>
            <div class="endpoint">GET /api/contacts - List contacts</div>
            <div class="endpoint">GET /api/parts - List parts</div>
            <div class="endpoint">GET /api/orders - List orders</div>
            <div class="endpoint">GET /api/schedule - List schedules</div>
            <div class="endpoint">GET /api/shop/info - Shop information</div>
            
            <div class="note">
                <strong>📱 Frontend Application:</strong><br>
                This is the backend API server. The React frontend should be running separately on port 3000.
                <br><br>
                To start the frontend:
                <code>cd ../client && npm start</code>
            </div>
            
            <h2>🔗 Quick Links</h2>
            <a href="/api/health" class="button">Health Check</a>
            <a href="http://localhost:3000" class="button">Frontend App</a>
            
            <h2>📚 Documentation</h2>
            <p>See <code>README.md</code> for complete API documentation and setup instructions.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'OK', 'message': 'AutoShop Management API is running'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Something went wrong!'}), 500

# Initialize scheduler for background tasks
def update_shipping_statuses():
    """Background task to update shipping statuses"""
    with app.app_context():
        print('Running scheduled task to update shipping statuses...')
        # This will be implemented in the orders service

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=update_shipping_statuses,
    trigger="interval",
    hours=6,
    id='update_shipping_statuses'
)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Start scheduler
    scheduler.start()
    
    # Run the app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown() 