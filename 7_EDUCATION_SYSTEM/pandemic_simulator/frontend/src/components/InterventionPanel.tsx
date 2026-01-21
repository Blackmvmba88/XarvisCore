/**
 * InterventionPanel Component
 * Controls for pandemic interventions
 * BlackMamba University - Pandemic Simulator
 */

import React, { useState } from 'react';

interface Intervention {
  id: string;
  name: string;
  icon: string;
  cost: number;
  effectiveness: string;
  description: string;
  active: boolean;
}

interface InterventionPanelProps {
  budget: number;
  onInterventionToggle: (interventionId: string) => void;
}

export function InterventionPanel({ budget, onInterventionToggle }: InterventionPanelProps) {
  const [activeInterventions, setActiveInterventions] = useState<Set<string>>(new Set());
  
  const interventions: Intervention[] = [
    {
      id: 'lockdown',
      name: 'Cuarentena General',
      icon: '🔒',
      cost: 10.0,
      effectiveness: 'Alta',
      description: 'Cierre total de actividades no esenciales',
      active: false
    },
    {
      id: 'masks',
      name: 'Mascarillas',
      icon: '😷',
      cost: 0.5,
      effectiveness: 'Media',
      description: 'Uso obligatorio de mascarillas',
      active: false
    },
    {
      id: 'social_distancing',
      name: 'Distanciamiento',
      icon: '↔️',
      cost: 2.0,
      effectiveness: 'Media',
      description: 'Mantener 2m de distancia',
      active: false
    },
    {
      id: 'vaccine',
      name: 'Vacuna',
      icon: '💉',
      cost: 50.0,
      effectiveness: 'Muy Alta',
      description: 'Vacunación masiva (365 días)',
      active: false
    },
    {
      id: 'border_closure',
      name: 'Cerrar Fronteras',
      icon: '🛂',
      cost: 5.0,
      effectiveness: 'Media',
      description: 'Cierre de fronteras internacionales',
      active: false
    },
    {
      id: 'testing',
      name: 'Tests Masivos',
      icon: '🧪',
      cost: 1.0,
      effectiveness: 'Media',
      description: 'Pruebas y rastreo de contactos',
      active: false
    }
  ];

  const toggleIntervention = (interventionId: string) => {
    const newActive = new Set(activeInterventions);
    if (newActive.has(interventionId)) {
      newActive.delete(interventionId);
    } else {
      newActive.add(interventionId);
    }
    setActiveInterventions(newActive);
    onInterventionToggle(interventionId);
  };

  const isActive = (id: string) => activeInterventions.has(id);

  const getTotalCost = () => {
    return interventions
      .filter(i => activeInterventions.has(i.id))
      .reduce((sum, i) => sum + i.cost, 0);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(amount * 1000000000); // Convert billions to actual amount
  };

  return (
    <div className="absolute bottom-4 right-4 bg-black/80 backdrop-blur-md border border-green-500/30 rounded-lg p-6 w-96 shadow-2xl">
      <div className="mb-4">
        <h3 className="text-2xl font-bold text-green-400 mb-2">
          Intervenciones Sanitarias
        </h3>
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Presupuesto:</span>
          <span className="text-green-400 font-bold">{formatCurrency(budget)}</span>
        </div>
        <div className="flex justify-between text-sm mt-1">
          <span className="text-gray-400">Costo Diario:</span>
          <span className={getTotalCost() > budget ? 'text-red-400' : 'text-orange-400'}>
            ${getTotalCost()}B/día
          </span>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {interventions.map(intervention => (
          <button
            key={intervention.id}
            onClick={() => toggleIntervention(intervention.id)}
            className={`
              w-full text-left p-4 rounded-lg border transition-all duration-200
              ${isActive(intervention.id)
                ? 'bg-green-900/30 border-green-500 shadow-lg shadow-green-500/20'
                : 'bg-gray-900/50 border-gray-700 hover:border-gray-500'
              }
            `}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-3xl">{intervention.icon}</span>
                <div>
                  <h4 className={`font-semibold ${
                    isActive(intervention.id) ? 'text-green-400' : 'text-gray-300'
                  }`}>
                    {intervention.name}
                  </h4>
                  <p className="text-xs text-gray-400 mt-1">
                    {intervention.description}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-sm font-bold ${
                  isActive(intervention.id) ? 'text-green-400' : 'text-gray-400'
                }`}>
                  ${intervention.cost}B
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {intervention.effectiveness}
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Intervenciones Activas:</span>
          <span className="text-green-400 font-bold">{activeInterventions.size}</span>
        </div>
      </div>

      {getTotalCost() > budget && (
        <div className="mt-3 bg-red-900/30 border border-red-500/50 rounded px-3 py-2">
          <p className="text-red-400 text-xs font-semibold text-center">
            ⚠️ Presupuesto Excedido
          </p>
        </div>
      )}
    </div>
  );
}

export default InterventionPanel;
