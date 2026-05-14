import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { fetchLivePollution, socket } from '../services/api';
import L from 'leaflet';
import { motion } from 'framer-motion';
import { Map as MapIcon } from 'lucide-react';

const zoneCoordinates = {
  'Zone A': { lat: 28.7041, lng: 77.1025, name: 'Delhi (Zone A)' },
  'Zone B': { lat: 19.0760, lng: 72.8777, name: 'Mumbai (Zone B)' },
  'Zone C': { lat: 12.9716, lng: 77.5946, name: 'Bangalore (Zone C)' },
  'Zone D': { lat: 13.0827, lng: 80.2707, name: 'Chennai (Zone D)' },
};



const LiveMap = () => {
  const center = [20.5937, 78.9629]; 
  const [zones, setZones] = useState([]);

  useEffect(() => {
    fetchLivePollution()
      .then((data) => {
        const latestPerZone = {};
        data.forEach(reading => {
          if (!latestPerZone[reading.zone]) {
            latestPerZone[reading.zone] = reading;
          }
        });
        
        const mapData = Object.values(latestPerZone).map(formatZoneData);
        setZones(mapData);
      })
      .catch(console.error);

    socket.on('newData', (newRecord) => {
      setZones((prevZones) => {
        const updatedZone = formatZoneData(newRecord);
        const exists = prevZones.find(z => z.originalZone === newRecord.zone);
        if (exists) {
          return prevZones.map(z => z.originalZone === newRecord.zone ? updatedZone : z);
        } else {
          return [...prevZones, updatedZone];
        }
      });
    });

    return () => socket.off('newData');
  }, []);

  const formatZoneData = (reading) => {
    let lat = 20;
    let lng = 78;
    let name = reading.zone;

    if (zoneCoordinates[reading.zone]) {
      lat = zoneCoordinates[reading.zone].lat;
      lng = zoneCoordinates[reading.zone].lng;
      name = zoneCoordinates[reading.zone].name;
    } else {
      let hash = 0;
      for (let i = 0; i < reading.zone.length; i++) {
        hash = reading.zone.charCodeAt(i) + ((hash << 5) - hash);
      }
      lat = 10.0 + (Math.abs(Math.sin(hash)) * 22.0);
      lng = 70.0 + (Math.abs(Math.cos(hash)) * 20.0);
    }

    return {
      id: reading._id || Math.random().toString(),
      originalZone: reading.zone,
      name: name,
      lat: lat,
      lng: lng,
      aqi: reading.aqi,
      risk: reading.risk_level,
      timestamp: reading.timestamp
    };
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="h-full flex flex-col space-y-6 pb-10"
    >
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center tracking-tight">
            <MapIcon className="mr-3 text-sky-400" size={24} />
            Live Global Monitors
          </h1>
          <p className="text-slate-400 mt-1 text-sm">Real-time geographical emission distribution across zones.</p>
        </div>
      </div>
      
      <div className="flex-1 glass-card rounded-2xl overflow-hidden relative z-0 p-1.5" style={{ minHeight: '600px' }}>
        <div className="w-full h-full rounded-xl overflow-hidden relative border border-slate-700/50">
          
          <MapContainer center={center} zoom={5} className="h-full w-full bg-[#0F172A]">
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              attribution='&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            />
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
            />
          </MapContainer>

        </div>
      </div>
    </motion.div>
  );
};

export default LiveMap;
