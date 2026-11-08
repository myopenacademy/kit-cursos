"""Pruebas de nucleo/generar_chuleta_global.py, sobre una copia del curso de ejemplo bueno (cursos/bueno/).

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
HERRAMIENTAS = PRUEBAS.parent
sys.path.insert(0, str(HERRAMIENTAS))
import formato_academia  # noqa: E402

BUENO = PRUEBAS / "cursos" / "bueno"
SCRIPT = HERRAMIENTAS / "nucleo" / "generar_chuleta_global.py"
MODULO = "fase-01-primeros-pasos/01-ficheros-json.md"


class GenerarChuletaGlobal(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="chuleta-global-"))
        self.raiz = self.tmp / "curso-ejemplo"
        shutil.copytree(BUENO, self.raiz)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ejecutar(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd)

    def chuleta(self):
        return (self.raiz / "99-chuleta-global.md").read_text(encoding="utf-8")

    def cambiar(self, antes, despues):
        ruta = self.raiz / MODULO
        texto = ruta.read_text(encoding="utf-8")
        self.assertIn(antes, texto)
        ruta.write_text(texto.replace(antes, despues, 1), encoding="utf-8")

    def test_la_chuleta_del_curso_bueno_esta_al_dia(self):
        self.assertEqual(self.ejecutar("--comprobar", str(BUENO)).returncode, 0)

    def test_baja_un_nivel_los_encabezados(self):
        self.ejecutar(cwd=self.raiz)
        self.assertIn("#### Tipos de valores", self.chuleta())
        self.assertIn("### 01.01 Ficheros JSON", self.chuleta())

    def test_termina_antes_de_las_preguntas_de_repaso(self):
        self.ejecutar(str(self.raiz))
        self.assertNotIn("Preguntas de repaso", self.chuleta())
        self.assertNotIn("¿Qué rodea a un objeto JSON?", self.chuleta())

    def test_corrige_los_enlaces_relativos_y_las_anclas(self):
        self.cambiar("| Texto | `\"hola\"` |", "| Texto | `\"hola\"` |\n\nMás en [1.2](#12-objetos-y-listas), "
                     "[el índice](../00-indice.md) y ![Estructura](img/estructura.svg).")
        self.ejecutar(str(self.raiz))
        texto = self.chuleta()
        self.assertIn(f"[1.2]({MODULO}#12-objetos-y-listas)", texto)
        self.assertIn("[el índice](00-indice.md)", texto)
        self.assertIn("![Estructura](fase-01-primeros-pasos/img/estructura.svg)", texto)

    def test_no_toca_los_enlaces_dentro_de_un_bloque_de_codigo(self):
        self.cambiar("| Texto | `\"hola\"` |", "| Texto | `\"hola\"` |\n\n````markdown\n![foto](foto.png)\n````")
        self.ejecutar(str(self.raiz))
        self.assertIn("![foto](foto.png)", self.chuleta())

    def test_omite_los_modulos_no_disponibles(self):
        d = json.loads((self.raiz / "curso.json").read_text(encoding="utf-8"))
        d["fases"][0]["modulos"][0]["disponible"] = False
        (self.raiz / "curso.json").write_text(json.dumps(d), encoding="utf-8")
        self.ejecutar(str(self.raiz))
        self.assertIn("Todavía no hay ningún módulo disponible.", self.chuleta())

    def test_la_chuleta_generada_no_tiene_enlaces_rotos(self):
        self.cambiar("| Texto | `\"hola\"` |", "| Texto | `\"hola\"` |\n\nMás en [1.2](#12-objetos-y-listas).")
        self.ejecutar(str(self.raiz))
        informe, _ = formato_academia.comprobar(self.raiz)
        self.assertEqual([e for e in informe.errores if "99-chuleta-global.md" in e[0]], [])

    def test_desfasada(self):
        self.cambiar("| Texto | `\"hola\"` |", "| Texto | `\"adiós\"` |")
        r = self.ejecutar("--comprobar", str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("no está al día", r.stdout)

    def test_argumentos_mal(self):
        self.assertEqual(self.ejecutar("--rapido").returncode, 2)
        self.assertEqual(self.ejecutar("/no/existe").returncode, 2)


if __name__ == "__main__":
    unittest.main()
