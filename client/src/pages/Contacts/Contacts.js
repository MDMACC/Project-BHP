import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Users,
  Phone,
  Mail,
  MapPin,
  Star,
  Building
} from 'lucide-react';
import { contactsAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import StatusBadge from '../../components/UI/StatusBadge';
import toast from 'react-hot-toast';

const Contacts = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const { isManager } = useAuth();
  const queryClient = useQueryClient();

  // Fetch contacts data
  const { data: contactsData, isLoading, error } = useQuery(
    ['contacts', currentPage, searchTerm, typeFilter],
    () => contactsAPI.getAll({
      page: currentPage,
      limit: 20,
      search: searchTerm,
      type: typeFilter,
    }),
    { select: (data) => data.data }
  );

  // Delete contact mutation
  const deleteContactMutation = useMutation(
    (id) => contactsAPI.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('contacts');
        toast.success('Contact deleted successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to delete contact');
      },
    }
  );

  // Rate contact mutation
  const rateContactMutation = useMutation(
    ({ id, rating }) => contactsAPI.rate(id, rating),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('contacts');
        toast.success('Rating updated successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to update rating');
      },
    }
  );

  const handleDelete = (id, name) => {
    if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
      deleteContactMutation.mutate(id);
    }
  };

  const handleRate = (id, rating) => {
    rateContactMutation.mutate({ id, rating });
  };

  const types = ['supplier', 'customer', 'vendor', 'distributor'];

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
        <Users className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading contacts</h3>
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
          <h1 className="text-2xl font-bold text-gray-900">Contacts</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your suppliers, customers, and vendors
          </p>
        </div>
        {isManager && (
          <Link
            to="/contacts/new"
            className="btn-primary"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Contact
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
                  <Users className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Contacts</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {contactsData?.pagination?.total || 0}
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
                  <Building className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Suppliers</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {contactsData?.contacts?.filter(c => c.type === 'supplier').length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Customers</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {contactsData?.contacts?.filter(c => c.type === 'customer').length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center">
                  <Star className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Avg Rating</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {contactsData?.contacts?.length > 0 
                    ? (contactsData.contacts.reduce((sum, c) => sum + (c.rating || 0), 0) / contactsData.contacts.length).toFixed(1)
                    : '0.0'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
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
                placeholder="Search contacts..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Type filter */}
            <select
              className="input"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="">All Types</option>
              {types.map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>

            {/* Results count */}
            <div className="flex items-center text-sm text-gray-500">
              <Users className="w-4 h-4 mr-2" />
              {contactsData?.pagination?.total || 0} contacts found
            </div>
          </div>
        </div>
      </div>

      {/* Contacts grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {contactsData?.contacts?.map((contact) => (
          <div key={contact._id} className="card hover:shadow-lg transition-shadow duration-200">
            <div className="card-body">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-medium text-gray-900">
                      {contact.name}
                    </h3>
                    <StatusBadge status={contact.type} type="contact" />
                  </div>
                  
                  {contact.company && (
                    <p className="text-sm text-gray-600 mt-1">
                      {contact.company}
                    </p>
                  )}

                  <div className="mt-3 space-y-2">
                    {contact.contactInfo?.email && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Mail className="w-4 h-4 mr-2" />
                        <a 
                          href={`mailto:${contact.contactInfo.email}`}
                          className="hover:text-primary-600 transition-colors"
                        >
                          {contact.contactInfo.email}
                        </a>
                      </div>
                    )}
                    
                    {contact.contactInfo?.phone && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Phone className="w-4 h-4 mr-2" />
                        <a 
                          href={`tel:${contact.contactInfo.phone}`}
                          className="hover:text-primary-600 transition-colors"
                        >
                          {contact.contactInfo.phone}
                        </a>
                      </div>
                    )}

                    {contact.address && (
                      <div className="flex items-start text-sm text-gray-600">
                        <MapPin className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="truncate">
                          {contact.fullAddress}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Rating */}
                  <div className="mt-3 flex items-center">
                    <div className="flex items-center">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          onClick={() => handleRate(contact._id, star)}
                          className="text-yellow-400 hover:text-yellow-500 transition-colors"
                          disabled={rateContactMutation.isLoading}
                        >
                          <Star 
                            className={`w-4 h-4 ${
                              star <= (contact.rating || 0) ? 'fill-current' : ''
                            }`} 
                          />
                        </button>
                      ))}
                    </div>
                    <span className="ml-2 text-sm text-gray-500">
                      ({contact.rating || 0}/5)
                    </span>
                  </div>
                </div>

                <div className="flex flex-col space-y-2">
                  <Link
                    to={`/contacts/${contact._id}/edit`}
                    className="text-primary-600 hover:text-primary-900"
                    title="Edit contact"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                  {isManager && (
                    <button
                      onClick={() => handleDelete(contact._id, contact.name)}
                      className="text-red-600 hover:text-red-900"
                      title="Delete contact"
                      disabled={deleteContactMutation.isLoading}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty state */}
      {(!contactsData?.contacts || contactsData.contacts.length === 0) && (
        <div className="text-center py-12">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No contacts found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || typeFilter
              ? 'Try adjusting your search or filter criteria.'
              : 'Get started by adding your first contact.'}
          </p>
          {isManager && !searchTerm && !typeFilter && (
            <div className="mt-6">
              <Link to="/contacts/new" className="btn-primary">
                <Plus className="w-4 h-4 mr-2" />
                Add Contact
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Pagination */}
      {contactsData?.pagination && contactsData.pagination.pages > 1 && (
        <div className="card">
          <div className="card-footer">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing page {contactsData.pagination.current} of {contactsData.pagination.pages}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={!contactsData.pagination.hasPrev}
                  className="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage(prev => prev + 1)}
                  disabled={!contactsData.pagination.hasNext}
                  className="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Contacts;
