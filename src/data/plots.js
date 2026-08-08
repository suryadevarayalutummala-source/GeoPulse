export const LOCALITIES = [
  "Old City (Charminar / Malakpet)",
  "Banjara Hills / Jubilee Hills",
  "Gachibowli / HITEC City",
  "Kokapet / Narsingi",
  "Gandipet / Manikonda",
  "Kompally / Medchal",
  "Uppal / LB Nagar",
  "Shamshabad"
];

// All coordinates and polygon boundaries strictly use [longitude, latitude] format
export const PLOTS_DATA = [
  {
    plot_id: "PLOT-101",
    name: "Charminar Heritage Enclave",
    locality: "Old City (Charminar / Malakpet)",
    locality_description: "Dense historic urban core with narrow legacy roads and heritage zoning constraints.",
    coordinates: [78.4747, 17.3616],
    area_sqft: 12000,
    zoning_type: "Mixed Use",
    ownership_status: "Clear Ancestral Title & Heritage Clearance",
    plot_boundary_geojson: [
      [78.4739, 17.3622],
      [78.4754, 17.3625],
      [78.4758, 17.3609],
      [78.4743, 17.3606]
    ],
    // Builder
    bearing_capacity_kpa: 230,
    water_table_depth_m: 7.5,
    soil_type: "Alluvial Sandy Silt",
    flood_risk_zone: "Moderate Risk (Historic Settlement)",
    max_permissible_floors: 6, // Low height restriction
    utility_access: ["Old City Feeder Line", "Municipal Water Supply", "Legacy Underground Drainage"],
    construction_cost_estimate_per_sqft: 2700,

    // Investor
    current_price_sqft: 12800,
    historical_growth_rates: [
      { year: "2021", price: 9500 },
      { year: "2022", price: 10400 },
      { year: "2023", price: 11200 },
      { year: "2024", price: 12000 },
      { year: "2025", price: 12800 }
    ],
    rental_yield_percentage: 7.5,
    roi_percentage: 11.5,
    risk_score: "Moderate",
    infrastructure_development_pipeline: [
      "Old City Metro Line Phase 2 Extension (MGBS to Falaknuma)",
      "Musiramam Bridge Pedestrianization & Heritage Walkway"
    ],

    // Homebuyer
    schools_nearby: 16,
    hospitals_nearby: 10,
    transit_hubs_nearby: 5,
    nearest_hospital_km: 0.3,
    air_quality_index: 68,
    commute_time_to_city_center_min: 5
  },
  {
    plot_id: "PLOT-102",
    name: "Jubilee Boulevard Ridge Villa Plot",
    locality: "Banjara Hills / Jubilee Hills",
    locality_description: "Premium established urban area characterized by high elevation, hilly/rocky terrain, and solid bearing capacity.",
    coordinates: [78.4071, 17.4319],
    area_sqft: 21000,
    zoning_type: "Residential",
    ownership_status: "Clear GHMC Permitted Layout Title",
    plot_boundary_geojson: [
      [78.4063, 17.4325],
      [78.4078, 17.4328],
      [78.4082, 17.4312],
      [78.4067, 17.4309]
    ],
    bearing_capacity_kpa: 360,
    water_table_depth_m: 16.5,
    soil_type: "Solid Granite Bedrock & Weathered Rock",
    flood_risk_zone: "Zero Flood Risk (Elevated Slope)",
    max_permissible_floors: 5, // Luxury low-rise zone
    utility_access: ["Dual Feeder High-Tension Grid", "300mm Municipal Water Main", "Underground Fiber Trench"],
    construction_cost_estimate_per_sqft: 4500,

    current_price_sqft: 21000,
    historical_growth_rates: [
      { year: "2021", price: 15000 },
      { year: "2022", price: 16800 },
      { year: "2023", price: 18200 },
      { year: "2024", price: 19800 },
      { year: "2025", price: 21000 }
    ],
    rental_yield_percentage: 4.8,
    roi_percentage: 12.0,
    risk_score: "Low",
    infrastructure_development_pipeline: [
      "Jubilee Hills Checkpost Elevated Underpass Expansion",
      "KBR Park Eco-Buffer Zone Enhancement"
    ],

    schools_nearby: 15,
    hospitals_nearby: 9,
    transit_hubs_nearby: 4,
    nearest_hospital_km: 0.9,
    air_quality_index: 42,
    commute_time_to_city_center_min: 10
  },
  {
    plot_id: "PLOT-103",
    name: "Cyber City Tech Corridor Corner",
    locality: "Gachibowli / HITEC City",
    locality_description: "Mature IT/commercial corridor on flat terrain with high-density commercial zoning.",
    coordinates: [78.3762, 17.4474],
    area_sqft: 32000,
    zoning_type: "Commercial",
    ownership_status: "HMDA & TSIIC Commercial Allotment",
    plot_boundary_geojson: [
      [78.3755, 17.4480],
      [78.3770, 17.4483],
      [78.3774, 17.4468],
      [78.3759, 17.4465]
    ],
    bearing_capacity_kpa: 340,
    water_table_depth_m: 14.0,
    soil_type: "Hard Red Granite Bedrock",
    flood_risk_zone: "Low Risk (Zone 0)",
    max_permissible_floors: 38,
    utility_access: ["Commercial Power Grid", "Industrial Water Mains", "Multi-Carrier Optic Fiber Spine"],
    construction_cost_estimate_per_sqft: 3100,

    current_price_sqft: 13500,
    historical_growth_rates: [
      { year: "2021", price: 9200 },
      { year: "2022", price: 10500 },
      { year: "2023", price: 11800 },
      { year: "2024", price: 12700 },
      { year: "2025", price: 13500 }
    ],
    rental_yield_percentage: 9.1,
    roi_percentage: 15.2,
    risk_score: "Low",
    infrastructure_development_pipeline: [
      "Airport Express Metro Rail Station (Cyber Towers Link)",
      "Smart Underground Utility & Drainage Duct Grid"
    ],

    schools_nearby: 12,
    hospitals_nearby: 8,
    transit_hubs_nearby: 6,
    nearest_hospital_km: 0.5,
    air_quality_index: 55,
    commute_time_to_city_center_min: 15
  },
  {
    plot_id: "PLOT-104",
    name: "Neopolis Golden Heights Node",
    locality: "Kokapet / Narsingi",
    locality_description: "Peri-urban, high-growth expansion node featuring transitional terrain and recent HMDA land auctions.",
    coordinates: [78.3274, 17.3986],
    area_sqft: 40000,
    zoning_type: "Mixed Use",
    ownership_status: "HMDA e-Auction Direct Clear Title",
    plot_boundary_geojson: [
      [78.3265, 17.3992],
      [78.3280, 17.3995],
      [78.3284, 17.3980],
      [78.3268, 17.3977]
    ],
    bearing_capacity_kpa: 290,
    water_table_depth_m: 11.5,
    soil_type: "Gravelly Sandy Clay & Granitic Rock",
    flood_risk_zone: "Very Low Risk",
    max_permissible_floors: 34,
    utility_access: ["Underground HT Power", "Municipal Water Connection", "Stormwater Trunk Grid"],
    construction_cost_estimate_per_sqft: 2400,

    current_price_sqft: 8500,
    historical_growth_rates: [
      { year: "2021", price: 4800 },
      { year: "2022", price: 5900 },
      { year: "2023", price: 7000 },
      { year: "2024", price: 7900 },
      { year: "2025", price: 8500 }
    ],
    rental_yield_percentage: 6.8,
    roi_percentage: 21.0,
    risk_score: "Low",
    infrastructure_development_pipeline: [
      "Neopolis SEZ Dedicated Trumpet Interchange to ORR",
      "Narsingi Elevated Link Flyover Corridor"
    ],

    schools_nearby: 9,
    hospitals_nearby: 5,
    transit_hubs_nearby: 3,
    nearest_hospital_km: 1.8,
    air_quality_index: 38,
    commute_time_to_city_center_min: 24
  },
  {
    plot_id: "PLOT-105",
    name: "Gandipet Lake Front Eco-Parcel",
    locality: "Gandipet / Manikonda",
    locality_description: "Ecologically sensitive lake-adjacent zone governed by high water tables and GO 111 environmental regulations.",
    coordinates: [78.3051, 17.3912],
    area_sqft: 50000,
    zoning_type: "Residential",
    ownership_status: "GO 111 Compliant - Clear HMDA Title",
    plot_boundary_geojson: [
      [78.3042, 17.3920],
      [78.3060, 17.3922],
      [78.3064, 17.3904],
      [78.3046, 17.3901]
    ],
    bearing_capacity_kpa: 240,
    water_table_depth_m: 6.2,
    soil_type: "Alluvial Sandy Clay & Silt",
    flood_risk_zone: "Moderate Risk (Lake Proximity Zone)",
    max_permissible_floors: 12,
    utility_access: ["Eco-Grid Solar Feed", "Borewell Water Mains", "Bio-Septic Drainage System"],
    construction_cost_estimate_per_sqft: 3200,

    current_price_sqft: 9500,
    historical_growth_rates: [
      { year: "2021", price: 4200 },
      { year: "2022", price: 5800 },
      { year: "2023", price: 7200 },
      { year: "2024", price: 8600 },
      { year: "2025", price: 9500 }
    ],
    rental_yield_percentage: 5.5,
    roi_percentage: 24.5,
    risk_score: "Moderate",
    infrastructure_development_pipeline: [
      "Gandipet Eco-Park Promenade & Bio-Retention Lake Belt",
      "Manikonda Link Expressway Widening Project"
    ],

    schools_nearby: 7,
    hospitals_nearby: 4,
    transit_hubs_nearby: 2,
    nearest_hospital_km: 2.5,
    air_quality_index: 28, // Pristine Air
    commute_time_to_city_center_min: 22
  },
  {
    plot_id: "PLOT-106",
    name: "Kompally North Suburban Corridor",
    locality: "Kompally / Medchal",
    locality_description: "Suburban residential corridor with moderate density and flat topography.",
    coordinates: [78.4842, 17.5388],
    area_sqft: 65000,
    zoning_type: "Residential",
    ownership_status: "HMDA Approved Residential Layout",
    plot_boundary_geojson: [
      [78.4834, 17.5396],
      [78.4852, 17.5399],
      [78.4856, 17.5380],
      [78.4838, 17.5377]
    ],
    bearing_capacity_kpa: 380,
    water_table_depth_m: 18.0,
    soil_type: "Dense Gravel & Hard Red Granite",
    flood_risk_zone: "Zero Risk (Flat Plateau)",
    max_permissible_floors: 14,
    utility_access: ["Substation Power Feeder", "Municipal Water Supply", "Sewerage Main Grid"],
    construction_cost_estimate_per_sqft: 1800,

    current_price_sqft: 4200,
    historical_growth_rates: [
      { year: "2021", price: 2400 },
      { year: "2022", price: 2900 },
      { year: "2023", price: 3400 },
      { year: "2024", price: 3800 },
      { year: "2025", price: 4200 }
    ],
    rental_yield_percentage: 7.8,
    roi_percentage: 17.5,
    risk_score: "Low",
    infrastructure_development_pipeline: [
      "NH-44 Nagpur Highway 8-Laning Expansion",
      "Kompally Logistics & Regional Bus Terminal"
    ],

    schools_nearby: 8,
    hospitals_nearby: 5,
    transit_hubs_nearby: 4,
    nearest_hospital_km: 2.2,
    air_quality_index: 48,
    commute_time_to_city_center_min: 32
  },
  {
    plot_id: "PLOT-107",
    name: "Uppal Transit Junction Parcel",
    locality: "Uppal / LB Nagar",
    locality_description: "Older established suburban fringe with mixed residential and light industrial usage.",
    coordinates: [78.5583, 17.3984],
    area_sqft: 22000,
    zoning_type: "Mixed Use",
    ownership_status: "GHMC Permitted Commercial/Mixed Title",
    plot_boundary_geojson: [
      [78.5575, 17.3990],
      [78.5590, 17.3993],
      [78.5594, 17.3977],
      [78.5579, 17.3974]
    ],
    bearing_capacity_kpa: 285,
    water_table_depth_m: 12.0,
    soil_type: "Red Soil & Sandy Clay",
    flood_risk_zone: "Low Risk",
    max_permissible_floors: 22,
    utility_access: ["3-Phase Power Feeder", "Municipal Water Mains", "Direct Metro Line Access"],
    construction_cost_estimate_per_sqft: 2400,

    current_price_sqft: 7600,
    historical_growth_rates: [
      { year: "2021", price: 4500 },
      { year: "2022", price: 5200 },
      { year: "2023", price: 6100 },
      { year: "2024", price: 6900 },
      { year: "2025", price: 7600 }
    ],
    rental_yield_percentage: 7.2,
    roi_percentage: 16.0,
    risk_score: "Low",
    infrastructure_development_pipeline: [
      "Uppal Skywalk Pedestrian Junction Multi-Modal Hub",
      "Warangal Highway Grade Separator Flyover"
    ],

    schools_nearby: 11,
    hospitals_nearby: 7,
    transit_hubs_nearby: 7,
    nearest_hospital_km: 0.7,
    air_quality_index: 60,
    commute_time_to_city_center_min: 15
  },
  {
    plot_id: "PLOT-108",
    name: "Shamshabad Aerotropolis Commercial Zone",
    locality: "Shamshabad",
    locality_description: "Infrastructure-driven growth node adjacent to the airport, dominated by SEZ development.",
    coordinates: [78.4294, 17.2403],
    area_sqft: 95000,
    zoning_type: "Commercial",
    ownership_status: "HMDA Aerotropolis SEZ Special Clearance",
    plot_boundary_geojson: [
      [78.4284, 17.2412],
      [78.4305, 17.2415],
      [78.4309, 17.2394],
      [78.4288, 17.2391]
    ],
    bearing_capacity_kpa: 340,
    water_table_depth_m: 15.0,
    soil_type: "Weathered Granite Rock",
    flood_risk_zone: "Zero Risk",
    max_permissible_floors: 24,
    utility_access: ["Airport High-Capacity Grid", "Industrial Water Pipeline", "Fiber Corridor Spine"],
    construction_cost_estimate_per_sqft: 2600,

    current_price_sqft: 5900,
    historical_growth_rates: [
      { year: "2021", price: 3100 },
      { year: "2022", price: 3800 },
      { year: "2023", price: 4500 },
      { year: "2024", price: 5200 },
      { year: "2025", price: 5900 }
    ],
    rental_yield_percentage: 8.5,
    roi_percentage: 22.8,
    risk_score: "Low",
    infrastructure_development_pipeline: [
      "RGIA Airport Metro Express Connection Line",
      "World Trade Center Shamshabad SEZ Complex"
    ],

    schools_nearby: 6,
    hospitals_nearby: 4,
    transit_hubs_nearby: 6,
    nearest_hospital_km: 1.5,
    air_quality_index: 32,
    commute_time_to_city_center_min: 25
  }
];
const clusterToLocality = {
  "Old City": "Old City (Charminar / Malakpet)",
  "Banjara Hills": "Banjara Hills / Jubilee Hills",
  "Jubilee Hills": "Banjara Hills / Jubilee Hills",
  "Gachibowli": "Gachibowli / HITEC City",
  "HITEC City": "Gachibowli / HITEC City",
  "Kokapet": "Kokapet / Narsingi",
  "Narsingi": "Kokapet / Narsingi",
  "Gandipet": "Gandipet / Manikonda",
  "Manikonda": "Gandipet / Manikonda",
  "Kompally": "Kompally / Medchal",
  "Medchal": "Kompally / Medchal",
  "Uppal": "Uppal / LB Nagar",
  "LB Nagar": "Uppal / LB Nagar",
  "Shamshabad": "Shamshabad",
};


/**
 * Maps incoming Pydantic `PlotData` / `PlotCore` JSON from FastAPI to the UI state model.
 * Handles coordinates format [longitude, latitude] as required by GeoJSON / plot_models.py
 */
export function mapPlotFromBackend(plot) {
  if (!plot) return null;

  // Extract coordinates [longitude, latitude] safely matching plot_models.py
  const coordinates = plot.coordinates
    ? [plot.coordinates.longitude, plot.coordinates.latitude]
    : [0, 0];

  // Extract boundary coordinates if present
  const boundaryCoords = plot.plot_boundary_geojson?.coordinates?.[0]?.map((pt) => [pt[0], pt[1]]) || [];

  const rawCluster = plot.cluster || plot.locality || "Unknown";

  return {
    plot_id: plot.plot_id,
    name: plot.name,
    locality: clusterToLocality[rawCluster] || rawCluster,
    locality_description: `${plot.name} (${plot.zoning_type || 'General'} Zoning)`,
    coordinates,
    area_sqft: plot.area_sqft,
    zoning_type: plot.zoning_type,
    ownership_status: plot.ownership_status,
    plot_boundary_geojson: boundaryCoords,

    // Extract nested sub-models if populated by backend
    builder_metrics: plot.builder_metrics || null,
    investor_metrics: plot.investor_metrics || null,
    buyer_metrics: plot.buyer_metrics || null,
  };
}

/**
 * Enriches base plot data with extended context payload from backend analysis APIs
 */
export function enrichPlotWithContext(plot, data) {
  if (!plot || !data) return plot;

  const ctx = data.context || {};
  const builder = ctx.builder || plot.builder_metrics || {};
  const investor = ctx.investor || plot.investor_metrics || {};
  const buyer = ctx.buyer || plot.buyer_metrics || {};

  const mappedPlot = {
    ...plot,
    locality_description: data.location?.display_name || plot.locality_description,

    // Builder Metrics
    bearing_capacity_kpa: builder.bearing_capacity_kpa ?? null,
    water_table_depth_m: builder.water_table_depth_m ?? null,
    soil_type: builder.soil_type ?? "N/A",
    flood_risk_zone: builder.flood_risk_zone ?? "low",
    max_permissible_floors: builder.max_permissible_floors ?? null,
    utility_access: builder.utility_access ?? { water: false, electricity: false, sewage: false },
    construction_cost_estimate_per_sqft: builder.construction_cost_estimate_per_sqft ?? null,
    construction_suitability: builder.construction_suitability ?? "N/A",
    foundation_recommendation: builder.foundation_recommendation ?? "N/A",
    groundwater_risk: builder.groundwater_risk ?? "N/A",
    excavation_difficulty: builder.excavation_difficulty ?? "N/A",

    // Investor Metrics
    current_price_sqft: investor.current_price_sqft ?? 0,
    rental_yield_percentage: investor.rental_yield_percentage ?? null,
    roi_percentage: investor.roi_percentage ?? null,
    risk_score: investor.risk_score ?? null,
    infrastructure_development_pipeline: investor.infrastructure_development_pipeline || [],

    // Buyer Metrics
    schools_nearby: buyer.schools_nearby ?? 0,
    hospitals_nearby: buyer.hospitals_nearby ?? 0,
    transit_hubs_nearby: buyer.transit_hubs_nearby ?? 0,
    nearest_hospital_km: buyer.nearest_hospital_km ?? null,
    air_quality_index: buyer.air_quality_index ?? null,
    commute_time_to_city_center_min: buyer.commute_time_to_city_center_min ?? null,
    top_nearby_schools: buyer.top_nearby_schools || [],
    top_nearby_hospitals: buyer.top_nearby_hospitals || [],
    top_nearby_shopping_centres: buyer.top_nearby_shopping_centres || [],

    // AI Summaries & Advisory
    location_summary: ctx.location_summary || "",
    property_summary: ctx.property_summary || "",
    strengths: ctx.strengths || [],
    weaknesses: ctx.weaknesses || [],
    investment_recommendation: ctx.investment_recommendation || "",
    construction_recommendation: ctx.construction_recommendation || "",
    buyer_recommendation: ctx.buyer_recommendation || "",
    scores: ctx.scores || {},
  };

  // Process historical growth rates array safely
  const basePrice = mappedPlot.current_price_sqft;
  if (investor.historical_growth_rates && Array.isArray(investor.historical_growth_rates)) {
    const rates = investor.historical_growth_rates;
    mappedPlot.historical_growth_rates = rates.map((rate, idx) => {
      const year = (2021 + idx).toString();
      const price = Math.round(basePrice * (1 + (rate - (rates[rates.length - 1] || 0)) / 100));
      return { year, price: price || basePrice };
    });
  } else {
    mappedPlot.historical_growth_rates = [];
  }

  return mappedPlot;
}
// Rename the original hardcoded array
const BASE_PLOTS = PLOTS_DATA;

// Generate 4 additional variants per base plot (5 total per locality)
function generatePlotVariants(basePlots) {
  const allPlots = [];
  basePlots.forEach((base) => {
    allPlots.push(base); // keep the original
    for (let i = 1; i <= 4; i++) {
      const jitter = i * 0.004; // small coordinate offset so markers don't overlap
      const variance = 1 + (Math.random() * 0.2 - 0.1); // ±10% numeric variance

      allPlots.push({
        ...base,
        plot_id: `${base.plot_id}-V${i}`,
        name: `${base.name} (Parcel ${i + 1})`,
        coordinates: [base.coordinates[0] + jitter, base.coordinates[1] + jitter],
        area_sqft: Math.round(base.area_sqft * variance),
        bearing_capacity_kpa: Math.round(base.bearing_capacity_kpa * variance),
        current_price_sqft: Math.round(base.current_price_sqft * variance),
        roi_percentage: +(base.roi_percentage * variance).toFixed(1),
        rental_yield_percentage: +(base.rental_yield_percentage * variance).toFixed(1),
        construction_cost_estimate_per_sqft: Math.round(base.construction_cost_estimate_per_sqft * variance),
      });
    }
  });
  return allPlots;
}

// Override the export with the expanded 40-plot set
export const EXPANDED_PLOTS_DATA = generatePlotVariants(BASE_PLOTS);