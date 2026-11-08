#!/usr/bin/env python3
"""Aplica sustituciones de texto en varios ficheros a la vez: todas o ninguna.

Sale de la herramienta del mismo nombre del curso inicial. Resuelve un problema real: un script de
sustituciones escribió unos ficheros, falló en otro, y el commit se hizo igual, con el cambio a medias. Sirve a
cualquier proyecto que actualice varios documentos a la vez (el kit, la academia, los cursos).

El fichero de cambios es una lista JSON, en orden:
    [{"fichero": "ESTADO.md", "antes": "texto exacto", "despues": "texto nuevo"}, …]

- Cada «antes» tiene que aparecer EXACTAMENTE UNA VEZ en su fichero, contando los cambios anteriores de la
  lista sobre ese mismo fichero (así un segundo cambio puede tocar lo que dejó el primero).
- Si alguno falla (el fichero no existe, el texto no aparece o aparece más de una vez), NO SE ESCRIBE NINGÚN
  FICHERO: dice cuál ha fallado y cuántas veces aparecía su texto, y termina con 1.
- Si todos van bien, escribe los ficheros y los vuelve a leer para comprobar que cada «despues» está en su sitio;
  solo entonces termina con 0. Si una escritura falla a medias (disco lleno, permisos), deja como estaban los
  ficheros que ya había escrito.
- Los ficheros se leen y se escriben en UTF-8, respetando sus saltos de línea (también los de Windows, \\r\\n).

Se encadena con el commit, que así solo se hace si todo ha ido bien:
    python3 ../kit-cursos/herramientas/nucleo/reemplazar.py cambios.json && git commit -am "…"

Uso:
    python3 …/reemplazar.py cambios.json                    # rutas relativas a la carpeta actual
    python3 …/reemplazar.py cambios.json --raiz ../curso-x  # rutas relativas a otra carpeta
    python3 …/reemplazar.py cambios.json --comprobar        # solo comprueba; no escribe nada
    python3 …/reemplazar.py --help
Termina con 0 si todo ha ido bien, con 1 si algún cambio falla (y no ha escrito nada) y con 2 si los
argumentos o el fichero de cambios están mal.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from argumentos import revisar, salir   # noqa: E402


def leer(ruta):
    with ruta.open(encoding="utf-8", newline="") as f:
        return f.read()


def escribir(ruta, texto):
    with ruta.open("w", encoding="utf-8", newline="") as f:
        f.write(texto)


def cargar_cambios(fichero):
    try:
        cambios = json.loads(Path(fichero).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        salir(f"{fichero} no es un JSON válido: {e.msg} (línea {e.lineno}).")
    if not isinstance(cambios, list) or not cambios:
        salir(f"{fichero} debe ser una lista con al menos un cambio.")
    for n, c in enumerate(cambios, 1):
        if not isinstance(c, dict) or not all(isinstance(c.get(k), str) for k in ("fichero", "antes", "despues")):
            salir(f"el cambio {n} de {fichero} debe tener «fichero», «antes» y «despues», los tres con texto.")
        if not c["antes"]:
            salir(f"el cambio {n} de {fichero} tiene «antes» vacío.")
    return cambios


def preparar(cambios, raiz):
    """Los textos nuevos de cada fichero, o la lista de errores (sin escribir nada)."""
    textos, errores = {}, []
    for n, c in enumerate(cambios, 1):
        ruta = raiz / c["fichero"]
        if ruta not in textos:
            if not ruta.is_file():
                errores.append(f"cambio {n} ({c['fichero']}): el fichero no existe")
                continue
            textos[ruta] = leer(ruta)
        veces = textos[ruta].count(c["antes"])
        if veces != 1:
            errores.append(f"cambio {n} ({c['fichero']}): el texto de «antes» aparece {veces} veces "
                           f"(tiene que aparecer una): {c['antes'][:70]!r}")
            continue
        textos[ruta] = textos[ruta].replace(c["antes"], c["despues"])
    return textos, errores


def main():
    usadas, valores, sueltos = revisar(__doc__, opciones=("--comprobar",), opciones_con_valor=("--raiz",), maximo=1)
    if not sueltos:
        salir("Falta el fichero de cambios.")
    raiz = Path(valores.get("--raiz", "."))
    if not raiz.is_dir():
        salir(f"No existe la carpeta {raiz}.")
    cambios = cargar_cambios(sueltos[0])
    textos, errores = preparar(cambios, raiz)
    if errores:
        print("\n".join(errores))
        print("❌ No se ha escrito ningún fichero.")
        sys.exit(1)
    if "--comprobar" in usadas:
        print(f"✅ Los {len(cambios)} cambios se pueden aplicar en {len(textos)} ficheros (no se ha escrito nada).")
        return
    originales, escritos = {ruta: leer(ruta) for ruta in textos}, []
    try:
        for ruta, texto in textos.items():
            escribir(ruta, texto)
            escritos.append(ruta)
    except OSError as e:
        for ruta in escritos:
            escribir(ruta, originales[ruta])
        print(f"❌ No se ha podido escribir {ruta}: {e}. Los ficheros ya escritos se han dejado como estaban.")
        sys.exit(1)
    for n, c in enumerate(cambios, 1):
        if c["despues"] and c["despues"] not in leer(raiz / c["fichero"]):
            print(f"❌ cambio {n} ({c['fichero']}): no se encuentra el texto nuevo tras escribir")
            sys.exit(1)
    print(f"✅ {len(cambios)} cambios aplicados en {len(textos)} ficheros.")


if __name__ == "__main__":
    main()
