import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

export default function GISRiskMap({ corridors, language, role }) {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (map.current) return;
    
    try {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: {
          version: 8,
          sources: {
            // Offline fallback vector map source
            'osm': {
              type: 'raster',
              tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '&copy; OpenStreetMap Contributors'
            },
            'ner-outline': {
              type: 'geojson',
              data: {
                type: 'FeatureCollection',
                features: [{
                  type: 'Feature',
                  geometry: {
                    type: 'Polygon',
                    coordinates: [[[89.0, 29.0], [97.5, 29.0], [97.5, 22.0], [89.0, 22.0], [89.0, 29.0]]]
                  }
                }]
              }
            }
          },
          layers: [
            {
              id: 'osm-tiles',
              type: 'raster',
              source: 'osm',
              minzoom: 0,
              maxzoom: 19
            },
            {
              id: 'ner-boundary',
              type: 'line',
              source: 'ner-outline',
              paint: {
                'line-color': '#475569',
                'line-width': 2,
                'line-dasharray': [2, 2]
              }
            }
          ]
        },
        center: [92.0, 26.0], // Approx center of NER
        zoom: 6
      });
      
      map.current.on('load', () => {
         // Add corridors source if provided
         map.current.addSource('corridors', {
            type: 'geojson',
            data: {
               type: 'FeatureCollection',
               features: corridors.map(c => ({
                 type: 'Feature',
                 properties: { status: c.status, id: c.corridor_id },
                 geometry: {
                   type: 'LineString',
                   // Mock coordinates based on state
                   coordinates: c.corridor_id.includes('NAGALAND') 
                     ? [[93.73, 25.9], [93.8, 25.8], [94.1, 25.67]] 
                     : [[88.4, 26.9], [88.5, 27.2], [88.6, 27.3]]
                 }
               }))
            }
         });
         
         map.current.addLayer({
            id: 'corridor-lines',
            type: 'line',
            source: 'corridors',
            paint: {
               'line-width': 5,
               'line-color': [
                  'match',
                  ['get', 'status'],
                  'OPEN', '#22c55e',
                  'COMPROMISED', '#f59e0b',
                  'BLOCKED', '#ef4444',
                  '#94a3b8' // Default
               ]
            }
         });
      });
    } catch (err) {
      console.error("Map load error (likely offline):", err);
      setError("Map tile server unavailable. Running in offline fallback mode.");
    }
    
    return () => {
        if(map.current) map.current.remove();
        map.current = null;
    }
  }, []);
  
  // Update corridor data when it changes
  useEffect(() => {
     if(map.current && map.current.getSource('corridors')) {
        map.current.getSource('corridors').setData({
           type: 'FeatureCollection',
           features: corridors.map(c => ({
             type: 'Feature',
             properties: { status: c.status, id: c.corridor_id },
             geometry: {
               type: 'LineString',
               coordinates: c.corridor_id.includes('NAGALAND') 
                 ? [[93.73, 25.9], [93.8, 25.8], [94.1, 25.67]] 
                 : [[88.4, 26.9], [88.5, 27.2], [88.6, 27.3]]
             }
           }))
        });
     }
  }, [corridors]);

  const handleBlockRoad = async (corridor_id) => {
    if (role !== "DistrictOfficer") {
       alert("403 Forbidden: Only District Officers can close roads.");
       return;
    }
    
    try {
        await fetch(`http://localhost:8000/api/risk/corridors/${corridor_id}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${role}`
            },
            body: JSON.stringify({ status: 'BLOCKED' })
        });
        // Normally we'd refresh the list here via a callback prop
        window.dispatchEvent(new Event('refresh-data'));
    } catch (e) {
        alert("Failed to reach server");
    }
  };

  return (
    <div className="relative w-full h-full min-h-[400px] border border-slate-300 rounded overflow-hidden">
      {error && <div className="absolute top-2 left-2 z-10 bg-yellow-100 text-yellow-800 p-2 text-xs rounded opacity-90">{error}</div>}
      <div ref={mapContainer} className="absolute inset-0" />
      
      {/* Dev UI overlay to trigger road blocks */}
      <div className="absolute bottom-4 right-4 z-10 bg-white p-2 rounded shadow flex flex-col gap-2">
         <span className="text-xs font-bold text-slate-700">Cedar Auth Test:</span>
         <button 
           onClick={() => handleBlockRoad("NH-29-NAGALAND")}
           className="bg-red-500 hover:bg-red-600 text-white text-xs px-2 py-1 rounded">
           Close NH-29
         </button>
      </div>
    </div>
  );
}
