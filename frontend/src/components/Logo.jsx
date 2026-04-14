import React from 'react';

const Logo = ({ className = "h-8 w-auto", showText = true }) => {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* The Graphical Mark */}
      <div className="relative flex items-center justify-center">
        {/* Outer Ring / Aperture */}
        <svg 
          viewBox="0 0 100 100" 
          className="w-8 h-8 md:w-10 md:h-10 text-odisha-primary"
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Stylized Leaf Silhouette Background */}
          <path 
            d="M50 10C27.9 10 10 27.9 10 50C10 72.1 27.9 90 50 90C72.1 90 90 72.1 90 50C90 27.9 72.1 10 50 10ZM50 82C32.3 82 18 67.7 18 50C18 32.3 32.3 18 50 18C67.7 18 82 32.3 82 50C82 67.7 67.7 82 50 82Z" 
            fill="currentColor" 
            fillOpacity="0.1" 
          />
          
          {/* Main Leaf Body */}
          <path 
            d="M50 20C55 35 70 50 80 50C70 50 55 65 50 80C45 65 30 50 20 50C30 50 45 35 50 20Z" 
            fill="currentColor"
          />
          
          {/* Central Detection Eye/Lens */}
          <circle cx="50" cy="50" r="8" fill="white" />
          <circle cx="50" cy="50" r="4" fill="#E67E22" /> {/* Odisha Terracotta Orange */}
          
          {/* Perspective Lines for 'Scanning' effect */}
          <path 
            d="M30 30L40 40M70 70L60 60M30 70L40 60M70 30L60 40" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
          />
        </svg>
      </div>

      {/* Brand Text */}
      {showText && (
        <div className="flex flex-col leading-tight">
          <span className="text-xl md:text-2xl font-black tracking-tight text-[#2C3E50]">
            COD<span className="text-odisha-primary">-</span>Odisha
          </span>
          <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-gray-400">
            Detection Portal
          </span>
        </div>
      )}
    </div>
  );
};

export default Logo;
