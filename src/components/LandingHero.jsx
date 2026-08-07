import React from 'react';
import { ArrowRight, HardHat, Home, TrendingUp, ShieldCheck, Cpu, MapPin, Sparkles, Layers } from 'lucide-react';

export default function LandingHero({ onSelectRole }) {
  const roles = [
    {
      id: 'builder',
      title: 'Builder Perspective',
      badge: 'Engineering & Construction',
      icon: '🏗️',
      IconComponent: HardHat,
      color: 'from-sage-200/90 via-beige-200/90 to-beige-100/95',
      borderColor: 'hover:border-forest-600/60',
      accentColor: 'text-forest-900',
      btnBg: 'bg-forest-800 hover:bg-forest-900 text-beige-100 border-forest-700',
      description: 'View construction feasibility, soil bearing capacity (kPa), flood risk zones, water table depth (m), utility access grid, and maximum permissible floors.',
      features: ['Soil Bearing Capacity (kPa)', 'Water Table & Flood Risk Zone', 'Utility Grid Readiness', 'Construction Cost / sqft']
    },
    {
      id: 'homebuyer',
      title: 'Homebuyer Perspective',
      badge: 'Lifestyle & Community',
      icon: '🏡',
      IconComponent: Home,
      color: 'from-beige-300/90 via-beige-200/90 to-beige-100/95',
      borderColor: 'hover:border-sage-600/60',
      accentColor: 'text-forest-900',
      btnBg: 'bg-sage-700 hover:bg-sage-800 text-beige-100 border-sage-600',
      description: 'Discover nearby top-rated schools, hospitals, transit hubs, green parks, daily commute times, and family-friendly neighborhood metrics.',
      features: ['Top K-12 Schools & Hospitals', 'Transit & Metro Hub Proximity', 'Greenery & Park Proximity', 'Commute Time Calculator']
    },
    {
      id: 'investor',
      title: 'Investor Perspective',
      badge: 'ROI & Financial Growth',
      icon: '📈',
      IconComponent: TrendingUp,
      color: 'from-olive-200/90 via-beige-200/90 to-beige-100/95',
      borderColor: 'hover:border-olive-600/60',
      accentColor: 'text-forest-900',
      btnBg: 'bg-olive-700 hover:bg-olive-800 text-beige-100 border-olive-600',
      description: 'Analyze multi-year price growth trends (Recharts), estimated 5-year ROI %, rental yield %, algorithmic risk scoring, and major government infrastructure pipelines.',
      features: ['Historical Appreciation Chart', 'Estimated Rental Yield %', 'Algorithmic Risk Profiling', 'Infra Pipeline Radar']
    }
  ];

  return (
    <div className="relative overflow-hidden pt-12 pb-16 lg:pt-16 lg:pb-20">
      {/* Background Decorative Gradients - Soft Sage & Olive Tints */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-sage-300/30 via-beige-300/25 to-olive-200/30 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-96 h-96 bg-sage-200/40 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Top Announcement Badge */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full glass-card border border-forest-600/30 text-xs font-bold text-forest-900 shadow-sm">
            <Sparkles className="w-4 h-4 text-forest-700 animate-pulse" />
            <span>GeoPulse AI Land Analytics</span>
            <span className="w-1.5 h-1.5 rounded-full bg-forest-700" />
            <span className="text-forest-800 font-semibold">Spatial Mapbox Integration</span>
          </div>
        </div>

        {/* Hero Headline & Subtitle */}
        <div className="text-center max-w-4xl mx-auto space-y-6">
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold font-heading tracking-tight text-forest-950 leading-tight">
            One Map.{' '}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-forest-800 via-forest-700 to-sage-700">
              Three Perspectives.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-forest-900 font-medium max-w-2xl mx-auto leading-relaxed">
            Analyze land parcels with AI-powered insights tailored specifically for{' '}
            <strong className="text-forest-950 font-extrabold">Builders</strong>,{' '}
            <strong className="text-forest-950 font-extrabold">Homebuyers</strong>, and{' '}
            <strong className="text-forest-950 font-extrabold">Investors</strong>.
          </p>

          {/* Large CTA Button */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => onSelectRole('builder')}
              className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-forest-800 hover:bg-forest-900 text-beige-100 font-extrabold text-base shadow-lg shadow-forest-900/15 flex items-center justify-center space-x-3 group transition-all transform hover:-translate-y-0.5 cursor-pointer"
            >
              <span>Launch GeoPulse Dashboard</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform text-beige-100" />
            </button>
          </div>
        </div>

        {/* Three Perspective Role Cards */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          {roles.map((role) => {
            const Icon = role.IconComponent;
            return (
              <div
                key={role.id}
                onClick={() => onSelectRole(role.id)}
                className={`group relative glass-card p-8 rounded-3xl cursor-pointer border border-sage-300 ${role.borderColor} bg-gradient-to-b ${role.color} flex flex-col justify-between hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1.5`}
              >
                <div>
                  {/* Top Card Icon & Badge */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="w-14 h-14 rounded-2xl bg-beige-100 border border-sage-300 flex items-center justify-center text-2xl shadow-sm group-hover:scale-110 transition-transform">
                      {role.icon}
                    </div>
                    <span className="text-[11px] font-extrabold tracking-wider px-3 py-1 rounded-full bg-beige-100 border border-sage-300 text-forest-900 uppercase">
                      {role.badge}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <h3 className="text-2xl font-extrabold font-heading text-forest-950 mb-3 flex items-center space-x-2">
                    <span>{role.title}</span>
                  </h3>

                  <p className="text-sm text-forest-800 font-medium leading-relaxed mb-6">
                    {role.description}
                  </p>

                  {/* Feature Checklist */}
                  <div className="space-y-2 mb-8">
                    {role.features.map((feat, idx) => (
                      <div key={idx} className="flex items-center space-x-2 text-xs text-forest-900 font-semibold">
                        <div className={`w-1.5 h-1.5 rounded-full bg-forest-700`} />
                        <span>{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Bottom Action CTA */}
                <button
                  className={`w-full py-3 px-4 rounded-xl border font-extrabold text-sm flex items-center justify-center space-x-2 transition-all shadow-xs ${role.btnBg}`}
                >
                  <span>Select {role.title.split(' ')[0]} View</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
