import React, { useState } from 'react';
import Navbar from './components/Navbar';
import LandingHero from './components/LandingHero';
import RoleSwitcher from './components/RoleSwitcher';
import LeftSidebar from './components/LeftSidebar';
import MapView from './components/MapView';
import RightAnalyticsPanel from './components/RightAnalyticsPanel';
import AiChatAdvisor from './components/AiChatAdvisor';
import DetailDrawer from './components/DetailDrawer';
import LoginPage from './components/LoginPage';
import { PLOTS_DATA } from './data/plots';

export default function App() {
  const [viewMode, setViewMode] = useState('landing'); // 'landing' | 'dashboard' | 'login'
  const [activeNavTab, setActiveNavTab] = useState('overview'); // 'overview' | 'dashboard' | 'ai-advisor'
  const [activeRole, setActiveRole] = useState('builder'); // 'builder' | 'homebuyer' | 'investor'
  const [selectedPlot, setSelectedPlot] = useState(PLOTS_DATA[0]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerPlot, setDrawerPlot] = useState(null);
  
  // User Authentication State
  const [user, setUser] = useState({
    name: 'Alex Vance',
    email: 'alex.vance@geoestate.ai',
    role: 'builder',
    avatar: 'AV'
  });

  const handleSelectRoleFromLanding = (role) => {
    setActiveRole(role);
    setViewMode('dashboard');
    setActiveNavTab('dashboard');
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'auto' });
      const mainEl = document.getElementById('dashboard-top-section');
      if (mainEl) mainEl.scrollTop = 0;
    }, 50);
  };

  const handleOpenDetails = (plot) => {
    setDrawerPlot(plot || selectedPlot);
    setIsDrawerOpen(true);
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    if (userData.role) {
      setActiveRole(userData.role);
    }
    setViewMode('landing');
    setActiveNavTab('overview');
  };

  return (
    <div className="min-h-screen bg-beige-150 text-forest-950 flex flex-col font-sans selection:bg-sage-500 selection:text-white">
      {/* Top Header Navbar */}
      <Navbar
        activeRole={activeRole}
        setActiveRole={setActiveRole}
        viewMode={viewMode}
        setViewMode={setViewMode}
        activeNavTab={activeNavTab}
        setActiveNavTab={setActiveNavTab}
        user={user}
        setUser={setUser}
      />

      {/* Main View Router */}
      {viewMode === 'login' ? (
        <main className="flex-1">
          <LoginPage
            onLoginSuccess={handleLoginSuccess}
            onNavigateLanding={() => {
              setViewMode('landing');
              setActiveNavTab('overview');
            }}
          />
        </main>
      ) : viewMode === 'landing' ? (
        <main className="flex-1">
          <LandingHero onSelectRole={handleSelectRoleFromLanding} />
        </main>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden">
          
          {/* Segmented Control Role Switcher */}
          <RoleSwitcher
            activeRole={activeRole}
            setActiveRole={setActiveRole}
          />

          {/* Main Dashboard Responsive Workspace */}
          <main id="dashboard-top-section" className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-6 flex flex-col space-y-4 lg:space-y-6 overflow-y-auto">
            
            {/* Top Workspace Grid: Left Inventory | Center Map | Right Role Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6 min-h-[580px]">
              
              {/* Left Sidebar Inventory */}
              <div className="lg:col-span-3 h-[480px] lg:h-auto">
                <LeftSidebar
                  plots={PLOTS_DATA}
                  selectedPlot={selectedPlot}
                  onSelectPlot={setSelectedPlot}
                />
              </div>

              {/* Center Interactive Mapbox Map */}
              <div className="lg:col-span-5 h-[480px] lg:h-auto">
                <MapView
                  plots={PLOTS_DATA}
                  selectedPlot={selectedPlot}
                  onSelect={setSelectedPlot}
                  onOpenDetails={handleOpenDetails}
                />
              </div>

              {/* Right Analytics Panel (Changes per Role) */}
              <div className="lg:col-span-4 h-auto">
                <RightAnalyticsPanel
                  selectedPlot={selectedPlot}
                  activeRole={activeRole}
                  onOpenDetails={handleOpenDetails}
                />
              </div>

            </div>

            {/* Bottom Row: AI Chat Advisor */}
            <div className="w-full">
              <AiChatAdvisor
                selectedPlot={selectedPlot}
                activeRole={activeRole}
                setActiveRole={setActiveRole}
              />
            </div>

          </main>
        </div>
      )}

      {/* Detail Slide-Over Drawer */}
      <DetailDrawer
        plot={drawerPlot}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />

      {/* Global Footer */}
      <footer className="w-full glass-panel border-t border-forest-600/20 py-4 px-6 text-center text-xs text-forest-800 font-semibold">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            GeoPulse © 2026 — Smart Spatial Analytics & Real Estate Intelligence
          </div>
          <div className="flex items-center space-x-3 text-forest-800 font-semibold">
            <span>One Map. Three Perspectives.</span>
            <span>•</span>
            <span className="text-forest-950 font-extrabold">Mapbox GL JS + React + Tailwind</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
