"""El ejecutor de Java (para verificar_codigo.py; no se ejecuta a mano).

Sale de herramientas/verificar_codigo.py del curso de Java (la primera edición), con las mismas reglas y las mismas
comparaciones (FORMATO.md, apartado 7.1, «Los de Java»), para que el kit dé el mismo resultado:

- ¿Es mío? Los ficheros .java. Los que no tienen main (una clase auxiliar, package-info, module-info) solo se
  comparan con su bloque.
- UN PROGRAMA SUELTO se ejecuta con «java Fichero.java» desde una copia de su carpeta, con las opciones de
  opciones-java.txt delante del fichero, los argumentos de args.txt detrás y entrada.txt como entrada estándar.
- UN PROGRAMA DE UN PROYECTO DE MAVEN (hay un pom.xml en su carpeta o en una superior, sin salir de codigo/): el
  proyecto se construye UNA VEZ por verificación («mvn package», pruebas incluidas, y el classpath con
  dependency:build-classpath) y la clase se ejecuta con «java -cp <classpath> paquete.Clase» desde la carpeta del
  módulo (la del pom.xml más cercano), como en IntelliJ. La raíz es el pom.xml más alto (un multimódulo). Igual con
  GRADLE (build.gradle.kts; la raíz, la del settings.gradle.kts): «gradle build» y el classpath que da la tarea de
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
    verificación; cada programa suelto, a uno nuevo.
  - SIN DOCKER: el java, javac, mvn y gradle del PATH del equipo, también sin conexión, con sus cachés (la de Maven,
    ~/.m2/repository o la de KIT_JAVA_M2; la de Gradle, ~/.gradle o la de GRADLE_USER_HOME), en una copia temporal.
    Es la verificación parcial: otras versiones pueden dar otra salida.
  El curso nunca se toca: target/, build/ y .gradle/ quedan en la copia.

Lo que vendrá (T5b): peticiones.txt y servidor.txt (Spring Boot), acciones.txt y «**La ventana:**» (JavaFX) y
Swing sin pantalla. Hoy, «**La ventana:**» no se compara: el programa solo se ejecuta.
"""
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import terminal

EXTENSIONES = {".java"}
DE_VERIFICACION = {"opciones-java.txt", "solo-compilar.txt"}
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
RESULTADOS = (SALIDA, SESION, "**La ventana:**", "**Con la aplicación arrancada:**")
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


def raiz_gradle(carpeta):
    """(raíz, subproyecto) del proyecto Gradle que contiene a carpeta, o None."""
    raiz = modulo = None
    for c in _arriba(Path(carpeta)):
        if modulo is None and (c / "build.gradle.kts").exists():
            modulo = c
        if (c / "settings.gradle.kts").exists():
            raiz = c
    return (raiz or modulo, modulo) if modulo else None


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
    if isinstance(t, terminal.Contenedor):
        init = f"{EN_LA_IMAGEN}/classpath.init.gradle.kts"
        extra = []
    else:
        init, extra = str(SERVICIOS_JAVA / "classpath.init.gradle.kts"), ["--no-daemon"]
    return ["gradle", "-q", "--offline", "--console=plain", "--no-configuration-cache", *extra,
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

    def __init__(self, tipo, raiz, con_docker):
        self.tipo, self.raiz, self.con_docker = tipo, raiz, con_docker
        self.t = None
        self.error = None           # el de la construcción, si falla (se repite para cada programa)
        self.construido = False
        self.classpaths = {}

    def terminal(self):
        if self.t is None:
            t = abrir_terminal(self.raiz, self.con_docker)
            self.t = t.__enter__()
        return self.t

    def cerrar(self):
        if self.t is not None:
            self.t.__exit__(None, None, None)
            self.t = None

    def ejecutar(self, orden, modulo=None, espera=600):
        directorio = modulo.relative_to(self.raiz).as_posix() if modulo else None
        return self.terminal().ejecutar(orden, espera=espera, directorio=directorio, entorno=entorno_de(self.terminal()))

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
            base = base_de(self.t)
            rel = modulo.relative_to(self.raiz).as_posix()
            dentro = f"{base}/{rel}" if rel != "." else base
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

    def cerrar(self):
        for p in self.proyectos.values():
            p.cerrar()
        self.proyectos.clear()

    def proyecto(self, carpeta):
        """(Proyecto, módulo) de la carpeta, o (None, None) si es un programa suelto."""
        maven = raiz_maven(carpeta)
        gradle = None if maven else raiz_gradle(carpeta)
        if not (maven or gradle):
            return None, None
        tipo, (raiz, modulo) = ("maven", maven) if maven else ("gradle", gradle)
        if raiz not in self.proyectos:
            self.proyectos[raiz] = Proyecto(tipo, raiz, self.v.con_docker)
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
        if proyecto and (modulo / SOLO_COMPILAR).is_file():
            try:
                proyecto.construir()
            except RuntimeError as e:
                self.v.informe.error(md.rel, i + 1, str(e))
            return
        if (donde / SOLO_COMPILAR).is_file():
            error = self.compilar(fichero)
            if error:
                self.v.informe.error(md.rel, i + 1, f"{fichero.name} no compila:\n{sangrar(error)}")
            return
        resultado = self.resultado_del_programa(md, i) if programa_de(donde) == fichero else k
        buscar = [donde] + ([modulo] if modulo and modulo != donde else [])
        variable = _primero(buscar, "salida-variable.txt")
        mascara = variable.parent if variable else donde
        sesion = self.etiqueta(md, resultado, SESION)
        if sesion is not None:
            if sesion:
                self.verificar_sesion(md, i, fichero, proyecto, modulo, buscar, sesion, mascara)
            return
        try:
            codigo, out, err = self.ejecutar(fichero, proyecto, modulo, buscar)
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
        salida = self.etiqueta(md, resultado, SALIDA)
        despues = resultado
        if salida:
            self.v.comparar(md, salida[0], salida[1], out, mascara, f"la salida de {fichero.name}")
            despues = self.siguiente_no_vacia(md, salida[2])
        if con_error:
            error = self.etiqueta(md, despues, SALIDA_DE_ERROR)
            if error:
                self.v.comparar(md, error[0], error[1], err, mascara, f"la salida de error de {fichero.name}")
            elif error is None:
                self.v.informe.error(md.rel, i + 1, f"{fichero.name} lleva termina-con-error.txt: falta "
                                                    f"«{SALIDA_DE_ERROR}» y su bloque")

    def orden(self, fichero, proyecto, modulo, buscar, t):
        """La orden de java (lista) y la carpeta (relativa a la copia) desde la que se ejecuta."""
        argumentos = _primero(buscar, "args.txt")
        opciones = _primero(buscar, OPCIONES_EXTRA)
        extra = shlex.split(argumentos.read_text(encoding="utf-8")) if argumentos else []
        jvm = shlex.split(opciones.read_text(encoding="utf-8")) if opciones else []
        if proyecto:
            return (["java", *OPCIONES_JVM, *jvm, "-cp", proyecto.classpath(modulo), clase_de(fichero), *extra],
                    modulo.relative_to(proyecto.raiz).as_posix())
        return ["java", *OPCIONES_JVM, *jvm, fichero.name, *extra], None

    def _terminal(self, fichero, proyecto):
        """La terminal del programa: la de su proyecto (abierta) o una nueva con su carpeta (sin abrir)."""
        return proyecto.terminal() if proyecto else abrir_terminal(fichero.parent, self.v.con_docker)

    def ejecutar(self, fichero, proyecto, modulo, buscar):
        entrada = _primero(buscar, "entrada.txt")
        datos = entrada.read_bytes() if entrada else b""
        try:
            if proyecto:
                t = proyecto.terminal()
                orden, desde = self.orden(fichero, proyecto, modulo, buscar, t)
                return t.ejecutar(orden, datos, TIEMPO_MAXIMO, desde, entorno_de(t))
            with abrir_terminal(fichero.parent, self.v.con_docker) as t:
                orden, desde = self.orden(fichero, None, None, buscar, t)
                return t.ejecutar(orden, datos, TIEMPO_MAXIMO, desde, entorno_de(t))
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
                codigo, texto, err = self._teclear(t, fichero, proyecto, modulo, buscar, entrada, proyecto.raiz)
            else:
                with abrir_terminal(fichero.parent, self.v.con_docker) as t:
                    codigo, texto, err = self._teclear(t, fichero, None, None, buscar, entrada, fichero.parent)
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
        orden, desde = self.orden(fichero, proyecto, modulo, buscar, t)
        base = base_de(t)
        ruta = f"{base}/{entrada.relative_to(copia).as_posix()}" if entrada else "-"
        if isinstance(t, terminal.Contenedor):
            teclear = ["python3", f"{EN_LA_IMAGEN}/teclear.py"]
        else:
            teclear = [sys.executable, str(SERVICIOS_JAVA / "teclear.py")]
        return t.ejecutar([*teclear, ruta, str(TIEMPO_MAXIMO), "--", *orden], None, TIEMPO_MAXIMO + 30, desde,
                          entorno_de(t))

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


def teclear_no_termina():
    return 124          # el código con el que termina servicios/java/teclear.py si el programa no termina


def _normalizar(texto):
    return "\n".join(linea.rstrip() for linea in texto.strip("\n").splitlines())


# -- --preparar-java -------------------------------------------------------------------------------------------------

def proyectos_de(carpetas):
    """Los proyectos (tipo, raíz) de las carpetas enlazadas: el de cada carpeta y los que haya dentro, sin repetir."""
    vistos = {}
    for carpeta in sorted(carpetas):
        candidatas = [carpeta] + sorted(p.parent for nombre in ("pom.xml", "build.gradle.kts")
                                        for p in carpeta.rglob(nombre)
                                        if not NO_COPIAR.union({"target", "build"}) & set(p.parts))
        for c in candidatas:
            maven = raiz_maven(c)
            gradle = None if maven else raiz_gradle(c)
            if maven:
                vistos.setdefault(maven[0], "maven")
            elif gradle:
                vistos.setdefault(gradle[0], "gradle")
    return sorted((tipo, raiz) for raiz, tipo in vistos.items())


def preparar(tipo, raiz, con_docker):
    """Construye el proyecto CON RED para llenar la caché (el volumen de Docker o las del equipo): la misma
    construcción que la verificación, más sus pruebas (sin parar si alguna falla a propósito). None si va bien, o
    el error."""
    if tipo == "maven":
        metas = ["package", "dependency:build-classpath", "-Dmdep.outputFile=${project.build.directory}/classpath.txt",
                 "-Dmaven.test.failure.ignore=true"]
    else:
        metas = ["build", "printRuntimeClasspath", "--continue"]
    if con_docker:
        try:
            with abrir_terminal(raiz, True, red=True) as t:
                if tipo == "maven":
                    orden = ["mvn", "-B", "-q", *metas]
                else:
                    orden = ["gradle", "-q", "--console=plain", "--no-configuration-cache", "--init-script",
                             f"{EN_LA_IMAGEN}/classpath.init.gradle.kts", *metas]
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
