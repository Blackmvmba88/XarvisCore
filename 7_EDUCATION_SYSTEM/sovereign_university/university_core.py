
import datetime

class BlackMambaUniversity:
    def __init__(self):
        self.name = "BlackMamba University (BMU)"
        self.philosophy = "Audacia, Multidisciplinariedad y Conocimiento Real"
        self.nodes = {}
        self.cert_reference = "https://www.linkedin.com/in/iyari-c/details/certifications/"
        
    def deploy_node(self, state, city):
        """
        Despliega un nodo universitario en una ubicación específica.
        Todos los nodos son parte de la misma red neuronal de conocimiento.
        """
        node_id = f"XSU-{state[:3].upper()}-{city[:3].upper()}"
        self.nodes[node_id] = {
            "state": state,
            "city": city,
            "status": "Online",
            "tech_level": "Ultra-Evolving",
            "deployed_at": datetime.datetime.now().isoformat()
        }
        return {"status": "Node Deployed", "node_id": node_id}

    def calculate_tuition(self, degree_count):
        """
        Lógica de la Oportunidad BMU: 
        1 licenciatura = Costo Premium (Lo mejor de lo mejor).
        3+ licenciaturas = Beca Total (Financiado por el Rey).
        Se premia la audacia y el hambre de conocimiento.
        """
        if degree_count >= 3:
            return {
                "costo": 0,
                "mensaje": "Beca de Audacia BMU Activada. El Rey financia tu conocimiento multidisciplinario.",
                "estatus": "Soberano"
            }
        return {
            "costo": "Premium",
            "mensaje": "Inversión en excelencia. Acceso a lo mejor de lo mejor.",
            "estatus": "Privilegiado"
        }

# Instancia del núcleo de BlackMamba University
bmu = BlackMambaUniversity()
