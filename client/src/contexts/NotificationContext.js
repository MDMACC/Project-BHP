import React, { createContext, useContext, useState, useCallback } from 'react';
import { Bell, X, CheckCircle, AlertTriangle, Info, AlertCircle } from 'lucide-react';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      timestamp: new Date(),
      read: false,
      ...notification,
    };

    setNotifications(prev => [newNotification, ...prev.slice(0, 49)]); // Keep last 50
    setUnreadCount(prev => prev + 1);

    // Auto-remove after 5 seconds for success/info notifications
    if (['success', 'info'].includes(notification.type)) {
      setTimeout(() => {
        removeNotification(id);
      }, 5000);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => {
      const notification = prev.find(n => n.id === id);
      if (notification && !notification.read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      return prev.filter(n => n.id !== id);
    });
  }, []);

  const markAsRead = useCallback((id) => {
    setNotifications(prev => 
      prev.map(n => 
        n.id === id && !n.read 
          ? { ...n, read: true }
          : n
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => 
      prev.map(n => ({ ...n, read: true }))
    );
    setUnreadCount(0);
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
    setUnreadCount(0);
  }, []);

  // Predefined notification types
  const notify = {
    success: (message, title = 'Success') => 
      addNotification({ type: 'success', title, message }),
    
    error: (message, title = 'Error') => 
      addNotification({ type: 'error', title, message }),
    
    warning: (message, title = 'Warning') => 
      addNotification({ type: 'warning', title, message }),
    
    info: (message, title = 'Info') => 
      addNotification({ type: 'info', title, message }),
    
    urgent: (message, title = 'Urgent') => 
      addNotification({ type: 'urgent', title, message }),
  };

  const value = {
    notifications,
    unreadCount,
    addNotification,
    removeNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    notify,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

// Notification Icon Component
export const NotificationIcon = ({ type, className = "w-5 h-5" }) => {
  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
    urgent: Bell,
  };

  const Icon = icons[type] || Info;
  const colors = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500',
    urgent: 'text-red-600',
  };

  return <Icon className={`${className} ${colors[type] || colors.info}`} />;
};

// Notification Item Component
export const NotificationItem = ({ notification, onRemove, onMarkAsRead }) => {
  const { id, type, title, message, timestamp, read } = notification;

  return (
    <div className={`p-4 border-l-4 ${
      read ? 'bg-gray-50' : 'bg-white'
    } ${
      type === 'success' ? 'border-green-400' :
      type === 'error' ? 'border-red-400' :
      type === 'warning' ? 'border-yellow-400' :
      type === 'urgent' ? 'border-red-600' :
      'border-blue-400'
    }`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <NotificationIcon type={type} />
          <div className="flex-1 min-w-0">
            <h4 className={`text-sm font-medium ${
              read ? 'text-gray-500' : 'text-gray-900'
            }`}>
              {title}
            </h4>
            <p className={`text-sm ${
              read ? 'text-gray-400' : 'text-gray-600'
            }`}>
              {message}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {timestamp.toLocaleTimeString()}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {!read && (
            <button
              onClick={() => onMarkAsRead(id)}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Mark read
            </button>
          )}
          <button
            onClick={() => onRemove(id)}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotificationProvider;
