#!/usr/bin/env python3
"""Comprueba que el código de los módulos y sus copias en `codigo/` coinciden y funcionan.

Sale de herramientas/verificar_codigo.py del curso de Java: es su núcleo, sin nada de Java, con las mismas
convenciones (FORMATO.md, apartado 7.1). Cada lenguaje o formato tiene su comprobador en herramientas/lenguajes/.
Hoy: bash, las sesiones de terminal, y JSON, YAML, XML, CSV y Markdown. Git y curl, cuando los pida el curso.

Para cada bloque de código de un módulo seguido de una línea «📁 **Código:**» con el enlace a su carpeta:
  1. El bloque debe ser idéntico a uno de los ficheros de esa carpeta (sin contar los espacios al final de las
     líneas ni las líneas en blanco del principio y del final).
  2. Si es un script de bash (.sh), se ejecuta con «bash fichero.sh» en una copia de su carpeta (con los
     argumentos de args.txt y la entrada de entrada.txt) y debe terminar con código 0. Si tras el enlace viene
     «**Salida:**» y un bloque ```text, su salida estándar debe coincidir. Si la carpeta tiene
     termina-con-error.txt, debe terminar con un código distinto de 0, y tras su «**Salida:**» (opcional) debe
     venir «**Salida de error:**» con un bloque ```text igual a su salida de error.
  3. bash 3.2 (la de macOS): cada .sh no puede usar lo que no existe en ella (lenguajes/bash.py). Con Docker,
     además se ejecuta con bash 3.2.57 y su salida y su código de salida deben ser los mismos que con la de
     Ubuntu. Lo que NO se comprueba: que sed, date, ls… se comporten igual en macOS (allí son las de BSD, aquí
     las de GNU); eso lo avisa el texto de cada módulo.
Para cada bloque «**En tu terminal** (`sesion.txt`):» con su bloque ```text y su enlace «📁 **Código:**»: se
teclean las órdenes de ese sesion.txt de la carpeta en una bash con terminal (indicador «$ »), en una carpeta
personal con los demás ficheros de la carpeta, y la pantalla debe ser la del bloque.
Los ficheros de datos de cada carpeta enlazada (.json, .yaml/.yml, .xml, .csv y .md) tienen que ser válidos
(lenguajes/formato_*.py: JSON y YAML que se leen, XML bien formado, CSV con su separador.txt y las mismas
columnas en cada fila, Markdown con enlaces, anclas y tablas bien escritos y los bloques cerrados). Si la carpeta
tiene debe-fallar.txt, todos sus ficheros de datos tienen que FALLAR (están mal a propósito). Si una carpeta tiene
un .json y un .yaml con el mismo nombre (una conversión), tienen que cargar los mismos datos.
Antes de comparar, lo que encaja con cada expresión regular del salida-variable.txt de la carpeta se sustituye
por «…», en la salida real y en la del texto.
Además: error por cada fichero enlazado que Git ignora (.gitignore: no llegaría a un clon del curso), y aviso por
cada carpeta de codigo/ que ningún módulo enlaza y por cada script que ningún bloque muestra.

Dónde se ejecuta (servicios/terminal.py):
  - CON DOCKER, la verificación completa: un contenedor sin red, con Ubuntu 26.04.1, Git 2.56.0, bash 5.3 y
    3.2.57, en español y con la hora de Madrid, siempre los mismos. La primera vez se construye la imagen
    (unos minutos, con internet).
  - SIN DOCKER (o con --sin-docker), la verificación parcial: la bash del equipo, sin poder cortar la red, con
    sus versiones y sin bash 3.2 (solo la búsqueda de lo que no existe en ella). Lo dice al final: para cerrar
    una fase, verifica con Docker.

Uso, desde la raíz del curso (con el kit en la carpeta hermana ../kit-cursos/):
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py                         # todo el curso
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py fase-02-tu-ordenador    # una carpeta
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py fase-02-…/02-….md       # un módulo
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --sin-docker            # sin Docker
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --versiones             # qué lleva la imagen
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --help
Termina con 0 si todo coincide y funciona (aunque haya avisos), con 1 si hay algún error y con 2 si los
argumentos están mal.
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
for carpeta in (AQUI, AQUI.parent, AQUI.parent / "servicios", AQUI.parent / "lenguajes"):
    sys.path.insert(0, str(carpeta))
from argumentos import revisar                                                     # noqa: E402
from formato_academia import CARPETAS_IGNORADAS, FICHEROS_DE_TRABAJO, Informe, Markdown   # noqa: E402
import terminal                                                                    # noqa: E402
import bash as lenguaje_bash                                                       # noqa: E402
import formato_csv, formato_json, formato_markdown, formato_xml, formato_yaml       # noqa: E402,E401

FORMATOS = [formato_json, formato_yaml, formato_xml, formato_csv, formato_markdown]

ENLACE_CODIGO = re.compile(r"^📁 \*\*Código:\*\* \[[^\]]*\]\(([^)\s]+)\)")
SESION = re.compile(r"^\*\*En tu terminal\*\* \(`([^`]+)`\):\s*$")
SALIDA, SALIDA_DE_ERROR = "**Salida:**", "**Salida de error:**"
DE_VERIFICACION = {"entrada.txt", "args.txt", "termina-con-error.txt", "debe-fallar.txt", "separador.txt",
                   "salida-variable.txt"}


def es_de_verificacion(nombre):
    return nombre in DE_VERIFICACION or re.fullmatch(r"sesion(-[\w-]+)?\.txt", nombre) is not None


def normalizar(texto):
    lineas = [l.rstrip() for l in texto.replace("\r\n", "\n").split("\n")]
    while lineas and not lineas[0]:
        lineas.pop(0)
    while lineas and not lineas[-1]:
        lineas.pop()
    return "\n".join(lineas)


def enmascarar(texto, carpeta):
    variable = carpeta / "salida-variable.txt"
    if variable.is_file():
        for linea in variable.read_text(encoding="utf-8").splitlines():
            if linea.strip() and not linea.lstrip().startswith("#"):
                texto = re.sub(linea.strip(), "…", texto)
    return texto


def primera_diferencia(esperado, real, nombre_real="la salida real", nombre_esperado="el bloque"):
    """Una explicación corta de la primera línea distinta."""
    e, r = esperado.split("\n"), real.split("\n")
    for n, (a, b) in enumerate(zip(e, r), 1):
        if a != b:
            return f"en la línea {n}:\n      {nombre_esperado}: {a!r}\n      {nombre_real}: {b!r}"
    if len(e) != len(r):
        sobra = r[len(e)] if len(r) > len(e) else None
        falta = e[len(r)] if len(e) > len(r) else None
        return (f"{nombre_real} tiene {len(r)} líneas y {nombre_esperado} {len(e)}"
                + (f"; sobra {sobra!r}" if sobra is not None else f"; falta {falta!r}"))
    return "difieren"


class Verificador:
    def __init__(self, raiz, informe, con_docker):
        self.raiz, self.informe, self.con_docker = raiz, informe, con_docker
        self.enlazadas = set()          # carpetas enlazadas (resueltas)
        self.mostrados = set()          # ficheros que un bloque muestra
        self.cuentas = {"bloques": 0, "scripts": 0, "sesiones": 0, "datos": 0}
        self.compatibilidad_revisada = set()

    def rel(self, ruta):
        try:
            return ruta.resolve().relative_to(self.raiz.resolve()).as_posix()
        except ValueError:
            return str(ruta)

    # -- encontrar lo que hay que comprobar ---------------------------------------------------------------

    def bloque_que_termina_en(self, md, i):
        """El bloque de código cuya última línea es la anterior no vacía a i, o None."""
        j = i - 1
        while j >= 0 and not md.lineas[j].strip():
            j -= 1
        return next((b for b in md.bloques if b[1] == j), None)

    def siguiente_etiqueta(self, md, i, etiqueta):
        """Si tras la línea i (saltando las vacías) viene la etiqueta y un bloque, (línea de la etiqueta, texto del
        bloque); si no, None."""
        j = i + 1
        while j < len(md.lineas) and not md.lineas[j].strip():
            j += 1
        if j >= len(md.lineas) or md.lineas[j].strip() != etiqueta:
            return None
        k = j + 1
        while k < len(md.lineas) and not md.lineas[k].strip():
            k += 1
        bloque = next((b for b in md.bloques if b[0] == k), None)
        if not bloque:
            self.informe.error(md.rel, j + 1, f"falta el bloque ```text tras «{etiqueta}»")
            return None
        return j, bloque

    def texto_del_bloque(self, md, bloque):
        return "\n".join(md.lineas[bloque[0] + 1:bloque[1]])

    def verificar_md(self, md):
        for i, linea in enumerate(md.lineas):
            if md.en_codigo[i]:
                continue
            m = ENLACE_CODIGO.match(linea.strip())
            if not m:
                continue
            carpeta = (md.ruta.parent / m.group(1)).resolve()
            if not carpeta.is_dir():
                self.informe.error(md.rel, i + 1, f"el enlace «📁 Código» no lleva a una carpeta que exista: {m.group(1)}")
                continue
            self.enlazadas.add(carpeta)
            bloque = self.bloque_que_termina_en(md, i)
            if bloque is None:
                self.informe.error(md.rel, i + 1, "«📁 Código» sin un bloque de código justo antes")
                continue
            # ¿Es la pantalla de una sesión?
            j = bloque[0] - 1
            while j >= 0 and not md.lineas[j].strip():
                j -= 1
            sesion = SESION.match(md.lineas[j].strip()) if j >= 0 else None
            if sesion:
                self.verificar_sesion(md, j, carpeta, sesion.group(1), self.texto_del_bloque(md, bloque))
            else:
                self.verificar_bloque(md, i, bloque, carpeta)

    # -- un bloque con su fichero ---------------------------------------------------------------------

    def verificar_bloque(self, md, i, bloque, carpeta):
        self.cuentas["bloques"] += 1
        texto = normalizar(self.texto_del_bloque(md, bloque))
        candidatos = [f for f in sorted(carpeta.rglob("*")) if f.is_file() and not es_de_verificacion(f.name)]
        iguales = []
        for f in candidatos:
            try:
                if normalizar(f.read_text(encoding="utf-8")) == texto:
                    iguales.append(f)
            except UnicodeDecodeError:
                continue
        if not iguales:
            cerca = max(candidatos, default=None, key=lambda f: difflib.SequenceMatcher(
                None, texto, f.read_text(encoding="utf-8", errors="replace")).quick_ratio())
            detalle = ""
            if cerca:
                detalle = f" (el más parecido, {cerca.name}: {primera_diferencia(texto, normalizar(cerca.read_text(encoding='utf-8', errors='replace')), 'el fichero')})"
            self.informe.error(md.rel, bloque[0] + 1, f"el bloque no es igual a ningún fichero de {self.rel(carpeta)}/{detalle}")
            return
        fichero = iguales[0]
        self.mostrados.add(fichero.resolve())
        if lenguaje_bash.es_mio(fichero):
            self.verificar_script(md, i, fichero, carpeta)

    def verificar_script(self, md, i, fichero, carpeta):
        self.compatibilidad_3_2(fichero)
        salida = self.siguiente_etiqueta(md, i, SALIDA)
        despues = salida[1][1] if salida else i
        error = self.siguiente_etiqueta(md, despues, SALIDA_DE_ERROR)
        con_error = (carpeta / "termina-con-error.txt").is_file()
        if error and not con_error:
            self.informe.error(md.rel, error[0] + 1, f"«{SALIDA_DE_ERROR}» sin termina-con-error.txt en la carpeta")
        if con_error and not error:
            self.informe.error(md.rel, i + 1, f"{fichero.name} lleva termina-con-error.txt: falta «{SALIDA_DE_ERROR}» y su bloque")
        self.cuentas["scripts"] += 1
        entrada = (carpeta / "entrada.txt").read_bytes() if (carpeta / "entrada.txt").is_file() else None
        sub = fichero.parent.relative_to(carpeta).as_posix()
        try:
            with terminal.terminal(carpeta, con_docker=self.con_docker) as t:
                ruta = fichero.name if sub == "." else f"{sub}/{fichero.name}"
                orden = lenguaje_bash.orden(Path(ruta), carpeta)
                orden[1] = ruta
                codigo, out, err = t.ejecutar(orden, entrada)
                otra = None
                if t.completa:
                    otra = t.ejecutar(["bash-3.2", *orden[1:]], entrada)
        except terminal.ErrorDeTerminal as e:
            self.informe.error(md.rel, i + 1, f"{fichero.name}: {e}")
            return
        nombre = self.rel(fichero)
        if con_error and codigo == 0:
            self.informe.error(md.rel, i + 1, f"{nombre} lleva termina-con-error.txt pero termina bien (código 0)")
        elif not con_error and codigo != 0:
            self.informe.error(md.rel, i + 1, f"{nombre} termina con el código {codigo}:\n    {err.strip()[-800:]}")
        if salida:
            self.comparar(md, salida[0], self.texto_del_bloque(md, salida[1]), out, carpeta, f"la salida de {fichero.name}")
        if error:
            self.comparar(md, error[0], self.texto_del_bloque(md, error[1]), err, carpeta, f"la salida de error de {fichero.name}")
        if otra is not None:
            codigo32, out32, _ = otra
            if (codigo32 == 0) != (codigo == 0) or normalizar(enmascarar(out32, carpeta)) != normalizar(enmascarar(out, carpeta)):
                self.informe.error(md.rel, i + 1, f"{nombre}: con bash 3.2 (la de macOS) no hace lo mismo "
                                                  f"(código {codigo32} frente a {codigo}; "
                                                  f"{primera_diferencia(normalizar(out), normalizar(out32), 'con bash 3.2', 'con bash 5')})")

    def compatibilidad_3_2(self, fichero):
        if fichero in self.compatibilidad_revisada:
            return
        self.compatibilidad_revisada.add(fichero)
        for n, que in lenguaje_bash.incompatibilidades_3_2(fichero.read_text(encoding="utf-8", errors="replace")):
            self.informe.error(self.rel(fichero), n, f"no existe en bash 3.2, la de macOS: {que}")

    def comparar(self, md, linea, esperado, real, carpeta, que):
        e, r = normalizar(enmascarar(esperado, carpeta)), normalizar(enmascarar(real, carpeta))
        if e != r:
            self.informe.error(md.rel, linea + 1, f"{que} no es la del texto: {primera_diferencia(e, r)}")

    # -- una sesión -----------------------------------------------------------------------------------------

    def verificar_sesion(self, md, linea, carpeta, nombre, esperado):
        self.cuentas["sesiones"] += 1
        fichero = carpeta / nombre
        if not fichero.is_file():
            self.informe.error(md.rel, linea + 1, f"no existe {self.rel(fichero)}")
            return
        for f in carpeta.glob("*.sh"):
            self.compatibilidad_3_2(f)
            self.mostrados.add(f.resolve())          # en una sesión, los scripts se ven al ejecutarlos
        try:
            ordenes = terminal.ordenes_de(fichero.read_text(encoding="utf-8"))
            excluir = {nombre, "salida-variable.txt"}
            with terminal.terminal(carpeta, excluir, con_docker=self.con_docker) as t:
                real = t.sesion(ordenes)
        except terminal.ErrorDeTerminal as e:
            self.informe.error(md.rel, linea + 1, f"la sesión {nombre}: {e}")
            return
        self.comparar(md, linea, esperado, real, carpeta, f"la pantalla de {nombre}")

    # -- lo que no está enlazado o no llegaría a un clon -----------------------------------------------------

    def revisar_codigo(self, carpetas_revisadas):
        for raiz_codigo in carpetas_revisadas:
            for codigo in sorted(raiz_codigo.rglob("codigo")):
                if not codigo.is_dir() or (CARPETAS_IGNORADAS - {"codigo"}) & set(codigo.resolve().relative_to(self.raiz.resolve()).parts):
                    continue
                # Las carpetas de ejemplos y soluciones: ejemplos/X, ejercicios/X, retos/X (y proyecto/codigo/X)
                hojas = [c for c in codigo.glob("*/ejemplos/*") if c.is_dir()]
                hojas += [c for c in codigo.glob("*/ejercicios/*") if c.is_dir()]
                hojas += [c for c in codigo.glob("retos/*") if c.is_dir()]
                for hoja in sorted(hojas):
                    if hoja.resolve() not in self.enlazadas:
                        self.informe.aviso(self.rel(hoja) + "/", 0, "carpeta de código que ningún módulo enlaza")
        for carpeta in sorted(self.enlazadas):
            for script in sorted(carpeta.rglob("*.sh")):
                if script.resolve() not in self.mostrados:
                    self.informe.aviso(self.rel(script), 0, "script que ningún bloque del módulo muestra")
                    self.compatibilidad_3_2(script)
        self.revisar_datos()
        self.revisar_ignorados()

    def revisar_datos(self):
        """Los ficheros de datos de las carpetas enlazadas: válidos, o que fallen si la carpeta tiene debe-fallar.txt."""
        vistos, sin_pyyaml = set(), None
        for carpeta in sorted(self.enlazadas):
            debe_fallar = (carpeta / "debe-fallar.txt").is_file()
            de_datos = [(f, fmt) for f in sorted(carpeta.rglob("*")) if f.is_file() and not es_de_verificacion(f.name)
                        for fmt in FORMATOS if fmt.es_mio(f)]
            if debe_fallar and not de_datos:
                self.informe.error(self.rel(carpeta / "debe-fallar.txt"), 0, "debe-fallar.txt en una carpeta sin ficheros de datos")
            cargados = {}
            for f, fmt in de_datos:
                if f.resolve() in vistos:
                    continue
                vistos.add(f.resolve())
                try:
                    problemas = fmt.errores(f, f.parent)
                except formato_yaml.SinPyYAML as e:
                    sin_pyyaml = sin_pyyaml or (self.rel(f), str(e))
                    continue
                self.cuentas["datos"] += 1
                if debe_fallar:
                    if not problemas:
                        self.informe.error(self.rel(f), 0, "su carpeta tiene debe-fallar.txt (está mal a propósito), pero es válido")
                    continue
                for linea, mensaje in problemas:
                    self.informe.error(self.rel(f), linea, mensaje)
                if not problemas and fmt in (formato_json, formato_yaml):
                    cargados.setdefault(f.with_suffix(""), []).append((f, fmt.cargar(f)))
            for _, versiones in cargados.items():
                if len(versiones) > 1 and any(d != versiones[0][1] for _, d in versiones[1:]):
                    nombres = " y ".join(f.name for f, _ in versiones)
                    self.informe.error(self.rel(versiones[0][0].parent), 0, f"{nombres} no tienen los mismos datos "
                                                                           "(una conversión debe cargar lo mismo)")
        if sin_pyyaml:
            self.informe.aviso(sin_pyyaml[0], 0, f"no se han podido comprobar los YAML: {sin_pyyaml[1]}")

    def revisar_ignorados(self):
        ficheros = [f for c in self.enlazadas for f in c.rglob("*") if f.is_file()]
        if not ficheros:
            return
        try:
            r = subprocess.run(["git", "-C", str(self.raiz), "check-ignore", "--stdin"], capture_output=True, text=True,
                               input="\n".join(str(f) for f in ficheros))
        except OSError:
            return
        if r.returncode not in (0, 1):          # 128: no es un repositorio de Git
            return
        for ignorado in r.stdout.splitlines():
            self.informe.error(self.rel(Path(ignorado)), 0, "Git lo ignora (.gitignore): funcionaría aquí, pero no llegaría a un clon del curso")


def ficheros_md(raiz, rutas):
    encontrados = []
    for ruta in [Path(r) for r in rutas] or [raiz]:
        if ruta.is_file():
            encontrados.append(ruta)
            continue
        for md in sorted(ruta.rglob("*.md")):
            rel = md.resolve().relative_to(raiz.resolve())
            if CARPETAS_IGNORADAS & set(rel.parts[:-1]) or rel.as_posix() in FICHEROS_DE_TRABAJO:
                continue
            encontrados.append(md)
    return encontrados


def main():
    usadas, _, rutas = revisar(__doc__, opciones=("--sin-docker", "--versiones"))
    if "--versiones" in usadas:
        if not terminal.hay_docker():
            print("❌ Sin Docker no hay imagen de la terminal del kit.", file=sys.stderr)
            sys.exit(1)
        print(terminal.versiones(), end="")
        return
    raiz = Path(".")
    con_docker = False if "--sin-docker" in usadas else terminal.hay_docker()
    informe = Informe()
    verificador = Verificador(raiz, informe, con_docker)
    if con_docker:
        try:
            terminal.imagen()
        except terminal.ErrorDeTerminal as e:
            print(f"❌ No se puede preparar la terminal del kit:\n{e}", file=sys.stderr)
            sys.exit(1)
    mds = ficheros_md(raiz, rutas)
    for md in mds:
        verificador.verificar_md(Markdown(md, verificador.rel(md)))
    carpetas = [Path(r) for r in rutas if Path(r).is_dir()] or [raiz]
    verificador.revisar_codigo(carpetas if not any(Path(r).is_file() for r in rutas) else [])
    c = verificador.cuentas
    resumen = (f"{len(mds)} ficheros revisados: {c['bloques']} bloques con su fichero, {c['scripts']} scripts "
               f"ejecutados, {c['sesiones']} sesiones de terminal y {c['datos']} ficheros de datos.")
    if con_docker:
        resumen += " En la terminal del kit (Docker, sin red): verificación completa."
    else:
        resumen += ("\n⚠️  Sin Docker: verificación parcial (la bash del equipo, sin cortar la red, con sus versiones y "
                    "sin bash 3.2). Para cerrar una fase, verifica con Docker.")
    for f, l, m in sorted(informe.errores, key=lambda e: (e[0], e[1])):
        print(f"{f}:{l}: ERROR: {m}" if l else f"{f}: ERROR: {m}")
    for f, l, m in sorted(informe.avisos, key=lambda e: (e[0], e[1])):
        print(f"{f}:{l}: AVISO: {m}" if l else f"{f}: AVISO: {m}")
    if informe.errores or informe.avisos:
        print()
    print(resumen)
    if informe.errores:
        print(f"❌ {len(informe.errores)} error(es) y {len(informe.avisos)} aviso(s).")
        sys.exit(1)
    print(f"✅ Todo el código coincide y funciona ({len(informe.avisos)} aviso(s)).")


if __name__ == "__main__":
    main()
