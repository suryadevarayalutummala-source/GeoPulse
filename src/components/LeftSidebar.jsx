import React, { useState, useMemo } from 'react';
import { Search, Filter, Layers, MapPin, Building2, Tag } from 'lucide-react';
import PlotCard from './PlotCard';
import { LOCALITIES } from '../data/plots';

export default function LeftSidebar({ plots = [], selectedPlot, onSelectPlot }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLocality, setSelectedLocality] = useState('All');
  const [selectedZoning, setSelectedZoning] = useState('All');

  const filteredPlots = useMemo(() => {
    return plots.filter((plot) => {
      const matchesSearch =
        plot.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        plot.plot_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        plot.locality.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesLocality =
        selectedLocality === 'All' || plot.locality === selectedLocality;

      const matchesZoning =
        selectedZoning === 'All' || plot.zoning_type === selectedZoning;

      return matchesSearch && matchesLocality && matchesZoning;
    });
  }, [plots, searchTerm, selectedLocality, selectedZoning]);

  return (
    <div className="w-full h-full glass-panel rounded-2xl border border-forest-600/20 p-4 flex flex-col space-y-3.5 shadow-sm overflow-hidden">
      
      {/* Header & Parcel Counter */}
      <div className="flex items-center justify-between border-b border-sage-300/60 pb-3">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-xl bg-forest-800 text-beige-100 shadow-sm">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-forest-950 font-heading">
              Land Inventory
            </h3>
            <p className="text-[10px] text-forest-700 font-medium">
              Spatial Filter & Inventory
            </p>
          </div>
        </div>

        <span className="px-2.5 py-1 text-xs font-mono font-extrabold text-forest-950 bg-sage-200 border border-sage-400/60 rounded-lg">
          {filteredPlots.length} Plots
        </span>
      </div>

      {/* Search Input Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-forest-700 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by plot ID, name, or locality..."
          className="w-full pl-9 pr-3 py-2 rounded-xl text-xs glass-input focus:ring-1 focus:ring-forest-600 placeholder:text-forest-700/60 font-semibold"
        />
      </div>

      {/* Locality Dropdown & Zoning Filters */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div>
          <label className="block text-[10px] font-extrabold text-forest-800 uppercase mb-1">
            Shortlisted Locality:
          </label>
          <select
            value={selectedLocality}
            onChange={(e) => setSelectedLocality(e.target.value)}
            className="w-full py-1.5 px-2 rounded-lg glass-input text-xs font-bold"
          >
            <option value="All">All 8 Localities</option>
            {LOCALITIES.map((loc, idx) => (
              <option key={idx} value={loc}>
                {loc}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[10px] font-extrabold text-forest-800 uppercase mb-1">
            Zoning Type:
          </label>
          <select
            value={selectedZoning}
            onChange={(e) => setSelectedZoning(e.target.value)}
            className="w-full py-1.5 px-2 rounded-lg glass-input text-xs font-bold"
          >
            <option value="All">All Zones</option>
            <option value="Commercial">Commercial</option>
            <option value="Residential">Residential</option>
            <option value="Industrial">Industrial</option>
            <option value="Mixed Use">Mixed Use</option>
          </select>
        </div>
      </div>

      {/* Scrollable Plot Card List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {filteredPlots.length === 0 ? (
          <div className="p-6 text-center text-xs text-forest-700 italic glass-card rounded-xl border border-sage-300">
            No land parcels match your search criteria.
          </div>
        ) : (
          filteredPlots.map((plot) => (
            <PlotCard
              key={plot.plot_id}
              plot={plot}
              isSelected={selectedPlot?.plot_id === plot.plot_id}
              onSelect={onSelectPlot}
            />
          ))
        )}
      </div>

    </div>
  );
}
