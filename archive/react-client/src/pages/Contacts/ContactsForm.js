import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const ContactsForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = !!id;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/contacts')}
          className="p-2 text-gray-400 hover:text-gray-600"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isEditing ? 'Edit Contact' : 'Add New Contact'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {isEditing ? 'Update contact information' : 'Add a new supplier, customer, or vendor'}
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900">Contact Form</h3>
            <p className="mt-1 text-sm text-gray-500">
              This form will allow you to manage suppliers, customers, and vendors with contact information and ratings.
            </p>
            <p className="mt-2 text-sm text-gray-400">
              Form implementation coming soon...
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactsForm;
