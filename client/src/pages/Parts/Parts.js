import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Package,
  AlertTriangle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { partsAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import StatusBadge from '../../components/UI/StatusBadge';
import toast from 'react-hot-toast';

const Parts = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const { isManager } = useAuth();
  const queryClient = useQueryClient();

  // Fetch parts data
  const { data: partsData, isLoading, error } = useQuery(
    ['parts', currentPage, searchTerm, categoryFilter],
    () => partsAPI.getAll({
      page: currentPage,
      limit: 20,
      search: searchTerm,
      category: categoryFilter,
    }),
    { select: (data) => data.data }
  );

  // Delete part mutation
  const deletePartMutation = useMutation(
    (id) => partsAPI.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('parts');
        toast.success('Part deleted successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to delete part');
      },
    }
  );

  const handleDelete = (id, name) => {
    if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
      deletePartMutation.mutate(id);
    }
  };

  const categories = [
    'engine', 'brake', 'transmission', 'electrical', 
    'body', 'interior', 'exhaust', 'suspension', 'other'
  ];

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
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading parts</h3>
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
          <h1 className="text-2xl font-bold text-gray-900">Parts Inventory</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your automotive parts inventory
          </p>
        </div>
        {isManager && (
          <Link
            to="/parts/new"
            className="btn-primary"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Part
          </Link>
        )}
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search parts..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

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

            {/* Results count */}
            <div className="flex items-center text-sm text-gray-500">
              <Package className="w-4 h-4 mr-2" />
              {partsData?.pagination?.total || 0} parts found
            </div>
          </div>
        </div>
      </div>

      {/* Parts table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">Part Number</th>
                <th className="table-header-cell">Name</th>
                <th className="table-header-cell">Category</th>
                <th className="table-header-cell">Brand</th>
                <th className="table-header-cell">Stock</th>
                <th className="table-header-cell">Price</th>
                <th className="table-header-cell">Status</th>
                <th className="table-header-cell">Actions</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {partsData?.parts?.map((part) => (
                <tr key={part._id} className="table-row">
                  <td className="table-cell">
                    <div className="font-medium text-primary-600">
                      {part.partNumber}
                    </div>
                  </td>
                  <td className="table-cell">
                    <div>
                      <div className="font-medium text-gray-900">{part.name}</div>
                      {part.description && (
                        <div className="text-sm text-gray-500 truncate max-w-xs">
                          {part.description}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="table-cell">
                    <span className="capitalize">{part.category}</span>
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
                    <div className="text-xs text-gray-500">
                      Cost: ${part.cost}
                    </div>
                  </td>
                  <td className="table-cell">
                    <StatusBadge 
                      status={part.stockStatus} 
                      type="stock" 
                    />
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center space-x-2">
                      <Link
                        to={`/parts/${part._id}/edit`}
                        className="text-primary-600 hover:text-primary-900"
                        title="Edit part"
                      >
                        <Edit className="w-4 h-4" />
                      </Link>
                      {isManager && (
                        <button
                          onClick={() => handleDelete(part._id, part.name)}
                          className="text-red-600 hover:text-red-900"
                          title="Delete part"
                          disabled={deletePartMutation.isLoading}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empty state */}
        {(!partsData?.parts || partsData.parts.length === 0) && (
          <div className="text-center py-12">
            <Package className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No parts found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || categoryFilter
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by adding your first part.'}
            </p>
            {isManager && !searchTerm && !categoryFilter && (
              <div className="mt-6">
                <Link to="/parts/new" className="btn-primary">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Part
                </Link>
              </div>
            )}
          </div>
        )}

        {/* Pagination */}
        {partsData?.pagination && partsData.pagination.pages > 1 && (
          <div className="card-footer">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing page {partsData.pagination.current} of {partsData.pagination.pages}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={!partsData.pagination.hasPrev}
                  className="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(prev => prev + 1)}
                  disabled={!partsData.pagination.hasNext}
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

export default Parts;
