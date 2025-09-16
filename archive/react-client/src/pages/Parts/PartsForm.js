import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { ArrowLeft, Save, Loader2 } from 'lucide-react';
import { partsAPI, contactsAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const PartsForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isManager } = useAuth();
  const queryClient = useQueryClient();
  const isEditing = !!id;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm();

  // Fetch part data if editing
  const { data: part, isLoading: partLoading } = useQuery(
    ['part', id],
    () => partsAPI.getById(id),
    { 
      enabled: isEditing,
      select: (data) => data.data,
      onSuccess: (data) => {
        reset(data);
      }
    }
  );

  // Fetch suppliers
  const { data: suppliers } = useQuery(
    'suppliers',
    () => contactsAPI.getSuppliers(),
    { select: (data) => data.data }
  );

  // Create/Update mutation
  const savePartMutation = useMutation(
    (data) => isEditing ? partsAPI.update(id, data) : partsAPI.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('parts');
        toast.success(`Part ${isEditing ? 'updated' : 'created'} successfully`);
        navigate('/parts');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || `Failed to ${isEditing ? 'update' : 'create'} part`);
      },
    }
  );

  const onSubmit = (data) => {
    savePartMutation.mutate(data);
  };

  if (!isManager) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Access Denied</h3>
        <p className="mt-1 text-sm text-gray-500">
          You don't have permission to {isEditing ? 'edit' : 'create'} parts.
        </p>
      </div>
    );
  }

  if (partLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/parts')}
          className="p-2 text-gray-400 hover:text-gray-600"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isEditing ? 'Edit Part' : 'Add New Part'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {isEditing ? 'Update part information' : 'Add a new part to your inventory'}
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit(onSubmit)} className="card-body space-y-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {/* Part Number */}
            <div>
              <label htmlFor="partNumber" className="label">
                Part Number *
              </label>
              <input
                id="partNumber"
                type="text"
                className={`input ${errors.partNumber ? 'input-error' : ''}`}
                placeholder="Enter part number"
                {...register('partNumber', {
                  required: 'Part number is required',
                })}
              />
              {errors.partNumber && (
                <p className="mt-1 text-sm text-danger-600">{errors.partNumber.message}</p>
              )}
            </div>

            {/* Name */}
            <div>
              <label htmlFor="name" className="label">
                Part Name *
              </label>
              <input
                id="name"
                type="text"
                className={`input ${errors.name ? 'input-error' : ''}`}
                placeholder="Enter part name"
                {...register('name', {
                  required: 'Part name is required',
                })}
              />
              {errors.name && (
                <p className="mt-1 text-sm text-danger-600">{errors.name.message}</p>
              )}
            </div>

            {/* Category */}
            <div>
              <label htmlFor="category" className="label">
                Category *
              </label>
              <select
                id="category"
                className={`input ${errors.category ? 'input-error' : ''}`}
                {...register('category', {
                  required: 'Category is required',
                })}
              >
                <option value="">Select category</option>
                <option value="engine">Engine</option>
                <option value="brake">Brake</option>
                <option value="transmission">Transmission</option>
                <option value="electrical">Electrical</option>
                <option value="body">Body</option>
                <option value="interior">Interior</option>
                <option value="exhaust">Exhaust</option>
                <option value="suspension">Suspension</option>
                <option value="other">Other</option>
              </select>
              {errors.category && (
                <p className="mt-1 text-sm text-danger-600">{errors.category.message}</p>
              )}
            </div>

            {/* Brand */}
            <div>
              <label htmlFor="brand" className="label">
                Brand *
              </label>
              <input
                id="brand"
                type="text"
                className={`input ${errors.brand ? 'input-error' : ''}`}
                placeholder="Enter brand"
                {...register('brand', {
                  required: 'Brand is required',
                })}
              />
              {errors.brand && (
                <p className="mt-1 text-sm text-danger-600">{errors.brand.message}</p>
              )}
            </div>

            {/* Price */}
            <div>
              <label htmlFor="price" className="label">
                Selling Price *
              </label>
              <input
                id="price"
                type="number"
                step="0.01"
                min="0"
                className={`input ${errors.price ? 'input-error' : ''}`}
                placeholder="0.00"
                {...register('price', {
                  required: 'Price is required',
                  min: { value: 0, message: 'Price must be positive' },
                })}
              />
              {errors.price && (
                <p className="mt-1 text-sm text-danger-600">{errors.price.message}</p>
              )}
            </div>

            {/* Cost */}
            <div>
              <label htmlFor="cost" className="label">
                Cost *
              </label>
              <input
                id="cost"
                type="number"
                step="0.01"
                min="0"
                className={`input ${errors.cost ? 'input-error' : ''}`}
                placeholder="0.00"
                {...register('cost', {
                  required: 'Cost is required',
                  min: { value: 0, message: 'Cost must be positive' },
                })}
              />
              {errors.cost && (
                <p className="mt-1 text-sm text-danger-600">{errors.cost.message}</p>
              )}
            </div>

            {/* Quantity in Stock */}
            <div>
              <label htmlFor="quantityInStock" className="label">
                Quantity in Stock *
              </label>
              <input
                id="quantityInStock"
                type="number"
                min="0"
                className={`input ${errors.quantityInStock ? 'input-error' : ''}`}
                placeholder="0"
                {...register('quantityInStock', {
                  required: 'Quantity is required',
                  min: { value: 0, message: 'Quantity must be non-negative' },
                })}
              />
              {errors.quantityInStock && (
                <p className="mt-1 text-sm text-danger-600">{errors.quantityInStock.message}</p>
              )}
            </div>

            {/* Minimum Stock Level */}
            <div>
              <label htmlFor="minimumStockLevel" className="label">
                Minimum Stock Level
              </label>
              <input
                id="minimumStockLevel"
                type="number"
                min="0"
                className={`input ${errors.minimumStockLevel ? 'input-error' : ''}`}
                placeholder="5"
                {...register('minimumStockLevel', {
                  min: { value: 0, message: 'Minimum stock must be non-negative' },
                })}
              />
              {errors.minimumStockLevel && (
                <p className="mt-1 text-sm text-danger-600">{errors.minimumStockLevel.message}</p>
              )}
            </div>

            {/* Supplier */}
            <div className="sm:col-span-2">
              <label htmlFor="supplier" className="label">
                Supplier *
              </label>
              <select
                id="supplier"
                className={`input ${errors.supplier ? 'input-error' : ''}`}
                {...register('supplier', {
                  required: 'Supplier is required',
                })}
              >
                <option value="">Select supplier</option>
                {suppliers?.map((supplier) => (
                  <option key={supplier._id} value={supplier._id}>
                    {supplier.name} {supplier.company && `- ${supplier.company}`}
                  </option>
                ))}
              </select>
              {errors.supplier && (
                <p className="mt-1 text-sm text-danger-600">{errors.supplier.message}</p>
              )}
            </div>

            {/* Description */}
            <div className="sm:col-span-2">
              <label htmlFor="description" className="label">
                Description
              </label>
              <textarea
                id="description"
                rows={3}
                className={`input ${errors.description ? 'input-error' : ''}`}
                placeholder="Enter part description"
                {...register('description')}
              />
              {errors.description && (
                <p className="mt-1 text-sm text-danger-600">{errors.description.message}</p>
              )}
            </div>
          </div>

          {/* Form actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={() => navigate('/parts')}
              className="btn-outline"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || savePartMutation.isLoading}
              className="btn-primary"
            >
              {isSubmitting || savePartMutation.isLoading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              {isEditing ? 'Update Part' : 'Create Part'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PartsForm;
