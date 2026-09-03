# ORCA — Marine Ecosystem Reasoning with Collaborative Agents

An autonomous, multi-agent AI decision-support platform engineered for the **Indian Space Research Organisation (ISRO)** and Department of Space (SIH 2026 Problem Statement 26176). 

ORCA fuses satellite Earth Observation (EO) telemetry (Oceansat-3 OCM-3, INSAT-3DR TIR) with in-situ oceanographic feeds (INCOIS, Open-Meteo Hydrodynamics) to deliver real-time Potential Fishing Zone (PFZ) discovery, ocean hazard risk assessment, maritime boundary geofencing, A* safe route optimization, and voice-enabled multilingual advisory synthesis across 13 Indian regional languages.

---

## Key Capabilities

- **Potential Fishing Zone (PFZ) Discovery:** Generates high-confidence candidate zones by calculating thermal-chlorophyll front coincidence ($\nabla \text{SST} \times \nabla \text{Chl-a}$) and species-specific Habitat Suitability Indexing (HSI) for Yellowfin Tuna, Indian Mackerel, Oil Sardine, and Silver Pomfret.
- **Geofencing & Maritime Safety:** Real-time proximity checking for International Maritime Boundary Lines (IMBL) (India–Sri Lanka, India–Pakistan) and Marine Protected Areas (MPAs) such as Gulf of Mannar and Gahirmatha Sanctuary to prevent accidental border crossings and protect marine biodiversity.
- **Sea-State & Weather Risk Fusion:** Hydrodynamic risk assessment evaluating significant wave height, wind speed (Beaufort scale), swell period, and tropical cyclone danger radii.
- **Weather-Aware A* Route Optimization:** Calculates safe, energy-efficient maritime paths avoiding landmasses, high-wave hazard zones, and restricted boundaries.
- **Multi-Agent Execution DAG & Supervisor Architecture:** Dynamic planner and execution graph orchestrating specialized agents (Marine Data, Weather & Hazard, Ocean Analytics, Geospatial & Routing, Decision Engine).
- **Explainable Evidence & Provenance:** Full traceability graph connecting raw satellite/sensor telemetry to final operational recommendations (`RECOMMENDED`, `ACCEPTABLE`, `CAUTION`, `NO_GO`).
- **Multilingual Vernacular Support:** Native conversational dialogue and voice speech synthesis across 13 Indian languages (English, Hindi, Tamil, Telugu, Malayalam, Bengali, Gujarati, Marathi, Kannada, Konkani, Odia, Tulu, Kutchi).

---

## System Architecture

```text
                               +-----------------------------+
                               |     User Interface (Web/App)|
                               +--------------+--------------+
                                              |
                                              v
                               +--------------+--------------+
                               |     Master Orchestrator     |
                               +--------------+--------------+
                                              |
               +------------------------------+------------------------------+
               |                              |                              |
               v                              v                              v
+--------------+--------------+ +-------------+---------------+ +------------+---------------+
|      Supervisor Planner     | |       Session Memory        | |      Temporal Resolver      |
+--------------+--------------+ +-------------+---------------+ +------------+---------------+
               |                              |                              |
               +------------------------------+------------------------------+
                                              |
                                              v
+--------------------------------------------------------------------------------------------+
|                                    Specialized Agents                                      |
|  +---------------------+  +---------------------+  +-----------------+  +------------------+  |
|  |  Marine Data Agent  |  | Weather Hazard Agent|  | Ocean Analytics |  | Geospatial Agent |  |
|  +---------------------+  +---------------------+  +-----------------+  +------------------+  |
+--------------------------------------------------------------------------------------------+
                                              |
                                              v
+--------------------------------------------------------------------------------------------+
|                                 Decision & Evidence Engine                                 |
|  - Evidence Collector    - Hard Safety Gate Overrides    - Claim Validation Verifier       |
+--------------------------------------------------------------------------------------------+
```

---

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Asyncio, NetCDF4, Xarray, NumPy, SciPy
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Leaflet GIS, Lucide Icons, Framer Motion
- **Mobile Support:** Capacitor JS (Cross-platform Android / iOS PWA)

---

## Project Directory Structure

```text
├── backend/
│   ├── main.py                     # FastAPI application entrypoint & API router
│   ├── config.py                   # Environment configuration & CORS policies
│   ├── agents/                     # Specialized autonomous agent implementations
│   │   ├── orchestrator.py         # Master orchestrator & tool execution DAG
│   │   ├── marine_data_agent.py    # Satellite EO & NetCDF raster reader
│   │   ├── weather_hazard_agent.py # Hydrodynamics & meteorological telemetry
│   │   ├── ocean_analytics_agent.py# PFZ thermal-chlorophyll front coincidence
│   │   └── geospatial_agent.py     # Geofence checking & A* route optimizer
│   ├── data/                       # Spatial dataset adapters & raster catalogs
│   ├── decision/                   # Decision engine, claim verifier & evidence graph
│   ├── geospatial/                 # A* pathfinding, MPA/IMBL geofencing & risk scoring
│   ├── memory/                     # Bounded LRU session state & conversation history
│   ├── planning/                   # Supervisor planner, intent parser & DAG graph
│   ├── temporal/                   # Temporal horizon resolver & ISO-8601 parser
│   └── tools/                      # Tool registry & dynamic function calling wrappers
├── client/                         # React + Vite GIS Command Center frontend
│   ├── src/
│   │   ├── components/             # GIS view, layer controls, decision panels, modals
│   │   ├── utils/                  # Speech synthesis, geofencing, translations
│   │   ├── types/                  # Shared TypeScript interfaces & API schemas
│   │   ├── App.tsx                 # Main application hub & tab routing
│   │   └── main.tsx                # Application mounting script
├── scratch/                        # Automated verification & test suites
└── requirements.txt                # Python backend dependencies
```

---

## API Reference

### Core REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/pfz` | Returns active PFZ hotspots for a reference fishing harbour |
| `GET` | `/api/pfz/candidates` | Discovers spatial PFZ polygons within a bounding box |
| `GET` | `/api/weather` | Returns sea-state, wave height, wind speed, and safety index |
| `GET` | `/api/cyclones` | Returns active cyclonic storms, forecast tracks, and warning cones |
| `GET` | `/api/geofence` | Evaluates proximity to IMBL boundaries and Marine Protected Areas |
| `GET` | `/api/risk/evaluate` | Evaluates multi-factor operational sea risk for coordinates |
| `POST`| `/api/route` | Computes a weather-aware, border-safe A* navigational route |
| `GET` | `/api/satellites` | Returns status of ISRO Earth Observation constellation |
| `GET` | `/api/decision` | Synthesizes evidence-backed operational decisions with safety overrides |
| `GET` | `/api/tts` | Streams native speech audio for vernacular Indian languages |

### WebSocket Endpoint

- `WS /ws/agent-stream`: Real-time streaming of agent execution steps, thought trace, and dynamic tool invocation DAG.

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher & npm

### 1. Backend Setup

```bash
# Navigate to project root
cd sih_2026_26176

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend server will run at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

```bash
# Navigate to client folder
cd client

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

The web application will be accessible at `http://localhost:5173`.

---

## Verification & Testing

To run the complete automated test suite verifying all 10 project phases, execute:

```bash
python scratch/run_all_phases.py
```

Individual test suites can also be run independently:
- `python scratch/validate_science.py`: Scientific calculation validation
- `python scratch/test_security_hardening.py`: Input hardening & prompt injection audit
- `python scratch/benchmark_performance.py`: Latency & concurrency benchmarks
