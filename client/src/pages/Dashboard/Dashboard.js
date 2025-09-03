import React from 'react';
import { useQuery } from 'react-query';
import { 
  Package, 
  ShoppingCart, 
  Users, 
  Calendar,
  TrendingUp,
  AlertTriangle,
  Clock,
  CheckCircle
} from 'lucide-react';
import { ordersAPI, scheduleAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import CountdownTimer from '../../components/UI/CountdownTimer';
import StatusBadge from '../../components/UI/StatusBadge';

const Dashboard = () => {
  // Fetch dashboard data
  const { data: orders, isLoading: ordersLoading } = useQuery(
    'dashboard-orders',
    () => ordersAPI.getAll({ limit: 5 }),
    { select: (data) => data.data.orders }
  );



  const { data: urgentOrders, isLoading: urgentLoading } = useQuery(
    'urgent-orders',
    () => ordersAPI.getUrgent(),
    { select: (data) => data.data }
  );

  const { data: todaySchedule, isLoading: scheduleLoading } = useQuery(
    'today-schedule',
    () => scheduleAPI.getByDate(new Date().toISOString().split('T')[0]),
    { select: (data) => data.data }
  );

  const stats = [
    {
      name: 'Total Parts',
      value: '1,234',
      change: '+12%',
      changeType: 'positive',
      icon: Package,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Orders',
      value: '23',
      change: '+5%',
      changeType: 'positive',
      icon: ShoppingCart,
      color: 'bg-green-500',
    },
    {
      name: 'Today\'s Appointments',
      value: '8',
      change: '-2%',
      changeType: 'negative',
      icon: Calendar,
      color: 'bg-purple-500',
    },
    {
      name: 'Total Contacts',
      value: '156',
      change: '+8%',
      changeType: 'positive',
      icon: Users,
      color: 'bg-orange-500',
    },
  ];

  if (ordersLoading || urgentLoading || scheduleLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back! Here's what's happening at your shop today.
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="card-body">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`w-8 h-8 ${stat.color} rounded-md flex items-center justify-center`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {stat.value}
                        </div>
                        <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                          stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          <TrendingUp className="self-center flex-shrink-0 h-4 w-4" />
                          <span className="sr-only">
                            {stat.changeType === 'positive' ? 'Increased' : 'Decreased'} by
                          </span>
                          {stat.change}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Urgent Orders */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-warning-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Urgent Orders</h3>
          </div>
        </div>
        <div className="card-body">
          {urgentOrders && urgentOrders.length > 0 ? (
            <div className="space-y-3">
              {urgentOrders.slice(0, 5).map((order) => (
                <div key={order._id} className="flex items-center justify-between p-3 bg-warning-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Order #{order.orderNumber}
                    </p>
                    <p className="text-xs text-gray-500">
                      {order.supplier?.name}
                    </p>
                  </div>
                  <CountdownTimer endTime={order.countdownEndTime} />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6">
              <CheckCircle className="mx-auto h-12 w-12 text-green-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No urgent orders</h3>
              <p className="mt-1 text-sm text-gray-500">
                All orders are on track for delivery.
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Orders */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <ShoppingCart className="w-5 h-5 text-primary-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Recent Orders</h3>
            </div>
          </div>
          <div className="card-body">
            {orders && orders.length > 0 ? (
              <div className="space-y-3">
                {orders.map((order) => (
                  <div key={order._id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Order #{order.orderNumber}
                      </p>
                      <p className="text-xs text-gray-500">
                        {order.supplier?.name} • ${order.totalAmount}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <StatusBadge status={order.status} type="order" />
                      {order.countdownEndTime && (
                        <CountdownTimer endTime={order.countdownEndTime} />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <ShoppingCart className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No recent orders</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Orders will appear here once created.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Today's Schedule */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <Calendar className="w-5 h-5 text-purple-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Today's Schedule</h3>
            </div>
          </div>
          <div className="card-body">
            {todaySchedule && todaySchedule.length > 0 ? (
              <div className="space-y-3">
                {todaySchedule.slice(0, 5).map((appointment) => (
                  <div key={appointment._id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {appointment.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(appointment.startTime).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })} • {appointment.customer?.name || 'No customer'}
                      </p>
                    </div>
                    <StatusBadge status={appointment.status} type="schedule" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No appointments today</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Schedule appointments to see them here.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
