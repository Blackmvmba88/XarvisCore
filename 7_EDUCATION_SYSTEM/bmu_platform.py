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

if __name__ == '__main__':
    print("🎓 BlackMamba University Platform")
    print("=" * 60)
    print("Iniciando servidor en puerto 7777...")
    print("Accede en: http://localhost:7777")
    print("=" * 60)
    app.run(host='0.0.0.0', port=7777, debug=True)
