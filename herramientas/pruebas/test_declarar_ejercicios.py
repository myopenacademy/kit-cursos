"""Pruebas de nucleo/declarar_ejercicios.py, sobre una copia del curso de ejemplo bueno (cursos/bueno/).

Desde la raíz del kit:
    python3 -m unittest discover -s herramientas/pruebas -v
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PRUEBAS = Path(__file__).resolve().parent
SCRIPT = PRUEBAS.parent / "nucleo" / "declarar_ejercicios.py"
BUENO = PRUEBAS / "cursos" / "bueno"
MODULO = "fase-01-primeros-pasos/01-ficheros-json.md"
FASE = "fase-01-primeros-pasos"


class DeclararEjercicios(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="declarar-"))
        self.raiz = self.tmp / "curso-ejemplo"
        shutil.copytree(BUENO, self.raiz)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ejecutar(self, *args):
        r = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=self.raiz)
        self.salida = r.stdout + r.stderr
        return r.returncode

    def curso(self):
        return json.loads((self.raiz / "curso.json").read_text(encoding="utf-8"))

    def ejercicios(self):
        return [(e["id"], e["titulo"]) for e in self.curso()["fases"][0]["modulos"][0]["ejercicios"]]

    def cambiar(self, antes, despues):
        ruta = self.raiz / MODULO
        texto = ruta.read_text(encoding="utf-8")
        self.assertIn(antes, texto)
        ruta.write_text(texto.replace(antes, despues), encoding="utf-8")

    def cambiar_json(self, cambio):
        d = self.curso()
        cambio(d)
        (self.raiz / "curso.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def test_sin_cambios_deja_curso_json_igual(self):
        antes = (self.raiz / "curso.json").read_bytes()
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)
        self.assertEqual((self.raiz / "curso.json").read_bytes(), antes)

    def test_declara_desde_cero_con_la_regla_de_formato(self):
        self.cambiar_json(lambda d: d["fases"][0]["modulos"][0].update(ejercicios=[], disponible=False))
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)
        self.assertEqual(self.ejercicios(), [("ejemplo.ficheros-json.un-pedido-de-la-tienda", "Un pedido de la tienda"),
                                             ("ejemplo.ficheros-json.la-coma-de-mas", "La coma de más")])
        self.assertNotIn("disponible", self.curso()["fases"][0]["modulos"][0])

    def test_conserva_el_id_aunque_cambie_la_posicion(self):
        texto = (self.raiz / MODULO).read_text(encoding="utf-8")
        texto = texto.replace("#### Ejercicio 1 · Un pedido de la tienda", "#### Ejercicio 1 · TMP")
        texto = texto.replace("#### Ejercicio 2 · La coma de más", "#### Ejercicio 2 · Un pedido de la tienda")
        (self.raiz / MODULO).write_text(texto.replace("#### Ejercicio 1 · TMP", "#### Ejercicio 1 · La coma de más"),
                                        encoding="utf-8")
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)
        self.assertEqual(self.ejercicios(), [("ejemplo.ficheros-json.la-coma-de-mas", "La coma de más"),
                                             ("ejemplo.ficheros-json.un-pedido", "Un pedido de la tienda")])

    def test_ejercicio_nuevo_recibe_id_y_los_demas_conservan_el_suyo(self):
        self.cambiar("### 🔴 Avanzado\n", "### 🔴 Avanzado\n\n#### Ejercicio 3 · ¿Qué fecha es?\n\nEnunciado.\n")
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)
        self.assertIn(("ejemplo.ficheros-json.que-fecha-es", "¿Qué fecha es?"), self.ejercicios())
        self.assertIn(("ejemplo.ficheros-json.un-pedido", "Un pedido de la tienda"), self.ejercicios())
        self.assertIn("ejercicio nuevo «¿Qué fecha es?»", self.salida)

    def test_titulo_que_cambia_para_y_pregunta(self):
        antes = (self.raiz / "curso.json").read_bytes()
        self.cambiar("Ejercicio 2 · La coma de más", "Ejercicio 2 · La coma que sobra")
        self.assertEqual(self.ejecutar(MODULO), 1)
        self.assertIn("ya no están «La coma de más» (ejemplo.ficheros-json.la-coma-de-mas)", self.salida)
        self.assertIn("¿Es el mismo ejercicio con otro título?", self.salida)
        self.assertIn("No se ha escrito nada", self.salida)
        self.assertEqual((self.raiz / "curso.json").read_bytes(), antes)

    def test_mismo_ejercicio_con_otro_titulo_conserva_el_id(self):
        self.cambiar("Ejercicio 2 · La coma de más", "Ejercicio 2 · La coma que sobra")
        self.cambiar_json(lambda d: d["fases"][0]["modulos"][0]["ejercicios"][1].update(titulo="La coma que sobra"))
        self.assertEqual(self.ejecutar(MODULO), 0, self.salida)
        self.assertIn(("ejemplo.ficheros-json.la-coma-de-mas", "La coma que sobra"), self.ejercicios())

    def test_otro_ejercicio_con_aceptar_cambios(self):
        self.cambiar("Ejercicio 2 · La coma de más", "Ejercicio 2 · La coma que sobra")
        self.assertEqual(self.ejecutar(MODULO, "--aceptar-cambios"), 0, self.salida)
        self.assertIn(("ejemplo.ficheros-json.la-coma-que-sobra", "La coma que sobra"), self.ejercicios())
        self.assertNotIn("la-coma-de-mas", str(self.ejercicios()))

    def test_identificador_repetido(self):
        self.cambiar("### 🔴 Avanzado\n", "### 🔴 Avanzado\n\n#### Ejercicio 3 · La coma, de más\n\nEnunciado.\n")
        self.assertEqual(self.ejecutar(MODULO), 1)
        self.assertIn("el identificador «ejemplo.ficheros-json.la-coma-de-mas» se repite", self.salida)

    def test_titulo_con_formato(self):
        self.cambiar("### 🔴 Avanzado\n", "### 🔴 Avanzado\n\n#### Ejercicio 3 · El fichero `datos.json`\n\nEnunciado.\n")
        self.assertEqual(self.ejecutar(MODULO), 1)
        self.assertIn("lleva formato Markdown", self.salida)

    def test_una_fase_y_sus_retos(self):
        self.cambiar_json(lambda d: d["fases"][0].update(retos_disponibles=False))
        self.assertEqual(self.ejecutar(FASE, "--retos"), 0, self.salida)
        self.assertNotIn("retos_disponibles", self.curso()["fases"][0])

    def test_comprobar_no_escribe(self):
        self.cambiar_json(lambda d: d["fases"][0]["modulos"][0].update(ejercicios=[]))
        antes = (self.raiz / "curso.json").read_bytes()
        self.assertEqual(self.ejecutar(MODULO, "--comprobar"), 0, self.salida)
        self.assertIn("no se ha escrito nada", self.salida)
        self.assertEqual((self.raiz / "curso.json").read_bytes(), antes)

    def test_una_fase_con_un_modulo_pendiente_lo_deja_pendiente(self):
        self.assertEqual(self.ejecutar(FASE), 0, self.salida)
        self.assertIn("02-ficheros-yaml.md: todavía no está escrito; sigue pendiente", self.salida)

    def test_un_modulo_pendiente_sin_fichero(self):
        self.assertEqual(self.ejecutar("fase-01-primeros-pasos/02-ficheros-yaml.md"), 1)
        self.assertIn("no existe su fichero", self.salida)

    def test_ruta_que_no_es_de_curso_json(self):
        self.assertEqual(self.ejecutar("README.md"), 2)
        self.assertIn("no es ningún módulo ni ninguna carpeta de fase", self.salida)


if __name__ == "__main__":
    unittest.main()
