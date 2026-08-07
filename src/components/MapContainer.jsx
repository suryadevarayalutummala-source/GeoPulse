import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Maximize2, Layers, MapPin, Sparkles, Navigation } from 'lucide-react';

// Custom Marker Generator function for futuristic dark look
const createCustomIcon = (isSelected, zoningType) => {
  const color = isSelected ? '#06B6D4' : '#64748B';
  const pulseColor = isSelected ? 'rgba(6, 182, 212, 0.4)' : 'transparent';

  const html = `
    <div style="position: relative; width: 32px; height: 32px; display: flex; items-center; justify-content: center;">
      <div style="position: absolute; width: 100%; height: 100%; border-radius: 50%; background: ${pulseColor}; animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
      <div style="position: relative; width: 24px; height: 24px; border-radius: 50%; background: #0B0F19; border: 2px solid ${color}; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px ${color};">
        <div style="width: 10px; height: 10px; border-radius: 50%; background: ${color};"></div>
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-map-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16]
  });
};

// Map Recenter Helper component
function ChangeView({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.flyTo(center, 14, { duration: 1.2 });
    }
  }, [center, map]);
  return null;
}

export default function InteractiveMap({ plots, selectedPlot, onSelectPlot, onOpenDetails }) {
  const defaultCenter = selectedPlot
    ? selectedPlot.coordinates
    : [17.4143, 78.3489];

  return (
    <div className="relative w-full h-[450px] lg:h-full rounded-2xl overflow-hidden glass-panel border border-gray-800 shadow-2xl dark-map flex flex-col">
      
      {/* Map Header Overlay Bar */}
      <div className="absolute top-4 left-4 right-4 z-[500] flex items-center justify-between pointer-events-none">
        <div className="pointer-events-auto flex items-center space-x-2 px-3 py-1.5 rounded-xl glass-panel text-xs font-semibold text-gray-200 border border-gray-700/80 shadow-lg">
          <Navigation className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
          <span>Interactive Mapbox Layer</span>
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
          <span className="text-gray-400 font-mono text-[10px] uppercase">HYD Vector Grid</span>
        </div>

        {selectedPlot && (
          <div className="pointer-events-auto hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-xl glass-panel border border-cyan-500/40 text-xs font-bold text-cyan-300 shadow-lg">
            <MapPin className="w-3.5 h-3.5" />
            <span>Selected: {selectedPlot.name}</span>
          </div>
        )}
      </div>

      {/* Leaflet Map React Container */}
      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={true}
        className="w-full h-full z-10"
        style={{ background: '#0B0F19' }}
      >
        <ChangeView center={defaultCenter} />

        {/* Dark Mode CartoDB Tile Layer */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> Mapbox Vector Engine'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Render Boundaries Polygons & Markers for all plots */}
        {plots.map((plot) => {
          const isSelected = selectedPlot?.plot_id === plot.plot_id;
          const polygonPositions = plot.plot_boundary_geojson;

          return (
            <React.Fragment key={plot.plot_id}>
              {/* Boundary Polygon */}
              <Polygon
                positions={polygonPositions}
                pathOptions={{
                  color: isSelected ? '#06B6D4' : '#475569',
                  fillColor: isSelected ? '#06B6D4' : '#334155',
                  fillOpacity: isSelected ? 0.45 : 0.2,
                  weight: isSelected ? 3 : 1.5,
                  dashArray: isSelected ? null : '4'
                }}
                eventHandlers={{
                  click: () => onSelectPlot(plot)
                }}
              />

              {/* Center Marker */}
              <Marker
                position={plot.coordinates}
                icon={createCustomIcon(isSelected, plot.zoning_type)}
                eventHandlers={{
                  click: () => onSelectPlot(plot)
                }}
              >
                <Popup>
                  <div className="p-1 min-w-[200px] text-gray-100">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] font-mono font-bold text-cyan-400 bg-cyan-950 px-1.5 py-0.5 rounded border border-cyan-500/30">
                        {plot.plot_id}
                      </span>
                      <span className="text-[10px] text-gray-400 font-semibold">{plot.zoning_type}</span>
                    </div>

                    <h4 className="text-xs font-bold text-white mb-2">{plot.name}</h4>

                    <div className="space-y-1 text-[11px] text-gray-300 mb-3 bg-gray-900/90 p-2 rounded-lg border border-gray-800">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Area:</span>
                        <span className="font-semibold text-gray-100">{plot.area_sqft.toLocaleString()} sqft</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Price:</span>
                        <span className="font-semibold text-cyan-300 font-mono">₹{plot.current_price_sqft}/sqft</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Locality:</span>
                        <span className="font-semibold text-gray-100">{plot.locality}</span>
                      </div>
                    </div>

                    <button
                      onClick={() => onOpenDetails(plot)}
                      className="w-full py-1.5 px-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xs flex items-center justify-center space-x-1 transition-all shadow-md"
                    >
                      <Maximize2 className="w-3 h-3" />
                      <span>Open Details</span>
                    </button>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Bottom Map Legend */}
      <div className="absolute bottom-4 left-4 z-[500] pointer-events-auto glass-panel px-3 py-2 rounded-xl border border-gray-800 flex items-center space-x-4 text-[11px]">
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-3 rounded bg-cyan-500/80 border border-cyan-400" />
          <span className="text-gray-300 font-medium">Active Selection</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-3 rounded bg-slate-600/50 border border-slate-500 border-dashed" />
          <span className="text-gray-400">Adjacent Parcels</span>
        </div>
      </div>

    </div>
  );
}
