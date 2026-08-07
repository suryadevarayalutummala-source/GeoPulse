import React, { useState } from 'react';
import { Layers, Mail, Lock, ArrowRight, ShieldCheck, Eye, EyeOff, Sparkles, HardHat, Home, TrendingUp, UserCheck } from 'lucide-react';

export default function LoginPage({ onLoginSuccess, onNavigateLanding }) {
  const [email, setEmail] = useState('alex.vance@geoestate.ai');
  const [password, setPassword] = useState('••••••••••••');
  const [selectedRole, setSelectedRole] = useState('builder');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isRegisterMode, setIsRegisterMode] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      onLoginSuccess({
        name: 'Alex Vance',
        email: email || 'alex.vance@geoestate.ai',
        role: selectedRole,
        avatar: 'AV'
      });
    }, 600);
  };

  const handleDemoLogin = (role) => {
    setSelectedRole(role);
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      onLoginSuccess({
        name: 'Alex Vance',
        email: `${role}.demo@geopulse.ai`,
        role: role,
        avatar: 'AV'
      });
    }, 400);
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-8 relative overflow-hidden">
      {/* Subtle Background Glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-tr from-sage-300/30 via-beige-300/25 to-olive-200/30 rounded-full blur-[140px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        
        {/* Top Logo & Header */}
        <div className="text-center mb-6 cursor-pointer" onClick={onNavigateLanding}>
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-forest-800 via-forest-700 to-sage-600 shadow-md shadow-forest-900/15 mb-3">
            <Layers className="w-6 h-6 text-beige-100" />
          </div>
          <h1 className="text-2xl font-extrabold font-heading text-forest-950">
            {isRegisterMode ? 'Create your GeoPulse Account' : 'Welcome back to GeoPulse'}
          </h1>
          <p className="text-xs text-forest-700 font-medium mt-1">
            {isRegisterMode
              ? 'Join the spatial real estate intelligence platform'
              : 'Sign in to access AI land analytics & 3-perspective mapping'}
          </p>
        </div>

        {/* Login Form Card */}
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-forest-600/20 shadow-lg bg-beige-100/90">
          
          {/* Quick Role Selection Tabs */}
          <div className="mb-5">
            <label className="block text-[11px] font-extrabold text-forest-800 uppercase tracking-wide mb-2">
              Select Primary Access Perspective:
            </label>
            <div className="grid grid-cols-3 gap-1.5 bg-beige-200/80 p-1 rounded-xl border border-sage-300/60">
              <button
                type="button"
                onClick={() => setSelectedRole('builder')}
                className={`py-2 px-1 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1 ${
                  selectedRole === 'builder'
                    ? 'bg-forest-800 text-beige-100 shadow-sm'
                    : 'text-forest-800 hover:text-forest-950'
                }`}
              >
                <HardHat className="w-3.5 h-3.5" />
                <span>Builder</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedRole('homebuyer')}
                className={`py-2 px-1 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1 ${
                  selectedRole === 'homebuyer'
                    ? 'bg-sage-700 text-beige-100 shadow-sm'
                    : 'text-forest-800 hover:text-forest-950'
                }`}
              >
                <Home className="w-3.5 h-3.5" />
                <span>Homebuyer</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedRole('investor')}
                className={`py-2 px-1 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1 ${
                  selectedRole === 'investor'
                    ? 'bg-olive-700 text-beige-100 shadow-sm'
                    : 'text-forest-800 hover:text-forest-950'
                }`}
              >
                <TrendingUp className="w-3.5 h-3.5" />
                <span>Investor</span>
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            
            {/* Email Field */}
            <div>
              <label className="block text-xs font-bold text-forest-900 mb-1.5">
                Work Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-forest-700 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl text-xs glass-input focus:ring-1 focus:ring-forest-600 transition-all font-semibold"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-forest-900">
                  Password
                </label>
                {!isRegisterMode && (
                  <a href="#forgot" onClick={(e) => e.preventDefault()} className="text-[11px] font-bold text-forest-700 hover:underline">
                    Forgot password?
                  </a>
                )}
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-forest-700 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl text-xs glass-input focus:ring-1 focus:ring-forest-600 transition-all font-semibold"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-forest-700 hover:text-forest-950"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <div className="flex items-center justify-between text-xs text-forest-800 font-semibold pt-1">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded border-sage-400 text-forest-800 focus:ring-forest-600" />
                <span>Keep me signed in</span>
              </label>
              <span className="text-[10px] text-forest-700">Encrypted 256-bit</span>
            </div>

            {/* Main Submit CTA */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 rounded-xl bg-forest-800 hover:bg-forest-900 text-beige-100 font-extrabold text-xs flex items-center justify-center space-x-2 transition-all shadow-md cursor-pointer disabled:opacity-50 mt-2"
            >
              {isLoading ? (
                <span>Authenticating GeoPulse...</span>
              ) : (
                <>
                  <span>{isRegisterMode ? 'Create GeoPulse Account' : 'Sign In to Dashboard'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Login Preset */}
          <div className="mt-6 pt-5 border-t border-sage-300/60">
            <div className="text-[11px] font-bold text-forest-700 text-center mb-2.5 uppercase tracking-wider flex items-center justify-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 text-forest-800" />
              <span>Instant Hackathon Demo Login</span>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleDemoLogin('builder')}
                className="py-1.5 px-2 rounded-lg bg-beige-200 hover:bg-sage-200 border border-sage-300 text-[10px] font-extrabold text-forest-950 transition-all flex items-center justify-center space-x-1"
              >
                <span>🏗️ Builder</span>
              </button>
              <button
                type="button"
                onClick={() => handleDemoLogin('homebuyer')}
                className="py-1.5 px-2 rounded-lg bg-beige-200 hover:bg-sage-200 border border-sage-300 text-[10px] font-extrabold text-forest-950 transition-all flex items-center justify-center space-x-1"
              >
                <span>🏡 Homebuyer</span>
              </button>
              <button
                type="button"
                onClick={() => handleDemoLogin('investor')}
                className="py-1.5 px-2 rounded-lg bg-beige-200 hover:bg-sage-200 border border-sage-300 text-[10px] font-extrabold text-forest-950 transition-all flex items-center justify-center space-x-1"
              >
                <span>📈 Investor</span>
              </button>
            </div>
          </div>

          {/* Bottom Switch Mode Toggle */}
          <div className="mt-5 text-center text-xs text-forest-800 font-semibold">
            {isRegisterMode ? (
              <span>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsRegisterMode(false)}
                  className="font-extrabold text-forest-950 underline hover:text-forest-700"
                >
                  Sign In
                </button>
              </span>
            ) : (
              <span>
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsRegisterMode(true)}
                  className="font-extrabold text-forest-950 underline hover:text-forest-700"
                >
                  Create One
                </button>
              </span>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
