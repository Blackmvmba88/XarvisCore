
import os
import json
from datetime import datetime

class AlexandriaEngine:
    def __init__(self):
        self.library_path = "/Users/blackmamba/Desktop/XarvisCore/6_WORLD_DATA/library_index.json"
        self.metadata_dir = "/Users/blackmamba/Desktop/XarvisCore/7_EDUCATION_SYSTEM/metadata"
        
        if not os.path.exists(self.metadata_dir):
            os.makedirs(self.metadata_dir)
            
    def register_knowledge_resource(self, title, category, source_url, description):
        """
        Registra un nuevo recurso educativo en la Biblioteca de Alejandría 2.0.
        """
        resource = {
            "id": f"KNOW-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "category": category,
            "source_url": source_url,
            "description": description,
            "integrity_hash": "pending_validation",
            "added_at": datetime.now().isoformat()
        }
        
        # Simulación de persistencia en índice
        try:
            index = []
            if os.path.exists(self.library_path):
                with open(self.library_path, 'r') as f:
                    index = json.load(f)
            
            index.append(resource)
            with open(self.library_path, 'w') as f:
                json.dump(index, f, indent=4)
                
            return {"status": "success", "resource_id": resource["id"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_knowledge(self, query):
        """
        Busca en el índice de conocimiento democratizado.
        """
        if not os.path.exists(self.library_path):
            return []
            
        with open(self.library_path, 'r') as f:
            index = json.load(f)
            
        return [r for r in index if query.lower() in r["title"].lower() or query.lower() in r["description"].lower()]

# Instancia del motor
alexandria = AlexandriaEngine()
