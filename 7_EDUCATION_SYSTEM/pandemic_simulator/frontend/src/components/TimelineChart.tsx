/**
 * TimelineChart Component
 * Visualizes pandemic progression over time
 * BlackMamba University - Pandemic Simulator
 */

import React from 'react';

interface TimelineEntry {
  day: number;
  susceptible: number;
  exposed: number;
  infected: number;
  recovered: number;
  deaths: number;
  r_effective: number;
}

interface TimelineChartProps {
  timeline: TimelineEntry[];
  currentDay: number;
}

export function TimelineChart({ timeline, currentDay }: TimelineChartProps) {
  if (timeline.length === 0) {
    return (
      <div className="absolute top-4 right-4 bg-black/80 backdrop-blur-md border border-green-500/30 rounded-lg p-6 w-96">
        <h3 className="text-xl font-bold text-green-400 mb-4">
          Línea de Tiempo
        </h3>
        <p className="text-gray-400 text-center">
          Esperando datos de simulación...
        </p>
      </div>
    );
  }

  const maxInfected = Math.max(...timeline.map(e => e.infected));
  const maxDeaths = Math.max(...timeline.map(e => e.deaths));

  const getBarHeight = (value: number, max: number): string => {
    if (max === 0) return '0%';
    return `${(value / max) * 100}%`;
  };

  // Show last 50 days or all if less
  const displayTimeline = timeline.slice(Math.max(0, timeline.length - 50));

  return (
    <div className="absolute top-4 right-96 bg-black/80 backdrop-blur-md border border-green-500/30 rounded-lg p-6 w-96 shadow-2xl">
      <div className="mb-4">
        <h3 className="text-xl font-bold text-green-400 mb-2">
          Línea de Tiempo
        </h3>
        <p className="text-gray-400 text-sm">
          Últimos {displayTimeline.length} días
        </p>
      </div>

      {/* Chart Area */}
      <div className="relative h-48 mb-4 bg-gray-900/50 rounded-lg p-2">
        <div className="flex items-end justify-between h-full gap-px">
          {displayTimeline.map((entry, index) => (
            <div
              key={entry.day}
              className="flex-1 flex flex-col justify-end space-y-px"
              title={`Día ${entry.day}: ${entry.infected.toLocaleString()} infectados`}
            >
              {/* Infected bar */}
              <div
                className="bg-orange-500 rounded-sm transition-all duration-200 hover:bg-orange-400"
                style={{ height: getBarHeight(entry.infected, maxInfected) }}
              />
              {/* Deaths bar */}
              <div
                className="bg-red-500 rounded-sm transition-all duration-200 hover:bg-red-400"
                style={{ height: getBarHeight(entry.deaths, maxDeaths) }}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-orange-500 rounded"></div>
            <span className="text-gray-400">Infectados</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span className="text-gray-400">Fallecidos</span>
          </div>
        </div>
      </div>

      {/* Key Stats */}
      <div className="mt-4 pt-4 border-t border-gray-700 space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-400">Pico de Infección:</span>
          <span className="text-orange-400 font-bold">
            {maxInfected.toLocaleString()}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Total Fallecidos:</span>
          <span className="text-red-400 font-bold">
            {timeline[timeline.length - 1]?.deaths.toLocaleString() || 0}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">R Actual:</span>
          <span className={`font-bold ${
            timeline[timeline.length - 1]?.r_effective > 1.0 
              ? 'text-red-400' 
              : 'text-green-400'
          }`}>
            {timeline[timeline.length - 1]?.r_effective.toFixed(2) || '0.00'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default TimelineChart;
