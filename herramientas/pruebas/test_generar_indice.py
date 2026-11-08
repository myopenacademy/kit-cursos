"""Pruebas de nucleo/generar_indice.py, sobre una copia del curso de ejemplo bueno (cursos/bueno/).

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
sys.path.insert(0, str(HERRAMIENTAS / "nucleo"))
import formato_academia  # noqa: E402
import generar_indice  # noqa: E402

BUENO = PRUEBAS / "cursos" / "bueno"
SCRIPT = HERRAMIENTAS / "nucleo" / "generar_indice.py"


class GenerarIndice(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="generar-indice-"))
        self.raiz = self.tmp / "curso-ejemplo"
        shutil.copytree(BUENO, self.raiz)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ejecutar(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=cwd)

    def indice(self):
        return (self.raiz / "00-indice.md").read_text(encoding="utf-8")

    def cambiar_json(self, cambio):
        d = json.loads((self.raiz / "curso.json").read_text(encoding="utf-8"))
        cambio(d)
        (self.raiz / "curso.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_el_indice_del_curso_bueno_esta_al_dia(self):
        r = self.ejecutar("--comprobar", str(BUENO))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_desde_la_raiz_del_curso_sin_argumentos(self):
        (self.raiz / "00-indice.md").unlink()
        r = self.ejecutar(cwd=self.raiz)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("## Fase 01 — Primeros pasos", self.indice())

    def test_modulo_disponible_con_nivel_y_tiempo_de_su_cabecera(self):
        self.assertIn("| 01.01 | [Ficheros JSON](fase-01-primeros-pasos/01-ficheros-json.md) | Básico · Núcleo | 2 h | ✅ Disponible |",
                      self.indice())

    def test_modulo_pendiente_sin_enlace(self):
        self.assertIn("| 01.02 | Ficheros YAML | — | — | Pendiente |", self.indice())

    def test_retos_pendientes_sin_enlace(self):
        self.cambiar_json(lambda d: d["fases"][0].update(retos_disponibles=False))
        texto, _, _ = generar_indice.generar(self.raiz)
        self.assertIn("| | Retos de la fase | | | Pendiente |", texto)

    def test_tiempo_con_decimales(self):
        modulo = self.raiz / "fase-01-primeros-pasos/01-ficheros-json.md"
        modulo.write_text(modulo.read_text(encoding="utf-8").replace("2 horas", "1,5 horas"), encoding="utf-8")
        texto, _, _ = generar_indice.generar(self.raiz)
        self.assertIn("| Básico · Núcleo | 1,5 h |", texto)

    def test_cambiar_un_titulo_deja_el_indice_desfasado(self):
        self.cambiar_json(lambda d: d["fases"][0].update(titulo="Los primeros pasos"))
        r = self.ejecutar("--comprobar", str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("no está al día", r.stdout)
        self.assertEqual(self.ejecutar(str(self.raiz)).returncode, 0)
        self.assertIn("## Fase 01 — Los primeros pasos", self.indice())

    def test_el_indice_generado_cumple_el_formato(self):
        self.cambiar_json(lambda d: d["fases"][0].update(titulo="Los primeros pasos"))
        retos = self.raiz / "fase-01-primeros-pasos/retos.md"
        retos.write_text(retos.read_text(encoding="utf-8").replace("— Primeros pasos", "— Los primeros pasos"), encoding="utf-8")
        self.ejecutar(str(self.raiz))
        informe, _ = formato_academia.comprobar(self.raiz)
        self.assertEqual([e for e in informe.errores if "00-indice.md" in e[0]], [])
        self.assertEqual([a for a in informe.avisos if "00-indice.md" in a[0]], [])

    def test_proyecto_de_tipo_modulo(self):
        self.cambiar_json(lambda d: d.update(proyecto={"tipo": "modulo", "modulo": "ejemplo.ficheros-json"}))
        texto, _, _ = generar_indice.generar(self.raiz)
        self.assertIn("🎯 [Ficheros JSON]", texto)
        self.assertNotIn("## Proyecto", texto)

    def test_sin_curso_json(self):
        (self.raiz / "curso.json").unlink()
        r = self.ejecutar(str(self.raiz))
        self.assertEqual(r.returncode, 1)
        self.assertIn("No se puede generar el índice", r.stderr)

    def test_argumentos_mal(self):
        self.assertEqual(self.ejecutar("--rapido").returncode, 2)
        self.assertEqual(self.ejecutar("/no/existe").returncode, 2)
        self.assertEqual(self.ejecutar("--help").returncode, 0)


if __name__ == "__main__":
    unittest.main()
