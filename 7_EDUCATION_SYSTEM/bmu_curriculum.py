
class BMUCurriculum:
    def __init__(self):
        self.university = "BlackMamba University (BMU)"
        
    def get_foundation_stage(self):
        """
        La Primera Etapa: Lo esencial para la vida y la soberanía personal.
        Depende de la edad, pero es la base de todo estudiante BMU.
        """
        return {
            "nombre": "Cimientos de Soberanía",
            "materias_vitales": [
                "Arquitectura del Hogar (Cómo hacer tu casa)",
                "Gastronomía de Supervivencia y Nutrición (La Cocina)",
                "Orden del Entorno (Limpieza e Higiene)",
                "Responsabilidad Individual e Integridad",
                "Ética y Moral del Conocimiento Real"
            ],
            "especialidad_temprana": "Tu materia o conocimiento favorito (Pasión Pura)"
        }

    def multidisciplinary_path(self, interests):
        """
        Diseña una ruta para estudiantes audaces que buscan 3+ licenciaturas.
        """
        return {
            "objetivo": "Formación de Polímatas / Multidisciplinarios",
            "ruta_sugerida": interests,
            "beneficio": "Sponsorship Total (Costo 0) por Audacia",
            "referencia_excelencia": "https://www.linkedin.com/in/iyari-c/details/certifications/"
        }

# Instancia del currículo BMU
curriculum = BMUCurriculum()
