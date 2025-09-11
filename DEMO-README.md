# Bluez PowerHouse Management System - HTML Demo

This is a standalone HTML demo of the Bluez PowerHouse Management System that can be opened on both Mac and Windows without requiring any server setup.

## Quick Start

### For Mac Users:
```bash
./open-demo.sh
```

### For Windows Users:
```cmd
open-demo.bat
```

### Manual Opening:
Simply double-click on `demo.html` to open it in your default web browser.

## Demo Features

### 🏠 Dashboard
- **Real-time Statistics**: Total parts, active orders, today's appointments, and contacts
- **Urgent Orders**: Orders with countdown timers showing delivery urgency
- **Inventory Alerts**: Out-of-stock and low-stock part notifications
- **Recent Activity**: Latest orders and today's schedule

### 🧩 System Modules
- **Parts Management**: Track inventory, pricing, and stock levels
- **Order Management**: Create and track orders with custom countdown timers
- **Contact Management**: Manage suppliers, customers, and vendors
- **Scheduling**: Book appointments and track technician schedules
- **Inventory**: Monitor stock levels and reorder points
- **Shipping**: Track package delivery and status

### 🎨 Visual Features
- **Modern UI**: Clean, professional interface with Bluez PowerHouse branding
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Interactive Elements**: Hover effects, animated countdown timers, and status badges
- **Real-time Updates**: Countdown timers update automatically

### 🔧 Technical Features
- **Cross-Platform**: Works on Mac, Windows, and Linux
- **No Dependencies**: Pure HTML, CSS, and JavaScript
- **Offline Capable**: No internet connection required
- **Modern Browsers**: Compatible with Chrome, Firefox, Safari, and Edge

## Sample Data

The demo includes realistic sample data:

### Orders
- Order #BHP-2024-001: AutoZone Supply Co. - $1,247.50 (Urgent - 2h 15m)
- Order #BHP-2024-002: NAPA Auto Parts - $892.30 (Shipped - 1d 4h)
- Order #BHP-2024-003: O'Reilly Auto Parts - $2,156.80 (Delivered)

### Inventory Alerts
- 3 parts out of stock
- 7 parts below minimum stock level

### Today's Schedule
- 9:00 AM: Brake Pad Replacement (Sarah Johnson) - Confirmed
- 11:30 AM: Oil Change & Filter (Mike Rodriguez) - Confirmed
- 2:00 PM: Transmission Service (Lisa Chen) - Pending

### Statistics
- 1,247 total parts ($45,230 value)
- 23 active orders (8 pending)
- 7 today's appointments (5 confirmed)
- 156 total contacts (42 suppliers)

## Color Scheme

The demo uses the official Bluez PowerHouse color palette:
- **Primary Blue**: #4f46e5 (Bluez-600)
- **Metallic Gray**: #64748b (Metallic-500)
- **Success Green**: #22c55e (Success-500)
- **Warning Yellow**: #f59e0b (Warning-500)
- **Danger Red**: #ef4444 (Danger-500)

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## File Structure

```
Project-BHP/
├── demo.html              # Main demo file
├── open-demo.sh          # Mac/Linux launcher script
├── open-demo.bat         # Windows launcher script
└── DEMO-README.md        # This file
```

## Customization

The demo is built with vanilla HTML, CSS, and JavaScript, making it easy to customize:

- **Colors**: Modify the Tailwind CSS color configuration
- **Data**: Update the sample data in the HTML
- **Layout**: Adjust the grid and component structure
- **Functionality**: Add more interactive features in the JavaScript

## Notes

- This is a **static demo** and does not connect to any backend services
- All data is simulated and resets when the page is refreshed
- The countdown timers are for demonstration purposes only
- Navigation between modules is simulated (clicking shows visual feedback)

## Support

For questions about the full system implementation, refer to the main README.md file in the project root.

---

**Bluez PowerHouse**  
250 W Spazier Ave 101  
Burbank, CA 91502
