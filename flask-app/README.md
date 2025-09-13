# AutoShop Management System - Flask Version

This is a Flask-based conversion of the original Node.js/Express AutoShop Management System. The application provides comprehensive management tools for automotive repair shops including inventory management, order tracking, scheduling, and customer management.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation & Setup

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd Project-BHP
   ```

2. **Run the setup script** (recommended)
   
   **For Windows (PowerShell):**
   ```powershell
   .\start-server.ps1
   ```
   
   **For Windows/Linux/macOS (Python):**
   ```bash
   python start-server.py
   ```

3. **Manual setup** (alternative)
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env file with your configuration
   
   # Run the application
   python app.py
   ```

## 🏗️ Architecture

### Technology Stack
- **Backend Framework**: Flask 2.3.3
- **Database**: SQLite (default) / PostgreSQL (configurable)
- **ORM**: SQLAlchemy
- **Authentication**: JWT with Flask-JWT-Extended
- **API Validation**: Marshmallow
- **Task Scheduling**: APScheduler
- **CORS**: Flask-CORS

### Project Structure
```
Project-BHP/
├── app.py                 # Main Flask application
├── database.py            # Database configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── models/               # SQLAlchemy models
│   ├── user.py
│   ├── contact.py
│   ├── order.py
│   ├── part.py
│   ├── schedule.py
│   └── shop.py
├── routes/               # Flask blueprints (API routes)
│   ├── auth.py
│   ├── contacts.py
│   ├── orders.py
│   ├── parts.py
│   ├── schedule.py
│   └── shop.py
├── middleware/           # Authentication middleware
│   └── auth.py
├── client/               # React frontend (unchanged)
└── migrations/           # Database migrations (auto-generated)
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory with the following variables:

```env
PORT=5000
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_key_here
DATABASE_URL=sqlite:///autoshop_management.db
```

### Database Configuration
- **SQLite** (default): `sqlite:///autoshop_management.db`
- **PostgreSQL**: `postgresql://username:password@localhost/dbname`
- **MySQL**: `mysql://username:password@localhost/dbname`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Contacts
- `GET /api/contacts` - List contacts with pagination and filtering
- `POST /api/contacts` - Create new contact
- `GET /api/contacts/<id>` - Get specific contact
- `PUT /api/contacts/<id>` - Update contact
- `DELETE /api/contacts/<id>` - Delete contact (soft delete)
- `GET /api/contacts/suppliers` - Get all suppliers

### Parts
- `GET /api/parts` - List parts with filtering and pagination
- `POST /api/parts` - Create new part
- `GET /api/parts/<id>` - Get specific part
- `PUT /api/parts/<id>` - Update part
- `DELETE /api/parts/<id>` - Delete part

### Orders
- `GET /api/orders` - List orders with filtering and pagination
- `POST /api/orders` - Create new order
- `GET /api/orders/<id>` - Get specific order
- `PUT /api/orders/<id>` - Update order
- `DELETE /api/orders/<id>` - Delete order

### Schedule
- `GET /api/schedule` - List schedules with filtering
- `POST /api/schedule` - Create new schedule
- `GET /api/schedule/<id>` - Get specific schedule
- `PUT /api/schedule/<id>` - Update schedule
- `DELETE /api/schedule/<id>` - Delete schedule

### Shop
- `GET /api/shop/info` - Get shop information
- `PUT /api/shop/info` - Update shop information (admin only)

### Health Check
- `GET /api/health` - API health check

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### User Roles
- **admin**: Full access to all features
- **manager**: Access to most features, limited admin functions
- **employee**: Basic access to daily operations

## 🗄️ Database Models

### User
- Authentication and user management
- Role-based access control
- Password hashing with bcrypt

### Contact
- Suppliers, customers, vendors, and distributors
- Contact information and business details
- Address and payment terms

### Part
- Inventory management
- Pricing and cost tracking
- Stock levels and locations
- Supplier relationships

### Order
- Purchase orders and tracking
- Shipping information
- Countdown timers for delivery
- Custom and catalog parts

### Schedule
- Appointments and maintenance scheduling
- Technician assignments
- Cost estimation (labor and parts)
- Customer and vehicle information

### Shop
- Shop configuration and settings
- Business hours and contact info
- System-wide preferences

## 🚀 Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Database Migrations
```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

### Adding New Features
1. Create/update models in `models/`
2. Create/update routes in `routes/`
3. Add validation schemas using Marshmallow
4. Update API documentation

## 🔄 Migration from Node.js

### Key Changes Made
1. **Express.js → Flask**: Complete framework migration
2. **Mongoose → SQLAlchemy**: Database ORM change
3. **MongoDB → SQLite/PostgreSQL**: Database system change
4. **express-validator → Marshmallow**: Validation library change
5. **node-cron → APScheduler**: Task scheduling change
6. **JWT handling**: Migrated to Flask-JWT-Extended

### Data Migration
If migrating from the Node.js version with existing data:
1. Export data from MongoDB
2. Transform data structure to match SQLAlchemy models
3. Import data using Flask-Migrate or custom scripts

## 🧪 Testing

### Manual Testing
Use the health check endpoint to verify the API is running:
```bash
curl http://localhost:5000/api/health
```

### API Testing
Use tools like Postman, curl, or HTTPie to test endpoints:
```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"password123","role":"admin"}'
```

## 🚀 Production Deployment

### Using Gunicorn (Recommended)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables for Production
```env
FLASK_ENV=production
SECRET_KEY=your_production_secret_key
JWT_SECRET=your_production_jwt_secret
DATABASE_URL=postgresql://user:pass@localhost/autoshop_prod
```

## 📝 License

MIT License - see the original project license for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the API health endpoint
2. Review the logs for error messages
3. Verify environment configuration
4. Check database connectivity

---

**Note**: This Flask version maintains API compatibility with the original Node.js frontend, so the React client should work without modifications. 