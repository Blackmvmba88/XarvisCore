
import random
import csv
import os
from datetime import datetime, timedelta

class VirtualMarketLab:
    """
    Laboratorio Virtual Soberano (Dependency-Free).
    Genera datos sintéticos sin necesidad de pandas/numpy.
    """
    def __init__(self, output_dir="/Users/blackmamba/Desktop/XarvisCore/12_SOVEREIGN_FINANCE/simulations"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_scenario(self, name, days=100, trend="sideways", volatility=0.02, has_bluff=False):
        """
        Genera un CSV de precios simulados usando random de Python.
        """
        random.seed(42)
        dates = [datetime.now() - timedelta(days=x) for x in range(days)]
        dates.reverse()

        # Determinar media de retorno diario (Ajustado para Detección)
        if trend == "bull":
            mu = 0.008  # ~0.8% diario
        elif trend == "bear":
            mu = -0.008 # ~-0.8% diario
        else:
            mu = 0.000

        price = 100.0
        rows = []
        
        for i in range(days):
            # Retorno aleatorio (simulando distribución normal simple)
            r = random.gauss(mu, volatility)
            
            # Inyectar Bluff al final del periodo para detección inmediata
            if has_bluff and (days - 10 <= i <= days - 6):
                r += 0.04
            if has_bluff and (days - 5 <= i <= days):
                r -= 0.08 # Caída más fuerte para CRASH

            price *= (1 + r)
            
            row = {
                "Date": dates[i].strftime("%Y-%m-%d"),
                "Open": round(price * (1 - random.uniform(0.005, 0.01)), 2),
                "High": round(price * (1 + random.uniform(0.005, 0.01)), 2),
                "Low": round(price * (1 - random.uniform(0.01, 0.015)), 2),
                "Close": round(price, 2),
                "Volume": random.randint(1000, 10000)
            }
            rows.append(row)

        output_path = os.path.join(self.output_dir, f"{name}.csv")
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "Open", "High", "Low", "Close", "Volume"])
            writer.writeheader()
            writer.writerows(rows)
            
        return output_path

    def run_full_testing_suite(self):
        print("🚀 Iniciando Suite de Pruebas Virtuales (Modo Soberano)...")
        scenarios = [
            {"name": "TSLA_SIM_BULL", "trend": "bull", "vol": 0.02, "bluff": False},
            {"name": "AAPL_SIM_BEAR", "trend": "bear", "vol": 0.015, "bluff": False},
            {"name": "BTC_SIM_CRASH", "trend": "bear", "vol": 0.06, "bluff": True},
            {"name": "GRR_SIM_SIDEWAYS", "trend": "sideways", "vol": 0.01, "bluff": False}
        ]
        
        for s in scenarios:
            path = self.generate_scenario(s["name"], trend=s["trend"], volatility=s["vol"], has_bluff=s["bluff"])
            print(f"✅ Escenario '{s['name']}' generado.")
        
if __name__ == "__main__":
    lab = VirtualMarketLab()
    lab.run_full_testing_suite()
