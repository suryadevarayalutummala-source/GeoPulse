import React from 'react';
import { HardHat, Home, TrendingUp } from 'lucide-react';

export default function RoleSwitcher({ activeRole, setActiveRole }) {
  const roles = [
    {
      id: 'builder',
      label: 'Builder',
      icon: HardHat,
      emoji: '🏗️',
      description: 'Soil Bearing Capacity • Water Table • Max Floors',
      activeBg: 'bg-forest-800 text-beige-100 shadow-md shadow-forest-900/15 border-forest-700'
    },
    {
      id: 'homebuyer',
      label: 'Homebuyer',
      icon: Home,
      emoji: '🏡',
      description: 'Parks & Greenery • Commute • Schools & Hospitals',
      activeBg: 'bg-sage-700 text-beige-100 shadow-md shadow-sage-900/15 border-sage-600'
    },
    {
      id: 'investor',
      label: 'Investor',
      icon: TrendingUp,
      emoji: '📈',
      description: 'Price / sqft • 5-Yr ROI % • Infra Pipeline',
      activeBg: 'bg-olive-700 text-beige-100 shadow-md shadow-olive-900/15 border-olive-600'
    }
  ];

  return (
    <div className="w-full glass-panel border-b border-forest-600/20 py-2.5 px-4 lg:px-8">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        
        <div className="flex items-center space-x-2 text-xs font-extrabold text-forest-950 uppercase tracking-wider">
          <span>Analysis Perspective:</span>
        </div>

        {/* 3 Role Segmented Buttons */}
        <div className="grid grid-cols-3 gap-2 w-full sm:w-auto bg-beige-200/90 p-1.5 rounded-2xl border border-sage-300/60">
          {roles.map((role) => {
            const Icon = role.icon;
            const isActive = activeRole === role.id;
            return (
              <button
                key={role.id}
                onClick={() => setActiveRole(role.id)}
                className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all flex items-center justify-center space-x-2 border cursor-pointer ${
                  isActive
                    ? role.activeBg
                    : 'bg-transparent text-forest-800 hover:text-forest-950 hover:bg-beige-300/60 border-transparent'
                }`}
              >
                <span className="text-base">{role.emoji}</span>
                <span className="capitalize">{role.label}</span>
              </button>
            );
          })}
        </div>

        {/* Perspective Description */}
        <div className="hidden lg:block text-xs font-medium text-forest-800 italic">
          {roles.find((r) => r.id === activeRole)?.description}
        </div>

      </div>
    </div>
  );
}
