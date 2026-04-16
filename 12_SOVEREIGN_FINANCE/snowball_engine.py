
import datetime

class SnowballInvestor:
    def __init__(self, initial_capital_mxn=2000):
        self.capital = initial_capital_mxn
        self.currency = "MXN"
        self.history = []
        self.strategy = "Apuesta Segura / Micromovimientos Legales"
        
    def record_movement(self, amount, description, risk_level="Bajo"):
        """
        Registra un micromovimiento o inversión segura.
        """
        self.capital += amount
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "amount": amount,
            "description": description,
            "risk_level": risk_level,
            "current_balance": self.capital
        }
        self.history.append(entry)
        return {"status": "Escalado", "new_balance": self.capital}

    def predict_growth(self, months, monthly_yield_rate=0.01):
        """
        Proyección simple del efecto bola de nieve.
        """
        projected = self.capital
        for _ in range(months):
            projected *= (1 + monthly_yield_rate)
        return {
            "periodo_meses": months,
            "capital_inicial": self.capital,
            "proyeccion_final": round(projected, 2),
            "incremento": round(projected - self.capital, 2)
        }

    def get_sovereign_advice(self):
        return {
            "filosofia": "Dios nos hizo inteligentes para no necesitar lo ilegal.",
            "metodo": "Micropagos constantes + Reinterversión = Bola de Nieve.",
            "estado": "Cimentando independencia financiera."
        }

# Instancia del motor financiero
snowball = SnowballInvestor()
