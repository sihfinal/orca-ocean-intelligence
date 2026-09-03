/**
 * Indian Ocean Maritime Boundaries & Exclusive Economic Zone (EEZ)
 * Sourced from UNCLOS / ITLOS Treaties & Ministry of Earth Sciences (MoES).
 * Represents India's 200 Nautical Mile Exclusive Economic Zone and 12 NM Territorial Waters.
 */

export interface MaritimeBoundary {
  name: string;
  type: 'eez' | 'territorial_waters' | 'imbl';
  description: string;
  color: string;
  coordinates: [number, number][];
}

// 200 Nautical Mile Indian Exclusive Economic Zone (EEZ) Outer Limit (Arabian Sea & Bay of Bengal)
export const INDIAN_EEZ_BOUNDARY: [number, number][] = [
  // West Coast EEZ Outer Perimeter (Arabian Sea)
  [21.5000, 65.5000],
  [20.0000, 66.2000],
  [18.5000, 67.5000],
  [16.0000, 68.8000],
  [14.0000, 70.0000],
  [12.0000, 71.2000],
  [10.0000, 72.5000],
  [8.0000, 73.8000],
  [6.5000, 75.5000],
  [5.5000, 77.5000], // South of Kanyakumari

  // East Coast EEZ Outer Perimeter (Bay of Bengal)
  [6.0000, 79.5000],
  [7.5000, 81.5000],
  [9.0000, 82.8000],
  [11.5000, 84.0000],
  [14.0000, 85.5000],
  [16.5000, 87.0000],
  [18.5000, 88.2000],
  [20.5000, 89.5000],
  [21.5000, 89.2000]
];

// 12 Nautical Mile Sovereign Territorial Waters Buffer
export const INDIAN_TERRITORIAL_WATERS_12NM: [number, number][] = [
  // Gujarat / Kutch
  [23.5833, 68.1000], [22.4000, 68.5000], [21.3000, 69.2000], [20.6000, 71.0000],
  // Maharashtra / Goa
  [19.2000, 72.3000], [17.5000, 72.7000], [15.2000, 73.3000],
  // Karnataka / Kerala
  [13.8000, 74.0000], [11.8000, 74.8000], [9.8000, 75.7000], [8.2000, 76.8000],
  // Cape Comorin / Kanyakumari
  [7.8000, 77.5000],
  // Tamil Nadu / Andhra Pradesh
  [8.8000, 78.4000], [10.5000, 80.0000], [13.2000, 80.5000], [15.8000, 80.4000],
  [17.8000, 83.5000],
  // Odisha / West Bengal
  [19.6000, 85.5000], [20.4000, 86.9000], [21.5000, 87.8000]
];
