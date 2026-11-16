"""El comprobador de los ficheros Markdown de codigo/ (para verificar_codigo.py; no se ejecuta a mano).

Los .md que el curso enseña como ejemplo o solución (un README, unos apuntes): que sus enlaces relativos lleven
a un fichero o carpeta que exista y, si llevan ancla, a un encabezado que exista (como en GitHub); que sus tablas
tengan la fila separadora y el mismo número de columnas en cada fila; y que sus bloques de código estén cerrados.
Los enlaces a internet no se comprueban (la verificación es sin red). Usa el Markdown de formato_academia.py.

Un .md que empieza por una cabecera YAML entre «---» (como las plantillas de issue de GitHub,
.github/ISSUE_TEMPLATE/*.md, o el frontmatter de Jekyll): la cabecera, que debe cerrarse con otra «---» y ser
YAML válido con claves y valores (con formato_yaml, PyYAML), y el resto, como Markdown.

Las etiquetas de Liquid de Jekyll ({{ … }} y {% … %}) son texto: Jekyll las sustituye antes de leer el Markdown y
el kit no ejecuta Jekyll. Así que no se cuentan sus «|» (los filtros, {{ x | upcase }}) como columnas de una tabla,
y no se comprueba un enlace cuyo destino lleva Liquid ([Ver]({{ ruta.url }})).
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from formato_academia import ENLACE, Markdown   # noqa: E402
import formato_yaml                             # noqa: E402

EXTENSIONES = {".md", ".markdown"}
LIQUID_VALOR = re.compile(r"\{\{.*?\}\}")         # {{ ruta.nombre }}: escribe un valor
LIQUID_ETIQUETA = re.compile(r"\{%.*?%\}")        # {% for … %}: no escribe nada
SEPARADORA = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$")


def es_mio(fichero):
    return fichero.suffix.lower() in EXTENSIONES


def sin_liquid(linea):
    """La línea como la deja Jekyll, más o menos: cada {{ … }}, un valor («x»), y cada {% … %}, nada."""
    return LIQUID_ETIQUETA.sub("", LIQUID_VALOR.sub("x", linea))


def columnas(linea):
    celdas = re.sub(r"\\\|", "", sin_liquid(linea).strip())
    celdas = celdas[1:] if celdas.startswith("|") else celdas
    celdas = celdas[:-1] if celdas.endswith("|") else celdas
    return len(celdas.split("|"))


def cabecera(lineas):
    """Si el fichero empieza por «---», el índice de la línea que la cierra («---» o «...»); -1 si no se cierra;
    None si no tiene cabecera."""
    if not lineas or lineas[0].rstrip() != "---":
        return None
    return next((i for i in range(1, len(lineas)) if lineas[i].rstrip() in ("---", "...")), -1)


def errores_de_cabecera(lineas, fin):
    if fin == -1:
        return [(1, "Markdown: la cabecera YAML que empieza en la línea 1 con «---» no se cierra con otra «---»")]
    if formato_yaml.yaml is None:
        raise formato_yaml.SinPyYAML("falta PyYAML para comprobar las cabeceras YAML de los .md (en Ubuntu, "
                                     "python3-yaml; con pip, pyyaml)")
    try:
        datos = formato_yaml.yaml.safe_load("\n".join(lineas[1:fin]))
    except formato_yaml.yaml.YAMLError as e:
        marca = getattr(e, "problem_mark", None)
        problema = getattr(e, "problem", None) or str(e).split("\n")[0]
        return [((marca.line + 2) if marca else 1, f"cabecera YAML no válida: {problema}"
                 + (f" (columna {marca.column + 1})" if marca else ""))]
    if not isinstance(datos, dict):
        return [(1, "la cabecera YAML entre «---» debe tener claves y valores (name: …, about: …)")]
    return []


def errores(fichero, carpeta=None):
    md = Markdown(fichero, fichero.name)
    problemas = []
    fin = cabecera(md.lineas)
    if fin is not None:
        problemas += errores_de_cabecera(md.lineas, fin)
        for i in range(len(md.lineas) if fin == -1 else fin + 1):
            md.en_codigo[i] = True          # la cabecera no es Markdown: ni enlaces ni tablas
    if md.sin_cerrar is not None:
        problemas.append((md.sin_cerrar + 1, "Markdown: bloque de código sin cerrar"))
    # Enlaces
    for i in range(len(md.lineas)):
        linea = md.texto_sin_codigo(i)
        for m in ENLACE.finditer(linea):
            destino = m.group(3)
            if not destino or re.match(r"^[a-z]+:", destino) or "{{" in destino or "{%" in destino:
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
        if not md.en_codigo[i] and "|" in sin_liquid(md.lineas[i]) and SEPARADORA.match(md.lineas[i + 1]) and "-" in md.lineas[i + 1]:
            n = columnas(md.lineas[i])
            if columnas(md.lineas[i + 1]) != n:
                problemas.append((i + 2, f"Markdown: la fila separadora de la tabla tiene {columnas(md.lineas[i + 1])} columnas y la cabecera {n}"))
            j = i + 2
            while j < len(md.lineas) and "|" in sin_liquid(md.lineas[j]) and md.lineas[j].strip() and not md.en_codigo[j]:
                if columnas(md.lineas[j]) != n:
                    problemas.append((j + 1, f"Markdown: la fila de la tabla tiene {columnas(md.lineas[j])} columnas y la cabecera {n}"))
                j += 1
            i = j
        else:
            i += 1
    return problemas
