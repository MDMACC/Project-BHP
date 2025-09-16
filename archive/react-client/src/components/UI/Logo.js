import React from 'react';

const Logo = ({ size = 'md', showText = true, className = '' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-20 h-20',
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-lg',
  };

  return (
    <div className={`flex items-center ${className}`}>
      {/* Logo Icon */}
      <div className={`${sizeClasses[size]} relative`}>
        {/* Car Silhouette Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-bluez-800 to-bluez-900 rounded-lg shadow-lg">
          {/* Car Body */}
          <div className="absolute inset-1 bg-gradient-to-r from-bluez-600 to-bluez-700 rounded-md">
            {/* Car Spoiler */}
            <div className="absolute top-0 right-0 w-2 h-1 bg-bluez-800 rounded-tr-md"></div>
            {/* Car Hood */}
            <div className="absolute top-1 left-1 w-3 h-1 bg-bluez-500 rounded-sm"></div>
            {/* Car Windows */}
            <div className="absolute top-2 left-2 w-4 h-2 bg-bluez-400 rounded-sm opacity-60"></div>
          </div>
          
          {/* B.P.H. Text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-white font-bold text-xs tracking-wider">
              B.P.H.
            </div>
          </div>
          
          {/* Gear Wheels */}
          <div className="absolute bottom-0 left-1 w-2 h-2 bg-gradient-to-br from-metallic-600 to-metallic-800 rounded-full border border-metallic-400">
            <div className="absolute inset-0.5 bg-metallic-800 rounded-full"></div>
            <div className="absolute top-0.5 left-0.5 w-1 h-1 bg-metallic-400 rounded-full"></div>
          </div>
          <div className="absolute bottom-0 right-1 w-2 h-2 bg-gradient-to-br from-metallic-600 to-metallic-800 rounded-full border border-metallic-400">
            <div className="absolute inset-0.5 bg-metallic-800 rounded-full"></div>
            <div className="absolute top-0.5 left-0.5 w-1 h-1 bg-metallic-400 rounded-full"></div>
          </div>
        </div>
        
        {/* Metallic Shine Effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 rounded-lg animate-shimmer"></div>
      </div>
      
      {/* Shop Name */}
      {showText && (
        <div className="ml-3">
          <div className={`font-bold text-bluez-900 ${textSizeClasses[size]}`}>
            Bluez PowerHouse
          </div>
          <div className={`text-metallic-600 ${textSizeClasses[size]} text-xs`}>
            250 W Spazier Ave 101, Burbank, CA 91502
          </div>
        </div>
      )}
    </div>
  );
};

export default Logo;
