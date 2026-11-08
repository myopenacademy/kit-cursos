"""Pruebas de nucleo/verificar_codigo.py y lenguajes/bash.py, sobre una copia del curso de ejemplo bueno.

Las que ejecutan con Docker (la verificación completa, con bash 3.2) se saltan si no hay Docker; la primera vez
se construye la imagen de la terminal del kit (unos minutos, con internet).

Desde la raíz del kit:
    python3 -m unittest discover -s herramientas/pruebas -v
"""
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
import terminal  # noqa: E402

BUENO = PRUEBAS / "cursos" / "bueno"
SCRIPT = HERRAMIENTAS / "nucleo" / "verificar_codigo.py"
MODULO = "fase-01-primeros-pasos/01-ficheros-json.md"
EJEMPLOS = "fase-01-primeros-pasos/codigo/01-ficheros-json/ejemplos"
CONTAR = f"{EJEMPLOS}/2.2-contar-clientes/contar.sh"
HAY_DOCKER = terminal.hay_docker()


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
    def test_interpreta_retornos_borrados_y_colores(self):
        self.assertEqual(terminal.pantalla("hola\rHO\r\n\x1b[31mrojo\x1b[0m\r\nabc\x08\x08X\x1b[K"), ["HOla", "rojo", "aX"])


class Base(unittest.TestCase):
    sin_docker = False

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="verificar-codigo-"))
        self.raiz = self.tmp / "curso-ejemplo"
        shutil.copytree(BUENO, self.raiz)

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
        self.assertTrue(any(all(t in l for t in trozos) for l in self.salida.split("\nfase-")), self.salida)


class SinDocker(Base):
    """La verificación parcial, con la bash del equipo: funciona en cualquier máquina con bash."""
    sin_docker = True

    def test_el_curso_bueno_pasa_y_avisa_de_que_es_parcial(self):
        self.assertEqual(self.ejecutar(), 0, self.salida)
        self.assertIn("1 scripts ejecutados y 1 sesiones", self.salida)
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


@unittest.skipUnless(HAY_DOCKER, "hace falta Docker")
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

    def test_git_reproducible(self):
        ordenes = ["git init -q", "git add cliente.json",
                   'GIT_AUTHOR_DATE=2026-11-08T10:00:00 GIT_COMMITTER_DATE=2026-11-08T10:00:00 git commit -q -m "Primero"',
                   "git log --format='%h %an'"]
        primera, segunda = self.sesion(ordenes), self.sesion(ordenes)
        self.assertEqual(primera, segunda)
        self.assertIn("Ana García", primera)

    def test_las_versiones_de_la_imagen(self):
        pantalla = self.sesion(["git --version", 'echo "$BASH_VERSION"', "bash-3.2 -c 'echo $BASH_VERSION'"])
        self.assertIn("git version 2.56.0", pantalla)
        self.assertIn("5.3.", pantalla)
        self.assertIn("3.2.57", pantalla)

if __name__ == "__main__":
    unittest.main()
