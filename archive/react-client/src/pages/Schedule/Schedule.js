import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Calendar,
  Clock,
  User,
  Car,
  Phone,
  Mail,
  Play,
  CheckCircle,
  Grid3X3,
  List,
  ChevronLeft,
  ChevronRight,
  XCircle
} from 'lucide-react';
import { scheduleAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import StatusBadge from '../../components/UI/StatusBadge';
import CalendarView from '../../components/Schedule/CalendarView';
import toast from 'react-hot-toast';

const Schedule = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'calendar'
  const [currentDate, setCurrentDate] = useState(new Date());
  const { isManager } = useAuth();
  const queryClient = useQueryClient();

  // Fetch schedule data
  const { data: scheduleData, isLoading, error } = useQuery(
    ['schedule', currentPage, searchTerm, statusFilter, typeFilter],
    () => scheduleAPI.getAll({
      page: currentPage,
      limit: 20,
      status: statusFilter,
      type: typeFilter,
    }),
    { select: (data) => data.data }
  );

  // Start appointment mutation
  const startAppointmentMutation = useMutation(
    (id) => scheduleAPI.start(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('schedule');
        toast.success('Appointment started');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to start appointment');
      },
    }
  );

  // Complete appointment mutation
  const completeAppointmentMutation = useMutation(
    ({ id, data }) => scheduleAPI.complete(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('schedule');
        toast.success('Appointment completed');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to complete appointment');
      },
    }
  );

  // Cancel appointment mutation
  const cancelAppointmentMutation = useMutation(
    (id) => scheduleAPI.cancel(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('schedule');
        toast.success('Appointment cancelled');
      },
      onError: (error) => {
        toast.error(error.response?.data?.message || 'Failed to cancel appointment');
      },
    }
  );

  const handleStart = (id) => {
    startAppointmentMutation.mutate(id);
  };

  const handleComplete = (id) => {
    const laborCost = prompt('Enter labor cost (optional):');
    const partsCost = prompt('Enter parts cost (optional):');
    
    const data = {};
    if (laborCost) data.labor = parseFloat(laborCost);
    if (partsCost) data.parts = parseFloat(partsCost);
    
    completeAppointmentMutation.mutate({ id, data });
  };

  const handleAppointmentClick = (appointment) => {
    // You could open a modal or navigate to edit page
    console.log('Appointment clicked:', appointment);
  };

  const handleDateChange = (newDate) => {
    setCurrentDate(newDate);
  };

  const handleCancel = (id, title) => {
    if (window.confirm(`Are you sure you want to cancel "${title}"?`)) {
      cancelAppointmentMutation.mutate(id);
    }
  };

  const statuses = ['scheduled', 'in_progress', 'completed', 'cancelled', 'no_show'];
  const types = ['appointment', 'maintenance', 'repair', 'inspection', 'delivery', 'meeting', 'other'];

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
        <Calendar className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading schedule</h3>
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
          <h1 className="text-2xl font-bold text-gray-900">Schedule</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage appointments and track technician schedules
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('list')}
              className={`flex items-center px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'list'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <List className="w-4 h-4 mr-1" />
              List
            </button>
            <button
              onClick={() => setViewMode('calendar')}
              className={`flex items-center px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'calendar'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Grid3X3 className="w-4 h-4 mr-1" />
              Calendar
            </button>
          </div>

          {isManager && (
            <Link
              to="/schedule/new"
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Appointment
            </Link>
          )}
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Total Appointments</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {scheduleData?.length || 0}
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
                <p className="text-sm font-medium text-gray-500">Completed</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {scheduleData?.filter(s => s.status === 'completed').length || 0}
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
                  <Clock className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">In Progress</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {scheduleData?.filter(s => s.status === 'in_progress').length || 0}
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
                  <User className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Scheduled</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {scheduleData?.filter(s => s.status === 'scheduled').length || 0}
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
                placeholder="Search appointments..."
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
                  {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
                </option>
              ))}
            </select>

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
              <Calendar className="w-4 h-4 mr-2" />
              {scheduleData?.length || 0} appointments found
            </div>
          </div>
        </div>
      </div>

      {/* Calendar or List View */}
      {viewMode === 'calendar' ? (
        <CalendarView
          appointments={scheduleData || []}
          currentDate={currentDate}
          onDateChange={handleDateChange}
          onAppointmentClick={handleAppointmentClick}
        />
      ) : (
        <>
          {/* Schedule list */}
          <div className="space-y-4">
        {scheduleData?.map((appointment) => (
          <div key={appointment._id} className="card">
            <div className="card-body">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-medium text-gray-900">
                      {appointment.title}
                    </h3>
                    <StatusBadge status={appointment.status} type="schedule" />
                  </div>
                  
                  <p className="text-sm text-gray-600 mt-1">
                    {appointment.description}
                  </p>

                  <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="w-4 h-4 mr-2" />
                      <span>
                        {new Date(appointment.startTime).toLocaleString()}
                      </span>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-600">
                      <User className="w-4 h-4 mr-2" />
                      <span>
                        {appointment.assignedTechnician?.username || 'Unassigned'}
                      </span>
                    </div>

                    <div className="flex items-center text-sm text-gray-600">
                      <Calendar className="w-4 h-4 mr-2" />
                      <span className="capitalize">{appointment.type}</span>
                    </div>
                  </div>

                  {/* Customer info */}
                  {appointment.customer && (
                    <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Customer Information</h4>
                      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                        <div className="flex items-center text-sm text-gray-600">
                          <User className="w-4 h-4 mr-2" />
                          <span>{appointment.customer.name}</span>
                        </div>
                        
                        {appointment.customer.phone && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Phone className="w-4 h-4 mr-2" />
                            <a 
                              href={`tel:${appointment.customer.phone}`}
                              className="hover:text-primary-600 transition-colors"
                            >
                              {appointment.customer.phone}
                            </a>
                          </div>
                        )}
                        
                        {appointment.customer.email && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Mail className="w-4 h-4 mr-2" />
                            <a 
                              href={`mailto:${appointment.customer.email}`}
                              className="hover:text-primary-600 transition-colors"
                            >
                              {appointment.customer.email}
                            </a>
                          </div>
                        )}
                        
                        {appointment.customer.vehicle && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Car className="w-4 h-4 mr-2" />
                            <span>
                              {appointment.customer.vehicle.year} {appointment.customer.vehicle.make} {appointment.customer.vehicle.model}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Required parts */}
                  {appointment.requiredParts && appointment.requiredParts.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Required Parts</h4>
                      <div className="space-y-1">
                        {appointment.requiredParts.map((part, index) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">
                              {part.part?.partNumber} - {part.part?.name} (Qty: {part.quantity})
                            </span>
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              part.isAvailable 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {part.isAvailable ? 'Available' : 'Out of Stock'}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="ml-6 flex flex-col space-y-2">
                  <Link
                    to={`/schedule/${appointment._id}/edit`}
                    className="text-primary-600 hover:text-primary-900"
                    title="Edit appointment"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                  
                  {appointment.status === 'scheduled' && (
                    <button
                      onClick={() => handleStart(appointment._id)}
                      className="text-green-600 hover:text-green-900"
                      title="Start appointment"
                      disabled={startAppointmentMutation.isLoading}
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  )}
                  
                  {appointment.status === 'in_progress' && (
                    <button
                      onClick={() => handleComplete(appointment._id)}
                      className="text-blue-600 hover:text-blue-900"
                      title="Complete appointment"
                      disabled={completeAppointmentMutation.isLoading}
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                  )}
                  
                  {appointment.status !== 'completed' && isManager && (
                    <button
                      onClick={() => handleCancel(appointment._id, appointment.title)}
                      className="text-red-600 hover:text-red-900"
                      title="Cancel appointment"
                      disabled={cancelAppointmentMutation.isLoading}
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
          {(!scheduleData || scheduleData.length === 0) && (
            <div className="text-center py-12">
              <Calendar className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No appointments found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm || statusFilter || typeFilter
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Get started by scheduling your first appointment.'}
              </p>
              {isManager && !searchTerm && !statusFilter && !typeFilter && (
                <div className="mt-6">
                  <Link to="/schedule/new" className="btn-primary">
                    <Plus className="w-4 h-4 mr-2" />
                    New Appointment
                  </Link>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Schedule;
