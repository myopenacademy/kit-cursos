#!/usr/bin/env python3
"""Genera 00-indice.md a partir de curso.json.

Sale de herramientas/generar_indice.py del curso de Java, que tenía la lista de fases y módulos dentro
del script; aquí la lista es curso.json (FORMATO.md, apartado 3). El nivel y el tiempo de cada módulo
se leen de su cabecera («> **Nivel:**» y «> **Tiempo estimado:**», FORMATO.md, apartado 5.2), así que
solo los tienen los módulos disponibles; los que tienen "disponible": false aparecen como «Pendiente»,
sin enlace. Lo mismo los retos de cada fase y las etapas del proyecto.

El índice lleva un encabezado «## Fase NN — Título» por fase, que es lo que lee la academia, y los
títulos son los de curso.json.

Uso, desde la raíz del curso (con el kit en la carpeta hermana ../kit-cursos/):
    python3 ../kit-cursos/herramientas/nucleo/generar_indice.py              # escribe 00-indice.md
    python3 ../kit-cursos/herramientas/nucleo/generar_indice.py --comprobar  # solo dice si está al día
    python3 ../kit-cursos/herramientas/nucleo/generar_indice.py ../curso-x   # otro curso
    python3 ../kit-cursos/herramientas/nucleo/generar_indice.py --help

Termina con 0 si lo ha generado (o, con --comprobar, si está al día), con 1 si curso.json no se puede
leer (o, con --comprobar, si el índice no está al día) y con 2 si los argumentos están mal.
Después de cambiar el temario, actualiza también el plan, los roadmaps y el estado del curso.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argumentos import revisar          # noqa: E402
from formato_academia import ancla       # noqa: E402

CABECERA = re.compile(r"^>\s*\*\*(Nivel|Tiempo estimado):\*\*\s*(.+?)\s*$")


def datos_del_modulo(ruta):
    """Nivel y horas (como número) de la cabecera de un módulo, o (None, None)."""
    nivel = horas = None
    try:
        lineas = ruta.read_text(encoding="utf-8").split("\n")[:15]
    except OSError:
        return None, None
    for linea in lineas:
        m = CABECERA.match(linea)
        if m and m.group(1) == "Nivel":
            nivel = m.group(2)
        elif m:
            h = re.match(r"^(\d+(?:,\d+)?) horas?$", m.group(2))
            if h:
                horas = float(h.group(1).replace(",", "."))
    return nivel, horas


def plural(n, singular, plural_):
    return f"{n} {singular if n == 1 else plural_}"


def numero(horas):
    """1.5 → «1,5»; 2.0 → «2»."""
    texto = f"{horas:.1f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def generar(raiz):
    curso = json.loads((raiz / "curso.json").read_text(encoding="utf-8"))
    fases = curso.get("fases", [])
    partes = curso.get("partes") or []
    proyecto = curso.get("proyecto") or {}
    modulos = [m for f in fases for m in f.get("modulos", [])]
    disponibles = [m for m in modulos if m.get("disponible", True)]

    datos, total_horas, horas_por_fase = {}, 0.0, {}
    for fase in fases:
        horas_fase = 0.0
        for m in fase.get("modulos", []):
            if m.get("disponible", True) and m.get("fichero"):
                datos[m["id"]] = datos_del_modulo(raiz / m["fichero"])
                horas_fase += datos[m["id"]][1] or 0
        horas_por_fase[fase["id"]] = horas_fase
        total_horas += horas_fase

    lineas = []
    w = lineas.append
    w(f"# Índice — {curso.get('titulo', '')}")
    w("")
    w(f"> **{plural(len(fases), 'fase', 'fases')} · {plural(len(modulos), 'módulo', 'módulos')}**"
      + (f" · {plural(len(proyecto.get('etapas', [])), 'etapa', 'etapas')} del proyecto" if proyecto.get("tipo") == "etapas" else ""))
    if len(disponibles) < len(modulos):
        w(f"> **Disponibles:** {len(disponibles)} de {len(modulos)} módulos (los demás aparecen como «Pendiente»)")
    else:
        w(f"> **Disponibles:** los {len(modulos)} módulos")
    w("")
    if curso.get("descripcion"):
        w(curso["descripcion"])
        w("")
    w("Cada módulo indica su nivel, si es **núcleo** (imprescindible) o **ampliación** (para profundizar más adelante) "
      "y un tiempo estimado de estudio, incluidos los ejercicios. Los **retos** del final de cada fase son opcionales.")
    w("")
    enlaces = ["🏠 [Portada](README.md)"]
    if (raiz / "ROADMAP.md").exists():
        enlaces.append("🗺️ [Ruta de aprendizaje](ROADMAP.md)")
    if (raiz / "99-chuleta-global.md").exists():
        enlaces.append("📋 [Chuleta global](99-chuleta-global.md)")
    w(" · ".join(enlaces))
    w("")
    w("## Contenido")
    w("")

    def linea_de_fase(fase):
        n = fase["carpeta"][5:7]
        encabezado = f"Fase {n} — {fase['titulo']}"
        horas = horas_por_fase[fase["id"]]
        return (f"- [{encabezado}](#{ancla(encabezado)}) · {plural(len(fase.get('modulos', [])), 'módulo', 'módulos')}"
                + (f" · ~{numero(horas)} h" if horas else ""))

    if partes:
        for parte in partes:
            w(f"**{parte['titulo']}**")
            w("")
            for fase in fases:
                if fase["id"] in parte.get("fases", []):
                    w(linea_de_fase(fase))
            w("")
    else:
        for fase in fases:
            w(linea_de_fase(fase))
        w("")
    if proyecto.get("tipo") == "etapas":
        w(f"- [Proyecto: {proyecto.get('titulo', '')}](#{ancla('Proyecto: ' + proyecto.get('titulo', ''))}) · "
          f"{plural(len(proyecto.get('etapas', [])), 'etapa', 'etapas')}")
        w("")
    if total_horas:
        w(f"**Tiempo de los módulos disponibles:** ~{numero(total_horas)} horas.")
        w("")

    modulo_proyecto = proyecto.get("modulo") if proyecto.get("tipo") == "modulo" else None
    for fase in fases:
        n = fase["carpeta"][5:7]
        w("---")
        w("")
        w(f"## Fase {n} — {fase['titulo']}")
        w("")
        horas = horas_por_fase[fase["id"]]
        carpeta = (f"[`{fase['carpeta']}/`]({fase['carpeta']}/)" if (raiz / fase["carpeta"]).is_dir()
                   else f"`{fase['carpeta']}/` (todavía no existe)")
        w(f"**Carpeta:** {carpeta}" + (f" · **Tiempo:** ~{numero(horas)} h" if horas else ""))
        w("")
        w("| # | Módulo | Nivel | Tiempo | Estado |")
        w("|---|---|---|---|---|")
        for m in fase.get("modulos", []):
            fichero = m.get("fichero") or ""
            nm = Path(fichero).name[:2] if fichero else "??"
            marca = "🎯 " if m.get("id") == modulo_proyecto else ""
            if m.get("disponible", True):
                nivel, h = datos.get(m["id"], (None, None))
                w(f"| {n}.{nm} | {marca}[{m['titulo']}]({fichero}) | {nivel or '—'} | "
                  f"{numero(h) + ' h' if h else '—'} | ✅ Disponible |")
            else:
                w(f"| {n}.{nm} | {marca}{m['titulo']} | — | — | Pendiente |")
        if fase.get("retos"):
            if fase.get("retos_disponibles", True):
                w(f"| | [Retos de la fase]({fase['retos']}) | | | ✅ Disponible |")
            else:
                w("| | Retos de la fase | | | Pendiente |")
        w("")
        if modulo_proyecto and any(m.get("id") == modulo_proyecto for m in fase.get("modulos", [])):
            w("🎯 El proyecto final del curso, para tu portfolio.")
            w("")

    if proyecto.get("tipo") == "etapas":
        w("---")
        w("")
        w(f"## Proyecto: {proyecto.get('titulo', '')}")
        w("")
        w("Un proyecto para tu portfolio que crece a lo largo del curso. Carpeta: [`proyecto/`](proyecto/).")
        w("")
        w("| Etapa | Qué se construye | Estado |")
        w("|---|---|---|")
        for i, etapa in enumerate(proyecto.get("etapas", []), 1):
            if (raiz / etapa["fichero"]).exists():
                w(f"| ◆ {i} | [{etapa['titulo']}]({etapa['fichero']}) | ✅ Disponible |")
            else:
                w(f"| ◆ {i} | {etapa['titulo']} | Pendiente |")
        w("")

    primero = next((m for m in modulos if m.get("disponible", True) and m.get("fichero")), None)
    w("---")
    w("🏠 [Portada](README.md)" + (f" · ➡️ [Primer módulo]({primero['fichero']})" if primero else ""))
    return "\n".join(lineas) + "\n", len(fases), len(modulos)


def main():
    usadas, _, sueltos = revisar(__doc__, opciones=("--comprobar",), maximo=1)
    raiz = Path(sueltos[0]) if sueltos else Path(".")
    try:
        texto, nfases, nmodulos = generar(raiz)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"❌ No se puede generar el índice desde {raiz / 'curso.json'}: {e}. "
              "Comprueba antes el curso con formato_academia.py.", file=sys.stderr)
        sys.exit(1)
    destino = raiz / "00-indice.md"
    if "--comprobar" in usadas:
        actual = destino.read_text(encoding="utf-8") if destino.exists() else ""
        if actual != texto:
            print(f"❌ {destino} no está al día con curso.json: genéralo con generar_indice.py.")
            sys.exit(1)
        print(f"✅ {destino} está al día.")
        return
    destino.write_text(texto, encoding="utf-8")
    print(f"✅ Generado {destino}: {plural(nfases, 'fase', 'fases')}, {plural(nmodulos, 'módulo', 'módulos')}.")


if __name__ == "__main__":
    main()
