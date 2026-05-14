import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, AreaChart, Area, BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ScatterChart, Scatter, ZAxis } from 'recharts';
import { BarChart, Activity, TrendingUp, AlertCircle } from 'lucide-react';
import { fetchLivePollution } from '../services/api';

const Analytics = () => {
  const [topZonesData, setTopZonesData] = useState([]);
  const [pmData, setPmData] = useState([]);
  const [scatterData, setScatterData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLivePollution()
      .then((data) => {
        // Filter out any invalid data
        const validData = data.filter(d => d.aqi && d.pm25 && d.pm10);
        
        // Sort by AQI descending
        const sorted = [...validData].sort((a, b) => b.aqi - a.aqi);
        
        // 1. Top 15 Polluted Zones
        const top15 = sorted.slice(0, 15).map(d => ({
          zone: (d.zone.split(',')[0] || '').substring(0, 12) + '...',
          aqi: Math.round(d.aqi),
          pm25: parseFloat(d.pm25).toFixed(1)
        }));
        
        // 2. Particulate Matter Comparison (Top 25)
        const pmDataArray = sorted.slice(0, 25).map(d => ({
          zone: (d.zone.split(',')[0] || '').substring(0, 10),
          pm25: Math.round(d.pm25),
          pm10: Math.round(d.pm10)
        }));

        // 3. PM 2.5 vs AQI Correlation
        const sData = validData.map(d => ({
          pm25: Math.round(d.pm25),
          aqi: Math.round(d.aqi),
          z: 100, 
          name: d.zone
        }));

        setTopZonesData(top15);
        setPmData(pmDataArray);
        setScatterData(sData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const pointName = payload[0].payload.name || label;
      return (
        <div className="bg-[#0F172A] border border-slate-700 p-4 rounded-xl shadow-xl">
          <p className="text-slate-100 font-bold mb-3 text-sm">{pointName}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center space-x-3 text-sm mb-1.5 last:mb-0">
              <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color || entry.fill }}></div>
              <span className="text-slate-400 font-medium capitalize">{entry.name}:</span>
              <span className="font-bold text-slate-100">{entry.value}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 pb-10 max-w-7xl mx-auto"
    >
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center">
            <BarChart className="mr-3 text-sky-400" size={24} />
            Advanced Analytics
          </h1>
          <p className="text-slate-400 mt-1 text-sm">Deep insights and predictive forecasting based on current datasets.</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Top 15 Most Polluted Zones */}
          <motion.div variants={itemVariants} className="glass-card p-6 flex flex-col h-[400px]">
            <div className="mb-6 flex items-center">
              <AlertCircle className="text-rose-400 mr-2" size={18} />
              <h2 className="text-sm font-semibold text-slate-200">Top 15 Hazardous Zones (AQI)</h2>
            </div>
            <div className="flex-1 w-full relative z-10">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsBarChart data={topZonesData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="zone" stroke="#64748b" fontSize={10} tickMargin={10} interval={0} angle={-45} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Bar dataKey="aqi" name="AQI" fill="#F43F5E" radius={[4, 4, 0, 0]} />
                </RechartsBarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* PM2.5 vs PM10 Chart */}
          <motion.div variants={itemVariants} className="glass-card p-6 flex flex-col h-[400px]">
            <div className="mb-6 flex items-center">
              <TrendingUp className="text-indigo-400 mr-2" size={18} />
              <h2 className="text-sm font-semibold text-slate-200">PM2.5 vs PM10 Across Zones</h2>
            </div>
            <div className="flex-1 w-full relative z-10">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={pmData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <defs>
                    <linearGradient id="colorPm10" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorPm25" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="zone" stroke="#64748b" fontSize={10} tickMargin={10} interval={0} angle={-45} textAnchor="end" />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="pm10" name="PM 10" stroke="#F59E0B" strokeWidth={2} fillOpacity={1} fill="url(#colorPm10)" />
                  <Area type="monotone" dataKey="pm25" name="PM 2.5" stroke="#8B5CF6" strokeWidth={2} fillOpacity={1} fill="url(#colorPm25)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* PM 2.5 vs AQI Scatter Plot */}
          <motion.div variants={itemVariants} className="glass-card p-6 flex flex-col h-[400px] lg:col-span-2">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center">
                <Activity className="text-violet-400 mr-2" size={18} />
                <h2 className="text-sm font-semibold text-slate-200">PM2.5 Density vs. Predicted AQI Correlation</h2>
              </div>
              <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-2.5 py-1 rounded-md border border-indigo-500/20 font-bold tracking-wide uppercase">Dataset Analysis</span>
            </div>
            <div className="flex-1 w-full relative z-10">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis type="number" dataKey="pm25" name="PM 2.5 Density" stroke="#64748b" fontSize={11} label={{ value: 'PM 2.5 (µg/m³)', position: 'insideBottom', offset: -10, fill: '#64748b' }} />
                  <YAxis type="number" dataKey="aqi" name="AQI" stroke="#64748b" fontSize={11} label={{ value: 'Air Quality Index', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
                  <ZAxis type="number" dataKey="z" range={[40, 100]} name="Volume" />
                  <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
                  <Scatter name="Zones" data={scatterData} fill="#38BDF8" fillOpacity={0.6} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

        </div>
      )}
    </motion.div>
  );
};

export default Analytics;
