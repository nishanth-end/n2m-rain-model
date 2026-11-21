/**
 * N²M Flood Prediction Model — Centralized Content Configuration
 * =============================================================
 * All project descriptions, academic disclosures, maintainer details,
 * and editorial copy are managed in this single file.
 * 
 * Edit the clearly marked [ADD ...] placeholders below to customize the text.
 */

export const content = {
  // ---------------------------------------------------------------------------
  // Project Identity & Typography
  // ---------------------------------------------------------------------------
  brand: {
    name: "N²M Flood Prediction Model",
    shortName: "N²M Model",
    version: "v1.0 (Research Prototype)",
    subtitle: "Experimental Urban Flood Susceptibility Mapping & Spatial Risk Analysis — Bengaluru",
    tagline: "A high-resolution machine learning framework estimating terrain and precipitation susceptibility across 3,026 urban grid cells.",
    location: "Bengaluru, Karnataka, India",
    monsoonEvent: "September 2022 Holdout Sequence (E2022_09)",
  },

  // ---------------------------------------------------------------------------
  // Landing Page: Narrative & Academic Sections
  // ---------------------------------------------------------------------------
  home: {
    hero: {
      headline: "Spatial Flood Susceptibility for Bengaluru's Built Environment",
      subheadline: "Integrating antecedent precipitation matrices and high-resolution terrain indices to quantify relative urban inundation vulnerability.",
      ctaPrimary: "Explore Flood Map",
      ctaSecondary: "Methodology & Data",
    },

    overview: {
      title: "Project Overview",
      description: "[N²M Flood Prediction Model evaluates the complex hydrological response of Bengaluru's undulating terrain during monsoon downpours. By coupling daily satellite-gauge precipitation with topographic indicators, the model ranks 3,026 spatial cells (approx. 500m × 500m) into daily relative susceptibility tiers.]",
      keyGoal: "To demonstrate how machine learning and open geospatial datasets can provide localized spatial prioritization during extreme rainfall events without relying on expensive, computationally prohibitive 2D hydrodynamic simulation networks.",
    },

    problemStatement: {
      title: "The Problem Statement",
      content: "[Rapid, uncontrolled urbanization across Bengaluru has severely altered natural drainage valleys, encroached upon interconnected lake cascades (keres), and increased impervious surfaces from under 10% in 1973 to over 90% in dense eastern corridors. Conventional municipal flood alerts remain city-wide or ward-level generalizations, failing to pinpoint which micro-catchments and arterial underpasses are at imminent risk during localized cloudbursts.]",
      urbanChallenge: "Precipitation across Bengaluru is highly localized: a cloudburst dropping 80 mm in Bellandur or Mahadevapura may register as mere drizzle across northern Rajajinagar. Micro-topography dictates inundation.",
    },

    approach: {
      title: "Our Engineering Approach",
      content: "[The framework partitions Greater Bengaluru into 3,026 discrete grid cells. Each cell is parameterized with 10 static hydrological terrain attributes extracted from digital elevation models and vector hydrography, coupled with 8 dynamic rainfall features derived from CHIRPS precipitation grids. An explainable gradient-boosted decision tree (XGBoost) model evaluates relative daily risk.]",
      pillars: [
        {
          title: "Terrain Morphology",
          description: "Elevation, slope, Topographic Wetness Index (TWI), Height Above Nearest Drainage (HAND), and flow accumulation.",
        },
        {
          title: "Built Surface & Drainage",
          description: "Impervious surface fraction, proximity to major arterial roads, distances to lakes, and natural stormwater drains.",
        },
        {
          title: "Precipitation Dynamics",
          description: "Daily rainfall, antecedent cumulative saturation (3d, 7d, 14d, 30d rolling windows), and preceding daily lags (lag1, lag2, lag3).",
        },
      ],
    },

    modelOverview: {
      title: "The Machine Learning Model",
      architecture: "XGBoost Classifier (binary:logistic) calibrated with scale_pos_weight",
      summary: "[The predictive engine is an XGBoost decision tree ensemble optimized for severe class imbalance. Rather than attempting to predict arbitrary flood boundaries, the model computes a continuous susceptibility index and partitions cells into strictly relative daily rank tiers: High (Top 150 cells, ~5%), Moderate (Ranks 151–300, ~10%), and Baseline/None (remaining 2,726 cells).]",
      trainingEventContext: "The historical replay uses a dedicated holdout model (flood_xgb_holdout_E2022_09.json) strictly sequestered from training on the September 2022 flood event to ensure unbiased validation.",
    },

    statistics: [
      { value: "3,026", label: "Grid Cells Evaluated", detail: "~500 m spatial resolution across Bengaluru" },
      { value: "18", label: "Model Features", detail: "10 static terrain indices + 8 dynamic rainfall metrics" },
      { value: "24 Days", label: "Replay Event Span", detail: "22 Aug 2022 to 14 Sep 2022 sequence" },
      { value: "2.0×", label: "Holdout Precision Lift", detail: "PR-AUC 0.0026 vs 0.0013 random chance baseline" },
    ],

    limitations: {
      title: "Scientific Boundaries & Known Limitations",
      summary: "[The N²M Flood Prediction Model is an empirical academic research prototype and is NOT a certified emergency early warning system. Users and researchers must interpret results within the following known constraints:]",
      items: [
        "Relative Susceptibility Only: Model outputs represent relative daily spatial priority, NOT calibrated physical flood probabilities.",
        "Ground Truth Sparsity: Model ground truth relies on ~10 verified flooded locations across 6 historical events; surrounding positive cells are assumed via a 3×3 spatial buffer.",
        "Precipitation Resolution: CHIRPS daily ~5 km gridded data cannot capture hyper-local convective cloudbursts lasting 30–60 minutes.",
        "No Hydrodynamic Flow: The model evaluates local cell susceptibility but does not simulate dynamic fluid flow between adjacent cells.",
        "Non-Operational: Strictly non-certified for life-safety or civic evacuation deployment.",
      ],
    },
  },

  // ---------------------------------------------------------------------------
  // Live & Simulation Page
  // ---------------------------------------------------------------------------
  simulation: {
    rainfallContext: {
      title: "Precipitation Data Context & Source Specifications",
      provider: "Climate Hazards Center CHIRPS (UCSB/CHG)",
      resolution: "~0.05° spatial grid (approximately 5.3 km resolution at Bengaluru latitude)",
      temporalCadence: "Daily cumulative rainfall (mm), UTC calendar cycle",
      coverage: "Full Greater Bengaluru Urban Agglomeration (3,026 cells linked via cell_pixel_map.csv)",
      statusNotice: "[LIVE INGESTION STATUS: Live precipitation ingestion remains an isolated research prototype. The production model requires CHIRPS-calibrated feature distributions. Real-time feeds (such as Open-Meteo or IMD ground stations) exhibit distributional shifts and cannot be silently substituted without re-calibration.]",
    },
    demoMode: {
      title: "Manual Input Sensitivity Demonstration",
      subtitle: "Observe how varying rainfall accumulation scenarios alter model susceptibility scores for a sample cell.",
      notice: "SIMULATED LAB ENVIRONMENT — Input adjustments here are for educational demonstration and do not affect the historical replay archive or municipal systems.",
      presets: [
        {
          name: "Dry Pre-Monsoon Baseline",
          desc: "Negligible antecedent rainfall, dry soil saturation",
          values: { rain_1d_mm: 0.0, rain_3d_mm: 2.5, rain_7d_mm: 5.0, rain_14d_mm: 12.0, rain_30d_mm: 35.0, rain_lag1_mm: 0.0, rain_lag2_mm: 1.0, rain_lag3_mm: 1.5 }
        },
        {
          name: "Sustained Monsoon Inundation",
          desc: "Repeated heavy showers causing high soil water saturation",
          values: { rain_1d_mm: 45.0, rain_3d_mm: 95.0, rain_7d_mm: 160.0, rain_14d_mm: 240.0, rain_30d_mm: 380.0, rain_lag1_mm: 30.0, rain_lag2_mm: 20.0, rain_lag3_mm: 15.0 }
        },
        {
          name: "September 2022 Extreme Cloudburst",
          desc: "Historical cloudburst conditions observed in eastern valleys (Mahadevapura/Bellandur)",
          values: { rain_1d_mm: 82.5, rain_3d_mm: 145.0, rain_7d_mm: 215.0, rain_14d_mm: 285.0, rain_30d_mm: 420.0, rain_lag1_mm: 48.0, rain_lag2_mm: 14.5, rain_lag3_mm: 0.0 }
        }
      ]
    }
  },

  // ---------------------------------------------------------------------------
  // Telegram Page: Demonstration Bot Integration
  // ---------------------------------------------------------------------------
  telegram: {
    title: "Telegram Alert Demonstration Channel",
    subtitle: "Private developer sandbox showcasing automated spatial summary dispatch using historical replay data.",
    botUsername: "@N2M_Flood_Demo_Bot",
    botPlaceholder: "[ADD TELEGRAM BOT USERNAME: e.g. @N2M_Flood_Demo_Bot]",
    status: "Sandbox Offline / Local Simulation Mode (TELEGRAM_ENABLED=false)",
    statusDescription: "In accordance with safety guidelines, active push notifications to public Telegram channels are disabled by default. The preview interface below renders the exact formatted alert payload in-memory without making live bot API calls.",
    tokenGuidance: "[TELEGRAM BOT CONFIGURATION: To enable private testing, configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the backend .env configuration. Tokens must never be committed to source repositories or exposed to the client.]",
    warning: "EXPERIMENTAL DEMO ONLY — Messages generated through this interface are historical simulations and must never be broadcast as public emergency directives.",
  },

  // ---------------------------------------------------------------------------
  // Maintainers & Academic Credits Page
  // ---------------------------------------------------------------------------
  creators: {
    title: "Project Maintainers",
    subtitle: "An academic engineering inquiry into urban hydrology and explainable geospatial machine learning.",
    institution: "Dayananda Sagar College of Engineering, Bengaluru",
    department: "Department of Computer Science & Engineering",
    facultyGuide: {
      name: "Dr. Punith Kumar",
      role: "Faculty Project Advisor",
      designation: "Associate Professor, Department of Computer Science & Engineering",
      affiliation: "Dayananda Sagar College of Engineering, Bengaluru",
    },
    teamMembers: [
      {
        name: "Nishanth G M",
        role: "Data Pipeline & Terrain Feature Extraction",
        contribution: "Constructed the 3,026-cell spatial skeleton, DEM hydrology extraction, HAND, and CHIRPS rainfall linkage.",
      },
      {
        name: "Mohith M",
        role: "Machine Learning Modeling & Validation",
        contribution: "Developed the XGBoost ensemble, holdout evaluation framework, class imbalance calibration, and PR-AUC validation.",
      },
      {
        name: "Nihal Rao",
        role: "Full Stack Developer",
        contribution: "Designed the academic GIS research dashboard, high-performance Canvas map renderer, and simulation interface.",
      },

    ],
    acknowledgements: "We express our gratitude to our project guide, department faculty, and the open-source geospatial community for tools and open datasets. Special acknowledgment to KSNDMC (Karnataka State Natural Disaster Monitoring Centre) and BBMP for open hydrological reports.",
    datasetCredits: [
      {
        title: "CHIRPS Precipitation",
        source: "Climate Hazards Center, UC Santa Barbara",
        description: "Daily quasi-global gridded precipitation dataset blending satellite cold cloud duration and station records.",
      },
      {
        title: "SRTM Digital Elevation Model",
        source: "NASA / USGS",
        description: "30-meter elevation data utilized for slope, flow direction, and Topographic Wetness Index (TWI) calculation.",
      },
      {
        title: "Copernicus Sentinel-1 SAR",
        source: "European Space Agency (ESA)",
        description: "Synthetic Aperture Radar ground scattering backscatter used for historical surface water boundary detection.",
      },
      {
        title: "OpenStreetMap (OSM)",
        source: "OpenStreetMap Contributors",
        description: "Urban road vectors, stormwater drainage channels (rajakaluves), and civic ward administrative polygons.",
      },
    ],
    tooling: [
      { name: "XGBoost", role: "Gradient Boosted Trees (Estimator Version 3.4.1)" },
      { name: "FastAPI", role: "Asynchronous Python Backend & OpenAPI Gateway" },
      { name: "Leaflet & Canvas", role: "Lightweight High-FPS Geospatial Vector Rendering" },
      { name: "React & Vite", role: "Component Architecture & Rapid Bundling" },
      { name: "Pandas & PyArrow", role: "Vectorized Parquet Storage & In-Memory Replay" },
    ],
    contact: {
      email: "nishanthenggex@gmail.com",
      github: "https://github.com/nishanth-end/n2m-rain-model",
      location: "Bengaluru, Karnataka, India",
    },
  },
};
