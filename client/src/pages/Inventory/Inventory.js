import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  Package, 
  AlertTriangle, 
  TrendingUp,
  TrendingDown,
  BarChart3,
  Search,
  Filter
} from 'lucide-react';
import { partsAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import StatusBadge from '../../components/UI/StatusBadge';

const Inventory = () => {
  const [categoryFilter, setCategoryFilter] = useState('');
  const [stockFilter, setStockFilter] = useState('');

  // Fetch all parts for inventory overview
  const { data: allParts, isLoading: allPartsLoading } = useQuery(
    'inventory-all-parts',
    () => partsAPI.getAll({ limit: 1000 }),
    { select: (data) => data.data.parts }
  );

  // Fetch low stock parts
  const { data: lowStockParts, isLoading: lowStockLoading } = useQuery(
    'inventory-low-stock',
    () => partsAPI.getLowStock(),
    { select: (data) => data.data }
  );

  if (allPartsLoading || lowStockLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Calculate inventory statistics
  const totalParts = allParts?.length || 0;
  const totalValue = allParts?.reduce((sum, part) => sum + (part.price * part.quantityInStock), 0) || 0;
  const lowStockCount = lowStockParts?.length || 0;
  const outOfStockCount = allParts?.filter(part => part.quantityInStock === 0).length || 0;

  // Filter parts based on selected filters
  const filteredParts = allParts?.filter(part => {
    if (categoryFilter && part.category !== categoryFilter) return false;
    if (stockFilter === 'low' && part.quantityInStock > part.minimumStockLevel) return false;
    if (stockFilter === 'out' && part.quantityInStock > 0) return false;
    return true;
  }) || [];

  // Group parts by category
  const partsByCategory = filteredParts.reduce((acc, part) => {
    if (!acc[part.category]) {
      acc[part.category] = [];
    }
    acc[part.category].push(part);
    return acc;
  }, {});

  const categories = [
    'engine', 'brake', 'transmission', 'electrical', 
    'body', 'interior', 'exhaust', 'suspension', 'other'
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Inventory Overview</h1>
        <p className="mt-1 text-sm text-gray-500">
          Monitor your parts inventory and stock levels
        </p>
      </div>

      {/* Inventory stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <Package className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Parts</p>
                <p className="text-2xl font-semibold text-gray-900">{totalParts}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Value</p>
                <p className="text-2xl font-semibold text-gray-900">
                  ${totalValue.toLocaleString()}
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
                  <AlertTriangle className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Low Stock</p>
                <p className="text-2xl font-semibold text-gray-900">{lowStockCount}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                  <TrendingDown className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Out of Stock</p>
                <p className="text-2xl font-semibold text-gray-900">{outOfStockCount}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Low stock alert */}
      {lowStockParts && lowStockParts.length > 0 && (
        <div className="card border-l-4 border-l-yellow-400 bg-yellow-50">
          <div className="card-header">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Low Stock Alert</h3>
            </div>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {lowStockParts.slice(0, 6).map((part) => (
                <div key={part._id} className="p-3 bg-white rounded-lg border border-yellow-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {part.partNumber}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {part.name}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-yellow-600">
                        {part.quantityInStock} left
                      </p>
                      <p className="text-xs text-gray-500">
                        Min: {part.minimumStockLevel}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {lowStockParts.length > 6 && (
              <p className="mt-3 text-sm text-gray-600">
                And {lowStockParts.length - 6} more parts with low stock...
              </p>
            )}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {/* Category filter */}
            <select
              className="input"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="">All Categories</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>

            {/* Stock filter */}
            <select
              className="input"
              value={stockFilter}
              onChange={(e) => setStockFilter(e.target.value)}
            >
              <option value="">All Stock Levels</option>
              <option value="low">Low Stock</option>
              <option value="out">Out of Stock</option>
            </select>

            {/* Results count */}
            <div className="flex items-center text-sm text-gray-500">
              <BarChart3 className="w-4 h-4 mr-2" />
              {filteredParts.length} parts found
            </div>
          </div>
        </div>
      </div>

      {/* Inventory by category */}
      <div className="space-y-6">
        {Object.keys(partsByCategory).map((category) => (
          <div key={category} className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900 capitalize">
                {category} Parts ({partsByCategory[category].length})
              </h3>
            </div>
            <div className="card-body">
              <div className="overflow-x-auto">
                <table className="table">
                  <thead className="table-header">
                    <tr>
                      <th className="table-header-cell">Part Number</th>
                      <th className="table-header-cell">Name</th>
                      <th className="table-header-cell">Brand</th>
                      <th className="table-header-cell">Stock</th>
                      <th className="table-header-cell">Price</th>
                      <th className="table-header-cell">Value</th>
                      <th className="table-header-cell">Status</th>
                    </tr>
                  </thead>
                  <tbody className="table-body">
                    {partsByCategory[category].map((part) => (
                      <tr key={part._id} className="table-row">
                        <td className="table-cell">
                          <div className="font-medium text-primary-600">
                            {part.partNumber}
                          </div>
                        </td>
                        <td className="table-cell">
                          <div className="font-medium text-gray-900">{part.name}</div>
                          {part.description && (
                            <div className="text-sm text-gray-500 truncate max-w-xs">
                              {part.description}
                            </div>
                          )}
                        </td>
                        <td className="table-cell">{part.brand}</td>
                        <td className="table-cell">
                          <div className="flex items-center">
                            <span className="font-medium">{part.quantityInStock}</span>
                            {part.quantityInStock <= part.minimumStockLevel && (
                              <AlertTriangle className="w-4 h-4 text-warning-500 ml-1" />
                            )}
                          </div>
                          <div className="text-xs text-gray-500">
                            Min: {part.minimumStockLevel}
                          </div>
                        </td>
                        <td className="table-cell">
                          <div className="font-medium">${part.price}</div>
                        </td>
                        <td className="table-cell">
                          <div className="font-medium">
                            ${(part.price * part.quantityInStock).toLocaleString()}
                          </div>
                        </td>
                        <td className="table-cell">
                          <StatusBadge status={part.stockStatus} type="stock" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty state */}
      {filteredParts.length === 0 && (
        <div className="text-center py-12">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No parts found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {categoryFilter || stockFilter
              ? 'Try adjusting your filter criteria.'
              : 'No parts in inventory yet.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default Inventory;
