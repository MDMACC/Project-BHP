# Bluez PowerHouse Auto Repair - Demo Instructions

## Two Portal System Overview

I've successfully built out two distinct sections for your auto shop management system:

### 1. Customer Portal (Main Route: `/`)
- **URL**: `http://localhost:5000/`
- **Purpose**: Public-facing website for customers
- **Features**:
  - Beautiful landing page with professional design
  - Service showcase with pricing
  - Contact information and service request form
  - Company information and credentials
  - Responsive design with modern UI/UX
  - Call-to-action buttons for scheduling and contact

### 2. Admin Portal (Route: `/admin`)
- **URL**: `http://localhost:5000/admin`
- **Purpose**: Staff management interface
- **Features**:
  - Secure login required (redirects to login if not authenticated)
  - Role-based access control (admin/manager only)
  - Comprehensive dashboard with:
    - Real-time inventory statistics
    - Stock alerts (out of stock & low stock warnings)
    - Quick action buttons for all management functions
    - System status monitoring
    - Recent activity feed
    - Admin tools section

## How to Access Each Section

### Customer Portal Access:
1. Navigate to `http://localhost:5000/`
2. No login required - public access
3. Features a professional auto repair website with services, pricing, and contact information

### Admin Portal Access:
1. Navigate to `http://localhost:5000/admin`
2. System will redirect to login page if not authenticated
3. Use demo credentials:
   - **Admin**: admin@autoshop.com / admin123
   - **Manager**: manager@autoshop.com / manager123
4. After login, you'll be redirected to the admin dashboard

## Key Features Implemented

### Customer Portal Features:
- ✅ Professional hero section with company branding
- ✅ Services showcase with 6 main service categories
- ✅ Pricing information for each service
- ✅ About section highlighting company strengths
- ✅ Contact section with form and business information
- ✅ Mobile-responsive design
- ✅ Modern gradient styling and animations
- ✅ Staff portal access button in header

### Admin Portal Features:
- ✅ Role-based authentication (admin/manager access only)
- ✅ Real-time dashboard with key metrics
- ✅ Inventory alerts system
- ✅ Quick action buttons for all management functions
- ✅ System status monitoring
- ✅ Recent activity tracking
- ✅ Admin tools section
- ✅ Consistent branding with customer portal

## Technical Implementation

### Route Structure:
- `/` - Customer home page (public access)
- `/admin` - Redirects to admin dashboard or login
- `/admin/dashboard` - Admin dashboard (authenticated access only)
- `/login` - Authentication page
- All existing management routes remain functional

### Security Features:
- Role-based access control
- Session management
- Secure password handling
- Admin privilege verification
- Automatic redirects for unauthorized access

### UI/UX Design:
- Consistent branding across both portals
- Modern gradient design system
- Professional color scheme (blues and metallics)
- Responsive layout for all devices
- Smooth animations and transitions
- Accessible design patterns

## Demo Flow

1. **Start at Customer Portal** (`/`):
   - View the professional landing page
   - Browse services and pricing
   - Use the contact form
   - Click "Staff Portal" to access admin section

2. **Access Admin Portal** (`/admin`):
   - Login with demo credentials
   - Explore the comprehensive dashboard
   - View inventory alerts and statistics
   - Use quick action buttons to access management features

This implementation provides a complete dual-portal system that serves both customer-facing needs and internal management requirements while maintaining security and professional presentation.
