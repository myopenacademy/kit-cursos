"""El comprobador de los ficheros JSON (para verificar_codigo.py; no se ejecuta a mano).

Que el fichero sea JSON válido, con la biblioteca de Python. Cada error, con su línea y su columna.
"""
import json

EXTENSIONES = {".json"}


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def cargar(fichero, carpeta=None):
    return json.loads(fichero.read_text(encoding="utf-8"))


def errores(fichero, carpeta=None):
    """[(línea, qué)] si no es válido; [] si lo es."""
    try:
        cargar(fichero)
    except json.JSONDecodeError as e:
        return [(e.lineno, f"JSON no válido: {e.msg} (columna {e.colno})")]
    except UnicodeDecodeError:
        return [(0, "no está en UTF-8")]
    return []
