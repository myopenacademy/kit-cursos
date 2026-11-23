"""Pruebas de lenguajes/java.py (el ejecutor de Java de verificar_codigo.py) y de --preparar-java, sobre una copia
del curso de ejemplo de Java (pruebas/cursos/java/).

Sin Docker, con el java, mvn y gradle del equipo (se saltan si falta alguno); con Docker, en la imagen de Java del
kit (se saltan sin Docker; la primera vez se construye, unos minutos, con internet). Las de Maven y Gradle
necesitan la caché preparada: se prepara una vez por ejecución de las pruebas y por modo, con
«verificar_codigo.py --preparar-java» (lo único que usa la red). Con Docker, en un volumen solo para las pruebas
(VOLUMEN_PRUEBAS), para que lo que haya preparado otro curso no cambie el resultado; sin Docker, en las cachés del
equipo (~/.m2 y ~/.gradle), como lo haría el autor.

Desde la raíz del kit:
    python3 -m unittest discover -s herramientas/pruebas -p test_java.py -v
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PRUEBAS = Path(__file__).resolve().parent
HERRAMIENTAS = PRUEBAS.parent
for carpeta in ("lenguajes", "servicios", "nucleo"):
    sys.path.insert(0, str(HERRAMIENTAS / carpeta))
import terminal  # noqa: E402
import verificar_codigo  # noqa: E402
try:
    import java as lenguaje_java  # noqa: E402
except ImportError:          # todavía no existe: las pruebas fallan (RED) en vez de no poder cargarse
    lenguaje_java = None

CURSO = PRUEBAS / "cursos" / "java"
BUENO = PRUEBAS / "cursos" / "bueno"
SCRIPT = HERRAMIENTAS / "nucleo" / "verificar_codigo.py"
HAY_DOCKER = terminal.hay_docker()
HAY_JAVA_LOCAL = all(shutil.which(p) for p in ("java", "javac", "mvn", "gradle"))
VOLUMEN_PRUEBAS = "kit-java-cache-pruebas"

PROGRAMAS = "fase-01-java/01-programas.md"
MAVEN = "fase-01-java/02-maven.md"
GRADLE = "fase-01-java/03-gradle.md"
EJEMPLOS = "fase-01-java/codigo/01-programas/ejemplos"
TIENDA = "fase-01-java/codigo/02-maven/ejemplos/2.1-tienda"
INVENTARIO = "fase-01-java/codigo/03-gradle/ejemplos/2.1-inventario"

PREPARADOS = {}         # modo (sin_docker) -> salida de --preparar-java, una vez por ejecución de las pruebas


def entorno():
    return {**os.environ, "KIT_JAVA_CACHE": VOLUMEN_PRUEBAS}


class Unidad(unittest.TestCase):
    """Lo que no ejecuta Java: funciona en cualquier máquina."""

    def setUp(self):
        self.assertIsNotNone(lenguaje_java, "falta lenguajes/java.py")

    def test_registrado_como_ejecutor_con_sus_ficheros_de_verificacion(self):
        self.assertIn((lenguaje_java, "verificar_java"), verificar_codigo.EJECUTORES)
        self.assertTrue(lenguaje_java.es_mio(Path("Hola.java")))
        self.assertFalse(lenguaje_java.es_mio(Path("hola.sh")))
        for nombre in ("opciones-java.txt", "solo-compilar.txt"):
            self.assertTrue(verificar_codigo.es_de_verificacion(nombre), nombre)

    def test_resumen_de_surefire_sin_tiempos_ni_trazas(self):
        salida = "\n".join([
            "[INFO] Scanning for projects...",
            "[INFO] -------------------------------------------------------",
            "[INFO]  T E S T S",
            "[INFO] Running es.tienda.PrecioTest",
            "[ERROR] Tests run: 2, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 0.052 s <<< FAILURE! -- in es.tienda.PrecioTest",
            "[ERROR] es.tienda.PrecioTest.sumaElIva -- Time elapsed: 0.01 s <<< FAILURE!",
            "org.opentest4j.AssertionFailedError: expected: <24.2> but was: <24.21>",
            "\tat org.junit.jupiter.api.AssertionUtils.fail(AssertionUtils.java:158)",
            "\t... 2 more",
            "",
            "[INFO] ",
            "[INFO] Results:",
            "[ERROR] Failures: ",
            "[ERROR]   PrecioTest.sumaElIva:12 expected: <24.2> but was: <24.21>",
            "[ERROR] Tests run: 2, Failures: 1, Errors: 0, Skipped: 0",
            "[INFO] BUILD FAILURE",
        ])
        self.assertEqual(lenguaje_java.resumen_pruebas(salida), "\n".join([
            "[INFO] Running es.tienda.PrecioTest",
            "[ERROR] Tests run: 2, Failures: 1, Errors: 0, Skipped: 0 <<< FAILURE! -- in es.tienda.PrecioTest",
            "[ERROR] es.tienda.PrecioTest.sumaElIva <<< FAILURE!",
            "org.opentest4j.AssertionFailedError: expected: <24.2> but was: <24.21>",
            "[ERROR] Tests run: 2, Failures: 1, Errors: 0, Skipped: 0",
        ]))
        self.assertIsNone(lenguaje_java.resumen_pruebas("[ERROR] COMPILATION ERROR"))

    def test_raiz_de_maven_y_de_gradle(self):
        carpeta = CURSO / TIENDA / "src/main/java/es/tienda"
        self.assertEqual(lenguaje_java.raiz_maven(carpeta), (CURSO / TIENDA, CURSO / TIENDA))
        self.assertIsNone(lenguaje_java.raiz_gradle(carpeta))
        self.assertEqual(lenguaje_java.raiz_gradle(CURSO / INVENTARIO / "src/main/java/es/inventario"),
                         (CURSO / INVENTARIO, CURSO / INVENTARIO))
        self.assertIsNone(lenguaje_java.raiz_maven(CURSO / EJEMPLOS / "2.1-saludo"))

    def test_preparar_sin_proyectos(self):
        tmp = Path(tempfile.mkdtemp(prefix="test-java-"))
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(BUENO, tmp / "curso")
        r = subprocess.run([sys.executable, str(SCRIPT), "--preparar-java", "--sin-docker"], capture_output=True,
                           text=True, cwd=tmp / "curso", env=entorno(), timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("No hay proyectos de Maven ni de Gradle en las carpetas enlazadas: no hay nada que preparar.",
                      r.stdout)

    def test_la_ayuda_explica_preparar_java(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertIn("--preparar-java", r.stdout)

    def test_el_curso_de_ejemplo_cumple_el_formato(self):
        r = subprocess.run([sys.executable, str(HERRAMIENTAS / "formato_academia.py"), str(CURSO)],
                           capture_output=True, text=True, cwd=HERRAMIENTAS.parent)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(": 0 errores", r.stdout)


class Base(unittest.TestCase):
    sin_docker = True

    def setUp(self):
        self.assertIsNotNone(lenguaje_java, "falta lenguajes/java.py")
        self.tmp = Path(tempfile.mkdtemp(prefix="test-java-"))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.raiz = self.tmp / "curso"
        shutil.copytree(CURSO, self.raiz)

    def ejecutar(self, *args):
        opciones = ["--sin-docker"] if self.sin_docker else []
        r = subprocess.run([sys.executable, str(SCRIPT), *opciones, *args], capture_output=True, text=True,
                           cwd=self.raiz, env=entorno(), timeout=1800)
        self.salida = r.stdout + r.stderr
        return r.returncode

    def preparar(self):
        """--preparar-java, una vez por modo y ejecución de las pruebas (lo único con red)."""
        if self.sin_docker not in PREPARADOS:
            codigo = self.ejecutar("--preparar-java")
            self.assertEqual(codigo, 0, self.salida)
            PREPARADOS[self.sin_docker] = self.salida
        return PREPARADOS[self.sin_docker]

    def cambiar(self, rel, antes, despues):
        ruta = self.raiz / rel
        texto = ruta.read_text(encoding="utf-8")
        self.assertIn(antes, texto, f"la prueba está mal: no encuentro «{antes}» en {rel}")
        ruta.write_text(texto.replace(antes, despues, 1), encoding="utf-8")

    def linea(self, rel, texto, despues):
        """El número (desde 1) de la primera línea igual a `texto` tras la que contiene `despues`."""
        lineas = (self.raiz / rel).read_text(encoding="utf-8").split("\n")
        inicio = next(i for i, l in enumerate(lineas) if despues in l)
        return next(i for i in range(inicio, len(lineas)) if lineas[i].strip() == texto) + 1

    def enlace(self, rel, carpeta, n=1):
        """La línea del enlace «📁 Código» n.º n (desde 1) a la carpeta."""
        lineas = (self.raiz / rel).read_text(encoding="utf-8").split("\n")
        return [i for i, l in enumerate(lineas) if l.startswith("📁") and f"({carpeta}" in l][n - 1] + 1

    def assertError(self, md, linea, *trozos, args=None):
        self.assertEqual(self.ejecutar(*(args or [md])), 1, self.salida)
        mensajes = re.split(r"\n(?=\S)", self.salida)
        prefijo = f"{md}:{linea}: ERROR: "
        self.assertTrue(any(m.startswith(prefijo) and all(t in m for t in trozos) for m in mensajes),
                        f"no encuentro «{prefijo}…{' … '.join(trozos)}» en:\n{self.salida}")


@unittest.skipUnless(HAY_JAVA_LOCAL, "sin java, javac, mvn o gradle en el PATH")
class ProgramasSinDocker(Base):
    """Los programas de un solo fichero (java Fichero.java), con todos sus ficheros de verificación."""

    def test_el_modulo_pasa(self):
        self.assertEqual(self.ejecutar(PROGRAMAS), 0, self.salida)
        self.assertIn("7 programas de Java", self.salida)
        if self.sin_docker:
            self.assertIn("Sin Docker: verificación parcial", self.salida)
            self.assertIn("el JDK, Maven y Gradle del equipo", self.salida)
        else:
            self.assertIn("verificación completa", self.salida)

    def test_args(self):
        (self.raiz / EJEMPLOS / "2.1-saludo/args.txt").write_text("Luis\n", encoding="utf-8")
        self.assertError(PROGRAMAS, self.linea(PROGRAMAS, "**Salida:**", "2.1. Un saludo"),
                         "la salida de Saludo.java no es la del texto", "'Hola, Luis.'")

    def test_sesion_en_la_terminal_con_entrada(self):
        (self.raiz / EJEMPLOS / "2.2-preguntar/entrada.txt").write_text("Luis\n7\n", encoding="utf-8")
        self.assertError(PROGRAMAS, self.linea(PROGRAMAS, "**Sesión en la terminal:**", "2.2. Preguntar"),
                         "la sesión en la terminal de Preguntar.java no es la del texto", "'¿Cómo te llamas? Luis'")

    def test_opciones_java(self):
        (self.raiz / EJEMPLOS / "2.3-opciones/opciones-java.txt").unlink()
        self.assertError(PROGRAMAS, self.linea(PROGRAMAS, "**Salida:**", "2.3. Una opción"),
                         "la salida de Propiedad.java no es la del texto", "'Tienda: null'")

    def test_termina_con_error_sin_su_fichero(self):
        (self.raiz / EJEMPLOS / "2.4-error/termina-con-error.txt").unlink()
        self.assertError(PROGRAMAS, self.enlace(PROGRAMAS, "codigo/01-programas/ejemplos/2.4-error/"),
                         f"{EJEMPLOS}/2.4-error/Media.java termina con el código 1",
                         "Error: no hay notas para hacer la media.")

    def test_salida_de_error_distinta(self):
        self.cambiar(PROGRAMAS, "Error: no hay notas para hacer la media.\n```", "Error: no hay datos.\n```")
        self.assertError(PROGRAMAS, self.linea(PROGRAMAS, "**Salida de error:**", "2.4. Un programa"),
                         "la salida de error de Media.java no es la del texto")

    def test_termina_bien_con_termina_con_error(self):
        (self.raiz / EJEMPLOS / "2.1-saludo/termina-con-error.txt").write_text("x\n", encoding="utf-8")
        self.assertError(PROGRAMAS, self.enlace(PROGRAMAS, "codigo/01-programas/ejemplos/2.1-saludo/"),
                         f"{EJEMPLOS}/2.1-saludo/Saludo.java lleva termina-con-error.txt pero termina bien (código 0)")

    def test_salida_variable(self):
        (self.raiz / EJEMPLOS / "2.5-hora/salida-variable.txt").unlink()
        self.assertError(PROGRAMAS, self.linea(PROGRAMAS, "**Salida:**", "2.5. La hora"),
                         "la salida de Hora.java no es la del texto")

    def test_solo_compilar_que_no_compila(self):
        for rel in (f"{EJEMPLOS}/2.6-ventana/Aviso.java", PROGRAMAS):
            self.cambiar(rel, '"Tu pedido está en camino.");', '"Tu pedido está en camino.")')
        self.assertError(PROGRAMAS, self.enlace(PROGRAMAS, "codigo/01-programas/ejemplos/2.6-ventana/"),
                         "Aviso.java no compila", "Aviso.java:5: error: ';' expected")

    def test_solo_compilar_no_lo_ejecuta(self):
        # Sin solo-compilar.txt se ejecutaría, y sin pantalla JOptionPane falla (HeadlessException)
        (self.raiz / EJEMPLOS / "2.6-ventana/solo-compilar.txt").unlink()
        self.assertError(PROGRAMAS, self.enlace(PROGRAMAS, "codigo/01-programas/ejemplos/2.6-ventana/"),
                         "Aviso.java termina con el código 1", "HeadlessException")


@unittest.skipUnless(HAY_DOCKER, "sin Docker")
class ProgramasConDocker(ProgramasSinDocker):
    sin_docker = False


@unittest.skipUnless(HAY_JAVA_LOCAL, "sin java, javac, mvn o gradle en el PATH")
class MavenSinDocker(Base):
    """Un proyecto de Maven: se construye una vez, el programa se ejecuta con su classpath y JUnit con Surefire."""

    def setUp(self):
        super().setUp()
        self.preparar()

    def test_el_modulo_pasa(self):
        self.assertEqual(self.ejecutar(MAVEN), 0, self.salida)
        self.assertIn("2 programas de Java", self.salida)       # el programa y la clase de pruebas

    def test_preparar_dice_lo_que_prepara(self):
        self.assertIn(f"✅ Preparado (Maven): {TIENDA}/", self.preparar())
        self.assertIn(f"✅ Preparado (Gradle): {INVENTARIO}/", self.preparar())

    def test_salida_distinta(self):
        self.cambiar(MAVEN, "cuesta 24,20 € con IVA.\n```", "cuesta 24,21 € con IVA.\n```")
        self.assertError(MAVEN, self.linea(MAVEN, "**Salida:**", "Y el programa que lo usa"),
                         "la salida de App.java no es la del texto")

    def test_salida_de_las_pruebas_distinta(self):
        self.cambiar(MAVEN, "[INFO] Tests run: 2, Failures: 0, Errors: 0, Skipped: 0\n```",
                     "[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0\n```")
        self.assertError(MAVEN, self.linea(MAVEN, "**Salida de las pruebas:**", "Sus pruebas"),
                         "la salida de las pruebas de PrecioTest.java no es la del texto")

    def test_una_prueba_que_falla_se_ve_en_el_resumen(self):
        for rel in (f"{TIENDA}/src/test/java/es/tienda/PrecioTest.java", MAVEN):
            self.cambiar(rel, "assertEquals(24.2, ", "assertEquals(24.3, ")
        self.assertError(MAVEN, self.enlace(MAVEN, "codigo/02-maven/ejemplos/2.1-tienda/src/main", 2),
                         "mvn package falla en 2.1-tienda")
        self.assertIn("la salida de las pruebas de PrecioTest.java no es la del texto", self.salida)
        self.assertIn("Tests run: 2, Failures: 1", self.salida)

    def test_no_compila(self):
        for rel in (f"{TIENDA}/src/main/java/es/tienda/Precio.java", MAVEN):
            self.cambiar(rel, "return Math.round(precio * 1.21 * 100) / 100.0;", "return Math.round(precio * 1.21 * 100) / 100.0")
        self.assertError(MAVEN, self.enlace(MAVEN, "codigo/02-maven/ejemplos/2.1-tienda/src/main", 2),
                         "mvn package falla en 2.1-tienda", "Precio.java:[5,55] ';' expected")

    def test_dependencia_que_no_esta_en_la_cache(self):
        # Sin red, lo que no ha preparado --preparar-java no se puede descargar
        dependencia = ("        <dependency>\n            <groupId>org.apache.commons</groupId>\n"
                       "            <artifactId>commons-lang3</artifactId>\n            <version>3.22.0</version>\n"
                       "        </dependency>\n        <dependency>\n            <groupId>org.junit.jupiter</groupId>")
        if self.sin_docker:     # en el equipo puede estar en ~/.m2: una que no existe en ninguna parte
            dependencia = dependencia.replace("org.apache.commons", "es.ejemplo.kit").replace("commons-lang3", "no-esta-en-la-cache")
        for rel in (f"{TIENDA}/pom.xml", MAVEN):
            self.cambiar(rel, "        <dependency>\n            <groupId>org.junit.jupiter</groupId>", dependencia)
        self.assertError(MAVEN, self.enlace(MAVEN, "codigo/02-maven/ejemplos/2.1-tienda/src/main", 2),
                         "faltan dependencias en la caché de Maven",
                         "ejecuta antes «verificar_codigo.py --preparar-java»")


@unittest.skipUnless(HAY_DOCKER, "sin Docker")
class MavenConDocker(MavenSinDocker):
    sin_docker = False


@unittest.skipUnless(HAY_JAVA_LOCAL, "sin java, javac, mvn o gradle en el PATH")
class GradleSinDocker(Base):
    def setUp(self):
        super().setUp()
        self.preparar()

    def test_el_modulo_pasa(self):
        self.assertEqual(self.ejecutar(GRADLE), 0, self.salida)
        self.assertIn("1 programas de Java", self.salida)

    def test_salida_distinta(self):
        self.cambiar(GRADLE, "Hay 3 productos: Lápiz, Cuaderno, Goma.\n```", "Hay 3 productos: Lápiz, Goma.\n```")
        self.assertError(GRADLE, self.linea(GRADLE, "**Salida:**", "2.1. Un inventario"),
                         "la salida de Main.java no es la del texto")

    def test_no_compila(self):
        for rel in (f"{INVENTARIO}/src/main/java/es/inventario/Main.java", GRADLE):
            self.cambiar(rel, 'List.of("Lápiz", "Cuaderno", "Goma");', 'List.of("Lápiz", "Cuaderno", "Goma")')
        self.assertError(GRADLE, self.enlace(GRADLE, "codigo/03-gradle/ejemplos/2.1-inventario/src/main"),
                         "gradle build falla en 2.1-inventario")

    def test_dependencia_que_no_esta_en_la_cache(self):
        dependencia = 'implementation("org.apache.commons:commons-lang3:3.22.0")\n    testImplementation("org.junit'
        if self.sin_docker:
            dependencia = dependencia.replace("org.apache.commons:commons-lang3", "es.ejemplo.kit:no-esta-en-la-cache")
        for rel in (f"{INVENTARIO}/build.gradle.kts", GRADLE):
            self.cambiar(rel, 'testImplementation("org.junit', dependencia)
        self.assertError(GRADLE, self.enlace(GRADLE, "codigo/03-gradle/ejemplos/2.1-inventario/src/main"),
                         "faltan dependencias en la caché de Gradle",
                         "ejecuta antes «verificar_codigo.py --preparar-java»")


@unittest.skipUnless(HAY_DOCKER, "sin Docker")
class GradleConDocker(GradleSinDocker):
    sin_docker = False


@unittest.skipUnless(HAY_DOCKER, "sin Docker")
class SinRed(unittest.TestCase):
    def test_la_imagen_de_java_verifica_sin_red(self):
        with terminal.Contenedor(CURSO / EJEMPLOS / "2.1-saludo", imagen=terminal.imagen_java()) as t:
            codigo, _, err = t.ejecutar(["curl", "-sS", "-m", "5", "https://repo.maven.apache.org/maven2/"])
        self.assertNotEqual(codigo, 0)
        self.assertIn("Could not resolve host", err)


if __name__ == "__main__":
    unittest.main()
