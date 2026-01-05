"""
🎓 BlackMamba University Platform
Arquitecto: Iyari Cancino Gomez
Sistema de educación democratizada con 30+ certificaciones

Filosofía:
"Paga por una si quieres lujo; estudia tres y el Rey te las paga todas.
Premiamos la audacia, no el dinero."
"""

from flask import Flask, render_template_string, jsonify, request, session
from flask_cors import CORS
import os
import json
import datetime
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.getenv("BMU_SECRET", "bmu-sovereign-knowledge-2025")
CORS(app)

# === NIVEL 1: FUNDAMENTOS DE SOBERANÍA ===
# Antes de la teoría, enseñamos la vida
FOUNDATION_STAGE = {
    "construccion_hogar": {
        "nombre": "🏠 Construcción del Hogar",
        "descripcion": "Desde cimientos hasta techo. Aprender a construir tu propio refugio con honor y técnica",
        "cursos": [
            {"id": "cimientos", "titulo": "Cimientos y Estructuras", "duracion": "30h", "nivel": "Fundacional"},
            {"id": "carpinteria", "titulo": "Carpintería Básica", "duracion": "25h", "nivel": "Fundacional"},
            {"id": "electricidad", "titulo": "Electricidad Doméstica", "duracion": "20h", "nivel": "Fundacional"},
            {"id": "plomeria", "titulo": "Plomería y Sistemas de Agua", "duracion": "20h", "nivel": "Fundacional"},
        ]
    },
    "higiene_limpieza": {
        "nombre": "🧹 Higiene y Limpieza",
        "descripcion": "Cuidado del cuerpo, el hogar y el entorno. La limpieza es el primer acto de soberanía",
        "cursos": [
            {"id": "higiene_personal", "titulo": "Higiene Personal y Salud", "duracion": "15h", "nivel": "Fundacional"},
            {"id": "limpieza_hogar", "titulo": "Limpieza y Mantenimiento del Hogar", "duracion": "15h", "nivel": "Fundacional"},
            {"id": "organizacion", "titulo": "Organización de Espacios", "duracion": "10h", "nivel": "Fundacional"},
            {"id": "ecologia", "titulo": "Ecología Doméstica", "duracion": "15h", "nivel": "Fundacional"},
        ]
    },
    "etica_moral": {
        "nombre": "⚖️ Ética y Moral",
        "descripcion": "El código de honor del soberano. Principios inmutables para la vida digna",
        "cursos": [
            {"id": "principios", "titulo": "Principios de Honor", "duracion": "20h", "nivel": "Fundacional"},
            {"id": "responsabilidad", "titulo": "Responsabilidad Personal", "duracion": "15h", "nivel": "Fundacional"},
            {"id": "justicia", "titulo": "Justicia y Equidad", "duracion": "20h", "nivel": "Fundacional"},
            {"id": "verdad", "titulo": "El Camino de la Verdad", "duracion": "15h", "nivel": "Fundacional"},
        ]
    },
    "musica_universo": {
        "nombre": "🎵 Música: Lenguaje del Universo",
        "descripcion": "La música como arquitectura emocional y clave de comprensión universal",
        "cursos": [
            {"id": "teoria_musical", "titulo": "Teoría Musical Fundamental", "duracion": "30h", "nivel": "Fundacional"},
            {"id": "ritmo_tiempo", "titulo": "Ritmo y Tiempo Universal", "duracion": "25h", "nivel": "Fundacional"},
            {"id": "armonia", "titulo": "Armonía y Resonancia", "duracion": "30h", "nivel": "Fundacional"},
            {"id": "produccion", "titulo": "Producción Musical Básica", "duracion": "40h", "nivel": "Fundacional"},
        ]
    },
    "gastronomia": {
        "nombre": "🍳 Gastronomía y Nutrición",
        "descripcion": "Cocinar es un acto de amor propio. Nutrición inteligente para cuerpo y mente",
        "cursos": [
            {"id": "nutricion", "titulo": "Nutrición Soberana", "duracion": "20h", "nivel": "Fundacional"},
            {"id": "cocina_basica", "titulo": "Cocina Básica", "duracion": "25h", "nivel": "Fundacional"},
            {"id": "conservacion", "titulo": "Conservación de Alimentos", "duracion": "15h", "nivel": "Fundacional"},
            {"id": "cultivo", "titulo": "Cultivo Urbano de Alimentos", "duracion": "25h", "nivel": "Fundacional"},
        ]
    },
    "salud_fisica": {
        "nombre": "💪 Salud Física y Mental",
        "descripcion": "Cuerpo fuerte, mente clara. El templo debe ser cuidado con honor",
        "cursos": [
            {"id": "ejercicio", "titulo": "Ejercicio y Movimiento", "duracion": "20h", "nivel": "Fundacional"},
            {"id": "meditacion", "titulo": "Meditación y Claridad Mental", "duracion": "15h", "nivel": "Fundacional"},
            {"id": "primeros_auxilios", "titulo": "Primeros Auxilios", "duracion": "20h", "nivel": "Fundacional"},
            {"id": "prevencion", "titulo": "Prevención de Enfermedades", "duracion": "15h", "nivel": "Fundacional"},
        ]
    }
}

# === NIVEL 2+: CERTIFICACIONES TÉCNICAS ===
# Basadas en el curriculum del Arquitecto
CERTIFICATIONS = {
    "ia_neuronal": {
        "nombre": "🧠 IA & Arquitectura Neuronal",
        "descripcion": "Construcción y entrenamiento de redes neuronales, ingeniería de prompts",
        "cursos": [
            {"id": "nn_cpp", "titulo": "Neural Networks en C++", "duracion": "40h", "nivel": "Avanzado"},
            {"id": "nn_python", "titulo": "Neural Networks en Python", "duracion": "35h", "nivel": "Avanzado"},
            {"id": "prompt_eng", "titulo": "Prompt Engineering", "duracion": "20h", "nivel": "Intermedio"},
            {"id": "working_ai", "titulo": "Working with AI", "duracion": "15h", "nivel": "Básico"},
        ]
    },
    "ingenieria": {
        "nombre": "🛠️ Ingeniería de Dominio & Microservicios",
        "descripcion": "DDD, contenedores, arquitectura de software moderna",
        "cursos": [
            {"id": "ddd", "titulo": "Domain-Driven Design", "duracion": "50h", "nivel": "Avanzado"},
            {"id": "docker", "titulo": "Docker Esencial", "duracion": "30h", "nivel": "Intermedio"},
            {"id": "dotnet", "titulo": ".NET Avanzado", "duracion": "45h", "nivel": "Avanzado"},
            {"id": "fastapi", "titulo": "FastAPI Mastery", "duracion": "25h", "nivel": "Intermedio"},
        ]
    },
    "ciberseguridad": {
        "nombre": "🛡️ Ciberseguridad & Sistemas",
        "descripcion": "CompTIA Security+, gestión de incidentes, shell scripting",
        "cursos": [
            {"id": "security_plus", "titulo": "CompTIA Security+", "duracion": "60h", "nivel": "Certificación"},
            {"id": "incident_mgmt", "titulo": "Gestión de Incidentes", "duracion": "30h", "nivel": "Avanzado"},
            {"id": "shell_script", "titulo": "Shell Scripting", "duracion": "25h", "nivel": "Intermedio"},
            {"id": "linux_admin", "titulo": "Administración Linux", "duracion": "40h", "nivel": "Intermedio"},
        ]
    },
    "data_science": {
        "nombre": "📊 Ciencia de Datos",
        "descripcion": "Big Data con PySpark, limpieza de datos, análisis estratégico",
        "cursos": [
            {"id": "pyspark", "titulo": "Big Data con PySpark", "duracion": "45h", "nivel": "Avanzado"},
            {"id": "data_clean", "titulo": "Limpieza de Datos Avanzada", "duracion": "30h", "nivel": "Intermedio"},
            {"id": "data_science", "titulo": "Data Science Estratégico", "duracion": "50h", "nivel": "Avanzado"},
        ]
    },
    "creatividad": {
        "nombre": "🎨 Creatividad & Videojuegos",
        "descripcion": "Diseño de videojuegos, modelado 3D, suite visual",
        "cursos": [
            {"id": "game_design", "titulo": "Diseño de Videojuegos", "duracion": "60h", "nivel": "Avanzado"},
            {"id": "sketchup", "titulo": "Modelado 3D (SketchUp)", "duracion": "35h", "nivel": "Intermedio"},
            {"id": "canva_suite", "titulo": "Suite Visual Canva", "duracion": "25h", "nivel": "Básico"},
        ]
    },
    "pedagogia": {
        "nombre": "🏫 Pedagogía Soberana",
        "descripcion": "Fundamentos docentes, democratización del conocimiento",
        "cursos": [
            {"id": "teaching_basics", "titulo": "Fundamentos Docentes", "duracion": "30h", "nivel": "Básico"},
            {"id": "canva_teachers", "titulo": "Canva para Profesores", "duracion": "20h", "nivel": "Básico"},
        ]
    }
}

# === PLANIFICACIÓN PEDAGÓGICA PARA TUTORES ===
# Cada curso tiene su propia guía didáctica completa
TEACHING_PLANS = {
    # FUNDAMENTOS - Construcción del Hogar
    "cimientos": {
        "duracion_semanas": 6,
        "sesiones_semanales": 2,
        "duracion_sesion": "2.5h",
        "objetivo_general": "Capacitar al estudiante en la construcción de cimientos sólidos con técnicas seguras y profesionales",
        "modulos": [
            {
                "semana": "1-2",
                "tema": "Tipos de Suelo y Preparación",
                "objetivos": ["Identificar tipos de suelo", "Realizar excavaciones seguras", "Calcular profundidad de cimientos"],
                "actividades": ["Análisis de muestras de suelo", "Práctica de excavación manual", "Cálculos de resistencia"],
                "materiales": ["Palas, piochas", "Muestras de suelo", "Nivel láser", "Calculadora de estructuras"],
                "evaluacion": "Práctica supervisada de excavación + Quiz teórico"
            },
            {
                "semana": "3-4",
                "tema": "Mezcla de Concreto y Armado",
                "objetivos": ["Preparar mezcla de concreto correcta", "Instalar armado de acero", "Cimbrar correctamente"],
                "actividades": ["Práctica de mezclas 1:2:3", "Doblado y amarre de varillas", "Instalación de cimbra"],
                "materiales": ["Cemento, arena, grava", "Varillas corrugadas", "Alambre recocido", "Madera para cimbra"],
                "evaluacion": "Construcción de maqueta de cimiento a escala"
            },
            {
                "semana": "5-6",
                "tema": "Vaciado y Curado",
                "objetivos": ["Vaciar concreto sin segregación", "Vibrar correctamente", "Aplicar técnicas de curado"],
                "actividades": ["Vaciado simulado", "Uso de vibrador", "Métodos de curado húmedo"],
                "materiales": ["Carretilla", "Vibrador de concreto", "Manguera", "Plástico para curado"],
                "evaluacion": "Proyecto final: Construcción de cimiento real (práctica comunitaria)"
            }
        ],
        "recursos_tutor": ["Manual de construcción ACI", "Videos técnicos de CEMEX", "Normas NTC para construcción"],
        "evaluacion_final": "Construcción supervisada de cimiento para proyecto comunitario real"
    },
    
    "teoria_musical": {
        "duracion_semanas": 6,
        "sesiones_semanales": 2,
        "duracion_sesion": "2.5h",
        "objetivo_general": "Dominar los fundamentos de teoría musical como base de comprensión universal",
        "modulos": [
            {
                "semana": "1-2",
                "tema": "Ritmo y Tiempo Universal",
                "objetivos": ["Entender el tiempo como arquitectura", "Dominar compases básicos", "Sentir el pulso interno"],
                "actividades": ["Ejercicios de percusión corporal", "Análisis de ritmos naturales (corazón, respiración)", "Práctica de compases 4/4, 3/4, 6/8"],
                "materiales": ["Metrónomo", "Instrumentos de percusión básica", "Grabaciones de la naturaleza"],
                "evaluacion": "Composición rítmica basada en patrones naturales"
            },
            {
                "semana": "3-4",
                "tema": "Melodía y Escalas",
                "objetivos": ["Construcción de escalas mayores/menores", "Intervalos y su significado emocional", "Melodía como narrativa"],
                "actividades": ["Construcción física de escalas", "Improvisación melódica", "Análisis de melodías famosas"],
                "materiales": ["Teclado o piano", "Software de notación (MuseScore)", "Grabador de audio"],
                "evaluacion": "Crear melodía original que cuente una historia"
            },
            {
                "semana": "5-6",
                "tema": "Armonía: La Geometría del Sonido",
                "objetivos": ["Construir acordes triada", "Progresiones armónicas clásicas", "Armonía como arquitectura emocional"],
                "actividades": ["Construcción de acordes I-IV-V", "Análisis armónico de canciones BlackMamba RECORDS", "Práctica de cifrado"],
                "materiales": ["Instrumento armónico", "Partituras de análisis", "DAW básico (GarageBand/Reaper)"],
                "evaluacion": "Armonización de melodía propia + Análisis escrito de progresión"
            }
        ],
        "recursos_tutor": ["Catálogo BlackMamba RECORDS (280+ tracks)", "The Jazz Theory Book - Mark Levine", "Videos de análisis musical"],
        "evaluacion_final": "Composición completa (ritmo + melodía + armonía) con análisis teórico adjunto"
    },
    
    "etica_moral": {
        "duracion_semanas": 4,
        "sesiones_semanales": 2,
        "duracion_sesion": "2.5h",
        "objetivo_general": "Establecer el código de honor personal basado en principios inmutables",
        "modulos": [
            {
                "semana": "1",
                "tema": "El Fundamento: No Mentirse a Uno Mismo",
                "objetivos": ["Identificar auto-engaños comunes", "Practicar honestidad radical", "Distinguir verdad de confort"],
                "actividades": ["Diario de auto-reflexión", "Ejercicios de decisión ética", "Casos de estudio reales"],
                "materiales": ["Diario personal", "Casos de estudio impresos", "Guía de reflexión"],
                "evaluacion": "Ensayo sobre una decisión difícil propia analizada con honestidad"
            },
            {
                "semana": "2",
                "tema": "Responsabilidad Total",
                "objetivos": ["Eliminar mentalidad de víctima", "Asumir consecuencias", "Distinguir control vs. influencia"],
                "actividades": ["Mapeo de áreas de control", "Role-playing de situaciones complejas", "Análisis de El Manifiesto Soberano"],
                "materiales": ["The Long Manifesto (lectura obligatoria)", "Círculos de influencia (diagrama)", "Casos prácticos"],
                "evaluacion": "Plan de acción para problema personal asumiendo responsabilidad total"
            },
            {
                "semana": "3",
                "tema": "Justicia sin Venganza",
                "objetivos": ["Diferenciar justicia de venganza", "Aplicar consecuencias proporcionales", "Restauración vs. Castigo"],
                "actividades": ["Debate socrático", "Análisis de sistemas judiciales", "Resolución de conflictos reales"],
                "materiales": ["Códigos de honor históricos", "Casos legales para análisis", "Principios restaurativos"],
                "evaluacion": "Diseño de sistema de justicia para comunidad pequeña"
            },
            {
                "semana": "4",
                "tema": "El Código Personal",
                "objetivos": ["Definir principios propios inmutables", "Crear código de honor escrito", "Comprometerse públicamente"],
                "actividades": ["Redacción de código personal", "Ceremonia de compromiso", "Establecer accountability"],
                "materiales": ["Formato de código de honor", "Ejemplos históricos", "Testigos de compromiso"],
                "evaluacion": "Presentación pública de código de honor personal + compromiso ante comunidad"
            }
        ],
        "recursos_tutor": ["The Long Manifesto - Iyari Cancino Gomez", "Meditations - Marcus Aurelius", "Código de Hammurabi (análisis)"],
        "evaluacion_final": "Código de Honor Personal firmado + Proyecto de aplicación en comunidad"
    },
    
    "nutricion": {
        "duracion_semanas": 4,
        "sesiones_semanales": 2,
        "duracion_sesion": "2.5h",
        "objetivo_general": "Dominar nutrición inteligente para soberanía alimentaria",
        "modulos": [
            {
                "semana": "1",
                "tema": "Macronutrientes y Energía",
                "objetivos": ["Calcular necesidades calóricas", "Balancear carbohidratos/proteínas/grasas", "Leer etiquetas correctamente"],
                "actividades": ["Cálculo de TDEE personal", "Análisis de dieta actual", "Comparación de alimentos"],
                "materiales": ["Calculadora nutricional", "Báscula de alimentos", "App de tracking (MyFitnessPal)"],
                "evaluacion": "Plan nutricional personalizado de 1 semana"
            },
            {
                "semana": "2",
                "tema": "Micronutrientes y Suplementación",
                "objetivos": ["Identificar deficiencias comunes", "Fuentes naturales de vitaminas/minerales", "Cuándo suplementar"],
                "actividades": ["Análisis de sangre (lectura)", "Diseño de menú rico en micronutrientes", "Comparativa suplementos"],
                "materiales": ["Tablas nutricionales", "Muestras de suplementos", "Guía de síntomas de deficiencia"],
                "evaluacion": "Menú de 3 días optimizado para micronutrientes sin suplementos"
            },
            {
                "semana": "3",
                "tema": "Nutrición Deportiva y Rendimiento",
                "objetivos": ["Timing de nutrientes", "Pre/post entrenamiento", "Hidratación inteligente"],
                "actividades": ["Diseño de protocolo deportivo", "Preparación de comidas pre/post", "Práctica de hidratación"],
                "materiales": ["Shakers", "Ingredientes deportivos", "Medidor de hidratación"],
                "evaluacion": "Protocolo nutricional completo para rutina de ejercicio personal"
            },
            {
                "semana": "4",
                "tema": "Cocina Nutritiva Práctica",
                "objetivos": ["Técnicas que preservan nutrientes", "Meal prep eficiente", "Presupuesto inteligente"],
                "actividades": ["Sesión de cocina grupal", "Batch cooking", "Compra inteligente en mercado"],
                "materiales": ["Utensilios de cocina", "Ingredientes frescos", "Contenedores meal prep"],
                "evaluacion": "Meal prep de 5 días con presupuesto < $500 MXN + análisis nutricional"
            }
        ],
        "recursos_tutor": ["Tablas USDA de nutrición", "Guía de suplementación basada en evidencia", "Recetarios de alto rendimiento"],
        "evaluacion_final": "Plan nutricional de 30 días + Meal prep + Presupuesto + Análisis de macro/micronutrientes"
    },
    
    "higiene_personal": {
        "duracion_semanas": 3,
        "sesiones_semanales": 2,
        "duracion_sesion": "2.5h",
        "objetivo_general": "Dominar hábitos de higiene personal como base de salud y dignidad",
        "modulos": [
            {
                "semana": "1",
                "tema": "Higiene Corporal Fundamental",
                "objetivos": ["Microbiología básica de la piel", "Técnicas correctas de baño", "Rutina sostenible"],
                "actividades": ["Demostración de lavado correcto", "Análisis de productos (químicos vs naturales)", "Diseño de rutina personal"],
                "materiales": ["Productos de higiene básicos", "Microscopio", "Jabones artesanales"],
                "evaluacion": "Demostración práctica + explicación científica"
            },
            {
                "semana": "2",
                "tema": "Higiene Dental y Bucal",
                "objetivos": ["Técnica de cepillado Bass", "Prevención de caries", "Hábitos alimenticios saludables"],
                "actividades": ["Práctica con modelos dentales", "Análisis de pH bucal", "Pasta dental natural"],
                "materiales": ["Modelos dentales", "Cepillos variados", "Bicarbonato, aceite coco"],
                "evaluacion": "Técnica de cepillado + plan dental 30 días"
            },
            {
                "semana": "3",
                "tema": "Higiene Íntima y Ciclo Menstrual",
                "objetivos": ["Anatomía y fisiología básica", "Productos higiénicos sostenibles", "Manejo digno del ciclo"],
                "actividades": ["Sesiones género-específicas", "Comparativa de productos", "Higiene durante deporte"],
                "materiales": ["Modelos anatómicos", "Muestras de productos", "Copas, toallas reutilizables"],
                "evaluacion": "Ensayo reflexivo + plan sostenible"
            }
        ],
        "recursos_tutor": ["Manual OMS de salud pública", "Guía de higiene sostenible", "Red de profesionales salud"],
        "evaluacion_final": "Rutina 30 días documentada + presentación de hábitos saludables"
    },
    
    "higiene_hogar": {
        "duracion_semanas": 4,
        "sesiones_semanales": 2,
        "duracion_sesion": "2.5h",
        "objetivo_general": "Mantener espacios habitables limpios, ordenados y saludables",
        "modulos": [
            {
                "semana": "1",
                "tema": "Limpieza Profunda de Superficies",
                "objetivos": ["Tipos de superficies y productos", "Desinfección efectiva", "Limpiadores naturales"],
                "actividades": ["Limpieza de cocina completa", "Preparación de limpiadores caseros", "Test bacteriano"],
                "materiales": ["Productos básicos", "Vinagre, bicarbonato", "Trapos microfibra", "Cultivos"],
                "evaluacion": "Limpieza supervisada + protocolo escrito"
            },
            {
                "semana": "2",
                "tema": "Organización y Orden Funcional",
                "objetivos": ["Método KonMari adaptado", "Almacenamiento inteligente", "Sistemas sostenibles"],
                "actividades": ["Reorganización closet/alacena", "Almacenamiento reciclado", "Técnicas de doblado"],
                "materiales": ["Cajas organizadoras", "Etiquetas", "Materiales reciclados"],
                "evaluacion": "Antes/después + manual de mantenimiento"
            },
            {
                "semana": "3",
                "tema": "Manejo de Plagas y Prevención",
                "objetivos": ["Identificar plagas comunes", "Prevención mediante limpieza", "Control natural"],
                "actividades": ["Inspección espacios", "Sellado de grietas", "Repelentes naturales"],
                "materiales": ["Masilla", "Trampas no tóxicas", "Cítricos, menta"],
                "evaluacion": "Plan de prevención + protocolo acción"
            },
            {
                "semana": "4",
                "tema": "Lavandería y Textiles",
                "objetivos": ["Lavar diferentes telas", "Secado y planchado", "Costura básica"],
                "actividades": ["Lavado manual y máquina", "Clasificación textil", "Reparación de ropa"],
                "materiales": ["Detergentes", "Plancha", "Kit costura", "Telas práctica"],
                "evaluacion": "Lavado completo + 3 reparaciones"
            }
        ],
        "recursos_tutor": ["Manual limpieza profesional", "Guía eco-friendly", "Videos organización"],
        "evaluacion_final": "Limpieza hogar comunitario + documentación foto + checklist"
    },
    
    "residuos_compostaje": {
        "duracion_semanas": 3,
        "sesiones_semanales": 2,
        "duracion_sesion": "2.5h",
        "objetivo_general": "Gestionar residuos mediante separación, reciclaje y compostaje",
        "modulos": [
            {
                "semana": "1",
                "tema": "Separación y Reciclaje",
                "objetivos": ["Clasificar orgánicos/reciclables/inorgánicos", "Ciclo de vida materiales", "Consumo consciente"],
                "actividades": ["Auditoría basura 1 semana", "Sistema de separación hogar", "Visita virtual reciclaje"],
                "materiales": ["Contenedores separación", "Guías reciclaje local", "Básculas"],
                "evaluacion": "Reporte auditoría + plan reducción 50%"
            },
            {
                "semana": "2",
                "tema": "Compostaje Doméstico",
                "objetivos": ["Construir compostera casera", "Balance C:N ratio", "Mantenimiento óptimo"],
                "actividades": ["Construcción compostera", "Inicio pila compost", "Volteo y temperatura"],
                "materiales": ["Contenedor", "Residuos orgánicos", "Termómetro", "Material seco"],
                "evaluacion": "Compostera funcional + bitácora 2 semanas"
            },
            {
                "semana": "3",
                "tema": "Vermicompostaje y Aplicación",
                "objetivos": ["Cultivar lombrices rojas", "Cosechar humus", "Aplicar compost"],
                "actividades": ["Setup vermicompostera", "Cuidado lombrices", "Cosecha y aplicación"],
                "materiales": ["Contenedor opaco", "Lombrices 500g", "Residuos", "Plantas"],
                "evaluacion": "Vermicompostera activa + 2kg humus + aplicación"
            }
        ],
        "recursos_tutor": ["Manual EPA compostaje", "Guía vermicompost", "Integración 16_AGRICULTURE"],
        "evaluacion_final": "Sistema residuos completo + 5kg compost + reporte impacto"
    },
    
    "fitness_acondicionamiento": {
        "duracion_semanas": 8,
        "sesiones_semanales": 3,
        "duracion_sesion": "1.5h",
        "objetivo_general": "Desarrollar condición física mediante entrenamiento progresivo",
        "modulos": [
            {
                "semana": "1-2",
                "tema": "Evaluación y Fundamentos",
                "objetivos": ["Medir condición física actual", "Principios de entrenamiento", "Metas SMART"],
                "actividades": ["Test de Cooper", "Test de fuerza", "Flexibilidad", "Plan personalizado"],
                "materiales": ["Cronómetro", "Cinta métrica", "Báscula", "Formato evaluación"],
                "evaluacion": "Reporte inicial + plan 8 semanas"
            },
            {
                "semana": "3-4",
                "tema": "Entrenamiento Cardiovascular",
                "objetivos": ["Resistencia aeróbica", "Técnicas respiración", "Prevenir lesiones"],
                "actividades": ["Trote 20-30min", "HIIT básico", "Movilidad articular"],
                "materiales": ["Espacio abierto", "Ropa deportiva", "Agua", "Monitor cardíaco"],
                "evaluacion": "Test 5K + frecuencia cardíaca reposo"
            },
            {
                "semana": "5-6",
                "tema": "Fuerza con Peso Corporal",
                "objetivos": ["Movimientos básicos", "Fuerza funcional", "Progresiones"],
                "actividades": ["Calistenia", "Circuitos 3x semana", "Core"],
                "materiales": ["Colchoneta", "Barra dominadas", "Bandas elásticas"],
                "evaluacion": "50 push-ups, 100 squats, plank 3min"
            },
            {
                "semana": "7-8",
                "tema": "Flexibilidad y Recuperación",
                "objetivos": ["Rango movimiento", "Foam rolling", "Hábito sostenible"],
                "actividades": ["Yoga/stretching", "Foam rolling", "Rutina mantenimiento"],
                "materiales": ["Colchoneta yoga", "Foam roller", "Bloques"],
                "evaluacion": "Test final (vs semana 1) + rutina continua"
            }
        ],
        "recursos_tutor": ["Manual entrenamiento funcional", "Videos técnica", "Prevención lesiones"],
        "evaluacion_final": "Mejora 3 áreas + rutina personalizada + presentación progreso"
    },
    
    "primeros_auxilios": {
        "duracion_semanas": 4,
        "sesiones_semanales": 2,
        "duracion_sesion": "3h",
        "objetivo_general": "Responder a emergencias médicas y salvar vidas",
        "modulos": [
            {
                "semana": "1",
                "tema": "Evaluación y RCP",
                "objetivos": ["Evaluar seguridad escena", "RCP adultos/niños/bebés", "Usar DEA"],
                "actividades": ["Simulacros evaluación", "Práctica RCP maniquíes", "Uso DEA"],
                "materiales": ["Maniquíes RCP", "DEA entrenamiento", "Guantes"],
                "evaluacion": "Certificación RCP: 5 ciclos + DEA correcto"
            },
            {
                "semana": "2",
                "tema": "Hemorragias y Shock",
                "objetivos": ["Presión directa y torniquetes", "Reconocer shock", "Estabilizar paciente"],
                "actividades": ["Vendaje compresivo", "Torniquete", "Manejo shock"],
                "materiales": ["Vendas", "Torniquetes", "Mantas térmicas"],
                "evaluacion": "Detener hemorragia <3min + protocolo shock"
            },
            {
                "semana": "3",
                "tema": "Fracturas y Quemaduras",
                "objetivos": ["Inmovilizar fracturas", "Clasificar quemaduras", "Curar heridas"],
                "actividades": ["Entablillado", "Tratamiento quemaduras", "Sutura sintética"],
                "materiales": ["Férulas", "Apósitos", "Kit curación"],
                "evaluacion": "3 fracturas + herida estéril"
            },
            {
                "semana": "4",
                "tema": "Emergencias Comunes",
                "objetivos": ["Infarto, stroke, convulsiones", "Heimlich", "Hipo/hipertermia"],
                "actividades": ["Simulacros variados", "Heimlich", "Activación emergencias"],
                "materiales": ["Maniquí Heimlich", "Tarjetas escenarios", "Números emergencia"],
                "evaluacion": "5 emergencias resueltas correctamente"
            }
        ],
        "recursos_tutor": ["Manual Cruz Roja", "Certificación Cruz Roja", "Servicios emergencia"],
        "evaluacion_final": "Certificado Primeros Auxilios (válido 2 años) + examen 90%+"
    },
    
    "salud_mental": {
        "duracion_semanas": 6,
        "sesiones_semanales": 2,
        "duracion_sesion": "2h",
        "objetivo_general": "Desarrollar inteligencia emocional y herramientas de salud mental",
        "modulos": [
            {
                "semana": "1-2",
                "tema": "Autoconocimiento Emocional",
                "objetivos": ["Identificar emociones", "Triggers y patrones", "Emoción vs pensamiento"],
                "actividades": ["Diario emocional", "Rueda Plutchik", "Meditación escaneo"],
                "materiales": ["Diario", "Rueda emociones", "App Insight Timer"],
                "evaluacion": "14 días diario + 3 patrones personales"
            },
            {
                "semana": "3",
                "tema": "Estrés y Ansiedad",
                "objetivos": ["Signos estrés crónico", "Respiración 4-7-8", "Grounding"],
                "actividades": ["Respiración diafragmática", "Técnica 5-4-3-2-1", "Plan anti-estrés"],
                "materiales": ["Colchoneta", "Audio meditación", "Objetos sensoriales"],
                "evaluacion": "3 técnicas respiración + plan personal"
            },
            {
                "semana": "4",
                "tema": "Relaciones y Límites",
                "objetivos": ["Límites personales", "Comunicación asertiva", "Detectar toxicidad"],
                "actividades": ["Role-playing", "Decir 'no' con respeto", "Análisis relaciones"],
                "materiales": ["Guía CNV", "Casos estudio", "Ejercicios asertividad"],
                "evaluacion": "3 límites establecidos + asertividad"
            },
            {
                "semana": "5",
                "tema": "Depresión y Ayuda Profesional",
                "objetivos": ["Signos depresión DSM-5", "Desestigmatizar terapia", "Recursos disponibles"],
                "actividades": ["Educación salud mental", "Mitos vs realidades", "Directorio recursos"],
                "materiales": ["Material educativo", "Lista psicólogos", "Testimonios"],
                "evaluacion": "Ensayo desestigmatización + plan acción"
            },
            {
                "semana": "6",
                "tema": "Hábitos de Vida Saludable",
                "objetivos": ["Higiene del sueño", "Ejercicio antidepresivo", "Propósito de vida"],
                "actividades": ["Rutina sueño", "Integración fitness", "Voluntariado"],
                "materiales": ["Diario sueño", "Plan ejercicio", "Oportunidades voluntariado"],
                "evaluacion": "Rutina sueño 7 días + ejercicio + actividad comunitaria"
            }
        ],
        "recursos_tutor": ["Manual OMS salud mental", "Primeros auxilios psicológicos", "Red psicólogos"],
        "evaluacion_final": "Plan integral salud mental + presentación + compromiso autocuidado"
    }
}

# Metodología Pedagógica BMU
TEACHING_METHODOLOGY = {
    "filosofia": "Aprender haciendo. La teoría sin práctica es conocimiento muerto.",
    "principios": [
        "70% práctica, 30% teoría",
        "Proyectos comunitarios reales como evaluación",
        "Mentorías peer-to-peer",
        "No hay fracaso, solo retroalimentación",
        "Enseñar es la mejor forma de aprender"
    ],
    "estructura_sesion": {
        "apertura": "15min - Repaso y conexión con vida real",
        "teoria": "30min - Conceptos fundamentales",
        "practica_guiada": "60min - Hacer junto al tutor",
        "practica_autonoma": "30min - Hacer con supervisión",
        "cierre": "15min - Reflexión y siguiente sesión"
    },
    "evaluacion": {
        "diagnostica": "Entrevista inicial + prueba práctica",
        "formativa": "Retroalimentación continua en cada sesión",
        "sumativa": "Proyecto final aplicado a comunidad real"
    },
    "rol_tutor": [
        "Facilitador, no dictador",
        "Modelo a seguir en la práctica",
        "Mentor emocional y técnico",
        "Conector con recursos comunitarios",
        "Evaluador justo basado en esfuerzo y progreso"
    ]
}

# Rutas de carreras múltiples (3+ = GRATIS)
CAREER_PATHS = {
    "soberano_completo": {
        "nombre": "Soberano Completo",
        "areas": ["construccion_hogar", "higiene_limpieza", "etica_moral", "musica_universo", "gastronomia", "salud_fisica"],
        "nivel": "Fundacional",
        "duracion_total": "600h+",
        "costo_sin_beca": "$0 MXN (Siempre gratuito)",
        "costo_con_beca": "GRATIS - Derecho Universal"
    },
    "polimata_tech": {
        "nombre": "Polímata Tecnológico",
        "areas": ["ia_neuronal", "ingenieria", "ciberseguridad"],
        "nivel": "Avanzado",
        "duracion_total": "500h+",
        "costo_sin_beca": "$150,000 MXN",
        "costo_con_beca": "GRATIS (3+ áreas)"
    },
    "data_architect": {
        "nombre": "Arquitecto de Datos",
        "areas": ["data_science", "ingenieria", "ia_neuronal"],
        "nivel": "Avanzado",
        "duracion_total": "450h+",
        "costo_sin_beca": "$140,000 MXN",
        "costo_con_beca": "GRATIS (3+ áreas)"
    },
    "creative_engineer": {
        "nombre": "Ingeniero Creativo",
        "areas": ["creatividad", "ingenieria", "pedagogia"],
        "nivel": "Avanzado",
        "duracion_total": "400h+",
        "costo_sin_beca": "$120,000 MXN",
        "costo_con_beca": "GRATIS (3+ áreas)"
    }
}

# CSS Theme (Matrix/Cyberpunk)
BMU_CSS = """
:root {
    --primary: #00ff41;
    --secondary: #ffaa00;
    --bg: #0a0a0a;
    --glass: rgba(20, 20, 20, 0.85);
    --border: rgba(0, 255, 65, 0.3);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    color: var(--primary);
    font-family: 'Inter', 'Segoe UI', monospace;
    min-height: 100vh;
    background-attachment: fixed;
}

.header {
    background: var(--glass);
    backdrop-filter: blur(20px);
    padding: 2rem;
    text-align: center;
    border-bottom: 2px solid var(--border);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.header h1 {
    font-size: 2.5rem;
    text-shadow: 0 0 20px var(--primary);
    margin-bottom: 0.5rem;
}

.header p {
    color: #888;
    font-size: 1.1rem;
}

.container {
    max-width: 1400px;
    margin: 2rem auto;
    padding: 0 2rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.stat-card {
    background: var(--glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 255, 65, 0.3);
    border-color: var(--primary);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: var(--primary);
    text-shadow: 0 0 10px var(--primary);
    margin: 0.5rem 0;
}

.stat-label {
    color: #888;
    font-size: 0.9rem;
    text-transform: uppercase;
}

.section-title {
    font-size: 2rem;
    margin: 3rem 0 1.5rem;
    color: var(--primary);
    text-shadow: 0 0 15px var(--primary);
}

.categories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.category-card {
    background: var(--glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem;
    transition: all 0.3s ease;
}

.category-card:hover {
    border-color: var(--primary);
    box-shadow: 0 8px 25px rgba(0, 255, 65, 0.2);
}

.category-header {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: var(--primary);
}

.category-desc {
    color: #888;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

.course-list {
    list-style: none;
}

.course-item {
    background: rgba(0, 0, 0, 0.3);
    padding: 1rem;
    margin-bottom: 0.75rem;
    border-radius: 8px;
    border-left: 3px solid var(--primary);
    transition: all 0.2s ease;
}

.course-item:hover {
    background: rgba(0, 255, 65, 0.1);
    transform: translateX(5px);
}

.course-title {
    font-weight: bold;
    color: var(--primary);
    margin-bottom: 0.25rem;
}

.course-meta {
    color: #666;
    font-size: 0.85rem;
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: bold;
    margin-left: 0.5rem;
}

.badge-fundacional { background: var(--secondary); color: #000; font-weight: bold; }
.badge-basico { background: #333; color: #fff; }
.badge-intermedio { background: var(--secondary); color: #000; }
.badge-avanzado { background: var(--primary); color: #000; }
.badge-certificacion { background: #ff4444; color: #fff; }

.career-path {
    background: linear-gradient(135deg, rgba(0, 255, 65, 0.1), rgba(0, 0, 0, 0.8));
    border: 2px solid var(--primary);
    border-radius: 15px;
    padding: 2rem;
    margin-bottom: 2rem;
}

.path-name {
    font-size: 1.8rem;
    color: var(--primary);
    margin-bottom: 1rem;
}

.path-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.path-detail {
    background: rgba(0, 0, 0, 0.5);
    padding: 1rem;
    border-radius: 8px;
}

.path-detail strong {
    color: var(--primary);
    display: block;
    margin-bottom: 0.5rem;
}

.cta-section {
    text-align: center;
    margin: 4rem 0;
    padding: 3rem;
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 2px solid var(--primary);
    border-radius: 15px;
}

.cta-title {
    font-size: 2rem;
    color: var(--primary);
    margin-bottom: 1rem;
}

.cta-text {
    font-size: 1.2rem;
    color: #888;
    margin-bottom: 2rem;
}

button {
    background: var(--primary);
    color: #000;
    border: none;
    padding: 1rem 2rem;
    font-size: 1rem;
    font-weight: bold;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
}

button:hover {
    box-shadow: 0 0 30px var(--primary);
    transform: scale(1.05);
}

.footer {
    text-align: center;
    padding: 2rem;
    color: #666;
    margin-top: 4rem;
}
"""

# HTML Template
BMU_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BlackMamba University | Educación Soberana</title>
    <style>{{ css }}</style>
</head>
<body>
    <div class="header">
        <h1>🎓 BlackMamba University</h1>
        <p>Democratización del Conocimiento Real</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">
            "Antes de la teoría, enseñamos la vida"
        </p>
    </div>

    <div class="container">
        <!-- Estadísticas -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Cursos</div>
                <div class="stat-value">{{ total_certs }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Nivel Fundacional</div>
                <div class="stat-value">{{ foundation_hours }}h</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Nivel Avanzado</div>
                <div class="stat-value">{{ advanced_hours }}h</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Fundamentos</div>
                <div class="stat-value" style="font-size: 2rem;">GRATIS</div>
            </div>
        </div>

        <!-- NIVEL 1: FUNDAMENTOS DE SOBERANÍA -->
        <h2 class="section-title">🌟 Nivel 1: Fundamentos de Soberanía (SIEMPRE GRATUITO)</h2>
        <p style="color: #888; margin-bottom: 2rem; font-size: 1.1rem; text-align: center;">
            Antes de la teoría, enseñamos la vida. Estos conocimientos son un derecho universal.
        </p>
        <div class="categories-grid">
            {% for cat_id, category in foundation_stage.items() %}
            <div class="category-card" style="border-color: var(--secondary);">
                <h3 class="category-header" style="color: var(--secondary);">{{ category.nombre }}</h3>
                <p class="category-desc">{{ category.descripcion }}</p>
                <ul class="course-list">
                    {% for curso in category.cursos %}
                    <li class="course-item" style="border-left-color: var(--secondary);">
                        <div class="course-title">
                            {{ curso.titulo }}
                            <span class="badge badge-fundacional">{{ curso.nivel }}</span>
                        </div>
                        <div class="course-meta">⏱️ {{ curso.duracion }} | 🆔 {{ curso.id }}</div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>

        <!-- Rutas de Carrera -->
        <h2 class="section-title">🚀 Rutas de Carrera Completas</h2>
        {% for path_id, path in career_paths.items() %}
        <div class="career-path" {% if path.nivel == 'Fundacional' %}style="border-color: var(--secondary);"{% endif %}>
            <div class="path-name">{{ path.nombre }}</div>
            <p style="color: #888; margin-bottom: 1rem;">
                {% if path.nivel == 'Fundacional' %}
                Educación soberana completa - siempre gratuita para todos
                {% else %}
                Combina {{ path.areas|length }} áreas de experticia para convertirte en un verdadero polímata
                {% endif %}
            </p>
            <div class="path-info">
                <div class="path-detail">
                    <strong>Áreas Incluidas:</strong>
                    <ul style="color: #888; padding-left: 1.5rem; margin-top: 0.5rem;">
                        {% for area in path.areas %}
                        <li>
                            {% if area in foundation_stage %}
                                {{ foundation_stage[area].nombre }}
                            {% elif area in advanced_certs %}
                                {{ advanced_certs[area].nombre }}
                            {% endif %}
                        </li>
                        {% endfor %}
                    </ul>
                </div>
                <div class="path-detail">
                    <strong>Duración Total:</strong>
                    <span style="color: #888;">{{ path.duracion_total }}</span>
                </div>
                <div class="path-detail">
                    <strong>Nivel:</strong>
                    <span style="color: {% if path.nivel == 'Fundacional' %}var(--secondary){% else %}var(--primary){% endif %};">
                        {{ path.nivel }}
                    </span>
                </div>
                <div class="path-detail">
                    <strong>Costo:</strong>
                    <span style="color: var(--primary); font-size: 1.3rem; font-weight: bold;">{{ path.costo_con_beca }}</span>
                </div>
            </div>
        </div>
        {% endfor %}

        <!-- NIVEL 2+: Catálogo de Certificaciones Técnicas -->
        <h2 class="section-title">📚 Nivel 2+: Certificaciones Técnicas (Beca 3+ Áreas)</h2>
        <p style="color: #888; margin-bottom: 2rem; font-size: 1.1rem; text-align: center;">
            Conocimiento avanzado basado en el curriculum del Arquitecto Iyari Cancino Gomez
        </p>
        <div class="categories-grid">
            {% for cat_id, category in advanced_certs.items() %}
            <div class="category-card">
                <h3 class="category-header">{{ category.nombre }}</h3>
                <p class="category-desc">{{ category.descripcion }}</p>
                <ul class="course-list">
                    {% for curso in category.cursos %}
                    <li class="course-item">
                        <div class="course-title">
                            {{ curso.titulo }}
                            <span class="badge badge-{{ curso.nivel|lower }}">{{ curso.nivel }}</span>
                        </div>
                        <div class="course-meta">⏱️ {{ curso.duracion }} | 🆔 {{ curso.id }}</div>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>

        <!-- CTA Section -->
        <div class="cta-section">
            <h2 class="cta-title">La Educación Soberana Te Espera</h2>
            <p class="cta-text">
                <strong>Nivel 1 (Fundamentos):</strong> Siempre gratuito - derecho universal<br>
                <strong>Nivel 2+ (Técnico):</strong> Elige 3+ áreas y accede sin costo<br>
                El conocimiento es un derecho, no un privilegio.
            </p>
            <button onclick="alert('Sistema de registro próximamente. Contacta al Arquitecto: LinkedIn/in/iyari-c')">
                📝 SOLICITAR ACCESO
            </button>
            <button onclick="window.open('https://www.linkedin.com/in/iyari-c/details/certifications/', '_blank')" 
                    style="background: #333; color: var(--primary); margin-left: 1rem;">
                🔗 VER CERTIFICACIONES DEL ARQUITECTO
            </button>
        </div>
    </div>

    <div class="footer">
        <p>🦅 BlackMamba University - Parte del Sistema Soberano XarvisCore</p>
        <p style="margin-top: 0.5rem; font-size: 0.9rem;">
            Arquitecto: Iyari Cancino Gomez | 2025
        </p>
        <p style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;">
            "Antes de la teoría, enseñamos la vida"
        </p>
    </div>

    <script>
        console.log('🎓 BlackMamba University - Sistema Cargado');
        console.log('Total Cursos:', {{ total_certs }});
        console.log('Fundamentos:', {{ foundation_hours }}, 'h (GRATIS)');
        console.log('Avanzado:', {{ advanced_hours }}, 'h (Beca 3+)');
        console.log('Filosofía: Antes de la teoría, enseñamos la vida');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal de BMU"""
    
    # Calcular estadísticas - INCLUIR FUNDAMENTOS
    foundation_certs = sum(len(cat['cursos']) for cat in FOUNDATION_STAGE.values())
    advanced_certs = sum(len(cat['cursos']) for cat in CERTIFICATIONS.values())
    total_certs = foundation_certs + advanced_certs
    
    total_areas = len(FOUNDATION_STAGE) + len(CERTIFICATIONS)
    
    foundation_hours = sum(
        sum(int(curso['duracion'].replace('h', '')) for curso in cat['cursos'])
        for cat in FOUNDATION_STAGE.values()
    )
    advanced_hours = sum(
        sum(int(curso['duracion'].replace('h', '')) for curso in cat['cursos'])
        for cat in CERTIFICATIONS.values()
    )
    total_hours = foundation_hours + advanced_hours
    
    # Combinar ambos catálogos para la vista
    all_categories = {**FOUNDATION_STAGE, **CERTIFICATIONS}
    
    return render_template_string(
        BMU_TEMPLATE,
        css=BMU_CSS,
        certifications=all_categories,
        foundation_stage=FOUNDATION_STAGE,
        advanced_certs=CERTIFICATIONS,
        career_paths=CAREER_PATHS,
        total_certs=total_certs,
        total_areas=total_areas,
        total_hours=total_hours,
        foundation_hours=foundation_hours,
        advanced_hours=advanced_hours
    )

@app.route('/api/catalog')
def get_catalog():
    """API endpoint para el catálogo completo"""
    return jsonify({
        "foundation_stage": FOUNDATION_STAGE,
        "certifications": CERTIFICATIONS,
        "career_paths": CAREER_PATHS,
        "philosophy": "Antes de la teoría, enseñamos la vida. Paga por una si quieres lujo; estudia tres y el Rey te las paga todas",
        "architect": "Iyari Cancino Gomez",
        "linkedin": "https://www.linkedin.com/in/iyari-c/details/certifications/"
    })

@app.route('/api/stats')
def get_stats():
    """Estadísticas de BMU"""
    foundation_certs = sum(len(cat['cursos']) for cat in FOUNDATION_STAGE.values())
    advanced_certs = sum(len(cat['cursos']) for cat in CERTIFICATIONS.values())
    total_certs = foundation_certs + advanced_certs
    
    foundation_hours = sum(
        sum(int(curso['duracion'].replace('h', '')) for curso in cat['cursos'])
        for cat in FOUNDATION_STAGE.values()
    )
    advanced_hours = sum(
        sum(int(curso['duracion'].replace('h', '')) for curso in cat['cursos'])
        for cat in CERTIFICATIONS.values()
    )
    
    return jsonify({
        "total_certifications": total_certs,
        "foundation_certifications": foundation_certs,
        "advanced_certifications": advanced_certs,
        "total_areas": len(FOUNDATION_STAGE) + len(CERTIFICATIONS),
        "foundation_areas": len(FOUNDATION_STAGE),
        "advanced_areas": len(CERTIFICATIONS),
        "total_hours": foundation_hours + advanced_hours,
        "foundation_hours": foundation_hours,
        "advanced_hours": advanced_hours,
        "career_paths": len(CAREER_PATHS),
        "scholarship_threshold": 3,
        "scholarship_discount": "100%"
    })

@app.route('/api/career/<path_id>')
def get_career_path(path_id):
    """Detalles de una ruta de carrera"""
    if path_id not in CAREER_PATHS:
        return jsonify({"error": "Ruta no encontrada"}), 404
    
    path = CAREER_PATHS[path_id]
    
    # Buscar áreas en ambos catálogos
    detailed_areas = []
    for area in path['areas']:
        if area in FOUNDATION_STAGE:
            detailed_areas.append(FOUNDATION_STAGE[area])
        elif area in CERTIFICATIONS:
            detailed_areas.append(CERTIFICATIONS[area])
    
    return jsonify({
        "path": path,
        "detailed_areas": detailed_areas
    })

@app.route('/api/tutor/plan/<curso_id>')
def get_teaching_plan(curso_id):
    """Obtener planificación pedagógica de un curso"""
    if curso_id not in TEACHING_PLANS:
        return jsonify({"error": "Plan no encontrado. Planificaciones disponibles en desarrollo continuo."}), 404
    
    plan = TEACHING_PLANS[curso_id]
    return jsonify({
        "curso_id": curso_id,
        "plan": plan,
        "metodologia": TEACHING_METHODOLOGY
    })

@app.route('/api/tutor/methodology')
def get_methodology():
    """Metodología pedagógica completa de BMU"""
    return jsonify(TEACHING_METHODOLOGY)

@app.route('/api/tutor/plans')
def list_teaching_plans():
    """Listar todos los planes pedagógicos disponibles"""
    plans_summary = {}
    for curso_id, plan in TEACHING_PLANS.items():
        plans_summary[curso_id] = {
            "duracion_semanas": plan["duracion_semanas"],
            "sesiones_semanales": plan["sesiones_semanales"],
            "objetivo_general": plan["objetivo_general"],
            "total_modulos": len(plan["modulos"])
        }
    
    return jsonify({
        "total_plans": len(TEACHING_PLANS),
        "plans": plans_summary,
        "philosophy": TEACHING_METHODOLOGY["filosofia"]
    })

@app.route('/tutor')
def tutor_dashboard():
    """Dashboard para tutores con planificaciones"""
    
    TUTOR_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BMU - Portal de Tutores</title>
    <style>{{ css }}</style>
    <style>
        .plan-card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        .modulo {
            background: rgba(0, 0, 0, 0.3);
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid var(--primary);
            border-radius: 8px;
        }
        .modulo h4 {
            color: var(--primary);
            margin-bottom: 1rem;
        }
        .section {
            margin: 1rem 0;
        }
        .section strong {
            color: var(--secondary);
        }
        .tag {
            display: inline-block;
            background: rgba(0, 255, 65, 0.2);
            color: var(--primary);
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.85rem;
            margin: 0.2rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>👨‍🏫 Portal de Tutores BMU</h1>
        <p>Planificación Pedagógica y Metodología</p>
    </div>

    <div class="container">
        <h2 class="section-title">🎯 Metodología BMU</h2>
        <div class="plan-card">
            <h3 style="color: var(--primary);">{{ metodologia.filosofia }}</h3>
            <div class="section">
                <strong>Principios Fundamentales:</strong>
                <ul style="color: #888; margin-top: 0.5rem;">
                    {% for principio in metodologia.principios %}
                    <li>{{ principio }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <strong>Estructura de Sesión (150min):</strong>
                <ul style="color: #888; margin-top: 0.5rem;">
                    <li>{{ metodologia.estructura_sesion.apertura }}</li>
                    <li>{{ metodologia.estructura_sesion.teoria }}</li>
                    <li>{{ metodologia.estructura_sesion.practica_guiada }}</li>
                    <li>{{ metodologia.estructura_sesion.practica_autonoma }}</li>
                    <li>{{ metodologia.estructura_sesion.cierre }}</li>
                </ul>
            </div>
            
            <div class="section">
                <strong>Rol del Tutor:</strong>
                <ul style="color: #888; margin-top: 0.5rem;">
                    {% for rol in metodologia.rol_tutor %}
                    <li>{{ rol }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        <h2 class="section-title">📚 Planificaciones Disponibles</h2>
        {% for curso_id, plan in planes.items() %}
        <div class="plan-card">
            <h3 style="color: var(--primary);">Curso: {{ curso_id }}</h3>
            <p style="color: #888; margin: 1rem 0;">{{ plan.objetivo_general }}</p>
            
            <div class="section">
                <strong>Duración:</strong> {{ plan.duracion_semanas }} semanas | 
                <strong>Sesiones:</strong> {{ plan.sesiones_semanales }}/semana ({{ plan.duracion_sesion }} c/u)
            </div>
            
            <h4 style="color: var(--secondary); margin-top: 1.5rem;">Módulos del Curso:</h4>
            {% for modulo in plan.modulos %}
            <div class="modulo">
                <h4>📅 Semana {{ modulo.semana }}: {{ modulo.tema }}</h4>
                
                <div class="section">
                    <strong>Objetivos:</strong>
                    <ul style="color: #888; margin-top: 0.5rem;">
                        {% for objetivo in modulo.objetivos %}
                        <li>{{ objetivo }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <strong>Actividades:</strong>
                    <ul style="color: #888; margin-top: 0.5rem;">
                        {% for actividad in modulo.actividades %}
                        <li>{{ actividad }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <strong>Materiales Necesarios:</strong><br>
                    {% for material in modulo.materiales %}
                    <span class="tag">{{ material }}</span>
                    {% endfor %}
                </div>
                
                <div class="section" style="margin-top: 1rem;">
                    <strong>Evaluación:</strong> <span style="color: #888;">{{ modulo.evaluacion }}</span>
                </div>
            </div>
            {% endfor %}
            
            <div class="section" style="margin-top: 2rem; padding: 1rem; background: rgba(255, 170, 0, 0.1); border-radius: 8px;">
                <strong style="color: var(--secondary);">📖 Recursos para el Tutor:</strong>
                <ul style="color: #888; margin-top: 0.5rem;">
                    {% for recurso in plan.recursos_tutor %}
                    <li>{{ recurso }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section" style="margin-top: 1rem; padding: 1rem; background: rgba(0, 255, 65, 0.1); border-radius: 8px;">
                <strong style="color: var(--primary);">✅ Evaluación Final:</strong>
                <p style="color: #888; margin-top: 0.5rem;">{{ plan.evaluacion_final }}</p>
            </div>
        </div>
        {% endfor %}
        
        <div class="cta-section">
            <h2 class="cta-title">¿Quieres ser Tutor BMU?</h2>
            <p class="cta-text">
                Los tutores son pilares de la educación soberana.<br>
                Si tienes experiencia en alguna área fundacional, únete al equipo.
            </p>
            <button onclick="alert('Proceso de certificación de tutores próximamente. Contacta: LinkedIn/in/iyari-c')">
                📝 APLICAR COMO TUTOR
            </button>
        </div>
    </div>

    <div class="footer">
        <p>🦅 BlackMamba University - Portal de Tutores</p>
        <p style="margin-top: 0.5rem; font-size: 0.9rem;">
            "Enseñar es la mejor forma de aprender"
        </p>
    </div>
</body>
</html>
    """
    
    return render_template_string(
        TUTOR_TEMPLATE,
        css=BMU_CSS,
        metodologia=TEACHING_METHODOLOGY,
        planes=TEACHING_PLANS
    )

if __name__ == '__main__':
    print("🎓 BlackMamba University Platform")
    print("=" * 60)
    print("Iniciando servidor en puerto 7777...")
    print("Accede en: http://localhost:7777")
    print("=" * 60)
    app.run(host='0.0.0.0', port=7777, debug=True)
