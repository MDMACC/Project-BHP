import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  ArrowLeft, 
  Plus, 
  Trash2, 
  Upload, 
  Save, 
  Loader2,
  Package,
  User,
  Clock,
  Image as ImageIcon
} from 'lucide-react';
import { ordersAPI, contactsAPI, partsAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const OrdersForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isManager } = useAuth();
  const queryClient = useQueryClient();
  const isEditing = !!id;
  const [useCustomSupplier, setUseCustomSupplier] = useState(false);
  const [uploadingImages, setUploadingImages] = useState({});

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors, isSubmitting },
    reset,
  } = useForm({
    defaultValues: {
      parts: [{ part: '', customPart: { name: '', description: '', image: '' }, quantity: 1, unitPrice: 0 }],
      estimatedArrivalTime: '',
      customTimeLimit: 72,
      notes: ''
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'parts'
  });

  // Fetch existing order if editing
  const { data: order, isLoading: orderLoading } = useQuery(
    ['order', id],
    () => ordersAPI.getById(id),
    { 
      enabled: isEditing,
      select: (data) => data.data,
      onSuccess: (data) => {
        reset(data);
        setUseCustomSupplier(!!data.customSupplier);
      }
    }
  );

  // Fetch suppliers and parts for dropdowns
  const { data: suppliers } = useQuery(
    'suppliers',
    () => contactsAPI.getSuppliers(),
    { select: (data) => data.data }
  );

  const { data: parts } = useQuery(
    'parts',
    () => partsAPI.getAll({ limit: 1000 }),
    { select: (data) => data.data.parts }
  );

  // Create/Update mutation
  const saveOrderMutation = useMutation(
    (data) => isEditing ? ordersAPI.update(id, data) : ordersAPI.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('orders');
        toast.success(`Order ${isEditing ? 'updated' : 'created'} successfully`);
        navigate('/orders');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || `Failed to ${isEditing ? 'update' : 'create'} order`);
      },
    }
  );

  const handleImageUpload = async (file, partIndex) => {
    setUploadingImages(prev => ({ ...prev, [partIndex]: true }));
    
    try {
      // In a real app, you'd upload to a cloud service like AWS S3, Cloudinary, etc.
      // For now, we'll create a mock URL
      const mockImageUrl = URL.createObjectURL(file);
      
      setValue(`parts.${partIndex}.customPart.image`, mockImageUrl);
      toast.success('Image uploaded successfully');
    } catch (error) {
      toast.error('Failed to upload image');
    } finally {
      setUploadingImages(prev => ({ ...prev, [partIndex]: false }));
    }
  };

  const onSubmit = (data) => {
    // Clean up data - remove empty custom parts if using catalog parts
    const cleanedData = {
      ...data,
      parts: data.parts.map(part => {
        if (part.part) {
          // Remove custom part data if using catalog part
          const { customPart, ...rest } = part;
          return rest;
        }
        return part;
      })
    };

    saveOrderMutation.mutate(cleanedData);
  };

  if (!isManager) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Access Denied</h3>
        <p className="mt-1 text-sm text-gray-500">
          You don't have permission to {isEditing ? 'edit' : 'create'} orders.
        </p>
      </div>
    );
  }

  if (orderLoading) {
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
          onClick={() => navigate('/orders')}
          className="p-2 text-gray-400 hover:text-gray-600"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isEditing ? 'Edit Order' : 'Create Custom Order'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {isEditing ? 'Update order information' : 'Create a new custom order with parts and supplier details'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Supplier Information */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <User className="w-5 h-5 text-bluez-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Supplier Information</h3>
            </div>
          </div>
          <div className="card-body space-y-4">
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="existing"
                  checked={!useCustomSupplier}
                  onChange={() => setUseCustomSupplier(false)}
                  className="mr-2"
                />
                Use Existing Supplier
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="custom"
                  checked={useCustomSupplier}
                  onChange={() => setUseCustomSupplier(true)}
                  className="mr-2"
                />
                Custom Supplier
              </label>
            </div>

            {!useCustomSupplier ? (
              <div>
                <label className="label">Supplier *</label>
                <select
                  className={`input ${errors.supplier ? 'input-error' : ''}`}
                  {...register('supplier', { required: !useCustomSupplier && 'Supplier is required' })}
                >
                  <option value="">Select a supplier</option>
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
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="label">Supplier Name *</label>
                  <input
                    type="text"
                    className={`input ${errors.customSupplier?.name ? 'input-error' : ''}`}
                    {...register('customSupplier.name', { required: useCustomSupplier && 'Supplier name is required' })}
                    placeholder="Enter supplier name"
                  />
                  {errors.customSupplier?.name && (
                    <p className="mt-1 text-sm text-danger-600">{errors.customSupplier.name.message}</p>
                  )}
                </div>
                <div>
                  <label className="label">Company</label>
                  <input
                    type="text"
                    className="input"
                    {...register('customSupplier.company')}
                    placeholder="Enter company name"
                  />
                </div>
                <div>
                  <label className="label">Email</label>
                  <input
                    type="email"
                    className="input"
                    {...register('customSupplier.contactInfo.email')}
                    placeholder="Enter email address"
                  />
                </div>
                <div>
                  <label className="label">Phone</label>
                  <input
                    type="tel"
                    className="input"
                    {...register('customSupplier.contactInfo.phone')}
                    placeholder="Enter phone number"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="label">Address</label>
                  <input
                    type="text"
                    className="input"
                    {...register('customSupplier.contactInfo.address.street')}
                    placeholder="Street address"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    className="input"
                    {...register('customSupplier.contactInfo.address.city')}
                    placeholder="City"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    className="input"
                    {...register('customSupplier.contactInfo.address.state')}
                    placeholder="State"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    className="input"
                    {...register('customSupplier.contactInfo.address.zipCode')}
                    placeholder="ZIP Code"
                  />
                </div>
                <div>
                  <input
                    type="url"
                    className="input"
                    {...register('customSupplier.website')}
                    placeholder="Website URL"
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Parts Information */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Package className="w-5 h-5 text-bluez-600 mr-2" />
                <h3 className="text-lg font-medium text-gray-900">Parts Information</h3>
              </div>
              <button
                type="button"
                onClick={() => append({ part: '', customPart: { name: '', description: '', image: '' }, quantity: 1, unitPrice: 0 })}
                className="btn-primary"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Part
              </button>
            </div>
          </div>
          <div className="card-body space-y-6">
            {fields.map((field, index) => (
              <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-md font-medium text-gray-900">Part {index + 1}</h4>
                  {fields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="label">Use Catalog Part</label>
                    <select
                      className="input"
                      {...register(`parts.${index}.part`)}
                    >
                      <option value="">Select from catalog</option>
                      {parts?.map((part) => (
                        <option key={part._id} value={part._id}>
                          {part.partNumber} - {part.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="label">Or Enter Custom Part</label>
                    <input
                      type="text"
                      className="input"
                      {...register(`parts.${index}.customPart.name`)}
                      placeholder="Custom part name"
                    />
                  </div>
                </div>

                {watch(`parts.${index}.customPart.name`) && (
                  <div className="mt-4 space-y-4">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <label className="label">Part Number</label>
                        <input
                          type="text"
                          className="input"
                          {...register(`parts.${index}.customPart.partNumber`)}
                          placeholder="Part number"
                        />
                      </div>
                      <div>
                        <label className="label">Brand</label>
                        <input
                          type="text"
                          className="input"
                          {...register(`parts.${index}.customPart.brand`)}
                          placeholder="Brand"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="label">Description</label>
                      <textarea
                        rows={2}
                        className="input"
                        {...register(`parts.${index}.customPart.description`)}
                        placeholder="Part description"
                      />
                    </div>
                    <div>
                      <label className="label">Product Image</label>
                      <div className="flex items-center space-x-4">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => {
                            const file = e.target.files[0];
                            if (file) handleImageUpload(file, index);
                          }}
                          className="hidden"
                          id={`image-upload-${index}`}
                        />
                        <label
                          htmlFor={`image-upload-${index}`}
                          className="btn-outline cursor-pointer"
                        >
                          {uploadingImages[index] ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <Upload className="w-4 h-4 mr-2" />
                          )}
                          Upload Image
                        </label>
                        {watch(`parts.${index}.customPart.image`) && (
                          <div className="flex items-center space-x-2">
                            <ImageIcon className="w-4 h-4 text-green-600" />
                            <span className="text-sm text-green-600">Image uploaded</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <label className="label">Quantity *</label>
                    <input
                      type="number"
                      min="1"
                      className={`input ${errors.parts?.[index]?.quantity ? 'input-error' : ''}`}
                      {...register(`parts.${index}.quantity`, { 
                        required: 'Quantity is required',
                        min: { value: 1, message: 'Quantity must be at least 1' }
                      })}
                    />
                    {errors.parts?.[index]?.quantity && (
                      <p className="mt-1 text-sm text-danger-600">{errors.parts[index].quantity.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="label">Unit Price *</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      className={`input ${errors.parts?.[index]?.unitPrice ? 'input-error' : ''}`}
                      {...register(`parts.${index}.unitPrice`, { 
                        required: 'Unit price is required',
                        min: { value: 0, message: 'Price must be positive' }
                      })}
                    />
                    {errors.parts?.[index]?.unitPrice && (
                      <p className="mt-1 text-sm text-danger-600">{errors.parts[index].unitPrice.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="label">Total Price</label>
                    <input
                      type="text"
                      className="input bg-gray-50"
                      value={watch(`parts.${index}.quantity`) * watch(`parts.${index}.unitPrice`) || 0}
                      readOnly
                    />
                  </div>
                </div>
              </div>
            ))}
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
          <div className="card-body space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="label">Estimated Arrival Time *</label>
                <input
                  type="text"
                  className={`input ${errors.estimatedArrivalTime ? 'input-error' : ''}`}
                  {...register('estimatedArrivalTime', { required: 'Estimated arrival time is required' })}
                  placeholder="e.g., 3-5 business days, 1 week, 2-3 weeks"
                />
                {errors.estimatedArrivalTime && (
                  <p className="mt-1 text-sm text-danger-600">{errors.estimatedArrivalTime.message}</p>
                )}
              </div>
              <div>
                <label className="label">Custom Time Limit (hours)</label>
                <input
                  type="number"
                  min="1"
                  max="168"
                  className="input"
                  {...register('customTimeLimit', { 
                    min: { value: 1, message: 'Time limit must be at least 1 hour' },
                    max: { value: 168, message: 'Time limit cannot exceed 168 hours' }
                  })}
                />
              </div>
            </div>
            <div>
              <label className="label">Notes</label>
              <textarea
                rows={3}
                className="input"
                {...register('notes')}
                placeholder="Additional notes about this order"
              />
            </div>
          </div>
        </div>

        {/* Form actions */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/orders')}
            className="btn-outline"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting || saveOrderMutation.isLoading}
            className="btn-primary"
          >
            {isSubmitting || saveOrderMutation.isLoading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            {isEditing ? 'Update Order' : 'Create Order'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default OrdersForm;
