import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Home, 
  Package, 
  ShoppingCart, 
  Users, 
  Calendar, 
  BarChart3, 
  Truck,
  X
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Logo from '../UI/Logo';

const Sidebar = ({ isOpen, onClose }) => {
  const { isManager } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Parts', href: '/parts', icon: Package },
    { name: 'Orders', href: '/orders', icon: ShoppingCart },
    { name: 'Contacts', href: '/contacts', icon: Users },
    { name: 'Schedule', href: '/schedule', icon: Calendar },
    { name: 'Inventory', href: '/inventory', icon: BarChart3 },
    { name: 'Shipping', href: '/shipping', icon: Truck },
  ];

  const isActive = (href) => {
    return location.pathname === href || location.pathname.startsWith(href + '/');
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={onClose}
        >
          <div className="absolute inset-0 bg-gray-600 opacity-75"></div>
        </div>
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white/95 backdrop-blur-sm shadow-xl border-r border-metallic-200/50 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-metallic-200/50">
          <Logo size="sm" showText={false} />
          
          <button
            type="button"
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            onClick={onClose}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                      isActive
                        ? 'sidebar-link-active'
                        : 'sidebar-link-inactive'
                    }`
                  }
                  onClick={onClose}
                >
                  <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  {item.name}
                </NavLink>
              );
            })}
          </div>
        </nav>

        {/* User info at bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-primary-600">
                {isManager ? 'M' : 'E'}
              </span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">
                {isManager ? 'Manager' : 'Employee'}
              </p>
              <p className="text-xs text-gray-500">Access Level</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
