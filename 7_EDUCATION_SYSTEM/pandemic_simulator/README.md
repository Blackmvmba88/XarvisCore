# 🦠 Pandemic Simulator: Sistema Educativo de Simulación de Pandemias

## 🎓 BlackMamba University - Módulo Educativo #2

> **"Entender las pandemias del pasado es la clave para prevenir las del futuro."**

---

## 🎯 Objetivo

Crear un simulador avanzado de propagación viral en tiempo real que enseña epidemiología, salud pública y toma de decisiones en crisis sanitarias. Los estudiantes aprenden mediante la experiencia directa de gestionar pandemias históricas y crear sus propias simulaciones.

---

## 📚 ¿Qué Aprenderás?

### Conceptos Epidemiológicos
- **Modelo SEIR**: Susceptible-Exposed-Infected-Recovered
- **R0 (Número Básico de Reproducción)**: ¿Qué tan contagiosa es una enfermedad?
- **R efectivo**: Cómo las intervenciones modifican la transmisión
- **Curva de Aplanamiento**: Importancia del timing en intervenciones
- **Tasa de Mortalidad vs Transmisibilidad**: El trade-off epidemiológico

### Salud Pública
- **Intervenciones no farmacéuticas**: Cuarentena, distanciamiento, mascarillas
- **Intervenciones farmacéuticas**: Vacunas y su desarrollo
- **Trade-offs económicos**: Salud vs economía (falso dilema)
- **Gestión de recursos**: Presupuesto limitado, decisiones difíciles
- **Comunicación de riesgos**: Transparencia y confianza pública

### Historia de las Pandemias
- **Peste Negra (1347)**: El origen de la cuarentena
- **Gripe Española (1918)**: Lecciones de la Primera Guerra Mundial
- **COVID-19 (2019)**: La pandemia moderna más documentada

---

## 🚀 Inicio Rápido

### Backend (Python)

```bash
# Navegar al directorio
cd 7_EDUCATION_SYSTEM/pandemic_simulator

# Ejecutar el motor de simulación
python3 pandemic_simulator_engine.py

# Ejecutar tests
python3 tests/test_pandemic_simulator.py
```

### Frontend (React/TypeScript)

```bash
# Navegar al frontend
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Compilar para producción
npm run build
```

---

## 📊 Arquitectura del Sistema

### Backend: Motor de Simulación SEIR

```python
from pandemic_simulator_engine import PandemicSimulatorEngine, Virus

# Crear motor
engine = PandemicSimulatorEngine()

# Obtener virus histórico
covid = engine.historical_pandemics["covid19"]["virus"]

# Simular con intervenciones
results = engine.simulate_spread(
    virus=covid,
    origin_country="China",
    days=365,
    interventions=[
        {"type": "lockdown", "start_day": 30},
        {"type": "masks", "start_day": 45},
        {"type": "vaccine", "start_day": 365, "coverage": 0.7}
    ]
)

print(f"Total infectados: {results['total_infected']:,}")
print(f"Total muertes: {results['total_deaths']:,}")
print(f"Día pico: {results['peak_day']}")
```

### Modelo SEIR

El modelo divide la población en 4 compartimentos:

1. **S (Susceptible)**: Población que puede infectarse
2. **E (Exposed)**: Expuestos al virus (incubación)
3. **I (Infected)**: Infectados activos (contagiosos)
4. **R (Recovered/Dead)**: Recuperados o fallecidos

**Ecuaciones simplificadas:**
```
Nuevas infecciones = I × R_eff / días_infecciosos
Nuevas muertes = I × tasa_mortalidad / días_infecciosos
Nuevos recuperados = I × (1 - tasa_mortalidad) / días_infecciosos
```

---

## 🎮 Desafíos Educativos

### 1. **Reescribe la Historia del COVID-19**
**Dificultad**: Experto  
**Objetivo**: Evitar 7 millones de muertes  
**Presupuesto**: $1 Trillón USD  

```bash
Escenario: Diciembre 2019, Wuhan, China
- Detectado: Nuevo coronavirus
- R0 inicial: 2.5
- Mortalidad: 2%

¿Qué harás?
```

**Intervenciones disponibles:**
- 🔒 Cuarentena: -60% R0, $10B/día
- 😷 Mascarillas: -50% R0, $0.5B/día
- ↔️ Distanciamiento: -30% R0, $2B/día
- 💉 Vacuna: -90% R0, $50B total (365 días)
- 🛂 Fronteras: -40% R0, $5B/día
- 🧪 Tests: -25% R0, $1B/día

### 2. **Crea tu Propio Virus**
**Dificultad**: Intermedio  
**Objetivo**: Diseñar y contener un virus personalizado

Ajusta parámetros:
- **R0**: 0.5 - 5.0
- **Mortalidad**: 0.1% - 80%
- **Transmisión**: Aérea, contacto, vector, agua
- **Incubación**: 1-14 días
- **Infeccioso**: 3-21 días

### 3. **La Peste Negra: Europa 1347**
**Dificultad**: Difícil  
**Objetivo**: Salvar Europa con tecnología medieval

**Limitaciones:**
- ❌ Sin antibióticos
- ❌ Sin vacunas
- ❌ Sin conocimiento de bacterias
- ✅ Solo cuarentena y aislamiento

**Contexto histórico:**
- Mortalidad real: 60%
- Muertes: 75 millones
- Duración: 6 años (1347-1353)

---

## 📁 Estructura del Proyecto

```
pandemic_simulator/
├── README.md                          # Este archivo
├── pandemic_simulator_engine.py       # Motor de simulación Python
├── data/
│   ├── historical_pandemics.json      # Datos de pandemias reales
│   ├── interventions.json             # Definiciones de intervenciones
│   └── world_population.json          # Datos de población mundial
├── challenges/
│   ├── scenario_covid_replay.json     # Desafío COVID-19
│   ├── scenario_custom_virus.json     # Desafío personalizado
│   └── scenario_black_death.json      # Desafío Peste Negra
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PandemicGlobe.tsx      # Visualización 3D
│   │   │   ├── StatsPanel.tsx         # Panel de estadísticas
│   │   │   ├── InterventionPanel.tsx  # Control de intervenciones
│   │   │   └── TimelineChart.tsx      # Gráfica temporal
│   │   └── App.tsx                     # Aplicación principal
│   └── package.json
└── tests/
    └── test_pandemic_simulator.py     # Suite de tests
```

---

## 🧪 API del Motor de Simulación

### Clase `PandemicSimulatorEngine`

#### Métodos Principales

**`__init__()`**
Inicializa el motor con pandemias históricas.

**`simulate_spread(virus, origin_country, days, interventions)`**
Simula la propagación de un virus durante X días.

**Parámetros:**
- `virus`: Objeto Virus con características
- `origin_country`: País de origen (string)
- `days`: Días a simular (int)
- `interventions`: Lista de intervenciones

**Retorna:**
```python
{
    "timeline": [
        {"day": 0, "infected": 100, "deaths": 0, "r_effective": 2.5},
        # ...
    ],
    "total_infected": 1000000,
    "total_deaths": 20000,
    "peak_day": 45
}
```

**`create_custom_virus(name, r0, mortality, transmission)`**
Crea un virus personalizado.

**`compare_pandemics(pandemic_ids)`**
Compara múltiples pandemias históricas.

**`get_intervention_recommendations(current_state)`**
IA recomienda intervenciones basadas en estado actual.

### Dataclass `Virus`

```python
@dataclass
class Virus:
    name: str
    r0: float              # 1.0 - 5.0
    mortality_rate: float  # 0.0 - 1.0
    incubation_days: int   # 1 - 14
    infectious_days: int   # 3 - 21
    transmission_type: str # 'airborne', 'contact', 'vector', 'water'
```

---

## 🎨 Frontend: Interfaz Interactiva

### Componentes React

#### `<PandemicGlobe />`
Visualización 3D del planeta con heat map de infección.

#### `<StatsPanel />`
Panel en tiempo real con:
- Día actual
- Susceptibles, Expuestos, Infectados, Recuperados, Muertes
- R efectivo
- Tasa de mortalidad
- Estado de la pandemia

#### `<InterventionPanel />`
Control de intervenciones:
- Lista de intervenciones disponibles
- Costo diario/total
- Efectividad
- Presupuesto restante
- Toggle on/off

#### `<TimelineChart />`
Gráfica de evolución:
- Línea de infectados (naranja)
- Línea de muertes (rojo)
- Línea de recuperados (verde)
- R efectivo (azul)

---

## 📖 Datos Históricos

### Peste Negra (1347-1353)
- **Patógeno**: Yersinia pestis (bacteria)
- **R0**: 3.0
- **Mortalidad**: 60%
- **Transmisión**: Vector (pulgas de ratas)
- **Muertes**: 75 millones
- **Lección clave**: Origen de la cuarentena de 40 días

### Gripe Española (1918-1920)
- **Patógeno**: Influenza A H1N1
- **R0**: 2.0
- **Mortalidad**: 10%
- **Transmisión**: Aérea (gotas respiratorias)
- **Muertes**: 50 millones
- **Lección clave**: Mascarillas funcionan, oleadas múltiples

### COVID-19 (2019-2023)
- **Patógeno**: SARS-CoV-2 (coronavirus)
- **R0**: 2.5
- **Mortalidad**: 2%
- **Transmisión**: Aérea (aerosoles)
- **Muertes**: 7 millones
- **Lección clave**: Vacunas rápidas posibles, cooperación global esencial

---

## 🧮 Fórmulas y Conceptos Clave

### R0 (Número Básico de Reproducción)
> Número promedio de personas que un infectado contagia en una población totalmente susceptible.

- **R0 < 1**: Pandemia se extingue
- **R0 = 1**: Endémica (estable)
- **R0 > 1**: Pandemia crece exponencialmente

### R efectivo (R_eff)
> R0 modificado por intervenciones y inmunidad poblacional.

```
R_eff = R0 × (1 - efectividad_intervenciones) × (susceptibles / población_total)
```

### Tasa de Ataque
> Proporción de población que se infecta durante la pandemia.

```
Tasa de Ataque = (Infectados + Recuperados + Muertes) / Población Total
```

### Inmunidad de Rebaño
> Proporción de población inmune necesaria para detener transmisión.

```
Umbral = 1 - (1 / R0)
```

Ejemplos:
- R0 = 2.0 → 50% inmunes
- R0 = 3.0 → 67% inmunes
- R0 = 5.0 → 80% inmunes

---

## 🎓 Objetivos de Aprendizaje

### Nivel 1: Básico
- [ ] Comprender qué es R0 y R efectivo
- [ ] Identificar tipos de transmisión
- [ ] Conocer intervenciones básicas
- [ ] Interpretar curvas epidémicas

### Nivel 2: Intermedio
- [ ] Calcular R efectivo con intervenciones
- [ ] Analizar trade-offs económicos
- [ ] Comparar pandemias históricas
- [ ] Diseñar estrategias de respuesta

### Nivel 3: Avanzado
- [ ] Optimizar timing de intervenciones
- [ ] Balancear presupuesto y vidas salvadas
- [ ] Predecir oleadas futuras
- [ ] Entender limitaciones de modelos

### Nivel 4: Experto
- [ ] Replicar respuesta COVID-19 mejorada
- [ ] Crear virus personalizados y contenerlos
- [ ] Gestionar crisis con información limitada
- [ ] Comunicar decisiones de salud pública

---

## 🔬 Tests y Validación

### Ejecutar Tests

```bash
cd 7_EDUCATION_SYSTEM/pandemic_simulator
python3 tests/test_pandemic_simulator.py
```

### Coverage de Tests
- ✅ Carga de pandemias históricas
- ✅ Creación de virus personalizados
- ✅ Simulación básica sin intervenciones
- ✅ Aplicación de intervenciones individuales
- ✅ Intervenciones múltiples (stacking)
- ✅ Timing de intervenciones
- ✅ Vacunas con diferentes coberturas
- ✅ Comparación de pandemias
- ✅ Cálculo de día pico
- ✅ Recomendaciones de IA
- ✅ Reducción de muertes con intervenciones

---

## 🌟 Características Avanzadas

### IA de Recomendaciones
El sistema analiza el estado actual y sugiere intervenciones:

```python
state = {
    "r_effective": 2.5,
    "infected": 1000000,
    "deaths": 20000
}

recommendations = engine.get_intervention_recommendations(state)
# ['lockdown', 'masks', 'social_distancing', 'vaccine']
```

### Comparación de Pandemias
Analiza múltiples pandemias simultáneamente:

```python
comparison = engine.compare_pandemics([
    "black_death",
    "spanish_flu",
    "covid19"
])
```

### Simulación Acelerada
Simula años en segundos con control de velocidad (1x, 2x, 5x, 10x).

---

## 🎯 Casos de Uso Educativos

### Caso 1: Estudiante de Medicina
**Objetivo**: Entender epidemiología básica  
**Actividad**: Simular COVID-19 con diferentes intervenciones  
**Tiempo**: 30 minutos  

### Caso 2: Estudiante de Salud Pública
**Objetivo**: Analizar trade-offs económicos  
**Actividad**: Optimizar respuesta con presupuesto limitado  
**Tiempo**: 1 hora  

### Caso 3: Historiador
**Objetivo**: Comprender impacto de pandemias históricas  
**Actividad**: Comparar Peste Negra, Gripe Española y COVID-19  
**Tiempo**: 45 minutos  

### Caso 4: Matemático/Científico de Datos
**Objetivo**: Entender modelos SEIR  
**Actividad**: Crear virus personalizados con parámetros específicos  
**Tiempo**: 2 horas  

---

## 🛠️ Dependencias

### Python (Backend)
- Python 3.8+
- Dataclasses (built-in)
- JSON (built-in)

### JavaScript/TypeScript (Frontend)
- React 18.2+
- TypeScript 5.0+
- Three.js 0.160+ (visualización 3D)
- Recharts 2.10+ (gráficas)
- Tailwind CSS 3.4+ (estilos)
- Vite 5.0+ (bundler)

---

## 📈 Roadmap Futuro

### Fase 1 ✅ (Actual)
- [x] Motor SEIR funcional
- [x] 3 pandemias históricas
- [x] 8 intervenciones
- [x] Frontend interactivo
- [x] 3 desafíos educativos

### Fase 2 🚧 (Próximo)
- [ ] Simulación por países
- [ ] Modelos de movilidad
- [ ] Variantes virales
- [ ] Sistema de logros
- [ ] Leaderboard educativo

### Fase 3 📋 (Futuro)
- [ ] Integración con datos reales (API OMS)
- [ ] Modo multijugador (cooperativo)
- [ ] Generador de reportes PDF
- [ ] Integración con BMU LMS
- [ ] Certificación al completar desafíos

---

## 👨‍💻 Contribuir

Este es un proyecto educativo de código abierto. Contribuciones bienvenidas:

1. **Nuevas pandemias históricas**: SARS, MERS, Ébola, etc.
2. **Desafíos adicionales**: Escenarios creativos
3. **Mejoras al modelo**: Más realismo epidemiológico
4. **Visualizaciones**: Mapas interactivos, gráficas avanzadas
5. **Traducciones**: Inglés, francés, portugués, etc.

---

## 📞 Contacto y Soporte

**Arquitecto**: Iyari Cancino Gomez  
**Institución**: BlackMamba University  
**LinkedIn**: https://www.linkedin.com/in/iyari-c/  
**GitHub**: https://github.com/Blackmvmba88/XarvisCore  

---

## 📄 Licencia

MIT License - Uso educativo libre

---

## 🏆 Créditos

**Desarrollado por**: BlackMamba University Education Team  
**Inspirado en**: Johns Hopkins COVID-19 Dashboard, Our World in Data  
**Modelos basados en**: SIR/SEIR epidemiológicos clásicos  

---

## 🦅 Filosofía BMU

> "Paga por una si quieres lujo; estudia tres y el Rey te las paga todas"

Este simulador es parte del compromiso de BMU con la democratización del conocimiento. Gratis, open-source, y diseñado para enseñar conceptos que salvan vidas.

---

**🦠 "Entender las pandemias del pasado es la clave para prevenir las del futuro."**

— BMU Pandemic Simulator Team
