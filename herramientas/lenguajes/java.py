"""El ejecutor de Java (para verificar_codigo.py; no se ejecuta a mano).

Sale de herramientas/verificar_codigo.py del curso de Java (la primera edición), con las mismas reglas y las mismas
comparaciones (FORMATO.md, apartado 7.1, «Los de Java»), para que el kit dé el mismo resultado:

- ¿Es mío? Los ficheros .java. Los que no tienen main (una clase auxiliar, package-info, module-info) solo se
  comparan con su bloque.
- UN PROGRAMA SUELTO se ejecuta con «java Fichero.java» desde una copia de su carpeta, con las opciones de
  opciones-java.txt delante del fichero, los argumentos de args.txt detrás y entrada.txt como entrada estándar. Si
  tiene package y sus carpetas son las del paquete (src/es/tienda/app/Main.java con «package es.tienda.app;»), la
  copia es la de la raíz de las fuentes (src/, sin salir de codigo/) y se ejecuta desde la carpeta del programa, como
  en su sitio: el lanzador de código fuente (JDK 22 o posterior) encuentra las demás clases desde esa raíz.
- UN PROGRAMA DE UN PROYECTO DE MAVEN (hay un pom.xml en su carpeta o en una superior, sin salir de codigo/): el
  proyecto se construye UNA VEZ por verificación («mvn package», pruebas incluidas, y el classpath con
  dependency:build-classpath) y la clase se ejecuta con «java -cp <classpath> paquete.Clase» desde la carpeta del
  módulo (la del pom.xml más cercano), como en IntelliJ. La raíz es el pom.xml más alto (un multimódulo). Igual con
  GRADLE (build.gradle.kts o build.gradle; la raíz, la carpeta más exterior con settings.gradle.kts o settings.gradle,
  sin salir de codigo/; FORMATO.md, apartado 7): «gradle build» y el classpath que da la tarea de
  servicios/java/classpath.init.gradle.kts. entrada.txt, args.txt y opciones-java.txt pueden ir junto al fichero o
  en la raíz del módulo, y salida-variable.txt, también junto al pom.xml.
- Tras el enlace «📁 Código», o más abajo, tras otros ficheros del mismo proyecto (solo para el programa de la
  carpeta: su único fichero con main o, si hay varios, Main.java), antes del siguiente título o el siguiente
  programa:
    «**Salida:**» y un bloque ```text: su salida estándar (System.err no se compara).
    «**Sesión en la terminal:**» y un bloque ```text: se ejecuta en una terminal (pty) y cada línea de entrada.txt
      se teclea cuando el programa la espera (servicios/java/teclear.py); la transcripción completa, con lo
      tecleado y System.err, debe coincidir. Tiene que terminar con 0.
  Si la carpeta tiene termina-con-error.txt, debe terminar con un código distinto de 0, y tras su «**Salida:**»
  (opcional) viene «**Salida de error:**» con su System.err. Si no, debe terminar con 0.
- «**Salida de las pruebas:**» tras una clase de pruebas de un proyecto de Maven: se ejecutan solo esas pruebas
  («mvn test -Dtest=paquete.Clase») y se compara el resumen de Surefire: desde «Running» hasta «Results:», más el
  «Tests run:» del total, sin tiempos, trazas ni líneas vacías (resumen_pruebas()).
- solo-compilar.txt junto al programa: solo se compila con javac. Junto al pom.xml: el proyecto solo se construye
  (pruebas incluidas) y sus programas no se ejecutan.
- Los programas se ejecutan sin pantalla, con la salida en UTF-8 y en español (OPCIONES_JVM y LC_ALL=C.UTF-8,
  como el original), y tienen TIEMPO_MAXIMO segundos.

Dónde (servicios/terminal.py):
  - CON DOCKER: en la imagen de Java del kit (servicios/java/Dockerfile: Temurin, Maven y Gradle fijados), SIN RED.
    Maven y Gradle trabajan sin conexión (-o, --offline) con la caché del volumen de Docker VOLUMEN (o el que diga
    la variable de entorno KIT_JAVA_CACHE), que llena «verificar_codigo.py --preparar-java», la única vez que hay
    red. Si falta una dependencia, el error lo dice. Cada proyecto se copia a un contenedor que dura toda la
    verificación; cada programa suelto, a uno nuevo. Gradle, sin demonio (--no-daemon): el demonio de un proyecto
    seguiría vivo en su contenedor con el bloqueo de la caché compartida, y Gradle no puede pedirle que lo suelte
    desde otro contenedor («Timeout waiting to lock journal cache»).
  - SIN DOCKER: el java, javac, mvn y gradle del PATH del equipo, también sin conexión, con sus cachés (la de Maven,
    ~/.m2/repository o la de KIT_JAVA_M2; la de Gradle, ~/.gradle o la de GRADLE_USER_HOME), en una copia temporal.
    Es la verificación parcial: otras versiones pueden dar otra salida.
  El curso nunca se toca: target/, build/ y .gradle/ quedan en la copia.

APLICACIONES WEB DE SPRING BOOT: con un peticiones.txt junto al pom.xml, la clase con main no se ejecuta como un
programa: si tras ella (o más abajo, como la «**Salida:**») viene «**Con la aplicación arrancada:**» y un bloque
```text, se arranca en un puerto libre (--server.port), se espera a que acepte conexiones, se lanzan las órdenes de
peticiones.txt (curl, «VAR=$(curl … | jq -r .campo)», «curl … | jq -r .campo», sleep y cp) con ese puerto en lugar
del 8080 y se para (servicios/java/aplicacion.py, dentro de la terminal: con Docker, sin red, solo localhost). La
sesión se compara sin la cabecera Date, con los métodos de Allow ordenados, el puerto visto como 8080 y sin las
fechas y horas ISO (ni lo de salida-variable.txt). Sin ese bloque, el proyecto solo se construye. Con un servidor.txt
junto al pom.xml, los programas que nombra (una API simulada, «../api-externa/ApiDelTiempo.java», que escribe
«Escuchando en http://localhost:PUERTO/»; u otro proyecto de Spring Boot con sus opciones, «../catalogo
--server.port=8082», que se construye con -DskipTests y se arranca con java -jar) se arrancan antes, en orden, y se
paran después: para eso, la copia de la terminal es la carpeta que los contiene a todos. Un compose.yaml en el
servidor.txt todavía no se admite (necesita Docker dentro de la terminal). Un servidor.txt junto a un programa suelto
que lo nombra (el servidor de una página con fetch): ese programa solo se compila.
VENTANAS (sin pantalla, con las letras de la imagen): una aplicación de JavaFX (una clase que extiende Application,
en un proyecto con JavaFX) se ejecuta con -Dglass.platform=headless -Dprism.order=sw, JavaFX en el module path y el
lanzador servicios/java/CapturaVentana.java, que hace las acciones de acciones.txt (junto al programa o en la raíz
de su módulo), guarda la imagen de la ventana de delante y la cierra. Un programa de Swing con «public static JPanel
content()» no ejecuta su main: el lanzador CapturaSwing.java pinta ese panel (-Djava.awt.headless=true). Si tras el
enlace (y su «**Salida:**», si la hay) viene «**La ventana:**» y una imagen ![…](….png), la de ahora debe ser
idéntica, byte a byte. Si no lo es (o si la imagen todavía no existe), la de ahora se guarda en
.verificacion/ventanas/ (con la misma ruta que la del texto, desde la carpeta en la que se verifica) y el error lo
dice: si el cambio es correcto, el autor la copia encima de la del curso. Las imágenes se hacen con la imagen de Java
del kit (con Docker): sin Docker, con otras letras, salen distintas.
"""
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import terminal

EXTENSIONES = {".java"}
DE_VERIFICACION = {"opciones-java.txt", "solo-compilar.txt", "peticiones.txt", "servidor.txt", "acciones.txt"}
MAIN = re.compile(r"\bvoid\s+main\s*\(")
PAQUETE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.M)
TIEMPO_MAXIMO = 60                      # segundos por programa
# Salida en UTF-8 y configuración regional española: printf, String.format y Scanner usan la coma decimal
OPCIONES_JVM = ["-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8", "-Duser.language=es", "-Duser.country=ES"]
ENTORNO = {"LC_ALL": "C.UTF-8"}
OPCIONES_EXTRA = "opciones-java.txt"
SOLO_COMPILAR = "solo-compilar.txt"
SALIDA, SALIDA_DE_ERROR = "**Salida:**", "**Salida de error:**"
SESION, PRUEBAS = "**Sesión en la terminal:**", "**Salida de las pruebas:**"
LA_VENTANA, ARRANCADA = "**La ventana:**", "**Con la aplicación arrancada:**"
RESULTADOS = (SALIDA, SESION, LA_VENTANA, ARRANCADA)
PETICIONES, SERVIDOR, ACCIONES = "peticiones.txt", "servidor.txt", "acciones.txt"
APLICACION_FX = re.compile(r"\bextends\s+Application\b")
APLICACION_SWING = re.compile(r"\bpublic\s+static\s+JPanel\s+content\s*\(\s*\)")
JAR_FX = re.compile(r"^(javafx-[a-z]+)-\d")
IMAGEN = re.compile(r"^!\[[^\]]*\]\(([^)]+\.png)\)\s*$")
# Las fechas y horas de las respuestas (el «timestamp» de un error) cambian en cada ejecución
MARCA_DE_TIEMPO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?")
TIEMPO_APLICACION = 600     # segundos para toda la sesión de peticiones (arrancar, las órdenes y parar)
NO_COPIAR = {".gradle", ".idea", "out"}         # además de target/ y build/ (servicios/terminal.py)

SERVICIOS_JAVA = Path(__file__).resolve().parent.parent / "servicios" / "java"
EN_LA_IMAGEN = "/opt/kit-java"
VOLUMEN = "kit-java-cache"
PREPARAR = "ejecuta antes «verificar_codigo.py --preparar-java» (la única vez que se usa la red)"
SIN_RED = re.compile(r"offline mode|has not been downloaded from it before|No cached version|available for offline")
TIEMPO_PRUEBA = re.compile(r"(,| --)? Time elapsed: [\d.,]+ s")


def es_mio(fichero):
    return fichero.suffix in EXTENSIONES


def volumen():
    return os.environ.get("KIT_JAVA_CACHE") or VOLUMEN


def repositorio_maven_local():
    return Path(os.environ.get("KIT_JAVA_M2") or Path.home() / ".m2" / "repository")


def gradle_local():
    return Path(os.environ.get("GRADLE_USER_HOME") or Path.home() / ".gradle")


def clase_de(fichero):
    paquete = PAQUETE.search(fichero.read_text(encoding="utf-8"))
    return (paquete.group(1) + "." if paquete else "") + fichero.stem


def _arriba(carpeta):
    """La carpeta y las superiores, hasta codigo/ o la raíz del curso (la que tiene curso.json), sin incluirlas."""
    for c in [carpeta, *carpeta.parents]:
        if c.name == "codigo" or (c / "curso.json").exists():
            return
        yield c


def raiz_maven(carpeta):
    """(raíz, módulo) del proyecto Maven que contiene a carpeta, o None: el módulo es la carpeta con pom.xml más
    cercana y la raíz, la más alta (en un multimódulo, la que agrupa a todos)."""
    poms = [c for c in _arriba(Path(carpeta)) if (c / "pom.xml").exists()]
    return (poms[-1], poms[0]) if poms else None


BUILD_GRADLE = ("build.gradle.kts", "build.gradle")
SETTINGS_GRADLE = ("settings.gradle.kts", "settings.gradle")


def raiz_gradle(carpeta):
    """(raíz, subproyecto) del proyecto Gradle que contiene a carpeta, o None: el subproyecto es la carpeta con
    build.gradle.kts o build.gradle más cercana y la raíz, la más alta con settings.gradle.kts o settings.gradle (sin
    salir de codigo/)."""
    raiz = modulo = None
    for c in _arriba(Path(carpeta)):
        if modulo is None and any((c / n).exists() for n in BUILD_GRADLE):
            modulo = c
        if any((c / n).exists() for n in SETTINGS_GRADLE):
            raiz = c
    return (raiz or modulo, modulo) if modulo else None


def raiz_de_fuentes(fichero):
    """La carpeta que se copia para ejecutar un programa suelto: si tiene package y las carpetas de encima son las del
    paquete, la raíz de las fuentes (se sube tantas carpetas como partes tiene el paquete, sin llegar a codigo/); si
    no, su carpeta."""
    fichero = Path(fichero)
    paquete = PAQUETE.search(fichero.read_text(encoding="utf-8"))
    if not paquete:
        return fichero.parent
    partes = paquete.group(1).split(".")
    carpetas = list(_arriba(fichero.parent))       # la del fichero y las de encima, sin codigo/
    if len(carpetas) <= len(partes) or [c.name for c in carpetas[len(partes) - 1::-1]] != partes:
        return fichero.parent
    return carpetas[len(partes)]


def programa_de(carpeta):
    """El programa de la carpeta: su único fichero con main o, si hay varios, Main.java (None si no lo hay)."""
    con_main = [f for f in sorted(carpeta.glob("*.java")) if MAIN.search(f.read_text(encoding="utf-8"))]
    if len(con_main) == 1:
        return con_main[0]
    return carpeta / "Main.java" if carpeta / "Main.java" in con_main else None


def resumen_pruebas(salida):
    """El resumen de Surefire de la salida de «mvn test»: desde «Running» hasta «Results:» (que repite los fallos),
    más el «Tests run:» del total, sin tiempos, trazas («at …», «... 2 more», «Suppressed: …») ni líneas vacías.
    None si Maven no ha llegado a ejecutar las pruebas."""
    lineas = salida.splitlines()
    inicio = next((i for i, linea in enumerate(lineas) if "] Running " in linea), None)
    fin = next((i for i in range(len(lineas) - 1, -1, -1) if "] Tests run:" in lineas[i]), None)
    if inicio is None or fin is None:
        return None
    resultados = next((i for i in range(inicio, fin) if lineas[i].endswith("] Results:")), fin)
    resumen = []
    for linea in lineas[inicio:resultados] + [lineas[fin]]:
        linea = TIEMPO_PRUEBA.sub("", linea).rstrip()
        if linea.lstrip().startswith(("at ", "... ", "Suppressed: ")) or linea in ("", "[INFO]", "[ERROR]", "[WARNING]"):
            continue
        resumen.append(linea)
    return "\n".join(resumen)


def sangrar(texto):
    """El texto (la salida de una orden) con cada línea sangrada 4 espacios, para que en el informe se vea dentro de su
    error."""
    return "\n".join("    " + linea for linea in texto.strip().splitlines())


def _primero(carpetas, nombre):
    return next((c / nombre for c in carpetas if (c / nombre).is_file()), None)


def _sin_red(salida, herramienta):
    if SIN_RED.search(salida):
        return RuntimeError(f"faltan dependencias en la caché de {herramienta} (sin red no se descargan): "
                            f"{PREPARAR}\n{sangrar(salida.strip()[-1500:])}")
    return None


# -- dónde se ejecuta ----------------------------------------------------------------------------------------------

def abrir_terminal(carpeta, con_docker, red=False):
    """Una terminal (sin entrar todavía) con la copia de carpeta: en la imagen de Java con la caché montada, o la
    del equipo."""
    if con_docker:
        return terminal.Contenedor(carpeta, NO_COPIAR, imagen=terminal.imagen_java(), red=red,
                                   opciones=["-v", f"{volumen()}:{EN_LA_IMAGEN}/cache"])
    return terminal.Local(carpeta, NO_COPIAR)


def base_de(t):
    """La carpeta de la copia dentro de la terminal (para las rutas absolutas)."""
    return terminal.CASA if isinstance(t, terminal.Contenedor) else str(t.casa)


def orden_maven(t, *metas):
    local = [] if isinstance(t, terminal.Contenedor) else [f"-Dmaven.repo.local={repositorio_maven_local()}"]
    return ["mvn", "-o", "-B", *local, *metas]


def orden_gradle(t, *tareas):
    """Sin demonio también con Docker: el de un proyecto se quedaría con el bloqueo de la caché compartida."""
    if isinstance(t, terminal.Contenedor):
        init = f"{EN_LA_IMAGEN}/classpath.init.gradle.kts"
    else:
        init = str(SERVICIOS_JAVA / "classpath.init.gradle.kts")
    return ["gradle", "-q", "--offline", "--console=plain", "--no-configuration-cache", "--no-daemon",
            "--init-script", init, *tareas]


def entorno_de(t):
    """Las variables de los programas: sin pantalla (ni Docker ni Local pasan DISPLAY) y en UTF-8; sin Docker,
    además el JAVA_HOME y la caché de Gradle del equipo."""
    if isinstance(t, terminal.Contenedor):
        return dict(ENTORNO)
    extra = {"GRADLE_USER_HOME": str(gradle_local())}
    if os.environ.get("JAVA_HOME"):
        extra["JAVA_HOME"] = os.environ["JAVA_HOME"]
    return {**ENTORNO, **extra}


class Proyecto:
    """Un proyecto de Maven o Gradle copiado a una terminal que dura toda la verificación: se construye una vez y
    luego se ejecutan sus programas y sus pruebas."""

    def __init__(self, tipo, raiz, con_docker, copia=None):
        # copia: la carpeta que se copia a la terminal (la raíz o, con un servidor.txt, la que contiene también sus
        # servidores)
        self.tipo, self.raiz, self.con_docker, self.copia = tipo, raiz, con_docker, copia or raiz
        self.t = None
        self.lanzadores = {}        # (lanzador, module path de JavaFX) -> carpeta con el .class, en la terminal
        self.jars = {}              # proyecto de Spring Boot de un servidor.txt -> su .jar, en la terminal
        self.error = None           # el de la construcción, si falla (se repite para cada programa)
        self.construido = False
        self.classpaths = {}

    def terminal(self):
        if self.t is None:
            t = abrir_terminal(self.copia, self.con_docker)
            self.t = t.__enter__()
        return self.t

    def cerrar(self):
        if self.t is not None:
            self.t.__exit__(None, None, None)
            self.t = None

    def rel(self, carpeta):
        return Path(carpeta).relative_to(self.copia).as_posix()

    def dentro(self, carpeta):
        """La ruta de la carpeta (o el fichero) en la terminal."""
        rel = self.rel(carpeta)
        return base_de(self.terminal()) + ("" if rel == "." else f"/{rel}")

    def ejecutar(self, orden, carpeta=None, espera=600, entrada=None):
        """Ejecuta en la terminal del proyecto, desde la carpeta (de la raíz si no se dice)."""
        t = self.terminal()
        return t.ejecutar(orden, entrada, espera, self.rel(carpeta or self.raiz), entorno_de(t))

    def construir(self):
        if self.error:
            raise RuntimeError(self.error)
        if self.construido:
            return
        try:
            t = self.terminal()
            if self.tipo == "maven":
                codigo, out, err = self.ejecutar(orden_maven(t, "-q", "package", "dependency:build-classpath",
                                                             "-Dmdep.outputFile=${project.build.directory}/classpath.txt"))
                que = "mvn package"
            else:
                codigo, out, err = self.ejecutar(orden_gradle(t, "build"))
                que = "gradle build"
        except (OSError, terminal.ErrorDeTerminal) as e:
            self.error = f"no se puede construir {self.raiz.name}: {e}"
            raise RuntimeError(self.error)
        if codigo != 0:
            falta = _sin_red(out + err, "Maven" if self.tipo == "maven" else "Gradle")
            self.error = str(falta) if falta else f"{que} falla en {self.raiz.name}:\n{sangrar((out + err).strip()[-2000:])}"
            raise RuntimeError(self.error)
        self.construido = True

    def classpath(self, modulo):
        """El classpath del módulo, con las rutas de dentro de la terminal."""
        self.construir()
        if modulo not in self.classpaths:
            dentro = self.dentro(modulo)
            if self.tipo == "maven":
                codigo, out, err = self.ejecutar(["cat", f"{dentro}/target/classpath.txt"])
                if codigo != 0:
                    raise RuntimeError(f"no está el classpath de {modulo.name}: {err.strip()}")
                self.classpaths[modulo] = os.pathsep.join(filter(None, [f"{dentro}/target/classes", out.strip()]))
            else:
                ruta = ":".join(modulo.relative_to(self.raiz).parts)
                codigo, out, err = self.ejecutar(orden_gradle(self.t, f":{ruta}:printRuntimeClasspath" if ruta
                                                              else ":printRuntimeClasspath"))
                if codigo != 0:
                    raise RuntimeError(f"no se pudo obtener el classpath de {modulo.name}:\n{sangrar((out + err).strip()[-2000:])}")
                self.classpaths[modulo] = out.strip().splitlines()[-1]
        return self.classpaths[modulo]

    def pruebas(self, clase):
        """La salida de «mvn test -Dtest=clase»."""
        codigo, out, err = self.ejecutar(orden_maven(self.terminal(), "test", f"-Dtest={clase}",
                                                     "-Dsurefire.failIfNoSpecifiedTests=false"))
        return out + err


# -- la verificación -------------------------------------------------------------------------------------------------

class Java:
    """El ejecutor de Java de un Verificador (verificar_codigo.py): verificar() para cada fichero .java que un bloque
    muestra, y cerrar() al final."""

    def __init__(self, verificador):
        self.v = verificador
        self.proyectos = {}
        self.temporales = []        # carpetas temporales del equipo (sin Docker), que se borran al cerrar

    def cerrar(self):
        for p in self.proyectos.values():
            p.cerrar()
        self.proyectos.clear()
        for carpeta in self.temporales:
            shutil.rmtree(carpeta, ignore_errors=True)
        self.temporales.clear()

    def temporal(self, t):
        """Una carpeta vacía de usar y tirar en la terminal (fuera de la carpeta personal)."""
        if isinstance(t, terminal.Contenedor):
            ruta = f"/tmp/kit-java-{uuid.uuid4().hex[:10]}"
            t.ejecutar(["mkdir", "-p", ruta])
            return ruta
        ruta = tempfile.mkdtemp(prefix="kit-java-")
        self.temporales.append(ruta)
        return ruta

    def lanzador(self, t, nombre, modulos_fx=None, cache=None):
        """Compila el lanzador (CapturaVentana o CapturaSwing) en la terminal, una vez por terminal, y da la carpeta
        con su .class."""
        clave = (nombre, modulos_fx)
        if cache is not None and clave in cache:
            return cache[clave]
        fuente = (f"{EN_LA_IMAGEN}/{nombre}.java" if isinstance(t, terminal.Contenedor)
                  else str(SERVICIOS_JAVA / f"{nombre}.java"))
        destino = self.temporal(t)
        fx = ["--module-path", modulos_fx, "--add-modules", "javafx.controls"] if modulos_fx else []
        codigo, out, err = t.ejecutar(["javac", *fx, "-d", destino, fuente], None, TIEMPO_MAXIMO, None, entorno_de(t))
        if codigo != 0:
            raise RuntimeError(f"no compila {nombre}.java:\n{sangrar(out + err)}")
        if cache is not None:
            cache[clave] = destino
        return destino

    def proyecto(self, carpeta):
        """(Proyecto, módulo) de la carpeta, o (None, None) si es un programa suelto."""
        maven = raiz_maven(carpeta)
        gradle = None if maven else raiz_gradle(carpeta)
        if not (maven or gradle):
            return None, None
        tipo, (raiz, modulo) = ("maven", maven) if maven else ("gradle", gradle)
        if raiz not in self.proyectos:
            self.proyectos[raiz] = Proyecto(tipo, raiz, self.v.con_docker, copia_con_servidores(raiz, modulo))
        return self.proyectos[raiz], modulo

    # Lo que viene tras el enlace

    def siguiente_no_vacia(self, md, i):
        while i < len(md.lineas) and not md.lineas[i].strip():
            i += 1
        return i

    def bloque_en(self, md, k):
        return next((b for b in md.bloques if b[0] == k), None)

    def resultado_del_programa(self, md, j):
        """Dónde empieza lo que muestra el programa cuyo enlace está en la línea j: justo después o más abajo, tras
        otros ficheros del proyecto, hasta el siguiente título o el siguiente programa (un bloque con main que sea el
        programa de su carpeta, o uno de JavaScript enlazado). Si no hay, la primera línea no vacía tras el enlace."""
        k = self.siguiente_no_vacia(md, j + 1)
        i = k
        while i < len(md.lineas) and not (md.lineas[i].startswith("#") and not md.en_codigo[i]):
            linea = md.lineas[i].rstrip()
            if linea in RESULTADOS and not md.en_codigo[i]:
                return i
            bloque = self.bloque_en(md, i)
            if bloque:
                siguiente = self.siguiente_no_vacia(md, bloque[1] + 1)
                enlace = siguiente < len(md.lineas) and md.lineas[siguiente].startswith("📁 **Código:**")
                codigo = "\n".join(md.lineas[bloque[0] + 1:bloque[1]])
                if enlace and bloque[2] == "javascript":
                    break
                if enlace and bloque[2] == "java" and MAIN.search(codigo):
                    m = re.search(r"\]\(([^)\s]+)\)", md.lineas[siguiente])
                    carpeta = (md.ruta.parent / m.group(1)).resolve() if m else None
                    programa = programa_de(carpeta) if carpeta and carpeta.is_dir() else None
                    if programa is None or _normalizar(programa.read_text(encoding="utf-8")) == _normalizar(codigo):
                        break
                i = bloque[1] + 1
                continue
            i += 1
        return k

    def etiqueta(self, md, k, etiqueta):
        """Si la línea k es la etiqueta: (k, texto del bloque ```text que la sigue, índice tras el bloque); None si no
        lo es. Si falta el bloque, error y False."""
        if k >= len(md.lineas) or md.lineas[k].strip() != etiqueta:
            return None
        b = self.bloque_en(md, self.siguiente_no_vacia(md, k + 1))
        if not b:
            self.v.informe.error(md.rel, k + 1, f"falta el bloque ```text tras «{etiqueta}»")
            return False
        return k, "\n".join(md.lineas[b[0] + 1:b[1]]), b[1] + 1

    # El fichero

    def verificar(self, md, i, fichero, carpeta):
        texto = fichero.read_text(encoding="utf-8")
        donde = fichero.parent
        k = self.siguiente_no_vacia(md, i + 1)
        pruebas = self.etiqueta(md, k, PRUEBAS)
        if pruebas is not None:
            if pruebas:
                self.verificar_pruebas(md, i, fichero, *pruebas[:2])
            return
        if not MAIN.search(texto):
            return              # una clase auxiliar, package-info, module-info: solo se compara
        self.v.cuentas["java"] = self.v.cuentas.get("java", 0) + 1
        proyecto, modulo = self.proyecto(donde)
        buscar = [donde] + ([modulo] if modulo and modulo != donde else [])
        variable = _primero(buscar, "salida-variable.txt")
        mascara = variable.parent if variable else donde
        # Una aplicación web de Spring Boot con peticiones.txt: se arranca y se le hacen las peticiones
        if proyecto and proyecto.tipo == "maven" and (modulo / PETICIONES).is_file():
            k = self.resultado_del_programa(md, i)
            arrancada = self.etiqueta(md, k, ARRANCADA)
            if arrancada is None:
                self.construir(md, i, proyecto)
            elif arrancada:
                self.verificar_peticiones(md, i, fichero, proyecto, modulo, buscar, arrancada, mascara)
            return
        if proyecto and (modulo / SOLO_COMPILAR).is_file():
            self.construir(md, i, proyecto)
            return
        # El servidor de una página con fetch (su servidor.txt lo nombra): no termina, así que solo se compila
        lista = donde / SERVIDOR
        es_servidor = lista.is_file() and any(ruta == fichero.name for ruta, _ in lineas_de_servidor(lista))
        if (donde / SOLO_COMPILAR).is_file() or es_servidor:
            error = self.compilar(fichero)
            if error:
                self.v.informe.error(md.rel, i + 1, f"{fichero.name} no compila:\n{sangrar(error)}")
            return
        resultado = self.resultado_del_programa(md, i) if programa_de(donde) == fichero else k
        sesion = self.etiqueta(md, resultado, SESION)
        if sesion is not None:
            if sesion:
                self.verificar_sesion(md, i, fichero, proyecto, modulo, buscar, sesion, mascara)
            return
        # La imagen de la ventana (JavaFX o Swing): tras el enlace, y tras su «**Salida:**» si la hay
        salida = self.etiqueta(md, resultado, SALIDA)
        if salida is False:
            return
        despues = self.siguiente_no_vacia(md, salida[2]) if salida else resultado
        ventana = None
        if despues < len(md.lineas) and md.lineas[despues].strip() == LA_VENTANA:
            j = self.siguiente_no_vacia(md, despues + 1)
            imagen = IMAGEN.match(md.lineas[j].strip()) if j < len(md.lineas) else None
            if not imagen:
                self.v.informe.error(md.rel, despues + 1, f"falta la imagen ![…](….png) tras «{LA_VENTANA}»")
                return
            ventana = (md.ruta.parent / imagen.group(1)).resolve()
            despues = self.siguiente_no_vacia(md, j + 1)
        try:
            codigo, out, err, png = self.ejecutar(fichero, proyecto, modulo, buscar, captura=ventana is not None)
        except RuntimeError as e:
            self.v.informe.error(md.rel, i + 1, str(e))
            return
        nombre = self.v.rel(fichero)
        con_error = (donde / "termina-con-error.txt").is_file()
        if con_error and codigo == 0:
            self.v.informe.error(md.rel, i + 1, f"{nombre} lleva termina-con-error.txt pero termina bien (código 0)")
            return
        if not con_error and codigo != 0:
            self.v.informe.error(md.rel, i + 1, f"{nombre} termina con el código {codigo}:\n{sangrar(err.strip()[:1500])}")
            return
        if ventana is not None:
            self.comparar_ventana(md, despues_de_la_etiqueta(md, LA_VENTANA, resultado), fichero, ventana, png)
        if salida:
            self.v.comparar(md, salida[0], salida[1], out, mascara, f"la salida de {fichero.name}")
        if con_error:
            error = self.etiqueta(md, despues, SALIDA_DE_ERROR)
            if error:
                self.v.comparar(md, error[0], error[1], err, mascara, f"la salida de error de {fichero.name}")
            elif error is None:
                self.v.informe.error(md.rel, i + 1, f"{fichero.name} lleva termina-con-error.txt: falta "
                                                    f"«{SALIDA_DE_ERROR}» y su bloque")

    def construir(self, md, i, proyecto):
        try:
            proyecto.construir()
        except RuntimeError as e:
            self.v.informe.error(md.rel, i + 1, str(e))

    def comparar_ventana(self, md, linea, fichero, ventana, png):
        """La imagen de ahora (png) debe ser la del texto, byte a byte. Si no, se guarda en .verificacion/ventanas/."""
        if png is None:
            self.v.informe.error(md.rel, linea + 1, f"{fichero.name} no ha guardado la imagen de su ventana")
            return
        if ventana.is_file() and ventana.read_bytes() == png:
            return
        nueva = Path.cwd() / ".verificacion" / "ventanas" / self.v.rel(ventana)
        nueva.parent.mkdir(parents=True, exist_ok=True)
        nueva.write_bytes(png)
        donde = nueva.relative_to(Path.cwd()).as_posix()
        if not ventana.is_file():
            self.v.informe.error(md.rel, linea + 1, f"no existe la imagen {self.v.rel(ventana)}: la de ahora está en "
                                                    f"{donde} (si es correcta, cópiala ahí)")
        else:
            self.v.informe.error(md.rel, linea + 1, f"la ventana de {fichero.name} no es como en la imagen "
                                                    f"{self.v.rel(ventana)}: la de ahora está en {donde} (si el "
                                                    "cambio es correcto, cópiala encima)")

    def orden(self, fichero, proyecto, modulo, buscar, t, captura=None, raiz=None):
        """La orden de java (lista) y la carpeta (relativa a la copia) desde la que se ejecuta. Una aplicación de JavaFX
        va con su lanzador, CapturaVentana, y un programa de Swing con content(), con CapturaSwing; los dos guardan
        la imagen de la ventana en captura (una ruta de la terminal) si se pide. Un programa suelto se ejecuta desde
        su carpeta, dentro de la copia de raiz (raiz_de_fuentes(); su carpeta si no se dice)."""
        argumentos = _primero(buscar, "args.txt")
        opciones = _primero(buscar, OPCIONES_EXTRA)
        extra = shlex.split(argumentos.read_text(encoding="utf-8")) if argumentos else []
        jvm = shlex.split(opciones.read_text(encoding="utf-8")) if opciones else []
        fuente = fichero.read_text(encoding="utf-8")
        captura_opcion = [f"-Dcaptura.fichero={captura}"] if captura else []
        if proyecto:
            classpath = proyecto.classpath(modulo)
            clase = clase_de(fichero)
            if APLICACION_FX.search(fuente) and "openjfx" in classpath:
                rutas = classpath.split(os.pathsep)
                javafx = [r for r in rutas if "openjfx" in r and JAR_FX.match(Path(r).name)]
                resto = [r for r in rutas if r not in javafx]
                modulos = sorted({JAR_FX.match(Path(r).name).group(1).replace("-", ".") for r in javafx})
                modulos_fx = os.pathsep.join(javafx)
                acciones = _primero(buscar, ACCIONES)
                programa = ["-Dglass.platform=headless", "-Dprism.order=sw", "--enable-native-access=javafx.graphics",
                            "--module-path", modulos_fx, "--add-modules", ",".join(modulos), *captura_opcion,
                            *([f"-Dcaptura.acciones={proyecto.dentro(acciones)}"] if acciones else []),
                            "-cp", os.pathsep.join([self.lanzador(t, "CapturaVentana", modulos_fx, proyecto.lanzadores),
                                                    *resto]), "CapturaVentana", clase]
            elif APLICACION_SWING.search(fuente):
                programa = ["-Djava.awt.headless=true", *captura_opcion, "-cp",
                            os.pathsep.join([self.lanzador(t, "CapturaSwing", None, proyecto.lanzadores), classpath]),
                            "CapturaSwing", clase]
            else:
                programa = ["-cp", classpath, clase]
            return ["java", *OPCIONES_JVM, *jvm, *programa, *extra], proyecto.rel(modulo)
        rel = fichero.parent.relative_to(raiz or fichero.parent).as_posix()
        desde = None if rel == "." else rel
        if APLICACION_SWING.search(fuente):
            # Un programa suelto de Swing: se compila su carpeta y se pinta su content()
            compilado = self.temporal(t)
            fuentes = [f.name for f in sorted(fichero.parent.glob("*.java"))]
            codigo, out, err = t.ejecutar(["javac", "-encoding", "UTF-8", "-d", compilado, *fuentes], None,
                                          TIEMPO_MAXIMO, desde, entorno_de(t))
            if codigo != 0:
                raise RuntimeError(f"{fichero.name} no compila:\n{sangrar(out + err)}")
            clase = clase_de(fichero)
            programa = ["-Djava.awt.headless=true", *captura_opcion, "-cp",
                        os.pathsep.join([self.lanzador(t, "CapturaSwing"), compilado]), "CapturaSwing", clase]
            return ["java", *OPCIONES_JVM, *jvm, *programa, *extra], desde
        return ["java", *OPCIONES_JVM, *jvm, fichero.name, *extra], desde

    def ejecutar(self, fichero, proyecto, modulo, buscar, captura=False):
        """(código, salida, salida de error, imagen de la ventana o None)."""
        entrada = _primero(buscar, "entrada.txt")
        datos = entrada.read_bytes() if entrada else b""
        raiz = None if proyecto else raiz_de_fuentes(fichero)

        def en(t):
            ruta = f"{self.temporal(t)}/ventana.png" if captura else None
            orden, desde = self.orden(fichero, proyecto, modulo, buscar, t, ruta, raiz)
            codigo, out, err = t.ejecutar(orden, datos, TIEMPO_MAXIMO, desde, entorno_de(t))
            return codigo, out, err, (t.leer(ruta) if ruta else None)

        try:
            if proyecto:
                return en(proyecto.terminal())
            with abrir_terminal(raiz, self.v.con_docker) as t:
                return en(t)
        except terminal.ErrorDeTerminal as e:
            raise RuntimeError(f"{fichero.name}: {e}")
        except OSError as e:
            raise RuntimeError(f"{fichero.name}: no se puede ejecutar ({e}); sin Docker hacen falta java, javac, mvn "
                               "y gradle en el PATH")

    def verificar_sesion(self, md, i, fichero, proyecto, modulo, buscar, sesion, mascara):
        entrada = _primero(buscar, "entrada.txt")
        try:
            if proyecto:
                t = proyecto.terminal()
                codigo, texto, err = self._teclear(t, fichero, proyecto, modulo, buscar, entrada, proyecto.copia)
            else:
                raiz = raiz_de_fuentes(fichero)
                with abrir_terminal(raiz, self.v.con_docker) as t:
                    codigo, texto, err = self._teclear(t, fichero, None, None, buscar, entrada, raiz)
        except (RuntimeError, terminal.ErrorDeTerminal, OSError) as e:
            self.v.informe.error(md.rel, i + 1, f"{fichero.name}: {e}")
            return
        if codigo == teclear_no_termina():
            self.v.informe.error(md.rel, i + 1, f"{fichero.name} no termina en {TIEMPO_MAXIMO} s")
        elif codigo != 0:
            self.v.informe.error(md.rel, i + 1, f"{self.v.rel(fichero)} termina con el código {codigo}:\n"
                                                f"{sangrar(texto.strip()[-800:] + chr(10) + err.strip()[-400:])}")
        else:
            self.v.comparar(md, sesion[0], sesion[1], texto, mascara, f"la sesión en la terminal de {fichero.name}")

    def _teclear(self, t, fichero, proyecto, modulo, buscar, entrada, copia):
        orden, desde = self.orden(fichero, proyecto, modulo, buscar, t, raiz=None if proyecto else copia)
        base = base_de(t)
        ruta = f"{base}/{entrada.relative_to(copia).as_posix()}" if entrada else "-"
        return t.ejecutar([*python_de(t), _del_kit(t, "teclear.py"), ruta, str(TIEMPO_MAXIMO), "--", *orden], None,
                          TIEMPO_MAXIMO + 30, desde, entorno_de(t))

    # Spring Boot

    def verificar_peticiones(self, md, i, fichero, proyecto, modulo, buscar, arrancada, mascara):
        try:
            real = self.sesion_curl(fichero, proyecto, modulo, buscar)
        except (RuntimeError, terminal.ErrorDeTerminal, OSError) as e:
            self.v.informe.error(md.rel, i + 1, f"{fichero.name}: {e}")
            return
        self.v.comparar(md, arrancada[0], MARCA_DE_TIEMPO.sub("<fecha y hora>", arrancada[1]),
                        MARCA_DE_TIEMPO.sub("<fecha y hora>", real), mascara,
                        f"la sesión con la aplicación arrancada de {fichero.name}")

    def sesion_curl(self, fichero, proyecto, modulo, buscar):
        """Arranca los servidores del servidor.txt y la aplicación en la terminal del proyecto, lanza las peticiones y
        lo para todo (servicios/java/aplicacion.py). Devuelve la sesión."""
        t = proyecto.terminal()
        orden, desde = self.orden(fichero, proyecto, modulo, buscar, t)
        servidores = []
        lista = modulo / SERVIDOR
        for ruta, opciones in (lineas_de_servidor(lista) if lista.is_file() else []):
            programa = (modulo / ruta).resolve()
            if programa != proyecto.copia and proyecto.copia not in programa.parents:
                raise RuntimeError(f"{SERVIDOR}: {ruta} está fuera de la carpeta del ejemplo")
            if opciones and not (programa.is_dir() and (programa / "pom.xml").is_file()):
                raise RuntimeError(f"{SERVIDOR}: las opciones {' '.join(opciones)} solo valen para un proyecto de Spring Boot")
            if programa.name in ("compose.yaml", "compose.yml"):
                raise RuntimeError(f"{SERVIDOR}: {ruta}: el kit todavía no arranca un compose.yaml como servidor")
            if programa.is_dir() and (programa / "pom.xml").is_file():
                servidores.append({"tipo": "spring", "carpeta": proyecto.dentro(programa), "nombre": programa.name,
                                   "orden": ["java", "-jar", self.jar_de(proyecto, programa), *opciones],
                                   "puerto": puerto_de(programa, opciones)})
            elif programa.is_file():
                servidores.append({"tipo": "java", "carpeta": proyecto.dentro(programa.parent), "nombre": programa.name,
                                   "orden": ["java", "-Dstdout.encoding=UTF-8", programa.name]})
            else:
                raise RuntimeError(f"{SERVIDOR}: no existe {ruta}")
        encargo = {"servidores": servidores, "espera": TIEMPO_MAXIMO,
                   "aplicacion": {"carpeta": proyecto.dentro(modulo), "orden": orden, "nombre": fichero.name},
                   "peticiones": proyecto.dentro(modulo / PETICIONES)}
        codigo, out, err = t.ejecutar([*python_de(t), _del_kit(t, "aplicacion.py")],
                                      json.dumps(encargo).encode("utf-8"), TIEMPO_APLICACION, desde, entorno_de(t))
        try:
            respuesta = json.loads(out)
        except ValueError:
            raise RuntimeError(f"aplicacion.py no responde (código {codigo}):\n{sangrar(out + err)}")
        if "error" in respuesta:
            raise RuntimeError(respuesta["error"])
        return respuesta["sesion"]

    def jar_de(self, proyecto, programa):
        """Construye (una vez, sin pruebas y sin red) otro proyecto de Spring Boot de un servidor.txt y da su .jar, en
        la terminal."""
        if programa not in proyecto.jars:
            codigo, out, err = proyecto.ejecutar(orden_maven(proyecto.terminal(), "-q", "-DskipTests", "package"),
                                                 programa)
            if codigo != 0:
                falta = _sin_red(out + err, "Maven")
                raise RuntimeError(str(falta) if falta else f"{programa.name} no se construye:\n{sangrar((out + err)[-2000:])}")
            codigo, out, _ = proyecto.ejecutar(["ls", "target"], programa)
            jars = sorted(n for n in out.split() if n.endswith(".jar") and not n.endswith(".original"))
            if not jars:
                raise RuntimeError(f"{programa.name}: no hay ningún .jar en target/")
            proyecto.jars[programa] = f"{proyecto.dentro(programa)}/target/{jars[0]}"
        return proyecto.jars[programa]

    def compilar(self, fichero):
        """Compila el fichero solo, sin ejecutarlo, desde su carpeta: el error de javac, o None si compila."""
        try:
            with abrir_terminal(fichero.parent, self.v.con_docker) as t:
                destino = tempfile.mkdtemp(prefix="kit-javac-") if isinstance(t, terminal.Local) else "/tmp/kit-javac"
                try:
                    codigo, out, err = t.ejecutar(["javac", "-d", destino, fichero.name], None, TIEMPO_MAXIMO,
                                                  None, entorno_de(t))
                finally:
                    if isinstance(t, terminal.Local):
                        shutil.rmtree(destino, ignore_errors=True)
        except terminal.ErrorDeTerminal as e:
            return str(e)
        except OSError as e:
            return f"no se puede ejecutar javac ({e}); sin Docker hace falta un JDK en el PATH"
        return (out + err).strip() if codigo != 0 else None

    def verificar_pruebas(self, md, i, fichero, linea, esperado):
        proyecto, _ = self.proyecto(fichero.parent)
        if proyecto is None or proyecto.tipo != "maven":
            self.v.informe.error(md.rel, i + 1, f"{fichero.name} no está en un proyecto Maven")
            return
        self.v.cuentas["java"] = self.v.cuentas.get("java", 0) + 1
        clase = clase_de(fichero)
        try:
            salida = proyecto.pruebas(clase)
        except (terminal.ErrorDeTerminal, OSError) as e:
            self.v.informe.error(md.rel, i + 1, f"{fichero.name}: {e}")
            return
        real = resumen_pruebas(salida)
        if real is None:
            falta = _sin_red(salida, "Maven")
            self.v.informe.error(md.rel, i + 1, str(falta) if falta else
                                 f"Maven no ha ejecutado las pruebas de {clase}:\n{sangrar(salida.strip()[-2000:])}")
            return
        self.v.comparar(md, linea, esperado, real, fichero.parent, f"la salida de las pruebas de {fichero.name}")


def python_de(t):
    return ["python3"] if isinstance(t, terminal.Contenedor) else [sys.executable]


def _del_kit(t, nombre):
    """Un programa del kit (servicios/java/), en la terminal: en la imagen o en el equipo."""
    return f"{EN_LA_IMAGEN}/{nombre}" if isinstance(t, terminal.Contenedor) else str(SERVICIOS_JAVA / nombre)


def despues_de_la_etiqueta(md, etiqueta, desde):
    """La línea de la etiqueta desde la línea desde (para dar el error en ella)."""
    for k in range(desde, len(md.lineas)):
        if md.lineas[k].strip() == etiqueta:
            return k
    return desde


def lineas_de_servidor(lista):
    """Las líneas de un servidor.txt: [(ruta, opciones)], sin las vacías ni los comentarios (#). Cada línea es la ruta,
    las opciones que empiezan por -- (solo para un proyecto de Spring Boot) y una descripción, que no se usa."""
    servidores = []
    for linea in Path(lista).read_text(encoding="utf-8").splitlines():
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        ruta, *resto = linea.split()
        opciones = []
        for palabra in resto:
            if not palabra.startswith("--"):
                break
            opciones.append(palabra)
        servidores.append((ruta, opciones))
    return servidores


def copia_con_servidores(raiz, modulo):
    """La carpeta que se copia a la terminal de un proyecto: su raíz o, si junto a su pom.xml hay un servidor.txt, la
    más baja que contiene también a todos sus servidores (sin salir de codigo/)."""
    lista = Path(modulo) / SERVIDOR
    if not lista.is_file():
        return raiz
    rutas = [raiz]
    for ruta, _ in lineas_de_servidor(lista):
        programa = (Path(modulo) / ruta).resolve()
        rutas.append(programa if programa.is_dir() else programa.parent)
    comun = Path(os.path.commonpath([str(r) for r in rutas]))
    return comun if comun.name != "codigo" and any(p.name == "codigo" for p in comun.parents) else raiz


def puerto_de(proyecto, opciones=()):
    """El server.port de las opciones, del application-<perfil>.properties del perfil de las opciones o del
    application.properties de un proyecto de Spring Boot (8080 si no lo dice)."""
    perfiles = []
    for opcion in opciones:
        if opcion.startswith("--server.port="):
            return int(opcion.split("=", 1)[1])
        if opcion.startswith("--spring.profiles.active="):
            perfiles = [p.strip() for p in opcion.split("=", 1)[1].split(",")]
    recursos = Path(proyecto) / "src" / "main" / "resources"
    for nombre in [f"application-{p}.properties" for p in reversed(perfiles)] + ["application.properties"]:
        propiedades = recursos / nombre
        if propiedades.is_file():
            for linea in propiedades.read_text(encoding="utf-8").splitlines():
                if linea.strip().startswith("server.port="):
                    return int(linea.split("=", 1)[1].strip())
    return 8080


def teclear_no_termina():
    return 124          # el código con el que termina servicios/java/teclear.py si el programa no termina


def _normalizar(texto):
    return "\n".join(linea.rstrip() for linea in texto.strip("\n").splitlines())


# -- --preparar-java -------------------------------------------------------------------------------------------------

def proyectos_de(carpetas):
    """Los proyectos (tipo, raíz) de las carpetas enlazadas: el de cada carpeta y los que haya dentro, sin repetir."""
    vistos = {}
    for carpeta in sorted(carpetas):
        candidatas = [carpeta] + sorted(p.parent for nombre in ("pom.xml", *BUILD_GRADLE)
                                        for p in carpeta.rglob(nombre)
                                        if not NO_COPIAR.union({"target", "build"}) & set(p.parts))
        # Los proyectos de Spring Boot que arranca el servidor.txt de un proyecto, aunque no estén enlazados
        for c in list(candidatas):
            lista = c / SERVIDOR
            if (c / "pom.xml").is_file() and lista.is_file():
                candidatas += [(c / ruta).resolve() for ruta, _ in lineas_de_servidor(lista)
                               if ((c / ruta).resolve() / "pom.xml").is_file()]
        for c in candidatas:
            maven = raiz_maven(c)
            gradle = None if maven else raiz_gradle(c)
            if maven:
                vistos.setdefault(maven[0], "maven")
            elif gradle:
                vistos.setdefault(gradle[0], "gradle")
    return sorted((tipo, raiz) for raiz, tipo in vistos.items())


def metas_de_preparar(tipo):
    """Lo que construye --preparar-java: lo mismo que la verificación, más sus pruebas (sin parar si alguna falla a
    propósito). Con Maven, sin el repackage de Spring Boot, que falla en un proyecto sin clase con main (una
    autoconfiguración): lo que se quiere es la caché, no el .jar."""
    if tipo == "maven":
        return ["package", "dependency:build-classpath", "-Dmdep.outputFile=${project.build.directory}/classpath.txt",
                "-Dmaven.test.failure.ignore=true", "-Dspring-boot.repackage.skip=true"]
    # -PkitPreparar: las pruebas que fallan a propósito no paran la construcción (classpath.init.gradle.kts)
    return ["build", "printRuntimeClasspath", "--continue", "-PkitPreparar"]


def preparar(tipo, raiz, con_docker):
    """Construye el proyecto CON RED para llenar la caché (el volumen de Docker o las del equipo), con
    metas_de_preparar(). None si va bien, o el error."""
    metas = metas_de_preparar(tipo)
    if con_docker:
        try:
            with abrir_terminal(raiz, True, red=True) as t:
                if tipo == "maven":
                    orden = ["mvn", "-B", "-q", *metas]
                else:
                    orden = ["gradle", "-q", "--console=plain", "--no-configuration-cache", "--no-daemon",
                             "--init-script", f"{EN_LA_IMAGEN}/classpath.init.gradle.kts", *metas]
                codigo, out, err = t.ejecutar(orden, espera=1800, entorno=dict(ENTORNO))
        except terminal.ErrorDeTerminal as e:
            return str(e)
    else:
        copia = Path(tempfile.mkdtemp(prefix="kit-preparar-"))
        try:
            shutil.copytree(raiz, copia / raiz.name, ignore=shutil.ignore_patterns("target", "build", *NO_COPIAR))
            if tipo == "maven":
                orden = ["mvn", "-B", "-q", f"-Dmaven.repo.local={repositorio_maven_local()}", *metas]
            else:
                orden = ["gradle", "-q", "--console=plain", "--no-configuration-cache", "--no-daemon",
                         "--init-script", str(SERVICIOS_JAVA / "classpath.init.gradle.kts"), *metas]
            entorno = {**os.environ, **ENTORNO, "GRADLE_USER_HOME": str(gradle_local())}
            r = subprocess.run(orden, cwd=copia / raiz.name, capture_output=True, text=True, env=entorno, timeout=1800)
            codigo, out, err = r.returncode, r.stdout, r.stderr
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"no se puede ejecutar {'mvn' if tipo == 'maven' else 'gradle'}: {e}"
        finally:
            shutil.rmtree(copia, ignore_errors=True)
    if codigo != 0:
        return f"{'mvn' if tipo == 'maven' else 'gradle'} falla (código {codigo}):\n{sangrar((out + err).strip()[-2000:])}"
    return None
