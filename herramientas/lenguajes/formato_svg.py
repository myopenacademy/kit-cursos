"""El comprobador de las imágenes SVG (para verificar_codigo.py; no se ejecuta a mano).

Que el fichero sea XML bien formado (formato_xml.py) y que su elemento raíz sea <svg> con
xmlns="http://www.w3.org/2000/svg": sin él, un navegador no dibuja el fichero como imagen (en un <img> o en
el Markdown de GitHub). Con la biblioteca de Python.

Las imágenes se comprueban siempre: un debe-fallar.txt en su carpeta no les afecta (es para los ficheros de
datos mal a propósito, y la imagen de un ejemplo roto sigue teniendo que verse).
"""
import xml.etree.ElementTree as ET

import formato_xml

EXTENSIONES = {".svg"}
ESPACIO = "{http://www.w3.org/2000/svg}"
SIEMPRE = True      # no le afecta debe-fallar.txt


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def errores(fichero, carpeta=None):
    """[(línea, qué)] si no es válido; [] si lo es."""
    problemas = formato_xml.errores(fichero)
    if problemas:
        return [(linea, mensaje.replace("XML mal formado", "SVG mal formado (es XML)")) for linea, mensaje in problemas]
    raiz = ET.parse(fichero).getroot()
    if raiz.tag == "svg":
        return [(1, 'SVG: a <svg> le falta xmlns="http://www.w3.org/2000/svg" (sin él, el navegador no lo dibuja)')]
    if raiz.tag != ESPACIO + "svg":
        return [(1, f"SVG: el elemento raíz debe ser <svg> y es <{raiz.tag.split('}')[-1]}>")]
    return []
