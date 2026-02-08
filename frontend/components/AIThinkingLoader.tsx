'use client';

import { useEffect, useState } from 'react';

interface AIThinkingLoaderProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function AIThinkingLoader({ 
  message = "AI is thinking...", 
  size = 'md' 
}: AIThinkingLoaderProps) {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  };

  return (
    <div className="flex flex-col items-center justify-center gap-6 p-8">
      <div className={`relative ${sizeClasses[size]} flex items-center justify-center`}>
        
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-400/20 via-purple-400/20 to-pink-400/20 blur-xl animate-pulse" />
        
        <div className="absolute inset-0 animate-spin-slow">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-gradient-to-r from-cyan-400 to-cyan-300 rounded-full shadow-lg shadow-cyan-400/50" />
          <div className="absolute top-1/2 right-0 -translate-y-1/2 w-2.5 h-2.5 bg-gradient-to-r from-purple-400 to-purple-300 rounded-full shadow-lg shadow-purple-400/50" />
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-gradient-to-r from-pink-400 to-pink-300 rounded-full shadow-lg shadow-pink-400/50" />
          <div className="absolute top-1/2 left-0 -translate-y-1/2 w-2.5 h-2.5 bg-gradient-to-r from-cyan-400 to-cyan-300 rounded-full shadow-lg shadow-cyan-400/50" />
        </div>

        <div className="absolute inset-2 animate-spin-reverse">
          <div className="absolute top-0 right-1/4 w-1.5 h-1.5 bg-purple-300 rounded-full shadow-md shadow-purple-300/50" />
          <div className="absolute bottom-0 left-1/4 w-1.5 h-1.5 bg-pink-300 rounded-full shadow-md shadow-pink-300/50" />
        </div>

        <div className="relative z-10 w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/10">
          <div className="absolute inset-2 rounded-full bg-gradient-to-br from-cyan-400/30 to-purple-400/30 blur-sm animate-pulse" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-3 h-3 bg-gradient-to-r from-cyan-300 to-purple-300 rounded-full shadow-lg shadow-cyan-400/50 animate-ping" />
            <div className="absolute w-3 h-3 bg-white rounded-full" />
          </div>
        </div>

        <div className="absolute inset-0 rounded-full border border-dashed border-cyan-400/20 animate-spin-slower" />
        <div className="absolute inset-2 rounded-full border border-dashed border-purple-400/20 animate-spin-reverse-slower" />
      </div>

      {message && (
        <div className="text-center">
          <p className="text-white/90 text-lg font-medium">
            {message}{dots}
          </p>
          <p className="text-white/50 text-sm mt-2">
            Creating viral content magic ✨
          </p>
        </div>
      )}
    </div>
  );
}