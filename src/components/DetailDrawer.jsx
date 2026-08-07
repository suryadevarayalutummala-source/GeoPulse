import React from 'react';
import { X, MapPin, Building2, ShieldCheck, Zap, Layers, CheckCircle2, Compass, HardHat, Home, TrendingUp, Trees } from 'lucide-react';

export default function DetailDrawer({ plot, isOpen, onClose }) {
  if (!isOpen || !plot) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-forest-950/40 backdrop-blur-sm transition-opacity animate-fade-in">
      <div className="w-full max-w-xl h-full glass-panel bg-beige-100/98 border-l border-sage-300 p-6 flex flex-col space-y-6 overflow-y-auto shadow-2xl">
        
        {/* Top Drawer Bar */}
        <div className="flex items-center justify-between border-b border-sage-300 pb-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold text-forest-950 bg-sage-200 px-2 py-0.5 rounded border border-sage-400/50">
                {plot.plot_id}
              </span>
              <span className="text-xs font-bold text-forest-900 bg-beige-200 px-2 py-0.5 rounded border border-sage-300">
                {plot.zoning_type} Zone
              </span>
            </div>
            <h2 className="text-xl font-extrabold text-forest-950 mt-1">
              {plot.name}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-beige-200 hover:bg-beige-300 text-forest-800 hover:text-forest-950 border border-sage-300 transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Ownership & Location Banner */}
        <div className="glass-card p-4 rounded-xl border border-sage-400/50 bg-beige-200/90 flex items-center justify-between">
          <div>
            <div className="text-[11px] text-forest-700 font-semibold">Ownership & Approval Status</div>
            <div className="text-sm font-extrabold text-forest-950 flex items-center space-x-1.5 mt-0.5">
              <ShieldCheck className="w-4 h-4 text-forest-700" />
              <span>{plot.ownership_status}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[11px] text-forest-700 font-semibold">Locality</div>
            <div className="text-sm font-extrabold text-forest-950 flex items-center justify-end space-x-1 mt-0.5">
              <MapPin className="w-3.5 h-3.5 text-forest-700" />
              <span>{plot.locality}</span>
            </div>
          </div>
        </div>

        {/* 3 Role Specification Tabs */}
        
        {/* 1. Builder Specifications */}
        <div className="space-y-3">
          <h3 className="text-xs font-extrabold text-forest-950 uppercase tracking-wider flex items-center space-x-2">
            <HardHat className="w-4 h-4 text-forest-800" />
            <span>Engineering & Civil Specifications (Builder)</span>
          </h3>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">Bearing Capacity</div>
              <div className="text-sm font-extrabold text-forest-950 font-mono mt-0.5">{plot.bearing_capacity_kpa} kPa</div>
            </div>
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">Water Table Depth</div>
              <div className="text-sm font-extrabold text-forest-950 font-mono mt-0.5">{plot.water_table_depth_m} m</div>
            </div>
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">Soil Type</div>
              <div className="text-sm font-extrabold text-forest-950 mt-0.5">{plot.soil_type}</div>
            </div>
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">Max Floors Permitted</div>
              <div className="text-sm font-extrabold text-forest-950 font-mono mt-0.5">{plot.max_permissible_floors} Floors</div>
            </div>
          </div>
        </div>

        {/* Utility Grid Checklist */}
        <div className="space-y-2">
          <div className="text-xs font-bold text-forest-800">Utility Access Grid:</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {plot.utility_access.map((util, i) => (
              <div key={i} className="flex items-center space-x-2 bg-beige-200 p-2.5 rounded-lg border border-sage-300 text-forest-950 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-forest-700 shrink-0" />
                <span>{util}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 2. Investor Financial Metrics */}
        <div className="space-y-3 pt-2 border-t border-sage-300">
          <h3 className="text-xs font-extrabold text-forest-950 uppercase tracking-wider flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-forest-800" />
            <span>Financial & Yield Metrics (Investor)</span>
          </h3>
          <div className="grid grid-cols-3 gap-3 text-xs text-center">
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">Current Rate</div>
              <div className="text-sm font-extrabold text-forest-950 font-mono mt-0.5">₹{plot.current_price_sqft}</div>
            </div>
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">Rental Yield</div>
              <div className="text-sm font-extrabold text-forest-950 font-mono mt-0.5">{plot.rental_yield_percentage}%</div>
            </div>
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">5-Yr ROI</div>
              <div className="text-sm font-extrabold text-forest-950 font-mono mt-0.5">+{plot.roi_percentage}%</div>
            </div>
          </div>
        </div>

        {/* 3. Homebuyer Livability Metrics */}
        <div className="space-y-3 pt-2 border-t border-sage-300">
          <h3 className="text-xs font-extrabold text-forest-950 uppercase tracking-wider flex items-center space-x-2">
            <Home className="w-4 h-4 text-forest-800" />
            <span>Livability & Infrastructure (Homebuyer)</span>
          </h3>
          <div className="grid grid-cols-3 gap-3 text-xs text-center">
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">Parks & Greenery</div>
              <div className="text-sm font-extrabold text-forest-950 mt-0.5">Pristine Parks</div>
            </div>
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">City Commute</div>
              <div className="text-sm font-extrabold text-forest-950 font-mono mt-0.5">{plot.commute_time_to_city_center_min} min</div>
            </div>
            <div className="bg-beige-200 p-3 rounded-xl border border-sage-300">
              <div className="text-forest-700 text-[10px] font-semibold">Hospital Dist.</div>
              <div className="text-sm font-extrabold text-forest-950 font-mono mt-0.5">{plot.nearest_hospital_km} km</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
