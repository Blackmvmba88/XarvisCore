/**
 * StatsPanel Component
 * Displays real-time pandemic statistics
 * BlackMamba University - Pandemic Simulator
 */

import React from 'react';

interface PandemicStats {
  day: number;
  susceptible: number;
  exposed: number;
  infected: number;
  recovered: number;
  deaths: number;
  r_effective: number;
}

interface StatsPanelProps {
  stats: PandemicStats;
}

interface StatRowProps {
  label: string;
  value: string | number;
  color: 'orange' | 'green' | 'red' | 'blue' | 'yellow' | 'gray';
}

function StatRow({ label, value, color }: StatRowProps) {
  const colorClasses = {
    orange: 'text-orange-500',
    green: 'text-green-500',
    red: 'text-red-500',
    blue: 'text-blue-500',
    yellow: 'text-yellow-500',
    gray: 'text-gray-400'
  };

  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-700">
      <span className="text-gray-300 font-medium">{label}</span>
      <span className={`text-xl font-bold ${colorClasses[color]}`}>
        {value}
      </span>
    </div>
  );
}

export function StatsPanel({ stats }: StatsPanelProps) {
  const formatNumber = (num: number): string => {
    return num.toLocaleString('es-MX');
  };

  const calculatePercentage = (value: number, total: number): string => {
    if (total === 0) return '0.0';
    return ((value / total) * 100).toFixed(2);
  };

  const totalPopulation = 8000000000;

  return (
    <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-md border border-green-500/30 rounded-lg p-6 w-80 shadow-2xl">
      <div className="mb-4">
        <h2 className="text-3xl font-bold text-green-400 mb-1">
          Día {stats.day}
        </h2>
        <p className="text-gray-400 text-sm">Simulación en Tiempo Real</p>
      </div>

      <div className="space-y-2">
        <StatRow 
          label="Susceptibles" 
          value={formatNumber(stats.susceptible)}
          color="gray"
        />
        
        <StatRow 
          label="Expuestos" 
          value={formatNumber(stats.exposed)}
          color="yellow"
        />
        
        <StatRow 
          label="Infectados Activos" 
          value={formatNumber(stats.infected)}
          color="orange"
        />
        
        <StatRow 
          label="Recuperados" 
          value={formatNumber(stats.recovered)}
          color="green"
        />
        
        <StatRow 
          label="Fallecidos" 
          value={formatNumber(stats.deaths)}
          color="red"
        />
        
        <div className="pt-4 border-t border-gray-600 mt-4">
          <StatRow 
            label="R Efectivo" 
            value={stats.r_effective.toFixed(2)}
            color={stats.r_effective > 1.0 ? 'red' : 'green'}
          />
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="text-xs text-gray-400 space-y-1">
          <div className="flex justify-between">
            <span>Tasa de Mortalidad:</span>
            <span className="text-red-400">
              {calculatePercentage(stats.deaths, stats.deaths + stats.recovered + stats.infected)}%
            </span>
          </div>
          <div className="flex justify-between">
            <span>Población Afectada:</span>
            <span className="text-orange-400">
              {calculatePercentage(stats.infected + stats.recovered + stats.deaths, totalPopulation)}%
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 text-center">
        {stats.r_effective > 1.0 ? (
          <div className="bg-red-900/30 border border-red-500/50 rounded px-3 py-2">
            <p className="text-red-400 text-sm font-semibold">
              ⚠️ Pandemia en Crecimiento
            </p>
          </div>
        ) : (
          <div className="bg-green-900/30 border border-green-500/50 rounded px-3 py-2">
            <p className="text-green-400 text-sm font-semibold">
              ✓ Pandemia Controlada
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default StatsPanel;
