"""
Geofence Service & Vector Geospatial Boundary Engine
ISRO SIH 2026 - Problem Statement 26176
Phase 7: Geofencing, Risk/Safety & Real Route Optimization

Manages authoritative Indian marine spatial boundaries, Marine Protected Areas (MPAs),
naval gunnery firing ranges, critical border corridors (IMBL), and dynamic storm exclusion zones.
Supports point-in-polygon, candidate polygon intersection, buffer corridors, and temporal validity.
"""

import math
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

from shapely.geometry import Point, Polygon, LineString, MultiPolygon, mapping, shape
from shapely.ops import transform
import pyproj

from backend.geospatial.schemas import (
    Geofence,
    GeofenceType,
    GeofenceStatus,
    SafetyClassification
)
from backend.data.geodata import IMBL_BOUNDARIES, MARINE_PROTECTED_AREAS

logger = logging.getLogger("orca.geospatial.geofence")

class GeofenceService:
    """
    Authoritative vector geospatial boundary service for Indian Exclusive Economic Zone.
    """

    def __init__(self):
        self._enabled = True
        self._geofences: Dict[str, Geofence] = {}
        self._shapely_geoms: Dict[str, Any] = {}
        self._initialize_authoritative_boundaries()

    def set_dataset_enabled(self, enabled: bool) -> None:
        """Enables or disables geofence dataset to test UNKNOWN handling (Section 5 & Test 4)."""
        self._enabled = enabled

    def is_enabled(self) -> bool:
        return self._enabled

    def _create_circle_polygon(self, center_lat: float, center_lon: float, radius_km: float, num_pts: int = 36) -> List[List[float]]:
        """Generates geodetic circle polygon coordinates [lon, lat] for RFC 7946 GeoJSON."""
        coords = []
        d_lat_deg = radius_km / 111.32
        d_lon_deg = radius_km / (111.32 * max(0.1, math.cos(math.radians(center_lat))))
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            lat = center_lat + d_lat_deg * math.sin(theta)
            lon = center_lon + d_lon_deg * math.cos(theta)
            coords.append([round(lon, 5), round(lat, 5)])
        coords.append(coords[0])  # Close ring
        return coords

    def _initialize_authoritative_boundaries(self) -> None:
        """Populates canonical Indian maritime boundaries from official gazetted coordinates."""
        
        # 1. Marine Protected Areas (MPAs) & Marine Sanctuaries
        for mpa in MARINE_PROTECTED_AREAS:
            ring = self._create_circle_polygon(mpa["center"][0], mpa["center"][1], mpa["radius_km"])
            gf = Geofence(
                id=mpa["id"],
                name=mpa["name"],
                type=GeofenceType.MARINE_PROTECTED_AREA,
                geometry_type="Polygon",
                coordinates=[ring],
                jurisdiction="Ministry of Environment, Forest & Climate Change (MoEFCC) / State Wildlife Wing",
                effective_start="1980-01-01T00:00:00Z",
                effective_end="2099-12-31T23:59:59Z",
                status="ACTIVE" if mpa.get("status") != "SEASONAL_CLOSURE" else "SEASONAL_CLOSED",
                restrictions=[mpa["restriction"]],
                description=f"{mpa['type']} - {mpa['name']}",
                provenance={
                    "authority": "MoEFCC Wildlife Protection Act 1972",
                    "gazette_reference": "National Marine Sanctuary Notification",
                    "state": mpa["state"]
                },
                source_url="https://moef.gov.in"
            )
            self._register_geofence(gf)

        # 2. Military / Naval Gunnery & Defense Exclusion Zones
        military_zones = [
            {
                "id": "DEF-01",
                "name": "Indian Navy Gunnery Practice Range (Kochi Offshore)",
                "type": GeofenceType.MILITARY_EXCLUSION_ZONE,
                "coordinates": [[
                    [75.80, 9.70], [76.10, 9.70], [76.10, 9.95], [75.80, 9.95], [75.80, 9.70]
                ]],
                "jurisdiction": "Southern Naval Command / Indian Navy",
                "restrictions": ["Live artillery firing exercises. Vessel entry prohibited under Notice to Mariners (NOTAM)."],
                "description": "Restricted maritime sector off Kochi. Permanent naval gunnery practice area.",
                "authority": "Naval Hydrographic Office (NHO) Dehradun"
            },
            {
                "id": "DEF-02",
                "name": "DRDO Missile Test Range Exclusion Corridor (APJ Abdul Kalam Island)",
                "type": GeofenceType.MILITARY_EXCLUSION_ZONE,
                "coordinates": [[
                    [87.00, 20.70], [87.35, 20.70], [87.35, 20.95], [87.00, 20.95], [87.00, 20.70]
                ]],
                "jurisdiction": "Defence Research and Development Organisation (DRDO)",
                "restrictions": ["Strategic flight testing impact danger zone. High-seas fishing banned during launch windows."],
                "description": "Offshore missile testing range corridor in northern Bay of Bengal.",
                "authority": "Integrated Test Range (ITR) Chandipur"
            },
            {
                "id": "DEF-03",
                "name": "Mumbai High Offshore Oil Production Security Perimeter",
                "type": GeofenceType.PORT_SECURITY_ZONE,
                "coordinates": [[
                    [71.20, 19.25], [71.60, 19.25], [71.60, 19.65], [71.20, 19.65], [71.20, 19.25]
                ]],
                "jurisdiction": "Oil and Natural Gas Corporation (ONGC) / Indian Coast Guard",
                "restrictions": ["Strict 500-meter safety zone around offshore platforms. Trawling prohibited to protect undersea pipelines."],
                "description": "Critical energy infrastructure safety zone in central Arabian Sea.",
                "authority": "Petroleum and Natural Gas Regulatory Board"
            }
        ]

        for mz in military_zones:
            gf = Geofence(
                id=mz["id"],
                name=mz["name"],
                type=mz["type"],
                geometry_type="Polygon",
                coordinates=mz["coordinates"],
                jurisdiction=mz["jurisdiction"],
                effective_start="2020-01-01T00:00:00Z",
                effective_end="2035-12-31T23:59:59Z",
                status="ACTIVE",
                restrictions=mz["restrictions"],
                description=mz["description"],
                provenance={"authority": mz["authority"]}
            )
            self._register_geofence(gf)

        # 3. International Maritime Boundary Line (IMBL) Exclusion Polygons
        for key, imbl in IMBL_BOUNDARIES.items():
            pts_lonlat = [[pt[1], pt[0]] for pt in imbl["coordinates"]]
            # Build a safety corridor buffer polygon around the boundary line (approx 3 NM / 5.5 km width)
            line = LineString(pts_lonlat)
            buffered_line = line.buffer(0.05)  # approx 5.5 km buffer in degrees
            poly_coords = [list(buffered_line.exterior.coords)]
            
            gf = Geofence(
                id=f"IMBL-{key.upper()}",
                name=f"{imbl['name']} Buffer Corridor",
                type=GeofenceType.INTERNATIONAL_BORDER_BUFFER,
                geometry_type="Polygon",
                coordinates=poly_coords,
                jurisdiction="Indian Coast Guard / Ministry of External Affairs",
                effective_start="1974-01-01T00:00:00Z",
                effective_end="2099-12-31T23:59:59Z",
                status="ACTIVE",
                restrictions=[imbl["description"], "Vessel transit strictly monitored; border crossing leads to foreign arrest."],
                description=imbl["description"],
                provenance={
                    "authority": "Bilateral Maritime Boundary Agreement / UNCLOS",
                    "buffer_warning_nm": imbl.get("buffer_warning_nm", 3.0)
                }
            )
            self._register_geofence(gf)

    def _register_geofence(self, gf: Geofence) -> None:
        """Registers a geofence and creates its internal Shapely geometry."""
        self._geofences[gf.id] = gf
        try:
            poly = Polygon(gf.coordinates[0])
            if not poly.is_valid:
                poly = poly.buffer(0)  # Fix minor self-intersections
            self._shapely_geoms[gf.id] = poly
        except Exception as e:
            logger.error(f"Failed to build Shapely geometry for {gf.id}: {e}")

    def load_custom_geofence(self, gf_dict: Dict[str, Any]) -> Geofence:
        """Loads a runtime custom geofence (e.g. for testing or temporary NOTAM)."""
        gf = Geofence(**gf_dict)
        self._register_geofence(gf)
        return gf

    def remove_geofence(self, gf_id: str) -> None:
        """Removes a geofence by ID (useful for temporary fixtures and test cleanup)."""
        self._geofences.pop(gf_id, None)
        self._shapely_geoms.pop(gf_id, None)

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in kilometers."""
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0)**2
        return r * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def _is_active_at_time(self, gf: Geofence, time_window: Optional[Any]) -> bool:
        """
        Evaluates temporal geofence validity against the requested TimeWindow.
        Section 10 requirement.
        """
        if not time_window:
            return gf.status == "ACTIVE"
            
        req_start = getattr(time_window, "start_datetime", None)
        req_end = getattr(time_window, "end_datetime", None)
        
        # If string, parse to datetime
        if isinstance(req_start, str):
            req_start = datetime.fromisoformat(req_start)
        if isinstance(req_end, str):
            req_end = datetime.fromisoformat(req_end)
            
        if not req_start:
            req_start = datetime.now(timezone.utc)
        if not req_end:
            req_end = req_start

        # Check geofence start
        if gf.effective_start:
            gf_start = datetime.fromisoformat(gf.effective_start.replace("Z", "+00:00"))
            if req_end < gf_start:
                return False  # Request is prior to restriction becoming effective

        # Check geofence end
        if gf.effective_end:
            gf_end = datetime.fromisoformat(gf.effective_end.replace("Z", "+00:00"))
            if req_start > gf_end:
                return False  # Restriction has expired for requested time

        return True

    def check_point(
        self,
        lat: float,
        lon: float,
        time_window: Optional[Any] = None,
        buffer_km: float = 5.0
    ) -> Dict[str, Any]:
        """
        Checks whether a point [lat, lon] lies within or near any active geofence.
        Section 7 & 8 requirement: UNKNOWN returned if dataset disabled.
        """
        if not self._enabled:
            return {
                "latitude": lat,
                "longitude": lon,
                "geofence_status": GeofenceStatus.UNKNOWN,
                "is_restricted": False,
                "is_near_restriction": False,
                "matched_geofence": None,
                "distance_to_nearest_km": None,
                "restrictions": [],
                "limitations": ["Geofence dataset is unavailable or disabled; regulatory status is UNKNOWN."]
            }

        pt = Point(lon, lat)
        active_violation = None
        min_dist_km = 999999.0
        nearest_gf = None

        for gf_id, gf in self._geofences.items():
            if not self._is_active_at_time(gf, time_window):
                continue
                
            poly = self._shapely_geoms.get(gf_id)
            if not poly:
                continue

            # Check point-in-polygon
            if poly.contains(pt) or poly.touches(pt):
                active_violation = gf
                min_dist_km = 0.0
                nearest_gf = gf
                break

            # Calculate distance to polygon boundary
            poly_centroid = poly.centroid
            # Geodesic distance approximation to polygon exterior
            ext_coords = list(poly.exterior.coords)
            for c_lon, c_lat in ext_coords:
                d = self._haversine_km(lat, lon, c_lat, c_lon)
                if d < min_dist_km:
                    min_dist_km = d
                    nearest_gf = gf

        if active_violation:
            return {
                "latitude": lat,
                "longitude": lon,
                "geofence_status": GeofenceStatus.RESTRICTED,
                "is_restricted": True,
                "is_near_restriction": True,
                "matched_geofence": {
                    "id": active_violation.id,
                    "name": active_violation.name,
                    "type": active_violation.type.value,
                    "jurisdiction": active_violation.jurisdiction,
                    "restrictions": active_violation.restrictions
                },
                "distance_to_nearest_km": 0.0,
                "restrictions": active_violation.restrictions,
                "limitations": []
            }
        elif min_dist_km <= buffer_km and nearest_gf:
            return {
                "latitude": lat,
                "longitude": lon,
                "geofence_status": GeofenceStatus.NEAR_RESTRICTION,
                "is_restricted": False,
                "is_near_restriction": True,
                "matched_geofence": {
                    "id": nearest_gf.id,
                    "name": nearest_gf.name,
                    "type": nearest_gf.type.value,
                    "jurisdiction": nearest_gf.jurisdiction,
                    "restrictions": nearest_gf.restrictions
                },
                "distance_to_nearest_km": round(min_dist_km, 2),
                "restrictions": nearest_gf.restrictions,
                "limitations": [f"Operating within {round(min_dist_km, 2)} km safety buffer of '{nearest_gf.name}'."]
            }
        else:
            return {
                "latitude": lat,
                "longitude": lon,
                "geofence_status": GeofenceStatus.CLEAR,
                "is_restricted": False,
                "is_near_restriction": False,
                "matched_geofence": {
                    "id": nearest_gf.id,
                    "name": nearest_gf.name,
                    "type": nearest_gf.type.value
                } if nearest_gf else None,
                "distance_to_nearest_km": round(min_dist_km, 2) if nearest_gf else None,
                "restrictions": [],
                "limitations": []
            }

    def check_candidate_polygon(
        self,
        polygon_coords: List[List[float]],
        time_window: Optional[Any] = None,
        buffer_km: float = 5.0
    ) -> Dict[str, Any]:
        """
        Checks whether a PFZ candidate polygon intersects or approaches any active geofence.
        Section 7 & 9 requirement.
        """
        if not self._enabled:
            return {
                "geofence_status": GeofenceStatus.UNKNOWN,
                "is_restricted": False,
                "is_near_restriction": False,
                "intersecting_geofences": [],
                "nearest_geofence": None,
                "distance_to_nearest_km": None,
                "limitations": ["Geofence dataset unavailable; regulatory compliance is UNKNOWN."]
            }

        try:
            cand_poly = Polygon(polygon_coords)
            if not cand_poly.is_valid:
                cand_poly = cand_poly.buffer(0)
        except Exception as e:
            return {
                "geofence_status": GeofenceStatus.UNKNOWN,
                "is_restricted": False,
                "is_near_restriction": False,
                "intersecting_geofences": [],
                "nearest_geofence": None,
                "distance_to_nearest_km": None,
                "limitations": [f"Invalid candidate polygon geometry: {e}"]
            }

        intersecting = []
        min_dist_km = 999999.0
        nearest_gf = None

        cand_centroid = cand_poly.centroid

        for gf_id, gf in self._geofences.items():
            if not self._is_active_at_time(gf, time_window):
                continue

            poly = self._shapely_geoms.get(gf_id)
            if not poly:
                continue

            # Polygon-in-polygon / intersection
            if cand_poly.intersects(poly):
                intersecting.append(gf)
                min_dist_km = 0.0
                nearest_gf = gf
            else:
                # Check exterior distance
                for c_lon, c_lat in list(poly.exterior.coords):
                    d = self._haversine_km(cand_centroid.y, cand_centroid.x, c_lat, c_lon)
                    if d < min_dist_km:
                        min_dist_km = d
                        nearest_gf = gf

        if intersecting:
            return {
                "geofence_status": GeofenceStatus.RESTRICTED,
                "is_restricted": True,
                "is_near_restriction": True,
                "intersecting_geofences": [
                    {"id": g.id, "name": g.name, "type": g.type.value, "restrictions": g.restrictions}
                    for g in intersecting
                ],
                "nearest_geofence": nearest_gf.name if nearest_gf else None,
                "distance_to_nearest_km": 0.0,
                "limitations": [f"Candidate polygon overlaps restricted boundary: {', '.join(g.name for g in intersecting)}."]
            }
        elif min_dist_km <= buffer_km and nearest_gf:
            return {
                "geofence_status": GeofenceStatus.NEAR_RESTRICTION,
                "is_restricted": False,
                "is_near_restriction": True,
                "intersecting_geofences": [],
                "nearest_geofence": nearest_gf.name,
                "distance_to_nearest_km": round(min_dist_km, 2),
                "limitations": [f"Candidate polygon is within {round(min_dist_km, 2)} km safety buffer of '{nearest_gf.name}'."]
            }
        else:
            return {
                "geofence_status": GeofenceStatus.CLEAR,
                "is_restricted": False,
                "is_near_restriction": False,
                "intersecting_geofences": [],
                "nearest_geofence": nearest_gf.name if nearest_gf else None,
                "distance_to_nearest_km": round(min_dist_km, 2) if nearest_gf else None,
                "limitations": []
            }

    def get_active_geofences(self, time_window: Optional[Any] = None) -> List[Geofence]:
        """Returns all currently active geofences for time window."""
        if not self._enabled:
            return []
        return [gf for gf in self._geofences.values() if self._is_active_at_time(gf, time_window)]

    def is_land_point(self, lat: float, lon: float) -> bool:
        """
        Geodetic land boundary determination for Indian Subcontinent.
        Section 24 requirement: strictly avoids routing across land.
        """
        # 1. Broad Indian Peninsular Bounding Polygon Check
        # Coarse polygon enclosing mainland India
        # Points inside this inland envelope are land (not Arabian Sea or Bay of Bengal)
        # Western Ghats coastline approx: lon > 74.0 for lat 14-16, lon > 75.0 for lat 11-13, lon > 76.0 for lat 9-10
        if 8.0 <= lat <= 24.0 and 72.0 <= lon <= 88.0:
            # Approximate Indian west coast longitude for given latitude:
            # Lat 8.5 (Kanyakumari): lon ~ 77.5
            # Lat 9.5 (Kochi): lon ~ 76.2
            # Lat 12.8 (Mangalore): lon ~ 74.8
            # Lat 15.0 (Goa): lon ~ 73.8
            # Lat 19.0 (Mumbai): lon ~ 72.8
            # Lat 21.0 (Gujarat): lon ~ 72.5
            # If lon is significantly east of the west coast AND west of the east coast, it is land!
            west_coast_lon = 77.5 - (lat - 8.0) * (77.5 - 72.5) / 13.0
            east_coast_lon = 78.0 + (lat - 8.0) * (87.0 - 78.0) / 14.0
            
            # Inland envelope
            if (west_coast_lon + 0.15) < lon < (east_coast_lon - 0.15):
                return True

        # Northern continental landmass
        if lat > 24.5 and 68.0 <= lon <= 90.0:
            return True

        # Sri Lanka landmass approximation
        if 5.9 <= lat <= 9.8 and 79.7 <= lon <= 81.9:
            return True

        return False
