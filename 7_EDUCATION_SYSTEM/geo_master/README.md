# 🌍 GeoMaster: Sistema Educativo de Geografía Interactiva

## 🎯 Filosofía

> *"La geografía ya no es memorización, es exploración."*

GeoMaster transforma el aprendizaje de geografía en una aventura interactiva usando tecnología 3D, gamificación y la visión educativa soberana de BlackMamba University.

## ✨ Características

- 🎮 **Gamificación total**: Sistema de badges, niveles y leaderboards
- 🌍 **Globo 3D interactivo**: Integración con Three.js para visualización inmersiva
- 📊 **Progreso personalizado**: Tracking individual con IA para rutas de aprendizaje adaptativas
- 🏆 **Certificaciones**: Badges verificables que demuestran dominio geográfico
- 🎯 **3 Niveles de dificultad**: Desde América Latina hasta experto mundial
- 📚 **Base de datos completa**: 195+ países con información detallada
- 🚀 **Interfaz moderna**: Frontend Spark con React y TypeScript

## 📋 Estructura del Proyecto

```
geo_master/
├── README.md                          # Este archivo
├── geo_master_engine.py               # Motor principal del sistema
├── data/                              # Base de datos geográfica
│   ├── countries.json                 # 195+ países con info detallada
│   ├── capitals.json                  # Referencia rápida de capitales
│   ├── cities.json                    # 60+ ciudades principales
│   └── landmarks.json                 # Puntos de interés geográfico
├── challenges/                        # Configuración de niveles
│   ├── level_1_americas.json          # Nivel Américas
│   ├── level_2_world.json             # Nivel Mundial
│   └── level_3_expert.json            # Nivel Experto
├── frontend/                          # Aplicación React/TypeScript
│   ├── src/
│   │   ├── components/                # Componentes UI
│   │   │   ├── GeoGlobe.tsx          # Globo 3D interactivo
│   │   │   ├── QuizPanel.tsx         # Panel de preguntas
│   │   │   ├── ScoreBoard.tsx        # Tabla de puntuaciones
│   │   │   └── CountryInfo.tsx       # Información de países
│   │   ├── hooks/                     # React hooks
│   │   │   └── useGeoQuiz.ts         # Hook del sistema de quiz
│   │   └── data/                      # Datos frontend
│   ├── package.json                   # Dependencias Node
│   ├── vite.config.ts                 # Configuración Vite
│   └── tsconfig.json                  # Configuración TypeScript
└── tests/                             # Tests unitarios
    └── test_geo_master.py             # Suite de tests Python
```

## 🚀 Instalación y Uso

### Backend (Python)

1. **Instalar dependencias**:
   ```bash
   cd /path/to/XarvisCore
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Ejecutar el motor**:
   ```python
   from geo_master_engine import GeoMasterEngine

   # Inicializar el motor
   engine = GeoMasterEngine()

   # Generar un quiz
   quiz = engine.generate_quiz(level="americas", num_questions=10)
   print(f"Quiz generado: {quiz['total_questions']} preguntas")

   # Validar respuestas
   result = engine.validate_answer(
       question_id="q_1_mexico",
       user_answer="Ciudad de México",
       correct_answer="Ciudad de México"
   )
   print(f"Respuesta correcta: {result['is_correct']}")

   # Calcular puntuación
   score = engine.calculate_score(
       correct_answers=8,
       total_questions=10,
       time_spent=300
   )
   print(f"Puntuación: {score['percentage']}%")

   # Otorgar badge
   badge = engine.award_badge(
       user_id="student_123",
       level_completed="americas",
       score=85.0
   )
   print(f"Badge otorgado: {badge['badge']['name']}")
   ```

3. **Obtener información de país**:
   ```python
   country = engine.get_country_info("mexico")
   print(f"País: {country['name']}")
   print(f"Capital: {country['capital']}")
   print(f"Población: {country['population']:,}")
   print(f"Datos curiosos: {country['fun_facts']}")
   ```

### Frontend (Spark/React)

1. **Instalar dependencias**:
   ```bash
   cd frontend
   npm install
   ```

2. **Ejecutar en desarrollo**:
   ```bash
   npm run dev
   # Abre http://localhost:5173
   ```

3. **Compilar para producción**:
   ```bash
   npm run build
   npm run preview
   ```

### Ejecutar Tests

```bash
cd tests
python -m pytest test_geo_master.py -v
# O con unittest:
python test_geo_master.py
```

## 🎓 Niveles de Aprendizaje

### Nivel 1: América Latina 🌎

**Maestro de América Latina**
- 📍 22 países de las Américas
- ⏱️ Tiempo límite: 10 minutos
- 🎯 Puntuación mínima: 80%
- 🏆 Badge: **🌎 Explorador de las Américas**

**Países incluidos**:
México, Argentina, Brasil, Chile, Colombia, Perú, Venezuela, Ecuador, Bolivia, Uruguay, Paraguay, Cuba, República Dominicana, Costa Rica, Panamá, Guatemala, Honduras, Nicaragua, El Salvador, Puerto Rico, Estados Unidos, Canadá

### Nivel 2: Mundial 🌍

**Viajero Mundial**
- 📍 34 países principales del mundo
- ⏱️ Tiempo límite: 20 minutos
- 🎯 Puntuación mínima: 85%
- 🏆 Badge: **🌍 Ciudadano Global**

**Continentes cubiertos**:
- Americas
- Europe
- Asia
- Africa
- Oceania

### Nivel 3: Experto 🗺️

**Cartógrafo Soberano**
- 📍 195+ países del mundo
- ⏱️ Sin límite de tiempo
- 🎯 Puntuación mínima: 90%
- 🏆 Badge: **🗺️ Maestro Geógrafo**

**Desafío completo**: Todos los países reconocidos internacionalmente

## 📊 Sistema de Puntuación

### Cálculo Base
```
Puntuación = (Respuestas Correctas / Total de Preguntas) × 100
```

### Bono por Tiempo
- Responder en menos de 30 segundos por pregunta otorga puntos bonus
- Bono máximo: 10 puntos
- Fórmula: `min(10, (30 - tiempo_promedio) / 3)`

### Ejemplo:
- 8/10 respuestas correctas = 80%
- Tiempo promedio: 20 segundos/pregunta
- Bono: (30-20)/3 = 3.33 puntos
- **Puntuación final: 83.33%**

## 🏅 Sistema de Badges

Los badges se otorgan al completar niveles con puntuación superior al mínimo requerido:

| Nivel | Badge | Requisito |
|-------|-------|-----------|
| Americas | 🌎 Explorador de las Américas | 80%+ |
| World | 🌍 Ciudadano Global | 85%+ |
| Expert | 🗺️ Maestro Geógrafo | 90%+ |

### Badges Especiales (Futuro)
- 💯 **Perfección**: 100% en cualquier nivel
- ⚡ **Velocista**: Completar en menos del 50% del tiempo
- 🎯 **Precisión Total**: 10 quizzes consecutivos sin errores
- 🌟 **Polímata**: Completar los 3 niveles

## 🔌 API Reference

### Generar Quiz
```python
quiz = engine.generate_quiz(
    level="americas",      # "americas" | "world" | "expert"
    num_questions=10       # Número de preguntas a generar
)
```

**Retorna**:
```json
{
  "quiz_id": "quiz_americas_1234567890",
  "level": "americas",
  "questions": [...],
  "total_questions": 10,
  "time_limit_minutes": 10,
  "passing_score": 80,
  "badge": {
    "name": "🌎 Explorador de las Américas",
    "description": "Dominas la geografía del continente americano"
  }
}
```

### Validar Respuesta
```python
result = engine.validate_answer(
    question_id="q_1_mexico",
    user_answer="Ciudad de México",
    correct_answer="Ciudad de México"
)
```

### Calcular Puntuación
```python
score = engine.calculate_score(
    correct_answers=8,
    total_questions=10,
    time_spent=300
)
```

### Obtener Información de País
```python
country = engine.get_country_info("mexico")
```

### Obtener Leaderboard
```python
leaderboard = engine.get_leaderboard(
    level="global",  # "americas" | "world" | "expert" | "global"
    limit=10
)
```

## 🎨 Componentes Frontend

### GeoGlobe
Globo 3D interactivo con Three.js:
```tsx
<GeoGlobe
  mode="quiz"
  highlightCountry="mexico"
  onCountryClick={(country) => console.log(country)}
/>
```

### QuizPanel
Panel de preguntas con opciones múltiples:
```tsx
<QuizPanel
  question={currentQuestion}
  questionNumber={1}
  totalQuestions={10}
  onAnswer={(answer) => handleAnswer(answer)}
/>
```

### ScoreBoard
Tabla de puntuaciones final:
```tsx
<ScoreBoard
  score={8}
  totalQuestions={10}
  timeSpent={300}
  level="americas"
  badgeEarned={badge}
/>
```

### CountryInfo
Información detallada de países:
```tsx
<CountryInfo
  country={countryData}
  onClose={() => setShowInfo(false)}
/>
```

## 🔗 Integración con BMU

GeoMaster se integra con el ecosistema completo de BlackMamba University:

### 7_EDUCATION_SYSTEM
- `bmu_platform.py` - Plataforma principal de BMU
- `bmu_curriculum.py` - Sistema de currículo
- `alexandria_engine.py` - Motor de búsqueda educativa

### 19_QUANTUM_CORE
- IA para recomendaciones personalizadas
- Análisis de patrones de aprendizaje
- Generación adaptativa de contenido

### globo-terrqueo-hd-8k (Futuro)
- Visualización 3D de alta definición
- Texturas realistas de la Tierra
- Iluminación dinámica día/noche

## 📈 Roadmap

### Fase 1: Core System ✅
- [x] Backend Python con motor de quizzes
- [x] Base de datos de 34 países
- [x] Sistema de niveles y badges
- [x] Estructura frontend Spark
- [x] Tests unitarios básicos

### Fase 2: Enhanced Features (En desarrollo)
- [ ] Frontend Spark completo y funcional
- [ ] Integración con globo 3D HD
- [ ] Sistema de persistencia de usuarios
- [ ] API REST completa

### Fase 3: Advanced Learning (Planificado)
- [ ] Modo multijugador competitivo
- [ ] IA para rutas de aprendizaje personalizadas
- [ ] Análisis de fortalezas/debilidades
- [ ] Recomendaciones adaptativas

### Fase 4: Expansion (Futuro)
- [ ] Más de 195 países completos
- [ ] Modo historia/geografía histórica
- [ ] Integración con otros módulos BMU
- [ ] Certificaciones blockchain

## 🧪 Testing

### Ejecutar Tests Completos
```bash
cd tests
python -m unittest test_geo_master.py -v
```

### Tests Incluidos
- ✅ Inicialización del motor
- ✅ Carga de datos geográficos
- ✅ Generación de quizzes por nivel
- ✅ Validación de respuestas
- ✅ Cálculo de puntuaciones
- ✅ Sistema de badges
- ✅ Integridad de datos
- ✅ Estructura de archivos

### Cobertura Actual
- Backend: ~90%
- Frontend: En desarrollo
- Integración: En desarrollo

## 🤝 Contribuir

GeoMaster es parte del ecosistema XarvisCore. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Parte del proyecto XarvisCore por Iyari Cancino Gomez y BlackMamba University.

## 🙏 Agradecimientos

- **Iyari Cancino Gomez** - Arquitecto de XarvisCore y visión educativa
- **BlackMamba University** - Plataforma de educación soberana
- Comunidad de contribuidores de XarvisCore

## 📞 Soporte

Para preguntas, issues o sugerencias:
- GitHub Issues: [XarvisCore Issues](https://github.com/Blackmvmba88/XarvisCore/issues)
- Email: (configurar email de soporte)
- Discord: (configurar servidor de comunidad)

---

**"La educación soberana comienza con geografía, porque entender el mundo es el primer paso para transformarlo."**

— Iyari Cancino Gomez, Arquitecto de XarvisCore

🌍 Explora. 🧠 Aprende. 🏆 Domina.
