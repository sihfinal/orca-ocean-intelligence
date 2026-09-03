import React, { useState, useEffect, useRef  } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Wind, 
  Waves, 
  Zap, 
  Compass, 
  Eye, 
  CheckCircle2, 
  XCircle,
  Radio,
  Anchor,
  Navigation
} from 'lucide-react';
import { WeatherObservation } from '../types';
import { t } from '../utils/translations';

interface SeaSafetyBarometerProps {
  weather: WeatherObservation | null;
  portName?: string;
  onPortSelect?: (lat: number, lon: number, name: string) => void;
  currentLang?: string; // <-- Add this line here
}

export interface HarbourTelemetry {
  id: string;
  name: string;
  state: string;
  lat: number;
  lon: number;
  weather: WeatherObservation;
}

export const INDIAN_HARBOURS_DATA: HarbourTelemetry[] = [
  {
    id: 'kochi',
    name: "Kochi Fishing Harbour",
    state: "Kerala",
    lat: 9.9416,
    lon: 76.2575,
    weather: {
      latitude: 9.9416,
      longitude: 76.2575,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 86.5,
      safety_badge_color: 'emerald',
      actionable_advice: "Optimal coastal conditions. Moderate swells under 1.2m. Mechanized and motorized crafts cleared for offshore venture within 25 NM.",
      significant_wave_height_m: 1.15,
      swell_period_seconds: 7.2,
      wind_speed_knots: 11.4,
      wind_speed_kmph: 21.1,
      wind_direction_degrees: 245,
      beaufort_scale: 3,
      sea_state: "Slight / Smooth",
      lightning_probability_percent: 8,
      visibility_km: 14.5,
      cyclone_influence: {
        active_cyclone: null,
        distance_km: null,
        intensity: null
      },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'mumbai',
    name: "Sassoon Dock, Mumbai",
    state: "Maharashtra",
    lat: 18.9167,
    lon: 72.8250,
    weather: {
      latitude: 18.9167,
      longitude: 72.8250,
      safety_status: 'EXERCISE_CAUTION',
      safety_index: 68.2,
      safety_badge_color: 'amber',
      actionable_advice: "Moderate chop and gusty cross-currents beyond 15 NM. Non-motorized traditional crafts advised to remain within 8 NM of Mumbai harbour.",
      significant_wave_height_m: 1.85,
      swell_period_seconds: 8.5,
      wind_speed_knots: 16.8,
      wind_speed_kmph: 31.1,
      wind_direction_degrees: 290,
      beaufort_scale: 4,
      sea_state: "Moderate Choppy",
      lightning_probability_percent: 15,
      visibility_km: 11.2,
      cyclone_influence: {
        active_cyclone: null,
        distance_km: null,
        intensity: null
      },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'chennai',
    name: "Kasimedu Fishing Harbour, Chennai",
    state: "Tamil Nadu",
    lat: 13.1250,
    lon: 80.3000,
    weather: {
      latitude: 13.1250,
      longitude: 80.3000,
      safety_status: 'EXERCISE_CAUTION',
      safety_index: 54.0,
      safety_badge_color: 'amber',
      actionable_advice: "High breaker swells along Coromandel coastline. Small motorized boats advised to suspend venture. Mechanized deep-sea trawlers exercise high vigilance.",
      significant_wave_height_m: 2.40,
      swell_period_seconds: 9.1,
      wind_speed_knots: 22.5,
      wind_speed_kmph: 41.6,
      wind_direction_degrees: 110,
      beaufort_scale: 6,
      sea_state: "Rough / High Breaker",
      lightning_probability_percent: 35,
      visibility_km: 8.5,
      cyclone_influence: {
        active_cyclone: "Bay of Bengal Low Pressure",
        distance_km: 420,
        intensity: "Developing Depression"
      },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'vizag',
    name: "Visakhapatnam Fishing Harbour",
    state: "Andhra Pradesh",
    lat: 17.6868,
    lon: 83.2185,
    weather: {
      latitude: 17.6868,
      longitude: 83.2185,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 82.5,
      safety_badge_color: 'emerald',
      actionable_advice: "Favorable sea state across Northern Circars basin. Tuna longliners and motorized gillnetters cleared for 35 NM deep-sea operations.",
      significant_wave_height_m: 1.30,
      swell_period_seconds: 6.8,
      wind_speed_knots: 12.0,
      wind_speed_kmph: 22.2,
      wind_direction_degrees: 180,
      beaufort_scale: 3,
      sea_state: "Smooth / Gentle",
      lightning_probability_percent: 12,
      visibility_km: 15.0,
      cyclone_influence: {
        active_cyclone: null,
        distance_km: null,
        intensity: null
      },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'veraval',
    name: "Veraval Fisheries Port",
    state: "Gujarat",
    lat: 20.9000,
    lon: 70.3667,
    weather: {
      latitude: 20.9000,
      longitude: 70.3667,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 79.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Favorable gillnetting and trawling conditions in Saurashtra basin. Maintain strict GPS vigil near Sir Creek Pakistan boundary.",
      significant_wave_height_m: 1.45,
      swell_period_seconds: 7.5,
      wind_speed_knots: 13.8,
      wind_speed_kmph: 25.5,
      wind_direction_degrees: 315,
      beaufort_scale: 4,
      sea_state: "Slight",
      lightning_probability_percent: 5,
      visibility_km: 16.0,
      cyclone_influence: {
        active_cyclone: null,
        distance_km: null,
        intensity: null
      },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'tuticorin',
    name: "Tuticorin Fishing Port",
    state: "Tamil Nadu",
    lat: 8.7642,
    lon: 78.1348,
    weather: {
      latitude: 8.7642,
      longitude: 78.1348,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 72.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Moderate channel currents in Gulf of Mannar. Sea venture cleared with mandatory 10 NM safe buffer from Sri Lanka IMBL boundary line.",
      significant_wave_height_m: 1.60,
      swell_period_seconds: 8.0,
      wind_speed_knots: 15.2,
      wind_speed_kmph: 28.1,
      wind_direction_degrees: 140,
      beaufort_scale: 4,
      sea_state: "Moderate",
      lightning_probability_percent: 18,
      visibility_km: 12.0,
      cyclone_influence: {
        active_cyclone: null,
        distance_km: null,
        intensity: null
      },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'paradip',
    name: "Paradip Fishing Harbour",
    state: "Odisha",
    lat: 20.2667,
    lon: 86.6667,
    weather: {
      latitude: 20.2667,
      longitude: 86.6667,
      safety_status: 'HAZARDOUS_NO_VENTURE',
      safety_index: 28.0,
      safety_badge_color: 'red',
      actionable_advice: "🚨 SEVERE WEATHER DIRECTIVE: Intense gale squalls associated with Northern Bay of Bengal cyclonic depression. Complete fishing suspension in effect. Do not venture into the sea.",
      significant_wave_height_m: 3.20,
      swell_period_seconds: 11.4,
      wind_speed_knots: 31.5,
      wind_speed_kmph: 58.3,
      wind_direction_degrees: 95,
      beaufort_scale: 7,
      sea_state: "Very Rough / High Gale",
      lightning_probability_percent: 65,
      visibility_km: 4.5,
      cyclone_influence: {
        active_cyclone: "Cyclonic Storm 'MIDHILI'",
        distance_km: 210,
        intensity: "Severe Cyclonic Storm (Gale 65 kts)"
      },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'mangalore',
    name: "Mangalore Old Port",
    state: "Karnataka",
    lat: 12.8550,
    lon: 74.8350,
    weather: {
      latitude: 12.8550,
      longitude: 74.8350,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 91.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Excellent calm sea conditions along Kanara coastline. All artisanal, motorized, and mechanized vessels cleared for round-the-clock venture.",
      significant_wave_height_m: 0.90,
      swell_period_seconds: 6.5,
      wind_speed_knots: 9.2,
      wind_speed_kmph: 17.0,
      wind_direction_degrees: 260,
      beaufort_scale: 2,
      sea_state: "Calm / Rippled",
      lightning_probability_percent: 6,
      visibility_km: 18.0,
      cyclone_influence: {
        active_cyclone: null,
        distance_km: null,
        intensity: null
      },
      timestamp: new Date().toISOString()
    }
  },
    // --- KERALA ---
  {
    id: 'munambam',
    name: "Munambam Fishing Harbour",
    state: "Kerala",
    lat: 10.1800,
    lon: 76.1750,
    weather: {
      latitude: 10.1800,
      longitude: 76.1750,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 85.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Calm sea conditions along Kochi-Munambam coastal belt. Mechanized gillnetters cleared for 30 NM offshore venture.",
      significant_wave_height_m: 1.10,
      swell_period_seconds: 7.0,
      wind_speed_knots: 11.0,
      wind_speed_kmph: 20.4,
      wind_direction_degrees: 250,
      beaufort_scale: 3,
      sea_state: "Smooth / Slight",
      lightning_probability_percent: 10,
      visibility_km: 14.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'neendakara',
    name: "Neendakara Fishing Harbour",
    state: "Kerala",
    lat: 8.9350,
    lon: 76.5380,
    weather: {
      latitude: 8.9350,
      longitude: 76.5380,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 88.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Favorable upwelling and trawl conditions near Ashtamudi estuary. Bottom trawlers cleared for round-the-clock venture.",
      significant_wave_height_m: 1.05,
      swell_period_seconds: 6.9,
      wind_speed_knots: 10.2,
      wind_speed_kmph: 18.9,
      wind_direction_degrees: 240,
      beaufort_scale: 3,
      sea_state: "Smooth",
      lightning_probability_percent: 7,
      visibility_km: 15.5,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'sakthikulangara',
    name: "Sakthikulangara Fishing Harbour",
    state: "Kerala",
    lat: 8.9220,
    lon: 76.5500,
    weather: {
      latitude: 8.9220,
      longitude: 76.5500,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 87.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Normal coastal swells. Deep-sea longliners and motorized ring-seiners cleared for Southern Kerala maritime sector.",
      significant_wave_height_m: 1.12,
      swell_period_seconds: 7.1,
      wind_speed_knots: 10.8,
      wind_speed_kmph: 20.0,
      wind_direction_degrees: 235,
      beaufort_scale: 3,
      sea_state: "Slight",
      lightning_probability_percent: 8,
      visibility_km: 15.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'vizhinjam',
    name: "Vizhinjam Fishing Harbour",
    state: "Kerala",
    lat: 8.3760,
    lon: 76.9890,
    weather: {
      latitude: 8.3760,
      longitude: 76.9890,
      safety_status: 'EXERCISE_CAUTION',
      safety_index: 69.5,
      safety_badge_color: 'amber',
      actionable_advice: "Strong oceanic cross-currents near Southern Tip convergence. Small crafts advise caution beyond 12 NM.",
      significant_wave_height_m: 1.75,
      swell_period_seconds: 8.4,
      wind_speed_knots: 16.0,
      wind_speed_kmph: 29.6,
      wind_direction_degrees: 220,
      beaufort_scale: 4,
      sea_state: "Moderate Choppy",
      lightning_probability_percent: 14,
      visibility_km: 13.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'koyilandy',
    name: "Koyilandy Fishing Harbour",
    state: "Kerala",
    lat: 11.4360,
    lon: 75.6940,
    weather: {
      latitude: 11.4360,
      longitude: 75.6940,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 84.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Gentle breeze along Malabar coastline. Motorized purse-seiners and artisanal crafts cleared for 25 NM operations.",
      significant_wave_height_m: 1.20,
      swell_period_seconds: 7.3,
      wind_speed_knots: 11.5,
      wind_speed_kmph: 21.3,
      wind_direction_degrees: 260,
      beaufort_scale: 3,
      sea_state: "Slight",
      lightning_probability_percent: 9,
      visibility_km: 14.5,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },

  // --- KARNATAKA ---
  {
    id: 'malpe',
    name: "Malpe Fishing Harbour",
    state: "Karnataka",
    lat: 13.3496,
    lon: 74.7031,
    weather: {
      latitude: 13.3496,
      longitude: 74.7031,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 89.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Optimal fishing conditions along Kanara-Udupi shelf. Multi-day mechanized deep-sea trawlers cleared for venture.",
      significant_wave_height_m: 0.95,
      swell_period_seconds: 6.6,
      wind_speed_knots: 9.8,
      wind_speed_kmph: 18.1,
      wind_direction_degrees: 255,
      beaufort_scale: 3,
      sea_state: "Calm / Slight",
      lightning_probability_percent: 5,
      visibility_km: 17.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'karwar',
    name: "Karwar (Baithkol) Fishing Harbour",
    state: "Karnataka",
    lat: 14.8080,
    lon: 74.1250,
    weather: {
      latitude: 14.8080,
      longitude: 74.1250,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 90.5,
      safety_badge_color: 'emerald',
      actionable_advice: "Protected natural harbour bay. All categories of fishing vessels cleared for offshore venture up to 35 NM.",
      significant_wave_height_m: 0.90,
      swell_period_seconds: 6.4,
      wind_speed_knots: 9.0,
      wind_speed_kmph: 16.7,
      wind_direction_degrees: 270,
      beaufort_scale: 2,
      sea_state: "Calm / Rippled",
      lightning_probability_percent: 4,
      visibility_km: 18.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },

  // --- MAHARASHTRA ---
  {
    id: 'mallet_bunder',
    name: "New Ferry Wharf (Mallet Bunder)",
    state: "Maharashtra",
    lat: 18.9550,
    lon: 72.8480,
    weather: {
      latitude: 18.9550,
      longitude: 72.8480,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 78.5,
      safety_badge_color: 'emerald',
      actionable_advice: "Moderate maritime traffic and favorable offshore winds. Deep-sea trawlers cleared with navigational radar vigil.",
      significant_wave_height_m: 1.40,
      swell_period_seconds: 7.6,
      wind_speed_knots: 13.5,
      wind_speed_kmph: 25.0,
      wind_direction_degrees: 295,
      beaufort_scale: 4,
      sea_state: "Slight / Moderate",
      lightning_probability_percent: 11,
      visibility_km: 12.5,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'ratnagiri',
    name: "Ratnagiri (Mirkarwada) Harbour",
    state: "Maharashtra",
    lat: 16.9950,
    lon: 73.2820,
    weather: {
      latitude: 16.9950,
      longitude: 73.2820,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 83.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Favorable Konkan coastal conditions. Mechanized purse-seiners cleared for 30 NM deep-sea operations.",
      significant_wave_height_m: 1.25,
      swell_period_seconds: 7.2,
      wind_speed_knots: 12.0,
      wind_speed_kmph: 22.2,
      wind_direction_degrees: 280,
      beaufort_scale: 3,
      sea_state: "Smooth / Slight",
      lightning_probability_percent: 6,
      visibility_km: 16.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },

  // --- GOA ---
  {
    id: 'malim',
    name: "Malim Fishing Jetty",
    state: "Goa",
    lat: 15.5030,
    lon: 73.8320,
    weather: {
      latitude: 15.5030,
      longitude: 73.8320,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 86.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Calm Mandovi estuary mouth and coastal waters. All motorized and mechanized crafts cleared for venture.",
      significant_wave_height_m: 1.05,
      swell_period_seconds: 6.8,
      wind_speed_knots: 10.5,
      wind_speed_kmph: 19.4,
      wind_direction_degrees: 275,
      beaufort_scale: 3,
      sea_state: "Smooth",
      lightning_probability_percent: 7,
      visibility_km: 16.5,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },

  // --- GUJARAT ---
  {
    id: 'mangrol',
    name: "Mangrol Fishing Harbour",
    state: "Gujarat",
    lat: 21.1200,
    lon: 70.1150,
    weather: {
      latitude: 21.1200,
      longitude: 70.1150,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 80.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Saurashtra shelf clear. Mechanized bottom trawlers cleared for 30 NM deep-sea fishing.",
      significant_wave_height_m: 1.40,
      swell_period_seconds: 7.4,
      wind_speed_knots: 13.2,
      wind_speed_kmph: 24.4,
      wind_direction_degrees: 310,
      beaufort_scale: 4,
      sea_state: "Slight",
      lightning_probability_percent: 6,
      visibility_km: 15.5,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'porbandar',
    name: "Porbandar Fishing Harbour",
    state: "Gujarat",
    lat: 21.6417,
    lon: 69.6293,
    weather: {
      latitude: 21.6417,
      longitude: 69.6293,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 81.0,
      safety_badge_color: 'emerald',
      actionable_advice: "North Arabian Sea clear. Maintain strict GPS geofence buffer from Sir Creek Pakistan boundary.",
      significant_wave_height_m: 1.35,
      swell_period_seconds: 7.3,
      wind_speed_knots: 12.8,
      wind_speed_kmph: 23.7,
      wind_direction_degrees: 320,
      beaufort_scale: 3,
      sea_state: "Slight",
      lightning_probability_percent: 5,
      visibility_km: 16.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },

  // --- TAMIL NADU ---
  {
    id: 'nagapattinam',
    name: "Nagapattinam Fishing Harbour",
    state: "Tamil Nadu",
    lat: 10.7650,
    lon: 79.8450,
    weather: {
      latitude: 10.7650,
      longitude: 79.8450,
      safety_status: 'EXERCISE_CAUTION',
      safety_index: 64.0,
      safety_badge_color: 'amber',
      actionable_advice: "Moderate swell breakers along Coromandel coast. Maintain 8 NM safe buffer from Palk Strait Sri Lanka IMBL.",
      significant_wave_height_m: 1.95,
      swell_period_seconds: 8.8,
      wind_speed_knots: 18.5,
      wind_speed_kmph: 34.3,
      wind_direction_degrees: 115,
      beaufort_scale: 5,
      sea_state: "Moderate Choppy",
      lightning_probability_percent: 22,
      visibility_km: 10.5,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },
  {
    id: 'chinnamuttom',
    name: "Chinnamuttom Fishing Harbour",
    state: "Tamil Nadu",
    lat: 8.0930,
    lon: 77.5620,
    weather: {
      latitude: 8.0930,
      longitude: 77.5620,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 76.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Tri-sea confluence normal swells. Motorized and mechanized crafts cleared for Gulf of Mannar sector.",
      significant_wave_height_m: 1.50,
      swell_period_seconds: 7.8,
      wind_speed_knots: 14.5,
      wind_speed_kmph: 26.9,
      wind_direction_degrees: 150,
      beaufort_scale: 4,
      sea_state: "Moderate",
      lightning_probability_percent: 12,
      visibility_km: 13.5,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },

  // --- ANDHRA PRADESH ---
  {
    id: 'kakinada',
    name: "Kakinada Fishing Harbour",
    state: "Andhra Pradesh",
    lat: 16.9600,
    lon: 82.2500,
    weather: {
      latitude: 16.9600,
      longitude: 82.2500,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 81.5,
      safety_badge_color: 'emerald',
      actionable_advice: "Godavari delta plume rich in pelagic catch. Trawlers cleared for 30 NM deep-sea venture.",
      significant_wave_height_m: 1.35,
      swell_period_seconds: 7.1,
      wind_speed_knots: 12.5,
      wind_speed_kmph: 23.2,
      wind_direction_degrees: 175,
      beaufort_scale: 3,
      sea_state: "Smooth / Slight",
      lightning_probability_percent: 15,
      visibility_km: 14.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },

  // --- ODISHA ---
  {
    id: 'dhamara',
    name: "Dhamara Fishing Harbour",
    state: "Odisha",
    lat: 20.7950,
    lon: 86.9550,
    weather: {
      latitude: 20.7950,
      longitude: 86.9550,
      safety_status: 'EXERCISE_CAUTION',
      safety_index: 62.0,
      safety_badge_color: 'amber',
      actionable_advice: "Gahirmatha turtle sanctuary nearby — respect 20 km seasonal buffer. Moderate swell in outer channel.",
      significant_wave_height_m: 2.10,
      swell_period_seconds: 8.9,
      wind_speed_knots: 19.2,
      wind_speed_kmph: 35.6,
      wind_direction_degrees: 100,
      beaufort_scale: 5,
      sea_state: "Moderate Choppy",
      lightning_probability_percent: 28,
      visibility_km: 9.5,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  },

  // --- WEST BENGAL ---
  {
    id: 'petuaghat',
    name: "Petuaghat (Deshapran) Fishing Harbour",
    state: "West Bengal",
    lat: 21.7890,
    lon: 87.8920,
    weather: {
      latitude: 21.7890,
      longitude: 87.8920,
      safety_status: 'SAFE_FOR_VENTURE',
      safety_index: 77.0,
      safety_badge_color: 'emerald',
      actionable_advice: "Rasulpur river mouth tidal streams active. Mechanized Hilsa gillnetters cleared for Northern Bay of Bengal.",
      significant_wave_height_m: 1.45,
      swell_period_seconds: 7.5,
      wind_speed_knots: 13.8,
      wind_speed_kmph: 25.6,
      wind_direction_degrees: 120,
      beaufort_scale: 4,
      sea_state: "Slight / Moderate",
      lightning_probability_percent: 20,
      visibility_km: 12.0,
      cyclone_influence: { active_cyclone: null, distance_km: null, intensity: null },
      timestamp: new Date().toISOString()
    }
  }
];

export const SeaSafetyBarometer: React.FC<SeaSafetyBarometerProps> = ({
  weather: parentWeather,
  portName = "Kochi Fishing Harbour",
  onPortSelect,
  currentLang = 'en'
}) => {
  const [selectedHarbourId, setSelectedHarbourId] = useState<string>('kochi');
  const [activeWeather, setActiveWeather] = useState<WeatherObservation>(
    INDIAN_HARBOURS_DATA[0].weather
  );
  const [activePortName, setActivePortName] = useState<string>(
    INDIAN_HARBOURS_DATA[0].name
  );
  // --- ADDED FILTER & SEARCH STATES ---
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedState, setSelectedState] = useState<string>('All');

  const filteredHarbours = INDIAN_HARBOURS_DATA.filter((h) => {
    const matchesSearch = h.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          h.state.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesState = selectedState === 'All' || h.state === selectedState;
    return matchesSearch && matchesState;
  });

  const uniqueStates = ['All', ...Array.from(new Set(INDIAN_HARBOURS_DATA.map(h => h.state)))];
  // If parent passes a live weather update for a selected coord
  const userSelectedRef = useRef<boolean>(false);
  useEffect(() => {
    if (parentWeather && !userSelectedRef.current) {
      setActiveWeather(parentWeather);
      if (portName) setActivePortName(portName);
    }
    // Reset the flag after a short delay so future API updates can still come through
    if (userSelectedRef.current) {
      const timer = setTimeout(() => {
        userSelectedRef.current = false;
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [parentWeather, portName]);

  const handlePortClick = (harbour: HarbourTelemetry) => {
    userSelectedRef.current = true;  // ← Block parentWeather from overriding
    setSelectedHarbourId(harbour.id);
    setActiveWeather(harbour.weather);
    setActivePortName(harbour.name);

    if (onPortSelect) {
      onPortSelect(harbour.lat, harbour.lon, harbour.name);
    }
  };

  const isSafe = activeWeather.safety_status === 'SAFE_FOR_VENTURE';
  const isCaution = activeWeather.safety_status === 'EXERCISE_CAUTION';
  const isHazardous = activeWeather.safety_status === 'HAZARDOUS_NO_VENTURE';

  return (
    <div className="space-y-3 font-['Outfit',sans-serif]">
           {/* ⚓ Top Coastal Harbours Directory (3-Column Vertical Scroll Grid) */}
      <div className="p-4 bg-white rounded-3xl border border-slate-200 shadow-xs space-y-3">
        {/* Header Title + Telemetry Badge */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-black text-slate-800 uppercase tracking-wider">
            <Anchor className="w-4 h-4 text-blue-600" />
            <span>Coastal Harbours Directory ({INDIAN_HARBOURS_DATA.length})</span>
          </div>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            ISRO Marine Telemetry
          </span>
        </div>

        {/* Search Bar + State Filter Chips */}
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            placeholder="🔍 Search harbour or state..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full sm:w-1/2 px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
          />
          <div className="flex items-center gap-1.5 overflow-x-auto custom-scrollbar pb-1">
            {uniqueStates.map((state) => (
              <button
                key={state}
                onClick={() => setSelectedState(state)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-bold whitespace-nowrap cursor-pointer transition-all ${
                  selectedState === state
                    ? 'bg-slate-800 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {state}
              </button>
            ))}
          </div>
        </div>

        {/* Multi-Column Vertical Scroll Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 h-[170px] content-start overflow-y-auto custom-scrollbar pr-1">
          {filteredHarbours.map((h) => {
            const isSelected = selectedHarbourId === h.id;
            const portSafe = h.weather.safety_status === 'SAFE_FOR_VENTURE';
            const portCaution = h.weather.safety_status === 'EXERCISE_CAUTION';

            return (
              <button
                key={h.id}
                onClick={() => handlePortClick(h)}
                className={`px-2.5 py-2 rounded-xl text-left text-xs font-bold transition-all cursor-pointer flex items-center justify-between border ${
                  isSelected
                    ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                    : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border-slate-200'
                }`}
              >
                <div className="flex items-center space-x-1.5 truncate">
                  <span
                    className={`w-2 h-2 rounded-full shrink-0 ${
                      isSelected
                        ? 'bg-white'
                        : portSafe
                        ? 'bg-emerald-500'
                        : portCaution
                        ? 'bg-amber-500'
                        : 'bg-red-500 animate-ping'
                    }`}
                  />
                  <span className="truncate">{h.name.replace(/ Fishing Harbour| Harbour| Fisheries Port/g, '')}</span>
                </div>
                <span className={`text-[10px] ml-1 shrink-0 ${isSelected ? 'text-blue-100' : 'text-slate-400'}`}>
                  {h.state.slice(0, 2).toUpperCase()}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Top Main Verdict Card */}
      <div className={`p-5 md:p-5 rounded-3xl border transition-all duration-300 ${
        isSafe 
          ? 'border-emerald-300 bg-emerald-50/70 shadow-sm' 
          : (isCaution 
              ? 'border-amber-300 bg-amber-50/70 shadow-sm' 
              : 'border-red-300 bg-red-50/90 shadow-lg shadow-red-900/10')
      } space-y-3`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/80 pb-4">
          <div className="flex items-center space-x-4">
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${
              isSafe ? 'bg-emerald-600 text-white' : (isCaution ? 'bg-amber-500 text-white' : 'bg-red-600 text-white animate-bounce')
            } shadow-md`}>
              {isSafe ? <ShieldCheck className="w-8 h-8" /> : <AlertTriangle className="w-8 h-8" />}
            </div>
            <div>
              <div className="text-xs text-slate-600 uppercase tracking-widest font-extrabold flex items-center space-x-1.5">
                <span>{t('sea_venture_clearance', currentLang)}</span>
                <span className="text-slate-400">·</span>
                <span className="text-blue-700 font-bold">{activePortName}</span>
              </div>
              <h2 className={`text-xl sm:text-2xl font-black ${
                isSafe ? 'text-emerald-900' : (isCaution ? 'text-amber-900' : 'text-red-900')
              }`}>
                {activeWeather.safety_status.replace(/_/g, ' ')}
              </h2>
            </div>
          </div>

          {/* 0-100 Score Badge */}
          <div className="flex items-center space-x-3 bg-white border border-slate-200 px-5 py-2.5 rounded-2xl shadow-xs shrink-0">
            <div className="text-right">
              <div className="text-[11px] text-slate-500 font-semibold">{t('safety_score', currentLang)}</div>
              <div className={`text-2xl font-black font-mono ${
                isSafe ? 'text-emerald-700' : (isCaution ? 'text-amber-700' : 'text-red-700')
              }`}>
                {activeWeather.safety_index}<span className="text-xs text-slate-400">/100</span>
              </div>
            </div>
            <div className={`w-11 h-11 rounded-full flex items-center justify-center border-2 font-black text-sm ${
              activeWeather.safety_index >= 70 
                ? 'border-emerald-500 text-emerald-700 bg-emerald-50' 
                : (activeWeather.safety_index >= 40 ? 'border-amber-500 text-amber-700 bg-amber-50' : 'border-red-500 text-red-700 bg-red-50 animate-pulse')
            }`}>
              {activeWeather.safety_index >= 70 ? '✓' : '!'}
            </div>
          </div>
        </div>

        {/* Actionable Directive */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200 text-xs text-slate-800 leading-relaxed font-semibold shadow-xs">
          📢 <strong className="text-blue-700">{t('official_advisory', currentLang)}:</strong> {activeWeather.actionable_advice}
        </div>

        {/* 4 Core Meteorological Meters */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          {/* Wave Height */}
          <div className="p-3 rounded-2xl bg-white border border-slate-200 space-y-0.5 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
              <span>{t('wave_height', currentLang)}</span>
              <Waves className="w-4 h-4 text-blue-600" />
            </div>
            <div className="text-lg font-black text-slate-900 font-mono">
              {activeWeather.significant_wave_height_m} <span className="text-xs text-slate-400">m</span>
            </div>
            <div className="text-[11px] text-slate-600">{t('swell_period', currentLang)}: {activeWeather.swell_period_seconds}s</div>
          </div>

          {/* Wind Speed & Beaufort */}
          <div className="p-4 rounded-2xl bg-white border border-slate-200 space-y-1 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
              <span>{t('wind_speed', currentLang)}</span>
              <Wind className="w-4 h-4 text-cyan-600" />
            </div>
            <div className="text-lg font-black text-slate-900 font-mono">
              {activeWeather.wind_speed_knots} <span className="text-xs text-slate-400">kts</span>
            </div>
            <div className="text-[11px] text-slate-600">Beaufort #{activeWeather.beaufort_scale} ({activeWeather.wind_speed_kmph} km/h)</div>
          </div>

          {/* Sea State */}
          <div className="p-4 rounded-2xl bg-white border border-slate-200 space-y-1 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
              <span>{t('sea_state', currentLang)}</span>
              <Compass className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-xs font-bold text-slate-900 truncate">
              {activeWeather.sea_state}
            </div>
            <div className="text-[11px] text-slate-600">{t('direction', currentLang)}: {activeWeather.wind_direction_degrees}°</div>
          </div>

          {/* Lightning Risk */}
          <div className="p-4 rounded-2xl bg-white border border-slate-200 space-y-1 shadow-xs">
            <div className="flex items-center justify-between text-slate-500 text-xs font-semibold">
              <span>{t('lightning_risk', currentLang)}</span>
              <Zap className="w-4 h-4 text-amber-500" />
            </div>
            <div className="text-lg font-black text-slate-900 font-mono">
              {activeWeather.lightning_probability_percent}%
            </div>
            <div className="text-[11px] text-slate-600">{t('visibility', currentLang)}: {activeWeather.visibility_km} km</div>
          </div>
        </div>
      </div>

      {/* Active Cyclone Radar Card */}
      {activeWeather.cyclone_influence && activeWeather.cyclone_influence.active_cyclone ? (
        <div className="p-5 rounded-3xl border border-red-300 bg-red-50/95 space-y-3 shadow-md">
          <div className="flex items-center justify-between">
            <span className="flex items-center space-x-2.5 text-xs font-black text-red-700">
              <span className="w-2.5 h-2.5 rounded-full bg-red-600 animate-ping"></span>
              <span>Severe Cyclone Alert · {activeWeather.cyclone_influence.active_cyclone}</span>
            </span>
            <span className="text-[11px] font-black px-2.5 py-1 rounded-md bg-red-600 text-white shadow-xs">
              {activeWeather.cyclone_influence.intensity}
            </span>
          </div>

          <p className="text-xs text-slate-700 leading-relaxed font-medium">
            Active cyclonic storm located approximately <strong>{activeWeather.cyclone_influence.distance_km} km</strong> from {activePortName}. Sustained gale force gusts reaching open ocean. Strict fishing suspension active in danger perimeter.
          </p>
        </div>
      ) : (
        <div className="p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200/80 text-xs text-emerald-900 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="font-semibold">No active cyclonic storm or severe ocean depression in operational sector for {activePortName}.</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-700 font-bold">{t('cyclone_radar_normal', currentLang)}</span>
        </div>
      )}
    </div>
  );
};
