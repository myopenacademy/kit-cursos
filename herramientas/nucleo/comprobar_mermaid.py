#!/usr/bin/env python3
"""Comprueba que los diagramas Mermaid de los ficheros Markdown del curso se dibujan sin errores.

Sale de herramientas/comprobar_mermaid.py del curso de Java, sin cambios en lo que comprueba; solo
cambia que se ejecuta desde la raíz del curso con el kit en ../kit-cursos/.

Un diagrama Mermaid mal escrito no da ningún aviso al escribirlo: simplemente GitHub no lo muestra.
Esta herramienta extrae cada bloque ```mermaid y lo dibuja con mermaid-cli en DOS versiones:
  - mermaid-cli 12.0.0 (Mermaid 12.2), reciente;
  - mermaid-cli 10.9.1 (Mermaid 10.9), antigua.
Un diagrama tiene que funcionar en las dos, porque no se sabe qué versión usará quien lea el curso
(GitHub, un editor, un visor de Markdown). También se comprueban los bloques ```mermaid que están dentro
de otro bloque (por ejemplo, en las chuletas), para que quien los copie pueda usarlos tal cual.
Se ignoran las carpetas .verificacion/, codigo/, herramientas/ y node_modules/.
Las reglas de FORMATO.md sobre Mermaid (sin negrita, entidades, directivas…) las comprueba
formato_academia.py; esta herramienta solo mira que se dibujen.

Requisitos (solo para esta herramienta, no para el curso): Node.js (con npx) y Google Chrome o
Chromium. La primera vez, npx descarga mermaid-cli en su caché (no toca el repositorio). Si el
navegador no está en un sitio habitual, indica su ruta en la variable de entorno CHROME_PATH.

Uso, desde la raíz del curso:
    python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py                       # todo el curso
    python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-03-poo           # una carpeta
    python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-03-poo/11-uml.md # un fichero
    python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py fase-03-poo/11-uml.md --imagenes /tmp/diagramas
    python3 ../kit-cursos/herramientas/nucleo/comprobar_mermaid.py --help
Con --imagenes, guarda además cada diagrama como PNG (con la versión reciente) para revisarlo a ojo.
Termina con código 0 si todos los diagramas se dibujan, con 1 y la lista de los que fallan (fichero,
línea donde empieza el bloque, versión y el error de Mermaid) o si falta Node o Chrome, y con 2 si los
argumentos están mal (una ruta que no existe o una opción desconocida), sin comprobar nada.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from argumentos import revisar   # noqa: E402

VERSIONES = ["12.0.0", "10.9.1"]
BLOQUE = re.compile(r"^[ \t]*```mermaid[ \t]*\n(.*?)^[ \t]*```", re.S | re.M)
IGNORADAS = {".verificacion", "codigo", "node_modules", ".git", "herramientas"}
NAVEGADORES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def navegador():
    if os.environ.get("CHROME_PATH"):
        return os.environ["CHROME_PATH"]
    for candidato in NAVEGADORES:
        ruta = shutil.which(candidato) or (candidato if Path(candidato).is_file() else None)
        if ruta:
            return ruta
    print("❌ No se encuentra Chrome ni Chromium. Instálalo o indica su ruta en CHROME_PATH.", file=sys.stderr)
    sys.exit(1)


def ficheros(rutas):
    """Los .md de las rutas (o de la carpeta actual), sin las carpetas ignoradas."""
    encontrados = []
    for ruta in [Path(r) for r in rutas] or [Path(".")]:
        if ruta.is_file():
            encontrados.append(ruta)
            continue
        # Las carpetas ignoradas se miran solo dentro de lo que se revisa (el curso puede estar, por
        # ejemplo, dentro de una carpeta herramientas/ de otro proyecto)
        encontrados += [f for f in sorted(ruta.rglob("*.md")) if not IGNORADAS & set(f.relative_to(ruta).parts[:-1])]
    return encontrados


def diagramas(md):
    """Lista de (línea donde empieza el bloque, texto del diagrama)."""
    texto = md.read_text(encoding="utf-8")
    return [(texto.count("\n", 0, m.start()) + 1, m.group(1)) for m in BLOQUE.finditer(texto)]


def mmdc(version, entrada, salida, configuracion):
    orden = ["npx", "--yes", "-p", f"@mermaid-js/mermaid-cli@{version}", "mmdc",
             "-p", str(configuracion), "-i", str(entrada), "-o", str(salida), "-b", "white", "-q"]
    entorno = dict(os.environ, PUPPETEER_SKIP_DOWNLOAD="1")
    resultado = subprocess.run(orden, capture_output=True, text=True, env=entorno, timeout=600)
    # El mensaje útil de Mermaid son las primeras líneas (el error, el trozo con ^ y lo que esperaba);
    # lo que viene después es la traza interna de mermaid-cli
    mensaje = []
    for linea in (resultado.stderr + resultado.stdout).splitlines():
        if re.match(r"\s*(at |\w+\.\w+ \()", linea):
            break
        if linea.strip():
            mensaje.append(linea.replace("Error: Evaluation failed: ", "").rstrip())
    return resultado.returncode == 0, "\n    ".join(mensaje[:4])


def main():
    _, valores, rutas = revisar(__doc__, opciones_con_valor=("--imagenes",))
    carpeta_imagenes = Path(valores["--imagenes"]) if "--imagenes" in valores else None
    if carpeta_imagenes:
        carpeta_imagenes.mkdir(parents=True, exist_ok=True)
    if not shutil.which("npx"):
        print("❌ No se encuentra npx: instala Node.js (https://nodejs.org) para usar esta herramienta.", file=sys.stderr)
        sys.exit(1)

    trabajo = Path(tempfile.mkdtemp(prefix="mermaid-"))
    configuracion = trabajo / "puppeteer.json"
    configuracion.write_text(json.dumps({"executablePath": navegador(), "args": ["--no-sandbox"]}))

    errores, total, con_diagramas = [], 0, 0
    for md in ficheros(rutas):
        bloques = diagramas(md)
        if not bloques:
            continue
        con_diagramas += 1
        total += len(bloques)
        print(f"{md.as_posix()}: {len(bloques)} diagrama(s)")
        for version in VERSIONES:
            # Primero, todos los diagramas del fichero de una vez; si algo falla, uno a uno para localizarlo
            juntos = trabajo / "juntos.md"
            juntos.write_text("".join(f"```mermaid\n{b}```\n\n" for _, b in bloques), encoding="utf-8")
            correcto, _ = mmdc(version, juntos, trabajo / "juntos-salida.md", configuracion)
            if correcto:
                continue
            for linea, bloque in bloques:
                suelto = trabajo / "suelto.mmd"
                suelto.write_text(bloque, encoding="utf-8")
                correcto, mensaje = mmdc(version, suelto, trabajo / "suelto.svg", configuracion)
                if not correcto:
                    errores.append(f"{md.as_posix()}:{linea}: mermaid-cli {version}:\n    {mensaje}")
        if carpeta_imagenes:
            for numero, (linea, bloque) in enumerate(bloques, 1):
                suelto = trabajo / "suelto.mmd"
                suelto.write_text(bloque, encoding="utf-8")
                imagen = f"{md.stem}-{numero:02d}-linea{linea}.png"
                mmdc(VERSIONES[0], suelto, carpeta_imagenes / imagen, configuracion)

    shutil.rmtree(trabajo, ignore_errors=True)
    print(f"\n{total} diagramas en {con_diagramas} ficheros")
    if errores:
        print(f"❌ {len(errores)} problema(s):\n")
        print("\n\n".join(errores))
        sys.exit(1)
    print("✅ Todos los diagramas se dibujan con las dos versiones de Mermaid.")
    if carpeta_imagenes:
        print(f"Imágenes guardadas en {carpeta_imagenes}")


if __name__ == "__main__":
    main()
