
import json
import os
from datetime import datetime

class ZeroHungerProtocol:
    def __init__(self):
        self.registry_path = "/Users/blackmamba/Desktop/XarvisCore/6_WORLD_DATA/resource_registry.json"
        
    def map_surplus(self, location, resource_type, quantity, expiry_date=None):
        """
        Registra un excedente de recursos vitales (alimento, agua, suministros).
        """
        entry = {
            "entry_id": f"VITAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "location": location,
            "resource_type": resource_type,
            "quantity": quantity,
            "expiry_date": expiry_date,
            "status": "available",
            "recorded_at": datetime.now().isoformat()
        }
        
        try:
            registry = []
            if os.path.exists(self.registry_path):
                with open(self.registry_path, 'r') as f:
                    registry = json.load(f)
            
            registry.append(entry)
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=4)
                
            return {"status": "success", "entry_id": entry["entry_id"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def calculate_distribution_routes(self):
        """
        Lógica preliminar para optimizar la entrega de recursos vitales.
        """
        # Aquí se integrará en el futuro el análisis de proximidad y necesidad
        return "Calculando rutas óptimas basándose en el principio de Hambre Cero..."

# Instancia del protocolo
zero_hunger = ZeroHungerProtocol()
