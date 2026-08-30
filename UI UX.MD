# Blue Orbit Design System & UI/UX Specification
**ISRO SIH 2026 — Problem Statement 26176**  
**Platform**: Blue Orbit — Marine Ecosystem Reasoning with Collaborative Agents

---

## 1. Design Aesthetics & Visual Identity

### 🌊 Color Palette (Deep Abyss & Bioluminescence)
- **Deep Ocean Slate Canvas**: `#030712` (Base background) with atmospheric radial gradients `#050E1F` and `#081A36`.
- **Electric Oceanic Cyan**: `#00F0FF` (Active AI agents, satellite telemetry, ocean currents, primary focus).
- **Phytoplankton Emerald Green**: `#10B981` (High chlorophyll concentration, high fish catch probability, safe sea condition).
- **Hazard Warning Amber**: `#F59E0B` (Rough sea warnings, squall advisories, buffer zone warnings).
- **Emergency Crimson / Alert**: `#EF4444` (Severe cyclones, storm surges, IMBL international border breach).
- **ISRO / National Saffron**: `#FF9933` (ISRO insignia, official Department of Space verification badge).
- **Glassmorphism Panels**: `rgba(11, 23, 48, 0.7)` with `backdrop-filter: blur(16px)` and subtle border `1px solid rgba(0, 240, 255, 0.15)`.

---

## 2. Core Layout Architecture

### A. Top Command Navigation Bar (`Header.tsx`)
- **Left**: ISRO logo insignia + Blue Orbit brand title with live blinking satellite connection pulse (`Oceansat-3 Live Feed`).
- **Center**: Quick-switch module tabs:
  - 🗺️ **GIS Ocean Command** (Full geospatial multi-layer map)
  - 🤖 **Agent Reasoning Lab** (Visual DAG execution inspector)
  - ⚠️ **Disaster & Safety Barometer** (Cyclones, waves, lightning alerts)
  - 📄 **Official Advisory Bulletin** (Downloadable INCOIS-ISRO format)
- **Right**:
  - Multi-Lingual Switcher with 13 Indian languages including English, Hindi, Tamil, Telugu, Malayalam, Bengali, Gujarati, Marathi, and 5 additional regional languages.
  - Quick SOS Emergency Distress Button.

### B. Interactive GIS Map Viewport (`MapViewport.tsx`)
- High-contrast dark ocean base map with toggleable scientific layers:
  1. **SST Thermal Gradients** (Sea Surface Temperature isotherms & contours).
  2. **Chlorophyll-a Biomass Heatmap** (Phytoplankton blooms indicating high pelagic fish density).
  3. **PFZ Hotspots** (Interactive pulsing markers with species breakdown: Tuna, Mackerel, Sardine, Pomfret).
  4. **Dynamic Wind & Wave Vectors** (Animated streamlines showing sea-state direction and swell height).
  5. **Geofencing & Boundary Compliance** (12nm territorial waters, 200nm Indian EEZ, and high-visibility India-Sri Lanka / India-Pakistan IMBL borders).
  6. **Marine Protected Areas (MPAs)** (Gulf of Mannar, Sundarbans with no-fishing restriction buffer).
  7. **Vessel Navigation & Safe Route Path** (Weather-optimized A* routing avoiding hazards and borders).

### C. Agentic AI Conversational & Reasoning Drawer (`AgentChatDrawer.tsx`)
- **Multi-Modal Input**: Text query bar + Voice microphone input (Web Speech API STT) + Audio speaker read-out (TTS).
- **Live Multi-Agent Reasoning DAG Visualizer**:
  - Animated step-by-step progress cards showing:
    - 🧭 *Planner Agent* -> Decomposing query intent
    - 🛰️ *Marine Data Agent* -> Querying MOSDAC/Oceansat-3 SST & Chlorophyll products
    - 🌪️ *Weather Agent* -> Checking IMD cyclone track & wave swell
    - 🐟 *PFZ Analytics Agent* -> Correlating thermal fronts with chlorophyll edges
    - 🛡️ *Geofence Agent* -> Checking IMBL border proximity & computing safe route
    - 📝 *Explainability Agent* -> Generating evidence-based multi-lingual advisory
- **Quick-Query Chips**: Fast single-click prompts for fishermen and coastal authorities.

### D. Fishermen Safety Barometer & Advisory Exporter
- Real-time 0-100 Sea Safety Score with wind, wave, and lightning risk gauges.
- 1-Click Printable / PDF Marine Advisory report generator with QR verification code and ISRO/INCOIS headers.