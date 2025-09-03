# Bluez PowerHouse Management Software

A comprehensive management system for automotive repair shops, featuring inventory management, order tracking, customer scheduling, and supplier contact management.

**Bluez PowerHouse**  
250 W Spazier Ave 101  
Burbank, CA 91502

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

## Quick Start

### Prerequisites
- Node.js (v14 or higher)
- MongoDB (v4.4 or higher)
- npm or yarn

### Backend Setup

1. **Install backend dependencies**
   ```bash
   npm install
   ```

2. **Environment Setup**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/autoshop_management
   JWT_SECRET=your_jwt_secret_key_here
   NODE_ENV=development
   ```

3. **Start MongoDB**
   ```bash
   # Using MongoDB service
   sudo systemctl start mongod
   
   # Or using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

4. **Start the backend**
   ```bash
   # Development mode
   npm run dev
   
   # Production mode
   npm start
   ```

The API will be available at `http://localhost:5000`

### Demo Credentials

Use these credentials to test the application:

- **Admin:** admin@autoshop.com / admin123
- **Manager:** manager@autoshop.com / manager123  
- **Employee:** employee@autoshop.com / employee123

### Frontend Setup

1. **Navigate to client directory**
   ```bash
   cd client
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Start the frontend**
   ```bash
   npm start
   ```

The application will open at `http://localhost:3000`

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
- `GET /api/parts/inventory/low-stock` - Get low stock parts
- `POST /api/parts/:id/restock` - Restock part

### Order Management
- `GET /api/orders` - Get all orders
- `GET /api/orders/:id` - Get single order
- `POST /api/orders` - Create new order
- `PUT /api/orders/:id` - Update order
- `DELETE /api/orders/:id` - Cancel order
- `GET /api/orders/shipping/overdue` - Get overdue orders
- `GET /api/orders/shipping/urgent` - Get urgent orders
- `POST /api/orders/:id/receive` - Mark order as received

### Shop Management
- `GET /api/shop` - Get shop information
- `PUT /api/shop` - Update shop information

### Contact Management
- `GET /api/contacts` - Get all contacts
- `GET /api/contacts/:id` - Get single contact
- `POST /api/contacts` - Create new contact
- `PUT /api/contacts/:id` - Update contact
- `DELETE /api/contacts/:id` - Delete contact
- `GET /api/contacts/type/suppliers` - Get suppliers
- `GET /api/contacts/type/customers` - Get customers
- `POST /api/contacts/:id/rate` - Rate contact

### Scheduling
- `GET /api/schedule` - Get all schedules
- `GET /api/schedule/:id` - Get single schedule
- `POST /api/schedule` - Create new schedule
- `PUT /api/schedule/:id` - Update schedule
- `DELETE /api/schedule/:id` - Cancel schedule
- `GET /api/schedule/calendar/:date` - Get schedule for date
- `GET /api/schedule/technician/:id` - Get technician schedule
- `POST /api/schedule/:id/start` - Start appointment
- `POST /api/schedule/:id/complete` - Complete appointment

## Database Models

### User
- Authentication and authorization
- Role-based access (admin, manager, employee)

### Part
- Inventory tracking with stock levels
- Pricing and cost management
- Supplier relationships
- Vehicle compatibility

### Order
- Order management with custom countdown timers
- Shipping tracking
- Status management (pending, confirmed, shipped, delivered)
- Progress tracking (not_started, waiting_on_parts, started, finished, waiting_for_pickup)

### Contact
- Supplier, customer, and vendor management
- Contact information and business details
- Rating system

### Schedule
- Appointment scheduling
- Technician assignment
- Customer and vehicle information
- Parts requirements

### Shop
- Shop information management
- Business address and contact details
- Settings and configuration

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

### Project Structure
```
Project-BHP/
├── models/          # Database models
├── routes/          # API routes
├── middleware/      # Authentication middleware
├── server.js        # Main server file
├── package.json     # Dependencies
└── README.md        # This file
```

### Adding New Features
1. Create model in `models/` directory
2. Add routes in `routes/` directory
3. Update server.js to include new routes
4. Add authentication middleware as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
