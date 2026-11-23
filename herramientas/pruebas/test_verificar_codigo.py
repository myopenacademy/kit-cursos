"""Pruebas de nucleo/verificar_codigo.py y lenguajes/bash.py, sobre una copia del curso de ejemplo bueno.

Las que ejecutan con Docker (la verificación completa, con bash 3.2) se saltan si no hay Docker; la primera vez
se construye la imagen de la terminal del kit (unos minutos, con internet).

Desde la raíz del kit:
    python3 -m unittest discover -s herramientas/pruebas -v
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PRUEBAS = Path(__file__).resolve().parent
HERRAMIENTAS = PRUEBAS.parent
sys.path.insert(0, str(HERRAMIENTAS / "lenguajes"))
sys.path.insert(0, str(HERRAMIENTAS / "servicios"))
import bash  # noqa: E402
sys.path.insert(0, str(HERRAMIENTAS / "nucleo"))
import verificar_codigo  # noqa: E402
import terminal  # noqa: E402
import servidor_http  # noqa: E402

BUENO = PRUEBAS / "cursos" / "bueno"
SCRIPT = HERRAMIENTAS / "nucleo" / "verificar_codigo.py"
MODULO = "fase-01-primeros-pasos/01-ficheros-json.md"
EJEMPLOS = "fase-01-primeros-pasos/codigo/01-ficheros-json/ejemplos"
CONTAR = f"{EJEMPLOS}/2.2-contar-clientes/contar.sh"
HAY_DOCKER = terminal.hay_docker()
API = f"{EJEMPLOS}/2.4-preguntar-a-una-api"     # el ejemplo con servidor.json (puerto 8080)


def puerto_libre():
    """Un puerto que no usa nadie en este momento, elegido por el sistema (se escucha en el 0 y se suelta), para
    que las pruebas no dependan de que el 8080 del equipo esté libre. Se escucha como servidor_http (en «::»,
    también IPv4) para que esté libre en las dos."""
    import socket
    try:
        s = socket.socket(socket.AF_INET6)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        s.bind(("::", 0))
    except OSError:
        s = socket.socket(socket.AF_INET)
        s.bind(("127.0.0.1", 0))
    with s:
        return s.getsockname()[1]


class Bash32(unittest.TestCase):
    def que(self, texto):
        return [q for _, q in bash.incompatibilidades_3_2(texto)]

    def test_detecta_lo_que_no_existe_en_bash_3_2(self):
        casos = {
            "declare -A precios": "arrays asociativos",
            "mapfile -t lineas < f.txt": "mapfile",
            'echo "${nombre,,}"': "mayúsculas",
            'echo "${nombre^^}"': "mayúsculas",
            "ls |& grep x": "|&",
            "orden &>> registro.log": "&>>",
            "[[ -v HOME ]] && echo si": "-v",
            'echo "${lista[-1]}"': "negativos",
            "for i in {1..10..2}; do :; done": "paso",
            "shopt -s globstar": "shopt",
        }
        for linea, trozo in casos.items():
            with self.subTest(linea=linea):
                self.assertTrue(any(trozo in q for q in self.que(linea)), self.que(linea))

    def test_no_avisa_de_lo_que_si_existe(self):
        texto = '\n'.join(['#!/bin/bash', 'nombres=(ana luis)', 'echo "${nombres[0]}" "${#nombres[@]}"',
                           'for i in {1..5}; do echo "$i"; done', 'resultado=$(ls 2>&1 | wc -l)',
                           '[[ -f datos.txt ]] && echo hay', "echo '${no,,} es texto'", '# declare -A en un comentario',
                           'case "$x" in a) echo a;; esac', 'echo "${nombre:-nadie}" "${ruta%/*}"'])
        self.assertEqual(bash.incompatibilidades_3_2(texto), [])

    def test_dice_la_linea(self):
        self.assertEqual(bash.incompatibilidades_3_2("echo hola\nmapfile x\n")[0][0], 2)


class Pantalla(unittest.TestCase):
    def test_tabuladores_hasta_la_siguiente_columna_de_8(self):
        self.assertEqual(terminal.pantalla("ab\tc\r\n12345678\tx"), ["ab      c", "12345678        x"])

    def test_interpreta_retornos_borrados_y_colores(self):
        self.assertEqual(terminal.pantalla("hola\rHO\r\n\x1b[31mrojo\x1b[0m\r\nabc\x08\x08X\x1b[K"), ["HOla", "rojo", "aX"])


class Base(unittest.TestCase):
    sin_docker = False

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="verificar-codigo-"))
        self.raiz = self.tmp / "curso-ejemplo"
        shutil.copytree(BUENO, self.raiz)
        # En la copia, el ejemplo del servidor HTTP escucha en un puerto libre y no en el 8080 (el curso de
        # ejemplo no se toca: la academia lo fija por su commit)
        self.puerto = puerto_libre()
        self.cambiar(f"{API}/servidor.json", '"puerto": 8080', f'"puerto": {self.puerto}')
        for rel in (f"{API}/sesion.txt", MODULO):
            self.cambiar(rel, "localhost:8080/", f"localhost:{self.puerto}/")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def cambiar(self, rel, antes, despues):
        ruta = self.raiz / rel
        texto = ruta.read_text(encoding="utf-8")
        self.assertIn(antes, texto, f"la prueba está mal: no encuentro «{antes}» en {rel}")
        ruta.write_text(texto.replace(antes, despues), encoding="utf-8")

    def ejecutar(self, *args):
        opciones = ["--sin-docker"] if self.sin_docker else []
        r = subprocess.run([sys.executable, str(SCRIPT), *opciones, *args], capture_output=True, text=True,
                           cwd=self.raiz, timeout=900)
        self.salida = r.stdout + r.stderr
        return r.returncode

    def assertError(self, *trozos):
        self.assertEqual(self.ejecutar(), 1, self.salida)
        self.assertTrue(any(all(t in l for t in trozos) for l in re.split(r"\n(?=\S)", self.salida)), self.salida)


class SinDocker(Base):
    """La verificación parcial, con la bash del equipo: funciona en cualquier máquina con bash."""
    sin_docker = True

    def test_el_curso_bueno_pasa_y_avisa_de_que_es_parcial(self):
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertIn("1 scripts ejecutados, 2 sesiones", self.salida)
        self.assertIn("Sin Docker: verificación parcial", self.salida)

    def test_bloque_distinto_de_su_fichero(self):
        self.cambiar(MODULO, 'echo "Clientes de $ciudad: $total"', 'echo "Clientes: $total"')
        self.assertError(MODULO, "no es igual a ningún fichero", "contar.sh")

    def test_salida_distinta(self):
        self.cambiar(MODULO, "Clientes de Madrid: 2", "Clientes de Madrid: 3")
        self.assertError(MODULO, "la salida de contar.sh no es la del texto")

    def test_salida_variable(self):
        self.cambiar(MODULO, "Clientes de Madrid: 2", "Clientes de Madrid: 7")
        (self.raiz / f"{EJEMPLOS}/2.2-contar-clientes/salida-variable.txt").write_text("# el número\n\\d+\n", encoding="utf-8")
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_script_que_falla_sin_termina_con_error(self):
        self.cambiar(CONTAR, 'echo "Clientes', 'exit 3\necho "Clientes')
        self.cambiar(MODULO, 'echo "Clientes', 'exit 3\necho "Clientes')
        self.assertError(MODULO, "termina con el código 3")

    def test_termina_con_error_y_su_salida_de_error(self):
        self.cambiar(CONTAR, 'echo "Clientes de $ciudad: $total"', 'echo "Clientes de $ciudad: $total"\necho "Falta la ciudad" >&2\nexit 1')
        self.cambiar(MODULO, 'echo "Clientes de $ciudad: $total"', 'echo "Clientes de $ciudad: $total"\necho "Falta la ciudad" >&2\nexit 1')
        (self.raiz / f"{EJEMPLOS}/2.2-contar-clientes/termina-con-error.txt").write_text("Enseña un error.\n", encoding="utf-8")
        self.cambiar(MODULO, "Clientes de Madrid: 2\n```\n", "Clientes de Madrid: 2\n```\n\n**Salida de error:**\n\n```text\nFalta la ciudad\n```\n")
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.cambiar(MODULO, "Falta la ciudad\n```", "Falta el cliente\n```")
        self.assertError(MODULO, "la salida de error de contar.sh no es la del texto")

    def test_termina_con_error_sin_salida_de_error(self):
        (self.raiz / f"{EJEMPLOS}/2.2-contar-clientes/termina-con-error.txt").write_text("x\n", encoding="utf-8")
        self.assertError(MODULO, "falta «**Salida de error:**»")

    def test_sesion_distinta(self):
        self.cambiar(MODULO, "$ cat cliente.json\n", "$ cat clientes.json\n")
        self.assertError(MODULO, "la pantalla de sesion.txt no es la del texto")

    def test_lo_que_no_existe_en_bash_3_2(self):
        self.cambiar(CONTAR, 'ciudad="$1"', 'declare -A ciudades\nciudad="$1"')
        self.cambiar(MODULO, 'ciudad="$1"', 'declare -A ciudades\nciudad="$1"')
        self.assertError(CONTAR, "no existe en bash 3.2", "arrays asociativos")

    def test_carpeta_sin_enlazar(self):
        (self.raiz / f"{EJEMPLOS}/2.9-suelto").mkdir()
        (self.raiz / f"{EJEMPLOS}/2.9-suelto/a.json").write_text("{}\n", encoding="utf-8")
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertIn("2.9-suelto/: AVISO: carpeta de código que ningún módulo enlaza", self.salida)

    def test_fichero_que_git_ignora(self):
        subprocess.run(["git", "init", "-q"], cwd=self.raiz, check=True)
        (self.raiz / ".gitignore").write_text("*.json\n", encoding="utf-8")
        self.assertError("clientes.json", "Git lo ignora")

    def test_un_solo_modulo(self):
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)
        self.assertIn("1 ficheros revisados", self.salida)

    def test_argumentos_mal(self):
        self.assertEqual(self.ejecutar("no-existe.md"), 2)

    def test_script_que_deja_algo_creado(self):
        # crea una copia de seguridad y falla si ya existe: bash 3.2 se ejecuta en una carpeta limpia
        orden = 'echo "Clientes de $ciudad: $total"'
        nuevo = orden + '\nif [ -e copia.json ]; then echo "ya hay copia" >&2; exit 1; fi\ncp clientes.json copia.json'
        self.cambiar(CONTAR, orden, nuevo)
        self.cambiar(MODULO, orden, nuevo)
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_user_en_los_scripts(self):
        orden = 'echo "Clientes de $ciudad: $total"'
        nuevo = orden + '\necho "Lo ha contado $USER"'
        self.cambiar(CONTAR, orden, nuevo)
        self.cambiar(MODULO, orden, nuevo)
        self.cambiar(MODULO, "Clientes de Madrid: 2\n", "Clientes de Madrid: 2\nLo ha contado alumno\n")
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_reloj_de_git_tambien_sin_docker(self):
        with terminal.Local(self.raiz / f"{EJEMPLOS}/2.3-ver-un-fichero") as t:
            pantalla = t.sesion([(o, None) for o in ["git init -q", "git add cliente.json", 'git commit -q -m "Uno"',
                                                     "echo x > b.txt", "git add b.txt", 'git commit -q -m "Dos"',
                                                     "git -c core.pager=cat log --format='%s %ad' --date=format:%H:%M"]])
        self.assertIn("Dos 10:01", pantalla)
        self.assertIn("Uno 10:00", pantalla)


class Encadenadas(Base):
    """Las sesiones encadenadas (sesion-1.txt, sesion-2.txt…): en orden, en la misma terminal, cada una en una bash
    nueva. Sin Docker (ConDockerEncadenadas repite las mismas pruebas con Docker)."""
    sin_docker = True
    CARPETA = f"{EJEMPLOS}/2.5-copias"
    ENLACE = "📁 **Código:** [`codigo/01-ficheros-json/ejemplos/2.5-copias/`](codigo/01-ficheros-json/ejemplos/2.5-copias/)"
    SERIE = [("mkdir copias\ncp notas.txt copias/\n", "$ mkdir copias\n$ cp notas.txt copias/\n"),
             ("ls\nls copias\n", "$ ls\ncopias  notas.txt\n$ ls copias\nnotas.txt\n"),
             ("rm -r copias\nls\n", "$ rm -r copias\n$ ls\nnotas.txt\n")]

    def serie(self, sesiones, bloques=None):
        """Escribe la carpeta con sus sesiones [(órdenes, pantalla)] y un bloque por sesión al final del módulo
        (solo las de `bloques`, si se dice)."""
        carpeta = self.raiz / self.CARPETA
        carpeta.mkdir()
        (carpeta / "notas.txt").write_text("comprar pan\n", encoding="utf-8")
        texto = ""
        for n, (ordenes, pantalla) in enumerate(sesiones, 1):
            (carpeta / f"sesion-{n}.txt").write_text(ordenes, encoding="utf-8")
            if bloques is None or n in bloques:
                texto += f"\n**En tu terminal** (`sesion-{n}.txt`):\n\n```text\n{pantalla}```\n\n{self.ENLACE}\n"
        with open(self.raiz / MODULO, "a", encoding="utf-8") as f:
            f.write(texto)

    def verificar_dentro(self):
        """verificar_codigo.verificar en este proceso (para poder acortar la espera de una orden que no termina)."""
        import contextlib, io, os
        salida, antes = io.StringIO(), os.getcwd()
        os.chdir(self.raiz)
        try:
            with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
                try:
                    verificar_codigo.verificar(Path("."), [], {"--sin-docker"} if self.sin_docker else set())
                    codigo = 0
                except SystemExit as e:
                    codigo = e.code
        finally:
            os.chdir(antes)
        self.salida = salida.getvalue()
        return codigo

    def test_la_serie_pasa_y_cada_una_ve_lo_que_dejo_la_anterior(self):
        self.serie(self.SERIE)
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertIn("5 sesiones", self.salida)

    def test_desde_cero_no_pasaria(self):
        # Lo que hacía antes el kit: la sesión 2, sola, no vería la carpeta copias
        self.serie([("ls\nls copias\n", "$ ls\ncopias  notas.txt\n$ ls copias\nnotas.txt\n")])
        self.assertError(MODULO, "la pantalla de sesion-1.txt no es la del texto")

    def test_cada_sesion_arranca_en_una_bash_nueva_en_la_carpeta_del_ejemplo(self):
        self.serie([("mkdir copias\ncd copias\nNOTA=pan\n", "$ mkdir copias\n$ cd copias\n$ NOTA=pan\n"),
                    ('ls\necho "[$NOTA]"\n', '$ ls\ncopias  notas.txt\n$ echo "[$NOTA]"\n[]\n')])
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_una_sesion_que_depende_de_un_cd_anterior_falla(self):
        self.serie([("mkdir copias\ncd copias\n", "$ mkdir copias\n$ cd copias\n"),
                    ("cp ../notas.txt .\n", "$ cp ../notas.txt .\n")])
        self.assertError(MODULO, "la pantalla de sesion-2.txt no es la del texto")

    def test_un_fallo_en_la_sesion_2_dice_cual_es(self):
        serie = list(self.SERIE)
        serie[1] = (serie[1][0], serie[1][1].replace("copias  notas.txt", "notas.txt"))
        self.serie(serie)
        self.assertEqual(self.ejecutar(), 1, self.salida)
        errores = [l for l in self.salida.splitlines() if "ERROR" in l]
        self.assertEqual(len(errores), 1, self.salida)
        self.assertIn("la pantalla de sesion-2.txt no es la del texto", errores[0])

    def test_una_orden_que_no_termina_en_la_sesion_2_y_las_siguientes(self):
        serie = list(self.SERIE)
        serie[1] = ("ls\nsleep 600\n", "$ ls\ncopias  notas.txt\n$ sleep 600\n")
        self.serie(serie)
        antes, terminal.ESPERA_ORDEN = terminal.ESPERA_ORDEN, 2
        try:
            self.assertEqual(self.verificar_dentro(), 1, self.salida)
        finally:
            terminal.ESPERA_ORDEN = antes
        errores = [l for l in re.split(r"\n(?=\S)", self.salida) if "ERROR" in l]
        self.assertEqual(len(errores), 2, self.salida)
        self.assertIn("la sesión sesion-2.txt: la orden «sleep 600» no termina", errores[0])
        self.assertIn("la sesión sesion-3.txt: no se ha podido teclear: va encadenada detrás de sesion-2.txt, que falla",
                      errores[1])

    def test_el_repositorio_y_el_reloj_de_git_siguen(self):
        log = "git log --format='%ad %s' --date=format:%H:%M"
        self.serie([("git init -q\ngit add notas.txt\ngit commit -q -m Uno\n",
                     "$ git init -q\n$ git add notas.txt\n$ git commit -q -m Uno\n"),
                    (f"echo leche >> notas.txt\ngit commit -q -am Dos\n{log}\n",
                     f"$ echo leche >> notas.txt\n$ git commit -q -am Dos\n$ {log}\n10:01 Dos\n10:00 Uno\n")])
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_numeros_con_saltos(self):
        self.serie(self.SERIE)
        (self.raiz / self.CARPETA / "sesion-2.txt").rename(self.raiz / self.CARPETA / "sesion-4.txt")
        self.assertError(MODULO, "tienen que ir de sesion-1.txt en adelante, sin saltos")

    def test_sesion_encadenada_sin_bloque_avisa_y_se_teclea_igual(self):
        self.serie(self.SERIE, bloques={2, 3})
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertIn("sesion-1.txt: AVISO: sesión encadenada que ningún bloque muestra", self.salida)

    def test_las_sueltas_siguen_desde_cero(self):
        self.serie(self.SERIE)
        (self.raiz / self.CARPETA / "sesion.txt").write_text("ls\n", encoding="utf-8")
        with open(self.raiz / MODULO, "a", encoding="utf-8") as f:
            f.write(f"\n**En tu terminal** (`sesion.txt`):\n\n```text\n$ ls\nnotas.txt\n```\n\n{self.ENLACE}\n")
        self.assertEqual(self.ejecutar(), 0, self.salida)


@unittest.skipUnless(HAY_DOCKER, "sin Docker")
class ConDockerEncadenadas(Encadenadas):
    sin_docker = False


class Datos(Base):
    """JSON, YAML, XML, CSV y Markdown: se comprueban con Python, con o sin Docker."""
    sin_docker = True

    def carpeta(self, nombre, ficheros, mostrar=None):
        """Crea la carpeta en codigo/ con esos ficheros y la enlaza desde el módulo con el bloque de uno de ellos."""
        carpeta = self.raiz / EJEMPLOS / nombre
        carpeta.mkdir()
        for f, texto in ficheros.items():
            (carpeta / f).parent.mkdir(parents=True, exist_ok=True)
            (carpeta / f).write_text(texto, encoding="utf-8")
        mostrar = mostrar or next(f for f in ficheros if not f.endswith(".txt"))
        vallas = "````" if mostrar.endswith(".md") else "```"
        self.cambiar(MODULO, "## 3. Errores típicos",
                     f"### 2.9. Prueba\n\n{vallas}text\n{ficheros[mostrar].rstrip()}\n{vallas}\n\n"
                     f"📁 **Código:** [`codigo/01-ficheros-json/ejemplos/{nombre}/`](codigo/01-ficheros-json/ejemplos/{nombre}/)\n\n"
                     "## 3. Errores típicos")

    def test_json_no_valido_con_su_linea(self):
        self.carpeta("2.9-json", {"pedido.json": '{\n  "id": 1,\n}\n'})
        self.assertError("pedido.json:2:", "JSON no válido")

    def test_debe_fallar_y_falla(self):
        self.carpeta("2.9-json", {"pedido.json": '{"id": 1,}\n', "debe-fallar.txt": "Sobra la coma del final.\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_debe_fallar_pero_es_valido(self):
        self.carpeta("2.9-json", {"pedido.json": '{"id": 1}\n', "debe-fallar.txt": "Sobra la coma.\n"})
        self.assertError("pedido.json", "debe-fallar.txt", "pero es válido")

    def test_yaml_mal_sangrado(self):
        self.carpeta("2.9-yaml", {"tienda.yaml": "tienda:\n  nombre: La Taza\n   ciudad: Madrid\n"})
        self.assertError("tienda.yaml:3:", "YAML no válido")

    def test_xml_mal_formado(self):
        self.carpeta("2.9-xml", {"pedido.xml": "<pedido>\n  <id>1</id>\n  <total>25</totl>\n</pedido>\n"})
        self.assertError("pedido.xml:3:", "XML mal formado")

    def test_csv_con_columnas_de_mas(self):
        self.carpeta("2.9-csv", {"ventas.csv": "fecha,importe\n2026-01-01,10\n2026-01-02,12,50\n"})
        self.assertError("ventas.csv:3:", "la fila tiene 3 columnas y la cabecera 2")

    def test_csv_con_su_separador(self):
        self.carpeta("2.9-csv", {"ventas.csv": "fecha;importe\n2026-01-01;10,50\n", "separador.txt": ";\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_csv_sin_su_separador(self):
        self.carpeta("2.9-csv", {"ventas.csv": "fecha;importe\n2026-01-01;10,50\n"})
        self.assertError("ventas.csv:2:", "la fila tiene 2 columnas y la cabecera 1")

    def test_csv_con_comillas_sin_cerrar(self):
        self.carpeta("2.9-csv", {"clientes.csv": 'nombre,ciudad\n"Ana,Madrid\n'})
        self.assertError("clientes.csv", "CSV mal escrito")

    def test_markdown_con_enlace_roto_tabla_rota_y_bloque_sin_cerrar(self):
        self.carpeta("2.9-md", {"README.md": "# Mi proyecto\n\n[Datos](datos.json) y [arriba](#mi-proyecto)\n\n"
                                              "| A | B |\n|---|---|\n| 1 | 2 | 3 |\n"})
        self.assertError("README.md:3:", "no existe datos.json")
        self.assertError("README.md:7:", "la fila de la tabla tiene 3 columnas y la cabecera 2")

    def test_markdown_bueno(self):
        self.carpeta("2.9-md", {"README.md": "# Mi proyecto\n\nVer [arriba](#mi-proyecto).\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n"
                                              "```bash\nls | wc -l\n```\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    PLANTILLA = ".github/ISSUE_TEMPLATE/error.md"

    def test_cabecera_yaml_de_una_plantilla_de_issue(self):
        self.carpeta("2.9-issue", {self.PLANTILLA: "---\nname: Informe de error\nabout: Algo no funciona\n"
                                                   "title: \"[Error] \"\nlabels: [error]\n---\n\n## Qué pasa\n\n| A | B |\n|---|---|\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_cabecera_yaml_no_valida_con_su_linea(self):
        self.carpeta("2.9-issue", {self.PLANTILLA: "---\nname: Informe de error\n  about: Algo no funciona\n---\n\n## Qué pasa\n"})
        self.assertError(".github/ISSUE_TEMPLATE/error.md:3:", "cabecera YAML no válida")

    def test_cabecera_yaml_sin_cerrar_o_sin_claves(self):
        self.carpeta("2.9-issue", {self.PLANTILLA: "---\nname: Informe de error\n\n## Qué pasa\n"})
        self.assertError("error.md:1:", "no se cierra")
        (self.raiz / EJEMPLOS / "2.9-issue" / self.PLANTILLA).write_text("---\n- error\n---\n", encoding="utf-8")
        self.cambiar(MODULO, "name: Informe de error\n\n## Qué pasa", "- error\n---")
        self.assertError("error.md:1:", "debe tener claves y valores")

    def test_la_cabecera_no_se_lee_como_markdown(self):
        self.carpeta("2.9-issue", {self.PLANTILLA: "---\nname: Informe de error\nabout: \"[x](no-existe.md) | a |\"\n---\n\nTexto.\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_la_terminal_copia_la_carpeta_github(self):
        carpeta = self.raiz / EJEMPLOS / "2.9-issue"
        (carpeta / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
        (carpeta / self.PLANTILLA).write_text("---\nname: Error\nabout: Algo falla\n---\n", encoding="utf-8")
        (carpeta / "sesion.txt").write_text("ls .github/ISSUE_TEMPLATE\nhead -2 .github/ISSUE_TEMPLATE/error.md\n", encoding="utf-8")
        self.cambiar(MODULO, "## 3. Errores típicos",
                     "### 2.9. Prueba\n\n**En tu terminal** (`sesion.txt`):\n\n```text\n$ ls .github/ISSUE_TEMPLATE\nerror.md\n"
                     "$ head -2 .github/ISSUE_TEMPLATE/error.md\n---\nname: Error\n```\n\n"
                     "📁 **Código:** [`codigo/01-ficheros-json/ejemplos/2.9-issue/`](codigo/01-ficheros-json/ejemplos/2.9-issue/)\n\n"
                     "## 3. Errores típicos")
        self.assertEqual(self.ejecutar(), 0, self.salida)

    JEKYLL = ("---\nlayout: default\ntitle: Rutas del club\n---\n\n# {{ page.title }}\n\n| Ruta | Km | Enlace |\n|---|---|---|\n"
              "{% for ruta in site.data.rutas %}| {{ ruta.nombre | upcase }} | {{ ruta.km }} | [Ver]({{ ruta.url | relative_url }}) |\n"
              "{% endfor %}\n\n- [Inicio]({{site.baseurl}}/index.html)\n- [Contacto](contacto.md)\n")

    def test_jekyll_liquid_es_texto(self):
        self.carpeta("2.9-web", {"index.md": self.JEKYLL, "contacto.md": "# Contacto\n",
                                 "_data/rutas.json": '[{"nombre": "La Pedriza", "km": 12, "url": "/pedriza.html"}]\n'},
                     mostrar="index.md")
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_jekyll_sigue_comprobando_tablas_enlaces_y_data(self):
        roto = self.JEKYLL.replace("(contacto.md)", "(no-existe.md)").replace("| {{ ruta.km }} |", "| {{ ruta.km }} | de más |")
        self.carpeta("2.9-web", {"index.md": roto, "_data/rutas.json": '[{"km": 12,}]\n'}, mostrar="index.md")
        self.assertError("2.9-web/index.md:14:", "no existe no-existe.md")
        self.assertError("2.9-web/index.md:10:", "la fila de la tabla tiene 4 columnas y la cabecera 3")
        self.assertError("2.9-web/_data/rutas.json:1:", "JSON no válido")

    def test_conversion_con_los_mismos_datos(self):
        self.carpeta("2.9-conv", {"pedido.json": '{"id": 1, "total": 25.5}\n', "pedido.yaml": "id: 1\ntotal: 25.5\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_conversion_con_otros_datos(self):
        self.carpeta("2.9-conv", {"pedido.json": '{"id": 1, "total": 25.5}\n', "pedido.yaml": "id: 1\ntotal: 25\n"})
        self.assertError("2.9-conv", "no tienen los mismos datos")

    # -- CSV con su JSON (reglas del reto 3 de la fase 4 del curso inicial, FORMATO.md 7.1) -----------------

    CSV = ('pedido,cp,precio,pagado,notas\n'
           'P-1,08012,12.50,sí,"Que ponga ""frágil"""\n'
           'P-2,28004,7,false,\n')
    JSON = [{"pedido": "P-1", "cp": "08012", "precio": 12.5, "pagado": True, "notas": 'Que ponga "frágil"'},
            {"notas": None, "pedido": "P-2", "cp": "28004", "precio": 7.0, "pagado": False}]

    def comparar(self, csv=None, datos=None, extra=None):
        self.carpeta("2.9-tabla", {"pedidos.csv": csv if csv is not None else self.CSV,
                                   "pedidos.json": json.dumps(datos if datos is not None else self.JSON, ensure_ascii=False),
                                   **(extra or {})}, mostrar="pedidos.csv")

    def cambiado(self, fila, clave, valor):
        datos = json.loads(json.dumps(self.JSON))
        datos[fila][clave] = valor
        return datos

    def test_csv_y_json_con_los_mismos_datos(self):
        self.comparar()
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertIn("(1 CSV comparados con su JSON)", self.salida)

    def test_sin_json_no_se_compara(self):
        self.carpeta("2.9-tabla", {"pedidos.csv": self.CSV})
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertNotIn("comparados", self.salida)

    def test_codigo_postal_como_numero(self):
        self.comparar(datos=self.cambiado(0, "cp", 8012))
        self.assertError("pedidos.csv:2:", "fila 1 de datos", "clave «cp»", "no se lee como número")

    def test_numero_con_coma_decimal(self):
        self.comparar(csv=self.CSV.replace("12.50", '"12,50"'))
        self.assertError("pedidos.csv:2:", "clave «precio»", "«12,50»")

    def test_otro_numero(self):
        self.comparar(datos=self.cambiado(1, "precio", 7.01))
        self.assertError("pedidos.csv:3:", "clave «precio»", "es el número 7.01 y en el CSV 7")

    def test_booleano_solo_en_minuscula(self):
        self.comparar(csv=self.CSV.replace(",sí,", ",Sí,"))
        self.assertError("pedidos.csv:2:", "clave «pagado»", "sí, no, true o false")

    def test_booleano_al_reves(self):
        self.comparar(datos=self.cambiado(1, "pagado", True))
        self.assertError("pedidos.csv:3:", "clave «pagado»", "es true y en el CSV «false»")

    def test_texto_igual_exacto(self):
        self.comparar(datos=self.cambiado(0, "cp", "8012"))
        self.assertError("pedidos.csv:2:", "clave «cp»", "texto «8012» y en el CSV «08012»")

    def test_vacio_solo_como_null(self):
        self.comparar(datos=self.cambiado(1, "notas", ""))
        self.assertError("pedidos.csv:3:", "clave «notas»", "solo vale como null")

    def test_null_con_campo_lleno(self):
        self.comparar(datos=self.cambiado(0, "notas", None))
        self.assertError("pedidos.csv:2:", "clave «notas»", "es null")

    def test_lista_en_el_json(self):
        self.comparar(datos=self.cambiado(0, "precio", [12.5]))
        self.assertError("pedidos.csv:2:", "clave «precio»", "es una lista")

    def test_claves_que_faltan_y_sobran(self):
        datos = json.loads(json.dumps(self.JSON))
        datos[1]["nota"] = datos[1].pop("notas")
        self.comparar(datos=datos)
        self.assertError("pedidos.csv:3:", "le falta «notas»")
        self.assertError("pedidos.csv:3:", "le sobra «nota»")

    def test_importa_el_orden_de_las_filas(self):
        self.comparar(datos=list(reversed(self.JSON)))
        self.assertError("pedidos.csv:2:", "clave «pedido»", "«P-2» y en el CSV «P-1»")

    def test_distinto_numero_de_filas(self):
        self.comparar(datos=self.JSON[:1])
        self.assertError("pedidos.csv", "2 filas de datos y pedidos.json, 1 objetos")

    def test_el_json_no_es_una_lista(self):
        self.comparar(datos={"pedidos": self.JSON})
        self.assertError("pedidos.csv", "debe ser una lista", "es un objeto")

    def test_con_su_separador(self):
        self.comparar(csv=self.CSV.replace(",", ";").replace('"Que ponga ""frágil"""', '"Que ponga ""frágil"""'),
                      extra={"separador.txt": ";\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_tsv_con_su_json(self):
        self.carpeta("2.9-tabla", {"pedidos.tsv": self.CSV.replace(",", "\t"),
                                   "pedidos.json": json.dumps(self.JSON, ensure_ascii=False)}, mostrar="pedidos.tsv")
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertIn("(1 CSV comparados con su JSON)", self.salida)

    # -- la codificación de los CSV -------------------------------------------------------------------

    def csv_en_bytes(self, nombre, datos, extra=None):
        self.carpeta(nombre, {"leeme.md": "# Datos\n", **(extra or {})}, mostrar="leeme.md")
        (self.raiz / EJEMPLOS / nombre / "clientes.csv").write_bytes(datos)

    def test_csv_con_bom(self):
        self.csv_en_bytes("2.9-bom", "nombre,ciudad\nLucía,Ávila\n".encode("utf-8-sig"))
        self.assertError("clientes.csv:1:", "BOM")

    def test_csv_en_windows_1252_sin_codificacion(self):
        self.csv_en_bytes("2.9-1252", "nombre,ciudad\nLucía,Ávila\n".encode("cp1252"))
        self.assertError("clientes.csv:2:", "no está en UTF-8", "codificacion.txt")

    def test_csv_en_windows_1252_con_codificacion(self):
        self.csv_en_bytes("2.9-1252", "nombre,ciudad\nLucía,Ávila\n".encode("cp1252"), {"codificacion.txt": "WINDOWS-1252\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_codificacion_que_sobra(self):
        self.csv_en_bytes("2.9-1252", "nombre,ciudad\nLucía,Ávila\n".encode("utf-8"), {"codificacion.txt": "WINDOWS-1252\n"})
        self.assertError("clientes.csv", "está en UTF-8", "sobra el codificacion.txt")

    def test_codificacion_desconocida(self):
        self.csv_en_bytes("2.9-1252", "nombre,ciudad\nLucia,Avila\n".encode("utf-8"), {"codificacion.txt": "MARCIANO\n"})
        self.assertError("clientes.csv", "«MARCIANO»", "no es una codificación conocida")

    # -- TOML, INI y SVG ------------------------------------------------------------------------------

    def test_toml_bueno_y_malo(self):
        self.carpeta("2.9-toml", {"tienda.toml": '[tienda]\nnombre = "La Taza"\npuerto = 8080\n'})
        self.assertEqual(self.ejecutar(), 0, self.salida)
        (self.raiz / EJEMPLOS / "2.9-toml" / "otra.toml").write_text('[tienda]\nnombre = La Taza\n', encoding="utf-8")
        self.assertError("otra.toml:2:", "TOML no válido")

    def test_ini_bueno(self):
        self.carpeta("2.9-ini", {"tienda.ini": "; La tienda\n[tienda]\nnombre = La Taza\nmargen = 20%\n"})
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_ini_con_clave_fuera_de_seccion_y_repetida(self):
        self.carpeta("2.9-ini", {"tienda.ini": "nombre = La Taza\n[tienda]\n"})
        self.assertError("tienda.ini:1:", "antes de la primera sección")
        (self.raiz / EJEMPLOS / "2.9-ini" / "tienda.ini").write_text("[tienda]\nnombre = A\nnombre = B\n", encoding="utf-8")
        self.assertError("tienda.ini:3:", "«nombre» está repetida en la sección [tienda]")

    def test_svg_sin_xmlns(self):
        self.carpeta("2.9-svg", {"logo.svg": '<svg width="10" height="10"><rect width="10" height="10"/></svg>\n'})
        self.assertError("logo.svg:1:", "xmlns")

    def test_svg_bueno_en_una_carpeta_con_debe_fallar(self):
        self.carpeta("2.9-roto", {"README.md": "# Roto\n\n[x](no-existe.md)\n", "debe-fallar.txt": "Enlace roto.\n",
                                  "logo.svg": '<svg xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1"/></svg>\n'},
                     mostrar="README.md")
        self.assertEqual(self.ejecutar(), 0, self.salida)

    def test_debe_fallar_con_solo_imagenes(self):
        self.carpeta("2.9-roto", {"logo.svg": '<svg xmlns="http://www.w3.org/2000/svg"/>\n', "debe-fallar.txt": "x\n"})
        self.assertError("debe-fallar.txt", "sin ficheros de datos")


class ServidorHTTP(unittest.TestCase):
    """servicios/servidor_http.py: el servidor.json y las respuestas, sin arrancar nada."""

    def cargar(self, datos):
        carpeta = Path(tempfile.mkdtemp(prefix="servidor-"))
        self.addCleanup(shutil.rmtree, carpeta)
        fichero = carpeta / "servidor.json"
        fichero.write_text(datos if isinstance(datos, str) else json.dumps(datos, indent=2), encoding="utf-8")
        return servidor_http.cargar(fichero)

    def problemas(self, datos):
        with self.assertRaises(servidor_http.ServidorMal) as e:
            self.cargar(datos)
        return e.exception.problemas

    def test_el_puerto_por_defecto(self):
        self.assertEqual(self.cargar({"rutas": [{"metodo": "GET", "ruta": "/", "estado": 200}]})["puerto"], 8080)

    def test_lo_que_esta_mal_con_su_linea(self):
        casos = [
            ({"rutas": []}, 'falta "rutas"'),
            ({"rutas": [{"metodo": "GET", "ruta": "/", "estado": 200}], "puerto": 80}, "entre 1024 y 65535"),
            ({"rutas": [{"metodo": "GET", "ruta": "/", "estado": 200}], "rutass": 1}, "clave desconocida «rutass»"),
            ({"rutas": [{"metodo": "get", "ruta": "/", "estado": 200}]}, '"metodo" tiene que ser uno de'),
            ({"rutas": [{"metodo": "GET", "ruta": "libros", "estado": 200}]}, "empezar por «/»"),
            ({"rutas": [{"metodo": "GET", "ruta": "/", "estado": 299}]}, "código de estado de HTTP"),
            ({"rutas": [{"metodo": "GET", "ruta": "/", "estado": "200"}]}, "código de estado de HTTP"),
            ({"rutas": [{"metodo": "GET", "ruta": "/"}]}, 'falta "estado"'),
            ({"rutas": [{"metodo": "GET", "ruta": "/", "estado": 200, "cuerpo": 1, "body": 1}]}, "clave desconocida «body»"),
            ({"rutas": [{"metodo": "GET", "ruta": "/", "estado": 200, "cabeceras": {"Content-Length": "3"}}]},
             "Content-Length lo pone el servidor"),
            ({"rutas": [{"metodo": "GET", "ruta": "/", "estado": 200, "cabeceras": {"X-Num": 3}}]}, "tiene que ser un texto"),
        ]
        for datos, trozo in casos:
            with self.subTest(trozo=trozo):
                self.assertTrue(any(trozo in m for _, m in self.problemas(datos)), self.problemas(datos))
        repetida = {"rutas": [{"metodo": "GET", "ruta": "/a", "estado": 200}, {"metodo": "GET", "ruta": "/a", "estado": 404}]}
        self.assertEqual(self.problemas(repetida), [(9, "ruta 2: GET /a repite la ruta 1")])
        self.assertEqual(self.problemas('{"rutas": [\n  {"metodo": "GET",}\n]}')[0][0], 2)    # JSON mal: su línea

    RUTAS = {"rutas": [
        {"metodo": "GET", "ruta": "/libros", "estado": 200, "cuerpo": [{"id": 1, "titulo": "Niebla"}]},
        {"metodo": "GET", "ruta": "/libros?autor=unamuno", "estado": 200, "cuerpo": []},
        {"metodo": "POST", "ruta": "/libros", "estado": 201, "cabeceras": {"Location": "/libros/2"}, "cuerpo": {"id": 2}},
        {"metodo": "GET", "ruta": "/estado", "estado": 200, "cuerpo": "Todo en orden\n"},
        {"metodo": "DELETE", "ruta": "/libros/1", "estado": 204},
        {"metodo": "GET", "ruta": "/xml", "estado": 200, "cabeceras": {"Content-Type": "application/xml"}, "cuerpo": "<a/>\n"},
    ]}

    def responder(self, metodo, objetivo):
        return servidor_http.respuesta(self.cargar(self.RUTAS), metodo, objetivo)

    def test_json_con_sangria_y_salto_final(self):
        estado, cabeceras, cuerpo = self.responder("GET", "/libros")
        self.assertEqual(estado, 200)
        self.assertEqual(cabeceras, [("Content-Type", "application/json"), ("Content-Length", str(len(cuerpo)))])
        self.assertEqual(cuerpo.decode(), '[\n  {\n    "id": 1,\n    "titulo": "Niebla"\n  }\n]\n')

    def test_texto_cabeceras_propias_y_sin_cuerpo(self):
        self.assertEqual(self.responder("GET", "/estado")[1][0], ("Content-Type", "text/plain; charset=utf-8"))
        self.assertEqual(self.responder("GET", "/xml")[1][0], ("Content-Type", "application/xml"))
        self.assertEqual(self.responder("POST", "/libros")[1][:2], [("Content-Type", "application/json"), ("Location", "/libros/2")])
        self.assertEqual(self.responder("DELETE", "/libros/1"), (204, [("Content-Length", "0")], b""))

    def test_consultas(self):
        self.assertEqual(self.responder("GET", "/libros?autor=unamuno")[2], b"[]\n")
        self.assertIn(b"Niebla", self.responder("GET", "/libros?autor=otro")[2])

    def test_head_404_y_405(self):
        self.assertEqual(self.responder("HEAD", "/libros")[0], 200)
        estado, _, cuerpo = self.responder("GET", "/nada")
        self.assertEqual((estado, json.loads(cuerpo)), (404, {"error": "No existe la ruta /nada"}))
        estado, cabeceras, cuerpo = self.responder("PUT", "/libros")
        self.assertEqual((estado, json.loads(cuerpo)), (405, {"error": "La ruta /libros no admite PUT"}))
        self.assertIn(("Allow", "GET, POST, HEAD"), cabeceras)


class Servidor(Base):
    """El servidor HTTP local en las sesiones y los scripts (servidor.json). Sin Docker, en el equipo (en un
    puerto libre, self.puerto); ConDockerServidor repite las mismas pruebas en la terminal del kit."""
    sin_docker = True
    CARPETA = API

    def test_el_ejemplo_pasa_y_el_servidor_json_no_se_copia(self):
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)
        self.assertIn("2 sesiones", self.salida)

    def test_una_respuesta_distinta_falla(self):
        self.cambiar(f"{self.CARPETA}/servidor.json", '"puntos": 120}', '"puntos": 121}')
        self.assertError(MODULO, "la pantalla de sesion.txt no es la del texto")

    def test_un_servidor_json_mal_da_error_con_su_linea(self):
        self.cambiar(f"{self.CARPETA}/servidor.json", '"estado": 200,\n      "cabeceras"', '"estado": 2000,\n      "cabeceras"')
        self.assertError(f"{self.CARPETA}/servidor.json:11:", '"estado" tiene que ser un código de estado de HTTP')
        self.assertIn("el servidor HTTP local no arranca", self.salida)

    def test_un_script_con_curl(self):
        carpeta = self.raiz / self.CARPETA
        script = ('#!/bin/bash\n# Guarda los clientes de la API en un fichero\n'
                  f'curl -s -o clientes.json http://localhost:{self.puerto}/clientes\ngrep -c nombre clientes.json\n')
        (carpeta / "guardar.sh").write_text(script, encoding="utf-8")
        self.cambiar(MODULO, "$ ls\nclientes.json\n", "$ ls\nclientes.json  guardar.sh\n")   # la sesión también lo ve
        enlace = f"📁 **Código:** [`{self.CARPETA[len('fase-01-primeros-pasos/'):]}/`]({self.CARPETA[len('fase-01-primeros-pasos/'):]}/)"
        with open(self.raiz / MODULO, "a", encoding="utf-8") as f:
            f.write(f"\n```bash\n{script}```\n\n{enlace}\n\n**Salida:**\n\n```text\n2\n```\n")
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)
        self.assertIn("2 scripts ejecutados", self.salida)

    def test_en_una_serie_el_servidor_sigue(self):
        carpeta = self.raiz / self.CARPETA
        (carpeta / "sesion.txt").rename(carpeta / "sesion-1.txt")
        (carpeta / "sesion-2.txt").write_text(f"curl -s localhost:{self.puerto}/clientes/1\n", encoding="utf-8")
        self.cambiar(MODULO, "(`sesion.txt`):\n\n```text\n$ curl -i", "(`sesion-1.txt`):\n\n```text\n$ curl -i")
        enlace = "📁 **Código:** [`codigo/01-ficheros-json/ejemplos/2.4-preguntar-a-una-api/`](codigo/01-ficheros-json/ejemplos/2.4-preguntar-a-una-api/)"
        with open(self.raiz / MODULO, "a", encoding="utf-8") as f:
            f.write(f'\n**En tu terminal** (`sesion-2.txt`):\n\n```text\n$ curl -s localhost:{self.puerto}/clientes/1\n'
                    f'{{\n  "nombre": "Ana",\n  "puntos": 120\n}}\n```\n\n{enlace}\n')
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)

    def test_el_puerto_ocupado(self):
        """Se ocupa a propósito el puerto del servidor.json (el libre de la copia)."""
        import socket
        with socket.socket(socket.AF_INET6) as ocupado:
            ocupado.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            try:
                ocupado.bind(("::", self.puerto))
            except OSError:
                self.skipTest(f"el puerto {self.puerto} lo ha ocupado otro programa entre medias")
            ocupado.listen()
            self.assertError(MODULO, "el servidor HTTP local no arranca", f"el puerto {self.puerto} ya está en uso")


@unittest.skipUnless(HAY_DOCKER, "sin Docker")
class ConDockerServidor(Servidor):
    sin_docker = False

    def test_el_puerto_ocupado(self):
        self.skipTest("con Docker, el puerto es el del contenedor: no lo ocupa nada del equipo")

    def test_puerto_en_uso_dentro_de_la_sesion(self):
        with terminal.Contenedor(self.raiz / self.CARPETA) as t:
            pantalla = t.sesion([(f"python3 -m http.server {self.puerto} 2>&1 | tail -1", None), ("ps -eo user,args | grep -c servidor_htt[p]", None)])
        self.assertIn("Address already in use", pantalla)
        self.assertIn("\n1\n", pantalla)


@unittest.skipUnless(HAY_DOCKER, "hace falta Docker")
class Commit(Base):
    """--commit: se verifica la versión de Git en una copia como la de un clon, no el disco."""
    sin_docker = True

    def git(self, *args, carpeta=None):
        return subprocess.run(["git", "-C", str(carpeta or self.raiz), *args], check=True, capture_output=True, text=True,
                              env={"GIT_AUTHOR_NAME": "Prueba", "GIT_AUTHOR_EMAIL": "p@ejemplo.org",
                                   "GIT_COMMITTER_NAME": "Prueba", "GIT_COMMITTER_EMAIL": "p@ejemplo.org",
                                   "HOME": str(self.tmp), "PATH": "/usr/bin:/bin"}).stdout

    def commit(self, mensaje="curso", carpeta=None):
        if not ((carpeta or self.raiz) / ".git").exists():
            self.git("init", "-q", "-b", "main", carpeta=carpeta)
        self.git("add", "-A", carpeta=carpeta)
        self.git("commit", "-q", "-m", mensaje, carpeta=carpeta)

    def test_opcion_commit(self):
        existe = {"fase-01"}.__contains__
        casos = {
            ("--commit",): ("HEAD", []),
            ("--commit", "v1.0.0"): ("v1.0.0", []),
            ("--commit=v1.0.0", "fase-01"): ("v1.0.0", ["fase-01"]),
            ("--commit", "fase-01"): ("HEAD", ["fase-01"]),            # una ruta que existe no es la referencia
            ("--commit", "--sin-docker"): ("HEAD", ["--sin-docker"]),
            ("fase-01",): (None, ["fase-01"]),
        }
        for argumentos, esperado in casos.items():
            with self.subTest(argumentos=argumentos):
                self.assertEqual(verificar_codigo.opcion_commit(list(argumentos), existe), esperado)

    def test_verifica_el_commit_y_no_el_disco(self):
        self.commit()
        self.cambiar(MODULO, "Clientes de Madrid: 2", "Clientes de Madrid: 3")     # roto en el disco, sin commit
        self.assertEqual(self.ejecutar(), 1, self.salida)
        self.assertEqual(self.ejecutar("--commit"), 0, self.salida)
        self.assertIn("Se verifica el commit", self.salida)
        self.assertIn("1 cambio(s) sin commit", self.salida)

    def test_una_referencia_anterior(self):
        self.commit("bueno")
        self.git("tag", "v1.0.0")
        self.cambiar(MODULO, "Clientes de Madrid: 2", "Clientes de Madrid: 3")
        self.commit("roto")
        self.assertEqual(self.ejecutar("--commit"), 1, self.salida)
        self.assertIn("la salida de contar.sh no es la del texto", self.salida)
        self.assertEqual(self.ejecutar("--commit", "v1.0.0"), 0, self.salida)
        self.assertIn("v1.0.0, ", self.salida)
        self.assertNotIn("sin commit", self.salida)

    def test_con_una_carpeta(self):
        self.commit()
        self.assertEqual(self.ejecutar("--commit", "fase-01-primeros-pasos"), 0, self.salida)
        self.assertIn("1 scripts ejecutados", self.salida)

    def test_lo_que_no_tiene_commit_no_entra(self):
        self.commit()
        nuevo = self.raiz / "fase-01-primeros-pasos" / "nuevo.md"
        nuevo.write_text("# Nuevo\n", encoding="utf-8")
        self.assertEqual(self.ejecutar("--commit", "fase-01-primeros-pasos/nuevo.md"), 2, self.salida)
        self.assertIn("No está en ese commit", self.salida)

    def test_referencia_que_no_existe(self):
        self.commit()
        self.assertEqual(self.ejecutar("--commit", "v9.9.9"), 2, self.salida)
        self.assertIn("«v9.9.9» no es un commit", self.salida)

    def test_sin_git(self):
        self.assertEqual(self.ejecutar("--commit"), 2, self.salida)
        self.assertIn("--commit", self.salida)

    def test_la_copia_es_como_un_clon(self):
        """Saltos de línea según .gitattributes, el permiso de ejecución, sin carpetas vacías; y el curso puede
        ser una subcarpeta de su repositorio (como bueno dentro del kit)."""
        repositorio = self.tmp / "repositorio"
        curso = repositorio / "cursos" / "bueno"
        shutil.copytree(self.raiz, curso)
        script = curso / CONTAR
        script.write_bytes(script.read_bytes().replace(b"\n", b"\r\n"))
        script.chmod(0o755)
        (curso / EJEMPLOS / "vacia").mkdir()
        self.commit(carpeta=repositorio)
        destino = self.tmp / "copia"
        copia, descripcion, cambios = verificar_codigo.sacar_commit(curso, "HEAD", destino)
        self.assertEqual(copia, destino / "cursos" / "bueno")
        self.assertNotIn(b"\r\n", (copia / CONTAR).read_bytes())             # * text=auto eol=lf
        self.assertTrue((copia / CONTAR).stat().st_mode & 0o100)
        self.assertFalse((copia / EJEMPLOS / "vacia").exists())
        self.assertIn("curso", descripcion)
        self.assertEqual(cambios, 0)


class Permisos(unittest.TestCase):
    """Los ficheros que van a la terminal, con permisos fijos (como un clon con umask 022), venga de donde venga
    la carpeta: ficheros 644 (755 si son ejecutables) y carpetas 755."""

    def comprobar(self, con_docker):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            (carpeta / "datos.txt").write_text("x\n", encoding="utf-8")
            (carpeta / "datos.txt").chmod(0o664)                    # umask 002, o git archive
            (carpeta / "script.sh").write_text("echo hola\n", encoding="utf-8")
            (carpeta / "script.sh").chmod(0o775)
            (carpeta / "Descargas").mkdir()
            (carpeta / "Descargas").chmod(0o775)
            (carpeta / "Descargas" / "solo-lectura.txt").write_text("x\n", encoding="utf-8")
            (carpeta / "Descargas" / "solo-lectura.txt").chmod(0o444)
            with terminal.terminal(carpeta, con_docker=con_docker) as t:
                codigo, salida, _ = t.ejecutar(["bash", "-c", "stat -c '%a %n' datos.txt script.sh Descargas Descargas/*"])
        self.assertEqual(codigo, 0)
        self.assertEqual(salida.split("\n")[:4], ["644 datos.txt", "755 script.sh", "755 Descargas",
                                                   "644 Descargas/solo-lectura.txt"])

    def test_sin_docker(self):
        self.comprobar(False)

    @unittest.skipUnless(HAY_DOCKER, "sin Docker")
    def test_con_docker(self):
        self.comprobar(True)


class ConDocker(SinDocker):
    """Las mismas pruebas en la terminal del kit, y lo que solo se ve con ella."""
    sin_docker = False

    def test_el_curso_bueno_pasa_y_avisa_de_que_es_parcial(self):
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertIn("verificación completa", self.salida)

    def test_lo_que_solo_falla_al_ejecutarlo_con_bash_3_2(self):
        orden = 'printf "Clientes de %s: %s (%(%Y)T)\\n" "$ciudad" "$total" 0'
        self.cambiar(CONTAR, 'echo "Clientes de $ciudad: $total"', orden)
        self.cambiar(MODULO, 'echo "Clientes de $ciudad: $total"', orden)
        self.cambiar(MODULO, "Clientes de Madrid: 2\n", "Clientes de Madrid: 2 (1970)\n")
        self.assertError(MODULO, "con bash 3.2 (la de macOS) no hace lo mismo")

    def sesion(self, ordenes):
        with terminal.Contenedor(self.raiz / f"{EJEMPLOS}/2.3-ver-un-fichero") as t:
            return t.sesion([(o, None) for o in ordenes])

    def test_sin_red(self):
        self.assertIn("Could not resolve host", self.sesion(["curl -sS -m 3 https://example.org"]))

    def test_git_en_espanol_con_la_rama_main(self):
        pantalla = self.sesion(["git init -q", "git status"])
        self.assertIn("En la rama main", pantalla)
        self.assertIn("No hay commits todavía", pantalla)

    HISTORIAL = ["git init -q", "git add cliente.json", 'git commit -q -m "Primero"', "git status --short",
                 'git commit -q -m "Vacío"', "echo '{}' > otro.json", "git add otro.json", 'git commit -q -m "Segundo"',
                 "git -c core.pager=cat log --format='%h %ad %an %s' --date=format:'%d/%m/%Y %H:%M'"]

    def test_git_reproducible_con_fechas_que_avanzan(self):
        primera, segunda = self.sesion(self.HISTORIAL), self.sesion(self.HISTORIAL)
        self.assertEqual(primera, segunda)
        self.assertRegex(primera, r"[0-9a-f]{7} 15/01/2026 10:01 Ana García Segundo")
        # el commit que falla («nada para hacer commit») no adelanta el reloj
        self.assertRegex(primera, r"[0-9a-f]{7} 15/01/2026 10:00 Ana García Primero")

    def test_git_respeta_las_fechas_que_pone_la_sesion(self):
        pantalla = self.sesion(["git init -q", "git add cliente.json",
                                'GIT_AUTHOR_DATE=2026-03-01T09:30:00 git commit -q -m "Uno"',
                                "git log --format='%ad' --date=format:'%d/%m %H:%M'"])
        self.assertIn("01/03 09:30", pantalla)

    def test_bash_y_las_herramientas_en_espanol(self):
        pantalla = self.sesion(["gti", "ls no-existe"])
        self.assertIn("bash: gti: orden no encontrada", pantalla)
        self.assertIn("ls: no se puede acceder a 'no-existe': No existe el archivo o el directorio", pantalla)

    def test_coreutils_de_gnu_en_espanol(self):
        pantalla = self.sesion(["ls --version | head -1", "touch -d '2026-01-15 10:00' Zeta.txt alfa.txt", "ls",
                                "ls -l alfa.txt", "rmdir nada"])
        self.assertIn("ls (GNU coreutils)", pantalla)
        self.assertIn("alfa.txt  cliente.json  sesion.txt  Zeta.txt", pantalla)  # sin distinguir mayúsculas; tabuladores, en espacios
        self.assertIn("ene 15  2026 alfa.txt", pantalla)
        self.assertIn("rmdir: fallo al borrar 'nada': No existe el archivo o el directorio", pantalla)

    def test_user_logname_y_shell(self):
        self.assertIn("alumno alumno /bin/bash", self.sesion(['echo "$USER $LOGNAME $SHELL"']))

    def test_git_esta_donde_en_un_ubuntu(self):
        pantalla = self.sesion(["command -v git", "type git"])
        self.assertIn("$ command -v git\n/usr/bin/git", pantalla)
        self.assertIn("git is /usr/bin/git", pantalla)

    def test_las_versiones_de_la_imagen(self):
        pantalla = self.sesion(["git --version", 'echo "$BASH_VERSION"', "bash-3.2 -c 'echo $BASH_VERSION'"])
        self.assertIn("git version 2.56.0", pantalla)
        self.assertIn("5.3.", pantalla)
        self.assertIn("3.2.57", pantalla)

if __name__ == "__main__":
    unittest.main()
