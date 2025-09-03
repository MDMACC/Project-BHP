import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react';

const CountdownTimer = ({ endTime, className = '' }) => {
  const [timeLeft, setTimeLeft] = useState(0);
  const [isOverdue, setIsOverdue] = useState(false);

  useEffect(() => {
    if (!endTime) return;

    const calculateTimeLeft = () => {
      const now = new Date().getTime();
      const end = new Date(endTime).getTime();
      const difference = end - now;

      if (difference > 0) {
        setTimeLeft(difference);
        setIsOverdue(false);
      } else {
        setTimeLeft(0);
        setIsOverdue(true);
      }
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);

    return () => clearInterval(timer);
  }, [endTime]);

  const formatTime = (milliseconds) => {
    const days = Math.floor(milliseconds / (1000 * 60 * 60 * 24));
    const hours = Math.floor((milliseconds % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);

    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  };

  const getStatusInfo = () => {
    if (isOverdue) {
      return {
        icon: <AlertTriangle className="w-4 h-4" />,
        text: 'Overdue',
        className: 'countdown-overdue',
        bgColor: 'bg-danger-50',
        borderColor: 'border-danger-200',
      };
    }

    const hours = Math.floor(timeLeft / (1000 * 60 * 60));
    
    if (hours < 24) {
      return {
        icon: <Clock className="w-4 h-4" />,
        text: 'Urgent',
        className: 'countdown-urgent',
        bgColor: 'bg-warning-50',
        borderColor: 'border-warning-200',
      };
    }

    return {
      icon: <Clock className="w-4 h-4" />,
      text: 'Normal',
      className: 'countdown-normal',
      bgColor: 'bg-primary-50',
      borderColor: 'border-primary-200',
    };
  };

  if (!endTime) {
    return (
      <div className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-600 ${className}`}>
        <CheckCircle className="w-4 h-4 mr-1" />
        No deadline
      </div>
    );
  }

  const statusInfo = getStatusInfo();

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-md text-sm font-medium border ${statusInfo.bgColor} ${statusInfo.borderColor} ${statusInfo.className} ${className}`}>
      {statusInfo.icon}
      <span className="ml-1">
        {isOverdue ? 'Overdue' : formatTime(timeLeft)}
      </span>
    </div>
  );
};

export default CountdownTimer;
