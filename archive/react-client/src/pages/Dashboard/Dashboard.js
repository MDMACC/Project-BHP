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
import { ordersAPI, scheduleAPI, partsAPI, contactsAPI } from '../../services/api';
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

  // Fetch parts statistics
  const { data: partsStats, isLoading: partsStatsLoading } = useQuery(
    'parts-stats',
    () => partsAPI.getAll({ limit: 1000 }),
    { 
      select: (data) => {
        const parts = data.data.parts;
        const totalParts = parts.length;
        const totalValue = parts.reduce((sum, part) => sum + (part.price * part.quantityInStock), 0);
        const outOfStock = parts.filter(part => part.quantityInStock === 0).length;
        const lowStock = parts.filter(part => part.quantityInStock <= part.minimumStockLevel && part.quantityInStock > 0).length;
        
        return { totalParts, totalValue, outOfStock, lowStock };
      }
    }
  );

  // Fetch contacts statistics
  const { data: contactsStats, isLoading: contactsStatsLoading } = useQuery(
    'contacts-stats',
    () => contactsAPI.getAll({ limit: 1000 }),
    { 
      select: (data) => {
        const contacts = data.data.contacts;
        const suppliers = contacts.filter(contact => contact.type === 'supplier').length;
        const customers = contacts.filter(contact => contact.type === 'customer').length;
        const vendors = contacts.filter(contact => contact.type === 'vendor').length;
        
        return { total: contacts.length, suppliers, customers, vendors };
      }
    }
  );

  const { data: todaySchedule, isLoading: scheduleLoading } = useQuery(
    'today-schedule',
    () => scheduleAPI.getByDate(new Date().toISOString().split('T')[0]),
    { select: (data) => data.data }
  );

  const stats = [
    {
      name: 'Total Parts',
      value: partsStats?.totalParts || 0,
      change: `$${partsStats?.totalValue?.toLocaleString() || 0}`,
      changeType: 'info',
      icon: Package,
      color: 'bg-gradient-to-r from-bluez-500 to-bluez-600',
    },
    {
      name: 'Active Orders',
      value: orders?.filter(order => ['pending', 'shipped'].includes(order.status)).length || 0,
      change: `${orders?.filter(order => order.status === 'pending').length || 0} pending`,
      changeType: 'neutral',
      icon: ShoppingCart,
      color: 'bg-gradient-to-r from-green-500 to-green-600',
    },
    {
      name: 'Today\'s Appointments',
      value: todaySchedule?.length || 0,
      change: `${todaySchedule?.filter(appointment => appointment.status === 'confirmed').length || 0} confirmed`,
      changeType: 'neutral',
      icon: Calendar,
      color: 'bg-gradient-to-r from-purple-500 to-purple-600',
    },
    {
      name: 'Total Contacts',
      value: contactsStats?.total || 0,
      change: `${contactsStats?.suppliers || 0} suppliers`,
      changeType: 'info',
      icon: Users,
      color: 'bg-gradient-to-r from-orange-500 to-orange-600',
    },
  ];

  if (ordersLoading || urgentLoading || scheduleLoading || partsStatsLoading || contactsStatsLoading) {
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

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
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
                        {order.supplier?.name || order.customSupplier?.name}
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

        {/* Inventory Alerts */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <Package className="w-5 h-5 text-danger-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Inventory Alerts</h3>
            </div>
          </div>
          <div className="card-body">
            {partsStats && (partsStats.outOfStock > 0 || partsStats.lowStock > 0) ? (
              <div className="space-y-3">
                {partsStats.outOfStock > 0 && (
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                    <div>
                      <p className="text-sm font-medium text-red-900">
                        Out of Stock
                      </p>
                      <p className="text-xs text-red-600">
                        {partsStats.outOfStock} parts need restocking
                      </p>
                    </div>
                    <div className="text-red-600 font-bold">
                      {partsStats.outOfStock}
                    </div>
                  </div>
                )}
                {partsStats.lowStock > 0 && (
                  <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <div>
                      <p className="text-sm font-medium text-yellow-900">
                        Low Stock
                      </p>
                      <p className="text-xs text-yellow-600">
                        {partsStats.lowStock} parts below minimum level
                      </p>
                    </div>
                    <div className="text-yellow-600 font-bold">
                      {partsStats.lowStock}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6">
                <CheckCircle className="mx-auto h-12 w-12 text-green-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">All parts in stock</h3>
                <p className="mt-1 text-sm text-gray-500">
                  No inventory alerts at this time.
                </p>
              </div>
            )}
          </div>
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
