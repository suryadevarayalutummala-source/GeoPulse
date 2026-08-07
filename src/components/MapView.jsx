import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { createRoot } from 'react-dom/client';
import { Navigation, MapPin, Layers, Sparkles, Compass, Settings, Key } from 'lucide-react';
import MarkerPopup from './MarkerPopup';
import { toLngLat, createPlotFeatureCollection, calculatePlotBounds } from '../utils/geoUtils';

const DEFAULT_MAPBOX_TOKEN = '';

export default function MapView({ plots = [], selectedPlot = null, onSelect = () => { }, onOpenDetails = () => { } }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markersRef = useRef([]);
  const popupRef = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapStyle, setMapStyle] = useState('outdoors');
  const [tokenInput, setTokenInput] = useState(localStorage.getItem('mapbox_token') || '');
  const [showSettings, setShowSettings] = useState(false);
  const [tokenError, setTokenError] = useState(false);
  const [mapReloadKey, setMapReloadKey] = useState(0);

  const mapboxToken =
    localStorage.getItem('mapbox_token') ||
    import.meta.env.VITE_MAPBOX_TOKEN ||
    import.meta.env.NEXT_PUBLIC_MAPBOX_TOKEN ||
    DEFAULT_MAPBOX_TOKEN;

  useEffect(() => {
    if (!mapContainerRef.current || !mapboxToken) return;

    mapboxgl.accessToken = mapboxToken;

    const initialCenter = selectedPlot
      ? toLngLat(selectedPlot.coordinates)
      : [78.3489, 17.4143];

    let map;
    try {
      map = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: 'mapbox://styles/mapbox/outdoors-v12',
        center: initialCenter,
        zoom: 13,
        pitch: 45,
        bearing: -10,
        antialias: true
      });
    } catch (err) {
      console.error('Failed to create Mapbox instance:', err);
      setTokenError(true);
      return;
    }

    map.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), 'top-right');
    map.addControl(new mapboxgl.FullscreenControl(), 'top-right');

    map.on('error', (e) => {
      console.error('Mapbox error event:', e);
      if (e.message?.includes('token') || e.message?.includes('Unauthorized') || (e.error && e.error.status === 401)) {
        setTokenError(true);
      }
    });

    map.on('load', () => {
      setMapLoaded(true);
      setTokenError(false);

      const geojson = createPlotFeatureCollection(plots, selectedPlot?.plot_id);

      if (!map.getSource('plots-source')) {
        map.addSource('plots-source', {
          type: 'geojson',
          data: geojson
        });

        // Add Polygon Fill Layer (Beige-Green palette)
        map.addLayer({
          id: 'plots-fill',
          type: 'fill',
          source: 'plots-source',
          paint: {
            'fill-color': [
              'case',
              ['boolean', ['get', 'isSelected'], false],
              '#54854E', // Sage Green
              '#8E9B4B'  // Olive Green
            ],
            'fill-opacity': [
              'case',
              ['boolean', ['get', 'isSelected'], false],
              0.55,
              0.25
            ]
          }
        });

        // Add Polygon Outline Layer
        map.addLayer({
          id: 'plots-outline',
          type: 'line',
          source: 'plots-source',
          paint: {
            'line-color': [
              'case',
              ['boolean', ['get', 'isSelected'], false],
              '#1B3419', // Dark Forest
              '#54854E'
            ],
            'line-width': [
              'case',
              ['boolean', ['get', 'isSelected'], false],
              3.5,
              1.5
            ],
            'line-dasharray': [
              'case',
              ['boolean', ['get', 'isSelected'], false],
              [1, 0],
              [2, 2]
            ]
          }
        });
      }
    });

    mapRef.current = map;

    return () => {
      if (map) {
        map.remove();
      }
      setMapLoaded(false);
    };
  }, [mapboxToken, mapReloadKey]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    const source = map.getSource('plots-source');
    if (source) {
      const geojson = createPlotFeatureCollection(plots, selectedPlot?.plot_id);
      source.setData(geojson);
    }
  }, [plots, selectedPlot, mapLoaded]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded || !selectedPlot) return;

    const center = toLngLat(selectedPlot.coordinates);

    map.flyTo({
      center,
      zoom: 14.5,
      pitch: 50,
      bearing: 15,
      speed: 1.2,
      curve: 1.4,
      essential: true
    });
  }, [selectedPlot, mapLoaded]);

  // Render Markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    plots.forEach((plot) => {
      const isSelected = selectedPlot?.plot_id === plot.plot_id;
      const lngLat = toLngLat(plot.coordinates);

      const el = document.createElement('div');
      el.className = 'custom-mapbox-marker group cursor-pointer';

      const badgeColor = isSelected
        ? 'bg-forest-800 border-beige-100 shadow-[0_0_15px_rgba(84,133,78,0.7)] scale-110'
        : 'bg-beige-100 border-forest-700/60 hover:border-forest-900 hover:scale-105';

      el.innerHTML = `
        <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;">
          ${isSelected
          ? '<div class="marker-pulse" style="position: absolute; width: 36px; height: 36px; border-radius: 50%; background: rgba(84, 133, 78, 0.45);"></div>'
          : ''
        }
          <div class="w-8 h-8 rounded-full border-2 ${badgeColor} flex items-center justify-center transition-all duration-300">
            <div class="w-2.5 h-2.5 rounded-full ${isSelected ? 'bg-beige-100' : 'bg-forest-800'}"></div>
          </div>
          <div class="absolute -bottom-6 left-1/2 -translate-x-1/2 hidden group-hover:block whitespace-nowrap bg-forest-950 text-beige-100 text-[10px] font-bold px-2 py-0.5 rounded border border-sage-400 shadow-lg z-50 pointer-events-none">
            ${plot.plot_id} • ${plot.locality}
          </div>
        </div>
      `;

      el.addEventListener('click', (e) => {
        e.stopPropagation();
        onSelect(plot);
        showPopup(map, plot, lngLat);
      });

      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat(lngLat)
        .addTo(map);

      markersRef.current.push(marker);
    });
  }, [plots, selectedPlot, mapLoaded]);

  const showPopup = (map, plot, lngLat) => {
    if (popupRef.current) {
      popupRef.current.remove();
    }

    const popupNode = document.createElement('div');
    const root = createRoot(popupNode);
    root.render(<MarkerPopup plot={plot} onOpenDetails={onOpenDetails} />);

    const popup = new mapboxgl.Popup({
      closeButton: true,
      closeOnClick: false,
      offset: 25,
      maxWidth: '280px'
    })
      .setLngLat(lngLat)
      .setDOMContent(popupNode)
      .addTo(map);

    popupRef.current = popup;
  };

  const changeStyle = (styleKey) => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;
    setMapStyle(styleKey);

    const styleUrl =
      styleKey === 'satellite'
        ? 'mapbox://styles/mapbox/satellite-streets-v12'
        : styleKey === 'dark'
          ? 'mapbox://styles/mapbox/dark-v11'
          : 'mapbox://styles/mapbox/outdoors-v12';

    map.setStyle(styleUrl);
  };

  const handleSaveToken = (e) => {
    e.preventDefault();
    const cleanToken = tokenInput.trim();
    if (cleanToken) {
      localStorage.setItem('mapbox_token', cleanToken);
      setTokenError(false);
      setShowSettings(false);
      setMapReloadKey((prev) => prev + 1);
    }
  };

  const handleResetToken = () => {
    localStorage.removeItem('mapbox_token');
    setTokenInput('');
    setTokenError(false);
    setShowSettings(false);
    setMapReloadKey((prev) => prev + 1);
  };

  return (
    <div className="relative w-full h-[480px] lg:h-full rounded-2xl overflow-hidden glass-panel border border-forest-600/20 shadow-sm flex flex-col">
      {/* Top Map Header Overlay Bar */}
      <div className="absolute top-4 left-4 right-14 z-10 flex items-center justify-between pointer-events-none">
        <div className="flex items-center space-x-2">
          <div className="pointer-events-auto flex items-center space-x-2 px-3 py-1.5 rounded-xl glass-panel text-xs font-bold text-forest-950 border border-forest-600/30 shadow-sm">
            <Navigation className="w-3.5 h-3.5 text-forest-700 animate-spin" />
            <span>GeoPulse Vector Grid</span>
            <span className="w-1.5 h-1.5 rounded-full bg-forest-700" />
            <span className="text-forest-800 font-mono text-[10px] uppercase font-bold text-nowrap">Mapbox GL JS</span>
          </div>

          <button
            onClick={() => setShowSettings(true)}
            className="pointer-events-auto p-1.5 rounded-xl glass-panel border border-forest-600/30 hover:border-forest-600/50 hover:bg-beige-100/90 text-forest-805 transition-all shadow-sm flex items-center justify-center cursor-pointer"
            title="Configure Mapbox Token"
          >
            <Settings className="w-3.5 h-3.5 text-forest-800" />
          </button>
        </div>

        {selectedPlot && (
          <div className="pointer-events-auto hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-xl glass-panel border border-forest-600/40 text-xs font-extrabold text-forest-950 shadow-sm bg-beige-100/90">
            <MapPin className="w-3.5 h-3.5 text-forest-800" />
            <span>Selected: {selectedPlot.name}</span>
          </div>
        )}
      </div>

      {/* Map Style Selector Overlay */}
      <div className="absolute bottom-4 right-4 z-10 glass-panel p-1 rounded-xl border border-forest-600/30 flex items-center space-x-1 shadow-sm">
        <button
          onClick={() => changeStyle('outdoors')}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all ${mapStyle === 'outdoors'
            ? 'bg-forest-800 text-beige-100 shadow'
            : 'text-forest-800 hover:text-forest-950'
            }`}
        >
          Terrain
        </button>
        <button
          onClick={() => changeStyle('satellite')}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all ${mapStyle === 'satellite'
            ? 'bg-forest-800 text-beige-100 shadow'
            : 'text-forest-800 hover:text-forest-950'
            }`}
        >
          Satellite
        </button>
        <button
          onClick={() => changeStyle('dark')}
          className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all ${mapStyle === 'dark'
            ? 'bg-forest-800 text-beige-100 shadow'
            : 'text-forest-800 hover:text-forest-950'
            }`}
        >
          Dark
        </button>
      </div>

      {/* Mapbox Canvas Container */}
      <div ref={mapContainerRef} className="w-full h-full relative" />

      {/* Token Error / Config Overlay */}
      {(tokenError || showSettings) && (
        <div className="absolute inset-0 bg-beige-150/95 backdrop-blur-md z-30 flex flex-col items-center justify-center p-6 text-center">
          <div className="max-w-md w-full glass-card p-6 rounded-2xl border border-forest-600/30 shadow-xl flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-forest-100/20 border border-forest-750/30 flex items-center justify-center mb-4">
              <Key className="w-6 h-6 text-forest-800 animate-pulse" />
            </div>

            <h3 className="text-base font-extrabold text-forest-950 mb-2">
              {tokenError ? 'Invalid Mapbox Access Token' : 'Mapbox Access Token'}
            </h3>

            <p className="text-xs text-forest-800 mb-4 leading-relaxed font-semibold">
              {tokenError
                ? 'The current Mapbox token is invalid or rate-limited. Please configure a valid Mapbox Public Access Token to load the vector maps.'
                : 'Configure your custom Mapbox Access Token below. This token will be saved locally in your browser.'}
            </p>

            <form onSubmit={handleSaveToken} className="w-full space-y-3">
              <div className="relative">
                <input
                  type="text"
                  placeholder="pk.eyJ1..."
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl glass-input border border-forest-600/30 focus:border-forest-700 font-mono focus:ring-1 focus:ring-forest-750"
                  required
                />
              </div>

              <div className="flex space-x-2">
                {showSettings && !tokenError && (
                  <button
                    type="button"
                    onClick={() => setShowSettings(false)}
                    className="flex-1 py-2 rounded-xl border border-forest-600/30 text-xs font-bold text-forest-800 hover:bg-beige-200 transition-all cursor-pointer"
                  >
                    Cancel
                  </button>
                )}
                {localStorage.getItem('mapbox_token') && (
                  <button
                    type="button"
                    onClick={handleResetToken}
                    className="py-2 px-3 rounded-xl border border-rose-300 text-xs font-bold text-rose-700 hover:bg-rose-50 transition-all cursor-pointer"
                    title="Reset to Default Token"
                  >
                    Reset
                  </button>
                )}
                <button
                  type="submit"
                  className="flex-1 py-2 rounded-xl bg-forest-800 hover:bg-forest-950 text-beige-100 text-xs font-bold transition-all shadow-sm cursor-pointer"
                >
                  Save & Reload
                </button>
              </div>
            </form>

            <div className="mt-4 pt-4 border-t border-forest-600/10 w-full text-[10px] text-forest-700 font-bold">
              Don't have a token? Get one for free at{' '}
              <a
                href="https://mapbox.com"
                target="_blank"
                rel="noreferrer"
                className="text-forest-900 underline hover:text-forest-950 font-extrabold"
              >
                mapbox.com
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Map Legend */}
      <div className="absolute bottom-4 left-4 z-10 pointer-events-auto glass-panel px-3 py-2 rounded-xl border border-forest-600/30 flex items-center space-x-4 text-[11px]">
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-3 rounded bg-sage-500 border border-forest-900 shadow-[0_0_8px_rgba(84,133,78,0.6)]" />
          <span className="text-forest-950 font-bold">Selected Parcel</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-3 h-3 rounded bg-olive-400 border border-forest-700/50" />
          <span className="text-forest-800 font-semibold">Surrounding Parcels</span>
        </div>
      </div>
    </div>
  );
}
