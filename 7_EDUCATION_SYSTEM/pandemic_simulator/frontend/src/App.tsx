/**
 * App Component - Main Pandemic Simulator Application
 * BlackMamba University Educational Module
 */

import React, { useState, useEffect } from 'react';
import { PandemicGlobe } from './components/PandemicGlobe';
import { StatsPanel } from './components/StatsPanel';
import { InterventionPanel } from './components/InterventionPanel';
import { TimelineChart } from './components/TimelineChart';

interface PandemicStats {
  day: number;
  susceptible: number;
  exposed: number;
  infected: number;
  recovered: number;
  deaths: number;
  r_effective: number;
}

interface TimelineEntry extends PandemicStats {}

function App() {
  const [stats, setStats] = useState<PandemicStats>({
    day: 0,
    susceptible: 8000000000,
    exposed: 0,
    infected: 100,
    recovered: 0,
    deaths: 0,
    r_effective: 2.5
  });

  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [budget] = useState(1000); // 1000 billion USD
  const [activeInterventions, setActiveInterventions] = useState<Set<string>>(new Set());

  // Simulate pandemic progression
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setStats(prevStats => {
        // Apply interventions to modify R0
        let effectiveR0 = 2.5;
        
        if (activeInterventions.has('lockdown')) effectiveR0 *= 0.4;
        if (activeInterventions.has('masks')) effectiveR0 *= 0.5;
        if (activeInterventions.has('social_distancing')) effectiveR0 *= 0.7;
        if (activeInterventions.has('vaccine')) effectiveR0 *= 0.1;
        if (activeInterventions.has('border_closure')) effectiveR0 *= 0.6;
        if (activeInterventions.has('testing')) effectiveR0 *= 0.75;

        effectiveR0 = Math.max(effectiveR0, 0.1);

        // Simple SEIR model calculations
        const infectiousDays = 10;
        const mortalityRate = 0.02;
        
        const newInfections = Math.min(
          prevStats.infected * effectiveR0 / infectiousDays,
          prevStats.susceptible
        );
        
        const newDeaths = prevStats.infected * mortalityRate / infectiousDays;
        const newRecovered = prevStats.infected * (1 - mortalityRate) / infectiousDays;

        const newStats = {
          day: prevStats.day + 1,
          susceptible: Math.max(0, prevStats.susceptible - newInfections),
          exposed: prevStats.exposed + newInfections,
          infected: Math.max(0, prevStats.infected + newInfections - newDeaths - newRecovered),
          recovered: prevStats.recovered + newRecovered,
          deaths: prevStats.deaths + newDeaths,
          r_effective: effectiveR0
        };

        // Add to timeline
        setTimeline(prev => [...prev, newStats]);

        return newStats;
      });
    }, 1000 / speed);

    return () => clearInterval(interval);
  }, [isPlaying, speed, activeInterventions]);

  const handleInterventionToggle = (interventionId: string) => {
    setActiveInterventions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(interventionId)) {
        newSet.delete(interventionId);
      } else {
        newSet.add(interventionId);
      }
      return newSet;
    });
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setStats({
      day: 0,
      susceptible: 8000000000,
      exposed: 0,
      infected: 100,
      recovered: 0,
      deaths: 0,
      r_effective: 2.5
    });
    setTimeline([]);
    setActiveInterventions(new Set());
  };

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed);
  };

  // Calculate infection level for globe visualization
  const totalPopulation = 8000000000;
  const infectedPopulation = stats.infected + stats.recovered + stats.deaths;
  const infectionLevel = Math.min(infectedPopulation / totalPopulation, 1.0);

  return (
    <div className="relative w-screen h-screen bg-black text-white overflow-hidden">
      {/* Main Globe Visualization */}
      <PandemicGlobe infectionLevel={infectionLevel} />

      {/* Stats Panel */}
      <StatsPanel stats={stats} />

      {/* Timeline Chart */}
      <TimelineChart timeline={timeline} currentDay={stats.day} />

      {/* Intervention Panel */}
      <InterventionPanel 
        budget={budget}
        onInterventionToggle={handleInterventionToggle}
      />

      {/* Control Panel */}
      <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-md border border-green-500/30 rounded-lg p-4 shadow-2xl">
        <div className="flex items-center space-x-4">
          <button
            onClick={handlePlayPause}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-bold transition-colors"
          >
            {isPlaying ? '⏸️ Pausar' : '▶️ Iniciar'}
          </button>
          
          <button
            onClick={handleReset}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-bold transition-colors"
          >
            🔄 Reiniciar
          </button>

          <div className="flex items-center space-x-2">
            <span className="text-gray-400 text-sm">Velocidad:</span>
            <div className="flex space-x-1">
              {[1, 2, 5, 10].map(s => (
                <button
                  key={s}
                  onClick={() => handleSpeedChange(s)}
                  className={`px-3 py-2 rounded ${
                    speed === s
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                  } transition-colors`}
                >
                  {s}x
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Educational Info */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-black/60 backdrop-blur-md border border-green-500/30 rounded-lg px-6 py-2">
        <p className="text-gray-300 text-sm">
          🎓 <span className="text-green-400 font-bold">BMU Educational Module</span> - 
          Modelo SEIR de Simulación de Pandemias
        </p>
      </div>
    </div>
  );
}

export default App;
