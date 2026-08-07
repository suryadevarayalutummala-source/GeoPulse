import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import {
  HardHat,
  Home,
  TrendingUp,
  ShieldAlert,
  Zap,
  CheckCircle2,
  Maximize2,
  Clock,
  Trees,
  Hospital,
  GraduationCap,
  Bus,
  Layers,
  Sparkles
} from 'lucide-react';
import MetricCard from './MetricCard';

export default function RightAnalyticsPanel({ selectedPlot, activeRole, onOpenDetails }) {
  if (!selectedPlot) {
    return (
      <div className="w-full h-full glass-panel rounded-2xl border border-forest-600/20 p-6 flex flex-col items-center justify-center text-forest-700 text-center">
        <Layers className="w-12 h-12 text-sage-400 mb-3 animate-pulse" />
        <p className="text-sm font-bold">Select a plot on the map to view detailed analytics</p>
      </div>
    );
  }

  return (
    <div id="analytics-section" className="w-full h-full glass-panel rounded-2xl border border-forest-600/20 p-4 lg:p-5 flex flex-col space-y-4 shadow-sm overflow-y-auto">
      
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-sage-300/60 pb-3">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold text-forest-950 bg-sage-200 px-2 py-0.5 rounded border border-sage-400/50">
              {selectedPlot.plot_id}
            </span>
            <span className="text-xs font-bold text-forest-900 bg-beige-200 px-2 py-0.5 rounded border border-sage-300 capitalize">
              {activeRole} View
            </span>
          </div>
          <h3 className="text-base font-extrabold text-forest-950 mt-1 line-clamp-1">
            {selectedPlot.name}
          </h3>
        </div>

        <button
          onClick={() => onOpenDetails(selectedPlot)}
          className="p-2 rounded-xl bg-beige-200 hover:bg-beige-300 text-forest-900 border border-sage-300 transition-all cursor-pointer shadow-xs"
          title="Open Full Specifications"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Dynamic Content based on Active Role */}
      {activeRole === 'builder' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <MetricCard
              title="Bearing Capacity"
              value={`${selectedPlot.bearing_capacity_kpa} kPa`}
              subtext={`Soil: ${selectedPlot.soil_type}`}
              badgeColor="sage"
              highlight={true}
            />
            <MetricCard
              title="Water Table Depth"
              value={`${selectedPlot.water_table_depth_m} m`}
              subtext="Groundwater baseline"
              badgeColor="beige"
            />
            <MetricCard
              title="Max Floors Allowed"
              value={`${selectedPlot.max_permissible_floors} F`}
              subtext={`Zoning: ${selectedPlot.zoning_type}`}
              badgeColor="sage"
            />
            <MetricCard
              title="Construction Cost Est."
              value={`₹${selectedPlot.construction_cost_estimate_per_sqft}/sqft`}
              subtext="Estimated baseline structure"
              badgeColor="olive"
            />
          </div>

          {/* Flood Risk & Foundation Specs */}
          <div className="glass-card p-3.5 rounded-xl border border-sage-300/60 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-forest-800">Flood Risk Zone:</span>
              <span className="font-extrabold text-forest-950 bg-sage-200 px-2 py-0.5 rounded border border-sage-400/60">
                {selectedPlot.flood_risk_zone}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-forest-800">Soil Classification:</span>
              <span className="font-extrabold text-forest-950">{selectedPlot.soil_type}</span>
            </div>
          </div>

          {/* Utility Access Checklist */}
          <div className="glass-card p-3.5 rounded-xl border border-sage-300/60">
            <h4 className="text-xs font-extrabold text-forest-950 uppercase tracking-wide mb-2.5 flex items-center space-x-1.5">
              <Zap className="w-3.5 h-3.5 text-forest-700" />
              <span>Utility Access & Infrastructure Grid</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {selectedPlot.utility_access.map((util, i) => (
                <div
                  key={i}
                  className="flex items-center space-x-2 bg-beige-100 p-2 rounded-lg border border-sage-300/50"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-forest-700 shrink-0" />
                  <span className="text-forest-900 text-[11px] font-bold">{util}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeRole === 'homebuyer' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <MetricCard
              title="Neighborhood Greenery"
              value="Pristine Parks"
              subtext="Eco-Buffer & Open Space"
              badgeColor="sage"
              highlight={true}
            />
            <MetricCard
              title="Commute to City"
              value={`${selectedPlot.commute_time_to_city_center_min} min`}
              subtext="Traffic fluid corridor"
              badgeColor="beige"
            />
            <MetricCard
              title="Nearest Hospital"
              value={`${selectedPlot.nearest_hospital_km} km`}
              subtext="Emergency response radius"
              badgeColor="olive"
            />
            <MetricCard
              title="Schools Nearby"
              value={`${selectedPlot.schools_nearby}`}
              subtext="K-12 Top Institutions"
              badgeColor="sage"
            />
          </div>

          {/* Amenities & Livability Summary */}
          <div className="glass-card p-3.5 rounded-xl border border-sage-300/60 space-y-3">
            <h4 className="text-xs font-extrabold text-forest-950 uppercase tracking-wide flex items-center space-x-1.5">
              <Home className="w-3.5 h-3.5 text-forest-700" />
              <span>Neighborhood Livability Score</span>
            </h4>
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className="bg-beige-100 p-2 rounded-xl border border-sage-300/50">
                <GraduationCap className="w-4 h-4 text-forest-800 mx-auto mb-1" />
                <div className="font-extrabold text-forest-950">{selectedPlot.schools_nearby}</div>
                <div className="text-[10px] text-forest-700 font-semibold">Schools</div>
              </div>
              <div className="bg-beige-100 p-2 rounded-xl border border-sage-300/50">
                <Hospital className="w-4 h-4 text-forest-800 mx-auto mb-1" />
                <div className="font-extrabold text-forest-950">{selectedPlot.hospitals_nearby}</div>
                <div className="text-[10px] text-forest-700 font-semibold">Hospitals</div>
              </div>
              <div className="bg-beige-100 p-2 rounded-xl border border-sage-300/50">
                <Bus className="w-4 h-4 text-forest-800 mx-auto mb-1" />
                <div className="font-extrabold text-forest-950">{selectedPlot.transit_hubs_nearby}</div>
                <div className="text-[10px] text-forest-700 font-semibold">Transit Hubs</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeRole === 'investor' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <MetricCard
              title="Current Price / Sqft"
              value={`₹${selectedPlot.current_price_sqft.toLocaleString()}`}
              subtext="Locality Benchmark"
              badgeColor="sage"
              highlight={true}
            />
            <MetricCard
              title="Estimated 5-Yr ROI"
              value={`${selectedPlot.roi_percentage}%`}
              subtext="Projected appreciation"
              badgeColor="olive"
              trend="up"
              trendValue={`+${selectedPlot.roi_percentage}%`}
            />
            <MetricCard
              title="Rental Yield"
              value={`${selectedPlot.rental_yield_percentage}%`}
              subtext="Annual commercial yield"
              badgeColor="beige"
            />
            <MetricCard
              title="Risk Profile"
              value={selectedPlot.risk_score}
              subtext="Clear Title & Governance"
              badgeColor="sage"
            />
          </div>

          {/* Historical Growth Chart (Recharts Light Warm Theme) */}
          <div className="glass-card p-3.5 rounded-xl border border-sage-300/60">
            <h4 className="text-xs font-extrabold text-forest-950 uppercase tracking-wide mb-2 flex items-center justify-between">
              <span className="flex items-center space-x-1.5">
                <TrendingUp className="w-3.5 h-3.5 text-forest-700" />
                <span>Historical Appreciation (₹/sqft)</span>
              </span>
              <span className="text-[10px] font-mono text-forest-900 font-extrabold">2021 - 2025</span>
            </h4>
            <div className="h-[140px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={selectedPlot.historical_growth_rates}>
                  <defs>
                    <linearGradient id="growthGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#54854E" stopOpacity={0.65} />
                      <stop offset="95%" stopColor="#54854E" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#D9E6D5" />
                  <XAxis dataKey="year" stroke="#3D6838" fontSize={10} tickLine={false} fontWeight={700} />
                  <YAxis stroke="#3D6838" fontSize={10} tickLine={false} domain={['auto', 'auto']} fontWeight={700} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#F9F5EC',
                      borderColor: '#9EBE98',
                      borderRadius: '8px',
                      color: '#182A1B',
                      fontSize: '11px',
                      fontWeight: 'bold'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke="#3D6838"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#growthGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Infrastructure Development Pipeline */}
          <div className="glass-card p-3.5 rounded-xl border border-sage-300/60">
            <h4 className="text-xs font-extrabold text-forest-950 uppercase tracking-wide mb-2.5 flex items-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 text-forest-700" />
              <span>Infrastructure Development Pipeline</span>
            </h4>
            <div className="space-y-2">
              {selectedPlot.infrastructure_development_pipeline.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-start space-x-2 text-xs bg-beige-100 p-2 rounded-lg border border-sage-300/50"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-forest-700 mt-1.5 shrink-0" />
                  <span className="text-forest-950 text-[11px] font-bold leading-tight">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
