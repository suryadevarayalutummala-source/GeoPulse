/**
 * Ensures coordinates are strictly in Mapbox GL JS [longitude, latitude] standard format
 * @param {Array<number>} coords - Input coordinates
 * @returns {Array<number>} [longitude, latitude]
 */
export function toLngLat(coords) {
  if (!coords || !Array.isArray(coords) || coords.length < 2) {
    return [78.3489, 17.4143]; // Default Hyderabad longitude, latitude
  }

  // If first number is lat (> 50 for longitude or < 25 for Hyderabad lat ~17.4)
  // Hyderabad lat is ~17.4, lng is ~78.4
  const val0 = Number(coords[0]);
  const val1 = Number(coords[1]);

  if (val0 < 30 && val1 > 60) {
    // Array was passed as [lat, lng], swap to [lng, lat]
    return [val1, val0];
  }

  return [val0, val1];
}

/**
 * Ensures polygon boundaries are strictly in [longitude, latitude] GeoJSON ring format
 * @param {Array<Array<number>>} ring 
 * @returns {Array<Array<number>>}
 */
export function polygonToLngLat(ring) {
  if (!ring || !Array.isArray(ring)) return [];
  
  const converted = ring.map((pt) => toLngLat(pt));
  
  // Close the polygon ring if not already closed
  if (converted.length > 0) {
    const first = converted[0];
    const last = converted[converted.length - 1];
    if (first[0] !== last[0] || first[1] !== last[1]) {
      converted.push([first[0], first[1]]);
    }
  }

  return converted;
}

/**
 * Creates GeoJSON FeatureCollection for Mapbox polygon and marker rendering
 * @param {Array<Object>} plots 
 * @returns {Object} GeoJSON FeatureCollection
 */
export function createPlotFeatureCollection(plots = [], selectedPlotId = null) {
  return {
    type: 'FeatureCollection',
    features: plots.map((plot) => {
      const lngLat = toLngLat(plot.coordinates);
      const ring = polygonToLngLat(plot.plot_boundary_geojson);

      return {
        type: 'Feature',
        id: plot.plot_id,
        properties: {
          id: plot.plot_id,
          name: plot.name,
          locality: plot.locality,
          zoning: plot.zoning_type,
          area: plot.area_sqft,
          price: plot.current_price_sqft,
          bearing_capacity: plot.bearing_capacity_kpa,
          water_table: plot.water_table_depth_m,
          soil: plot.soil_type,
          floors: plot.max_permissible_floors,
          roi: plot.roi_percentage,
          rental_yield: plot.rental_yield_percentage,
          greenery: 'Pristine Parks',
          commute: plot.commute_time_to_city_center_min,
          isSelected: plot.plot_id === selectedPlotId
        },
        geometry: {
          type: 'Polygon',
          coordinates: [ring]
        }
      };
    })
  };
}

/**
 * Calculates bounding box [minLng, minLat, maxLng, maxLat] from plot coordinates
 * @param {Array<Object>} plots 
 * @returns {Array<number>} [minLng, minLat, maxLng, maxLat]
 */
export function calculatePlotBounds(plots = []) {
  if (!plots || plots.length === 0) {
    return [78.28, 17.20, 78.58, 17.65];
  }

  let minLng = Infinity;
  let minLat = Infinity;
  let maxLng = -Infinity;
  let maxLat = -Infinity;

  plots.forEach((p) => {
    const [lng, lat] = toLngLat(p.coordinates);
    if (lng < minLng) minLng = lng;
    if (lng > maxLng) maxLng = lng;
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
  });

  return [minLng, minLat, maxLng, maxLat];
}
