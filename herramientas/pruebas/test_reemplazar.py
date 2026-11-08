"""Pruebas de nucleo/reemplazar.py.

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

SCRIPT = Path(__file__).resolve().parent.parent / "nucleo" / "reemplazar.py"


class Reemplazar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="reemplazar-"))
        (self.tmp / "a.md").write_text("Hola, mundo.\nAdiós, mundo.\n", encoding="utf-8")
        (self.tmp / "b.md").write_text("Versión 1.\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ejecutar(self, cambios, *opciones, cwd=None):
        (self.tmp / "cambios.json").write_text(json.dumps(cambios, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), str(self.tmp / "cambios.json"), *opciones],
                           capture_output=True, text=True, cwd=cwd or self.tmp)
        self.salida = r.stdout + r.stderr
        return r.returncode

    def leer(self, nombre):
        return (self.tmp / nombre).read_bytes().decode("utf-8")

    def test_aplica_todos(self):
        self.assertEqual(self.ejecutar([{"fichero": "a.md", "antes": "Hola", "despues": "Buenas"},
                                        {"fichero": "b.md", "antes": "Versión 1", "despues": "Versión 2"}]), 0, self.salida)
        self.assertEqual(self.leer("a.md"), "Buenas, mundo.\nAdiós, mundo.\n")
        self.assertEqual(self.leer("b.md"), "Versión 2.\n")

    def test_cuenta_los_cambios_anteriores_del_mismo_fichero(self):
        self.assertEqual(self.ejecutar([{"fichero": "a.md", "antes": "Hola", "despues": "Buenas"},
                                        {"fichero": "a.md", "antes": "Buenas, mundo", "despues": "Buenas, gente"}]), 0)
        self.assertIn("Buenas, gente", self.leer("a.md"))

    def test_si_uno_falla_no_escribe_ninguno(self):
        self.assertEqual(self.ejecutar([{"fichero": "b.md", "antes": "Versión 1", "despues": "Versión 2"},
                                        {"fichero": "a.md", "antes": "mundo", "despues": "gente"}]), 1)
        self.assertIn("cambio 2 (a.md): el texto de «antes» aparece 2 veces", self.salida)
        self.assertIn("No se ha escrito ningún fichero", self.salida)
        self.assertEqual(self.leer("b.md"), "Versión 1.\n")

    def test_texto_que_no_aparece(self):
        self.assertEqual(self.ejecutar([{"fichero": "a.md", "antes": "Chao", "despues": "x"}]), 1)
        self.assertIn("aparece 0 veces (tiene que aparecer una)", self.salida)

    def test_fichero_que_no_existe(self):
        self.assertEqual(self.ejecutar([{"fichero": "c.md", "antes": "x", "despues": "y"}]), 1)
        self.assertIn("cambio 1 (c.md): el fichero no existe", self.salida)

    def test_cambio_imposible_tras_otro_del_mismo_fichero(self):
        # el segundo busca un texto que el primero ya ha cambiado: imposible, y no se escribe nada
        self.assertEqual(self.ejecutar([{"fichero": "a.md", "antes": "Hola", "despues": "Buenas"},
                                        {"fichero": "a.md", "antes": "Hola, mundo", "despues": "x"}]), 1)
        self.assertIn("cambio 2 (a.md): el texto de «antes» aparece 0 veces", self.salida)
        self.assertEqual(self.leer("a.md"), "Hola, mundo.\nAdiós, mundo.\n")

    def test_escritura_que_falla_a_mitad_deja_todo_como_estaba(self):
        (self.tmp / "b.md").chmod(0o444)          # b.md no se puede escribir: a.md se escribe antes y se deshace
        try:
            self.assertEqual(self.ejecutar([{"fichero": "a.md", "antes": "Hola", "despues": "Buenas"},
                                            {"fichero": "b.md", "antes": "Versión 1", "despues": "Versión 2"}]), 1)
        finally:
            (self.tmp / "b.md").chmod(0o644)
        self.assertIn("No se ha podido escribir", self.salida)
        self.assertIn("se han dejado como estaban", self.salida)
        self.assertEqual(self.leer("a.md"), "Hola, mundo.\nAdiós, mundo.\n")
        self.assertEqual(self.leer("b.md"), "Versión 1.\n")

    def test_aplicar_dos_veces_la_segunda_no_escribe(self):
        cambios = [{"fichero": "b.md", "antes": "Versión 1", "despues": "Versión 2"}]
        self.assertEqual(self.ejecutar(cambios), 0)
        self.assertEqual(self.ejecutar(cambios), 1)
        self.assertEqual(self.leer("b.md"), "Versión 2.\n")

    def test_comprobar_no_escribe(self):
        self.assertEqual(self.ejecutar([{"fichero": "a.md", "antes": "Hola", "despues": "Buenas"}], "--comprobar"), 0)
        self.assertIn("no se ha escrito nada", self.salida)
        self.assertIn("Hola", self.leer("a.md"))

    def test_raiz(self):
        otra = Path(tempfile.mkdtemp(prefix="reemplazar-cwd-"))
        try:
            self.assertEqual(self.ejecutar([{"fichero": "a.md", "antes": "Hola", "despues": "Buenas"}],
                                           "--raiz", str(self.tmp), cwd=otra), 0, self.salida)
            self.assertIn("Buenas", self.leer("a.md"))
        finally:
            shutil.rmtree(otra)

    def test_respeta_los_saltos_de_linea_de_windows(self):
        (self.tmp / "w.md").write_bytes("Uno\r\nDos\r\n".encode("utf-8"))
        self.assertEqual(self.ejecutar([{"fichero": "w.md", "antes": "Dos", "despues": "Tres"}]), 0)
        self.assertEqual((self.tmp / "w.md").read_bytes(), b"Uno\r\nTres\r\n")

    def test_fichero_de_cambios_mal_escrito(self):
        self.assertEqual(self.ejecutar([{"fichero": "a.md", "antes": "Hola"}]), 2)
        self.assertIn("debe tener «fichero», «antes» y «despues»", self.salida)
        self.assertEqual(self.ejecutar([]), 2)

    def test_argumentos_mal(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=self.tmp)
        self.assertEqual(r.returncode, 2)
        self.assertIn("Falta el fichero de cambios", r.stderr)


if __name__ == "__main__":
    unittest.main()
