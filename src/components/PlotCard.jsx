import React from 'react';
import { MapPin, Building2, Tag, ChevronRight, Layers, Info } from 'lucide-react';

export default function PlotCard({ plot, isSelected, onSelect }) {
  const getZoningBadge = () => {
    switch (plot.zoning_type) {
      case 'Commercial':
        return 'text-beige-900 bg-beige-300 border-beige-500/40';
      case 'Residential':
        return 'text-forest-950 bg-sage-200 border-sage-400/60';
      case 'Industrial':
        return 'text-forest-950 bg-forest-200 border-forest-400/60';
      case 'Mixed Use':
      default:
        return 'text-olive-900 bg-olive-200 border-olive-400/60';
    }
  };

  return (
    <div
      onClick={() => onSelect(plot)}
      className={`glass-card p-3.5 rounded-xl border transition-all duration-300 cursor-pointer ${
        isSelected
          ? 'bg-beige-300/95 border-forest-600 shadow-[0_4px_16px_rgba(24,42,27,0.12)] scale-[1.01]'
          : 'border-sage-300/50 hover:border-forest-600/40 hover:bg-beige-300/60'
      }`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[10px] font-mono font-extrabold text-forest-950 bg-sage-200 px-2 py-0.5 rounded border border-sage-400/50">
          {plot.plot_id}
        </span>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getZoningBadge()}`}>
          {plot.zoning_type}
        </span>
      </div>

      <h4 className="text-xs font-bold text-forest-950 mb-1 line-clamp-1 group-hover:text-forest-700 transition-colors">
        {plot.name}
      </h4>

      <div className="flex items-center space-x-1 text-[11px] text-forest-900 mb-1 font-bold">
        <MapPin className="w-3 h-3 text-forest-700 shrink-0" />
        <span className="truncate">{plot.locality}</span>
      </div>

      {plot.locality_description && (
        <p className="text-[10px] text-forest-700 leading-tight mb-2 line-clamp-2 italic bg-beige-100/70 p-1.5 rounded border border-sage-300/40">
          {plot.locality_description}
        </p>
      )}

      <div className="flex items-center justify-between pt-2 border-t border-sage-300/50 text-xs">
        <div>
          <div className="text-[10px] text-forest-700 font-medium">Area</div>
          <div className="font-semibold text-forest-950 font-mono text-[11px]">
            {plot.area_sqft.toLocaleString()} sqft
          </div>
        </div>

        <div className="text-right">
          <div className="text-[10px] text-forest-700 font-medium">Price</div>
          <div className="font-extrabold text-forest-900 font-mono">
            ₹{plot.current_price_sqft.toLocaleString()}/sqft
          </div>
        </div>
      </div>
    </div>
  );
}
