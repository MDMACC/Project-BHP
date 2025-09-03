import React from 'react';
import { 
  Package, 
  User, 
  Clock, 
  MapPin, 
  Phone, 
  Mail, 
  Globe,
  Image as ImageIcon,
  Calendar,
  DollarSign
} from 'lucide-react';
import StatusBadge from '../UI/StatusBadge';
import CountdownTimer from '../UI/CountdownTimer';

const OrderDetails = ({ order }) => {
  if (!order) return null;

  return (
    <div className="space-y-6">
      {/* Order Header */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Order #{order.orderNumber}
              </h2>
              <p className="text-sm text-gray-500">
                Created on {new Date(order.orderDate).toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <StatusBadge status={order.status} type="order" />
              <StatusBadge status={order.progress} type="progress" />
              {order.countdownEndTime && (
                <CountdownTimer endTime={order.countdownEndTime} />
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Supplier Information */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <User className="w-5 h-5 text-bluez-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Supplier Information</h3>
            </div>
          </div>
          <div className="card-body">
            {order.supplier ? (
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900">{order.supplier.name}</h4>
                  {order.supplier.company && (
                    <p className="text-sm text-gray-600">{order.supplier.company}</p>
                  )}
                </div>
                
                {order.supplier.contactInfo && (
                  <div className="space-y-2">
                    {order.supplier.contactInfo.email && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Mail className="w-4 h-4 mr-2" />
                        <a 
                          href={`mailto:${order.supplier.contactInfo.email}`}
                          className="hover:text-bluez-600 transition-colors"
                        >
                          {order.supplier.contactInfo.email}
                        </a>
                      </div>
                    )}
                    
                    {order.supplier.contactInfo.phone && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Phone className="w-4 h-4 mr-2" />
                        <a 
                          href={`tel:${order.supplier.contactInfo.phone}`}
                          className="hover:text-bluez-600 transition-colors"
                        >
                          {order.supplier.contactInfo.phone}
                        </a>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900">{order.customSupplier.name}</h4>
                  {order.customSupplier.company && (
                    <p className="text-sm text-gray-600">{order.customSupplier.company}</p>
                  )}
                  <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                    Custom Supplier
                  </span>
                </div>
                
                {order.customSupplier.contactInfo && (
                  <div className="space-y-2">
                    {order.customSupplier.contactInfo.email && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Mail className="w-4 h-4 mr-2" />
                        <a 
                          href={`mailto:${order.customSupplier.contactInfo.email}`}
                          className="hover:text-bluez-600 transition-colors"
                        >
                          {order.customSupplier.contactInfo.email}
                        </a>
                      </div>
                    )}
                    
                    {order.customSupplier.contactInfo.phone && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Phone className="w-4 h-4 mr-2" />
                        <a 
                          href={`tel:${order.customSupplier.contactInfo.phone}`}
                          className="hover:text-bluez-600 transition-colors"
                        >
                          {order.customSupplier.contactInfo.phone}
                        </a>
                      </div>
                    )}
                    
                    {order.customSupplier.contactInfo.address && (
                      <div className="flex items-start text-sm text-gray-600">
                        <MapPin className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                        <div>
                          {order.customSupplier.contactInfo.address.street && (
                            <div>{order.customSupplier.contactInfo.address.street}</div>
                          )}
                          {(order.customSupplier.contactInfo.address.city || 
                            order.customSupplier.contactInfo.address.state || 
                            order.customSupplier.contactInfo.address.zipCode) && (
                            <div>
                              {[
                                order.customSupplier.contactInfo.address.city,
                                order.customSupplier.contactInfo.address.state,
                                order.customSupplier.contactInfo.address.zipCode
                              ].filter(Boolean).join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {order.customSupplier.website && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Globe className="w-4 h-4 mr-2" />
                    <a 
                      href={order.customSupplier.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-bluez-600 transition-colors"
                    >
                      {order.customSupplier.website}
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Order Details */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <Clock className="w-5 h-5 text-bluez-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Order Details</h3>
            </div>
          </div>
          <div className="card-body space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Estimated Arrival:</span>
              <span className="text-sm font-medium text-gray-900">
                {order.estimatedArrivalTime}
              </span>
            </div>
            
            {order.expectedDeliveryDate && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Expected Delivery:</span>
                <span className="text-sm font-medium text-gray-900">
                  {new Date(order.expectedDeliveryDate).toLocaleDateString()}
                </span>
              </div>
            )}
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Total Amount:</span>
              <span className="text-lg font-bold text-gray-900">
                ${order.totalAmount}
              </span>
            </div>
            
            {order.customTimeLimit && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Time Limit:</span>
                <span className="text-sm font-medium text-gray-900">
                  {order.customTimeLimit} hours
                </span>
              </div>
            )}
            
            {order.shippingInfo?.trackingNumber && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Tracking #:</span>
                <span className="text-sm font-medium text-gray-900">
                  {order.shippingInfo.trackingNumber}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Parts Information */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center">
            <Package className="w-5 h-5 text-bluez-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Parts Information</h3>
          </div>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {order.parts?.map((part, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {part.part ? (
                      // Catalog part
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {part.part.partNumber} - {part.part.name}
                        </h4>
                        <p className="text-sm text-gray-600">
                          {part.part.brand} • {part.part.category}
                        </p>
                        {part.part.description && (
                          <p className="text-sm text-gray-500 mt-1">
                            {part.part.description}
                          </p>
                        )}
                      </div>
                    ) : (
                      // Custom part
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {part.customPart.partNumber && `${part.customPart.partNumber} - `}
                          {part.customPart.name}
                        </h4>
                        {part.customPart.brand && (
                          <p className="text-sm text-gray-600">
                            {part.customPart.brand}
                            {part.customPart.category && ` • ${part.customPart.category}`}
                          </p>
                        )}
                        {part.customPart.description && (
                          <p className="text-sm text-gray-500 mt-1">
                            {part.customPart.description}
                          </p>
                        )}
                        
                        {part.customPart.specifications && (
                          <div className="mt-2 text-xs text-gray-500">
                            {part.customPart.specifications.material && (
                              <span className="mr-3">Material: {part.customPart.specifications.material}</span>
                            )}
                            {part.customPart.specifications.color && (
                              <span className="mr-3">Color: {part.customPart.specifications.color}</span>
                            )}
                            {part.customPart.specifications.weight && (
                              <span>Weight: {part.customPart.specifications.weight}lbs</span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="ml-4 text-right">
                    <div className="text-sm text-gray-600">
                      Qty: {part.quantity}
                    </div>
                    <div className="text-sm text-gray-600">
                      ${part.unitPrice} each
                    </div>
                    <div className="font-medium text-gray-900">
                      ${part.totalPrice}
                    </div>
                  </div>
                </div>
                
                {/* Product Image */}
                {part.customPart?.image && (
                  <div className="mt-3">
                    <div className="flex items-center text-sm text-gray-600 mb-2">
                      <ImageIcon className="w-4 h-4 mr-1" />
                      Product Image:
                    </div>
                    <img
                      src={part.customPart.image}
                      alt={part.customPart.name}
                      className="w-32 h-32 object-cover rounded-lg border border-gray-200"
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Notes */}
      {order.notes && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Notes</h3>
          </div>
          <div className="card-body">
            <p className="text-gray-700 whitespace-pre-wrap">{order.notes}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderDetails;
