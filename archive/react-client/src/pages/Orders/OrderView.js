import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { ordersAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import OrderDetails from '../../components/Orders/OrderDetails';

const OrderView = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: order, isLoading, error } = useQuery(
    ['order', id],
    () => ordersAPI.getById(id),
    { 
      select: (data) => data.data,
      onError: (error) => {
        console.error('Error fetching order:', error);
      }
    }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Order Not Found</h3>
        <p className="mt-1 text-sm text-gray-500">
          The order you're looking for doesn't exist or you don't have permission to view it.
        </p>
        <button
          onClick={() => navigate('/orders')}
          className="mt-4 btn-primary"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Orders
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/orders')}
          className="p-2 text-gray-400 hover:text-gray-600"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Order Details
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            View detailed information about order #{order.orderNumber}
          </p>
        </div>
      </div>

      <OrderDetails order={order} />
    </div>
  );
};

export default OrderView;
