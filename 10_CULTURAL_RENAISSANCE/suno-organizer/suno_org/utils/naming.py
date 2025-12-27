from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from pathlib import Path


def _strip_accents(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))


def slugify(name: str) -> str:
    # quitar acentos y emojis, normalizar a ascii básico si es posible
    name = _strip_accents(name)
    # reemplazar comillas extrañas y símbolos problemáticos
    name = name.replace('“', '"').replace('”', '"').replace('’', "'")
    # reemplazar separadores raros por espacios
    name = re.sub(r"[\u2600-\u27BF\U0001F300-\U0001FAFF]", " ", name)  # emojis y símbolos
    name = re.sub(r"[\s_]+", " ", name).strip()
    # limpiar caracteres no permitidos en nombres de archivo
    name = re.sub(r"[^A-Za-z0-9\-\. ]+", "", name)
    # compactar espacios y cambiar por guiones
    name = re.sub(r"\s+", " ", name).strip().replace(" ", "-")
    return name or "audio"


def build_suno_filename(created: datetime, title: str, ext: str) -> str:
    date_part = created.strftime("%Y-%m-%d")
    base = slugify(title) if title else "suno"
    return f"{date_part}_{base}_[Suno]{ext}"
