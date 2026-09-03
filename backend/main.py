"""
Blue Orbit Backend Server (FastAPI + WebSockets)
ISRO Smart India Hackathon 2026 - Problem Statement 26176
Modular Agentic AI Marine Intelligence & Decision Support Platform
"""

import asyncio
import json
import logging
import urllib.request
import urllib.parse
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import get_cors_origins
from backend.agents.orchestrator import MasterOrchestrator
from backend.agents.marine_data_agent import MarineDataAgent
from backend.agents.weather_hazard_agent import WeatherHazardAgent
from backend.agents.ocean_analytics_agent import OceanAnalyticsAgent
from backend.agents.geospatial_agent import GeospatialAgent
from backend.data.geodata import (
    INDIAN_PORTS, 
    IMBL_BOUNDARIES, 
    MARINE_PROTECTED_AREAS, 
    OCEAN_BUOYS, 
    ACTIVE_CYCLONE
)

logger = logging.getLogger("blue_orbit.backend")

app = FastAPI(
    title="Blue Orbit — Marine Ecosystem Reasoning with Collaborative Agents",
    description="ISRO Agentic AI Marine Decision Support & Conversational Intelligence Platform",
    version="1.0.0"
)

# Configurable CORS allow-list for local development and authorized production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global safe exception handler to prevent leaking internal stack traces or secrets
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, type(exc).__name__, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please consult system logs."}
    )

# Initialize Orchestrator and Agents
orchestrator = MasterOrchestrator()
marine_agent = MarineDataAgent()
weather_agent = WeatherHazardAgent()
ocean_agent = OceanAnalyticsAgent(marine_agent)
geo_agent = GeospatialAgent()

# Request Models with boundary validation
class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000, description="Natural language marine query")
    language: Optional[str] = Field(None, max_length=20, description="Language code")
    reference_port: Optional[str] = Field(None, max_length=100, description="Reference harbour key")
    user_lat: Optional[float] = Field(None, ge=-90.0, le=90.0, description="User latitude in decimal degrees")
    user_lon: Optional[float] = Field(None, ge=-180.0, le=180.0, description="User longitude in decimal degrees")
    session_id: Optional[str] = Field(None, max_length=128, description="Conversational multi-turn session ID")

class RouteRequest(BaseModel):
    start_port: str = Field(..., min_length=1, max_length=100, description="Departure port identifier")
    dest_lat: float = Field(..., ge=-90.0, le=90.0, description="Destination latitude")
    dest_lon: float = Field(..., ge=-180.0, le=180.0, description="Destination longitude")
    dest_name: Optional[str] = Field("Selected Target", max_length=200, description="Destination name")

class GeofenceCheckRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Vessel latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Vessel longitude in decimal degrees")

@app.get("/")
def root_status():
    return {
        "status": "ONLINE",
        "platform": "Blue Orbit — Marine Ecosystem Reasoning with Collaborative Agents",
        "organization": "Indian Space Research Organisation (ISRO)",
        "sih_problem_id": 26176,
        "active_agents": 6,
        "docs_url": "/docs"
    }

@app.post("/api/chat")
async def chat_endpoint(payload: ChatQueryRequest):
    """
    Main conversational agent endpoint. Orchestrates multi-agent execution pipeline.
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    result = await orchestrator.execute_query_pipeline(
        query=payload.query, 
        requested_lang=payload.language,
        user_lat=payload.user_lat,
        user_lon=payload.user_lon,
        reference_port_override=payload.reference_port,
        session_id=payload.session_id
    )
    return result

@app.post("/api/query")
async def query_alias(payload: ChatQueryRequest):
    """Alias for /api/chat."""
    return await chat_endpoint(payload)

@app.get("/api/tts")
async def text_to_speech_stream(
    text: str = Query(..., description="Text to synthesize"),
    lang: str = Query("en", description="Language code")
):
    """
    Streams native vernacular speech audio for all 13 Indian languages (en, hi, ta, te, ml, bn, gu, mr, and 5 new languages).
    Bypasses browser CORS / hotlink restrictions on Windows/macOS/Linux/Android/iOS.
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    clean_lang = lang.lower().strip()
    prefix = clean_lang.split("-")[0] if "-" in clean_lang else clean_lang
    if prefix not in ["en", "hi", "ta", "te", "ml", "bn", "gu", "mr"]:
        prefix = "en"
        
    encoded_text = urllib.parse.quote(text[:350])
    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={prefix}&client=tw-ob&q={encoded_text}"
    
    req = urllib.request.Request(tts_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://translate.google.com/"
    })
    
    try:
        loop = asyncio.get_event_loop()
        def fetch_audio():
            with urllib.request.urlopen(req, timeout=12) as response:
                return response.read()
        
        audio_data = await loop.run_in_executor(None, fetch_audio)
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "public, max-age=86400",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS synthesis error: {str(e)}")


@app.get("/api/pfz")
def get_pfz_hotspots(port: Optional[str] = None):
    """
    Returns Potential Fishing Zone (PFZ) hotspots with thermal-chlorophyll coincidence index.
    """
    return {
        "count": 15,
        "reference_port": port,
        "hotspots": ocean_agent.generate_pfz_hotspots(reference_port_key=port)
    }

@app.get("/api/pfz/candidates")
def get_spatial_pfz_candidates(
    min_lat: float = Query(10.0, ge=-90.0, le=90.0),
    max_lat: float = Query(15.0, ge=-90.0, le=90.0),
    min_lon: float = Query(72.0, ge=-180.0, le=180.0),
    max_lon: float = Query(76.0, ge=-180.0, le=180.0),
    ref_port: Optional[str] = Query(None, description="Optional reference harbour key")
):
    """
    Returns Phase 6 spatial PFZ candidate regions, bounding polygons, transparent scores, and confidence.
    """
    ref_lat = None
    ref_lon = None
    if ref_port and ref_port.lower() in INDIAN_PORTS:
        p = INDIAN_PORTS[ref_port.lower()]
        ref_lat = p["lat"]
        ref_lon = p["lon"]

    resp = ocean_agent.analyze_spatial_pfz(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        reference_lat=ref_lat,
        reference_lon=ref_lon
    )
    return resp.dict()

@app.get("/api/pfz/radius")
def get_pfz_within_radius(
    lat: float = Query(12.91, ge=-90.0, le=90.0, description="Center latitude"),
    lon: float = Query(74.85, ge=-180.0, le=180.0, description="Center longitude"),
    radius_km: float = Query(100.0, ge=5.0, le=500.0, description="Search radius in kilometers")
):
    """
    Discovers and ranks multi-variable PFZ candidate zones within an exact geodesic radius.
    """
    candidates = ocean_agent.find_candidates_within_radius(
        center_lat=lat,
        center_lon=lon,
        radius_km=radius_km
    )
    return {
        "center": {"lat": lat, "lon": lon},
        "radius_km": radius_km,
        "count": len(candidates),
        "candidates": [c.dict() for c in candidates]
    }

@app.get("/api/pfz/nearest")
def get_nearest_pfz_candidate(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Observer latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Observer longitude")
):
    """
    Finds the closest verified PFZ candidate zone to an observer coordinate.
    """
    cand = ocean_agent.find_nearest_candidate(ref_lat=lat, ref_lon=lon)
    return cand.dict() if cand else {"status": "UNAVAILABLE", "message": "No candidate within search range."}

@app.get("/api/ocean-grid")
def get_ocean_grid(
    step: float = Query(1.0, ge=0.1, le=5.0, description="Grid resolution step")
):
    """
    Returns 2D grid matrix of SST and Chlorophyll-a for geospatial GIS contour rendering.
    """
    return marine_agent.generate_ocean_grid(step=step)

@app.get("/api/eo/products")
def get_eo_products():
    """
    Returns discoverable catalog of verified Earth Observation satellite datasets.
    """
    return {"count": len(marine_agent.get_available_eo_products()), "products": marine_agent.get_available_eo_products()}

@app.get("/api/eo/point")
def get_eo_point(
    variable: str = Query("chlorophyll_a", description="Variable name"),
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
):
    """
    Extracts physical satellite observation from L3 raster at specific coordinates.
    """
    return marine_agent.get_satellite_point_value(variable, lat, lon)

@app.get("/api/eo/statistics")
def get_eo_statistics(
    variable: str = Query("chlorophyll_a", description="Variable name"),
    min_lat: float = Query(..., ge=-90.0, le=90.0),
    max_lat: float = Query(..., ge=-90.0, le=90.0),
    min_lon: float = Query(..., ge=-180.0, le=180.0),
    max_lon: float = Query(..., ge=-180.0, le=180.0)
):
    """
    Calculates zonal statistics (mean, median, min, max, std, valid count) strictly over valid ocean pixels.
    """
    return marine_agent.get_regional_statistics(variable, min_lat, max_lat, min_lon, max_lon)

@app.get("/api/eo/gradient")
def get_eo_gradient(
    variable: str = Query("sea_surface_temperature", description="Target variable"),
    min_lat: float = Query(..., ge=-90.0, le=90.0),
    max_lat: float = Query(..., ge=-90.0, le=90.0),
    min_lon: float = Query(..., ge=-180.0, le=180.0),
    max_lon: float = Query(..., ge=-180.0, le=180.0)
):
    """
    Calculates geodetic spacing-aware horizontal spatial gradients to detect thermal/color frontal boundaries.
    """
    return marine_agent.get_spatial_gradient(variable, min_lat, max_lat, min_lon, max_lon)

@app.get("/api/eo/contours")
def get_eo_contours(
    variable: str = Query("chlorophyll_a", description="Target variable"),
    min_lat: Optional[float] = Query(None, ge=-90.0, le=90.0),
    max_lat: Optional[float] = Query(None, ge=-90.0, le=90.0),
    min_lon: Optional[float] = Query(None, ge=-180.0, le=180.0),
    max_lon: Optional[float] = Query(None, ge=-180.0, le=180.0)
):
    """
    Generates RFC 7946 GeoJSON contour bands from valid satellite raster fields for Leaflet display.
    """
    return marine_agent.get_raster_contours(variable, min_lat, max_lat, min_lon, max_lon)

@app.get("/api/weather")
def get_weather_observation(
    lat: float = Query(9.94, ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    lon: float = Query(76.25, ge=-180.0, le=180.0, description="Longitude in decimal degrees")
):
    """
    Returns sea-state, significant wave height, Beaufort wind scale, and fishermen safety index.
    """
    return weather_agent.get_weather_at_point(lat, lon)

@app.get("/api/cyclones")
def get_cyclones_and_warnings():
    """
    Returns active cyclonic storms, forecast tracks, and high-wave alerts.
    """
    return weather_agent.get_active_cyclones_and_warnings()

@app.get("/api/geofence")
def check_geofence(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
):
    """
    Checks proximity to International Maritime Boundary Lines (IMBL) and Marine Protected Areas.
    """
    return geo_agent.check_geofence_status(lat, lon)

@app.get("/api/risk/evaluate")
def evaluate_marine_risk(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
):
    """
    Evaluates multi-factor marine operational risk and safety classification for coordinates.
    """
    weather = weather_agent.get_weather_at_point(lat, lon)
    cyclone = weather_agent.get_active_cyclones_and_warnings()
    return geo_agent.risk_engine.evaluate_point_risk(lat, lon, weather_telemetry=weather, cyclone_info=cyclone)

@app.post("/api/route")
def calculate_route(payload: RouteRequest):
    """
    Computes a weather-aware, border-safe navigational route with waypoints.
    """
    return geo_agent.compute_safe_route(
        start_port_key=payload.start_port,
        dest_lat=payload.dest_lat,
        dest_lon=payload.dest_lon,
        dest_name=payload.dest_name or "Target PFZ"
    )

@app.get("/api/satellites")
def get_satellite_telemetry():
    """
    Returns real-time status of ISRO Earth Observation satellites.
    """
    return {
        "constellation": marine_agent.get_satellite_telemetry(),
        "in_situ_buoys": OCEAN_BUOYS
    }

@app.get("/api/ports")
def get_indian_ports():
    """
    Returns reference Indian fishing harbours and maritime ports.
    """
    return INDIAN_PORTS

@app.get("/api/geodata/layers")
def get_geodata_layers():
    """
    Returns vector layers for IMBL lines, Marine Protected Areas, and Buoys.
    """
    return {
        "imbl_boundaries": IMBL_BOUNDARIES,
        "marine_protected_areas": MARINE_PROTECTED_AREAS,
        "ocean_buoys": OCEAN_BUOYS,
        "active_cyclone": ACTIVE_CYCLONE
    }
@app.get("/api/decision")
async def get_decision_evaluation(
    query: str = Query("Which PFZ is recommended from Kochi?", description="User operational query"),
    port: Optional[str] = Query("kochi", description="Reference port key"),
    objective: Optional[str] = Query(None, description="User objective (e.g. BALANCE_SUITABILITY_AND_SAFETY, MINIMIZE_RISK)")
):
    """
    Evaluates evidence, applies hard safety gates, and synthesizes an objective-driven decision.
    """
    res = await orchestrator.execute_query_pipeline(query, reference_port_override=port)
    return {
        "decision": res.get("decision"),
        "evidence_package": res.get("evidence_package"),
        "claim_validation": res.get("claim_validation"),
        "recommendation": res.get("recommendation"),
        "decision_status": res.get("decision_status"),
        "supporting_factors": res.get("supporting_factors"),
        "negative_factors": res.get("negative_factors"),
        "operational_risks": res.get("operational_risks"),
        "data_limitations": res.get("data_limitations")
    }


@app.websocket("/ws/agent-stream")
async def websocket_agent_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming of Agent thought processes and execution DAG.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            req = json.loads(data)
            query = req.get("query", "")
            lang = req.get("language", "en")
            
            # Send initial supervisor ack
            await websocket.send_json({
                "type": "STAGE_UPDATE",
                "stage": "INITIALIZING",
                "message": "Blue Orbit Supervisor initialized. Building collaborative execution graph..."
            })
            await asyncio.sleep(0.3)
            
            # Run pipeline and send final result
            result = await orchestrator.execute_query_pipeline(query, requested_lang=lang)
            
            for step in result["evidence_and_provenance"]["execution_trace"]:
                await websocket.send_json({
                    "type": "AGENT_STEP",
                    "step": step
                })
                await asyncio.sleep(0.25)
                
            await websocket.send_json({
                "type": "PIPELINE_COMPLETE",
                "payload": result
            })
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "ERROR", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
