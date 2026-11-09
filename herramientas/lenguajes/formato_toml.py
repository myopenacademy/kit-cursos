"""El comprobador de los ficheros TOML (para verificar_codigo.py; no se ejecuta a mano).

Que el fichero sea TOML válido (TOML 1.0), con tomllib, de la biblioteca de Python desde la 3.11.
"""
import re
import tomllib

EXTENSIONES = {".toml"}


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def cargar(fichero, carpeta=None):
    return tomllib.loads(fichero.read_text(encoding="utf-8"))


def errores(fichero, carpeta=None):
    """[(línea, qué)] si no es válido; [] si lo es."""
    try:
        cargar(fichero)
    except tomllib.TOMLDecodeError as e:
        # tomllib dice «… (at line 3, column 7)»: la línea va aparte y el resto, tal cual
        m = re.search(r"\(at line (\d+), column (\d+)\)", str(e))
        if m:
            return [(int(m.group(1)), f"TOML no válido: {str(e)[:m.start()].strip()} (columna {m.group(2)})")]
        return [(0, f"TOML no válido: {e}")]
    except UnicodeDecodeError:
        return [(0, "no está en UTF-8")]
    return []
