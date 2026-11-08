"""El comprobador de los ficheros XML (para verificar_codigo.py; no se ejecuta a mano).

Que el fichero sea XML bien formado (etiquetas cerradas y bien anidadas, un solo elemento raíz, atributos con
comillas…), con la biblioteca de Python. No lo valida contra un esquema.
"""
import xml.etree.ElementTree as ET

EXTENSIONES = {".xml"}


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def errores(fichero, carpeta=None):
    try:
        ET.parse(fichero)
    except ET.ParseError as e:
        linea, columna = e.position
        mensaje = str(e).split(":")[0]
        return [(linea, f"XML mal formado: {mensaje} (columna {columna + 1})")]
    return []
