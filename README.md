# Bluez PowerHouse Management Software

A comprehensive management system for automotive repair shops, featuring inventory management, order tracking, customer scheduling, and supplier contact management.

**Bluez PowerHouse**  
250 W Spazier Ave 101  
Burbank, CA 91502

**🚀 Now Available in Two Versions:**
- **Flask/Python Version** (Recommended) - Located in `flask-app/`
- **Node.js Version** (Archived) - Located in `archive/nodejs-original/`

## Features

### Backend Features
- **User Authentication & Authorization** - JWT-based auth with role-based access control
- **Parts Inventory Management** - Track parts, pricing, stock levels, and suppliers
- **Order Management** - Create and track orders with custom countdown timers
- **Shipping Tracking** - Monitor package delivery with real-time countdown
- **Contact Management** - Manage suppliers, customers, and vendors
- **Scheduling System** - Book appointments and track technician schedules

### Frontend Features
- Modern React-based dashboard with Bluez PowerHouse branding
- Custom B.P.H. logo component with automotive styling
- Dark blue metallic theme matching the shop's visual identity
- Real-time inventory tracking
- Interactive scheduling calendar
- Order tracking with countdown timers
- Contact management interface
- Responsive design for mobile and desktop

## 🐍 Flask Version (Recommended)

The Flask version is the current recommended implementation with modern Python technologies.

### Technology Stack
- **Flask 2.3.3** web framework
- **SQLAlchemy** ORM with SQLite/PostgreSQL
- **JWT** authentication with Flask-JWT-Extended
- **Marshmallow** for API validation
- **APScheduler** for background tasks
- **React 18** frontend (unchanged)

### Quick Start
```bash
cd flask-app
python start-server.py
# or for Windows PowerShell
.\start-server.ps1
```

📖 **Full Documentation**: See `flask-app/README.md` for detailed setup instructions.

## 🟢 Node.js Version (Archived)

The original Node.js implementation has been moved to `archive/nodejs-original/` for reference.

### Technology Stack (Archived)
- **Node.js** with Express.js framework
- **MongoDB** with Mongoose ODM
- **JWT** authentication
- **Express-validator** for input validation
- **Node-cron** for scheduled tasks

### Access Archived Version
```bash
cd archive/nodejs-original
npm install
npm start
```

📖 **Archive Documentation**: See `archive/README.md` for restoration instructions.

## Project Structure

```
Project-BHP/
├── flask-app/                    # Flask/Python Implementation (Recommended)
│   ├── app.py                   # Main Flask application
│   ├── database.py              # Database configuration
│   ├── requirements.txt         # Python dependencies
│   ├── models/                  # SQLAlchemy models
│   ├── routes/                  # Flask API routes
│   ├── middleware/              # Authentication middleware
│   ├── start-server.py          # Python startup script
│   ├── start-server.ps1         # PowerShell startup script
│   └── README.md               # Flask documentation
├── client/                      # React Frontend (Works with both versions)
│   ├── src/                    # React source code
│   ├── public/                 # Static assets
│   └── package.json           # Frontend dependencies
├── archive/                     # Archived Code
│   ├── nodejs-original/        # Original Node.js implementation
│   │   ├── server.js           # Original Express server
│   │   ├── package.json        # Node.js dependencies
│   │   ├── models/             # Mongoose models
│   │   ├── routes/             # Express routes
│   │   └── middleware/         # Express middleware
│   └── README.md              # Archive documentation
├── demo.html                   # Demo page
├── DEMO-README.md             # Demo instructions
└── README.md                  # This file
```

## Demo Credentials

Use these credentials to test the application:

- **Admin:** admin@autoshop.com / admin123
- **Manager:** manager@autoshop.com / manager123  
- **Employee:** employee@autoshop.com / employee123

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Parts Management
- `GET /api/parts` - Get all parts (with filtering)
- `GET /api/parts/:id` - Get single part
- `POST /api/parts` - Create new part
- `PUT /api/parts/:id` - Update part
- `DELETE /api/parts/:id` - Delete part

### Order Management
- `GET /api/orders` - Get all orders
- `GET /api/orders/:id` - Get single order
- `POST /api/orders` - Create new order
- `PUT /api/orders/:id` - Update order
- `DELETE /api/orders/:id` - Cancel order

### Contact Management
- `GET /api/contacts` - Get all contacts
- `GET /api/contacts/:id` - Get single contact
- `POST /api/contacts` - Create new contact
- `PUT /api/contacts/:id` - Update contact
- `DELETE /api/contacts/:id` - Delete contact

### Scheduling
- `GET /api/schedule` - Get all schedules
- `GET /api/schedule/:id` - Get single schedule
- `POST /api/schedule` - Create new schedule
- `PUT /api/schedule/:id` - Update schedule
- `DELETE /api/schedule/:id` - Cancel schedule

### Shop Management
- `GET /api/shop/info` - Get shop information
- `PUT /api/shop/info` - Update shop information

## Key Features

### Custom Countdown Timers
Orders include custom time limits (default 72 hours) with real-time countdown tracking. The system automatically categorizes orders as:
- **Normal**: More than 24 hours remaining
- **Urgent**: Less than 24 hours remaining
- **Overdue**: Past the expected delivery time

### Role-Based Access Control
- **Admin**: Full system access
- **Manager**: Can manage parts, orders, contacts, and schedules
- **Employee**: Read access with limited write permissions

## Development

### Adding New Features (Flask Version)
1. Create model in `flask-app/models/` directory
2. Add routes in `flask-app/routes/` directory
3. Add validation schemas using Marshmallow
4. Update API documentation

### Frontend Development
The React frontend is compatible with both Flask and Node.js versions:
```bash
cd client
npm install
npm start
```

## Migration

If you have data in the Node.js/MongoDB version and want to migrate to Flask:
1. Export your MongoDB data
2. Transform the data structure to match SQLAlchemy models
3. Import using Flask-Migrate or custom migration scripts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

---

**Current Version**: Flask/Python (Recommended)  
**Legacy Version**: Node.js/Express (Archived)  
**Frontend**: React 18 (Compatible with both versions)