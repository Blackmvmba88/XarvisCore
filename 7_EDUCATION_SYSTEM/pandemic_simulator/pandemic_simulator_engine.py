"""
🦠 Pandemic Simulator Engine
Sistema Educativo de Simulación de Pandemias para BlackMamba University

Este motor simula la propagación de enfermedades infecciosas usando el modelo SEIR
(Susceptible-Exposed-Infected-Recovered) y permite a los estudiantes comprender
epidemiología, salud pública y toma de decisiones en crisis sanitarias.

Author: BlackMamba University
License: MIT
"""

from dataclasses import dataclass
from typing import List, Dict
import json


@dataclass
class Virus:
    """Definición de un virus simulado"""
    name: str
    r0: float  # Número de reproducción básico (contagiosidad)
    mortality_rate: float  # Tasa de mortalidad (0.0 a 1.0)
    incubation_days: int  # Período de incubación
    infectious_days: int  # Días que es contagioso
    transmission_type: str  # 'airborne', 'contact', 'vector', 'water'


class PandemicSimulatorEngine:
    """Motor de simulación de pandemias"""
    
    def __init__(self):
        self.load_historical_pandemics()
        self.world_population = 8000000000
        self.countries = {}
    
    def load_historical_pandemics(self):
        """Carga datos históricos de pandemias reales"""
        self.historical_pandemics = {
            "black_death": {
                "name": "Peste Negra",
                "year": 1347,
                "virus": Virus(
                    name="Yersinia pestis",
                    r0=3.0,
                    mortality_rate=0.60,
                    incubation_days=2,
                    infectious_days=5,
                    transmission_type="vector"
                ),
                "deaths": 75000000,
                "origin": {"country": "China", "lat": 35.0, "lng": 105.0}
            },
            "spanish_flu": {
                "name": "Gripe Española",
                "year": 1918,
                "virus": Virus(
                    name="H1N1",
                    r0=2.0,
                    mortality_rate=0.10,
                    incubation_days=2,
                    infectious_days=7,
                    transmission_type="airborne"
                ),
                "deaths": 50000000,
                "origin": {"country": "USA", "lat": 37.0, "lng": -95.0}
            },
            "covid19": {
                "name": "COVID-19",
                "year": 2019,
                "virus": Virus(
                    name="SARS-CoV-2",
                    r0=2.5,
                    mortality_rate=0.02,
                    incubation_days=5,
                    infectious_days=10,
                    transmission_type="airborne"
                ),
                "deaths": 7000000,
                "origin": {"country": "China", "lat": 30.5928, "lng": 114.3055}
            }
        }
    
    def load_country_data(self):
        """Carga datos de población por país (simplificado)"""
        return {
            "China": {"population": 1400000000, "lat": 35.0, "lng": 105.0},
            "USA": {"population": 330000000, "lat": 37.0, "lng": -95.0},
            "Mexico": {"population": 130000000, "lat": 23.6345, "lng": -102.5528},
            "World": {"population": 8000000000, "lat": 0.0, "lng": 0.0}
        }
    
    def create_custom_virus(self, name: str, r0: float, mortality: float, 
                           transmission: str) -> Virus:
        """Permite al estudiante crear su propio virus"""
        return Virus(
            name=name,
            r0=r0,
            mortality_rate=mortality,
            incubation_days=5,
            infectious_days=10,
            transmission_type=transmission
        )
    
    def simulate_spread(self, virus: Virus, origin_country: str, 
                       days: int, interventions: List[Dict]) -> Dict:
        """
        Simula la propagación del virus durante X días
        
        Args:
            virus: Objeto Virus con características de la enfermedad
            origin_country: País de origen de la pandemia
            days: Número de días a simular
            interventions: Lista de intervenciones sanitarias
            
        Returns:
            Diccionario con timeline, estadísticas y resultados
        """
        # Modelo SEIR (Susceptible-Exposed-Infected-Recovered)
        results = {
            "timeline": [],
            "by_country": {},
            "interventions_applied": interventions
        }
        
        # Simulación día por día
        infected = 100  # Casos iniciales
        susceptible = self.world_population
        exposed = 0
        recovered = 0
        deaths = 0
        
        for day in range(days):
            # Aplicar intervenciones
            effective_r0 = self.apply_interventions(virus.r0, day, interventions)
            
            # Calcular nuevos casos usando modelo SEIR simplificado
            if infected > 0:
                new_infections = min(
                    infected * effective_r0 / virus.infectious_days,
                    susceptible
                )
                new_deaths = infected * virus.mortality_rate / virus.infectious_days
                new_recovered = infected * (1 - virus.mortality_rate) / virus.infectious_days
            else:
                new_infections = 0
                new_deaths = 0
                new_recovered = 0
            
            # Actualizar números
            exposed += new_infections
            infected = max(0, infected + new_infections - new_deaths - new_recovered)
            deaths += new_deaths
            recovered += new_recovered
            susceptible = max(0, susceptible - new_infections)
            
            results["timeline"].append({
                "day": day,
                "susceptible": int(susceptible),
                "exposed": int(exposed),
                "infected": int(infected),
                "recovered": int(recovered),
                "deaths": int(deaths),
                "r_effective": effective_r0
            })
        
        results["total_infected"] = int(infected + recovered + deaths)
        results["total_deaths"] = int(deaths)
        results["total_recovered"] = int(recovered)
        results["peak_day"] = self.find_peak_day(results["timeline"])
        
        return results
    
    def apply_interventions(self, base_r0: float, current_day: int, 
                           interventions: List[Dict]) -> float:
        """
        Aplica intervenciones sanitarias que reducen R0
        
        Args:
            base_r0: R0 base del virus sin intervenciones
            current_day: Día actual de la simulación
            interventions: Lista de intervenciones activas
            
        Returns:
            R0 efectivo después de aplicar intervenciones
        """
        effective_r0 = base_r0
        
        for intervention in interventions:
            if current_day >= intervention.get("start_day", 0):
                intervention_type = intervention.get("type", "")
                
                if intervention_type == "lockdown":
                    effective_r0 *= 0.4  # Reduce 60%
                elif intervention_type == "social_distancing":
                    effective_r0 *= 0.7  # Reduce 30%
                elif intervention_type == "masks":
                    effective_r0 *= 0.5  # Reduce 50%
                elif intervention_type == "vaccine":
                    coverage = intervention.get("coverage", 0.7)
                    effective_r0 *= (1 - coverage * 0.9)  # 90% efectividad
                elif intervention_type == "border_closure":
                    effective_r0 *= 0.6  # Reduce 40%
                elif intervention_type == "testing":
                    effective_r0 *= 0.75  # Reduce 25%
        
        return max(effective_r0, 0.1)  # Mínimo R0
    
    def find_peak_day(self, timeline: List[Dict]) -> int:
        """Encuentra el día con más casos activos"""
        max_infected = 0
        peak_day = 0
        for entry in timeline:
            if entry["infected"] > max_infected:
                max_infected = entry["infected"]
                peak_day = entry["day"]
        return peak_day
    
    def compare_pandemics(self, pandemic_ids: List[str]) -> Dict:
        """
        Compara múltiples pandemias históricas
        
        Args:
            pandemic_ids: Lista de IDs de pandemias a comparar
            
        Returns:
            Diccionario con datos comparativos
        """
        comparison = {}
        for pid in pandemic_ids:
            if pid in self.historical_pandemics:
                p = self.historical_pandemics[pid]
                comparison[pid] = {
                    "name": p["name"],
                    "year": p["year"],
                    "r0": p["virus"].r0,
                    "mortality": p["virus"].mortality_rate,
                    "deaths": p["deaths"],
                    "transmission": p["virus"].transmission_type
                }
        return comparison
    
    def get_intervention_recommendations(self, current_state: Dict) -> List[str]:
        """
        IA recomienda intervenciones según estado actual
        
        Args:
            current_state: Estado actual de la pandemia
            
        Returns:
            Lista de intervenciones recomendadas
        """
        recommendations = []
        
        r_effective = current_state.get("r_effective", 2.0)
        infected = current_state.get("infected", 0)
        deaths = current_state.get("deaths", 0)
        
        if r_effective > 1.5:
            recommendations.append("lockdown")
        if infected > 1000000:
            recommendations.append("emergency_healthcare")
        if r_effective > 1.0:
            recommendations.append("masks")
            recommendations.append("social_distancing")
        if deaths > 10000:
            recommendations.append("vaccine")
        if r_effective > 2.0:
            recommendations.append("border_closure")
        
        return recommendations
    
    def get_pandemic_data(self, pandemic_id: str) -> Dict:
        """Obtiene datos completos de una pandemia histórica"""
        if pandemic_id in self.historical_pandemics:
            return self.historical_pandemics[pandemic_id]
        return None


def save_pandemic_data():
    """Guarda datos de pandemias en JSON (utilidad para exportar)"""
    engine = PandemicSimulatorEngine()
    
    # Convertir datos a formato serializable
    data = {}
    for key, pandemic in engine.historical_pandemics.items():
        data[key] = {
            "name": pandemic["name"],
            "year": pandemic["year"],
            "virus": {
                "name": pandemic["virus"].name,
                "r0": pandemic["virus"].r0,
                "mortality_rate": pandemic["virus"].mortality_rate,
                "incubation_days": pandemic["virus"].incubation_days,
                "infectious_days": pandemic["virus"].infectious_days,
                "transmission_type": pandemic["virus"].transmission_type
            },
            "deaths": pandemic["deaths"],
            "origin": pandemic["origin"]
        }
    
    return data


# Main execution para pruebas rápidas
if __name__ == "__main__":
    print("🦠 Pandemic Simulator Engine - BMU")
    print("=" * 50)
    
    # Crear motor
    engine = PandemicSimulatorEngine()
    
    # Simular COVID-19 sin intervenciones
    covid_virus = engine.historical_pandemics["covid19"]["virus"]
    print(f"\n📊 Simulando {covid_virus.name}...")
    print(f"   R0: {covid_virus.r0}")
    print(f"   Mortalidad: {covid_virus.mortality_rate * 100}%")
    
    results = engine.simulate_spread(
        virus=covid_virus,
        origin_country="China",
        days=100,
        interventions=[]
    )
    
    print(f"\n🎯 Resultados después de 100 días:")
    print(f"   Total Infectados: {results['total_infected']:,}")
    print(f"   Total Muertes: {results['total_deaths']:,}")
    print(f"   Día Pico: {results['peak_day']}")
    
    # Comparar pandemias
    print(f"\n📈 Comparación de Pandemias Históricas:")
    comparison = engine.compare_pandemics(["black_death", "spanish_flu", "covid19"])
    for pid, data in comparison.items():
        print(f"   {data['name']}: R0={data['r0']}, Mortalidad={data['mortality']*100}%")
