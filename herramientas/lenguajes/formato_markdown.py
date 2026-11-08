"""El comprobador de los ficheros Markdown de codigo/ (para verificar_codigo.py; no se ejecuta a mano).

Los .md que el curso enseña como ejemplo o solución (un README, unos apuntes): que sus enlaces relativos lleven
a un fichero o carpeta que exista y, si llevan ancla, a un encabezado que exista (como en GitHub); que sus tablas
tengan la fila separadora y el mismo número de columnas en cada fila; y que sus bloques de código estén cerrados.
Los enlaces a internet no se comprueban (la verificación es sin red). Usa el Markdown de formato_academia.py.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from formato_academia import ENLACE, Markdown   # noqa: E402

EXTENSIONES = {".md", ".markdown"}
SEPARADORA = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$")


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def columnas(linea):
    celdas = re.sub(r"\\\|", "", linea.strip())
    celdas = celdas[1:] if celdas.startswith("|") else celdas
    celdas = celdas[:-1] if celdas.endswith("|") else celdas
    return len(celdas.split("|"))


def errores(fichero, carpeta=None):
    md = Markdown(fichero, fichero.name)
    problemas = []
    if md.sin_cerrar is not None:
        problemas.append((md.sin_cerrar + 1, "Markdown: bloque de código sin cerrar"))
    # Enlaces
    for i in range(len(md.lineas)):
        linea = md.texto_sin_codigo(i)
        for m in ENLACE.finditer(linea):
            destino = m.group(3)
            if not destino or re.match(r"^[a-z]+:", destino):
                continue
            ruta, _, seccion = destino.partition("#")
            objetivo = (fichero.parent / unquote(ruta)).resolve() if ruta else fichero.resolve()
            if not objetivo.exists():
                problemas.append((i + 1, f"Markdown: no existe {destino}"))
            elif seccion and objetivo.suffix == ".md" and unquote(seccion) not in Markdown(objetivo, objetivo.name).anclas():
                problemas.append((i + 1, f"Markdown: no existe la sección #{seccion}"))
    # Tablas: una fila con «|» seguida de la separadora empieza una tabla, que sigue mientras haya «|»
    i = 0
    while i < len(md.lineas) - 1:
        if not md.en_codigo[i] and "|" in md.lineas[i] and SEPARADORA.match(md.lineas[i + 1]) and "-" in md.lineas[i + 1]:
            n = columnas(md.lineas[i])
            if columnas(md.lineas[i + 1]) != n:
                problemas.append((i + 2, f"Markdown: la fila separadora de la tabla tiene {columnas(md.lineas[i + 1])} columnas y la cabecera {n}"))
            j = i + 2
            while j < len(md.lineas) and "|" in md.lineas[j] and md.lineas[j].strip() and not md.en_codigo[j]:
                if columnas(md.lineas[j]) != n:
                    problemas.append((j + 1, f"Markdown: la fila de la tabla tiene {columnas(md.lineas[j])} columnas y la cabecera {n}"))
                j += 1
            i = j
        else:
            i += 1
    return problemas
