#!/usr/bin/env python3
"""Genera RUTA-MINIMA.md a partir de «ruta_minima» de curso.json.

Sale de herramientas/generar_indice.py del curso de Java, que tenía la ruta mínima en una lista dentro del
script y su texto escrito en el código; aquí la lista es «ruta_minima» de curso.json y el texto propio del
curso va en su plantilla (FORMATO.md, apartados 3.2 y 4):

    "ruta_minima": {
      "modulos": ["java.que-es-programar", …],     los módulos de la ruta (obligatorio)
      "etapas": ["java.etapa.consola", …],          las etapas del proyecto que entran (opcional)
      "plantilla": "RUTA-MINIMA.plantilla.md"       el texto del curso (opcional)
    }

La plantilla es un .md de la raíz del curso con estos huecos, que se rellenan así:
    {{resumen}}    módulos y horas de la ruta, frente a los del curso entero, y sus etapas del proyecto;
    {{modulos}}    obligatorio: por fase, la tabla de sus módulos de la ruta con su tiempo y los que se
                   quedan fuera (o «Fuera de la ruta», si no entra ninguno);
    {{proyecto}}   la tabla de las etapas del proyecto de la ruta;
    {{consultas}}  las consultas puntuales: los módulos que no están en la ruta, pero que algún módulo de
                   la ruta enlaza en «Conviene saber antes» (o «Requisitos previos»), y quién los pide.
Cualquier otro hueco es un error (como en formato_academia.py). Sin plantilla, se usa un texto genérico con
las cuatro partes. Los módulos con "disponible": false aparecen sin enlace y con «—» de tiempo, y las
horas son las de los módulos disponibles (las de su cabecera, como en el índice).

Uso, desde la raíz del curso (con el kit en la carpeta hermana ../kit-cursos/):
    python3 ../kit-cursos/herramientas/nucleo/generar_ruta_minima.py              # escribe RUTA-MINIMA.md
    python3 ../kit-cursos/herramientas/nucleo/generar_ruta_minima.py --comprobar  # solo dice si está al día
    python3 ../kit-cursos/herramientas/nucleo/generar_ruta_minima.py ../curso-x   # otro curso
    python3 ../kit-cursos/herramientas/nucleo/generar_ruta_minima.py --help

Termina con 0 si lo ha generado (o, con --comprobar, si está al día); con 1 si curso.json no tiene
«ruta_minima», si no se puede leer o la ruta o su plantilla tienen un error (o, con --comprobar, si
RUTA-MINIMA.md falta o no está al día); y con 2 si los argumentos están mal.
RUTA-MINIMA.md no se edita a mano: después de cambiar la ruta, vuelve a generarlo, y también el índice
(generar_indice.py marca con 🧭 los módulos de la ruta).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argumentos import revisar                                  # noqa: E402
from formato_academia import HUECO, HUECOS_RUTA_MINIMA          # noqa: E402
from generar_indice import datos_del_modulo, numero, plural     # noqa: E402

# La línea de la cabecera de un módulo con los módulos que conviene saber antes («Requisitos previos» en los
# cursos escritos antes de FORMATO.md, como el de Java) y sus enlaces a otros .md (sin el ancla).
CONVIENE = re.compile(r"\*\*(Conviene saber antes|Requisitos previos):\*\*")
ENLACE_MD = re.compile(r"\]\(([^)#]+\.md)")

GENERICA = """# 🧭 Ruta mínima — {titulo}

{{{{resumen}}}}

La ruta mínima es **lo imprescindible del curso**, en orden. Los demás módulos amplían lo que sabes: los puedes hacer después, en cualquier orden.

🏠 [Portada](README.md) · 📚 [Índice](00-indice.md) (los módulos de la ruta llevan 🧭)

## Cómo seguirla

- **En el orden de las tablas**, que es el del curso: cada módulo usa lo de los anteriores.
- **El proyecto**: las etapas de la ruta, al terminar su fase. Es lo que luego enseñarás en tu portfolio.
- **Las consultas puntuales**: a veces un módulo de la ruta enlaza a otro que no está en ella. No hace falta hacer ese módulo entero: cuando llegues al enlace, **léelo por encima**, buscando lo que el texto menciona, y sigue. Están todas en [la tabla del final](#consultas-puntuales).

## Los módulos

{{{{modulos}}}}

## El proyecto

{{{{proyecto}}}}

## Consultas puntuales

Los módulos que no están en la ruta, pero que algún módulo de la ruta pide en «Conviene saber antes». Cuando llegues al enlace, léelo por encima buscando lo que el texto menciona (o hazlo entero si te interesa).

{{{{consultas}}}}

---
{pie}
"""


class ErrorDeRuta(Exception):
    """Un error de la ruta mínima o de su plantilla que hay que arreglar en el curso."""


def leer_plantilla(raiz, nombre):
    """El texto de la plantilla, después de comprobar sus huecos (los mismos que formato_academia.py)."""
    texto = (raiz / nombre).read_text(encoding="utf-8")
    admitidos = ", ".join("{{" + h + "}}" for h in sorted(HUECOS_RUTA_MINIMA))
    for n, linea in enumerate(texto.split("\n"), 1):
        for m in HUECO.finditer(linea):
            if m.group(1) not in HUECOS_RUTA_MINIMA:
                raise ErrorDeRuta(f"{nombre}:{n}: el hueco {m.group(0)} no existe (se admiten {admitidos})")
    if "{{modulos}}" not in texto:
        raise ErrorDeRuta(f"{nombre}: falta {{{{modulos}}}}, el hueco donde va la lista de módulos de la ruta mínima")
    return texto


def consultas_puntuales(raiz, modulos, en_ruta):
    """{fichero de un módulo fuera de la ruta: [números de los módulos de la ruta que lo enlazan]}."""
    raiz_real = raiz.resolve()
    consultas = {}
    for fichero, (n, _, _, dentro, disponible) in modulos.items():
        ruta = raiz / fichero
        if not dentro or not disponible or not ruta.is_file():
            continue
        cabecera = ruta.read_text(encoding="utf-8").split("\n## ", 1)[0]
        linea = next((l for l in cabecera.split("\n") if CONVIENE.search(l)), "")
        for enlace in ENLACE_MD.findall(linea):
            if "://" in enlace:
                continue
            try:
                destino = (ruta.parent / enlace).resolve().relative_to(raiz_real).as_posix()
            except ValueError:
                continue
            if destino in modulos and destino not in en_ruta:
                consultas.setdefault(destino, []).append(n)
    return consultas


def generar(raiz):
    """(texto de RUTA-MINIMA.md, (módulos de la ruta, sus horas, consultas puntuales))."""
    curso = json.loads((raiz / "curso.json").read_text(encoding="utf-8"))
    ruta = curso.get("ruta_minima")
    if ruta is None:
        raise ErrorDeRuta(f"{raiz / 'curso.json'} no tiene «ruta_minima»: no hay ruta mínima que generar "
                          "(FORMATO.md, apartado 3.2)")
    if not isinstance(ruta, dict) or not isinstance(ruta.get("modulos"), list) or not ruta["modulos"]:
        raise ErrorDeRuta("«ruta_minima» debe ser un objeto con «modulos», una lista con al menos un módulo")
    fases = curso.get("fases", [])
    proyecto = curso.get("proyecto") or {}
    etapas = proyecto.get("etapas", []) if proyecto.get("tipo") == "etapas" else []

    ids = {m["id"] for f in fases for m in f.get("modulos", [])}
    ids_etapas = {e["id"] for e in etapas}
    for ident in ruta["modulos"]:
        if ident not in ids:
            raise ErrorDeRuta(f"«ruta_minima»: el módulo «{ident}» no existe en el curso")
    for ident in ruta.get("etapas") or []:
        if ident not in ids_etapas:
            raise ErrorDeRuta(f"«ruta_minima»: la etapa «{ident}» no existe en el curso")
    en_ruta_ids, etapas_ruta = set(ruta["modulos"]), set(ruta.get("etapas") or [])

    # fichero → (número «02.01», título, horas o None, en la ruta, disponible)
    modulos, por_fase = {}, []
    for fase in fases:
        nf = fase["carpeta"][5:7]
        filas = []
        for m in fase.get("modulos", []):
            fichero = m.get("fichero") or ""
            disponible = m.get("disponible", True)
            horas = datos_del_modulo(raiz / fichero)[1] if disponible and fichero else None
            dato = (f"{nf}.{Path(fichero).name[:2] if fichero else '??'}", m["titulo"], horas, m["id"] in en_ruta_ids, disponible)
            modulos[fichero] = dato
            filas.append((fichero, *dato))
        por_fase.append((fase, nf, filas))
    en_ruta = {f for f, d in modulos.items() if d[3]}

    def horas(filas):
        return sum(h or 0 for _, _, _, h, _, _ in filas)

    def enlace(fichero, titulo, disponible):
        return f"[{titulo}]({fichero})" if disponible else titulo

    # {{resumen}}
    de_la_ruta = [f for _, _, filas in por_fase for f in filas if f[4]]
    horas_ruta = horas(de_la_ruta)
    horas_curso = horas([f for _, _, filas in por_fase for f in filas])
    numeros_etapas = [i for i, e in enumerate(etapas, 1) if e["id"] in etapas_ruta]
    resumen = (f"> **{plural(len(de_la_ruta), 'módulo', 'módulos')}" + (f" · ~{numero(horas_ruta)} h" if horas_ruta else "")
               + f"** (el curso entero: {plural(len(modulos), 'módulo', 'módulos')}"
               + (f", ~{numero(horas_curso)} h" if horas_curso else "") + ")")
    if len(numeros_etapas) == 1:
        resumen += f" · **Proyecto:** etapa {numeros_etapas[0]}"
    elif numeros_etapas:
        resumen += f" · **Proyecto:** etapas {', '.join(map(str, numeros_etapas[:-1]))} y {numeros_etapas[-1]}"
    pendientes = [f for f in de_la_ruta if not f[5]]
    if pendientes:
        resumen += (f"\n> **Disponibles:** {len(de_la_ruta) - len(pendientes)} de los {len(de_la_ruta)} módulos de la ruta "
                    "(los demás aparecen como «Pendiente»)")

    # {{modulos}}
    bloques = []
    for fase, nf, filas in por_fase:
        dentro = [f for f in filas if f[4]]
        fuera = [f for f in filas if not f[4]]
        b = [f"### Fase {nf} — {fase['titulo']}", ""]
        if not dentro:
            h = horas(fuera)
            b.append(f"**Fuera de la ruta** ({plural(len(fuera), 'módulo', 'módulos')}" + (f", ~{numero(h)} h" if h else "")
                     + "): para después.")
            bloques.append("\n".join(b))
            continue
        b += ["| # | Módulo | Tiempo |", "|---|---|---|"]
        for fichero, n, titulo, h, _, disponible in dentro:
            b.append(f"| {n} | {enlace(fichero, titulo, disponible)} | {numero(h) + ' h' if h else '—'} |")
        b.append("")
        pie = [f"**~{numero(horas(dentro))} h**"] if horas(dentro) else []
        if fuera:
            pie.append("Fuera de la ruta: " + ", ".join(f[1] for f in fuera))
        if pie:
            b.append(" · ".join(pie))
        else:
            b.pop()
        bloques.append("\n".join(b))
    texto_modulos = "\n\n".join(bloques)

    # {{proyecto}}
    if numeros_etapas:
        filas = ["| Etapa | Qué se construye |", "|---|---|"]
        for i in numeros_etapas:
            e = etapas[i - 1]
            filas.append(f"| ◆ {i} | {enlace(e['fichero'], e['titulo'], (raiz / e['fichero']).is_file())} |")
        texto_proyecto = "\n".join(filas)
    else:
        texto_proyecto = "Ninguna etapa del proyecto entra en la ruta mínima."

    # {{consultas}}
    consultas = consultas_puntuales(raiz, modulos, en_ruta)
    if consultas:
        filas = ["| Módulo | Lo piden |", "|---|---|"]
        for destino in sorted(consultas, key=lambda d: modulos[d][0]):
            n, titulo, _, _, disponible = modulos[destino]
            filas.append(f"| {n} {enlace(destino, titulo, disponible)} | {', '.join(sorted(set(consultas[destino])))} |")
        texto_consultas = "\n".join(filas)
    else:
        texto_consultas = "Ninguna: los módulos de la ruta no piden ninguno que esté fuera de ella."

    nombre = ruta.get("plantilla")
    if nombre:
        plantilla = leer_plantilla(raiz, nombre)
    else:
        primero = next((f for f in de_la_ruta if f[5] and f[0]), None)
        pie = "🏠 [Portada](README.md) · 📚 [Índice](00-indice.md)" + (f" · ➡️ [Primer módulo]({primero[0]})" if primero else "")
        plantilla = GENERICA.format(titulo=curso.get("titulo", ""), pie=pie)
    valores = {"resumen": resumen, "modulos": texto_modulos, "proyecto": texto_proyecto, "consultas": texto_consultas}
    texto = HUECO.sub(lambda m: valores[m.group(1)], plantilla)
    return texto.rstrip("\n") + "\n", (len(de_la_ruta), horas_ruta, len(consultas))


def main():
    usadas, _, sueltos = revisar(__doc__, opciones=("--comprobar",), maximo=1)
    raiz = Path(sueltos[0]) if sueltos else Path(".")
    try:
        texto, (nmodulos, horas, nconsultas) = generar(raiz)
    except ErrorDeRuta as e:
        print(f"❌ {e}. Comprueba antes el curso con formato_academia.py.", file=sys.stderr)
        sys.exit(1)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
        print(f"❌ No se puede generar la ruta mínima desde {raiz / 'curso.json'}: {e}. "
              "Comprueba antes el curso con formato_academia.py.", file=sys.stderr)
        sys.exit(1)
    destino = raiz / "RUTA-MINIMA.md"
    if "--comprobar" in usadas:
        if not destino.exists():
            print(f"❌ Falta {destino}: genéralo con generar_ruta_minima.py.")
            sys.exit(1)
        if destino.read_text(encoding="utf-8") != texto:
            print(f"❌ {destino} no está al día con curso.json: genéralo con generar_ruta_minima.py.")
            sys.exit(1)
        print(f"✅ {destino} está al día.")
        return
    destino.write_text(texto, encoding="utf-8")
    print(f"✅ Generado {destino}: {plural(nmodulos, 'módulo', 'módulos')}" + (f", ~{numero(horas)} h" if horas else "")
          + f", {plural(nconsultas, 'consulta puntual', 'consultas puntuales')}.")


if __name__ == "__main__":
    main()
