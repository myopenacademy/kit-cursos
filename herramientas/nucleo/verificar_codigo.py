#!/usr/bin/env python3
"""Comprueba que el código de los módulos y sus copias en `codigo/` coinciden y funcionan.

Sale de herramientas/verificar_codigo.py del curso de Java: es su núcleo, sin nada de Java, con las mismas
convenciones (FORMATO.md, apartado 7.1). Cada lenguaje o formato tiene su comprobador en herramientas/lenguajes/.
Hoy: bash, Java (lenguajes/java.py, desde el kit 1.1.0), las sesiones de terminal (también con Git y con curl), y
JSON, YAML, XML, CSV, TOML, INI, SVG y Markdown.

Para cada bloque de código de un módulo seguido de una línea «📁 **Código:**» con el enlace a su carpeta:
  1. El bloque debe ser idéntico a uno de los ficheros de esa carpeta (sin contar los espacios al final de las
     líneas ni las líneas en blanco del principio y del final). También puede ser uno de sus ficheros de
     verificación (entrada.txt, peticiones.txt…): cuenta como mostrado y no se ejecuta.
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
personal con los demás ficheros de la carpeta (menos los sesion*.txt y salida-variable.txt), y la pantalla debe
ser la del bloque.
Las SESIONES ENCADENADAS (sesion-1.txt, sesion-2.txt… de una misma carpeta) se teclean una detrás de otra en la
misma terminal, como las hace el alumno: cada una encuentra los ficheros y el reloj de Git como los dejó la
anterior, pero arranca en una bash nueva en la carpeta del ejemplo (sin el cd ni las variables de la anterior: el
alumno puede cerrar la terminal entre una y otra). Cada bloque se compara con la pantalla de la suya. Las demás
sesiones (sesion.txt, sesion-<nombre>.txt) empiezan cada una desde cero, con los ficheros de la carpeta.
Los ficheros de datos de cada carpeta enlazada (.json, .yaml/.yml, .xml, .csv/.tsv, .md, .toml, .ini y .svg)
tienen que ser válidos (lenguajes/formato_*.py: JSON, YAML y TOML que se leen, XML bien formado, CSV con su
separador.txt y las mismas columnas en cada fila, en UTF-8 sin BOM o en la codificación de su codificacion.txt,
TSV igual pero con tabulador, INI con sus claves dentro de secciones y sin repetir, SVG bien formado con su
xmlns, Markdown con enlaces, anclas y tablas bien escritos y los bloques cerrados). Si la carpeta tiene
debe-fallar.txt, todos sus ficheros de datos tienen que FALLAR (están mal a propósito), menos las imágenes SVG,
que siempre tienen que ser válidas. Si una carpeta tiene un .json y un .yaml con el mismo nombre (una
conversión), tienen que cargar los mismos datos; y si tiene un .csv (o .tsv) y un .json con el mismo nombre, los
mismos datos con las reglas de FORMATO.md, apartado 7.1 (cada fila, un objeto con las claves de la cabecera;
cada campo, según el tipo de su valor en el JSON).
EL SERVIDOR HTTP LOCAL: si la carpeta de una sesión o un script tiene un servidor.json, la terminal arranca antes
un servidor HTTP en localhost con las rutas que describe (servicios/servidor_http.py; FORMATO.md, apartado 7.1),
para que curl tenga a quién preguntar sin internet, y lo para después. El servidor.json de cada carpeta enlazada
se comprueba aunque ninguna sesión lo use, y no se copia a la terminal.
JAVA (lenguajes/java.py, que lo explica entero; FORMATO.md, apartado 7.1, «Los de Java»): cada .java con main que
muestra un bloque se ejecuta (un programa suelto con «java Fichero.java» desde su carpeta, con las demás fuentes si
tiene package bajo src/; uno de un proyecto de Maven o Gradle, con su classpath, tras construir el proyecto una
vez) con entrada.txt, args.txt y opciones-java.txt, y su «**Salida:**», «**Salida de error:**» (con
termina-con-error.txt) o «**Sesión en la terminal:**» debe ser la del texto; tras una clase de pruebas de Maven,
«**Salida de las pruebas:**» es el resumen de Surefire; con solo-compilar.txt, solo se compila (o, junto al
pom.xml, solo se construye). Con Docker, en la imagen de Java del kit (Temurin, Maven y Gradle fijados), sin red:
Maven y Gradle sin conexión (Gradle, sin demonio), con la caché que llena --preparar-java.
Antes de comparar, lo que encaja con cada expresión regular del salida-variable.txt de la carpeta se sustituye
por «…», en la salida real y en la del texto.
Además: error por cada fichero enlazado que Git ignora (.gitignore: no llegaría a un clon del curso), y aviso por
cada carpeta de codigo/ que ningún módulo enlaza y por cada script que ningún bloque muestra.

Dónde se ejecuta (servicios/terminal.py):
  - CON DOCKER, la verificación completa: un contenedor sin red, con Ubuntu 26.04.1, Git 2.56.0, bash 5.3 y
    3.2.57, en español y con la hora de Madrid, siempre los mismos. La primera vez se construye la imagen
    (unos minutos, con internet).
  - SIN DOCKER (o con --sin-docker), la verificación parcial: la bash del equipo, sin poder cortar la red, con
    sus versiones y sin bash 3.2 (solo la búsqueda de lo que no existe en ella); para Java, el JDK, Maven y Gradle
    del equipo (del PATH), también sin conexión y con sus cachés. Lo dice al final: para cerrar una fase,
    verifica con Docker.

LA RED, SOLO CON --preparar-java [carpeta]: es la única vez que hay red. Construye, con internet, cada proyecto de
Maven o Gradle de las carpetas enlazadas por los módulos (de todo el curso o de la carpeta o el módulo que se diga)
para descargar sus dependencias y plugins a la caché (sin el repackage de Spring Boot, que falla sin clase con
main): con Docker, al volumen kit-java-cache (o el de la variable de entorno KIT_JAVA_CACHE), que la verificación
monta en la imagen de Java; sin Docker, a las cachés del equipo (~/.m2/repository, o la de KIT_JAVA_M2, y
~/.gradle, o la de GRADLE_USER_HOME). Después, la verificación ya no necesita red; si falta una dependencia, el
error dice que hay que volver a prepararla. Hazlo la primera vez y cada vez que cambie una dependencia. No
verifica nada: termina con 0 si todos los proyectos se han preparado.

Qué se verifica:
  - SIN --commit, los ficheros del disco, tal como están: lo normal mientras se escribe un módulo.
  - CON --commit [referencia] (HEAD si no se dice otra: un commit, una rama o una etiqueta, como v1.0.0), el
    curso como lo recibe el alumno: se saca esa versión con «git archive» (que solo lee: no toca el repositorio)
    a una carpeta temporal y se verifica esa copia. Es igual que un clon: saltos de línea según .gitattributes,
    solo los permisos que guarda Git (ejecutable o no), sin carpetas vacías y sin lo que Git ignora ni lo que
    no tiene commit (si hay cambios sin commit, lo avisa al principio). Es la forma de verificar una fase
    entera antes de cerrarla, y la etiqueta antes de publicar una versión. Los mensajes dicen las rutas del
    curso, como siempre.

Uso, desde la raíz del curso (con el kit en la carpeta hermana ../kit-cursos/):
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py                         # todo el curso
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py fase-02-tu-ordenador    # una carpeta
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py fase-02-…/02-….md       # un módulo
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --commit                # el último commit, como un clon
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --commit v1.0.0         # una etiqueta (o --commit=v1.0.0)
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --sin-docker            # sin Docker
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --versiones             # qué llevan las imágenes
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --preparar-java         # la caché de Java (con red)
    python3 ../kit-cursos/herramientas/nucleo/verificar_codigo.py --help
Termina con 0 si todo coincide y funciona (aunque haya avisos), con 1 si hay algún error y con 2 si los
argumentos están mal.
"""
import difflib
import io
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
for carpeta in (AQUI, AQUI.parent, AQUI.parent / "servicios", AQUI.parent / "lenguajes"):
    sys.path.insert(0, str(carpeta))
from argumentos import revisar                                                     # noqa: E402
from formato_academia import CARPETAS_IGNORADAS, FICHEROS_DE_TRABAJO, Informe, Markdown   # noqa: E402
import terminal                                                                    # noqa: E402
import servidor_http                                                               # noqa: E402
import bash as lenguaje_bash                                                       # noqa: E402
import java as lenguaje_java                                                       # noqa: E402
import formato_csv, formato_ini, formato_json, formato_markdown, formato_svg, formato_toml, formato_xml, formato_yaml  # noqa: E402,E401

FORMATOS = [formato_json, formato_yaml, formato_xml, formato_csv, formato_markdown, formato_toml, formato_ini, formato_svg]

# LOS EJECUTORES: los lenguajes cuyo código se ejecuta, en orden (manda el primero que diga que el fichero es suyo).
# Cada uno es (módulo de lenguajes/, método del Verificador que lo ejecuta y compara con el texto). El módulo tiene:
#   es_mio(fichero) -> bool    ¿es un programa suyo? (por ejemplo, por su extensión)
#   DE_VERIFICACION            opcional: los nombres de sus ficheros de verificación, que se suman a los comunes
#                              (son para el kit: no se comparan con los bloques ni son ficheros de datos)
# y el método recibe (md, línea del enlace «📁 Código», fichero, carpeta enlazada).
EJECUTORES = [(lenguaje_bash, "verificar_script"), (lenguaje_java, "verificar_java")]

ENLACE_CODIGO = re.compile(r"^📁 \*\*Código:\*\* \[[^\]]*\]\(([^)\s]+)\)")
SESION = re.compile(r"^\*\*En tu terminal\*\* \(`([^`]+)`\):\s*$")
SALIDA, SALIDA_DE_ERROR = "**Salida:**", "**Salida de error:**"
ENCADENADA = re.compile(r"sesion-(\d+)\.txt")
DE_VERIFICACION = {"entrada.txt", "args.txt", "termina-con-error.txt", "debe-fallar.txt", "separador.txt",
                   "codificacion.txt", "salida-variable.txt", servidor_http.NOMBRE}.union(
                   *(getattr(ejecutor, "DE_VERIFICACION", ()) for ejecutor, _ in EJECUTORES))


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
        self.cuentas = {"bloques": 0, "scripts": 0, "sesiones": 0, "datos": 0, "comparaciones": 0}
        self.compatibilidad_revisada = set()
        self.cadenas = {}               # carpeta → {nombre: pantalla, o el error con el que no se ha podido teclear}
        self.sesiones_mostradas = set() # sesiones encadenadas que muestra algún bloque
        self.java = None                # el ejecutor de Java (lenguajes/java.py), cuando hace falta

    def cerrar(self):
        """Al terminar: para lo que siga abierto (los proyectos de Java)."""
        if self.java:
            self.java.cerrar()

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
        # También los ficheros de verificación: un bloque puede enseñarlos (FORMATO.md 7.1). Van al final, para que,
        # si el bloque es igual a uno de ellos y a otro fichero, gane el otro (el que se ejecuta)
        ficheros = [f for f in sorted(carpeta.rglob("*")) if f.is_file()]
        candidatos = ([f for f in ficheros if not es_de_verificacion(f.name)]
                      + [f for f in ficheros if es_de_verificacion(f.name)])
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
        if es_de_verificacion(fichero.name):
            return              # se enseña, pero es para el kit: ningún ejecutor lo ejecuta
        metodo = next((m for ejecutor, m in EJECUTORES if ejecutor.es_mio(fichero)), None)
        if metodo:
            getattr(self, metodo)(md, i, fichero, carpeta)

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
                completa = t.completa
            otra = None
            if completa:
                # bash 3.2, en un contenedor limpio: un script que deja algo creado (una copia de seguridad) se
                # comporta igual que la primera vez
                with terminal.terminal(carpeta, con_docker=self.con_docker) as t:
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

    def verificar_java(self, md, i, fichero, carpeta):
        if self.java is None:
            self.java = lenguaje_java.Java(self)
        self.java.verificar(md, i, fichero, carpeta)

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
        if ENCADENADA.fullmatch(nombre):
            self.sesiones_mostradas.add(fichero.resolve())
            if carpeta not in self.cadenas:
                self.cadenas[carpeta] = self.teclear_cadena(carpeta)
            real = self.cadenas[carpeta][nombre]
            if isinstance(real, Exception):
                self.informe.error(md.rel, linea + 1, f"la sesión {nombre}: {real}")
                return
        else:
            try:
                ordenes = terminal.ordenes_de(fichero.read_text(encoding="utf-8"))
                with terminal.terminal(carpeta, self.no_se_copian(carpeta), con_docker=self.con_docker) as t:
                    real = t.sesion(ordenes)
            except terminal.ErrorDeTerminal as e:
                self.informe.error(md.rel, linea + 1, f"la sesión {nombre}: {e}")
                return
        self.comparar(md, linea, esperado, real, carpeta, f"la pantalla de {nombre}")

    @staticmethod
    def no_se_copian(carpeta):
        """Lo que no se copia a la terminal de una sesión: las órdenes de todas las sesiones de la carpeta y
        salida-variable.txt (son para el kit; un «ls» no los enseña)."""
        return {f.name for f in carpeta.iterdir() if re.fullmatch(r"sesion(-[\w-]+)?\.txt", f.name)} | {"salida-variable.txt"}

    def teclear_cadena(self, carpeta):
        """Las sesiones encadenadas de la carpeta (sesion-1.txt, sesion-2.txt…), tecleadas en orden en la misma
        terminal, cada una en una bash nueva, como las hace el alumno. Devuelve {nombre: pantalla, o el error}."""
        numeros = sorted((int(m.group(1)), f.name) for f in carpeta.iterdir()
                         if f.is_file() and (m := ENCADENADA.fullmatch(f.name)))
        nombres = [n for _, n in numeros]
        esperados = [f"sesion-{i}.txt" for i in range(1, len(nombres) + 1)]
        if nombres != esperados:
            problema = terminal.ErrorDeTerminal(
                f"las sesiones encadenadas de {self.rel(carpeta)}/ tienen que ir de sesion-1.txt en adelante, sin "
                f"saltos ni ceros delante (hay {', '.join(nombres)})")
            return {n: problema for n in nombres}
        resultado = {}
        try:
            tramos = [terminal.ordenes_de((carpeta / n).read_text(encoding="utf-8")) for n in nombres]
        except terminal.ErrorDeTerminal as e:
            return {n: e for n in nombres}
        try:
            with terminal.terminal(carpeta, self.no_se_copian(carpeta), con_docker=self.con_docker) as t:
                pantallas = t.sesiones(tramos)
        except terminal.ErrorDeTerminal as e:
            fallo = getattr(e, "tramo", None)
            pantallas = getattr(e, "pantallas", [])
            for i, n in enumerate(nombres):
                if fallo is None or i == fallo:
                    resultado[n] = e
                elif i > fallo:
                    resultado[n] = terminal.ErrorDeTerminal(
                        f"no se ha podido teclear: va encadenada detrás de {nombres[fallo]}, que falla")
                else:
                    resultado[n] = pantallas[i]
            return resultado
        return dict(zip(nombres, pantallas))

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
                    # Enlazada, o con una subcarpeta enlazada (en un proyecto de Java, src/main/java/es/x/)
                    if not any(e == hoja.resolve() or hoja.resolve() in e.parents for e in self.enlazadas):
                        self.informe.aviso(self.rel(hoja) + "/", 0, "carpeta de código que ningún módulo enlaza")
        for carpeta in sorted(self.enlazadas):
            for sesion in sorted(carpeta.iterdir()):
                if ENCADENADA.fullmatch(sesion.name) and sesion.resolve() not in self.sesiones_mostradas:
                    self.informe.aviso(self.rel(sesion), 0, "sesión encadenada que ningún bloque muestra: se teclea "
                                                           "igual, en su orden, pero el alumno no la ve")
            for script in sorted(carpeta.rglob("*.sh")):
                if script.resolve() not in self.mostrados:
                    self.informe.aviso(self.rel(script), 0, "script que ningún bloque del módulo muestra")
                    self.compatibilidad_3_2(script)
            for fuente in sorted(carpeta.rglob("*.java")):
                if fuente.resolve() not in self.mostrados and not {"target", "build"} & set(fuente.relative_to(carpeta).parts):
                    self.informe.aviso(self.rel(fuente), 0, "fichero de Java que ningún bloque del módulo muestra")
        self.revisar_datos()
        self.revisar_ignorados()

    def revisar_datos(self):
        """Los ficheros de datos de las carpetas enlazadas: válidos, o que fallen si la carpeta tiene debe-fallar.txt."""
        vistos, sin_pyyaml = set(), None
        for carpeta in sorted(self.enlazadas):
            debe_fallar = (carpeta / "debe-fallar.txt").is_file()
            if (carpeta / servidor_http.NOMBRE).is_file():
                try:
                    servidor_http.cargar(carpeta / servidor_http.NOMBRE)
                except servidor_http.ServidorMal as e:
                    for linea, mensaje in e.problemas:
                        self.informe.error(self.rel(carpeta / servidor_http.NOMBRE), linea, mensaje)
            de_datos = [(f, fmt) for f in sorted(carpeta.rglob("*")) if f.is_file() and not es_de_verificacion(f.name)
                        for fmt in FORMATOS if fmt.es_mio(f)]
            if debe_fallar and not any(not getattr(fmt, "SIEMPRE", False) for _, fmt in de_datos):
                self.informe.error(self.rel(carpeta / "debe-fallar.txt"), 0, "debe-fallar.txt en una carpeta sin ficheros de datos")
            cargados, tablas = {}, []
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
                if debe_fallar and not getattr(fmt, "SIEMPRE", False):
                    if not problemas:
                        self.informe.error(self.rel(f), 0, "su carpeta tiene debe-fallar.txt (está mal a propósito), pero es válido")
                    continue
                for linea, mensaje in problemas:
                    self.informe.error(self.rel(f), linea, mensaje)
                if not problemas and fmt in (formato_json, formato_yaml):
                    cargados.setdefault(f.with_suffix(""), []).append((f, fmt.cargar(f)))
                if not problemas and fmt is formato_csv:
                    tablas.append(f)
            for _, versiones in cargados.items():
                if len(versiones) > 1 and any(d != versiones[0][1] for _, d in versiones[1:]):
                    nombres = " y ".join(f.name for f, _ in versiones)
                    self.informe.error(self.rel(versiones[0][0].parent), 0, f"{nombres} no tienen los mismos datos "
                                                                           "(una conversión debe cargar lo mismo)")
            # Un CSV (o TSV) y un JSON con el mismo nombre: los mismos datos, con las reglas de FORMATO.md 7.1
            for f in tablas:
                json_fichero = next((g for g, _ in cargados.get(f.with_suffix(""), []) if g.suffix.lower() == ".json"), None)
                if json_fichero:
                    self.cuentas["comparaciones"] += 1
                    for linea, mensaje in formato_csv.comparar(f, f.parent, json_fichero):
                        self.informe.error(self.rel(f), linea, f"no coincide con {json_fichero.name}: {mensaje}")
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


def opcion_commit(argumentos, existe=lambda a: Path(a).exists()):
    """Saca --commit y su referencia de los argumentos. Devuelve (referencia o None, argumentos restantes).
    La referencia es opcional (HEAD): «--commit=REF», o la palabra siguiente si no es una opción ni una ruta."""
    ref, resto, i = None, [], 0
    while i < len(argumentos):
        a = argumentos[i]
        if a.startswith("--commit="):
            ref = a.split("=", 1)[1] or "HEAD"
        elif a == "--commit":
            ref = "HEAD"
            siguiente = argumentos[i + 1] if i + 1 < len(argumentos) else None
            if siguiente and not siguiente.startswith("-") and not existe(siguiente):
                ref, i = siguiente, i + 1
        else:
            resto.append(a)
        i += 1
    return ref, resto


def git(raiz, *argumentos, binario=False):
    r = subprocess.run(["git", "-C", str(raiz), *argumentos], capture_output=True, text=not binario)
    if r.returncode != 0:
        raise RuntimeError((r.stderr if not binario else r.stderr.decode(errors="replace")).strip())
    return r.stdout


def sacar_commit(raiz, ref, destino):
    """Saca la versión ref del curso de la carpeta raiz a destino con git archive, como la recibiría un clon.
    Devuelve (carpeta del curso dentro de destino, descripción del commit, cuántos cambios sin commit hay)."""
    try:
        commit = git(raiz, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").strip()
    except OSError:
        raise RuntimeError("no encuentro Git: --commit lo necesita")
    except RuntimeError:
        raise RuntimeError(f"«{ref}» no es un commit, una rama ni una etiqueta de este repositorio "
                           "(o la carpeta no es un repositorio de Git)")
    prefijo = git(raiz, "rev-parse", "--show-prefix").strip()     # el curso puede ser una subcarpeta
    arriba = git(raiz, "rev-parse", "--show-toplevel").strip()
    tar = git(arriba, "archive", "--format=tar", commit, *([prefijo] if prefijo else []), binario=True)
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        if hasattr(tarfile, "tar_filter"):
            t.extractall(destino, filter="tar")                 # conserva los permisos de ejecución
        else:
            t.extractall(destino)
    cambios = 0
    if commit == git(raiz, "rev-parse", "HEAD").strip():
        cambios = len([l for l in git(raiz, "status", "--porcelain", "--", ".").splitlines() if l.strip()])
    descripcion = git(raiz, "log", "-1", "--format=%h %s", commit).strip()
    return Path(destino) / prefijo, (descripcion if ref == "HEAD" else f"{ref}, {descripcion}"), cambios


def main():
    ref, sys.argv[1:] = opcion_commit(sys.argv[1:])
    usadas, _, rutas = revisar(__doc__, opciones=("--sin-docker", "--versiones", "--preparar-java"))
    if "--versiones" in usadas:
        if not terminal.hay_docker():
            print("❌ Sin Docker no hay imagen de la terminal del kit.", file=sys.stderr)
            sys.exit(1)
        print(terminal.versiones(), end="")
        try:
            print("\n" + terminal.versiones_java(), end="")
        except terminal.ErrorDeTerminal as e:
            print(f"❌ No se puede preparar la imagen de Java del kit:\n{e}", file=sys.stderr)
            sys.exit(1)
        return
    raiz = Path(".")
    temporal = None
    if ref:
        temporal = Path(tempfile.mkdtemp(prefix="kit-commit-"))
        try:
            copia, descripcion, cambios = sacar_commit(raiz, ref, temporal)
        except RuntimeError as e:
            shutil.rmtree(temporal, ignore_errors=True)
            print(f"❌ --commit: {e}", file=sys.stderr)
            sys.exit(2)
        faltan = [r for r in rutas if not (copia / Path(r).resolve().relative_to(raiz.resolve())).exists()]
        if faltan:
            shutil.rmtree(temporal, ignore_errors=True)
            print(f"❌ No está en ese commit: {', '.join(faltan)}. No se ha revisado nada.", file=sys.stderr)
            sys.exit(2)
        rutas = [str(copia / Path(r).resolve().relative_to(raiz.resolve())) for r in rutas]
        print(f"Se verifica el commit {descripcion}, en una copia como la de un clon.")
        if cambios:
            print(f"⚠️  Tienes {cambios} cambio(s) sin commit, que no entran en la verificación.")
        print()
        raiz = copia
    try:
        (preparar_java if "--preparar-java" in usadas else verificar)(raiz, rutas, usadas)
    finally:
        if temporal:
            shutil.rmtree(temporal, ignore_errors=True)


def carpetas_enlazadas(raiz, rutas):
    """Las carpetas que enlazan los «📁 Código» de los módulos (las que existen)."""
    carpetas = set()
    for ruta in ficheros_md(raiz, rutas):
        md = Markdown(ruta, str(ruta))
        for i, linea in enumerate(md.lineas):
            m = ENLACE_CODIGO.match(linea.strip()) if not md.en_codigo[i] else None
            if m and (ruta.parent / m.group(1)).resolve().is_dir():
                carpetas.add((ruta.parent / m.group(1)).resolve())
    return carpetas


def preparar_java(raiz, rutas, usadas):
    """--preparar-java: la única vez que hay red. Prepara la caché de cada proyecto de Maven o Gradle enlazado."""
    con_docker = False if "--sin-docker" in usadas else terminal.hay_docker()
    proyectos = lenguaje_java.proyectos_de(carpetas_enlazadas(raiz, rutas))
    if not proyectos:
        print("No hay proyectos de Maven ni de Gradle en las carpetas enlazadas: no hay nada que preparar.")
        return
    donde = (f"el volumen de Docker {lenguaje_java.volumen()}" if con_docker else
             f"las cachés del equipo ({lenguaje_java.repositorio_maven_local()} y {lenguaje_java.gradle_local()})")
    print(f"Preparando {len(proyectos)} proyecto(s) de Java en {donde}, con red…", flush=True)
    fallos = 0
    for tipo, proyecto in proyectos:
        nombre = "Maven" if tipo == "maven" else "Gradle"
        rel = proyecto.resolve().relative_to(raiz.resolve()).as_posix() + "/"
        error = lenguaje_java.preparar(tipo, proyecto, con_docker)
        if error:
            fallos += 1
            print(f"{rel}: ERROR: no se ha podido preparar ({nombre}): {error}")
        else:
            print(f"✅ Preparado ({nombre}): {rel}", flush=True)
    if fallos:
        print(f"❌ {fallos} proyecto(s) sin preparar.")
        sys.exit(1)
    print("✅ Caché de Java preparada: ya se puede verificar sin red.")


def verificar(raiz, rutas, usadas):
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
    try:
        for md in mds:
            verificador.verificar_md(Markdown(md, verificador.rel(md)))
    finally:
        verificador.cerrar()
    carpetas = [Path(r) for r in rutas if Path(r).is_dir()] or [raiz]
    verificador.revisar_codigo(carpetas if not any(Path(r).is_file() for r in rutas) else [])
    c = verificador.cuentas
    java = c.get("java", 0)
    resumen = (f"{len(mds)} ficheros revisados: {c['bloques']} bloques con su fichero, {c['scripts']} scripts "
               f"ejecutados, " + (f"{java} programas de Java, " if java else "")
               + f"{c['sesiones']} sesiones de terminal y {c['datos']} ficheros de datos"
               + (f" ({c['comparaciones']} CSV comparados con su JSON)." if c["comparaciones"] else "."))
    if con_docker:
        resumen += " En la terminal del kit (Docker, sin red): verificación completa."
    else:
        resumen += ("\n⚠️  Sin Docker: verificación parcial (la bash del equipo, sin cortar la red, con sus versiones y "
                    "sin bash 3.2"
                    + ("; para Java, el JDK, Maven y Gradle del equipo, con sus versiones" if java else "")
                    + "). Para cerrar una fase, verifica con Docker.")
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
