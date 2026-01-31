
import csv
import sys
import os
import json
from pathlib import Path
from unittest.mock import MagicMock

# MOCK de Flask para evitar que el import se cuelgue o requiera dependencias pesadas
sys.modules["flask"] = MagicMock()
sys.modules["flask_cors"] = MagicMock()

# Agregar el directorio actual al path
sys.path.append(os.path.abspath("/Users/blackmamba/Desktop/XarvisCore/12_SOVEREIGN_FINANCE"))

try:
    from bull_market_intelligence import NashEquilibriumAnalyzer
except ImportError as e:
    print(f"❌ Error importando el analizador: {e}")
    sys.exit(1)

def run_validation():
    print("🧪 INICIANDO VALIDACIÓN DE ESTRATEGIAS NASH SOBERANAS")
    print("-" * 50)
    
    analyzer = NashEquilibriumAnalyzer()
    sim_dir = Path("/Users/blackmamba/Desktop/XarvisCore/12_SOVEREIGN_FINANCE/simulations")
    
    if not sim_dir.exists():
        print("❌ No se encontraron simulaciones. Ejecuta virtual_market_lab.py primero.")
        return

    results = []
    
    # Lista de archivos a procesar (ordenada para consistencia)
    sim_files = sorted(list(sim_dir.glob("*.csv")))
    
    for sim_file in sim_files:
        print(f"\n📂 Analizando escenario: {sim_file.name}")
        
        # Leer CSV sin pandas
        asset_data = []
        try:
            with open(sim_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed_row = {
                        'Date': row['Date'],
                        'Close': float(row['Close'])
                    }
                    asset_data.append(processed_row)
        except Exception as e:
            print(f"   ❌ Error leyendo CSV: {e}")
            continue
        
        # Ejecutar análisis de Nash
        try:
            nash_result = analyzer.calculate_nash_equilibrium(asset_data)
        except Exception as e:
            print(f"   ❌ Error en cálculo de Nash: {e}")
            continue
        
        if nash_result:
            scenario_name = sim_file.stem
            strategy = nash_result['equilibrium_strategy']
            confidence = nash_result['confidence']
            expected_return = nash_result['expected_return']
            
            # Validación de "Ground Truth"
            is_valid = False
            if "BULL" in scenario_name and strategy == "COMPRAR": is_valid = True
            elif "BEAR" in scenario_name and strategy == "VENDER": is_valid = True
            elif "SIDEWAYS" in scenario_name and strategy == "MANTENER": is_valid = True
            elif "CRASH" in scenario_name and strategy == "VENDER": is_valid = True
            
            status = "✅ EXITOSO" if is_valid else "⚠️ DESVIADO"
            
            print(f"   {status}")
            print(f"   Estrategia: {strategy}")
            print(f"   Confianza: {confidence}%")
            print(f"   Insight: {nash_result['nash_insight']}")
            
            results.append({
                "scenario": scenario_name,
                "valid": is_valid
            })
        else:
            print(f"   ❌ Fallo en el análisis de {sim_file.name}")

    # Reporte Final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE COMPORTAMIENTO SOBERANO")
    total = len(results)
    successes = sum(1 for r in results if r['valid'])
    accuracy = (successes / total * 100) if total > 0 else 0
    
    print(f"Exactitud de Predicción Nash: {accuracy:.1f}%")
    if accuracy >= 100:
        print("🏆 ESTADO: SISTEMA ROBUSTO Y LISTO PARA OPERACIONES REALES")
    elif accuracy >= 75:
        print("⚖️ ESTADO: SISTEMA OPERATIVO (Requiere ajustes menores)")
    else:
        print("🔧 ESTADO: REQUIERE AJUSTE DE SENSIBILIDAD")
    print("=" * 50)

if __name__ == "__main__":
    run_validation()
