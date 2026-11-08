#!/usr/bin/env python3
"""Declara en curso.json los ejercicios de uno o varios módulos, a partir de sus «#### Ejercicio N · Título».

Sale de la parte común del publicar.py del curso inicial. Para cada módulo (o cada módulo de la fase) que se le
indica:
  1. Lee sus encabezados «#### Ejercicio N · Título», en orden (los de dentro de un bloque de código no cuentan).
  2. Los pone en «ejercicios» de su módulo en curso.json, en ese orden. Un ejercicio se reconoce SOLO POR SU
     TÍTULO: si ya estaba en curso.json con el mismo título, conserva su identificador, aunque haya cambiado de
     posición. A los nuevos les propone uno con la regla de FORMATO.md (apartado 3.3): el id del módulo, un
     punto y el título en minúsculas, sin tildes y con guiones (`inicial.que-es-programar.es-un-algoritmo`).
  3. Quita el "disponible": false del módulo y, con --retos, el "retos_disponibles": false de su fase.
  4. Comprueba que ningún identificador se repite en todo el curso y que los títulos son texto plano.

CUIDADO CON LOS TÍTULOS QUE CAMBIAN. Un identificador no cambia nunca, aunque cambie el título: el progreso de los
alumnos va unido a él. Por eso, si en un módulo desaparecería algún ejercicio de curso.json (porque su título ya
no está en el módulo), la herramienta NO DECIDE: se para sin escribir nada y lo explica. Entonces:
  - si es el MISMO ejercicio con otro título, cambia su «titulo» en curso.json (conservando su «id») y vuelve a
    ejecutarla;
  - si de verdad es OTRO ejercicio (el anterior se quita), vuelve a ejecutarla con --aceptar-cambios.
Mientras un curso no tenga ninguna versión publicada, cambiar un identificador no afecta a nadie; desde la
primera, un identificador que desaparece necesita su equivalencia (FORMATO.md, apartado 11.2), y
formato_academia.py lo comprueba.

Uso, desde la raíz del curso (con el kit en la carpeta hermana ../kit-cursos/):
    python3 ../kit-cursos/herramientas/nucleo/declarar_ejercicios.py fase-03-herramientas/01-terminal-lo-basico.md
    python3 ../kit-cursos/herramientas/nucleo/declarar_ejercicios.py fase-03-herramientas --retos
    python3 ../kit-cursos/herramientas/nucleo/declarar_ejercicios.py fase-03-herramientas --comprobar
    python3 ../kit-cursos/herramientas/nucleo/declarar_ejercicios.py --help
Al declarar una fase entera, los módulos que aún no están escritos siguen pendientes. Solo escribe curso.json
si algo cambia, con sangría de 2 espacios (un curso.json formateado a mano se reformatea).
Con --comprobar dice lo que cambiaría, sin escribir nada. Termina con 0 si todo ha ido bien, con 1 si se ha
parado (un título que cambia, un identificador repetido, un título con formato…) sin escribir nada, y con 2 si
los argumentos están mal. Después, regenera el índice y comprueba el curso con formato_academia.py.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argumentos import revisar                               # noqa: E402
from formato_academia import Markdown, formato_en_titulo      # noqa: E402

EJERCICIO = re.compile(r"Ejercicio \d+ · (.+?)\s*")


def nombre(titulo):
    """El título en minúsculas, sin tildes y con guiones (FORMATO.md, apartado 3.3)."""
    texto = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def titulos_del_modulo(ruta):
    md = Markdown(ruta, ruta.name)
    return [(i + 1, m.group(1)) for i, nivel, t in md.encabezados if nivel == 4 and (m := EJERCICIO.fullmatch(t))]


def modulos_indicados(curso, rutas):
    """[(fase, módulo, pedido por su nombre)] de los ficheros o carpetas de fase indicados, o termina si alguno no
    es de curso.json."""
    todos = [(f, m) for f in curso.get("fases", []) for m in f.get("modulos", [])]
    elegidos = []
    for ruta in rutas:
        r = Path(ruta).as_posix().rstrip("/")
        encontrados = [(f, m, m.get("fichero") == r) for f, m in todos if m.get("fichero") == r or f.get("carpeta") == r]
        if not encontrados:
            print(f"❌ {ruta} no es ningún módulo ni ninguna carpeta de fase de curso.json.", file=sys.stderr)
            sys.exit(2)
        elegidos += [e for e in encontrados if all(e[1] is not x[1] for x in elegidos)]
    return elegidos


def declarar(curso, elegidos, raiz, retos, aceptar):
    """Cambia curso en memoria. Devuelve (cambios, problemas, avisos)."""
    cambios, problemas, avisos = [], [], []
    for fase, modulo, por_nombre in elegidos:
        fichero = modulo.get("fichero")
        if not fichero or not (raiz / fichero).is_file():
            if por_nombre or modulo.get("disponible", True):
                problemas.append(f"{modulo.get('id')}: no existe su fichero ({fichero}); no se puede declarar")
            else:
                cambios.append(f"{fichero}: todavía no está escrito; sigue pendiente")
            continue
        titulos = titulos_del_modulo(raiz / fichero)
        anteriores = {e.get("titulo"): e for e in modulo.get("ejercicios", [])}
        nuevos, vistos = [], set()
        for linea, titulo in titulos:
            que = formato_en_titulo(titulo)
            if que:
                problemas.append(f"{fichero}:{linea}: el título «{titulo}» lleva formato Markdown ({que}); los títulos son texto plano")
            if titulo in vistos:
                problemas.append(f"{fichero}:{linea}: dos ejercicios con el título «{titulo}»")
            vistos.add(titulo)
            if titulo in anteriores:
                nuevos.append(anteriores[titulo])
            else:
                nuevos.append({"id": f"{modulo['id']}.{nombre(titulo)}", "titulo": titulo})
                cambios.append(f"{fichero}:{linea}: ejercicio nuevo «{titulo}» → {nuevos[-1]['id']}")
        desaparecen = [e for t, e in anteriores.items() if t not in vistos]
        if desaparecen:
            lista = "; ".join(f"«{e.get('titulo')}» ({e.get('id')})" for e in desaparecen)
            nuevos_titulos = [e["titulo"] for e in nuevos if e not in anteriores.values()]
            if aceptar:
                avisos.append(f"{fichero}: se quitan de curso.json {lista} (con --aceptar-cambios)")
            else:
                problemas.append(
                    f"{fichero}: en el módulo ya no están {lista}"
                    + (f", y hay ejercicios nuevos ({', '.join('«' + t + '»' for t in nuevos_titulos)})" if nuevos_titulos else "")
                    + ". ¿Es el mismo ejercicio con otro título? Entonces cambia su «titulo» en curso.json, conservando su "
                      "«id», y vuelve a ejecutar. ¿Es otro ejercicio? Entonces vuelve a ejecutar con --aceptar-cambios")
        if [e.get("id") for e in nuevos] != [e.get("id") for e in modulo.get("ejercicios", [])]:
            if not any(c.startswith(f"{fichero}:") for c in cambios) and not desaparecen:
                cambios.append(f"{fichero}: ejercicios en otro orden (cada uno conserva su identificador)")
        modulo["ejercicios"] = nuevos
        if modulo.get("disponible") is False:
            del modulo["disponible"]
            cambios.append(f"{fichero}: el módulo pasa a estar disponible")
    if retos:
        for fase in {id(f): f for f, _, _ in elegidos}.values():
            if fase.get("retos_disponibles") is False:
                retos_md = fase.get("retos")
                if retos_md and (raiz / retos_md).is_file():
                    del fase["retos_disponibles"]
                    cambios.append(f"{fase.get('carpeta')}: los retos pasan a estar disponibles")
                else:
                    problemas.append(f"{fase.get('carpeta')}: --retos, pero no existe {retos_md}")
    # Identificadores repetidos en todo el curso
    vistos = {}
    for fase in curso.get("fases", []):
        for ident in [fase.get("id")] + [m.get("id") for m in fase.get("modulos", [])] + \
                [e.get("id") for m in fase.get("modulos", []) for e in m.get("ejercicios", [])]:
            if ident in vistos:
                problemas.append(f"el identificador «{ident}» se repite (pon a mano otro en curso.json para uno de los dos)")
            vistos[ident] = True
    return cambios, problemas, avisos


def main():
    usadas, _, rutas = revisar(__doc__, opciones=("--retos", "--comprobar", "--aceptar-cambios"), rutas=False)
    if not rutas:
        print("❌ Indica un módulo o una carpeta de fase. Usa --help para ver la ayuda.", file=sys.stderr)
        sys.exit(2)
    raiz = Path(".")
    ruta_json = raiz / "curso.json"
    try:
        curso = json.loads(ruta_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"❌ No se puede leer curso.json: {e}", file=sys.stderr)
        sys.exit(1)
    elegidos = modulos_indicados(curso, rutas)
    cambios, problemas, avisos = declarar(curso, elegidos, raiz, "--retos" in usadas, "--aceptar-cambios" in usadas)
    for linea in cambios:
        print(linea)
    for linea in avisos:
        print(f"⚠️  {linea}")
    if problemas:
        print("\n".join(f"❌ {p}" for p in problemas))
        print("No se ha escrito nada en curso.json.")
        sys.exit(1)
    ejercicios = sum(len(m.get("ejercicios", [])) for _, m, _ in elegidos)
    if "--comprobar" in usadas:
        print(f"✅ {len(elegidos)} módulos, {ejercicios} ejercicios: así quedaría curso.json (no se ha escrito nada).")
        return
    if curso == json.loads(ruta_json.read_text(encoding="utf-8")):
        print(f"✅ curso.json ya estaba al día: {len(elegidos)} módulos, {ejercicios} ejercicios (no se ha tocado).")
        return
    # Se escribe con sangría de 2 espacios (como lo escribe Python): un curso.json formateado a mano se reformatea
    ruta_json.write_text(json.dumps(curso, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ curso.json al día: {len(elegidos)} módulos, {ejercicios} ejercicios. "
          "Ahora, generar_indice.py y formato_academia.py.")


if __name__ == "__main__":
    main()
