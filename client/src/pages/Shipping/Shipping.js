import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Truck, 
  AlertTriangle, 
  Clock, 
  CheckCircle,
  Package,
  MapPin,
  Calendar,
  Phone
} from 'lucide-react';
import { ordersAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import StatusBadge from '../../components/UI/StatusBadge';
import CountdownTimer from '../../components/UI/CountdownTimer';
import toast from 'react-hot-toast';

const Shipping = () => {
  const [activeTab, setActiveTab] = useState('urgent');
  const queryClient = useQueryClient();

  // Fetch urgent orders
  const { data: urgentOrders, isLoading: urgentLoading } = useQuery(
    'urgent-orders',
    () => ordersAPI.getUrgent(),
    { select: (data) => data.data }
  );

  // Fetch overdue orders
  const { data: overdueOrders, isLoading: overdueLoading } = useQuery(
    'overdue-orders',
    () => ordersAPI.getOverdue(),
    { select: (data) => data.data }
  );

  // Receive order mutation
  const receiveOrderMutation = useMutation(
    (id) => ordersAPI.receive(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('urgent-orders');
        queryClient.invalidateQueries('overdue-orders');
        toast.success('Order marked as received');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to receive order');
      },
    }
  );

  const handleReceive = (id, orderNumber) => {
    if (window.confirm(`Mark order #${orderNumber} as received?`)) {
      receiveOrderMutation.mutate(id);
    }
  };

  const tabs = [
    { id: 'urgent', name: 'Urgent', count: urgentOrders?.length || 0 },
    { id: 'overdue', name: 'Overdue', count: overdueOrders?.length || 0 },
  ];

  const getTimeRemaining = (endTime) => {
    if (!endTime) return null;
    
    const now = new Date().getTime();
    const end = new Date(endTime).getTime();
    const difference = end - now;
    
    if (difference <= 0) return 'Overdue';
    
    const hours = Math.floor(difference / (1000 * 60 * 60));
    const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

  const getPriorityColor = (endTime) => {
    if (!endTime) return 'bg-gray-100 border-gray-200';
    
    const now = new Date().getTime();
    const end = new Date(endTime).getTime();
    const difference = end - now;
    
    if (difference <= 0) return 'bg-red-100 border-red-200';
    if (difference < 24 * 60 * 60 * 1000) return 'bg-yellow-100 border-yellow-200';
    return 'bg-blue-100 border-blue-200';
  };

  if (urgentLoading || overdueLoading) {
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
        <h1 className="text-2xl font-bold text-gray-900">Shipping Tracking</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor package deliveries and track shipping status
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
              {tab.count > 0 && (
                <span className={`ml-2 py-0.5 px-2 rounded-full text-xs ${
                  activeTab === tab.id
                    ? 'bg-primary-100 text-primary-600'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {activeTab === 'urgent' && (
          <div>
            <div className="flex items-center mb-4">
              <Clock className="w-5 h-5 text-yellow-500 mr-2" />
              <h2 className="text-lg font-medium text-gray-900">Urgent Orders</h2>
              <span className="ml-2 text-sm text-gray-500">
                Less than 24 hours remaining
              </span>
            </div>

            {urgentOrders && urgentOrders.length > 0 ? (
              <div className="grid gap-4">
                {urgentOrders.map((order) => (
                  <div
                    key={order._id}
                    className={`card border-l-4 border-l-yellow-400 ${getPriorityColor(order.countdownEndTime)}`}
                  >
                    <div className="card-body">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <h3 className="text-lg font-medium text-gray-900">
                              Order #{order.orderNumber}
                            </h3>
                            <StatusBadge status={order.status} type="order" />
                            <StatusBadge status={order.progress} type="progress" />
                          </div>
                          
                          <div className="mt-2 grid grid-cols-1 gap-4 sm:grid-cols-3">
                            <div className="flex items-center text-sm text-gray-600">
                              <Package className="w-4 h-4 mr-2" />
                              <span>{order.supplier?.name || order.customSupplier?.name}</span>
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <MapPin className="w-4 h-4 mr-2" />
                              <span>{order.supplier?.company}</span>
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <Calendar className="w-4 h-4 mr-2" />
                              <span>{new Date(order.orderDate).toLocaleDateString()}</span>
                            </div>
                          </div>

                          <div className="mt-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm text-gray-600">Parts Ordered:</p>
                                <div className="mt-1 space-y-1">
                                  {order.parts?.slice(0, 3).map((part, index) => (
                                    <div key={index} className="text-sm">
                                      <span className="font-medium">{part.part?.partNumber}</span>
                                      <span className="text-gray-500 ml-2">
                                        {part.part?.name} (Qty: {part.quantity})
                                      </span>
                                    </div>
                                  ))}
                                  {order.parts && order.parts.length > 3 && (
                                    <p className="text-sm text-gray-500">
                                      +{order.parts.length - 3} more parts
                                    </p>
                                  )}
                                </div>
                              </div>
                              
                              <div className="text-right">
                                <p className="text-sm text-gray-600">Total Amount:</p>
                                <p className="text-lg font-semibold text-gray-900">
                                  ${order.totalAmount}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="ml-6 flex flex-col items-end space-y-3">
                          <CountdownTimer endTime={order.countdownEndTime} />
                          
                          {order.status === 'shipped' && (
                            <button
                              onClick={() => handleReceive(order._id, order.orderNumber)}
                              className="btn-success"
                              disabled={receiveOrderMutation.isLoading}
                            >
                              <CheckCircle className="w-4 h-4 mr-2" />
                              Mark Received
                            </button>
                          )}

                          {order.shippingInfo?.trackingNumber && (
                            <div className="text-right">
                              <p className="text-xs text-gray-500">Tracking #</p>
                              <p className="text-sm font-medium text-gray-900">
                                {order.shippingInfo.trackingNumber}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <CheckCircle className="mx-auto h-12 w-12 text-green-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No urgent orders</h3>
                <p className="mt-1 text-sm text-gray-500">
                  All orders are on track for delivery.
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'overdue' && (
          <div>
            <div className="flex items-center mb-4">
              <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
              <h2 className="text-lg font-medium text-gray-900">Overdue Orders</h2>
              <span className="ml-2 text-sm text-gray-500">
                Past expected delivery time
              </span>
            </div>

            {overdueOrders && overdueOrders.length > 0 ? (
              <div className="grid gap-4">
                {overdueOrders.map((order) => (
                  <div
                    key={order._id}
                    className={`card border-l-4 border-l-red-400 ${getPriorityColor(order.countdownEndTime)}`}
                  >
                    <div className="card-body">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <h3 className="text-lg font-medium text-gray-900">
                              Order #{order.orderNumber}
                            </h3>
                            <StatusBadge status={order.status} type="order" />
                            <StatusBadge status={order.progress} type="progress" />
                          </div>
                          
                          <div className="mt-2 grid grid-cols-1 gap-4 sm:grid-cols-3">
                            <div className="flex items-center text-sm text-gray-600">
                              <Package className="w-4 h-4 mr-2" />
                              <span>{order.supplier?.name || order.customSupplier?.name}</span>
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <Phone className="w-4 h-4 mr-2" />
                              <span>{order.supplier?.contactInfo?.phone}</span>
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <Calendar className="w-4 h-4 mr-2" />
                              <span>Expected: {order.expectedDeliveryDate ? new Date(order.expectedDeliveryDate).toLocaleDateString() : 'N/A'}</span>
                            </div>
                          </div>

                          <div className="mt-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm text-gray-600">Parts Ordered:</p>
                                <div className="mt-1 space-y-1">
                                  {order.parts?.slice(0, 3).map((part, index) => (
                                    <div key={index} className="text-sm">
                                      <span className="font-medium">{part.part?.partNumber}</span>
                                      <span className="text-gray-500 ml-2">
                                        {part.part?.name} (Qty: {part.quantity})
                                      </span>
                                    </div>
                                  ))}
                                  {order.parts && order.parts.length > 3 && (
                                    <p className="text-sm text-gray-500">
                                      +{order.parts.length - 3} more parts
                                    </p>
                                  )}
                                </div>
                              </div>
                              
                              <div className="text-right">
                                <p className="text-sm text-gray-600">Total Amount:</p>
                                <p className="text-lg font-semibold text-gray-900">
                                  ${order.totalAmount}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="ml-6 flex flex-col items-end space-y-3">
                          <CountdownTimer endTime={order.countdownEndTime} />
                          
                          {order.status === 'shipped' && (
                            <button
                              onClick={() => handleReceive(order._id, order.orderNumber)}
                              className="btn-success"
                              disabled={receiveOrderMutation.isLoading}
                            >
                              <CheckCircle className="w-4 h-4 mr-2" />
                              Mark Received
                            </button>
                          )}

                          {order.shippingInfo?.trackingNumber && (
                            <div className="text-right">
                              <p className="text-xs text-gray-500">Tracking #</p>
                              <p className="text-sm font-medium text-gray-900">
                                {order.shippingInfo.trackingNumber}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <CheckCircle className="mx-auto h-12 w-12 text-green-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No overdue orders</h3>
                <p className="mt-1 text-sm text-gray-500">
                  All orders are on time or have been delivered.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Shipping;
