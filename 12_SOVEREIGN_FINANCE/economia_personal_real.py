#!/usr/bin/env python3
"""
Sistema de Economía Personal Real (SEPR)
Dominio: 12_SOVEREIGN_FINANCE
Arquitecto: Iyari Cancino Gomez

Filosofía: "No hay nada que robar, primero hay que levantar.
El sistema gira en mí para salir del bache."
"""

import datetime
import json
from pathlib import Path
from collections import defaultdict

class InventarioActivos:
    """Gestiona todos los activos físicos y digitales del Rey."""
    
    def __init__(self):
        self.activos = {
            "fisicos": {
                "computadoras": [],
                "equipo_dmx": [],
                "vehiculos": [
                    {
                        "tipo": "Golf MK7 Turbo",
                        "uso_actual": "Personal",
                        "potencial": ["Clases manejo deportivo", "Clases turbo", "Experiencias conducción"],
                        "estado": "Operativo"
                    }
                ],
                "motocicletas": [],  # Usuario confirma que tiene
                "instrumentos": [],
                "otros": []
            },
            "digitales": {
                "musica": {
                    "total_tracks": 280,
                    "soundcloud": "https://soundcloud.com/iyari-c/tracks",
                    "distribucion": ["DistroKid", "TuneCore"],
                    "generos": ["Trap", "Reggae", "Salsa", "Electronic", "Fusion"],
                    "monetizado": True,
                    "primer_pago": 800  # MXN
                },
                "software": {
                    "xarvis_core": {
                        "descripcion": "Sistema soberano de 19 dominios",
                        "valor_unico": "IA + Custodia + Educación + Finanzas",
                        "competencia": "NINGUNA",
                        "potencial": "Enterprise Level"
                    },
                    "herramientas_creative": [
                        "3milpixeles (redimensionador)",
                        "BlackMamba YTDLP (descargador)",
                        "Audio 3D Lab",
                        "YTDLP Web",
                        "Suite Suno completa"
                    ]
                },
                "conocimiento": {
                    "dmx_iluminacion": {
                        "nivel": "Especialista",
                        "competencia_local": "Muy baja",
                        "servicios": ["Cursos", "Eventos", "Venta equipo"],
                        "precio_premium": True
                    },
                    "ai_systems": {
                        "nivel": "Arquitecto de Sistemas",
                        "certificaciones": 30,
                        "equilibrio_ia_humano": "Control soberano único"
                    },
                    "diseño": {
                        "ui_web": "Nivel profesional",
                        "grafico": "Invitaciones a sistemas complejos",
                        "rapidez": "Alta"
                    },
                    "produccion_musical": {
                        "velocidad": "Alta",
                        "calidad": "Profesional",
                        "monetizacion": "Ya activa (6 meses)"
                    },
                    "conduccion_especializada": {
                        "vehiculo_deportivo": "Golf MK7 Turbo",
                        "especialidades": ["Manejo deportivo", "Control de turbo", "Conducción defensiva"],
                        "motocicleta": True,
                        "competencia_local": "Media-baja",
                        "ventaja": "Vehículo atractivo + múltiples especialidades"
                    }
                }
            },
            "ingresos_pasivos": {
                "rentas_departamentos": {
                    "activo": True,
                    "frecuencia": "mensual",
                    "estabilidad": "Alta"
                }
            }
        }
        
        self.inventario_file = Path(__file__).parent / "inventario_activos.json"
        self.cargar_inventario()
    
    def cargar_inventario(self):
        """Carga inventario desde archivo si existe."""
        if self.inventario_file.exists():
            with open(self.inventario_file, 'r', encoding='utf-8') as f:
                self.activos = json.load(f)
    
    def guardar_inventario(self):
        """Guarda inventario actualizado."""
        with open(self.inventario_file, 'w', encoding='utf-8') as f:
            json.dump(self.activos, f, indent=2, ensure_ascii=False)
        return {"status": "Guardado", "archivo": str(self.inventario_file)}
    
    def agregar_activo_fisico(self, categoria, item):
        """Agrega un activo físico al inventario."""
        if categoria in self.activos["fisicos"]:
            self.activos["fisicos"][categoria].append({
                **item,
                "fecha_agregado": datetime.datetime.now().isoformat()
            })
            self.guardar_inventario()
            return {"status": "Agregado", "categoria": categoria, "item": item}
        return {"status": "Error", "mensaje": f"Categoría {categoria} no existe"}
    
    def listar_activos_vendibles(self):
        """Lista todos los activos que pueden generar dinero YA."""
        vendibles = {
            "fisicos_inmediatos": [],
            "servicios_especializados": [],
            "productos_digitales": [],
            "educacion_cursos": []
        }
        
        # Físicos
        for comp in self.activos["fisicos"]["computadoras"]:
            vendibles["fisicos_inmediatos"].append({
                "tipo": "Computadora",
                "item": comp,
                "canal": ["Marketplace", "MercadoLibre", "OLX"]
            })
        
        for dmx in self.activos["fisicos"]["equipo_dmx"]:
            vendibles["fisicos_inmediatos"].append({
                "tipo": "Equipo DMX",
                "item": dmx,
                "canal": ["Eventos", "Productoras", "DJs"],
                "precio_premium": True
            })
        
        # Servicios especializados
        vendibles["servicios_especializados"] = [
            {
                "servicio": "Iluminación DMX para eventos",
                "nicho": "Muy especializado",
                "competencia": "Baja",
                "precio": "Premium (poca gente sabe)",
                "formatos": ["Por evento", "Renta equipo", "Curso completo"]
            },
            {
                "servicio": "Consultoría IA + Sistemas Soberanos",
                "valor": "Xarvis Core - único en el mercado",
                "target": "Empresas que necesitan control IA-humano",
                "precio": "Enterprise"
            },
            {
                "servicio": "Diseño UI/Web/Gráfico",
                "nivel": "Interfaces complejas a invitaciones",
                "velocidad": "Alta",
                "precio": "Por proyecto"
            },
            {
                "servicio": "Producción musical profesional",
                "ventaja": "280+ tracks, monetización activa",
                "formatos": ["Beats", "Licencias", "Composición custom"]
            }
        ]
        
        # Productos digitales
        vendibles["productos_digitales"] = [
            {
                "producto": "Suite Suno completa",
                "descripcion": "Afinador + Organizador + Extractor",
                "mercado": "Productores musicales"
            },
            {
                "producto": "BlackMamba YTDLP",
                "descripcion": "Descargador completo con pitch shifting",
                "mercado": "Creadores de contenido"
            },
            {
                "producto": "3milpixeles",
                "descripcion": "Redimensionador profesional",
                "mercado": "Diseñadores, ecommerce"
            }
        ]
        
        # Educación
        vendibles["educacion_cursos"] = [
            {
                "curso": "DMX Iluminación Profesional",
                "duracion": "4-6 semanas",
                "precio_mercado": "$8,000-15,000 MXN",
                "ventaja": "Poca competencia local"
            },
            {
                "curso": "IA Práctica para Negocios",
                "duracion": "6 semanas",
                "precio_mercado": "$10,000-20,000 MXN",
                "ventaja": "Caso real (Xarvis Core)"
            },
            {
                "curso": "Producción Musical Rápida",
                "duracion": "8 semanas",
                "precio_mercado": "$6,000-12,000 MXN",
                "ventaja": "280+ producciones como portfolio"
            }
        ]
        
        return vendibles


class TrackerIngresos:
    """Rastrea TODOS los ingresos reales con origen identificado."""
    
    def __init__(self):
        self.ingresos = []
        self.ingresos_file = Path(__file__).parent / "ingresos_reales.json"
        self.cargar_ingresos()
    
    def cargar_ingresos(self):
        """Carga historial de ingresos."""
        if self.ingresos_file.exists():
            with open(self.ingresos_file, 'r', encoding='utf-8') as f:
                self.ingresos = json.load(f)
    
    def guardar_ingresos(self):
        """Guarda historial actualizado."""
        with open(self.ingresos_file, 'w', encoding='utf-8') as f:
            json.dump(self.ingresos, f, indent=2, ensure_ascii=False)
    
    def registrar_ingreso(self, fuente, cantidad, descripcion, evidencia=None):
        """Registra un ingreso real con evidencia."""
        ingreso = {
            "timestamp": datetime.datetime.now().isoformat(),
            "fuente": fuente,
            "cantidad_mxn": cantidad,
            "descripcion": descripcion,
            "evidencia": evidencia,  # URL email, screenshot, etc
            "mes": datetime.datetime.now().strftime("%Y-%m")
        }
        self.ingresos.append(ingreso)
        self.guardar_ingresos()
        return {"status": "Registrado", "ingreso": ingreso}
    
    def resumen_por_fuente(self):
        """Genera resumen de ingresos por fuente."""
        por_fuente = defaultdict(lambda: {"total": 0, "cantidad": 0, "items": []})
        
        for ingreso in self.ingresos:
            fuente = ingreso["fuente"]
            por_fuente[fuente]["total"] += ingreso["cantidad_mxn"]
            por_fuente[fuente]["cantidad"] += 1
            por_fuente[fuente]["items"].append(ingreso)
        
        return dict(por_fuente)
    
    def resumen_mensual(self):
        """Resumen por mes."""
        por_mes = defaultdict(lambda: {"total": 0, "fuentes": defaultdict(float)})
        
        for ingreso in self.ingresos:
            mes = ingreso["mes"]
            fuente = ingreso["fuente"]
            cantidad = ingreso["cantidad_mxn"]
            
            por_mes[mes]["total"] += cantidad
            por_mes[mes]["fuentes"][fuente] += cantidad
        
        return dict(por_mes)
    
    def total_historico(self):
        """Total de todos los ingresos registrados."""
        return sum(i["cantidad_mxn"] for i in self.ingresos)


class PlanMonetizacion:
    """Plan estratégico de monetización por línea de negocio."""
    
    def __init__(self):
        self.lineas_negocio = {
            "musica": {
                "canales": {
                    "distribucion_streaming": {
                        "status": "Activo",
                        "plataformas": ["Spotify", "Apple Music", "YouTube Music"],
                        "pago_actual": 800,  # MXN después de 6 meses
                        "proyeccion_12_meses": 2000,  # Crece con reproducciones
                        "accion": "Continuar subiendo, promocionar"
                    },
                    "venta_beats": {
                        "status": "No activado",
                        "plataformas_sugeridas": ["BeatStars", "Airbit", "SoundClick"],
                        "precio_sugerido": "$500-2,000 MXN por beat",
                        "potencial_mensual": "$5,000-15,000 MXN",
                        "accion": "URGENTE: Subir beats a marketplaces"
                    },
                    "licencias_exclusivas": {
                        "status": "No activado",
                        "precio_sugerido": "$5,000-20,000 MXN por licencia exclusiva",
                        "target": "Artistas emergentes, publicidad",
                        "accion": "Crear catálogo de licenciamiento"
                    },
                    "composicion_custom": {
                        "status": "Disponible",
                        "precio_sugerido": "$8,000-25,000 MXN por producción",
                        "ventaja": "Rapidez + calidad profesional",
                        "accion": "Ofrecer a productoras, marcas"
                    }
                }
            },
            "software": {
                "canales": {
                    "xarvis_como_servicio": {
                        "status": "No comercializado",
                        "modelo": "SaaS para empresas",
                        "precio_sugerido": "$50,000-200,000 MXN/año por empresa",
                        "target": "Empresas que necesitan IA controlada",
                        "accion": "Crear pitch deck + demo enterprise"
                    },
                    "herramientas_individuales": {
                        "status": "No monetizado",
                        "productos": ["3milpixeles", "BlackMamba YTDLP", "Suite Suno"],
                        "precio_sugerido": "$200-800 MXN por herramienta",
                        "modelo": "Compra única o suscripción",
                        "accion": "Empaquetar y vender en Gumroad/Lemon Squeezy"
                    },
                    "consultoria_ia": {
                        "status": "Disponible",
                        "precio_sugerido": "$3,000-8,000 MXN/hora",
                        "target": "Empresas implementando IA",
                        "accion": "LinkedIn + networking directo"
                    }
                }
            },
            "dmx_iluminacion": {
                "canales": {
                    "cursos_presenciales": {
                        "status": "No activado",
                        "duracion": "4-6 semanas",
                        "precio_sugerido": "$8,000-15,000 MXN por alumno",
                        "competencia": "MUY BAJA",
                        "accion": "URGENTE: Crear programa + publicitar"
                    },
                    "servicios_eventos": {
                        "status": "Disponible",
                        "precio_sugerido": "$3,000-10,000 MXN por evento",
                        "target": "Bodas, corporativos, conciertos",
                        "accion": "Portafolio + red de contactos eventos"
                    },
                    "venta_equipo": {
                        "status": "Disponible",
                        "precio_premium": True,
                        "margen": "30-50% sobre costo",
                        "accion": "Inventariar equipo + marketplace"
                    },
                    "renta_equipo": {
                        "status": "No activado",
                        "precio_sugerido": "$1,000-3,000 MXN/día",
                        "ROI": "Rápido (equipo especializado)",
                        "accion": "Expandir inventario DMX"
                    }
                }
            },
            "diseño": {
                "canales": {
                    "freelance_web": {
                        "status": "Disponible",
                        "precio_sugerido": "$8,000-30,000 MXN por proyecto",
                        "plataformas": ["Upwork", "Fiverr", "99designs"],
                        "accion": "Portfolio + perfiles activos"
                    },
                    "templates_premium": {
                        "status": "No activado",
                        "precio_sugerido": "$500-2,000 MXN por template",
                        "plataformas": ["ThemeForest", "Creative Market"],
                        "accion": "Crear 5-10 templates de UI"
                    },
                    "diseño_grafico": {
                        "status": "Disponible",
                        "precio_sugerido": "$500-3,000 MXN por proyecto",
                        "rapidez": "Ventaja competitiva",
                        "accion": "Redes sociales + portafolio visual"
                    }
                }
            },
            "hardware": {
                "canales": {
                    "venta_computadoras": {
                        "status": "Inventario sin vender",
                        "accion": "INMEDIATO: Inventariar + publicar",
                        "plataformas": ["Marketplace", "MercadoLibre", "OLX"],
                        "liquidez": "Media-alta (7-30 días)"
                    }
                }
            },
            "educacion": {
                "canales": {
                    "bmu_premium": {
                        "status": "Plataforma lista",
                        "modelo": "Freemium + cursos premium",
                        "precio_sugerido": "$1,500-5,000 MXN por curso especializado",
                        "accion": "Grabar primeros 3 cursos"
                    }
                }
            },
            "conduccion": {
                "canales": {
                    "clases_manejo_deportivo": {
                        "status": "Disponible",
                        "vehiculo": "Golf MK7 Turbo",
                        "precio_sugerido": "$800-1,500 MXN por clase (2-3h)",
                        "paquetes": {
                            "basico": "$3,000 MXN (4 clases)",
                            "deportivo": "$5,000 MXN (5 clases + circuito)",
                            "turbo_avanzado": "$7,000 MXN (6 clases especializadas)"
                        },
                        "target": "Jóvenes 18-35, entusiastas autos",
                        "accion": "Diseñar programa + publicitar en grupos autos"
                    },
                    "clases_motocicleta": {
                        "status": "Disponible",
                        "precio_sugerido": "$600-1,200 MXN por clase",
                        "paquetes": {
                            "principiante": "$2,500 MXN (4 clases)",
                            "intermedio": "$3,500 MXN (5 clases)",
                            "avanzado": "$4,500 MXN (6 clases)"
                        },
                        "certificacion": "Opcional - Licencia tipo A",
                        "accion": "Programa + redes motociclistas"
                    },
                    "experiencias_conduccion": {
                        "status": "No activado",
                        "descripcion": "Experiencia conducción Golf Turbo en circuito/carretera",
                        "precio_sugerido": "$2,000-3,500 MXN por experiencia",
                        "duracion": "3-4 horas (teoría + práctica)",
                        "target": "Regalos, cumpleaños, empresas",
                        "accion": "Paquete experiencia + video del día"
                    }
                }
            }
        }
    
    def priorizar_acciones_inmediatas(self):
        """Retorna acciones que generan dinero en <30 días."""
        acciones_inmediatas = [
            {
                "accion": "Inventariar y vender computadoras",
                "tiempo": "7-30 días",
                "potencial": "$10,000-50,000 MXN",
                "dificultad": "Baja",
                "prioridad": 1
            },
            {
                "accion": "Subir beats a BeatStars/Airbit",
                "tiempo": "1-3 días setup",
                "potencial": "$5,000-15,000 MXN/mes",
                "dificultad": "Baja",
                "prioridad": 1
            },
            {
                "accion": "Crear curso DMX iluminación",
                "tiempo": "14 días",
                "potencial": "$8,000-15,000 MXN por alumno",
                "dificultad": "Media",
                "prioridad": 2
            },
            {
                "accion": "Empaquetar herramientas en Gumroad",
                "tiempo": "3-7 días",
                "potencial": "$200-800 MXN por venta",
                "dificultad": "Baja",
                "prioridad": 2
            },
            {
                "accion": "Lanzar clases de manejo deportivo (Golf Turbo)",
                "tiempo": "7-14 días",
                "potencial": "$3,000-7,000 MXN por alumno",
                "dificultad": "Baja",
                "prioridad": 2
            },
            {
                "accion": "LinkedIn + pitch Xarvis Enterprise",
                "tiempo": "30-90 días",
                "potencial": "$50,000-200,000 MXN/año",
                "dificultad": "Alta",
                "prioridad": 3
            }
        ]
        return sorted(acciones_inmediatas, key=lambda x: x["prioridad"])
    
    def proyeccion_12_meses(self):
        """Proyección conservadora de ingresos si se activan canales."""
        proyeccion = {
            "mes_1_3": {
                "rentas": 0,  # Usuario define
                "musica_streaming": 900,
                "venta_hardware": 15000,  # Una computadora
                "beats_online": 3000,
                "total": 18900
            },
            "mes_4_6": {
                "rentas": 0,
                "musica_streaming": 1200,
                "beats_online": 8000,
                "curso_dmx": 15000,  # 1 alumno
                "clases_manejo": 6000,  # 2 alumnos
                "servicios_eventos": 5000,
                "total": 35200
            },
            "mes_7_9": {
                "rentas": 0,
                "musica_streaming": 1500,
                "beats_online": 12000,
                "curso_dmx": 30000,  # 2 alumnos
                "clases_manejo": 12000,  # 4 alumnos
                "herramientas_digitales": 4000,
                "servicios_eventos": 8000,
                "total": 67500
            },
            "mes_10_12": {
                "rentas": 0,
                "musica_streaming": 2000,
                "beats_online": 15000,
                "licencias_exclusivas": 10000,
                "curso_dmx": 45000,  # 3 alumnos
                "clases_manejo": 18000,  # 6 alumnos
                "experiencias_conduccion": 6000,  # 2 experiencias
                "xarvis_consultoria": 20000,
                "servicios_eventos": 12000,
                "diseño_freelance": 15000,
                "total": 143000
            }
        }
        
        total_anual = sum(p["total"] for p in proyeccion.values())
        return {
            "proyeccion_mensual": proyeccion,
            "total_anual_proyectado": total_anual,
            "nota": "Proyección CONSERVADORA. Requiere ejecución constante."
        }


class SistemaVisibilidad:
    """Estrategia para que el mundo sepa que existes."""
    
    def __init__(self):
        self.estrategia = {
            "digital": {
                "linkedin": {
                    "status": "Crítico",
                    "acciones": [
                        "Perfil completo con 30+ certificaciones",
                        "Posts semanales sobre IA, sistemas, música",
                        "Networking activo con CTOs, empresas tech",
                        "Artículos sobre Xarvis Core"
                    ]
                },
                "github": {
                    "status": "Activo",
                    "acciones": [
                        "README profesionales en cada repo",
                        "Demos en vivo de herramientas",
                        "Contribuciones open source"
                    ]
                },
                "youtube": {
                    "status": "No activado",
                    "contenido_sugerido": [
                        "Tutoriales DMX",
                        "Producción musical en vivo",
                        "Arquitectura de Xarvis",
                        "Time-lapses de diseño"
                    ]
                },
                "instagram_tiktok": {
                    "status": "No activado",
                    "contenido": [
                        "Reels de producción musical",
                        "Before/after diseños",
                        "Demos de luces DMX",
                        "Behind the scenes"
                    ]
                }
            },
            "local": {
                "networking_eventos": {
                    "target": "Bodas, corporativos, productoras",
                    "accion": "Tarjetas + portfolio físico"
                },
                "alianzas": {
                    "djs": "Renta equipo DMX",
                    "productoras": "Servicios iluminación",
                    "escuelas_musica": "Cursos de producción"
                }
            },
            "plataformas_venta": {
                "musica": ["BeatStars", "Airbit", "SoundClick"],
                "software": ["Gumroad", "Lemon Squeezy"],
                "diseño": ["Upwork", "Fiverr", "99designs"],
                "hardware": ["Marketplace", "MercadoLibre", "OLX"],
                "cursos": ["Udemy", "Teachable", "Hotmart"]
            }
        }
    
    def plan_30_dias(self):
        """Plan de visibilidad para los próximos 30 días."""
        return {
            "semana_1": [
                "LinkedIn: Optimizar perfil, agregar certificaciones",
                "GitHub: README profesionales en top 5 repos",
                "Crear portafolio visual (diseño + música)"
            ],
            "semana_2": [
                "BeatStars: Crear cuenta, subir 10 beats",
                "Marketplace: Inventariar y publicar computadoras",
                "Instagram: 3 posts de trabajos recientes"
            ],
            "semana_3": [
                "LinkedIn: 3 posts sobre IA/sistemas",
                "YouTube: Primer tutorial DMX",
                "Networking: Contactar 5 productoras locales"
            ],
            "semana_4": [
                "Gumroad: Empaquetar 2 herramientas",
                "LinkedIn: Pitch Xarvis a 10 empresas",
                "Diseñar material promocional curso DMX"
            ]
        }


# === INSTANCIAS GLOBALES ===
inventario = InventarioActivos()
tracker = TrackerIngresos()
plan = PlanMonetizacion()
visibilidad = SistemaVisibilidad()

# === SISTEMA COMPLETO ===
class EconomiaPersonalReal:
    """Sistema integrado de economía personal."""
    
    def __init__(self):
        self.inventario = inventario
        self.tracker = tracker
        self.plan = plan
        self.visibilidad = visibilidad
    
    def dashboard(self):
        """Dashboard completo del sistema económico."""
        return {
            "fecha": datetime.datetime.now().isoformat(),
            "total_ingresos_historico": self.tracker.total_historico(),
            "activos_vendibles": self.inventario.listar_activos_vendibles(),
            "acciones_inmediatas": self.plan.priorizar_acciones_inmediatas(),
            "proyeccion_12_meses": self.plan.proyeccion_12_meses(),
            "plan_visibilidad_30d": self.visibilidad.plan_30_dias()
        }
    
    def inicializar_con_datos_reales(self):
        """Inicializa con los datos reales del Arquitecto."""
        # Registrar primer ingreso de música
        self.tracker.registrar_ingreso(
            fuente="musica_streaming",
            cantidad=800,
            descripcion="Primer pago después de 6 meses - Distribución digital",
            evidencia="correo_electronico"
        )
        
        print("✅ Sistema inicializado con datos reales")
        print(f"💰 Total histórico: ${self.tracker.total_historico()} MXN")
        print(f"🎵 Música: 280+ tracks en distribución")
        print(f"💡 DMX: Especialista con baja competencia")
        print(f"🚗 Golf MK7 Turbo: Clases deportivas + experiencias")
        print(f"🏍️ Motocicleta: Clases especializadas")
        print(f"🤖 Xarvis Core: Sistema único sin competencia")
        print("\n🎯 Próximas acciones:")
        for i, accion in enumerate(self.plan.priorizar_acciones_inmediatas()[:3], 1):
            print(f"   {i}. {accion['accion']} - Potencial: {accion['potencial']}")


# Instancia del sistema completo
sepr = EconomiaPersonalReal()

if __name__ == "__main__":
    print("🦅 SISTEMA DE ECONOMÍA PERSONAL REAL")
    print("=" * 70)
    print("Arquitecto: Iyari Cancino Gomez")
    print("Filosofía: 'Primero levantar. El sistema gira en mí.'")
    print("=" * 70)
    
    sepr.inicializar_con_datos_reales()
    
    print("\n📊 Dashboard disponible en:")
    print("   Python: from economia_personal_real import sepr; sepr.dashboard()")
