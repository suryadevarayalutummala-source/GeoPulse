import React from 'react';
import { MapPin, Maximize2, Layers } from 'lucide-react';

export default function MarkerPopup({ plot, onOpenDetails }) {
  if (!plot) return null;

  return (
    <div className="p-1 space-y-2 min-w-[210px] text-forest-950">
      
      {/* Popup Header */}
      <div className="flex items-center justify-between border-b border-sage-300/80 pb-1.5">
        <span className="text-[10px] font-mono font-extrabold text-forest-950 bg-sage-200 px-2 py-0.5 rounded border border-sage-400/50">
          {plot.plot_id}
        </span>
        <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-beige-200 text-forest-950 border border-sage-300">
          {plot.zoning_type}
        </span>
      </div>

      {/* Title & Locality */}
      <div>
        <h4 className="text-xs font-extrabold text-forest-950 leading-snug">
          {plot.name}
        </h4>
        <div className="flex items-center space-x-1 text-[11px] text-forest-800 font-semibold mt-0.5">
          <MapPin className="w-3 h-3 text-forest-700 shrink-0" />
          <span className="truncate">{plot.locality}</span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-1.5 pt-1 text-[11px] border-t border-sage-300/60">
        <div className="bg-beige-100 p-1.5 rounded border border-sage-300/50">
          <div className="text-[9px] text-forest-700 font-medium">Area</div>
          <div className="font-extrabold text-forest-950 font-mono text-[10px]">
            {plot.area_sqft.toLocaleString()} sqft
          </div>
        </div>

        <div className="bg-beige-100 p-1.5 rounded border border-sage-300/50">
          <div className="text-[9px] text-forest-700 font-medium">Price / sqft</div>
          <div className="font-extrabold text-forest-900 font-mono text-[10px]">
            ₹{plot.current_price_sqft.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Action Button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onOpenDetails(plot);
        }}
        className="w-full py-1.5 px-2 rounded-lg bg-forest-800 hover:bg-forest-900 text-beige-100 text-[11px] font-extrabold flex items-center justify-center space-x-1 transition-all shadow-xs cursor-pointer mt-1"
      >
        <span>Open Specs</span>
        <Maximize2 className="w-3 h-3 text-beige-100" />
      </button>

    </div>
  );
}
