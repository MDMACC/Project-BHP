import React from 'react';
import { ChevronLeft, ChevronRight, Clock, User, Car } from 'lucide-react';
import StatusBadge from '../UI/StatusBadge';

const CalendarView = ({ 
  appointments, 
  currentDate, 
  onDateChange, 
  onAppointmentClick 
}) => {
  const today = new Date();
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  // Get first day of month and number of days
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const daysInMonth = lastDay.getDate();
  const startingDayOfWeek = firstDay.getDay();

  // Generate calendar days
  const calendarDays = [];
  
  // Add empty cells for days before the first day of the month
  for (let i = 0; i < startingDayOfWeek; i++) {
    calendarDays.push(null);
  }
  
  // Add days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push(new Date(year, month, day));
  }

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const getAppointmentsForDate = (date) => {
    if (!date || !appointments) return [];
    const dateStr = date.toISOString().split('T')[0];
    return appointments.filter(apt => apt.date === dateStr);
  };

  const isToday = (date) => {
    if (!date) return false;
    return date.toDateString() === today.toDateString();
  };

  const isCurrentMonth = (date) => {
    if (!date) return false;
    return date.getMonth() === month;
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(month + direction);
    onDateChange(newDate);
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Calendar Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <button
          onClick={() => navigateMonth(-1)}
          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        
        <h2 className="text-lg font-semibold text-gray-900">
          {monthNames[month]} {year}
        </h2>
        
        <button
          onClick={() => navigateMonth(1)}
          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Day Headers */}
      <div className="grid grid-cols-7 border-b border-gray-200">
        {dayNames.map(day => (
          <div key={day} className="p-3 text-center text-sm font-medium text-gray-500 bg-gray-50">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7">
        {calendarDays.map((date, index) => {
          const dayAppointments = getAppointmentsForDate(date);
          const isCurrentDay = isToday(date);
          const isCurrentMonthDay = isCurrentMonth(date);

          return (
            <div
              key={index}
              className={`min-h-24 p-2 border-r border-b border-gray-200 ${
                isCurrentMonthDay ? 'bg-white' : 'bg-gray-50'
              } ${isCurrentDay ? 'bg-bluez-50' : ''}`}
            >
              {date && (
                <>
                  {/* Day Number */}
                  <div className={`text-sm font-medium mb-1 ${
                    isCurrentDay 
                      ? 'text-bluez-600' 
                      : isCurrentMonthDay 
                        ? 'text-gray-900' 
                        : 'text-gray-400'
                  }`}>
                    {date.getDate()}
                  </div>

                  {/* Appointments */}
                  <div className="space-y-1">
                    {dayAppointments.slice(0, 2).map((appointment) => (
                      <div
                        key={appointment._id}
                        onClick={() => onAppointmentClick(appointment)}
                        className={`text-xs p-1 rounded cursor-pointer truncate ${
                          appointment.status === 'confirmed' 
                            ? 'bg-green-100 text-green-800' 
                            : appointment.status === 'pending'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                        title={`${appointment.time} - ${appointment.customerName}`}
                      >
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span className="truncate">{appointment.time}</span>
                        </div>
                        <div className="truncate font-medium">
                          {appointment.customerName}
                        </div>
                      </div>
                    ))}
                    
                    {dayAppointments.length > 2 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{dayAppointments.length - 2} more
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CalendarView;
