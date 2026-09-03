/**
 * Offline IMBL Geofence Engine & Audio Alarm Synthesizer
 * Computes exact geodesic distance to International Maritime Boundaries (IMBL)
 * completely on-device without requiring internet connectivity.
 */

export interface IMBLBoundary {
  id: string;
  name: string;
  coordinates: [number, number][]; // [lat, lon]
}

export const OFFLINE_IMBL_BOUNDARIES: IMBLBoundary[] = [
  {
    id: "india_srilanka",
    name: "India-Sri Lanka IMBL (Palk Strait & Gulf of Mannar)",
    coordinates: [
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
  {
    id: "india_pakistan",
    name: "India-Pakistan IMBL (Sir Creek & Arabian Sea)",
    coordinates: [
      [23.5833, 68.1000],
      [23.4500, 67.8000],
      [23.2000, 67.4000],
      [22.8000, 66.8000],
      [22.3000, 66.2000],
      [21.5000, 65.5000]
    ]
  },
  {
    id: "india_bangladesh",
    name: "India-Bangladesh IMBL (Bay of Bengal)",
    coordinates: [
      [21.6333, 89.1500],
      [21.4333, 89.2500],
      [21.1167, 89.3667],
      [20.5667, 89.5000],
      [19.5000, 89.7000]
    ]
  }
];

/**
 * Calculates Haversine distance in kilometers between two GPS coordinates
 */
export function calculateHaversineDistanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371.0; // Earth radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Calculates perpendicular distance from a point to a line segment in km
 */
export function pointToSegmentDistanceKm(
  plat: number,
  plon: number,
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const dx = (lon2 - lon1) * Math.cos(((lat1 + lat2) / 2) * (Math.PI / 180)) * 111.32;
  const dy = (lat2 - lat1) * 110.57;

  if (dx === 0 && dy === 0) {
    return calculateHaversineDistanceKm(plat, plon, lat1, lon1);
  }

  const px = (plon - lon1) * Math.cos(((lat1 + plat) / 2) * (Math.PI / 180)) * 111.32;
  const py = (plat - lat1) * 110.57;

  const t = Math.max(0, Math.min(1, (px * dx + py * dy) / (dx * dx + dy * dy)));
  const nearestLat = lat1 + t * (lat2 - lat1);
  const nearestLon = lon1 + t * (lon2 - lon1);

  return calculateHaversineDistanceKm(plat, plon, nearestLat, nearestLon);
}

export interface GeofenceProximityResult {
  latitude: number;
  longitude: number;
  nearestBorderName: string;
  distanceKm: number;
  distanceNM: number;
  threatLevel: 'SAFE' | 'ADVISORY' | 'CAUTION' | 'CRITICAL_BREACH';
  alertMessage: string;
  isBreach: boolean;
  isCaution: boolean;
}

/**
 * Offline calculation of nearest IMBL boundary from device GPS
 * Checks both distance and foreign boundary crossings (Sri Lanka, Pakistan, Bangladesh, Outer EEZ)
 */
export function evaluateOfflineGeofence(lat: number, lon: number): GeofenceProximityResult {
  // 1. Check if completely outside Sovereign Indian Maritime EEZ Bounds (e.g. Europe, International Waters)
  const isOutsideIndianWaters = (lat < 2.0 || lat > 26.0 || lon < 64.0 || lon > 96.5);
  
  if (isOutsideIndianWaters) {
    return {
      latitude: lat,
      longitude: lon,
      nearestBorderName: "200 NM Indian EEZ Sovereign Outer Limit",
      distanceKm: 0.0,
      distanceNM: 0.0,
      threatLevel: 'CRITICAL_BREACH',
      alertMessage: `🚨 OUT OF BORDER WARNING: Vessel is in Foreign / International Waters (Lat: ${lat.toFixed(3)}°, Lon: ${lon.toFixed(3)}°). You are outside sovereign Indian Maritime jurisdiction. Turn 180° towards Indian Coast immediately!`,
      isBreach: true,
      isCaution: true
    };
  }

  // 2. Check specific regional IMBL cross-border territorial incursions
  // A. Sri Lanka IMBL Crossing (Palk Strait & Gulf of Mannar)
  // Approximate line: from (10.08, 79.87) to (9.35, 79.37) to (7.83, 78.60)
  if (lat >= 7.5 && lat <= 10.5 && lon >= 78.8) {
    const imblLonAtLat = 79.37 + (lat - 9.35) * ((79.87 - 79.37) / (10.08 - 9.35));
    if (lon > imblLonAtLat + 0.02) {
      return {
        latitude: lat,
        longitude: lon,
        nearestBorderName: "Sri Lankan Territorial Waters (Palk Strait)",
        distanceKm: 0.0,
        distanceNM: 0.0,
        threatLevel: 'CRITICAL_BREACH',
        alertMessage: `🚨 CRITICAL SRI LANKAN IMBL BREACH! Vessel has crossed the International Maritime Boundary Line into Sri Lankan Territorial Waters. Immediate foreign Navy arrest risk! Turn 180° West immediately!`,
        isBreach: true,
        isCaution: true
      };
    }
  }

  // B. Pakistan IMBL Crossing (Sir Creek & Arabian Sea)
  // Approximate line: from (23.58, 68.10) down to (21.50, 65.50)
  if (lat >= 21.0 && lat <= 24.5 && lon <= 68.5) {
    const imblLonAtLat = 68.10 - ((23.58 - lat) / (23.58 - 21.50)) * (68.10 - 65.50);
    if (lon < imblLonAtLat - 0.02) {
      return {
        latitude: lat,
        longitude: lon,
        nearestBorderName: "Pakistan Maritime Security Agency Zone (Sir Creek)",
        distanceKm: 0.0,
        distanceNM: 0.0,
        threatLevel: 'CRITICAL_BREACH',
        alertMessage: `🚨 CRITICAL PAKISTAN IMBL BREACH! Vessel has crossed into Pakistan Maritime Waters. Immediate seizure danger. Turn 180° East immediately!`,
        isBreach: true,
        isCaution: true
      };
    }
  }

  // C. Bangladesh IMBL Crossing (Bay of Bengal)
  if (lat >= 20.0 && lat <= 22.0 && lon >= 89.15) {
    return {
      latitude: lat,
      longitude: lon,
      nearestBorderName: "Bangladesh Maritime Boundary (Bay of Bengal)",
      distanceKm: 0.0,
      distanceNM: 0.0,
      threatLevel: 'CRITICAL_BREACH',
      alertMessage: `🚨 CRITICAL BANGLADESH IMBL BREACH! Vessel has crossed the International Maritime Boundary Line into Bangladesh waters. Turn 180° West immediately!`,
      isBreach: true,
      isCaution: true
    };
  }

  // 3. Calculate distance to nearest IMBL boundary line
  let minDistanceKm = 999999;
  let closestBorderName = "International Maritime Boundary";

  for (const boundary of OFFLINE_IMBL_BOUNDARIES) {
    const pts = boundary.coordinates;
    for (let i = 0; i < pts.length - 1; i++) {
      const d = pointToSegmentDistanceKm(
        lat,
        lon,
        pts[i][0],
        pts[i][1],
        pts[i + 1][0],
        pts[i + 1][1]
      );
      if (d < minDistanceKm) {
        minDistanceKm = d;
        closestBorderName = boundary.name;
      }
    }
  }

  const distanceNM = Number((minDistanceKm / 1.852).toFixed(2));
  const roundedKm = Number(minDistanceKm.toFixed(2));

  let threatLevel: GeofenceProximityResult['threatLevel'] = 'SAFE';
  let alertMessage = `Safe within Indian Sovereign Waters. Nearest border: ${distanceNM} NM away.`;
  let isBreach = false;
  let isCaution = false;

  if (distanceNM <= 2.5) {
    threatLevel = 'CRITICAL_BREACH';
    isBreach = true;
    isCaution = true;
    alertMessage = `🚨 CRITICAL BORDER WARNING: Vessel is only ${distanceNM} NM from ${closestBorderName}! Turn 180° immediately to avoid foreign arrest.`;
  } else if (distanceNM <= 6.0) {
    threatLevel = 'CAUTION';
    isCaution = true;
    alertMessage = `⚠️ BORDER PROXIMITY ALERT: ${distanceNM} NM from ${closestBorderName}. Alter course away from boundary line.`;
  } else if (distanceNM <= 12.0) {
    threatLevel = 'ADVISORY';
    alertMessage = `ℹ️ Outer Border Zone: ${distanceNM} NM from ${closestBorderName}. Maintain GPS awareness.`;
  }

  return {
    latitude: lat,
    longitude: lon,
    nearestBorderName: closestBorderName,
    distanceKm: roundedKm,
    distanceNM,
    threatLevel,
    alertMessage,
    isBreach,
    isCaution
  };
}

/**
 * Web Audio API Buzzer / Siren Synthesizer
 * Generates an oscillating emergency sound without loading external audio files
 */
class GeofenceAudioSiren {
  private audioCtx: AudioContext | null = null;
  private oscillator: OscillatorNode | null = null;
  private gainNode: GainNode | null = null;
  private isPlaying = false;
  private intervalId: any = null;

  private initContext() {
    if (!this.audioCtx && typeof window !== 'undefined') {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass) {
        this.audioCtx = new AudioContextClass();
      }
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  public isSirenDisabled = true; // Disabled per user request

  public startSiren(isCritical: boolean = true) {
    // Siren sound playback disabled per user request
    if (this.isSirenDisabled) return;
    if (this.isPlaying) return;
    this.initContext();
    if (!this.audioCtx) return;

    try {
      this.isPlaying = true;
      const freqHigh = isCritical ? 960 : 750;
      const freqLow = isCritical ? 620 : 500;
      const pulseRateMs = isCritical ? 250 : 500;

      let high = false;
      const playBeep = () => {
        if (!this.isPlaying || !this.audioCtx) return;

        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(high ? freqHigh : freqLow, this.audioCtx.currentTime);
        high = !high;

        gain.gain.setValueAtTime(0.3, this.audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + (pulseRateMs / 1000) * 0.8);

        osc.connect(gain);
        gain.connect(this.audioCtx.destination);

        osc.start();
        osc.stop(this.audioCtx.currentTime + (pulseRateMs / 1000) * 0.8);
      };

      playBeep();
      this.intervalId = setInterval(playBeep, pulseRateMs);
    } catch (e) {
      console.warn("Unable to start audio siren:", e);
    }
  }

  public stopSiren() {
    this.isPlaying = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  public isSirenActive(): boolean {
    return this.isPlaying;
  }
}

export const geofenceAudioSiren = new GeofenceAudioSiren();
