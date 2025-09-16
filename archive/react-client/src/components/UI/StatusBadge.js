import React from 'react';

const StatusBadge = ({ status, type = 'default', className = '' }) => {
  const getStatusConfig = () => {
    switch (type) {
      case 'order':
        switch (status) {
          case 'pending':
            return { label: 'Pending', className: 'badge-warning' };
          case 'confirmed':
            return { label: 'Confirmed', className: 'badge-info' };
          case 'shipped':
            return { label: 'Shipped', className: 'badge-primary' };
          case 'delivered':
            return { label: 'Delivered', className: 'badge-success' };
          case 'cancelled':
            return { label: 'Cancelled', className: 'badge-danger' };
          default:
            return { label: status, className: 'badge-gray' };
        }
      
      case 'progress':
        switch (status) {
          case 'not_started':
            return { label: 'Not Started', className: 'badge-gray' };
          case 'waiting_on_parts':
            return { label: 'Waiting on Parts', className: 'badge-warning' };
          case 'started':
            return { label: 'Started', className: 'badge-info' };
          case 'finished':
            return { label: 'Finished', className: 'badge-success' };
          case 'waiting_for_pickup':
            return { label: 'Waiting for Pickup', className: 'badge-primary' };
          default:
            return { label: status, className: 'badge-gray' };
        }
      
      case 'schedule':
        switch (status) {
          case 'scheduled':
            return { label: 'Scheduled', className: 'badge-info' };
          case 'in_progress':
            return { label: 'In Progress', className: 'badge-warning' };
          case 'completed':
            return { label: 'Completed', className: 'badge-success' };
          case 'cancelled':
            return { label: 'Cancelled', className: 'badge-danger' };
          case 'no_show':
            return { label: 'No Show', className: 'badge-gray' };
          default:
            return { label: status, className: 'badge-gray' };
        }
      
      case 'stock':
        switch (status) {
          case 'in_stock':
            return { label: 'In Stock', className: 'badge-success' };
          case 'low_stock':
            return { label: 'Low Stock', className: 'badge-warning' };
          case 'out_of_stock':
            return { label: 'Out of Stock', className: 'badge-danger' };
          default:
            return { label: status, className: 'badge-gray' };
        }
      
      case 'contact':
        switch (status) {
          case 'supplier':
            return { label: 'Supplier', className: 'badge-info' };
          case 'customer':
            return { label: 'Customer', className: 'badge-success' };
          case 'vendor':
            return { label: 'Vendor', className: 'badge-warning' };
          case 'distributor':
            return { label: 'Distributor', className: 'badge-primary' };
          default:
            return { label: status, className: 'badge-gray' };
        }
      
      default:
        return { label: status, className: 'badge-gray' };
    }
  };

  const config = getStatusConfig();

  return (
    <span className={`badge ${config.className} ${className}`}>
      {config.label}
    </span>
  );
};

export default StatusBadge;
