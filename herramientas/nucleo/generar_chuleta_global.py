#!/usr/bin/env python3
"""Genera 99-chuleta-global.md reuniendo la sección «## 6. Chuleta» de todos los módulos disponibles.

Sale de herramientas/generar_chuleta_global.py del curso de Java, con dos cambios: la lista de fases y
módulos (y sus títulos) sale de curso.json, y la chuleta de cada módulo termina en la sección siguiente
(«## 7. Preguntas de repaso»), no solo en la línea «---» de la navegación.

De cada módulo disponible, en el orden de curso.json, toma su chuleta, baja un nivel sus encabezados y
corrige los enlaces y las imágenes relativos para que funcionen desde la raíz del curso. Los módulos con
"disponible": false se omiten.

Uso, desde la raíz del curso (con el kit en la carpeta hermana ../kit-cursos/):
    python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py              # escribe 99-chuleta-global.md
    python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py --comprobar  # solo dice si está al día
    python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py ../curso-x   # otro curso
    python3 ../kit-cursos/herramientas/nucleo/generar_chuleta_global.py --help

Termina con 0 si la ha generado (o, con --comprobar, si está al día), con 1 si curso.json no se puede
leer (o, con --comprobar, si no está al día) y con 2 si los argumentos están mal.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argumentos import revisar                       # noqa: E402
from formato_academia import Markdown, ancla          # noqa: E402

ENLACE = re.compile(r"(\]\()([^)\s]+)(\))")


def plural(n, uno, varios):
    return f"{n} {uno if n == 1 else varios}"


def corregir_enlaces(linea, modulo, raiz):
    """Los enlaces relativos del módulo, reescritos para que funcionen desde la raíz del curso."""
    def corregir(m):
        destino = m.group(2)
        if re.match(r"^[a-z]+:", destino):           # https:, mailto:…
            return m.group(0)
        if destino.startswith("#"):                   # ancla dentro del propio módulo
            return m.group(1) + modulo.as_posix() + destino + m.group(3)
        ruta, _, seccion = destino.partition("#")
        nueva = os.path.relpath(os.path.normpath(os.path.join(modulo.parent.as_posix(), ruta)), ".").replace(os.sep, "/")
        return m.group(1) + nueva + ("#" + seccion if seccion else "") + m.group(3)
    return ENLACE.sub(corregir, linea)


def chuleta(raiz, fichero):
    """La sección de chuleta del módulo, lista para la chuleta global, o None si no la tiene."""
    md = Markdown(raiz / fichero, fichero)
    inicio = next((i for i, n, t in md.encabezados if n == 2 and t == "6. Chuleta"), None)
    if inicio is None:
        return None
    fin = next((i for i, n, _ in md.encabezados if n <= 2 and i > inicio), len(md.lineas))
    cuerpo = []
    for i in range(inicio + 1, fin):
        linea = md.lineas[i]
        if not md.en_codigo[i] and linea.strip() == "---":   # separador previo a la navegación
            break
        if not md.en_codigo[i]:
            if linea.startswith("#"):
                linea = "#" + linea
            linea = corregir_enlaces(linea, Path(fichero), raiz)
        cuerpo.append(linea)
    texto = "\n".join(cuerpo).strip("\n")
    return texto or None


def generar(raiz):
    curso = json.loads((raiz / "curso.json").read_text(encoding="utf-8"))
    secciones, indice, n = [], [], 0
    for fase in curso.get("fases", []):
        partes = []
        for modulo in fase.get("modulos", []):
            fichero = modulo.get("fichero")
            if not modulo.get("disponible", True) or not fichero or not (raiz / fichero).is_file():
                continue
            texto = chuleta(raiz, fichero)
            if not texto:
                continue
            titulo = f"{fase['carpeta'][5:7]}.{Path(fichero).name[:2]} {modulo['titulo']}"
            partes.append((titulo, fichero, texto))
        if not partes:
            continue
        nombre_fase = f"Fase {fase['carpeta'][5:7]} — {fase['titulo']}"
        indice.append(f"- **{nombre_fase}**")
        secciones.append(f"## {nombre_fase}")
        for titulo, fichero, texto in partes:
            n += 1
            indice.append(f"  - [{titulo}](#{ancla(titulo)})")
            secciones.append(f"### {titulo}\n\n📖 Módulo completo: [{fichero}]({fichero})\n\n{texto}")
    contenido = "\n".join([
        "# Chuleta global",
        "",
        "> Todas las chuletas de los módulos del curso, reunidas en un solo fichero para consultarlas rápido.",
        "> Se genera con `generar_chuleta_global.py` del kit de cursos: no lo edites a mano.",
        "",
        "📚 [Índice del curso](00-indice.md) · 🏠 [Portada](README.md)",
        "",
        "## Contenido",
        "",
        *(indice or ["Todavía no hay ningún módulo disponible."]),
        "",
        "---",
        "",
        "\n\n---\n\n".join(secciones),
        "",
        "---",
        "📚 [Índice del curso](00-indice.md) · 🏠 [Portada](README.md)",
        "",
    ])
    return contenido, n


def main():
    usadas, _, sueltos = revisar(__doc__, opciones=("--comprobar",), maximo=1)
    raiz = Path(sueltos[0]) if sueltos else Path(".")
    anterior = Path.cwd()
    try:
        os.chdir(raiz)                       # los enlaces se calculan relativos a la raíz del curso
        contenido, n = generar(Path("."))
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"❌ No se puede generar la chuleta global desde {raiz / 'curso.json'}: {e}. "
              "Comprueba antes el curso con formato_academia.py.", file=sys.stderr)
        sys.exit(1)
    finally:
        os.chdir(anterior)
    destino = raiz / "99-chuleta-global.md"
    if "--comprobar" in usadas:
        actual = destino.read_text(encoding="utf-8") if destino.exists() else ""
        if actual != contenido:
            print(f"❌ {destino} no está al día: genérala con generar_chuleta_global.py.")
            sys.exit(1)
        print(f"✅ {destino} está al día.")
        return
    destino.write_text(contenido, encoding="utf-8")
    print(f"✅ Generado {destino} con {plural(n, 'módulo', 'módulos')}.")


if __name__ == "__main__":
    main()
