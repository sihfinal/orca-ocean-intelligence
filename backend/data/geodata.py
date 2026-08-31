"""
Geospatial Reference Datasets for Blue Orbit (ISRO SIH 2026 - Problem 26176)
Contains Indian Maritime Zones, IMBL Borders, Marine Protected Areas, Harbours, Buoys & Cyclone tracks.
"""

from typing import List, Dict, Any

# Major Indian Fishing Harbours & Maritime Ports
INDIAN_PORTS: Dict[str, Dict[str, Any]] = {
    "kochi": {
        "name": "Kochi Fishing Harbour",
        "state": "Kerala",
        "lat": 9.9416,
        "lon": 76.2575,
        "region": "Arabian Sea",
        "vessel_capacity": 850,
        "primary_catch": ["Oil Sardine", "Indian Mackerel", "Yellowfin Tuna"]
    },
        "munambam": {
        "name": "Munambam Fishing Harbour",
        "state": "Kerala",
        "lat": 10.1800,
        "lon": 76.1750,
        "region": "Arabian Sea",
        "vessel_capacity": 600,
        "primary_catch": ["Oil Sardine", "Mackerel", "Shrimp", "Squid"]
    },
    "neendakara": {
        "name": "Neendakara Fishing Harbour",
        "state": "Kerala",
        "lat": 8.9350,
        "lon": 76.5380,
        "region": "Arabian Sea",
        "vessel_capacity": 900,
        "primary_catch": ["Karikkadi Shrimp", "Squid", "Threadfin Bream", "Cuttlefish"]
    },
    "sakthikulangara": {
        "name": "Sakthikulangara Fishing Harbour",
        "state": "Kerala",
        "lat": 8.9220,
        "lon": 76.5500,
        "region": "Arabian Sea",
        "vessel_capacity": 850,
        "primary_catch": ["Shrimp", "Tuna", "Sardine", "Reef Cod"]
    },
    "vizhinjam": {
        "name": "Vizhinjam Fishing Harbour",
        "state": "Kerala",
        "lat": 8.3760,
        "lon": 76.9890,
        "region": "Arabian Sea / Indian Ocean",
        "vessel_capacity": 650,
        "primary_catch": ["Yellowfin Tuna", "Skipjack Tuna", "Marlin", "Ribbon Fish"]
    },
    "koyilandy": {
        "name": "Koyilandy Fishing Harbour",
        "state": "Kerala",
        "lat": 11.4360,
        "lon": 75.6940,
        "region": "Arabian Sea",
        "vessel_capacity": 500,
        "primary_catch": ["Mackerel", "Sardine", "Anchovy", "Sole Fish"]
    },
    "malpe": {
        "name": "Malpe Fishing Harbour",
        "state": "Karnataka",
        "lat": 13.3496,
        "lon": 74.7031,
        "region": "Arabian Sea",
        "vessel_capacity": 1000,
        "primary_catch": ["Indian Mackerel", "Sardines", "Squid", "Kingfish"]
    },
    "karwar": {
        "name": "Karwar (Baithkol) Harbour",
        "state": "Karnataka",
        "lat": 14.8080,
        "lon": 74.1250,
        "region": "Arabian Sea",
        "vessel_capacity": 650,
        "primary_catch": ["Mackerel", "Pomfret", "Sardine", "Crab"]
    },
    "mallet_bunder": {
        "name": "New Ferry Wharf (Mallet Bunder)",
        "state": "Maharashtra",
        "lat": 18.9550,
        "lon": 72.8480,
        "region": "Arabian Sea",
        "vessel_capacity": 1400,
        "primary_catch": ["Silver Pomfret", "Bombay Duck", "Prawns", "Ghol Fish"]
    },
    "ratnagiri": {
        "name": "Ratnagiri (Mirkarwada) Harbour",
        "state": "Maharashtra",
        "lat": 16.9950,
        "lon": 73.2820,
        "region": "Arabian Sea",
        "vessel_capacity": 750,
        "primary_catch": ["Kingfish", "Pomfret", "Mackerel", "Squid"]
    },
    "malim": {
        "name": "Malim Fishing Jetty",
        "state": "Goa",
        "lat": 15.5030,
        "lon": 73.8320,
        "region": "Arabian Sea",
        "vessel_capacity": 450,
        "primary_catch": ["Kingfish", "Mackerel", "Reef Cod", "Squid"]
    },
    "mangrol": {
        "name": "Mangrol Fishing Harbour",
        "state": "Gujarat",
        "lat": 21.1200,
        "lon": 70.1150,
        "region": "North Arabian Sea",
        "vessel_capacity": 800,
        "primary_catch": ["Ribbon Fish", "Croaker", "Cuttlefish", "Pomfret"]
    },
    "nagapattinam": {
        "name": "Nagapattinam Fishing Harbour",
        "state": "Tamil Nadu",
        "lat": 10.7650,
        "lon": 79.8450,
        "region": "Bay of Bengal",
        "vessel_capacity": 700,
        "primary_catch": ["Silver Belly", "Sardine", "Crab", "Seer Fish"]
    },
    "chinnamuttom": {
        "name": "Chinnamuttom Fishing Harbour",
        "state": "Tamil Nadu",
        "lat": 8.0930,
        "lon": 77.5620,
        "region": "Gulf of Mannar",
        "vessel_capacity": 500,
        "primary_catch": ["Tuna", "Grouper", "Snapper", "Prawns"]
    },
    "kakinada": {
        "name": "Kakinada Fishing Harbour",
        "state": "Andhra Pradesh",
        "lat": 16.9600,
        "lon": 82.2500,
        "region": "Bay of Bengal",
        "vessel_capacity": 850,
        "primary_catch": ["Tiger Prawns", "Hilsa", "Ribbon Fish", "Pomfret"]
    },
    "dhamara": {
        "name": "Dhamara Fishing Harbour",
        "state": "Odisha",
        "lat": 20.7950,
        "lon": 86.9550,
        "region": "Bay of Bengal",
        "vessel_capacity": 600,
        "primary_catch": ["Hilsa", "Sea Bass (Bhetki)", "Pomfret", "Croaker"]
    },
    "petuaghat": {
        "name": "Petuaghat (Deshapran) Harbour",
        "state": "West Bengal",
        "lat": 21.7890,
        "lon": 87.8920,
        "region": "Bay of Bengal",
        "vessel_capacity": 750,
        "primary_catch": ["Hilsa (Tenualosa ilisha)", "Pompano", "Ribbon Fish", "Catfish"]
    },
    "chennai": {
        "name": "Chennai Kasimedu Harbour",
        "state": "Tamil Nadu",
        "lat": 13.1256,
        "lon": 80.2974,
        "region": "Bay of Bengal",
        "vessel_capacity": 1200,
        "primary_catch": ["Silver Pomfret", "King Mackerel", "Shrimp"]
    },
    "visakhapatnam": {
        "name": "Visakhapatnam Fishing Harbour",
        "state": "Andhra Pradesh",
        "lat": 17.6974,
        "lon": 83.2986,
        "region": "Bay of Bengal",
        "vessel_capacity": 950,
        "primary_catch": ["Ribbon Fish", "Tuna", "Croaker"]
    },
    "mumbai": {
        "name": "Sassoon Docks & Versova",
        "state": "Maharashtra",
        "lat": 18.9172,
        "lon": 72.8228,
        "region": "Arabian Sea",
        "vessel_capacity": 1500,
        "primary_catch": ["Bombay Duck", "Pomfret", "Prawns"]
    },
    "porbandar": {
        "name": "Porbandar Fisheries Port",
        "state": "Gujarat",
        "lat": 21.6417,
        "lon": 69.6293,
        "region": "North Arabian Sea",
        "vessel_capacity": 1100,
        "primary_catch": ["Cuttlefish", "Croaker", "Ribbon Fish"]
    },
    "rameswaram": {
        "name": "Rameswaram / Mandapam Jetty",
        "state": "Tamil Nadu",
        "lat": 9.2876,
        "lon": 79.3129,
        "region": "Palk Strait & Gulf of Mannar",
        "vessel_capacity": 600,
        "primary_catch": ["Crab", "Squid", "Ray Fish"]
    },
    "mangalore": {
        "name": "Mangalore Old Port",
        "state": "Karnataka",
        "lat": 12.8596,
        "lon": 74.8396,
        "region": "Arabian Sea",
        "vessel_capacity": 700,
        "primary_catch": ["Sardines", "Mackerel", "Tuna"]
    },
    "paradip": {
        "name": "Paradip Fishing Harbour",
        "state": "Odisha",
        "lat": 20.2644,
        "lon": 86.6698,
        "region": "Bay of Bengal",
        "vessel_capacity": 800,
        "primary_catch": ["Hilsa", "Sea Bass", "Pomfret"]
    },
    "kanyakumari": {
        "name": "Kanyakumari Harbour",
        "state": "Tamil Nadu",
        "lat": 8.0883,
        "lon": 77.5385,
        "region": "Indian Ocean Convergence",
        "vessel_capacity": 550,
        "primary_catch": ["Skipjack Tuna", "Reef Perch", "Shark"]
    },
    "port_blair": {
        "name": "Port Blair Junglighat Harbour",
        "state": "Andaman & Nicobar",
        "lat": 11.6643,
        "lon": 92.7305,
        "region": "Andaman Sea",
        "vessel_capacity": 400,
        "primary_catch": ["Yellowfin Tuna", "Barracuda", "Red Snapper"]
    }
}

# International Maritime Boundary Lines (IMBL)
IMBL_BOUNDARIES: Dict[str, Dict[str, Any]] = {
    "india_srilanka": {
        "name": "India-Sri Lanka IMBL (Palk Strait & Gulf of Mannar)",
        "risk_level": "CRITICAL_GEOFENCE",
        "buffer_warning_nm": 3.0,
        "description": "Restricted maritime boundary agreed under 1974 & 1976 bilateral agreements. Crossing leads to vessel seizure.",
        "coordinates": [
            [10.0833, 79.8667],
            [9.9500, 79.6167],
            [9.7000, 79.4333],
            [9.3500, 79.3667],
            [9.1000, 79.2500],
            [8.8833, 79.0333],
            [8.4000, 78.8333],
            [7.8333, 78.6000]
        ]
    },
    "india_pakistan": {
        "name": "India-Pakistan IMBL (Sir Creek & Arabian Sea)",
        "risk_level": "CRITICAL_GEOFENCE",
        "buffer_warning_nm": 5.0,
        "description": "High sensitivity maritime boundary off Kutch Gujarat. Zero-tolerance geofence zone.",
        "coordinates": [
            [23.5833, 68.1000],
            [23.4500, 67.8000],
            [23.2000, 67.4000],
            [22.8000, 66.8000],
            [22.3000, 66.2000],
            [21.5000, 65.5000]
        ]
    },
    "india_bangladesh": {
        "name": "India-Bangladesh IMBL (Bay of Bengal Delimitation)",
        "risk_level": "WARNING_GEOFENCE",
        "buffer_warning_nm": 4.0,
        "description": "UNCLOS ITLOS delimited boundary 2014 across Sundarbans delta to deep Bay of Bengal.",
        "coordinates": [
            [21.6333, 89.1500],
            [21.1000, 89.2500],
            [20.5000, 89.4500],
            [19.5000, 89.7000],
            [18.0000, 90.1000]
        ]
    }
}

# Marine Protected Areas & Ecologically Sensitive Zones (MPAs)
MARINE_PROTECTED_AREAS: List[Dict[str, Any]] = [
    {
        "id": "MPA-01",
        "name": "Gulf of Mannar Marine Biosphere Reserve",
        "state": "Tamil Nadu",
        "type": "Coral Reef & Dugong Habitat",
        "status": "STRICT_NO_TRAWLING",
        "center": [9.05, 79.15],
        "radius_km": 25.0,
        "restriction": "Commercial bottom-trawling and motorized purse seining strictly prohibited under Wildlife Protection Act."
    },
    {
        "id": "MPA-02",
        "name": "Gahirmatha Marine Wildlife Sanctuary",
        "state": "Odisha",
        "type": "Olive Ridley Sea Turtle Mass Nesting Ground",
        "status": "SEASONAL_CLOSURE",
        "center": [20.72, 87.05],
        "radius_km": 20.0,
        "restriction": "Complete fishing ban from November 1 to May 31 within 20 km of coast."
    },
    {
        "id": "MPA-03",
        "name": "Sundarbans National Park Coastal Buffer",
        "state": "West Bengal",
        "type": "Mangrove Delta & Estuarine Crocodile Biosphere",
        "status": "REGULATED_ZONE",
        "center": [21.80, 88.90],
        "radius_km": 30.0,
        "restriction": "Motorized vessel speed capped at 8 knots. Deep water dredging banned."
    },
    {
        "id": "MPA-04",
        "name": "Malvan Marine Sanctuary",
        "state": "Maharashtra",
        "type": "Submerged Coral & Pearl Oyster Beds",
        "status": "ECO_SENSITIVE",
        "center": [16.05, 73.45],
        "radius_km": 12.0,
        "restriction": "Spearfishing, dynamite fishing, and anchoring on coral reefs punishable."
    },
    {
        "id": "MPA-05",
        "name": "Mahatma Gandhi Marine National Park (Wandoor)",
        "state": "Andaman & Nicobar",
        "type": "Pristine Coral Reef Atolls",
        "status": "STRICT_SANCTUARY",
        "center": [11.55, 92.58],
        "radius_km": 18.0,
        "restriction": "No commercial extraction allowed. Scientific observation only."
    }
]

# INCOIS / ISRO Ocean Observation Buoy Stations
OCEAN_BUOYS: List[Dict[str, Any]] = [
    {"id": "AD01", "name": "INCOIS Arabian Sea Deep Buoy 1", "lat": 15.00, "lon": 69.00, "sst": 28.6, "wave_height_m": 1.4, "salinity_psu": 35.8, "status": "ACTIVE"},
    {"id": "AD02", "name": "INCOIS Lakshadweep Sea Buoy 2", "lat": 10.50, "lon": 72.50, "sst": 29.2, "wave_height_m": 1.1, "salinity_psu": 35.2, "status": "ACTIVE"},
    {"id": "BD08", "name": "INCOIS Bay of Bengal Buoy 8", "lat": 18.15, "lon": 89.65, "sst": 29.8, "wave_height_m": 2.3, "salinity_psu": 32.4, "status": "ACTIVE"},
    {"id": "BD09", "name": "INCOIS Chennai Offshore Buoy 9", "lat": 13.04, "lon": 80.33, "sst": 29.1, "wave_height_m": 1.6, "salinity_psu": 33.1, "status": "ACTIVE"},
    {"id": "BD11", "name": "INCOIS Andaman Sea Buoy 11", "lat": 11.20, "lon": 93.10, "sst": 29.5, "wave_height_m": 1.8, "salinity_psu": 32.8, "status": "ACTIVE"},
]

# Active Simulated Severe Weather / Cyclone Track (IMD Simulation)
ACTIVE_CYCLONE: Dict[str, Any] = {
    "name": "Cyclone ASNA-II",
    "category": "Very Severe Cyclonic Storm (VSCS)",
    "basin": "Bay of Bengal",
    "current_lat": 15.8,
    "current_lon": 84.6,
    "central_pressure_hpa": 982,
    "max_sustained_wind_knots": 65,
    "gusts_knots": 80,
    "movement_direction": "North-Northwest (NNW)",
    "speed_kmph": 16,
    "eye_radius_km": 28,
    "danger_radius_km": 180,
    "forecast_track": [
        {"hour": 0, "lat": 15.8, "lon": 84.6, "intensity": "VSCS", "wind_kts": 65},
        {"hour": 12, "lat": 16.9, "lon": 84.2, "intensity": "VSCS", "wind_kts": 70},
        {"hour": 24, "lat": 18.1, "lon": 83.9, "intensity": "SCS", "wind_kts": 60},
        {"hour": 36, "lat": 19.3, "lon": 84.1, "intensity": "CS (Landfall Near Gopalpur)", "wind_kts": 45},
        {"hour": 48, "lat": 20.2, "lon": 84.8, "intensity": "Deep Depression", "wind_kts": 30}
    ]
}
