import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  ShoppingCart,
  Truck,
  Package,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { ordersAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import StatusBadge from '../../components/UI/StatusBadge';
import CountdownTimer from '../../components/UI/CountdownTimer';
import toast from 'react-hot-toast';

const Orders = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [progressFilter, setProgressFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const { isManager } = useAuth();
  const queryClient = useQueryClient();

  // Fetch orders data
  const { data: ordersData, isLoading, error } = useQuery(
    ['orders', currentPage, searchTerm, statusFilter, progressFilter],
    () => ordersAPI.getAll({
      page: currentPage,
      limit: 20,
      status: statusFilter,
      progress: progressFilter,
    }),
    { select: (data) => data.data }
  );

  // Cancel order mutation
  const cancelOrderMutation = useMutation(
    (id) => ordersAPI.cancel(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('orders');
        toast.success('Order cancelled successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to cancel order');
      },
    }
  );

  // Receive order mutation
  const receiveOrderMutation = useMutation(
    (id) => ordersAPI.receive(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('orders');
        toast.success('Order marked as received');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to receive order');
      },
    }
  );

  const handleCancel = (id, orderNumber) => {
    if (window.confirm(`Are you sure you want to cancel order #${orderNumber}?`)) {
      cancelOrderMutation.mutate(id);
    }
  };

  const handleReceive = (id, orderNumber) => {
    if (window.confirm(`Mark order #${orderNumber} as received?`)) {
      receiveOrderMutation.mutate(id);
    }
  };

  const statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'];
  const progressStatuses = ['not_started', 'waiting_on_parts', 'started', 'finished', 'waiting_for_pickup'];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading orders</h3>
        <p className="mt-1 text-sm text-gray-500">
          {error.response?.data?.message || 'Something went wrong'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
          <p className="mt-1 text-sm text-gray-500">
            Track and manage your parts orders
          </p>
        </div>
        {isManager && (
          <Link
            to="/orders/new"
            className="btn-primary"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Order
          </Link>
        )}
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <ShoppingCart className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Orders</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {ordersData?.pagination?.total || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <Truck className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">In Transit</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {ordersData?.orders?.filter(o => o.status === 'shipped').length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Delivered</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {ordersData?.orders?.filter(o => o.status === 'delivered').length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Overdue</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {ordersData?.orders?.filter(o => 
                    o.countdownEndTime && new Date(o.countdownEndTime) < new Date()
                  ).length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search orders..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Status filter */}
            <select
              className="input"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>

            {/* Progress filter */}
            <select
              className="input"
              value={progressFilter}
              onChange={(e) => setProgressFilter(e.target.value)}
            >
              <option value="">All Progress</option>
              {progressStatuses.map((progress) => (
                <option key={progress} value={progress}>
                  {progress.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>

            {/* Results count */}
            <div className="flex items-center text-sm text-gray-500">
              <Package className="w-4 h-4 mr-2" />
              {ordersData?.pagination?.total || 0} orders found
            </div>
          </div>
        </div>
      </div>

      {/* Orders table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">Order #</th>
                <th className="table-header-cell">Supplier</th>
                <th className="table-header-cell">Parts</th>
                <th className="table-header-cell">Total</th>
                <th className="table-header-cell">Status</th>
                <th className="table-header-cell">Progress</th>
                <th className="table-header-cell">Countdown</th>
                <th className="table-header-cell">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {ordersData?.orders?.map((order) => (
                <tr key={order._id} className="table-row">
                  <td className="table-cell">
                    <div className="font-medium text-primary-600">
                      {order.orderNumber}
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(order.orderDate).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="table-cell">
                    <div>
                      <div className="font-medium text-gray-900">
                        {order.supplier?.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {order.supplier?.company}
                      </div>
                    </div>
                  </td>
                  <td className="table-cell">
                    <div className="text-sm">
                      {order.parts?.length || 0} parts
                    </div>
                    {order.parts && order.parts.length > 0 && (
                      <div className="text-xs text-gray-500">
                        {order.parts[0].part?.partNumber}
                        {order.parts.length > 1 && ` +${order.parts.length - 1} more`}
                      </div>
                    )}
                  </td>
                  <td className="table-cell">
                    <div className="font-medium">${order.totalAmount}</div>
                  </td>
                  <td className="table-cell">
                    <StatusBadge status={order.status} type="order" />
                  </td>
                  <td className="table-cell">
                    <StatusBadge status={order.progress} type="progress" />
                  </td>
                  <td className="table-cell">
                    {order.countdownEndTime && (
                      <CountdownTimer endTime={order.countdownEndTime} />
                    )}
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center space-x-2">
                      <Link
                        to={`/orders/${order._id}/edit`}
                        className="text-primary-600 hover:text-primary-900"
                        title="Edit order"
                      >
                        <Edit className="w-4 h-4" />
                      </Link>
                      {isManager && order.status !== 'delivered' && order.status !== 'cancelled' && (
                        <>
                          {order.status === 'shipped' && (
                            <button
                              onClick={() => handleReceive(order._id, order.orderNumber)}
                              className="text-green-600 hover:text-green-900"
                              title="Mark as received"
                              disabled={receiveOrderMutation.isLoading}
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleCancel(order._id, order.orderNumber)}
                            className="text-red-600 hover:text-red-900"
                            title="Cancel order"
                            disabled={cancelOrderMutation.isLoading}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empty state */}
        {(!ordersData?.orders || ordersData.orders.length === 0) && (
          <div className="text-center py-12">
            <ShoppingCart className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No orders found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || statusFilter
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by creating your first order.'}
            </p>
            {isManager && !searchTerm && !statusFilter && (
              <div className="mt-6">
                <Link to="/orders/new" className="btn-primary">
                  <Plus className="w-4 h-4 mr-2" />
                  New Order
                </Link>
              </div>
            )}
          </div>
        )}

        {/* Pagination */}
        {ordersData?.pagination && ordersData.pagination.pages > 1 && (
          <div className="card-footer">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing page {ordersData.pagination.current} of {ordersData.pagination.pages}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={!ordersData.pagination.hasPrev}
                  className="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(prev => prev + 1)}
                  disabled={!ordersData.pagination.hasNext}
                  className="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Orders;
