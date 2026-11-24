"""La prueba de fiabilidad del ejecutor de Java del kit con el curso de Java (no es una prueba de unittest: es lenta y
necesita el curso).

Saca un commit fijo del curso de Java («git archive», que solo lee: el repositorio no se toca) a DOS copias
temporales y verifica cada fase (o módulo) que se pida con las dos herramientas:

  - la ORIGINAL: el herramientas/verificar_codigo.py de ESE MISMO COMMIT del curso, en su copia (con el java, mvn y
    gradle del PATH del equipo, como siempre se ha usado);
  - la del KIT: nucleo/verificar_codigo.py de este kit (el de la carpeta en la que está este fichero), en la otra
    copia, con Docker (la imagen de Java del kit, sin red). Antes, «--preparar-java» de lo mismo (la única vez que
    hay red), con la caché en el volumen de Docker de --cache (variable KIT_JAVA_CACHE).

Después compara BLOQUE A BLOQUE, solo en el ámbito del ejecutor de Java: los bloques ```java con su enlace
«📁 **Código:**». Cada error de cada herramienta se asigna al bloque enlazado en cuyo tramo cae su línea (desde el
bloque de código hasta antes del siguiente bloque enlazado: el enlace, la «**Salida:**», la ventana…). Un bloque está
bien si no tiene ningún error; las dos herramientas COINCIDEN si las dos lo dan por bueno o las dos por malo. Se
marcan aparte («fuera del ámbito») los bloques de Java que necesitan lo que el ejecutor del kit no hace: una base de
datos (base-de-datos.txt), un modelo de IA (modelos-ia.txt) o guiones del navegador (navegador-*.txt). Los errores
que no caen en un bloque de Java (SQL, páginas, datos, ficheros sin enlazar…) se cuentan aparte, sin comparar.

Cada objetivo deja en la carpeta de --salida un <objetivo>.json (el resultado por bloque) y la salida completa de
cada herramienta (<objetivo>.original.txt y <objetivo>.kit.txt). Si el .json ya existe, ese objetivo no se repite
(salvo con --repetir): así una prueba larga se puede cortar y seguir. Con --resumen, solo junta los .json que haya y
escribe los totales y la lista de desacuerdos.

Con --ruta-minima, en lugar de verificar código, compara RUTA-MINIMA.md: en una copia del commit, añade a su
curso.json un «ruta_minima» con los módulos y las etapas de las listas RUTA_MINIMA y RUTA_ETAPAS del
herramientas/generar_indice.py de ese commit (leídas con ast, sin ejecutarlo) y una plantilla que es su RUTA-MINIMA.md
con los cuatro huecos en lugar de lo que se genera; la genera con nucleo/generar_ruta_minima.py del kit y deja en
--salida ruta-minima.diff, la diferencia con el RUTA-MINIMA.md del commit.

Uso, desde la raíz del kit:
    python3 herramientas/pruebas/fiabilidad_java.py ../curso-java cfb14f3e fase-02-fundamentos fase-07-java-avanzado
    python3 herramientas/pruebas/fiabilidad_java.py ../curso-java cfb14f3e fase-12-spring-rest-y-persistencia/01-introduccion.md
    python3 herramientas/pruebas/fiabilidad_java.py ../curso-java cfb14f3e --resumen
    python3 herramientas/pruebas/fiabilidad_java.py ../curso-java cfb14f3e --ruta-minima
    python3 herramientas/pruebas/fiabilidad_java.py --help
Termina con 0 si ha podido verificar (y comparar) todos los objetivos, aunque haya desacuerdos; con 1 si alguno no
se ha podido verificar; con 2 si los argumentos están mal.
"""
import argparse
import ast
import difflib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent.parent
VERIFICAR_KIT = KIT / "herramientas" / "nucleo" / "verificar_codigo.py"
SALIDA = KIT / "odd" / "fiabilidad"
CACHE = "kit-java-cache-fiabilidad"

ENLACE = re.compile(r"^📁 \*\*Código:\*\* \[`[^`]+`\]\(([^)]+)\)\s*$")
FENCE = re.compile(r"^(`{3,})(\S*)")
# El principio de un error de la herramienta original («ruta:línea: mensaje» o «ruta: mensaje») y de la del kit
ERROR_ORIGINAL = re.compile(r"^((?:fase-\d\d-[^:\s]+|proyecto[^:\s]*)\S*?)(?::(\d+))?: (.*)$")
ERROR_KIT = re.compile(r"^(\S.*?)(?::(\d+))?: (ERROR|AVISO): (.*)$")
FUERA = (("base-de-datos.txt", "base de datos"), ("modelos-ia.txt", "modelo de IA"))


def git(curso, *argumentos, binario=False):
    r = subprocess.run(["git", "-C", str(curso), *argumentos], capture_output=True, text=not binario)
    if r.returncode != 0:
        raise RuntimeError((r.stderr if not binario else r.stderr.decode(errors="replace")).strip())
    return r.stdout


def sacar(curso, commit, destino):
    """El commit del curso en destino, con git archive (solo lee el repositorio)."""
    tar = git(curso, "archive", "--format=tar", commit, binario=True)
    destino.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino, filter="tar")


# -- los bloques enlazados de un módulo ---------------------------------------------------------------------------

def bloques_enlazados(md):
    """[(lenguaje, línea del bloque, línea del enlace, carpeta enlazada)] de un módulo (líneas desde 1), como los
    leen las dos herramientas: un bloque de código seguido (tras líneas vacías) de su «📁 **Código:**»."""
    lineas = md.read_text(encoding="utf-8").splitlines()
    bloques, i = [], 0
    while i < len(lineas):
        m = FENCE.match(lineas[i])
        if not m:
            i += 1
            continue
        comillas, lenguaje, inicio = m.group(1), m.group(2), i
        fin = i + 1
        while fin < len(lineas) and lineas[fin].rstrip() != comillas:
            fin += 1
        j = fin + 1
        while j < len(lineas) and not lineas[j].strip():
            j += 1
        enlace = ENLACE.match(lineas[j]) if j < len(lineas) else None
        if enlace:
            bloques.append((lenguaje, inicio + 1, j + 1, enlace.group(1)))
        i = fin + 1
    return bloques


def fuera_del_ambito(carpeta):
    """Por qué un bloque de Java de esa carpeta necesita lo que el ejecutor del kit no hace (o None)."""
    for c in [carpeta, *carpeta.parents]:
        if c.name == "codigo":
            break
        for nombre, motivo in FUERA:
            if (c / nombre).is_file():
                return motivo
        if (c / "pom.xml").is_file() and any(c.glob("navegador-*.txt")):
            return "guiones del navegador"
    return None


# -- leer lo que dicen las herramientas ---------------------------------------------------------------------------

def errores_original(salida):
    """[(fichero, línea o 0, mensaje)] de la salida de la herramienta original."""
    if "problema(s):" not in salida:
        return []
    cuerpo = salida.split("problema(s):", 1)[1].splitlines()
    errores, anterior_vacia = [], True
    for linea in cuerpo:
        m = ERROR_ORIGINAL.match(linea) if anterior_vacia else None
        if m:
            errores.append([m.group(1), int(m.group(2) or 0), m.group(3)])
        elif errores:
            errores[-1][2] += "\n" + linea
        anterior_vacia = not linea.strip()
    return [(f, l, m.rstrip()) for f, l, m in errores]


def errores_kit(salida):
    """[(fichero, línea o 0, mensaje)] de los ERROR de la salida del kit (los AVISO no cuentan)."""
    errores, actual = [], None
    for linea in salida.splitlines():
        m = ERROR_KIT.match(linea)
        if m:
            actual = [m.group(1), int(m.group(2) or 0), m.group(4)] if m.group(3) == "ERROR" else None
            if actual:
                errores.append(actual)
        elif actual is not None and (linea.startswith((" ", "\t")) or not linea.strip()):
            actual[2] += "\n" + linea
        else:
            actual = None
    return [(f, l, m.rstrip()) for f, l, m in errores]


def asignar(errores, tramos):
    """Reparte los errores entre los tramos de los bloques ({md: [(desde, hasta, clave)]}); devuelve ({clave:
    [mensajes]}, [errores sin bloque])."""
    por_bloque, sueltos = {}, []
    for f, l, m in errores:
        clave = next((c for desde, hasta, c in tramos.get(f, []) if desde <= l <= hasta), None)
        if clave is None:
            sueltos.append(f"{f}:{l}: {m}" if l else f"{f}: {m}")
        else:
            por_bloque.setdefault(clave, []).append(m)
    return por_bloque, sueltos


# -- un objetivo ----------------------------------------------------------------------------------------------------

def ejecutar(orden, cwd, entorno=None):
    inicio = time.time()
    r = subprocess.run(orden, cwd=cwd, capture_output=True, text=True, env=entorno)
    return r.returncode, r.stdout + ("\n--- stderr ---\n" + r.stderr if r.stderr.strip() else ""), time.time() - inicio


def nombre_de(objetivo):
    return objetivo.rstrip("/").replace("/", "__")


def verificar_objetivo(objetivo, copia_original, copia_kit, salida, preparar, cache):
    nombre = nombre_de(objetivo)
    entorno_kit = {**os.environ, "KIT_JAVA_CACHE": cache}
    resultado = {"objetivo": objetivo}
    print(f"== {objetivo}: herramienta original…", flush=True)
    codigo, texto, segundos = ejecutar([sys.executable, "-I", "herramientas/verificar_codigo.py", objetivo],
                                       copia_original)
    (salida / f"{nombre}.original.txt").write_text(texto, encoding="utf-8")
    resultado["original"] = {"codigo": codigo, "segundos": round(segundos)}
    if preparar:
        print(f"== {objetivo}: --preparar-java del kit…", flush=True)
        codigo_p, texto_p, segundos_p = ejecutar([sys.executable, str(VERIFICAR_KIT), "--preparar-java", objetivo],
                                                 copia_kit, entorno_kit)
        (salida / f"{nombre}.preparar.txt").write_text(texto_p, encoding="utf-8")
        resultado["preparar"] = {"codigo": codigo_p, "segundos": round(segundos_p)}
    print(f"== {objetivo}: kit…", flush=True)
    codigo_k, texto_k, segundos_k = ejecutar([sys.executable, str(VERIFICAR_KIT), objetivo], copia_kit, entorno_kit)
    (salida / f"{nombre}.kit.txt").write_text(texto_k, encoding="utf-8")
    resultado["kit"] = {"codigo": codigo_k, "segundos": round(segundos_k)}

    # Los bloques enlazados de los módulos del objetivo (en la copia del kit, que no cambia: el kit no escribe en ella
    # más que .verificacion/)
    ruta = copia_kit / objetivo
    mds = [ruta] if ruta.is_file() else sorted(ruta.glob("*.md"))
    tramos, bloques = {}, {}
    for md in mds:
        rel = md.relative_to(copia_kit).as_posix()
        enlazados = bloques_enlazados(md)
        for n, (lenguaje, linea, enlace, carpeta) in enumerate(enlazados):
            hasta = enlazados[n + 1][1] - 1 if n + 1 < len(enlazados) else 10 ** 9
            clave = f"{rel}:{enlace}"
            tramos.setdefault(rel, []).append((linea, hasta, clave))
            fuera = None
            if lenguaje == "java":
                destino = (md.parent / carpeta).resolve()
                fuera = fuera_del_ambito(destino) if destino.is_dir() else None
            bloques[clave] = {"md": rel, "bloque": linea, "enlace": enlace, "lenguaje": lenguaje, "fuera": fuera}
    original, sueltos_o = asignar(errores_original(texto), tramos)
    kit, sueltos_k = asignar(errores_kit(texto_k), tramos)
    lista = []
    for clave, b in bloques.items():
        b["original"], b["kit"] = original.get(clave, []), kit.get(clave, [])
        b["coinciden"] = bool(b["original"]) == bool(b["kit"])
        lista.append(b)
    resultado["bloques"] = lista
    resultado["sin_bloque"] = {"original": sueltos_o, "kit": sueltos_k}
    resultado["cuentas"] = cuentas(lista)
    (salida / f"{nombre}.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    c = resultado["cuentas"]
    print(f"== {objetivo}: {c['java']} bloques de Java ({c['fuera']} fuera del ámbito); en el ámbito, "
          f"{c['coinciden']} coinciden y {c['no_coinciden']} no. Original {resultado['original']['segundos']} s, "
          f"kit {resultado['kit']['segundos']} s.", flush=True)
    return codigo in (0, 1) and codigo_k in (0, 1) and resultado.get("preparar", {}).get("codigo", 0) == 0


def cuentas(bloques):
    java = [b for b in bloques if b["lenguaje"] == "java"]
    dentro = [b for b in java if not b["fuera"]]
    return {
        "java": len(java),
        "fuera": len(java) - len(dentro),
        "coinciden": sum(b["coinciden"] for b in dentro),
        "no_coinciden": sum(not b["coinciden"] for b in dentro),
        "bien_los_dos": sum(not b["original"] and not b["kit"] for b in dentro),
        "mal_los_dos": sum(bool(b["original"]) and bool(b["kit"]) for b in dentro),
        "solo_original": sum(bool(b["original"]) and not b["kit"] for b in dentro),
        "solo_kit": sum(not b["original"] and bool(b["kit"]) for b in dentro),
        "otros_lenguajes_con_error": {
            "original": sum(bool(b["original"]) for b in bloques if b["lenguaje"] != "java"),
            "kit": sum(bool(b["kit"]) for b in bloques if b["lenguaje"] != "java"),
        },
    }


def resumen(salida):
    total, desacuerdos = {}, []
    for fichero in sorted(salida.glob("*.json")):
        r = json.loads(fichero.read_text(encoding="utf-8"))
        if "cuentas" not in r:
            continue                    # ruta-minima.json: no es el resultado de un objetivo
        for k, v in r["cuentas"].items():
            if isinstance(v, int):
                total[k] = total.get(k, 0) + v
        print(f"{r['objetivo']}: {json.dumps(r['cuentas'], ensure_ascii=False)}  "
              f"(original {r['original']['segundos']} s, kit {r['kit']['segundos']} s)")
        desacuerdos += [b for b in r["bloques"] if b["lenguaje"] == "java" and not b["fuera"] and not b["coinciden"]]
    print(f"\nTOTAL: {json.dumps(total, ensure_ascii=False)}")
    for b in desacuerdos:
        quien = "solo el original" if b["original"] else "solo el kit"
        mensaje = (b["original"] or b["kit"])[0].splitlines()[0][:200]
        print(f"- {b['md']}:{b['enlace']} ({quien}): {mensaje}")


# -- la ruta mínima ------------------------------------------------------------------------------------------------

def listas_de_la_ruta(generar_indice):
    """(RUTA_MINIMA, RUTA_ETAPAS) del generar_indice.py del curso, leídas sin ejecutarlo."""
    valores = {}
    for nodo in ast.parse(generar_indice.read_text(encoding="utf-8")).body:
        if isinstance(nodo, ast.Assign) and len(nodo.targets) == 1 and isinstance(nodo.targets[0], ast.Name):
            if nodo.targets[0].id in ("RUTA_MINIMA", "RUTA_ETAPAS"):
                valores[nodo.targets[0].id] = ast.literal_eval(nodo.value)
    return valores["RUTA_MINIMA"], valores["RUTA_ETAPAS"]


def plantilla_de(texto):
    """La plantilla que reproduce el RUTA-MINIMA.md original: lo generado, cambiado por sus huecos."""
    lineas = texto.rstrip("\n").split("\n")
    salida, seccion, i = [], None, 0
    while i < len(lineas):
        linea = lineas[i]
        if linea.startswith("## "):
            seccion = linea[3:]
        if seccion is None and linea.startswith("> **"):
            salida.append("{{resumen}}")
        elif seccion == "Los módulos" and not linea.startswith("## "):
            # Todo lo de la sección es generado: un solo hueco, entre líneas vacías
            if "{{modulos}}" not in salida:
                salida += ["{{modulos}}", ""] if linea.strip() else [""]
        elif seccion in ("El proyecto", "Consultas puntuales") and linea.startswith("|"):
            hueco = "{{proyecto}}" if seccion == "El proyecto" else "{{consultas}}"
            if salida[-1] != hueco:
                salida.append(hueco)
        else:
            salida.append(linea)
        i += 1
    return "\n".join(salida) + "\n"


def comparar_ruta_minima(curso, commit, salida):
    trabajo = Path(tempfile.mkdtemp(prefix="fiabilidad-ruta-"))
    try:
        copia = trabajo / "curso"
        sacar(curso, commit, copia)
        ruta, etapas = listas_de_la_ruta(copia / "herramientas" / "generar_indice.py")
        datos = json.loads((copia / "curso.json").read_text(encoding="utf-8"))
        modulos = [m["id"] for f in datos["fases"] for m in f["modulos"]
                   if int(Path(m["fichero"]).name[:2]) in ruta.get(f["carpeta"][5:7], [])]
        ids_etapas = [e["id"] for i, e in enumerate(datos["proyecto"]["etapas"], 1) if i in etapas]
        original = (copia / "RUTA-MINIMA.md").read_text(encoding="utf-8")
        (copia / "RUTA-MINIMA.plantilla.md").write_text(plantilla_de(original), encoding="utf-8")
        datos["ruta_minima"] = {"modulos": modulos, "etapas": ids_etapas, "plantilla": "RUTA-MINIMA.plantilla.md"}
        (copia / "curso.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(KIT / "herramientas" / "nucleo" / "generar_ruta_minima.py"), str(copia)],
                           capture_output=True, text=True)
        print(r.stdout + r.stderr, end="")
        if r.returncode != 0:
            return False
        generado = (copia / "RUTA-MINIMA.md").read_text(encoding="utf-8")
        diff = list(difflib.unified_diff(original.splitlines(), generado.splitlines(),
                                         f"RUTA-MINIMA.md ({commit[:8]})", "RUTA-MINIMA.md (kit)", lineterm=""))
        (salida / "ruta-minima.diff").write_text("\n".join(diff) + "\n", encoding="utf-8")
        (salida / "ruta-minima.json").write_text(json.dumps(datos["ruta_minima"], ensure_ascii=False, indent=1) + "\n",
                                                 encoding="utf-8")
        cambios = sum(1 for l in diff if l[:1] in "+-" and not l.startswith(("+++", "---")))
        print(f"{len(modulos)} módulos y {len(ids_etapas)} etapas en la ruta; {cambios} líneas distintas "
              f"(en {salida / 'ruta-minima.diff'}).")
        return True
    finally:
        shutil.rmtree(trabajo, ignore_errors=True)


def main():
    p = argparse.ArgumentParser(prog="fiabilidad_java.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("curso", help="el repositorio del curso de Java (solo se lee, con git archive)")
    p.add_argument("commit", help="el commit fijo que se verifica")
    p.add_argument("objetivos", nargs="*", help="fases o módulos, relativos a la raíz del curso")
    p.add_argument("--salida", default=str(SALIDA), help="carpeta de los resultados (por defecto, odd/fiabilidad/ del kit)")
    p.add_argument("--cache", default=CACHE, help=f"volumen de Docker de la caché de Java del kit (por defecto, {CACHE})")
    p.add_argument("--sin-preparar", action="store_true", help="no ejecutar --preparar-java (la caché ya está)")
    p.add_argument("--repetir", action="store_true", help="repetir los objetivos que ya tienen su .json")
    p.add_argument("--resumen", action="store_true", help="solo juntar los .json que haya")
    p.add_argument("--ruta-minima", action="store_true", help="comparar RUTA-MINIMA.md (no verifica código)")
    a = p.parse_args()
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    if a.resumen:
        resumen(salida)
        return
    curso = Path(a.curso)
    try:
        commit = git(curso, "rev-parse", "--verify", "--quiet", f"{a.commit}^{{commit}}").strip()
    except (RuntimeError, OSError):
        print(f"❌ «{a.commit}» no es un commit de {curso}", file=sys.stderr)
        sys.exit(2)
    if a.ruta_minima:
        sys.exit(0 if comparar_ruta_minima(curso, commit, salida) else 1)
    pendientes = [o for o in a.objetivos if a.repetir or not (salida / f"{nombre_de(o)}.json").exists()]
    if not pendientes:
        print("No hay nada pendiente (usa --repetir o --resumen).")
        return
    trabajo = Path(tempfile.mkdtemp(prefix="fiabilidad-java-"))
    print(f"Commit {commit[:8]} de {curso}, en {trabajo}", flush=True)
    bien = True
    try:
        sacar(curso, commit, trabajo / "original")
        sacar(curso, commit, trabajo / "kit")
        for objetivo in pendientes:
            if not (trabajo / "kit" / objetivo).exists():
                print(f"❌ No está en el commit: {objetivo}", file=sys.stderr)
                bien = False
                continue
            bien &= verificar_objetivo(objetivo, trabajo / "original", trabajo / "kit", salida,
                                       not a.sin_preparar, a.cache)
    finally:
        shutil.rmtree(trabajo, ignore_errors=True)
        if trabajo.exists():
            print(f"⚠️  Queda {trabajo} (ficheros de root de Docker): bórralo con «docker run --rm -u root -v "
                  f"{trabajo}:/x kit-terminal:<etiqueta> rm -rf /x/original /x/kit» y luego la carpeta.")
    sys.exit(0 if bien else 1)


if __name__ == "__main__":
    main()
