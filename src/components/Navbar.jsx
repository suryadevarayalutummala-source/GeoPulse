import React, { useState } from 'react';
import { Layers, MapPin, Compass, Bot, User, LogIn, LogOut, ChevronDown } from 'lucide-react';

export default function Navbar({ activeRole, setActiveRole, viewMode, setViewMode, activeNavTab, setActiveNavTab, user, setUser }) {
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const roleConfig = {
    builder: { label: 'Builder', icon: '🏗️', color: 'border-forest-600/30 text-forest-900 bg-sage-200/80' },
    homebuyer: { label: 'Homebuyer', icon: '🏡', color: 'border-olive-600/30 text-forest-900 bg-olive-200/80' },
    investor: { label: 'Investor', icon: '📈', color: 'border-sage-600/30 text-forest-900 bg-beige-300/80' }
  };

  const currentRole = roleConfig[activeRole] || roleConfig.builder;

  const currentTab = viewMode === 'landing' ? 'overview' : (activeNavTab || 'dashboard');

  const handleNavToOverview = () => {
    setViewMode('landing');
    if (setActiveNavTab) setActiveNavTab('overview');
  };

  const handleNavToDashboard = () => {
    setViewMode('dashboard');
    if (setActiveNavTab) setActiveNavTab('dashboard');
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      const mainEl = document.getElementById('dashboard-top-section');
      if (mainEl) mainEl.scrollTop = 0;
    }, 50);
  };

  const handleNavToAiAdvisor = () => {
    setViewMode('dashboard');
    if (setActiveNavTab) setActiveNavTab('ai-advisor');
    setTimeout(() => {
      const aiSection = document.getElementById('ai-advisor-section');
      if (aiSection) {
        aiSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 120);
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-forest-600/20 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* GeoPulse Logo & Tagline */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={handleNavToOverview}>
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-forest-800 via-forest-700 to-sage-600 shadow-md shadow-forest-900/10">
            <Layers className="w-5 h-5 text-beige-100" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-sage-300 rounded-full border-2 border-beige-100 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-heading font-extrabold text-xl tracking-tight text-forest-950">
                GeoPulse
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-extrabold tracking-wider text-forest-900 bg-sage-200 border border-sage-400/50 rounded uppercase">
                AI Platform
              </span>
            </div>
            <p className="text-[11px] text-forest-700 font-medium hidden sm:block">
              Land Analytics • 3 Perspectives
            </p>
          </div>
        </div>

        {/* Center Nav Items: Overview, Dashboard, AI Advisor */}
        <nav className="hidden md:flex items-center space-x-1 bg-beige-200/90 p-1.5 rounded-xl border border-sage-300/50 shadow-inner">
          <button
            onClick={handleNavToOverview}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer ${
              currentTab === 'overview'
                ? 'bg-sage-600 text-beige-50 shadow-sm'
                : 'text-forest-800 hover:text-forest-950 hover:bg-beige-300/60'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Overview</span>
          </button>

          <button
            onClick={handleNavToDashboard}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer ${
              currentTab === 'dashboard'
                ? 'bg-sage-600 text-beige-50 shadow-sm'
                : 'text-forest-800 hover:text-forest-950 hover:bg-beige-300/60'
            }`}
          >
            <MapPin className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={handleNavToAiAdvisor}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-extrabold transition-all cursor-pointer ${
              currentTab === 'ai-advisor'
                ? 'bg-sage-600 text-beige-50 shadow-sm'
                : 'text-forest-800 hover:text-forest-950 hover:bg-beige-300/60'
            }`}
          >
            <Bot className="w-3.5 h-3.5 text-forest-700" />
            <span>AI Advisor</span>
          </button>
        </nav>

        {/* Right Role Badge & Authentication Action */}
        <div className="flex items-center space-x-3">
          <div className={`hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-bold ${currentRole.color} transition-all shadow-sm`}>
            <span>{currentRole.icon}</span>
            <span className="capitalize">{currentRole.label} View</span>
          </div>

          {/* User Profile / Login Action */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                className="flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-beige-200 border border-sage-300/60 cursor-pointer hover:bg-beige-300/60 transition-all"
              >
                <div className="w-7 h-7 rounded-lg bg-forest-800 flex items-center justify-center text-beige-100 font-extrabold text-xs shadow-sm">
                  {user.avatar || 'AV'}
                </div>
                <div className="hidden lg:block text-left pr-1">
                  <div className="text-[11px] font-bold text-forest-950 leading-tight">{user.name || 'Alex Vance'}</div>
                  <div className="text-[9px] text-forest-700 font-semibold capitalize">{user.role || activeRole} Mode</div>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-forest-700" />
              </button>

              {/* Profile Dropdown */}
              {showProfileMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-beige-100 rounded-xl border border-sage-300 shadow-xl py-1 z-50 animate-fade-in">
                  <div className="px-3 py-2 border-b border-sage-300/60">
                    <div className="text-xs font-extrabold text-forest-950">{user.name}</div>
                    <div className="text-[10px] text-forest-700 font-medium truncate">{user.email}</div>
                  </div>
                  <button
                    onClick={() => {
                      handleNavToDashboard();
                      setShowProfileMenu(false);
                    }}
                    className="w-full text-left px-3 py-2 text-xs font-bold text-forest-900 hover:bg-beige-200 flex items-center space-x-2"
                  >
                    <MapPin className="w-3.5 h-3.5" />
                    <span>Open Dashboard</span>
                  </button>
                  <button
                    onClick={() => {
                      setUser(null);
                      setShowProfileMenu(false);
                      setViewMode('login');
                    }}
                    className="w-full text-left px-3 py-2 text-xs font-bold text-rose-700 hover:bg-rose-100/60 flex items-center space-x-2 border-t border-sage-300/40"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={() => setViewMode('login')}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
                viewMode === 'login'
                  ? 'bg-forest-900 text-beige-100 shadow-sm'
                  : 'bg-forest-800 hover:bg-forest-900 text-beige-100 shadow-sm'
              }`}
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </button>
          )}
        </div>

      </div>
    </header>
  );
}
