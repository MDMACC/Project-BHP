# Bluez PowerHouse Shipping API Integration System

## Overview

The Shipping API Integration System allows you to connect and track orders from multiple automotive parts suppliers including:

- **FCP-Euro** - European car parts specialist
- **O'Reilly Auto Parts** - National auto parts retailer  
- **AutoZone** - Auto parts and accessories
- **Harbor Freight** - Tools and automotive equipment
- **Amazon** - Marketplace orders

## Features

### ✅ **Account Management**
- Secure API key storage (encrypted)
- Multiple accounts per provider
- Account status management (active/inactive)
- Last sync tracking

### ✅ **Order Tracking**
- Real-time order status updates
- Tracking number integration
- Estimated delivery dates
- Order history and details

### ✅ **Shipping Dashboard**
- Visual order status overview
- Provider-specific filtering
- Interactive tracking maps
- Delivery timeline tracking

### ✅ **API Integration**
- Modular API classes for each provider
- Automatic order synchronization
- Error handling and logging
- Rate limiting support

## Getting Started

### 1. Access the Admin Panel

Navigate to the admin section of your Bluez PowerHouse system and log in with admin or manager privileges.

### 2. Configure Accounts

1. Click on **"Accounts"** in the admin sidebar
2. Click **"Add Account"** to configure a new provider
3. Fill in the required information:
   - **Provider**: Select from the dropdown
   - **Account Name**: Descriptive name for your reference
   - **Username**: Your login username (if applicable)
   - **API Key**: Your API key from the provider
   - **API Secret**: Your API secret (if required)

### 3. Provider Setup Instructions

#### **FCP-Euro**
- Contact FCP-Euro support to request API access
- They may provide API credentials for order tracking
- Business accounts typically have better API access

#### **O'Reilly Auto Parts**
- Register for O'Reilly's B2B program
- Contact their commercial support for API documentation
- May require business verification

#### **AutoZone**
- Sign up for AutoZone's Commercial program
- Access their business portal for API credentials
- Commercial accounts get priority API access

#### **Harbor Freight**
- API access may be limited
- Check their developer documentation
- Contact support for business API access

#### **Amazon**
- Register for Amazon MWS (Marketplace Web Service) or SP-API
- Requires Professional selling account ($39.99/month)
- Complete Amazon's developer application process
- Obtain refresh token and access keys

### 4. Sync Orders

Once accounts are configured:

1. Use **"Sync"** button for individual accounts
2. Use **"Sync All"** to update all active accounts
3. Orders will appear in the **Shipping** section

## Using the Shipping Dashboard

### Order Status Overview

The dashboard shows four key metrics:
- **Ordered**: Orders placed but not yet shipped
- **Shipped**: Orders that have left the warehouse
- **In Transit**: Orders currently being delivered
- **Delivered**: Successfully completed orders

### Filtering Options

- **Provider**: Filter by specific supplier
- **Status**: Filter by order status
- **Date Range**: Filter by time period

### Tracking Features

- **Track**: View detailed tracking events
- **Map**: See delivery progress on interactive map
- **Refresh**: Update all data from providers

## Database Schema

### ShippingAccount
- Provider information and API credentials
- Account status and sync timestamps
- Encrypted API key storage

### ShippingOrder  
- Order details from providers
- Tracking numbers and carrier info
- Delivery estimates and status

### TrackingEvent
- Individual tracking updates
- Location data with coordinates
- Event timestamps and descriptions

## API Endpoints

### Account Management
- `GET /admin/accounts` - List all accounts
- `POST /admin/accounts/add` - Add new account
- `POST /admin/accounts/<id>/edit` - Edit account
- `POST /admin/accounts/<id>/sync` - Sync single account
- `POST /admin/sync-all` - Sync all accounts

### Shipping Data
- `GET /shipping` - Shipping dashboard
- `GET /api/shipping/orders/<id>/tracking` - Get tracking data

## Security Features

- **Encrypted API Keys**: All API credentials are encrypted in database
- **Role-Based Access**: Only admin/manager roles can access shipping features
- **Secure Authentication**: Flask session management with CSRF protection
- **Input Validation**: All form inputs are validated and sanitized

## Troubleshooting

### Common Issues

**Authentication Failures**
- Verify API keys are correct
- Check if provider requires IP whitelisting
- Ensure account has API access enabled

**No Orders Appearing**
- Check date range filters
- Verify account sync completed successfully
- Review logs for API errors

**Tracking Not Working**
- Ensure tracking numbers are valid
- Check if provider supports tracking API
- Verify Google Maps API key is configured

### Logs

Check the application logs for detailed error messages:
```bash
tail -f flask-app/app.log
```

### Support

For technical issues:
1. Check the application logs
2. Verify provider API documentation
3. Contact provider support for API-specific issues
4. Review Flask application error messages

## Future Enhancements

### Planned Features
- **Automated Notifications**: Email/SMS alerts for delivery updates
- **Inventory Integration**: Automatic stock updates from orders
- **Advanced Analytics**: Delivery performance metrics
- **Mobile App**: Native mobile tracking application
- **Webhook Support**: Real-time updates from providers

### API Expansion
- Additional providers (NAPA, Advance Auto Parts, etc.)
- Enhanced tracking data (weather delays, route optimization)
- Integration with shipping calculators
- Bulk order management tools

## Technical Details

### Architecture
- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: HTML/CSS with Tailwind CSS
- **Database**: SQLite (can be upgraded to PostgreSQL/MySQL)
- **Maps**: Google Maps JavaScript API
- **Security**: Werkzeug password hashing, encrypted storage

### File Structure
```
flask-app/
├── models.py              # Database models
├── shipping_apis.py       # API integration classes
├── app.py                 # Main Flask application
├── templates/admin/       # Admin HTML templates
│   ├── accounts.html      # Account management
│   ├── shipping.html      # Shipping dashboard
│   └── ...
└── static/               # CSS, JS, images
```

### Dependencies
- Flask 2.3.3 - Web framework
- SQLAlchemy 2.0.23 - Database ORM
- Requests 2.31.0 - HTTP library for API calls
- APScheduler 3.10.4 - Background task scheduling
- Flask-CORS 4.0.0 - Cross-origin resource sharing

## License

This shipping integration system is part of the Bluez PowerHouse Auto Repair Management System. All rights reserved.

---

**Need Help?** Contact your system administrator or review the application logs for troubleshooting information.
