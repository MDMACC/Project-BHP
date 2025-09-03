# AutoShop Management - Frontend

A modern React-based frontend for the AutoShop Management Software, built with React 18, Tailwind CSS, and React Query.

## Features

- **Modern UI/UX** - Clean, responsive design with Tailwind CSS
- **Real-time Updates** - Live countdown timers for shipping tracking
- **Role-based Access** - Different permissions for admin, manager, and employee roles
- **Interactive Dashboard** - Overview of inventory, orders, and appointments
- **Advanced Filtering** - Search and filter across all modules
- **Mobile Responsive** - Works seamlessly on desktop and mobile devices

## Tech Stack

- **React 18** - Modern React with hooks and functional components
- **React Router** - Client-side routing
- **React Query** - Server state management and caching
- **React Hook Form** - Form handling and validation
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful, customizable icons
- **React Hot Toast** - Elegant notifications
- **Axios** - HTTP client for API requests

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API running on port 5000

### Installation

1. **Navigate to client directory**
   ```bash
   cd client
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

The application will open at `http://localhost:3000`

### Environment Variables

Create a `.env` file in the client directory:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

## Project Structure

```
client/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Layout/        # Layout components (Header, Sidebar)
│   │   └── UI/            # Generic UI components
│   ├── contexts/          # React contexts (Auth)
│   ├── pages/             # Page components
│   │   ├── Auth/          # Authentication pages
│   │   ├── Dashboard/     # Dashboard page
│   │   ├── Parts/         # Parts management
│   │   ├── Orders/        # Order management
│   │   ├── Contacts/      # Contact management
│   │   ├── Schedule/      # Scheduling
│   │   ├── Inventory/     # Inventory overview
│   │   └── Shipping/      # Shipping tracking
│   ├── services/          # API services
│   ├── App.js             # Main app component
│   ├── index.js           # App entry point
│   └── index.css          # Global styles
├── package.json
├── tailwind.config.js     # Tailwind configuration
└── README.md
```

## Key Components

### Authentication
- JWT-based authentication
- Role-based access control
- Protected routes
- Auto-logout on token expiry

### Dashboard
- Real-time statistics
- Urgent orders with countdown timers
- Low stock alerts
- Recent activity overview

### Parts Management
- CRUD operations for parts
- Category-based organization
- Stock level tracking
- Supplier relationships

### Order Tracking
- Custom countdown timers
- Shipping status updates
- Overdue order alerts
- Real-time countdown display

### Contact Management
- Supplier, customer, and vendor management
- Contact information storage
- Rating system
- Business details tracking

### Scheduling
- Appointment booking
- Technician assignment
- Customer and vehicle information
- Parts requirements tracking

### Inventory Overview
- Stock level monitoring
- Category-based organization
- Low stock alerts
- Total inventory value

### Shipping Tracking
- Urgent orders (less than 24 hours)
- Overdue orders
- Real-time countdown timers
- Package status updates

## Customization

### Styling
The application uses Tailwind CSS with a custom configuration. You can modify colors, spacing, and other design tokens in `tailwind.config.js`.

### API Integration
API calls are centralized in the `services/api.js` file. Update the base URL and add new endpoints as needed.

### Components
All components are modular and reusable. You can easily customize or extend them for your specific needs.

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details
